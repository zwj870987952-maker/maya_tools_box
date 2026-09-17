# -*- coding: utf-8 -*-
"""
Maya 绑定工具：复制重叠位置顶点蒙皮权重 (Copy Overlapping Skin Weights)

功能说明：
    在源对象（A）与目标对象（B）之间，基于三维空间坐标匹配重叠的顶点，
    并将对应顶点的蒙皮权重精确复制到目标对象上。

核心特点：
    - 高性能：采用 Maya API 2.0 与空间哈希桶算法（Spatial Grid Hashing），
      在毫秒级内完成数万面网格的重叠点检索。
    - 安全精准：仅修改重叠点权重，目标对象上非重叠点的已有权重完全保留。
    - 智能骨骼管理：自动检测源对象的影响骨骼，若目标对象缺少骨骼则自动补充
      （addInfluence），若目标对象未绑定蒙皮则可自动完成绑定。
    - 完整撤销支持：所有权重修改均封装在单个 Undo Chunk 中，支持 Ctrl+Z 一键撤销。
    - 友好的图形界面与无依赖纯 Python 实现，支持全版本 Maya（2018~2026+）。

使用方法：
    1. 在 Maya 脚本编辑器（Python）中运行以下代码调出界面：
       import copy_overlapping_weights
       copy_overlapping_weights.show_ui()

    2. 也可以在脚本中直接函数式调用：
       import copy_overlapping_weights
       copy_overlapping_weights.copy_overlapping_skin_weights(
           source="source_mesh",
           target="target_mesh",
           tolerance=0.001,
           space="world"
       )
"""

from __future__ import absolute_import, division, print_function

import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma


# ==============================================================================
# 核心数据与几何工具函数
# ==============================================================================

def get_mesh_shape(node):
    """
    根据输入的节点获取其 Mesh Shape 节点（长名称）。
    如果输入的是组件（如 vtx），会自动返回其所属网格。
    """
    if not node or not cmds.objExists(node):
        return None

    # 如果传入的是组件 (如 pSphere1.vtx[0])
    if "." in node:
        node = node.split(".")[0]

    node_type = cmds.nodeType(node)
    if node_type == "mesh":
        return cmds.ls(node, long=True)[0]
    elif node_type == "transform":
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True) or []
        mesh_shapes = [s for s in shapes if cmds.nodeType(s) == "mesh"]
        if mesh_shapes:
            return mesh_shapes[0]

    return None


def get_mesh_dag(node):
    """获取网格 Shape 节点的 OpenMaya.MDagPath"""
    shape = get_mesh_shape(node)
    if not shape:
        return None

    sel = om.MSelectionList()
    sel.add(shape)
    return sel.getDagPath(0)


def get_skin_cluster(mesh):
    """获取网格绑定的 skinCluster 节点名称"""
    shape = get_mesh_shape(mesh)
    if not shape:
        return None

    history = cmds.listHistory(shape, pruneDagObjects=True) or []
    skin_clusters = cmds.ls(history, type="skinCluster") or []
    return skin_clusters[0] if skin_clusters else None


def get_mesh_points(mesh, space="world"):
    """
    使用 Maya API 2.0 获取网格所有顶点的坐标列表。
    
    :param mesh: 网格节点名称
    :param space: 'world' (世界空间) 或 'object' (物体局部空间)
    :return: MPointArray 或 None
    """
    dag = get_mesh_dag(mesh)
    if not dag:
        return None

    fn_mesh = om.MFnMesh(dag)
    m_space = om.MSpace.kWorld if space.lower() == "world" else om.MSpace.kObject
    return fn_mesh.getPoints(m_space)


def find_overlapping_vertices(src_points, tgt_points, tolerance=0.001):
    """
    使用空间哈希桶算法（Spatial Grid Hashing）检索重叠顶点对。

    :param src_points: 源网格顶点坐标列表 (MPointArray 或 list of Points)
    :param tgt_points: 目标网格顶点坐标列表
    :param tolerance: 距离容差阈值
    :return: 字典 {target_vtx_index: source_vtx_index}
    """
    cell_size = max(float(tolerance), 1e-7)
    grid = {}

    # 将源点按网格空间哈希划分进桶
    for src_idx, pt in enumerate(src_points):
        cx = int(math.floor(pt.x / cell_size))
        cy = int(math.floor(pt.y / cell_size))
        cz = int(math.floor(pt.z / cell_size))
        key = (cx, cy, cz)
        if key not in grid:
            grid[key] = []
        grid[key].append((src_idx, pt))

    matches = {}
    tol_sq = float(tolerance) * float(tolerance)

    # 遍历目标点，查询相邻 3x3x3 共 27 个网格单元
    for tgt_idx, pt in enumerate(tgt_points):
        cx = int(math.floor(pt.x / cell_size))
        cy = int(math.floor(pt.y / cell_size))
        cz = int(math.floor(pt.z / cell_size))

        closest_src = None
        min_dist_sq = tol_sq

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    neighbor_key = (cx + dx, cy + dy, cz + dz)
                    if neighbor_key in grid:
                        for s_idx, s_pt in grid[neighbor_key]:
                            d_sq = (
                                (s_pt.x - pt.x) * (s_pt.x - pt.x)
                                + (s_pt.y - pt.y) * (s_pt.y - pt.y)
                                + (s_pt.z - pt.z) * (s_pt.z - pt.z)
                            )
                            if d_sq <= min_dist_sq:
                                min_dist_sq = d_sq
                                closest_src = s_idx

        if closest_src is not None:
            matches[tgt_idx] = closest_src

    return matches


# ==============================================================================
# 蒙皮与权重处理逻辑
# ==============================================================================

def ensure_target_skin(
    src_skin,
    tgt_mesh,
    auto_bind=True,
    add_missing_influences=True
):
    """
    检查并确保目标网格具有合法的 skinCluster，且包含源所需的影响骨骼。

    :param src_skin: 源对象的 skinCluster 名称
    :param tgt_mesh: 目标对象 Transform 或 Shape 名称
    :param auto_bind: 若目标未蒙皮，是否自动绑定
    :param add_missing_influences: 是否自动向目标添加缺少的骨骼
    :return: 目标对象的 skinCluster 名称
    """
    tgt_skin = get_skin_cluster(tgt_mesh)
    src_influences = cmds.skinCluster(src_skin, query=True, influence=True) or []

    if not tgt_skin:
        if not auto_bind:
            raise RuntimeError(
                "目标对象 [{}] 尚未绑定蒙皮 (skinCluster)，请先蒙皮或开启自动蒙皮选项。".format(
                    tgt_mesh
                )
            )

        if not src_influences:
            raise RuntimeError(
                "源对象蒙皮 [{}] 中未检测到任何有效的影响骨骼。".format(src_skin)
            )

        # 针对目标对象进行自动蒙皮绑定
        created_skins = cmds.skinCluster(
            src_influences,
            tgt_mesh,
            toSelectedBones=True,
            bindMethod=0,  # 紧密关联
            normalizeWeights=1,
            name="{}_skinCluster".format(tgt_mesh.split("|")[-1]),
        )
        tgt_skin = created_skins[0]
        print("已自动为目标对象 [{}] 创建蒙皮簇: {}".format(tgt_mesh, tgt_skin))
        return tgt_skin

    # 目标对象已存在蒙皮簇，检查是否有缺失骨骼
    if add_missing_influences:
        tgt_influences = set(
            cmds.skinCluster(tgt_skin, query=True, influence=True) or []
        )
        missing_influences = [
            inf for inf in src_influences if inf not in tgt_influences
        ]

        if missing_influences:
            for inf in missing_influences:
                if cmds.objExists(inf):
                    cmds.skinCluster(
                        tgt_skin,
                        edit=True,
                        addInfluence=inf,
                        weight=0.0,
                    )
            print(
                "已向目标蒙皮 [{}] 自动补充缺失骨骼 (共 {} 根): {}".format(
                    tgt_skin, len(missing_influences), missing_influences
                )
            )

    return tgt_skin


def copy_overlapping_skin_weights(
    source,
    target,
    tolerance=0.001,
    space="world",
    auto_bind=True,
    add_missing_influences=True,
    show_progress=True,
):
    """
    复制源对象 A 与目标对象 B 中重叠位置顶点的权重。

    :param source: 源对象（Transform 或 Mesh Shape）
    :param target: 目标对象（Transform 或 Mesh Shape）
    :param tolerance: 重叠匹配距离容差（默认 0.001）
    :param space: 'world' (默认) 或 'object'
    :param auto_bind: 目标若无蒙皮是否自动绑定（默认 True）
    :param add_missing_influences: 自动添加目标缺失的骨骼（默认 True）
    :param show_progress: 是否显示进度条（默认 True）
    :return: 字典，包含匹配统计信息
    """
    # 1. 节点与网格合法性校验
    src_shape = get_mesh_shape(source)
    tgt_shape = get_mesh_shape(target)

    if not src_shape or not cmds.objExists(src_shape):
        raise ValueError("无效的源对象: [{}]，未找到 Mesh 网格节点。".format(source))

    if not tgt_shape or not cmds.objExists(tgt_shape):
        raise ValueError("无效的目标对象: [{}]，未找到 Mesh 网格节点。".format(target))

    if src_shape == tgt_shape:
        raise ValueError("源对象与目标对象不能是同一个网格！")

    # 2. 检查源蒙皮簇
    src_skin = get_skin_cluster(src_shape)
    if not src_skin:
        raise RuntimeError(
            "源对象 [{}] 没有检测到绑定的蒙皮簇 (skinCluster)，无法作为源提供权重！".format(
                source
            )
        )

    # 3. 获取点位置与重叠匹配
    src_dag = get_mesh_dag(src_shape)
    tgt_dag = get_mesh_dag(tgt_shape)

    src_points = get_mesh_points(src_shape, space=space)
    tgt_points = get_mesh_points(tgt_shape, space=space)

    total_src = len(src_points)
    total_tgt = len(tgt_points)

    matches = find_overlapping_vertices(
        src_points, tgt_points, tolerance=tolerance
    )
    match_count = len(matches)

    if match_count == 0:
        warning_msg = (
            "未找到任何重叠顶点！源对象点数: {}，目标对象点数: {} (容差: {}, 空间: {})。\n"
            "请检查两物体位置是否重叠，或尝试增大容差阈值。".format(
                total_src, total_tgt, tolerance, space
            )
        )
        cmds.warning(warning_msg)
        return {
            "matched_count": 0,
            "total_source_points": total_src,
            "total_target_points": total_tgt,
            "tolerance": tolerance,
            "space": space,
        }

    # 4. 确保目标对象的蒙皮簇完备
    tgt_skin = ensure_target_skin(
        src_skin,
        tgt_shape,
        auto_bind=auto_bind,
        add_missing_influences=add_missing_influences,
    )

    # 5. 高性能读取源对象的全部权重 (Maya API 2.0)
    src_skin_node = om.MSelectionList().add(src_skin).getDependNode(0)
    fn_src_skin = oma.MFnSkinCluster(src_skin_node)

    comp_fn = om.MFnSingleIndexedComponent()
    src_comp = comp_fn.create(om.MFn.kMeshVertComponent)
    comp_fn.setCompleteData(total_src)

    all_src_weights, num_infs = fn_src_skin.getWeights(src_dag, src_comp)
    src_inf_dags = fn_src_skin.influenceObjects()
    src_inf_names = [inf.partialPathName() for inf in src_inf_dags]

    # 6. 安全写入权重 (带 Undo 支持及进度条)
    cmds.undoInfo(openChunk=True)
    use_progress = show_progress and match_count > 100

    if use_progress:
        cmds.progressWindow(
            title="复制重叠点权重",
            progress=0,
            status="正在复制权重: 0 / {}".format(match_count),
            isInterruptable=True,
            maxValue=match_count,
        )

    processed_count = 0
    try:
        # 针对每个重叠的目标点进行权重复制
        for tgt_vtx_idx, src_vtx_idx in matches.items():
            if use_progress:
                if cmds.progressWindow(query=True, isCancelled=True):
                    cmds.warning("用户已取消操作！已完成部分顶点的权重复制。")
                    break
                if processed_count % 50 == 0:
                    cmds.progressWindow(
                        edit=True,
                        progress=processed_count,
                        status="正在复制权重: {} / {}".format(
                            processed_count, match_count
                        ),
                    )

            # 提取源顶点有效骨骼权重
            transform_values = []
            base_offset = src_vtx_idx * num_infs
            for inf_i in range(num_infs):
                w = all_src_weights[base_offset + inf_i]
                if w > 1e-5:
                    transform_values.append((src_inf_names[inf_i], w))

            if transform_values:
                target_vtx = "{}.vtx[{}]".format(tgt_shape, tgt_vtx_idx)
                cmds.skinPercent(
                    tgt_skin,
                    target_vtx,
                    transformValue=transform_values,
                    zeroRemainingInfluences=True,
                    normalize=True,
                )

            processed_count += 1

    finally:
        if use_progress:
            cmds.progressWindow(endProgress=True)
        cmds.undoInfo(closeChunk=True)

    summary = (
        "权重复制完成！源 [{}] (共 {} 点) -> 目标 [{}] (共 {} 点)。\n"
        "匹配并更新了 {} 个重叠点 (容差: {}, 空间: {})。".format(
            source.split("|")[-1],
            total_src,
            target.split("|")[-1],
            total_tgt,
            processed_count,
            tolerance,
            space,
        )
    )
    print(summary)

    return {
        "matched_count": processed_count,
        "total_source_points": total_src,
        "total_target_points": total_tgt,
        "tolerance": tolerance,
        "space": space,
    }


def select_overlapping_vertices(
    source, target, tolerance=0.001, space="world", select_target=True
):
    """
    辅助功能：在视口中选中匹配的重叠顶点，方便绑定师直观核对与检查。

    :param source: 源对象
    :param target: 目标对象
    :param tolerance: 距离容差
    :param space: 'world' 或 'object'
    :param select_target: True 则选中目标上的重叠点，False 则选中源上的重叠点
    :return: 选中的顶点列表
    """
    src_shape = get_mesh_shape(source)
    tgt_shape = get_mesh_shape(target)

    if not src_shape or not tgt_shape:
        cmds.warning("请指定有效的源对象和目标对象！")
        return []

    src_points = get_mesh_points(src_shape, space=space)
    tgt_points = get_mesh_points(tgt_shape, space=space)

    matches = find_overlapping_vertices(
        src_points, tgt_points, tolerance=tolerance
    )
    if not matches:
        cmds.warning("未检测到任何重叠点！")
        return []

    if select_target:
        vtx_list = [
            "{}.vtx[{}]".format(tgt_shape, idx) for idx in matches.keys()
        ]
    else:
        vtx_list = [
            "{}.vtx[{}]".format(src_shape, idx) for idx in set(matches.values())
        ]

    cmds.select(vtx_list, replace=True)
    print("已选中 {} 个重叠顶点。".format(len(vtx_list)))
    return vtx_list


# ==============================================================================
# 图形用户界面 (GUI) - 基于原生 cmds，兼容 Maya 全版本
# ==============================================================================

class CopyOverlappingWeightsUI(object):
    """复制重叠点权重工具界面管理器"""

    WINDOW_NAME = "CopyOverlappingSkinWeightsWindow"

    def __init__(self):
        self.src_field = None
        self.tgt_field = None
        self.tolerance_field = None
        self.space_radio = None
        self.auto_bind_chk = None
        self.add_missing_chk = None
        self.status_text = None

    def show(self):
        """显示界面"""
        if cmds.about(batch=True):
            print("当前处于 Maya Batch/Standalone 模式，GUI 窗口仅在交互界面模式下可用。请直接使用 copy_overlapping_skin_weights()。")
            return

        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        window = cmds.window(
            self.WINDOW_NAME,
            title="复制重叠点蒙皮权重 (Copy Overlapping Weights)",
            widthHeight=(460, 420),
            sizeable=True,
        )

        main_layout = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=8, columnOffset=("both", 12)
        )

        # 标题提示说明
        cmds.separator(height=6, style="none")
        cmds.text(
            label="匹配源对象与目标对象中空间重叠的点，并将权重复制至目标对象。",
            align="left",
            font="obliqueLabelFont",
        )
        cmds.separator(height=6, style="in")

        # --- 1. 对象选择区域 ---
        cmds.frameLayout(
            label="1. 录入对象 (Objects)",
            collapsable=False,
            marginWidth=6,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # 源对象 A
        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnWidth3=[110, 220, 100],
            columnAttach=[(1, "left", 0), (2, "both", 2), (3, "right", 0)],
        )
        cmds.text(label="源对象 (Source A):", align="left")
        self.src_field = cmds.textField(
            placeholderText="选择源模型后点击右侧按钮载入"
        )
        cmds.button(
            label="<< 录入选中",
            command=lambda *args: self._load_selected(self.src_field),
            backgroundColor=[0.35, 0.45, 0.55],
        )
        cmds.setParent("..")

        # 目标对象 B
        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnWidth3=[110, 220, 100],
            columnAttach=[(1, "left", 0), (2, "both", 2), (3, "right", 0)],
        )
        cmds.text(label="目标对象 (Target B):", align="left")
        self.tgt_field = cmds.textField(
            placeholderText="选择目标模型后点击右侧按钮载入"
        )
        cmds.button(
            label="<< 录入选中",
            command=lambda *args: self._load_selected(self.tgt_field),
            backgroundColor=[0.35, 0.45, 0.55],
        )
        cmds.setParent("..")

        # 互换按钮
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.button(
            label=" 交换 A <-> B ",
            command=self._swap_objects,
            width=110,
        )
        cmds.text(
            label="（提示：也可以直接在视口中选两个物体后点执行）",
            align="left",
            font="smallPlainLabelFont",
        )
        cmds.setParent("..")

        # 退出 columnLayout 和 frameLayout 回到 main_layout
        cmds.setParent("..")
        cmds.setParent("..")

        # --- 2. 匹配与绑定设置 ---
        cmds.frameLayout(
            label="2. 参数设置 (Settings)",
            collapsable=False,
            marginWidth=6,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        # 容差输入
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=[140, 120],
            columnAttach=[(1, "left", 0), (2, "left", 4)],
        )
        cmds.text(label="距离容差 (Tolerance):", align="left")
        self.tolerance_field = cmds.floatField(
            value=0.0010,
            precision=4,
            minValue=0.00001,
            maxValue=100.0,
            step=0.001,
        )
        cmds.setParent("..")

        # 空间单选
        cmds.rowLayout(numberOfColumns=3, columnWidth3=[140, 100, 100])
        cmds.text(label="空间坐标系 (Space):", align="left")
        self.space_radio = cmds.radioButtonGrp(
            numberOfRadioButtons=2,
            labelArray2=["世界空间 (World)", "物体空间 (Object)"],
            select=1,
            columnWidth2=[130, 130],
        )
        cmds.setParent("..")

        # 选项复选框
        self.auto_bind_chk = cmds.checkBox(
            label="目标未蒙皮时自动绑定 (Auto Bind Target)",
            value=True,
        )
        self.add_missing_chk = cmds.checkBox(
            label="自动向目标补充缺失骨骼 (Add Missing Influences)",
            value=True,
        )

        # 退出 columnLayout 和 frameLayout 回到 main_layout
        cmds.setParent("..")
        cmds.setParent("..")

        # --- 3. 操作按钮 ---
        cmds.frameLayout(
            label="3. 执行操作 (Actions)",
            collapsable=False,
            marginWidth=6,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.button(
            label="执行复制权重 (Copy Overlapping Weights)",
            height=38,
            backgroundColor=[0.24, 0.52, 0.35],
            command=self._on_execute_copy,
        )

        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=1,
            columnWidth2=[210, 210],
            columnAttach=[(1, "both", 2), (2, "both", 2)],
        )
        cmds.button(
            label="高亮目标重叠点 (Select Target Verts)",
            height=26,
            command=lambda *args: self._on_select_verts(select_target=True),
        )
        cmds.button(
            label="高亮源重叠点 (Select Source Verts)",
            height=26,
            command=lambda *args: self._on_select_verts(select_target=False),
        )
        cmds.setParent("..")

        # 退出 columnLayout 和 frameLayout 回到 main_layout
        cmds.setParent("..")
        cmds.setParent("..")

        # 底部状态栏
        cmds.separator(height=6, style="in")
        self.status_text = cmds.text(
            label="就绪：请载入源对象与目标对象，或直接在视口中选择后点击执行。",
            align="left",
            font="smallPlainLabelFont",
        )
        cmds.separator(height=4, style="none")

        # 尝试自动从当前选择载入
        self._auto_populate_from_selection()

        cmds.showWindow(window)

    def _set_status(self, message, is_warning=False):
        """更新状态栏文字"""
        if self.status_text and cmds.text(self.status_text, exists=True):
            cmds.text(self.status_text, edit=True, label=message)
        if is_warning:
            cmds.warning(message)
        else:
            print(message)

    def _load_selected(self, target_text_field):
        """将当前选中的节点录入指定的文本框中"""
        selection = cmds.ls(selection=True)
        if not selection:
            self._set_status("当前未选中任何对象！", is_warning=True)
            return

        node = selection[0]
        shape = get_mesh_shape(node)
        if not shape:
            self._set_status("选中的对象 [{}] 不是有效的多边形网格！".format(node), is_warning=True)
            return

        # 优先填入 transform 节点名（更整洁），若无则填 shape
        parents = cmds.listRelatives(shape, parent=True, fullPath=False) or []
        display_name = parents[0] if parents else shape
        cmds.textField(target_text_field, edit=True, text=display_name)
        self._set_status("已载入对象: {}".format(display_name))

    def _swap_objects(self, *args):
        """互换源对象和目标对象"""
        src = cmds.textField(self.src_field, query=True, text=True)
        tgt = cmds.textField(self.tgt_field, query=True, text=True)
        cmds.textField(self.src_field, edit=True, text=tgt)
        cmds.textField(self.tgt_field, edit=True, text=src)
        self._set_status("已互换源对象与目标对象。")

    def _auto_populate_from_selection(self):
        """打开窗口时如果当前选中了两个不同物体，自动填入 A 和 B"""
        selection = cmds.ls(selection=True) or []
        meshes = []
        for item in selection:
            shape = get_mesh_shape(item)
            if shape:
                parents = cmds.listRelatives(shape, parent=True, fullPath=False) or []
                name = parents[0] if parents else shape
                if name not in meshes:
                    meshes.append(name)

        if len(meshes) >= 2:
            cmds.textField(self.src_field, edit=True, text=meshes[0])
            cmds.textField(self.tgt_field, edit=True, text=meshes[1])
            self._set_status("已从视口选择自动载入 A: {}, B: {}".format(meshes[0], meshes[1]))
        elif len(meshes) == 1:
            cmds.textField(self.src_field, edit=True, text=meshes[0])

    def _get_inputs(self):
        """获取并解析界面的输入参数"""
        src = cmds.textField(self.src_field, query=True, text=True).strip()
        tgt = cmds.textField(self.tgt_field, query=True, text=True).strip()

        # 如果文本框为空，回退检查当前视口选区
        if not src or not tgt:
            selection = cmds.ls(selection=True) or []
            meshes = []
            for item in selection:
                shape = get_mesh_shape(item)
                if shape:
                    parents = cmds.listRelatives(shape, parent=True, fullPath=False) or []
                    name = parents[0] if parents else shape
                    if name not in meshes:
                        meshes.append(name)

            if len(meshes) >= 2:
                src = src or meshes[0]
                tgt = tgt or meshes[1]
                cmds.textField(self.src_field, edit=True, text=src)
                cmds.textField(self.tgt_field, edit=True, text=tgt)

        if not src or not tgt:
            self._set_status("请分别录入或选择源对象 (A) 与目标对象 (B)！", is_warning=True)
            return None

        tolerance = cmds.floatField(self.tolerance_field, query=True, value=True)
        space_idx = cmds.radioButtonGrp(self.space_radio, query=True, select=True)
        space = "world" if space_idx == 1 else "object"
        auto_bind = cmds.checkBox(self.auto_bind_chk, query=True, value=True)
        add_missing = cmds.checkBox(self.add_missing_chk, query=True, value=True)

        return {
            "source": src,
            "target": tgt,
            "tolerance": tolerance,
            "space": space,
            "auto_bind": auto_bind,
            "add_missing_influences": add_missing,
        }

    def _on_execute_copy(self, *args):
        """点击执行复制权重的回调"""
        params = self._get_inputs()
        if not params:
            return

        try:
            res = copy_overlapping_skin_weights(
                source=params["source"],
                target=params["target"],
                tolerance=params["tolerance"],
                space=params["space"],
                auto_bind=params["auto_bind"],
                add_missing_influences=params["add_missing_influences"],
                show_progress=True,
            )
            matched = res.get("matched_count", 0)
            if matched > 0:
                self._set_status(
                    "成功完成！匹配并复制了 {} 个重叠顶点的权重。".format(matched)
                )
            else:
                self._set_status("未匹配到任何重叠点，请检查容差或对象位置。", is_warning=True)
        except Exception as e:
            self._set_status("执行失败: {}".format(e), is_warning=True)

    def _on_select_verts(self, select_target=True):
        """点击高亮重叠点的回调"""
        params = self._get_inputs()
        if not params:
            return

        try:
            verts = select_overlapping_vertices(
                source=params["source"],
                target=params["target"],
                tolerance=params["tolerance"],
                space=params["space"],
                select_target=select_target,
            )
            target_desc = "目标" if select_target else "源"
            if verts:
                self._set_status("已在视口选中 {} 的 {} 个重叠点。".format(target_desc, len(verts)))
            else:
                self._set_status("未检测到重叠点，无法高亮。", is_warning=True)
        except Exception as e:
            self._set_status("高亮重叠点失败: {}".format(e), is_warning=True)


def show_ui():
    """打开工具界面的快捷入口函数"""
    ui = CopyOverlappingWeightsUI()
    ui.show()
    return ui


if __name__ == "__main__":
    show_ui()
