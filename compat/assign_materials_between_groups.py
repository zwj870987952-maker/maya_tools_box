# -*- coding: utf-8 -*-
"""
Maya 物体材质双列表按行一对一指定工具
(Material Transfer by Row-by-Row Dual Lists with Sorting Presets & Drag-and-Drop)

功能说明：
    1. 双列表点击录入与交互：
       - A 列表（源物体列表，提供材质）：在视口/大纲中选择物体，点击【录入选中】。
       - B 列表（目标物体列表，接收材质）：在视口/大纲中选择物体，点击【录入选中】。
       - 严格按照行号一对一匹配：A 的第 1 行匹配 B 的第 1 行，A 的第 2 行匹配 B 的第 2 行……

    2. 强大的排序预设与拖拽调序：
       - 手动鼠标拖拽调序：鼠标按住表格任意行，可直接在表格中上下拖拽重新调整插入行位置！
       - 多种智能排序预设：
         * 名称自然排序 (A ➔ Z / Z ➔ A)：数字智能识别 (如 Part_1, Part_2, Part_10)；
         * Maya 大纲层级顺序 (自上而下 / 自下而上)；
         * 面数大小排序 (从多到少 / 从少到多)；
         * 材质球名称排序；
         * 原始录入顺序恢复。
       - 一键正反倒序：配备独立的【⇅ 倒序】按钮，快速翻转行次序。
       - 双表同步排序：一键将 A 和 B 列表同时按名称自然排序对齐。

    3. 智能材质指定与拓扑自适应：
       - 支持整物材质赋予与分面多材质指定（Per-Face Components，如 .f[0:100]）。
       - 拓扑安全校验：若目标网格面数与源网格不一致，自动将源物体中占比最大的主材质安全降级赋予整物。
       - 完整保留表面材质（surfaceShader）、置换（displacementShader）及着色网络连接。

    4. 生产级安全与撤销：
       - 封装于单一 Maya 原生 Undo Chunk，支持 `Ctrl+Z` 一键撤销。
       - 兼容 Maya 2018~2026+（支持 PySide2 与 PySide6，兼容 Python 2/3）。

使用方法：
    1. 在 Maya 脚本编辑器（Python）或架子（Shelf）中运行：
       import sys
       if "assign_materials_between_groups" in sys.modules:
           del sys.modules["assign_materials_between_groups"]
       import assign_materials_between_groups
       assign_materials_between_groups.show_ui()

    2. 或作为 Python API 调用：
       import assign_materials_between_groups as mat_tool
       mat_tool.transfer_materials_by_rows(
           source_list=["Cube_High", "Sphere_High"],
           target_list=["Cube_Low", "Sphere_Low"],
           transfer_face_assignments=True,
           fallback_on_topology_mismatch=True
       )
"""

from __future__ import absolute_import, division, print_function

import re
import sys
import time
import traceback
import maya.cmds as cmds
import maya.mel as mel

# ------------------------------------------------------------------------------
# 兼容导入 PySide2 (Maya 2017~2024) / PySide6 (Maya 2025+)
# ------------------------------------------------------------------------------
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, Signal
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt
        from PySide2.QtCore import Signal
    except ImportError:
        raise ImportError("当前 Maya 环境中未找到 PySide2 或 PySide6，无法初始化工具图形界面。")


# ==============================================================================
# Maya 窗口与宿主交互辅助函数
# ==============================================================================

def get_maya_main_window():
    """获取 Maya 主窗口作为 Qt 父级 Widget，确保窗口层级正确不会沉底。"""
    try:
        import maya.OpenMayaUI as omui
        ptr = omui.MQtUtil.mainWindow()
        if not ptr:
            return None
        try:
            from shiboken6 import wrapInstance
            return wrapInstance(int(ptr), QtWidgets.QWidget)
        except ImportError:
            pass
        try:
            from shiboken2 import wrapInstance
            return wrapInstance(int(ptr), QtWidgets.QWidget)
        except ImportError:
            pass
    except Exception:
        pass
    return None


# ==============================================================================
# 排序算法辅助函数 (自然排序、大纲排序等)
# ==============================================================================

def natural_sort_key(s):
    """
    自然排序 Key 函数：将字符串中的连续数字转换为整型进行数值比对。
    例如确保 'part_1' < 'part_2' < 'part_10'，而不是 'part_10' < 'part_2'。
    """
    if not s:
        return []
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s))]


def get_outliner_order_map():
    """获取场景中所有 DAG 节点在大纲中的树形深度优先顺序索引字典。"""
    all_dag = cmds.ls(dag=True, long=True) or []
    return {node: idx for idx, node in enumerate(all_dag)}


# ==============================================================================
# 核心数据与几何/材质提取算法
# ==============================================================================

def get_clean_name(node):
    """获取节点的无层级短名称（去父级路径）。"""
    if not node:
        return ""
    return node.rsplit("|", 1)[-1]


def strip_node_namespace(node):
    """剔除节点名称中的命名空间。"""
    if not node:
        return ""
    leaf = get_clean_name(node)
    if ":" in leaf:
        return leaf.rsplit(":", 1)[-1]
    return leaf


def get_transform_node(shape_node):
    """获取 mesh shape 的直接父级 transform 节点长名称。"""
    if not shape_node or not cmds.objExists(shape_node):
        return None
    if cmds.nodeType(shape_node) == "transform":
        return cmds.ls(shape_node, long=True)[0]
    parents = cmds.listRelatives(shape_node, parent=True, fullPath=True)
    if parents:
        return parents[0]
    return shape_node


def get_surface_shader(shading_engine):
    """根据 shadingEngine 节点查询其连接的 surfaceShader 节点。"""
    if not shading_engine or not cmds.objExists(shading_engine):
        return ""
    connections = cmds.listConnections(shading_engine + ".surfaceShader") or []
    if connections:
        return connections[0]
    return shading_engine


def extract_mesh_materials(mesh_shape):
    """
    提取单个 mesh shape 上的所有材质指定信息。
    """
    if not mesh_shape or not cmds.objExists(mesh_shape):
        return None

    mesh_long = cmds.ls(mesh_shape, long=True)[0]
    transform_long = get_transform_node(mesh_long)

    try:
        total_faces = cmds.polyEvaluate(mesh_long, face=True) or 0
    except Exception:
        total_faces = 0

    sgs = cmds.listConnections(mesh_long, type="shadingEngine") or []
    sgs = list(dict.fromkeys(sgs))

    valid_sgs = [sg for sg in sgs if cmds.nodeType(sg) == "shadingEngine"]
    if not valid_sgs:
        valid_sgs = ["initialShadingGroup"]

    assignments = []
    is_per_face = False

    for sg in valid_sgs:
        shader_name = get_surface_shader(sg)
        members = cmds.sets(sg, query=True) or []

        is_whole = False
        matching_faces = []

        for member in members:
            long_members = cmds.ls(member, long=True)
            if not long_members:
                continue
            m_long = long_members[0]

            if "." not in m_long:
                if m_long == mesh_long or m_long == transform_long:
                    is_whole = True
                    break
            else:
                base_node = m_long.split(".")[0]
                if base_node == mesh_long or base_node == transform_long:
                    expanded = cmds.ls(m_long, flatten=True) or []
                    for face_str in expanded:
                        try:
                            idx = int(face_str.split(".f[")[-1].rstrip("]"))
                            matching_faces.append(idx)
                        except ValueError:
                            pass

        if is_whole and not matching_faces:
            assignments.append({
                "sg": sg,
                "shader": shader_name,
                "is_whole_mesh": True,
                "face_indices": [],
                "face_count": total_faces
            })
        elif matching_faces:
            is_per_face = True
            unique_faces = sorted(list(set(matching_faces)))
            assignments.append({
                "sg": sg,
                "shader": shader_name,
                "is_whole_mesh": False,
                "face_indices": unique_faces,
                "face_count": len(unique_faces)
            })
        else:
            if len(valid_sgs) == 1:
                assignments.append({
                    "sg": sg,
                    "shader": shader_name,
                    "is_whole_mesh": True,
                    "face_indices": [],
                    "face_count": total_faces
                })

    # 智能排序：非 initialShadingGroup 优先，面数占比大的排前
    assignments.sort(
        key=lambda a: (
            0 if a["sg"] == "initialShadingGroup" else 1,
            a.get("face_count", 0)
        ),
        reverse=True
    )

    if len(assignments) > 1 or any(not a.get("is_whole_mesh", True) for a in assignments):
        is_per_face = True

    return {
        "shape": mesh_long,
        "transform": transform_long,
        "total_faces": total_faces,
        "is_per_face": is_per_face,
        "assignments": assignments
    }


def resolve_objects_from_selection(selected_nodes):
    """
    解析用户选中的节点列表（严格保持先后顺序）。
    若选中的是 Group 组节点，自动按大纲层级依序展开其下所有 Mesh Shape。
    """
    if not selected_nodes:
        return []

    collected_shapes = []
    seen = set()

    for node in selected_nodes:
        if not cmds.objExists(node):
            continue

        node_long = cmds.ls(node, long=True)[0]
        node_type = cmds.nodeType(node_long)

        if node_type == "mesh":
            if node_long not in seen:
                seen.add(node_long)
                collected_shapes.append(node_long)
        elif node_type == "transform":
            direct_shapes = cmds.listRelatives(node_long, shapes=True, fullPath=True, type="mesh") or []
            valid_direct = [s for s in direct_shapes if not cmds.getAttr(s + ".intermediateObject")]

            if valid_direct:
                for s in valid_direct:
                    if s not in seen:
                        seen.add(s)
                        collected_shapes.append(s)
            else:
                descendants = cmds.listRelatives(node_long, allDescendents=True, fullPath=True, type="mesh") or []
                valid_desc = [s for s in descendants if not cmds.getAttr(s + ".intermediateObject")]
                valid_desc = sorted(list(set(valid_desc)))
                for s in valid_desc:
                    if s not in seen:
                        seen.add(s)
                        collected_shapes.append(s)

    records = []
    for idx, s_long in enumerate(collected_shapes):
        t_long = get_transform_node(s_long)
        t_display = get_clean_name(t_long)
        mat_info = extract_mesh_materials(s_long) or {}
        assigns = mat_info.get("assignments", [])

        if assigns:
            mat_names = [a["shader"] if a["shader"] != a["sg"] else a["sg"] for a in assigns]
            if mat_info.get("is_per_face", False):
                mat_summary = "{} (分面{}材质)".format(", ".join(mat_names), len(assigns))
            else:
                mat_summary = mat_names[0]
        else:
            mat_summary = "无材质"

        records.append({
            "initial_index": idx,
            "transform": t_long,
            "shape": s_long,
            "display": t_display,
            "total_faces": mat_info.get("total_faces", 0),
            "materials": mat_info,
            "mat_summary": mat_summary,
            "status": "待指定"
        })

    return records


# ==============================================================================
# 单对材质指定执行函数
# ==============================================================================

def assign_materials_to_target(source_info,
                               target_shape,
                               transfer_face_assignments=True,
                               fallback_on_topology_mismatch=True,
                               logger=None):
    """
    将单个源网格的材质信息指定到目标网格上。
    返回: (status: str, detail: str)
    """
    if not target_shape or not cmds.objExists(target_shape):
        return "failed", "目标物体不存在"

    target_shape_long = cmds.ls(target_shape, long=True)[0]
    mat_data = source_info.get("materials") or {}
    assignments = mat_data.get("assignments") or []

    if not assignments:
        return "skipped", "源物体无有效材质"

    try:
        target_faces = cmds.polyEvaluate(target_shape_long, face=True) or 0
    except Exception:
        target_faces = 0
    source_faces = mat_data.get("total_faces", 0)
    is_per_face = mat_data.get("is_per_face", False)

    # 1. 整物赋予模式
    if not is_per_face or not transfer_face_assignments:
        primary_sg = assignments[0]["sg"]
        if not cmds.objExists(primary_sg):
            return "failed", "着色组 {} 不存在".format(primary_sg)
        try:
            cmds.sets(target_shape_long, edit=True, forceElement=primary_sg)
            return "success", "整物赋予 [{}] 成功".format(primary_sg)
        except Exception as e:
            return "failed", "整物赋予失败: {}".format(e)

    # 2. 分面多材质模式
    if source_faces != target_faces or target_faces == 0:
        msg = "拓扑面数不一致 (源: {} 面, 目标: {} 面)".format(source_faces, target_faces)
        if fallback_on_topology_mismatch:
            primary_sg = assignments[0]["sg"]
            try:
                cmds.sets(target_shape_long, edit=True, forceElement=primary_sg)
                return "downgraded", "面数不符，降级赋予主材质 [{}]".format(primary_sg)
            except Exception as e:
                return "failed", "降级赋予失败: {}".format(e)
        else:
            return "skipped", msg + "，已跳过分面赋予"

    try:
        success_count = 0
        for assign in assignments:
            sg = assign["sg"]
            if not cmds.objExists(sg):
                continue
            if assign.get("is_whole_mesh", False):
                cmds.sets(target_shape_long, edit=True, forceElement=sg)
                success_count += 1
            else:
                face_indices = assign.get("face_indices", [])
                if face_indices:
                    target_components = ["{}.f[{}]".format(target_shape_long, idx) for idx in face_indices]
                    cmds.sets(target_components, edit=True, forceElement=sg)
                    success_count += 1
        return "success", "分面赋予完成 ({}个着色组)".format(success_count)
    except Exception as e:
        if fallback_on_topology_mismatch and assignments:
            primary_sg = assignments[0]["sg"]
            try:
                cmds.sets(target_shape_long, edit=True, forceElement=primary_sg)
                return "downgraded", "分面赋予异常，已降级整物赋予: {}".format(e)
            except Exception:
                pass
        return "failed", "分面赋予异常: {}".format(e)


# ==============================================================================
# 无头 API 执行接口 (Headless Python API)
# ==============================================================================

def transfer_materials_by_rows(source_list,
                               target_list,
                               transfer_face_assignments=True,
                               fallback_on_topology_mismatch=True,
                               logger_func=None):
    """
    严格按照行号一对一执行材质传递：
    source_list[0] -> target_list[0]
    source_list[1] -> target_list[1]
    ...
    """
    def _log(msg, level="info"):
        if logger_func:
            logger_func(msg, level)
        else:
            prefix = "[MaterialTransfer]"
            if level == "error":
                cmds.warning("{} {}".format(prefix, msg))
            else:
                print("{} {}".format(prefix, msg))

    sources = resolve_objects_from_selection(source_list)
    targets = resolve_objects_from_selection(target_list)

    count = min(len(sources), len(targets))
    if count == 0:
        _log("源列表或目标列表为空，未执行任何材质传递。", "warning")
        return {"total": 0, "success": 0, "downgraded": 0, "failed": 0, "skipped": 0, "details": []}

    if len(sources) != len(targets):
        _log("提示：A 列表 ({}项) 与 B 列表 ({}项) 行数不一致，将处理前 {} 项对齐对。".format(
            len(sources), len(targets), count
        ), "warning")

    cmds.undoInfo(openChunk=True, chunkName="BatchTransferMaterialsByRows")
    stats = {"total": count, "success": 0, "downgraded": 0, "failed": 0, "skipped": 0, "details": []}

    try:
        for i in range(count):
            s_rec = sources[i]
            t_rec = targets[i]
            s_name = s_rec["display"]
            t_name = t_rec["display"]

            status, detail = assign_materials_to_target(
                source_info=s_rec,
                target_shape=t_rec["shape"],
                transfer_face_assignments=transfer_face_assignments,
                fallback_on_topology_mismatch=fallback_on_topology_mismatch,
                logger=logger_func
            )

            if status == "success":
                stats["success"] += 1
                _log("[第{}行] 成功: {} -> {} ({})".format(i + 1, s_name, t_name, detail), "success")
            elif status == "downgraded":
                stats["downgraded"] += 1
                _log("[第{}行] 降级: {} -> {} ({})".format(i + 1, s_name, t_name, detail), "warning")
            elif status == "failed":
                stats["failed"] += 1
                _log("[第{}行] 失败: {} -> {} ({})".format(i + 1, s_name, t_name, detail), "error")
            else:
                stats["skipped"] += 1
                _log("[第{}行] 跳过: {} -> {} ({})".format(i + 1, s_name, t_name, detail), "warning")

            stats["details"].append({
                "row": i + 1,
                "source": s_name,
                "target": t_name,
                "status": status,
                "detail": detail
            })

    except Exception as e:
        _log("材质按行传递过程发生异常: {}".format(e), "error")
        traceback.print_exc()
    finally:
        cmds.undoInfo(closeChunk=True)

    _log("处理完成！共执行: {} 行, 成功: {}, 降级: {}, 失败: {}, 跳过: {}".format(
        count, stats["success"], stats["downgraded"], stats["failed"], stats["skipped"]
    ), "info")

    return stats


# ==============================================================================
# 支持平滑鼠标拖拽改序的表格控件 (ReorderableTableWidget)
# ==============================================================================

class ReorderableTableWidget(QtWidgets.QTableWidget):
    """支持鼠标直接在行间拖拽调整行次序的表格控件。"""

    rowOrderChanged = Signal(int, int)  # 信号：(from_row, to_row)

    def __init__(self, parent=None):
        super(ReorderableTableWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self._drag_start_row = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                self._drag_start_row = item.row()
            else:
                self._drag_start_row = -1
        super(ReorderableTableWidget, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.source() == self and self._drag_start_row >= 0:
            pos = event.pos()
            target_item = self.itemAt(pos)
            if target_item:
                target_row = target_item.row()
            else:
                # 拖拽到最后空白处
                target_row = max(0, self.rowCount() - 1)

            from_row = self._drag_start_row
            if 0 <= from_row < self.rowCount() and 0 <= target_row < self.rowCount():
                if from_row != target_row:
                    self.rowOrderChanged.emit(from_row, target_row)
                    event.accept()
                    self._drag_start_row = -1
                    return
        event.ignore()
        self._drag_start_row = -1


# ==============================================================================
# 现代化深色双列表图形界面 (Dual-List PySide GUI with Presets & Drag Reorder)
# ==============================================================================

class DualListMaterialDialog(QtWidgets.QDialog):
    """材质双列表逐行指定主窗口。"""

    WINDOW_TITLE = "Maya 物体材质双列表逐行指定工具 (支持拖拽改序与多预设排序)"
    WINDOW_OBJECT_NAME = "MayaMaterialTransferDualListDialog"

    SORT_PRESETS = [
        ("--- 选择排序预设 ---", None),
        ("🔤 名称自然排序 (A ➔ Z)", "name_asc"),
        ("🔤 名称自然倒序 (Z ➔ A)", "name_desc"),
        ("🌲 大纲自上而下 (Outliner Order)", "outliner_asc"),
        ("🌲 大纲自下而上 (Outliner Reverse)", "outliner_desc"),
        ("🔷 面数从多到少 (Faces Max ➔ Min)", "faces_desc"),
        ("🔷 面数从少到多 (Faces Min ➔ Max)", "faces_asc"),
        ("🎨 材质球名称排序 (Material Name)", "mat_name"),
        ("⏱️ 恢复原始录入顺序 (Reset Order)", "original")
    ]

    def __init__(self, parent=None):
        super(DualListMaterialDialog, self).__init__(parent)
        self.setObjectName(self.WINDOW_OBJECT_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(1080, 750)
        self.setMinimumSize(900, 600)

        self._records_a = []
        self._records_b = []

        self._init_ui()
        self._apply_dark_style()

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # 1. 双列表展示区（左 A 右 B）
        # ----------------------------------------------------------------------
        h_lists_layout = QtWidgets.QHBoxLayout()
        h_lists_layout.setSpacing(10)

        # ====== 左侧：源物体列表 A ======
        grp_a = QtWidgets.QGroupBox("1. 源物体列表 A (提供材质)  [🖐️ 可直接鼠标拖拽行改序]")
        grp_a.setStyleSheet("QGroupBox { border-color: #386b40; }")
        v_a = QtWidgets.QVBoxLayout(grp_a)
        v_a.setContentsMargins(8, 10, 8, 8)
        v_a.setSpacing(6)

        # 顶部排序工具栏 A
        h_sort_a = QtWidgets.QHBoxLayout()
        h_sort_a.addWidget(QtWidgets.QLabel("排序预设:"))
        self.cbo_sort_a = QtWidgets.QComboBox()
        for label, code in self.SORT_PRESETS:
            self.cbo_sort_a.addItem(label, code)
        self.cbo_sort_a.currentIndexChanged.connect(lambda: self._on_apply_sort_preset(is_list_a=True))
        h_sort_a.addWidget(self.cbo_sort_a, stretch=1)

        btn_rev_a = QtWidgets.QPushButton("⇅ 倒序")
        btn_rev_a.setFixedWidth(56)
        btn_rev_a.setToolTip("一键将 A 列表所有行次序倒转 (正序/反序互换)")
        btn_rev_a.clicked.connect(lambda: self._reverse_list(is_list_a=True))
        h_sort_a.addWidget(btn_rev_a)
        v_a.addLayout(h_sort_a)

        self.table_a = ReorderableTableWidget()
        self.table_a.setColumnCount(4)
        self.table_a.setHorizontalHeaderLabels(["行号", "源物体 (Source)", "材质球/着色组", "面数"])
        self.table_a.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table_a.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.table_a.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table_a.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.table_a.setAlternatingRowColors(True)
        self.table_a.itemSelectionChanged.connect(self._on_table_a_selection_changed)
        self.table_a.rowOrderChanged.connect(lambda f, t: self._on_row_drag_dropped(is_list_a=True, from_row=f, to_row=t))
        v_a.addWidget(self.table_a)

        # 底部按钮栏 A
        h_btn_a = QtWidgets.QHBoxLayout()
        btn_load_a = QtWidgets.QPushButton("📥 录入选中")
        btn_load_a.setToolTip("用当前场景/视口中选中的物体覆盖 A 列表")
        btn_load_a.setStyleSheet("font-weight: bold; background-color: #2b6335;")
        btn_load_a.clicked.connect(lambda: self._load_selection_to_a(append=False))

        btn_append_a = QtWidgets.QPushButton("➕ 追加")
        btn_append_a.setToolTip("将当前选中的物体追加到 A 列表末尾")
        btn_append_a.clicked.connect(lambda: self._load_selection_to_a(append=True))

        btn_up_a = QtWidgets.QPushButton("⬆️")
        btn_up_a.setFixedWidth(30)
        btn_up_a.setToolTip("上移选中行")
        btn_up_a.clicked.connect(lambda: self._move_row(self.table_a, self._records_a, up=True))

        btn_down_a = QtWidgets.QPushButton("⬇️")
        btn_down_a.setFixedWidth(30)
        btn_down_a.setToolTip("下移选中行")
        btn_down_a.clicked.connect(lambda: self._move_row(self.table_a, self._records_a, up=False))

        btn_del_a = QtWidgets.QPushButton("🗑️ 移除")
        btn_del_a.setToolTip("移除选中的行")
        btn_del_a.clicked.connect(lambda: self._remove_selected_rows(self.table_a, self._records_a))

        btn_clear_a = QtWidgets.QPushButton("清空")
        btn_clear_a.setFixedWidth(46)
        btn_clear_a.clicked.connect(lambda: self._clear_list(self.table_a, self._records_a))

        h_btn_a.addWidget(btn_load_a)
        h_btn_a.addWidget(btn_append_a)
        h_btn_a.addWidget(btn_up_a)
        h_btn_a.addWidget(btn_down_a)
        h_btn_a.addWidget(btn_del_a)
        h_btn_a.addWidget(btn_clear_a)
        v_a.addLayout(h_btn_a)

        # ====== 中间控制（互换 / 同步排序） ======
        v_center = QtWidgets.QVBoxLayout()
        v_center.addStretch()

        btn_sync_sort = QtWidgets.QPushButton("⚡\n双\n表\n同\n步\n排\n序")
        btn_sync_sort.setFixedWidth(34)
        btn_sync_sort.setFixedHeight(120)
        btn_sync_sort.setStyleSheet("font-weight: bold; background-color: #3b5066;")
        btn_sync_sort.setToolTip("一键将 A 列表和 B 列表同时按【名称自然排序 A-Z】排好对齐！")
        btn_sync_sort.clicked.connect(self._sync_sort_both_lists)
        v_center.addWidget(btn_sync_sort)

        v_center.addSpacing(12)

        btn_swap = QtWidgets.QPushButton("⇄\n互\n换\nA\nB")
        btn_swap.setFixedWidth(34)
        btn_swap.setFixedHeight(110)
        btn_swap.setStyleSheet("font-weight: bold; background-color: #444444;")
        btn_swap.setToolTip("互换 A 列表与 B 列表的所有模型")
        btn_swap.clicked.connect(self._swap_lists)
        v_center.addWidget(btn_swap)

        v_center.addStretch()

        # ====== 右侧：目标物体列表 B ======
        grp_b = QtWidgets.QGroupBox("2. 目标物体列表 B (接收材质)  [🖐️ 可直接鼠标拖拽行改序]")
        grp_b.setStyleSheet("QGroupBox { border-color: #215987; }")
        v_b = QtWidgets.QVBoxLayout(grp_b)
        v_b.setContentsMargins(8, 10, 8, 8)
        v_b.setSpacing(6)

        # 顶部排序工具栏 B
        h_sort_b = QtWidgets.QHBoxLayout()
        h_sort_b.addWidget(QtWidgets.QLabel("排序预设:"))
        self.cbo_sort_b = QtWidgets.QComboBox()
        for label, code in self.SORT_PRESETS:
            self.cbo_sort_b.addItem(label, code)
        self.cbo_sort_b.currentIndexChanged.connect(lambda: self._on_apply_sort_preset(is_list_a=False))
        h_sort_b.addWidget(self.cbo_sort_b, stretch=1)

        btn_rev_b = QtWidgets.QPushButton("⇅ 倒序")
        btn_rev_b.setFixedWidth(56)
        btn_rev_b.setToolTip("一键将 B 列表所有行次序倒转 (正序/反序互换)")
        btn_rev_b.clicked.connect(lambda: self._reverse_list(is_list_a=False))
        h_sort_b.addWidget(btn_rev_b)
        v_b.addLayout(h_sort_b)

        self.table_b = ReorderableTableWidget()
        self.table_b.setColumnCount(5)
        self.table_b.setHorizontalHeaderLabels(["行号", "目标物体 (Target)", "原有材质", "面数", "状态"])
        self.table_b.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table_b.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.table_b.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table_b.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.table_b.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Interactive)
        self.table_b.setAlternatingRowColors(True)
        self.table_b.itemSelectionChanged.connect(self._on_table_b_selection_changed)
        self.table_b.rowOrderChanged.connect(lambda f, t: self._on_row_drag_dropped(is_list_a=False, from_row=f, to_row=t))
        v_b.addWidget(self.table_b)

        # 底部按钮栏 B
        h_btn_b = QtWidgets.QHBoxLayout()
        btn_load_b = QtWidgets.QPushButton("📥 录入选中")
        btn_load_b.setToolTip("用当前场景/视口中选中的物体覆盖 B 列表")
        btn_load_b.setStyleSheet("font-weight: bold; background-color: #1a517c;")
        btn_load_b.clicked.connect(lambda: self._load_selection_to_b(append=False))

        btn_append_b = QtWidgets.QPushButton("➕ 追加")
        btn_append_b.setToolTip("将当前选中的物体追加到 B 列表末尾")
        btn_append_b.clicked.connect(lambda: self._load_selection_to_b(append=True))

        btn_up_b = QtWidgets.QPushButton("⬆️")
        btn_up_b.setFixedWidth(30)
        btn_up_b.setToolTip("上移选中行")
        btn_up_b.clicked.connect(lambda: self._move_row(self.table_b, self._records_b, up=True))

        btn_down_b = QtWidgets.QPushButton("⬇️")
        btn_down_b.setFixedWidth(30)
        btn_down_b.setToolTip("下移选中行")
        btn_down_b.clicked.connect(lambda: self._move_row(self.table_b, self._records_b, up=False))

        btn_del_b = QtWidgets.QPushButton("🗑️ 移除")
        btn_del_b.setToolTip("移除选中的行")
        btn_del_b.clicked.connect(lambda: self._remove_selected_rows(self.table_b, self._records_b))

        btn_clear_b = QtWidgets.QPushButton("清空")
        btn_clear_b.setFixedWidth(46)
        btn_clear_b.clicked.connect(lambda: self._clear_list(self.table_b, self._records_b))

        h_btn_b.addWidget(btn_load_b)
        h_btn_b.addWidget(btn_append_b)
        h_btn_b.addWidget(btn_up_b)
        h_btn_b.addWidget(btn_down_b)
        h_btn_b.addWidget(btn_del_b)
        h_btn_b.addWidget(btn_clear_b)
        v_b.addLayout(h_btn_b)

        h_lists_layout.addWidget(grp_a, stretch=5)
        h_lists_layout.addLayout(v_center, stretch=0)
        h_lists_layout.addWidget(grp_b, stretch=5)

        main_layout.addLayout(h_lists_layout, stretch=3)

        # ----------------------------------------------------------------------
        # 2. 匹配规则与选项设置
        # ----------------------------------------------------------------------
        h_opts = QtWidgets.QHBoxLayout()
        self.chk_face_assign = QtWidgets.QCheckBox("保持分面多材质指定 (Per-Face Assignments)")
        self.chk_face_assign.setChecked(True)
        self.chk_face_assign.setToolTip("若源物体赋予了多个材质球，保持按面分量精确指定")

        self.chk_fallback = QtWidgets.QCheckBox("拓扑面数不符时自动降级整物赋予 (Fallback on Topology Mismatch)")
        self.chk_fallback.setChecked(True)
        self.chk_fallback.setToolTip("若目标与源网格面数不同，自动赋予主材质，避免跳过或报错")

        self.lbl_status = QtWidgets.QLabel("A 列表: 0 项 | B 列表: 0 项 (请在视口选择物体并点击录入)")
        self.lbl_status.setStyleSheet("color: #aaaaaa; font-style: italic;")

        h_opts.addWidget(self.chk_face_assign)
        h_opts.addWidget(self.chk_fallback)
        h_opts.addStretch()
        h_opts.addWidget(self.lbl_status)
        main_layout.addLayout(h_opts)

        # ----------------------------------------------------------------------
        # 3. 大按钮：执行按行一对一材质指定
        # ----------------------------------------------------------------------
        self.btn_execute = QtWidgets.QPushButton("⚡ 执行按行一对一材质指定 (A[第i行] -> B[第i行])")
        self.btn_execute.setFixedHeight(44)
        self.btn_execute.setStyleSheet(
            "font-size: 15px; font-weight: bold; background-color: #2b7a3d; color: #ffffff; border-radius: 5px;"
        )
        self.btn_execute.setEnabled(False)
        self.btn_execute.clicked.connect(self._on_execute_assignment)
        main_layout.addWidget(self.btn_execute)

        # ----------------------------------------------------------------------
        # 4. 日志控制台
        # ----------------------------------------------------------------------
        grp_log = QtWidgets.QGroupBox("执行日志 (Console Output)")
        v_log = QtWidgets.QVBoxLayout(grp_log)
        v_log.setContentsMargins(6, 6, 6, 6)
        v_log.setSpacing(4)

        self.txt_log = QtWidgets.QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setFixedHeight(115)
        self.txt_log.setStyleSheet("background-color: #1a1a1a; color: #d0d0d0; font-family: Consolas, monospace;")
        v_log.addWidget(self.txt_log)

        h_log_bar = QtWidgets.QHBoxLayout()
        btn_clear_log = QtWidgets.QPushButton("清空日志")
        btn_clear_log.setFixedWidth(80)
        btn_clear_log.clicked.connect(self.txt_log.clear)
        h_log_bar.addStretch()
        h_log_bar.addWidget(btn_clear_log)
        v_log.addLayout(h_log_bar)

        main_layout.addWidget(grp_log, stretch=1)

        self._log("工具已就绪。支持排序预设、一键反序以及直接鼠标拖拽行调序！", "info")

    def _apply_dark_style(self):
        """应用现代暗黑灰主题样式。"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #484848;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
                color: #dddddd;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                left: 10px;
            }
            QComboBox {
                background-color: #222222;
                color: #e0e0e0;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 3px 6px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #e0e0e0;
                selection-background-color: #007acc;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
            QTableWidget {
                background-color: #202020;
                alternate-background-color: #282828;
                color: #e0e0e0;
                gridline-color: #383838;
                border: 1px solid #404040;
            }
            QHeaderView::section {
                background-color: #323232;
                color: #c8c8c8;
                padding: 4px;
                border: 1px solid #404040;
                font-weight: bold;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 6px;
            }
            QScrollBar:vertical {
                border: none;
                background: #202020;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #505050;
                min-height: 20px;
                border-radius: 5px;
            }
        """)

    def _log(self, text, level="info"):
        color_map = {
            "info": "#c8c8c8",
            "success": "#4cd964",
            "warning": "#ffd60a",
            "error": "#ff453a"
        }
        color = color_map.get(level, "#c8c8c8")
        timestamp = time.strftime("%H:%M:%S")
        html = '<span style="color:#6e6e6e;">[{}]</span> <span style="color:{};">{}</span>'.format(
            timestamp, color, text
        )
        self.txt_log.append(html)

    # --------------------------------------------------------------------------
    # 列表数据录入与刷新
    # --------------------------------------------------------------------------
    def _load_selection_to_a(self, append=False):
        sel = cmds.ls(selection=True, long=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "提示", "请先在 Maya 场景中选择要录入的源模型或组！")
            return
        new_records = resolve_objects_from_selection(sel)
        if not new_records:
            QtWidgets.QMessageBox.warning(self, "提示", "所选对象中未找到任何有效 Mesh 网格！")
            return

        if append:
            self._records_a.extend(new_records)
            self._log("向 A 列表追加了 {} 个源物体。".format(len(new_records)), "info")
        else:
            self._records_a = new_records
            self._log("已录入 {} 个源物体到 A 列表。".format(len(new_records)), "info")

        self._refresh_table_a()
        self._update_status_and_validation()

    def _load_selection_to_b(self, append=False):
        sel = cmds.ls(selection=True, long=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "提示", "请先在 Maya 场景中选择要录入的目标模型或组！")
            return
        new_records = resolve_objects_from_selection(sel)
        if not new_records:
            QtWidgets.QMessageBox.warning(self, "提示", "所选对象中未找到任何有效 Mesh 网格！")
            return

        for r in new_records:
            r["status"] = "待指定"

        if append:
            self._records_b.extend(new_records)
            self._log("向 B 列表追加了 {} 个目标物体。".format(len(new_records)), "info")
        else:
            self._records_b = new_records
            self._log("已录入 {} 个目标物体到 B 列表。".format(len(new_records)), "info")

        self._refresh_table_b()
        self._update_status_and_validation()

    def _refresh_table_a(self):
        self.table_a.blockSignals(True)
        self.table_a.setRowCount(len(self._records_a))

        for row, rec in enumerate(self._records_a):
            idx_item = QtWidgets.QTableWidgetItem(str(row + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            idx_item.setForeground(QtGui.QColor("#4cd964"))
            self.table_a.setItem(row, 0, idx_item)

            obj_item = QtWidgets.QTableWidgetItem(rec["display"])
            obj_item.setToolTip(rec["transform"])
            self.table_a.setItem(row, 1, obj_item)

            mat_item = QtWidgets.QTableWidgetItem(rec["mat_summary"])
            self.table_a.setItem(row, 2, mat_item)

            face_item = QtWidgets.QTableWidgetItem(str(rec["total_faces"]))
            face_item.setTextAlignment(Qt.AlignCenter)
            self.table_a.setItem(row, 3, face_item)

        self.table_a.blockSignals(False)

    def _refresh_table_b(self):
        self.table_b.blockSignals(True)
        self.table_b.setRowCount(len(self._records_b))

        for row, rec in enumerate(self._records_b):
            idx_item = QtWidgets.QTableWidgetItem(str(row + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            idx_item.setForeground(QtGui.QColor("#007acc"))
            self.table_b.setItem(row, 0, idx_item)

            obj_item = QtWidgets.QTableWidgetItem(rec["display"])
            obj_item.setToolTip(rec["transform"])
            self.table_b.setItem(row, 1, obj_item)

            mat_item = QtWidgets.QTableWidgetItem(rec["mat_summary"])
            self.table_b.setItem(row, 2, mat_item)

            face_item = QtWidgets.QTableWidgetItem(str(rec["total_faces"]))
            face_item.setTextAlignment(Qt.AlignCenter)
            self.table_b.setItem(row, 3, face_item)

            status_str = rec.get("status", "待指定")
            st_item = QtWidgets.QTableWidgetItem(status_str)
            if "成功" in status_str:
                st_item.setForeground(QtGui.QColor("#4cd964"))
            elif "降级" in status_str:
                st_item.setForeground(QtGui.QColor("#ffd60a"))
            elif "失败" in status_str:
                st_item.setForeground(QtGui.QColor("#ff3b30"))
            else:
                st_item.setForeground(QtGui.QColor("#a0a0a0"))
            self.table_b.setItem(row, 4, st_item)

        self.table_b.blockSignals(False)

    def _update_status_and_validation(self):
        len_a = len(self._records_a)
        len_b = len(self._records_b)

        if len_a == 0 and len_b == 0:
            self.lbl_status.setText("A 列表: 0 项 | B 列表: 0 项 (请在视口选择物体并点击录入)")
            self.lbl_status.setStyleSheet("color: #aaaaaa; font-style: italic;")
            self.btn_execute.setEnabled(False)
            return

        if len_a == len_b and len_a > 0:
            self.lbl_status.setText("A 列表: {} 项 | B 列表: {} 项 (行数完全对齐，随时可以执行)".format(len_a, len_b))
            self.lbl_status.setStyleSheet("color: #4cd964; font-weight: bold;")
            self.btn_execute.setEnabled(True)
        elif len_a > 0 and len_b > 0:
            matched_pairs = min(len_a, len_b)
            self.lbl_status.setText(
                "⚠️ 行数不一致 (A: {} 项, B: {} 项)，仅前 {} 项将执行一对一指定".format(len_a, len_b, matched_pairs)
            )
            self.lbl_status.setStyleSheet("color: #ffd60a; font-weight: bold;")
            self.btn_execute.setEnabled(True)
        else:
            self.lbl_status.setText("A 列表: {} 项 | B 列表: {} 项 (需同时录入 A 和 B 才能执行)".format(len_a, len_b))
            self.lbl_status.setStyleSheet("color: #e0e0e0;")
            self.btn_execute.setEnabled(False)

    # --------------------------------------------------------------------------
    # 拖拽排序与手动按钮微调
    # --------------------------------------------------------------------------
    def _on_row_drag_dropped(self, is_list_a, from_row, to_row):
        """响应用户直接用鼠标拖拽某行释放时的事件。"""
        records = self._records_a if is_list_a else self._records_b
        table = self.table_a if is_list_a else self.table_b

        if 0 <= from_row < len(records) and 0 <= to_row < len(records):
            item = records.pop(from_row)
            records.insert(to_row, item)

            if is_list_a:
                self._refresh_table_a()
            else:
                self._refresh_table_b()

            table.selectRow(to_row)
            self._update_status_and_validation()
            list_name = "A 列表" if is_list_a else "B 列表"
            self._log("拖拽重排序 [{}]: 从第 {} 行移动至第 {} 行。".format(list_name, from_row + 1, to_row + 1), "info")

    def _move_row(self, table, records, up=True):
        sel = table.selectedIndexes()
        if not sel:
            return
        row = sel[0].row()
        target_row = row - 1 if up else row + 1

        if 0 <= target_row < len(records):
            records[row], records[target_row] = records[target_row], records[row]
            if table == self.table_a:
                self._refresh_table_a()
            else:
                self._refresh_table_b()
            table.selectRow(target_row)
            self._update_status_and_validation()

    def _remove_selected_rows(self, table, records):
        sel_rows = sorted(set(idx.row() for idx in table.selectedIndexes()), reverse=True)
        for r in sel_rows:
            if 0 <= r < len(records):
                del records[r]
        if table == self.table_a:
            self._refresh_table_a()
        else:
            self._refresh_table_b()
        self._update_status_and_validation()

    def _clear_list(self, table, records):
        del records[:]
        if table == self.table_a:
            self._refresh_table_a()
        else:
            self._refresh_table_b()
        self._update_status_and_validation()

    def _swap_lists(self):
        self._records_a, self._records_b = self._records_b, self._records_a
        self._refresh_table_a()
        self._refresh_table_b()
        self._update_status_and_validation()
        self._log("已互换 A 列表与 B 列表的所有物体。", "info")

    # --------------------------------------------------------------------------
    # 多种排序预设与正反翻转
    # --------------------------------------------------------------------------
    def _reverse_list(self, is_list_a):
        """一键正反倒转当前列表。"""
        records = self._records_a if is_list_a else self._records_b
        if not records:
            return
        records.reverse()
        if is_list_a:
            self._refresh_table_a()
        else:
            self._refresh_table_b()
        self._update_status_and_validation()
        list_name = "A 列表" if is_list_a else "B 列表"
        self._log("{} 已执行一键倒序翻转。".format(list_name), "info")

    def _on_apply_sort_preset(self, is_list_a):
        cbo = self.cbo_sort_a if is_list_a else self.cbo_sort_b
        code = cbo.currentData()
        if not code:
            return

        records = self._records_a if is_list_a else self._records_b
        if not records:
            return

        self._sort_records_by_code(records, code)

        if is_list_a:
            self._refresh_table_a()
        else:
            self._refresh_table_b()

        self._update_status_and_validation()
        list_name = "A 列表" if is_list_a else "B 列表"
        preset_name = cbo.currentText()
        self._log("{} 应用排序预设: {}。".format(list_name, preset_name), "info")

    def _sort_records_by_code(self, records, code):
        """根据指定的代码对记录执行排序。"""
        if code == "name_asc":
            records.sort(key=lambda r: natural_sort_key(r["display"]), reverse=False)
        elif code == "name_desc":
            records.sort(key=lambda r: natural_sort_key(r["display"]), reverse=True)
        elif code == "outliner_asc":
            outliner_map = get_outliner_order_map()
            records.sort(key=lambda r: outliner_map.get(r["transform"], 999999), reverse=False)
        elif code == "outliner_desc":
            outliner_map = get_outliner_order_map()
            records.sort(key=lambda r: outliner_map.get(r["transform"], 999999), reverse=True)
        elif code == "faces_desc":
            records.sort(key=lambda r: r.get("total_faces", 0), reverse=True)
        elif code == "faces_asc":
            records.sort(key=lambda r: r.get("total_faces", 0), reverse=False)
        elif code == "mat_name":
            records.sort(key=lambda r: natural_sort_key(r.get("mat_summary", "")), reverse=False)
        elif code == "original":
            records.sort(key=lambda r: r.get("initial_index", 0), reverse=False)

    def _sync_sort_both_lists(self):
        """快捷工具：一键将 A 和 B 列表同时按【名称自然排序 A-Z】排好对齐！"""
        if not self._records_a and not self._records_b:
            QtWidgets.QMessageBox.information(self, "提示", "当前 A 列表和 B 列表均为空！")
            return

        self._sort_records_by_code(self._records_a, "name_asc")
        self._sort_records_by_code(self._records_b, "name_asc")

        self.cbo_sort_a.blockSignals(True)
        self.cbo_sort_a.setCurrentIndex(1)  # A-Z
        self.cbo_sort_a.blockSignals(False)

        self.cbo_sort_b.blockSignals(True)
        self.cbo_sort_b.setCurrentIndex(1)  # A-Z
        self.cbo_sort_b.blockSignals(False)

        self._refresh_table_a()
        self._refresh_table_b()
        self._update_status_and_validation()
        self._log("⚡ A 列表与 B 列表已同步按【名称自然排序 A ➔ Z】排好对齐！", "success")

    # --------------------------------------------------------------------------
    # 视口高亮联动
    # --------------------------------------------------------------------------
    def _on_table_a_selection_changed(self):
        sel = self.table_a.selectedIndexes()
        if sel:
            row = sel[0].row()
            if 0 <= row < len(self._records_a):
                node = self._records_a[row]["transform"]
                if cmds.objExists(node):
                    cmds.select(node, replace=True)
            if row < len(self._records_b):
                self.table_b.blockSignals(True)
                self.table_b.selectRow(row)
                self.table_b.blockSignals(False)

    def _on_table_b_selection_changed(self):
        sel = self.table_b.selectedIndexes()
        if sel:
            row = sel[0].row()
            if 0 <= row < len(self._records_b):
                node = self._records_b[row]["transform"]
                if cmds.objExists(node):
                    cmds.select(node, replace=True)
            if row < len(self._records_a):
                self.table_a.blockSignals(True)
                self.table_a.selectRow(row)
                self.table_a.blockSignals(False)

    # --------------------------------------------------------------------------
    # 执行材质按行一对一指定
    # --------------------------------------------------------------------------
    def _on_execute_assignment(self):
        count = min(len(self._records_a), len(self._records_b))
        if count == 0:
            QtWidgets.QMessageBox.warning(self, "提示", "A 或 B 列表为空，请先录入模型！")
            return

        if len(self._records_a) != len(self._records_b):
            msg = (
                "A 列表有 {} 项，B 列表有 {} 项。\n\n"
                "将严格按照当前行号前 {} 项进行一对一材质传递，多余项将被跳过。\n"
                "操作支持 Ctrl+Z 撤销，是否继续？"
            ).format(len(self._records_a), len(self._records_b), count)
        else:
            msg = (
                "即将向 B 列表的 {} 个模型逐行指定 A 列表对应的材质。\n\n"
                "操作支持 Ctrl+Z 撤销，是否继续？"
            ).format(count)

        reply = QtWidgets.QMessageBox.question(
            self, "确认执行", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        transfer_face = self.chk_face_assign.isChecked()
        fallback_topo = self.chk_fallback.isChecked()

        self._log("开始执行按行一对一材质指定 (共 {} 行)...".format(count), "info")
        cmds.undoInfo(openChunk=True, chunkName="BatchTransferMaterialsByRows")

        stats = {"success": 0, "downgraded": 0, "failed": 0, "skipped": 0}

        try:
            for i in range(count):
                s_rec = self._records_a[i]
                t_rec = self._records_b[i]

                status, detail = assign_materials_to_target(
                    source_info=s_rec,
                    target_shape=t_rec["shape"],
                    transfer_face_assignments=transfer_face,
                    fallback_on_topology_mismatch=fallback_topo,
                    logger=self._log
                )

                if status == "success":
                    stats["success"] += 1
                    t_rec["status"] = "成功: " + detail
                    self._log("[第{}行] 成功: {} -> {} ({})".format(i + 1, s_rec["display"], t_rec["display"], detail), "success")
                elif status == "downgraded":
                    stats["downgraded"] += 1
                    t_rec["status"] = "安全降级: " + detail
                    self._log("[第{}行] 降级: {} -> {} ({})".format(i + 1, s_rec["display"], t_rec["display"], detail), "warning")
                elif status == "failed":
                    stats["failed"] += 1
                    t_rec["status"] = "失败: " + detail
                    self._log("[第{}行] 失败: {} -> {} ({})".format(i + 1, s_rec["display"], t_rec["display"], detail), "error")
                else:
                    stats["skipped"] += 1
                    t_rec["status"] = "跳过: " + detail
                    self._log("[第{}行] 跳过: {} -> {} ({})".format(i + 1, s_rec["display"], t_rec["display"], detail), "warning")

            for i in range(count):
                updated = extract_mesh_materials(self._records_b[i]["shape"]) or {}
                assigns = updated.get("assignments", [])
                if assigns:
                    mat_names = [a["shader"] if a["shader"] != a["sg"] else a["sg"] for a in assigns]
                    self._records_b[i]["mat_summary"] = ", ".join(mat_names)

            self._refresh_table_b()

        except Exception as e:
            self._log("材质指定过程异常: {}".format(e), "error")
            traceback.print_exc()
        finally:
            cmds.undoInfo(closeChunk=True)

        summary_msg = "按行一对一材质指定完成！\n总计执行: {} 行\n成功: {} 个\n安全降级: {} 个\n失败: {} 个\n\n提示：可在视口按 Ctrl+Z 撤销本次操作。".format(
            count, stats["success"], stats["downgraded"], stats["failed"]
        )
        self._log("=" * 40, "info")
        self._log(summary_msg.replace("\n", "  "), "info")
        QtWidgets.QMessageBox.information(self, "完成", summary_msg)


# ==============================================================================
# 界面展示入口单例管理
# ==============================================================================

_ACTIVE_DIALOG = None

def show_ui():
    """在 Maya 中创建并展示材质双列表逐行指定工具窗口。"""
    global _ACTIVE_DIALOG

    # 遍历所有顶级窗口，彻底关闭残留的同名旧窗口
    app = QtWidgets.QApplication.instance()
    if app:
        for w in app.topLevelWidgets():
            if w.objectName() == DualListMaterialDialog.WINDOW_OBJECT_NAME:
                try:
                    w.close()
                    w.deleteLater()
                except Exception:
                    pass
        app.processEvents()

    _ACTIVE_DIALOG = None

    parent_window = get_maya_main_window()
    _ACTIVE_DIALOG = DualListMaterialDialog(parent=parent_window)
    _ACTIVE_DIALOG.show()
    return _ACTIVE_DIALOG


if __name__ == "__main__":
    show_ui()
