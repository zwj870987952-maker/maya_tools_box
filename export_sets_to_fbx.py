# -*- coding: utf-8 -*-
"""
Maya 选择集批量导出 FBX 工具 (Selection Sets FBX Batch Exporter)

功能说明：
    1. 自动读取当前 Maya 场景中的所有用户选择集（objectSet），并过滤掉材质着色组及系统内置集合。
    2. 表格化展示集合列表，默认读取选择集名称作为 FBX 文件名，默认读取当前 Maya 场景文件所在目录作为导出路径。
    3. 支持勾选需要导出的选择集，支持自定义每个选择集的导出名称和保存路径。
    4. 提供便捷的批量操作：一键全选/反选、统一修改导出目录、批量添加前缀/后缀、点击行在视口高亮集合成员。
    5. 提供完善可配置的 FBX 导出参数面板（平滑组、平滑网格、三角化、切线、动画烘焙、骨骼蒙皮、BlendShape、贴图嵌入、轴向等）。
    6. 自动检测并加载 fbxmaya 插件，逐个批量导出选定对象为独立的 FBX 文件。
    7. 兼容 Maya 2017~2026+（支持 PySide2 与 PySide6，以及 Python 2/3）。

使用方法：
    1. 在 Maya 脚本编辑器（Python）或架子 (Shelf) 中运行（支持热更新）：
       import sys
       if "export_sets_to_fbx" in sys.modules:
           del sys.modules["export_sets_to_fbx"]
       import export_sets_to_fbx
       export_sets_to_fbx.show_ui()

    2. 或作为 Python API 调用：
       import export_sets_to_fbx
       export_sets_to_fbx.export_sets(
           export_items=[{"set_name": "Set_Hero", "fbx_name": "Hero.fbx", "export_dir": "D:/Export"}],
           fbx_options={...}
       )
"""

from __future__ import absolute_import, division, print_function

import os
import sys
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
        raise ImportError("当前环境中未找到 PySide2 或 PySide6，无法初始化工具图形界面。")


# ==============================================================================
# 核心数据与选择集管理
# ==============================================================================

class SetManager(object):
    """负责查询、过滤当前 Maya 场景中的选择集及其成员。"""

    # 系统内置或保留的默认集合黑名单
    SYSTEM_SET_BLACKLIST = {
        "defaultLightSet",
        "defaultObjectSet",
        "initialShadingGroup",
        "initialParticleSE",
        "defaultColorMgtGlobals",
    }

    @classmethod
    def get_scene_dir(cls):
        """
        获取当前 Maya 文件所在的目录路径。
        若当前场景未保存（Untitled），则回退返回当前 Workspace 项目目录或用户主目录。
        """
        scene_path = cmds.file(q=True, sceneName=True)
        if scene_path:
            return os.path.dirname(os.path.normpath(scene_path)).replace("\\", "/")

        # 回退至当前项目目录下的 scenes 文件夹或项目根目录
        try:
            workspace_dir = cmds.workspace(q=True, rootDirectory=True)
            if workspace_dir:
                scene_rule = cmds.workspace(fileRuleEntry="scene") or "scenes"
                scenes_dir = os.path.join(workspace_dir, scene_rule)
                if os.path.exists(scenes_dir):
                    return os.path.normpath(scenes_dir).replace("\\", "/")
                return os.path.normpath(workspace_dir).replace("\\", "/")
        except Exception:
            pass

        # 最终回退至用户目录
        return os.path.expanduser("~").replace("\\", "/")

    @classmethod
    def is_user_selection_set(cls, set_node):
        """判断一个 objectSet 节点是否为合法的用户选择集。"""
        if not cmds.objExists(set_node):
            return False

        if set_node in cls.SYSTEM_SET_BLACKLIST:
            return False

        # 排除 shadingEngine 材质着色组
        if cmds.nodeType(set_node) == "shadingEngine":
            return False

        # 排除可渲染着色组
        try:
            if cmds.sets(set_node, q=True, renderable=True):
                return False
        except Exception:
            pass

        # 排除动画层、显示层等相关内部集合
        if set_node.startswith("renderSetupLayer_") or set_node.startswith("defaultRenderLayer"):
            return False

        return True

    @classmethod
    def get_all_selection_sets(cls):
        """
        获取当前场景中所有经过过滤的用户选择集信息列表。
        :return: list of dict: [{"name": str, "members": list, "count": int}, ...]
        """
        raw_sets = cmds.ls(type="objectSet") or []
        result = []

        for s in raw_sets:
            if not cls.is_user_selection_set(s):
                continue

            members = cmds.sets(s, q=True) or []
            result.append({
                "name": s,
                "members": members,
                "count": len(members),
            })

        # 按名称字母顺序排序
        result.sort(key=lambda x: x["name"].lower())
        return result

    @classmethod
    def select_set_members(cls, set_name, include_children=False):
        """在 Maya 视口中高亮选中指定选择集的成员"""
        if not cmds.objExists(set_name):
            return False
        members = cmds.sets(set_name, q=True) or []
        if members:
            cmds.select(members, replace=True)
            if include_children:
                cmds.select(hierarchy=True)
            return True
        else:
            cmds.select(clear=True)
            return False


# ==============================================================================
# FBX 导出设置与执行引擎
# ==============================================================================

class FBXExportEngine(object):
    """负责处理 FBX 插件状态、MEL 参数注入与批量导出逻辑。"""

    @classmethod
    def ensure_fbx_plugin(cls):
        """确保 fbxmaya 插件已正确加载"""
        if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
            try:
                cmds.loadPlugin("fbxmaya", quiet=True)
            except Exception as e:
                raise RuntimeError("无法加载 Maya FBX 插件 (fbxmaya): {}".format(e))
        return True

    @classmethod
    def apply_fbx_settings(cls, options):
        """
        根据选项字典配置 Maya 的 FBX 导出命令环境。
        :param options: dict 包含各项参数配置
        """
        cls.ensure_fbx_plugin()

        # 重置导出选项为默认基准
        mel.eval("FBXResetExport;")

        # 文件格式与版本
        is_ascii = options.get("ascii", False)
        mel.eval("FBXExportInAscii -v {};".format("true" if is_ascii else "false"))

        fbx_version = options.get("fbx_version", "FBX202000")
        if fbx_version and fbx_version != "DEFAULT":
            try:
                mel.eval('FBXExportFileVersion -v "{}";'.format(fbx_version))
            except Exception:
                pass

        # 几何体选项
        smooth_groups = options.get("smoothing_groups", True)
        mel.eval("FBXExportSmoothingGroups -v {};".format("true" if smooth_groups else "false"))

        smooth_mesh = options.get("smooth_mesh", False)
        mel.eval("FBXExportSmoothMesh -v {};".format("true" if smooth_mesh else "false"))

        triangulate = options.get("triangulate", False)
        mel.eval("FBXExportTriangulate -v {};".format("true" if triangulate else "false"))

        tangents = options.get("tangents", False)
        mel.eval("FBXExportTangents -v {};".format("true" if tangents else "false"))

        # 变形与绑定
        skins = options.get("skins", True)
        mel.eval("FBXExportSkins -v {};".format("true" if skins else "false"))

        blend_shapes = options.get("blend_shapes", True)
        mel.eval("FBXExportShapes -v {};".format("true" if blend_shapes else "false"))

        # 动画选项
        animation = options.get("animation", False)
        mel.eval("FBXExportAnimationOnly -v false;")
        try:
            mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v {};'.format("true" if animation else "false"))
        except Exception:
            pass

        if animation:
            bake_anim = options.get("bake_animation", False)
            mel.eval("FBXExportBakeComplexAnimation -v {};".format("true" if bake_anim else "false"))
            if bake_anim:
                start_frame = options.get("start_frame", 1)
                end_frame = options.get("end_frame", 24)
                step = options.get("step", 1)
                mel.eval("FBXExportBakeComplexStart -v {};".format(start_frame))
                mel.eval("FBXExportBakeComplexEnd -v {};".format(end_frame))
                mel.eval("FBXExportBakeComplexStep -v {};".format(step))
                mel.eval("FBXExportBakeResampleAnimation -v true;")

        # 材质与贴图媒体
        embed_media = options.get("embed_media", False)
        mel.eval("FBXExportEmbeddedTextures -v {};".format("true" if embed_media else "false"))

        # 摄像机与灯光
        cameras = options.get("cameras", False)
        mel.eval("FBXExportCameras -v {};".format("true" if cameras else "false"))

        lights = options.get("lights", False)
        mel.eval("FBXExportLights -v {};".format("true" if lights else "false"))

        # 向上坐标轴 (Y / Z)
        up_axis = options.get("up_axis", "y").lower()
        if up_axis in ("y", "z"):
            mel.eval('FBXExportUpAxis "{}";'.format(up_axis))

        # 单位缩放因子
        scale_factor = float(options.get("scale_factor", 1.0))
        mel.eval("FBXExportScaleFactor {};".format(scale_factor))

        # 包括子对象 (Include Children)
        include_children = options.get("include_children", True)
        mel.eval("FBXExportIncludeChildren -v {};".format("true" if include_children else "false"))

        # 引用的资产内容 (Referenced Assets Content)
        ref_assets = options.get("referenced_assets", True)
        mel.eval("FBXExportReferencedAssetsContent -v {};".format("true" if ref_assets else "false"))

        # 输入连接 (Input Connections)
        input_conn = options.get("input_connections", False)
        mel.eval("FBXExportInputConnections -v {};".format("true" if input_conn else "false"))

    @classmethod
    def export_single_set(cls, set_name, export_path, options):
        """
        导出单个选择集中的对象到指定 FBX 文件。
        :param set_name: 选择集节点名称
        :param export_path: 完整的 FBX 目标文件路径（正斜杠）
        :param options: 导出配置字典
        :return: (bool, str) (是否成功, 消息)
        """
        if not cmds.objExists(set_name):
            return False, "选择集不存在: {}".format(set_name)

        members = cmds.sets(set_name, q=True) or []
        if not members:
            return False, "选择集 [{}] 为空，没有可导出的成员。".format(set_name)

        # 确保输出目录存在
        output_dir = os.path.dirname(export_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                return False, "创建输出目录失败 [{}]: {}".format(output_dir, e)

        # 统一转为 Unix 正斜杠路径，避免 MEL 转义错误
        clean_path = os.path.normpath(export_path).replace("\\", "/")

        # 应用 FBX 参数配置
        cls.apply_fbx_settings(options)

        # 选中选择集对象
        cmds.select(members, replace=True, noExpand=True)
        if options.get("include_children", True):
            # 同时也递归展开层级中的所有子对象，确保导出包含完整子层级
            cmds.select(hierarchy=True)

        # 执行选定对象导出 (-s 表示 Export Selection)
        mel_command = 'FBXExport -f "{}" -s;'.format(clean_path)
        try:
            mel.eval(mel_command)
        except Exception as e:
            return False, "导出 MEL 执行异常 [{}]: {}".format(set_name, e)

        if not os.path.exists(clean_path):
            return False, "导出命令完成但未检测到目标文件: {}".format(clean_path)

        return True, "成功导出: {}".format(clean_path)

    @classmethod
    def batch_export(cls, export_items, options, progress_callback=None):
        """
        批量导出多个选择集。
        :param export_items: list of dict, 每个包含:
            {
                "set_name": "...",
                "fbx_name": "...",
                "export_dir": "..."
            }
        :param options: dict FBX 参数
        :param progress_callback: 可选回调函数 progress_callback(index, total, current_item, status_msg)
        :return: dict 包含统计数据与详细日志:
            {"total": int, "success": int, "failed": int, "logs": list}
        """
        cls.ensure_fbx_plugin()

        # 记录用户当前视口选择，以便在导出完成后恢复现场
        original_selection = cmds.ls(selection=True)

        total = len(export_items)
        success_count = 0
        failed_count = 0
        logs = []

        try:
            for idx, item in enumerate(export_items):
                set_name = item["set_name"]
                fbx_name = item["fbx_name"].strip()
                export_dir = item["export_dir"].strip()

                # 规范化文件名扩展名
                if not fbx_name.lower().endswith(".fbx"):
                    fbx_name += ".fbx"

                full_path = os.path.normpath(os.path.join(export_dir, fbx_name)).replace("\\", "/")

                if progress_callback:
                    progress_callback(idx, total, item, "正在导出: {} -> {}".format(set_name, fbx_name))

                success, msg = cls.export_single_set(set_name, full_path, options)

                log_entry = {
                    "set_name": set_name,
                    "target_path": full_path,
                    "success": success,
                    "message": msg
                }
                logs.append(log_entry)

                if success:
                    success_count += 1
                else:
                    failed_count += 1

            if progress_callback:
                progress_callback(total, total, None, "全部导出任务完成！")

        finally:
            # 恢复原视口选区
            if original_selection:
                valid_sel = [x for x in original_selection if cmds.objExists(x)]
                if valid_sel:
                    cmds.select(valid_sel, replace=True)
                else:
                    cmds.select(clear=True)
            else:
                cmds.select(clear=True)

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "logs": logs
        }


# ==============================================================================
# UI 界面实现 (PySide2 / PySide6 跨版本兼容)
# ==============================================================================

class PathBrowseWidget(QtWidgets.QWidget):
    """包含路径输入框与文件夹浏览按钮的行内组件"""
    path_changed = Signal(str)

    def __init__(self, initial_path="", parent=None):
        super(PathBrowseWidget, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        self.line_edit = QtWidgets.QLineEdit(initial_path)
        self.btn_browse = QtWidgets.QPushButton("...")
        self.btn_browse.setFixedWidth(28)
        self.btn_browse.setToolTip("选择目标文件夹")

        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_browse)

        self.btn_browse.clicked.connect(self._on_browse)
        self.line_edit.textChanged.connect(self.path_changed.emit)

    def text(self):
        return self.line_edit.text().strip()

    def setText(self, path):
        self.line_edit.setText(path)

    def _on_browse(self):
        current_dir = self.text() or SetManager.get_scene_dir()
        selected_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 FBX 导出目录", current_dir
        )
        if selected_dir:
            clean_path = os.path.normpath(selected_dir).replace("\\", "/")
            self.line_edit.setText(clean_path)


class FBXBatchExportDialog(QtWidgets.QDialog):
    """主工具对话框窗口"""
    WINDOW_TITLE = "选择集批量导出 FBX 工具 (Selection Sets FBX Exporter)"
    WINDOW_OBJECT_NAME = "MayaSelectionSetsFBXBatchExporterWin"

    def __init__(self, parent=None):
        super(FBXBatchExportDialog, self).__init__(parent or self._get_maya_main_window())
        self.setObjectName(self.WINDOW_OBJECT_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(1050, 680)

        # 构建主布局
        self._init_ui()

        # 加载初始数据
        self.refresh_set_list()

    @staticmethod
    def _get_maya_main_window():
        """获取 Maya 主窗口作为 Parent 避免窗口漂移或多重实例化"""
        try:
            import maya.OpenMayaUI as omui
            if hasattr(omui.MQtUtil, "mainWindow"):
                ptr = omui.MQtUtil.mainWindow()
                if ptr is not None:
                    try:
                        import shiboken6
                        return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
                    except ImportError:
                        try:
                            import shiboken2
                            return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
                        except ImportError:
                            try:
                                import sip
                                return sip.wrapinstance(long(ptr), QtWidgets.QWidget)
                            except Exception:
                                pass
        except Exception:
            pass
        return None

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # ----------------------------------------------------------------------
        # 1. 顶部工具栏：刷新、勾选控制、过滤搜索
        # ----------------------------------------------------------------------
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.setSpacing(6)

        self.btn_refresh = QtWidgets.QPushButton("刷新列表 (Refresh)")
        self.btn_refresh.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
        self.btn_refresh.clicked.connect(self.refresh_set_list)
        top_bar.addWidget(self.btn_refresh)

        # 分隔条
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        top_bar.addWidget(line)

        # 勾选快捷按钮
        self.btn_select_all = QtWidgets.QPushButton("全选")
        self.btn_select_all.clicked.connect(lambda: self._set_all_checks(True))
        top_bar.addWidget(self.btn_select_all)

        self.btn_deselect_all = QtWidgets.QPushButton("全不选")
        self.btn_deselect_all.clicked.connect(lambda: self._set_all_checks(False))
        top_bar.addWidget(self.btn_deselect_all)

        self.btn_invert_sel = QtWidgets.QPushButton("反选")
        self.btn_invert_sel.clicked.connect(self._invert_checks)
        top_bar.addWidget(self.btn_invert_sel)

        top_bar.addSpacing(10)

        # 快捷搜索过滤
        lbl_search = QtWidgets.QLabel("搜索过滤:")
        self.edit_search = QtWidgets.QLineEdit()
        self.edit_search.setPlaceholderText("输入关键字过滤选择集名称...")
        self.edit_search.textChanged.connect(self._filter_table)
        top_bar.addWidget(lbl_search)
        top_bar.addWidget(self.edit_search)

        top_bar.addSpacing(6)

        # 热重载按钮
        self.btn_hot_reload = QtWidgets.QPushButton("🔄 热重载 (Reload)")
        self.btn_hot_reload.setToolTip("重新从磁盘加载本工具的最新 Python 代码并刷新界面")
        self.btn_hot_reload.clicked.connect(self._hot_reload_tool)
        top_bar.addWidget(self.btn_hot_reload)

        main_layout.addLayout(top_bar)

        # ----------------------------------------------------------------------
        # 2. 批量修改工具栏：统一路径、统一前缀/后缀
        # ----------------------------------------------------------------------
        batch_bar = QtWidgets.QHBoxLayout()
        batch_bar.setSpacing(6)

        lbl_batch_dir = QtWidgets.QLabel("统一修改导出路径:")
        self.edit_batch_dir = QtWidgets.QLineEdit()
        self.edit_batch_dir.setPlaceholderText("输入或浏览目标目录...")
        self.btn_batch_browse = QtWidgets.QPushButton("浏览...")
        self.btn_batch_browse.clicked.connect(self._on_batch_browse_clicked)

        self.btn_apply_batch_dir = QtWidgets.QPushButton("应用至勾选项")
        self.btn_apply_batch_dir.setStyleSheet("font-weight: bold;")
        self.btn_apply_batch_dir.clicked.connect(self._apply_batch_directory)

        batch_bar.addWidget(lbl_batch_dir)
        batch_bar.addWidget(self.edit_batch_dir)
        batch_bar.addWidget(self.btn_batch_browse)
        batch_bar.addWidget(self.btn_apply_batch_dir)

        batch_bar.addSpacing(15)

        # 批量前后缀
        lbl_prefix = QtWidgets.QLabel("加前缀:")
        self.edit_prefix = QtWidgets.QLineEdit()
        self.edit_prefix.setPlaceholderText("如 SM_")
        self.edit_prefix.setFixedWidth(70)

        lbl_suffix = QtWidgets.QLabel("加后缀:")
        self.edit_suffix = QtWidgets.QLineEdit()
        self.edit_suffix.setPlaceholderText("如 _LOD0")
        self.edit_suffix.setFixedWidth(70)

        self.btn_apply_affix = QtWidgets.QPushButton("应用命名")
        self.btn_apply_affix.clicked.connect(self._apply_prefix_suffix)

        batch_bar.addWidget(lbl_prefix)
        batch_bar.addWidget(self.edit_prefix)
        batch_bar.addWidget(lbl_suffix)
        batch_bar.addWidget(self.edit_suffix)
        batch_bar.addWidget(self.btn_apply_affix)

        main_layout.addLayout(batch_bar)

        # ----------------------------------------------------------------------
        # 3. 中间表格区域：选择集表格 (QTableWidget)
        # ----------------------------------------------------------------------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "导出", "选择集名称", "导出 FBX 文件名", "导出文件夹路径", "浏览", "成员数量"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setColumnWidth(1, 170)
        self.table.setColumnWidth(2, 200)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)

        # 单击或双击某行时，高亮 Maya 视口中的对象
        self.table.itemClicked.connect(self._on_table_item_clicked)

        main_layout.addWidget(self.table, stretch=1)

        # ----------------------------------------------------------------------
        # 4. 下方：FBX 导出参数配置 (折叠/分组框)
        # ----------------------------------------------------------------------
        grp_fbx_opts = QtWidgets.QGroupBox("FBX 导出参数设置 (FBX Export Options)")
        opts_layout = QtWidgets.QVBoxLayout(grp_fbx_opts)
        opts_layout.setContentsMargins(8, 8, 8, 8)
        opts_layout.setSpacing(6)

        # 第一行：常用几何体与格式设置
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(12)

        self.chk_smooth_groups = QtWidgets.QCheckBox("平滑组 (Smoothing Groups)")
        self.chk_smooth_groups.setChecked(True)
        row1.addWidget(self.chk_smooth_groups)

        self.chk_smooth_mesh = QtWidgets.QCheckBox("平滑网格 (Smooth Mesh)")
        self.chk_smooth_mesh.setChecked(False)
        row1.addWidget(self.chk_smooth_mesh)

        self.chk_triangulate = QtWidgets.QCheckBox("三角化 (Triangulate)")
        self.chk_triangulate.setChecked(False)
        row1.addWidget(self.chk_triangulate)

        self.chk_tangents = QtWidgets.QCheckBox("切线与副法线 (Tangents)")
        self.chk_tangents.setChecked(False)
        row1.addWidget(self.chk_tangents)

        self.chk_skins = QtWidgets.QCheckBox("骨骼蒙皮 (Skins)")
        self.chk_skins.setChecked(True)
        row1.addWidget(self.chk_skins)

        self.chk_blend_shapes = QtWidgets.QCheckBox("变形目标 (Blend Shapes)")
        self.chk_blend_shapes.setChecked(True)
        row1.addWidget(self.chk_blend_shapes)

        self.chk_embed_media = QtWidgets.QCheckBox("嵌入贴图 (Embed Media)")
        self.chk_embed_media.setChecked(False)
        row1.addWidget(self.chk_embed_media)

        row1.addStretch()
        opts_layout.addLayout(row1)

        # 第二行：动画、烘焙与时间范围
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(10)

        self.chk_animation = QtWidgets.QCheckBox("导出动画 (Animation)")
        self.chk_animation.setChecked(False)
        self.chk_animation.toggled.connect(self._toggle_anim_controls)
        row2.addWidget(self.chk_animation)

        self.chk_bake_anim = QtWidgets.QCheckBox("烘焙动画 (Bake)")
        self.chk_bake_anim.setChecked(False)
        self.chk_bake_anim.setEnabled(False)
        self.chk_bake_anim.toggled.connect(self._toggle_bake_controls)
        row2.addWidget(self.chk_bake_anim)

        lbl_start = QtWidgets.QLabel("起始帧:")
        self.spn_start_frame = QtWidgets.QSpinBox()
        self.spn_start_frame.setRange(-99999, 99999)
        self.spn_start_frame.setValue(int(cmds.playbackOptions(q=True, minTime=True) or 1))
        self.spn_start_frame.setEnabled(False)
        row2.addWidget(lbl_start)
        row2.addWidget(self.spn_start_frame)

        lbl_end = QtWidgets.QLabel("结束帧:")
        self.spn_end_frame = QtWidgets.QSpinBox()
        self.spn_end_frame.setRange(-99999, 99999)
        self.spn_end_frame.setValue(int(cmds.playbackOptions(q=True, maxTime=True) or 24))
        self.spn_end_frame.setEnabled(False)
        row2.addWidget(lbl_end)
        row2.addWidget(self.spn_end_frame)

        self.btn_use_slider = QtWidgets.QPushButton("使用时间滑条范围")
        self.btn_use_slider.setEnabled(False)
        self.btn_use_slider.clicked.connect(self._sync_slider_frames)
        row2.addWidget(self.btn_use_slider)

        lbl_step = QtWidgets.QLabel("步长:")
        self.spn_step = QtWidgets.QDoubleSpinBox()
        self.spn_step.setRange(0.01, 100.0)
        self.spn_step.setValue(1.0)
        self.spn_step.setEnabled(False)
        row2.addWidget(lbl_step)
        row2.addWidget(self.spn_step)

        row2.addStretch()
        opts_layout.addLayout(row2)

        # 第三行：包含关系与连接关系 (Include & Connections)
        row_include = QtWidgets.QHBoxLayout()
        row_include.setSpacing(12)

        self.chk_include_children = QtWidgets.QCheckBox("包括子对象 (Include Children)")
        self.chk_include_children.setChecked(True)
        self.chk_include_children.setToolTip("选中父节点导出时，递归展开导出其所有子层级对象")
        row_include.addWidget(self.chk_include_children)

        self.chk_referenced_assets = QtWidgets.QCheckBox("引用的资产内容 (Referenced Assets)")
        self.chk_referenced_assets.setChecked(True)
        self.chk_referenced_assets.setToolTip("导出场景中引用的资产实体内容而非代理")
        row_include.addWidget(self.chk_referenced_assets)

        self.chk_input_connections = QtWidgets.QCheckBox("输入连接 (Input Connections)")
        self.chk_input_connections.setChecked(False)
        self.chk_input_connections.setToolTip("导出对象的输入连接网络 (如动画曲线、变形节点输入等)")
        row_include.addWidget(self.chk_input_connections)

        self.chk_cameras = QtWidgets.QCheckBox("摄像机 (Cameras)")
        self.chk_cameras.setChecked(False)
        row_include.addWidget(self.chk_cameras)

        self.chk_lights = QtWidgets.QCheckBox("灯光 (Lights)")
        self.chk_lights.setChecked(False)
        row_include.addWidget(self.chk_lights)

        row_include.addStretch()
        opts_layout.addLayout(row_include)

        # 第四行：版本、格式、轴向与快速预设
        row4 = QtWidgets.QHBoxLayout()
        row4.setSpacing(10)

        lbl_version = QtWidgets.QLabel("FBX 版本:")
        self.combo_version = QtWidgets.QComboBox()
        self.combo_version.addItems(["FBX202000", "FBX201900", "FBX201800", "FBX201600", "FBX201400", "DEFAULT"])
        row4.addWidget(lbl_version)
        row4.addWidget(self.combo_version)

        lbl_format = QtWidgets.QLabel("文件格式:")
        self.combo_format = QtWidgets.QComboBox()
        self.combo_format.addItems(["Binary (二进制)", "ASCII (文本)"])
        row4.addWidget(lbl_format)
        row4.addWidget(self.combo_format)

        lbl_axis = QtWidgets.QLabel("向上轴 (Up Axis):")
        self.combo_axis = QtWidgets.QComboBox()
        self.combo_axis.addItems(["Y", "Z"])
        row4.addWidget(lbl_axis)
        row4.addWidget(self.combo_axis)

        row4.addSpacing(15)

        # 快速预设按钮
        lbl_preset = QtWidgets.QLabel("快速预设:")
        btn_preset_static = QtWidgets.QPushButton("静态模型 (Static Mesh)")
        btn_preset_static.clicked.connect(self._apply_preset_static_mesh)
        btn_preset_skeletal = QtWidgets.QPushButton("骨骼角色 (Skeletal Mesh)")
        btn_preset_skeletal.clicked.connect(self._apply_preset_skeletal_mesh)

        row4.addWidget(lbl_preset)
        row4.addWidget(btn_preset_static)
        row4.addWidget(btn_preset_skeletal)
        row4.addStretch()

        opts_layout.addLayout(row4)
        main_layout.addWidget(grp_fbx_opts)

        # ----------------------------------------------------------------------
        # 5. 底部操作栏：导出执行按钮、进度条、状态提示
        # ----------------------------------------------------------------------
        bottom_bar = QtWidgets.QHBoxLayout()
        bottom_bar.setSpacing(8)

        self.btn_export = QtWidgets.QPushButton("批量导出勾选的选择集 (Export Selected Sets)")
        self.btn_export.setFixedHeight(38)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #2b78e4;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3b88f4;
            }
            QPushButton:pressed {
                background-color: #1b68d4;
            }
        """)
        self.btn_export.clicked.connect(self.on_export_clicked)
        bottom_bar.addWidget(self.btn_export, stretch=2)

        self.btn_open_folder = QtWidgets.QPushButton("打开导出目录")
        self.btn_open_folder.setFixedHeight(38)
        self.btn_open_folder.clicked.connect(self._open_export_folder)
        bottom_bar.addWidget(self.btn_open_folder, stretch=1)

        main_layout.addLayout(bottom_bar)

        # 进度条与状态标签
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        main_layout.addWidget(self.progress_bar)

        self.lbl_status = QtWidgets.QLabel("就绪。")
        self.lbl_status.setStyleSheet("color: #888888;")
        main_layout.addWidget(self.lbl_status)

    # --------------------------------------------------------------------------
    # 界面交互逻辑与槽函数
    # --------------------------------------------------------------------------

    def _toggle_anim_controls(self, checked):
        """动画主开关联动"""
        self.chk_bake_anim.setEnabled(checked)
        self._toggle_bake_controls(checked and self.chk_bake_anim.isChecked())

    def _toggle_bake_controls(self, checked):
        """烘焙动画联动"""
        enabled = self.chk_animation.isChecked() and self.chk_bake_anim.isChecked()
        self.spn_start_frame.setEnabled(enabled)
        self.spn_end_frame.setEnabled(enabled)
        self.btn_use_slider.setEnabled(enabled)
        self.spn_step.setEnabled(enabled)

    def _sync_slider_frames(self):
        """同步时间滑条的首尾帧"""
        start_val = int(cmds.playbackOptions(q=True, minTime=True) or 1)
        end_val = int(cmds.playbackOptions(q=True, maxTime=True) or 24)
        self.spn_start_frame.setValue(start_val)
        self.spn_end_frame.setValue(end_val)

    def _apply_preset_static_mesh(self):
        """应用静态网格预设"""
        self.chk_smooth_groups.setChecked(True)
        self.chk_smooth_mesh.setChecked(False)
        self.chk_triangulate.setChecked(False)
        self.chk_tangents.setChecked(True)
        self.chk_skins.setChecked(False)
        self.chk_blend_shapes.setChecked(False)
        self.chk_animation.setChecked(False)
        self.chk_embed_media.setChecked(False)
        self.chk_include_children.setChecked(True)
        self.chk_referenced_assets.setChecked(True)
        self.chk_input_connections.setChecked(False)
        self.set_status("已应用【静态模型 (Static Mesh)】预设。")

    def _apply_preset_skeletal_mesh(self):
        """应用骨骼网格预设"""
        self.chk_smooth_groups.setChecked(True)
        self.chk_smooth_mesh.setChecked(False)
        self.chk_triangulate.setChecked(False)
        self.chk_tangents.setChecked(False)
        self.chk_skins.setChecked(True)
        self.chk_blend_shapes.setChecked(True)
        self.chk_animation.setChecked(True)
        self.chk_bake_anim.setChecked(True)
        self.chk_include_children.setChecked(True)
        self.chk_referenced_assets.setChecked(True)
        self.chk_input_connections.setChecked(True)
        self._sync_slider_frames()
        self.set_status("已应用【骨骼角色 (Skeletal Mesh)】预设。")

    def _hot_reload_tool(self):
        """重新从磁盘加载本工具的最新 Python 代码并重建界面"""
        self.close()
        self.deleteLater()

        import sys
        mod_name = "export_sets_to_fbx"
        if mod_name in sys.modules:
            del sys.modules[mod_name]

        try:
            import export_sets_to_fbx
            export_sets_to_fbx.show_ui()
            try:
                cmds.inViewMessage(
                    amg="<hl>选择集批量导出 FBX 工具</hl> 已成功热重载！",
                    pos="topCenter",
                    fade=True
                )
            except Exception:
                pass
        except Exception as e:
            cmds.warning("热重载失败: {}".format(e))

    def set_status(self, text, is_error=False):
        """设置底部状态提示文本"""
        color = "#e64a19" if is_error else "#cccccc"
        self.lbl_status.setStyleSheet("color: {};".format(color))
        self.lbl_status.setText(text)

    def refresh_set_list(self):
        """从当前场景读取选择集并填充表格"""
        scene_dir = SetManager.get_scene_dir()
        self.edit_batch_dir.setText(scene_dir)

        sets_info = SetManager.get_all_selection_sets()
        self.table.setRowCount(len(sets_info))

        for row, info in enumerate(sets_info):
            set_name = info["name"]
            count = info["count"]

            # 列 0: 勾选框
            chk_item = QtWidgets.QTableWidgetItem()
            chk_item.setCheckState(Qt.Checked)
            chk_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, chk_item)

            # 列 1: 选择集原名称
            name_item = QtWidgets.QTableWidgetItem(set_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # 只读
            self.table.setItem(row, 1, name_item)

            # 列 2: 导出 FBX 文件名（默认选择集名称）
            fbx_name_edit = QtWidgets.QLineEdit(set_name)
            self.table.setCellWidget(row, 2, fbx_name_edit)

            # 列 3: 导出路径输入框
            path_edit = QtWidgets.QLineEdit(scene_dir)
            self.table.setCellWidget(row, 3, path_edit)

            # 列 4: 浏览按钮
            btn_browse = QtWidgets.QPushButton("...")
            btn_browse.setFixedWidth(30)
            btn_browse.setToolTip("为该选择集单独选择导出目录")
            btn_browse.clicked.connect(lambda _, r=row: self._on_row_browse_clicked(r))
            self.table.setCellWidget(row, 4, btn_browse)

            # 列 5: 成员节点数量
            count_item = QtWidgets.QTableWidgetItem("{} 个节点".format(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
            if count == 0:
                count_item.setForeground(QtGui.QBrush(QtGui.QColor(180, 100, 100)))
            self.table.setItem(row, 5, count_item)

        self._filter_table(self.edit_search.text())
        self.set_status("已读取当前场景中的 {} 个选择集。默认路径: {}".format(len(sets_info), scene_dir))

    def _set_all_checks(self, checked_state):
        """全选或全不选"""
        state = Qt.Checked if checked_state else Qt.Unchecked
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    item.setCheckState(state)

    def _invert_checks(self):
        """反向勾选"""
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    new_state = Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
                    item.setCheckState(new_state)

    def _filter_table(self, keyword):
        """根据关键字隐藏/显示表格行"""
        keyword = keyword.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if not item:
                continue
            set_name = item.text().lower()
            match = (keyword in set_name) if keyword else True
            self.table.setRowHidden(row, not match)

    def _on_table_item_clicked(self, item):
        """单击表格某行时，在 Maya 视口高亮显示该选择集成员"""
        row = item.row()
        name_item = self.table.item(row, 1)
        if name_item:
            set_name = name_item.text()
            include_children = self.chk_include_children.isChecked()
            has_members = SetManager.select_set_members(set_name, include_children=include_children)
            if not has_members:
                self.set_status("选择集 [{}] 中未包含有效对象。".format(set_name))
            else:
                self.set_status("已在视口中选中集合 [{}] 的成员{}。".format(
                    set_name, " (含子对象)" if include_children else ""
                ))

    def _on_row_browse_clicked(self, row):
        """单行浏览文件夹按钮点击"""
        path_edit = self.table.cellWidget(row, 3)
        current_dir = path_edit.text().strip() if path_edit else SetManager.get_scene_dir()
        selected_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 FBX 导出目录", current_dir
        )
        if selected_dir:
            clean_path = os.path.normpath(selected_dir).replace("\\", "/")
            if path_edit:
                path_edit.setText(clean_path)

    def _on_batch_browse_clicked(self):
        """批量修改路径浏览按钮"""
        current_dir = self.edit_batch_dir.text().strip() or SetManager.get_scene_dir()
        selected_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择统一导出目录", current_dir
        )
        if selected_dir:
            clean_path = os.path.normpath(selected_dir).replace("\\", "/")
            self.edit_batch_dir.setText(clean_path)

    def _apply_batch_directory(self):
        """将顶部统一路径应用至所有勾选的行"""
        target_dir = self.edit_batch_dir.text().strip()
        if not target_dir:
            QtWidgets.QMessageBox.warning(self, "警告", "请先输入或选择有效的统一导出目录！")
            return

        applied_count = 0
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                path_edit = self.table.cellWidget(row, 3)
                if path_edit:
                    path_edit.setText(target_dir)
                    applied_count += 1

        self.set_status("已将导出路径应用至 {} 个勾选的选择集。".format(applied_count))

    def _apply_prefix_suffix(self):
        """为所有勾选的项批量添加前缀或后缀"""
        prefix = self.edit_prefix.text().strip()
        suffix = self.edit_suffix.text().strip()
        if not prefix and not suffix:
            QtWidgets.QMessageBox.information(self, "提示", "请输入需要添加的前缀或后缀。")
            return

        applied_count = 0
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                name_widget = self.table.cellWidget(row, 2)
                if name_widget:
                    original = name_widget.text().strip()
                    # 移除原有的 .fbx 后缀处理
                    base = original[:-4] if original.lower().endswith(".fbx") else original
                    new_name = "{}{}{}".format(prefix, base, suffix)
                    name_widget.setText(new_name)
                    applied_count += 1

        self.set_status("已为 {} 个勾选项更新导出名称。".format(applied_count))

    def _open_export_folder(self):
        """打开第一个有效勾选项的导出目录或当前场景目录"""
        target_dir = ""
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                path_edit = self.table.cellWidget(row, 3)
                if path_edit and path_edit.text().strip():
                    target_dir = path_edit.text().strip()
                    break

        if not target_dir:
            target_dir = self.edit_batch_dir.text().strip() or SetManager.get_scene_dir()

        if target_dir and os.path.exists(target_dir):
            try:
                os.startfile(os.path.normpath(target_dir))
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "错误", "无法打开目录 [{}]: {}".format(target_dir, e))
        else:
            QtWidgets.QMessageBox.warning(self, "提示", "目录尚不存在: {}".format(target_dir))

    def get_export_items(self):
        """从表格中收集所有勾选的导出项列表"""
        items = []
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if not chk_item or chk_item.checkState() != Qt.Checked:
                continue

            name_item = self.table.item(row, 1)
            set_name = name_item.text() if name_item else ""

            fbx_edit = self.table.cellWidget(row, 2)
            fbx_name = fbx_edit.text().strip() if fbx_edit else set_name

            path_edit = self.table.cellWidget(row, 3)
            export_dir = path_edit.text().strip() if path_edit else SetManager.get_scene_dir()

            items.append({
                "set_name": set_name,
                "fbx_name": fbx_name or set_name,
                "export_dir": export_dir
            })

        return items

    def get_fbx_options(self):
        """从界面控件读取当前的 FBX 导出选项字典"""
        is_ascii = (self.combo_format.currentIndex() == 1)
        fbx_ver = self.combo_version.currentText()
        up_axis = self.combo_axis.currentText().lower()

        return {
            "ascii": is_ascii,
            "fbx_version": fbx_ver,
            "up_axis": up_axis,
            "smoothing_groups": self.chk_smooth_groups.isChecked(),
            "smooth_mesh": self.chk_smooth_mesh.isChecked(),
            "triangulate": self.chk_triangulate.isChecked(),
            "tangents": self.chk_tangents.isChecked(),
            "skins": self.chk_skins.isChecked(),
            "blend_shapes": self.chk_blend_shapes.isChecked(),
            "embed_media": self.chk_embed_media.isChecked(),
            "include_children": self.chk_include_children.isChecked(),
            "referenced_assets": self.chk_referenced_assets.isChecked(),
            "input_connections": self.chk_input_connections.isChecked(),
            "animation": self.chk_animation.isChecked(),
            "bake_animation": self.chk_bake_anim.isChecked(),
            "start_frame": self.spn_start_frame.value(),
            "end_frame": self.spn_end_frame.value(),
            "step": self.spn_step.value(),
            "cameras": self.chk_cameras.isChecked(),
            "lights": self.chk_lights.isChecked(),
            "scale_factor": 1.0,
        }

    def on_export_clicked(self):
        """点击批量导出执行"""
        items = self.get_export_items()
        if not items:
            QtWidgets.QMessageBox.warning(self, "提示", "请至少勾选一个需要导出的选择集！")
            return

        options = self.get_fbx_options()

        # 提示用户确认
        confirm_msg = "即将批量导出 {} 个选择集为 FBX 文件。\n是否继续？".format(len(items))
        reply = QtWidgets.QMessageBox.question(
            self, "确认导出", confirm_msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 准备进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(items))
        self.progress_bar.setValue(0)
        self.btn_export.setEnabled(False)

        def progress_cb(idx, total, current_item, msg):
            self.progress_bar.setValue(idx)
            self.set_status(msg)
            QtWidgets.QApplication.processEvents()

        try:
            results = FBXExportEngine.batch_export(
                export_items=items,
                options=options,
                progress_callback=progress_cb
            )

            # 导出完成后的报告
            total = results["total"]
            success = results["success"]
            failed = results["failed"]

            summary_text = "批量导出完成！\n总计: {}\n成功: {}\n失败: {}".format(
                total, success, failed
            )

            if failed > 0:
                failed_details = [
                    "• {}: {}".format(log["set_name"], log["message"])
                    for log in results["logs"] if not log["success"]
                ]
                summary_text += "\n\n失败项详情:\n" + "\n".join(failed_details[:10])
                if len(failed_details) > 10:
                    summary_text += "\n...（更多详见控制台输出）"

                QtWidgets.QMessageBox.warning(self, "导出完成（存在失败项）", summary_text)
                self.set_status("导出完成，存在 {} 个失败项，请检查！".format(failed), is_error=True)
            else:
                QtWidgets.QMessageBox.information(self, "导出成功", summary_text)
                self.set_status("所有 {} 个选择集已成功导出！".format(success))

        except Exception as e:
            err_trace = traceback.format_exc()
            cmds.warning("批量导出 FBX 过程中发生异常: {}".format(err_trace))
            QtWidgets.QMessageBox.critical(self, "导出失败", "批量导出过程中发生未捕获异常:\n{}".format(e))
            self.set_status("导出失败: {}".format(e), is_error=True)

        finally:
            self.progress_bar.setVisible(False)
            self.btn_export.setEnabled(True)


# ==============================================================================
# 单例管理与启动入口
# ==============================================================================

_GLOBAL_FBX_EXPORT_DIALOG = None

def show_ui():
    """
    打开选择集批量导出 FBX 工具界面的入口函数。
    支持自动关闭旧实例，保证单例运行。
    """
    global _GLOBAL_FBX_EXPORT_DIALOG

    if _GLOBAL_FBX_EXPORT_DIALOG is not None:
        try:
            _GLOBAL_FBX_EXPORT_DIALOG.close()
            _GLOBAL_FBX_EXPORT_DIALOG.deleteLater()
        except Exception:
            pass
        _GLOBAL_FBX_EXPORT_DIALOG = None

    _GLOBAL_FBX_EXPORT_DIALOG = FBXBatchExportDialog()
    _GLOBAL_FBX_EXPORT_DIALOG.show()
    return _GLOBAL_FBX_EXPORT_DIALOG


def export_sets(export_items, fbx_options=None):
    """
    非 UI 纯脚本函数式批量导出接口。
    :param export_items: list of dict, 每个元素形如:
        {"set_name": "MySet", "fbx_name": "MyModel.fbx", "export_dir": "D:/Export"}
    :param fbx_options: dict FBX导出配置（若为 None 则使用默认推荐配置）
    :return: dict 批量导出结果
    """
    if fbx_options is None:
        fbx_options = {
            "ascii": False,
            "fbx_version": "FBX202000",
            "up_axis": "y",
            "smoothing_groups": True,
            "smooth_mesh": False,
            "triangulate": False,
            "tangents": False,
            "skins": True,
            "blend_shapes": True,
            "embed_media": False,
            "include_children": True,
            "referenced_assets": True,
            "input_connections": False,
            "animation": False,
            "cameras": False,
            "lights": False,
        }
    return FBXExportEngine.batch_export(export_items, fbx_options)


if __name__ == "__main__":
    show_ui()
