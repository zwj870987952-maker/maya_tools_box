# -*- coding: utf-8 -*-
"""
命名空间清理工具图形界面 (Namespace Clean UI)
"""
from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False

from ...core.ui_base import (
    QtWidgets,
    QtCore,
    QtGui,
    Qt,
    get_maya_main_window,
    apply_dark_theme,
)
from .tool import NamespaceCleanTool

_CLEAN_UI_INSTANCE = None


class NamespaceCleanDialog(QtWidgets.QDialog):
    """命名空间清理工具小对话框"""

    def __init__(self, parent=None):
        super(NamespaceCleanDialog, self).__init__(parent or get_maya_main_window())
        self.setWindowTitle("命名空间清理工具 (Namespace Cleaner)")
        self.resize(460, 380)
        self.tool = NamespaceCleanTool()

        apply_dark_theme(self)
        self._build_ui()
        self._refresh_selection()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 说明
        desc = QtWidgets.QLabel(
            "清理场景中选定物体或全场景的命名空间。\n"
            "支持将本地命名空间合并至根目录 (':')，并将外部引用节点平滑迁移至根。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #bbbbbb; font-size: 11px;")
        layout.addWidget(desc)

        # 选项组
        grp = QtWidgets.QGroupBox("清理范围与模式")
        grp_layout = QtWidgets.QVBoxLayout(grp)

        self.chk_all_scene = QtWidgets.QCheckBox("清理全场景所有本地命名空间 (Process All Scene)")
        self.chk_all_scene.setChecked(False)
        self.chk_all_scene.toggled.connect(self._on_mode_changed)
        grp_layout.addWidget(self.chk_all_scene)

        self.lbl_sel_info = QtWidgets.QLabel("当前选定节点: 0 个")
        self.lbl_sel_info.setStyleSheet("color: #9cdcfe; font-weight: bold;")
        grp_layout.addWidget(self.lbl_sel_info)

        btn_refresh = QtWidgets.QPushButton("🔄 刷新视口当前选区")
        btn_refresh.clicked.connect(self._refresh_selection)
        grp_layout.addWidget(btn_refresh)

        layout.addWidget(grp)

        # 结果反馈区
        self.txt_result = QtWidgets.QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setPlaceholderText("执行结果与预检信息将显示在此处...")
        layout.addWidget(self.txt_result)

        # 底部按钮栏
        btn_layout = QtWidgets.QHBoxLayout()

        self.btn_dry_run = QtWidgets.QPushButton("🔍 安全预检 (Dry-Run)")
        self.btn_dry_run.clicked.connect(self._on_dry_run)
        btn_layout.addWidget(self.btn_dry_run)

        self.btn_execute = QtWidgets.QPushButton("⚡ 开始清理命名空间")
        self.btn_execute.setObjectName("PrimaryBtn")
        self.btn_execute.clicked.connect(self._on_execute)
        btn_layout.addWidget(self.btn_execute)

        layout.addLayout(btn_layout)

    def _refresh_selection(self):
        if not MAYA_AVAILABLE or not cmds:
            self.lbl_sel_info.setText("Maya cmds 不可用")
            return
        sel = cmds.ls(selection=True, objectsOnly=True, long=True) or []
        self.selected_nodes = sel
        self.lbl_sel_info.setText("当前视口选定节点: {} 个".format(len(sel)))

    def _on_mode_changed(self, checked):
        if checked:
            self.lbl_sel_info.setText("已开启全场景模式 (将忽略单体选区)")
        else:
            self._refresh_selection()

    def _on_dry_run(self):
        process_all = self.chk_all_scene.isChecked()
        nodes = None if process_all else (self.selected_nodes if hasattr(self, "selected_nodes") else None)

        res = self.tool.run(dry_run=True, nodes=nodes, process_all_scene=process_all)
        self.txt_result.setText(
            "【预检结果】\n状态: {}\n信息: {}\n数据: {}".format(
                "成功" if res.success else "失败",
                res.message,
                res.data
            )
        )

    def _on_execute(self):
        process_all = self.chk_all_scene.isChecked()
        nodes = None if process_all else (self.selected_nodes if hasattr(self, "selected_nodes") else None)

        res = self.tool.run(dry_run=False, nodes=nodes, process_all_scene=process_all)
        status_str = "成功" if res.success else "失败"
        self.txt_result.setText(
            "【执行完成】\n状态: {}\n信息: {}\n已清理本地命名空间: {}\n已迁移引用: {}".format(
                status_str,
                res.message,
                res.data.get("removed_local_namespaces", []),
                res.data.get("removed_reference_namespaces", [])
            )
        )
        self._refresh_selection()


def show_ui(parent=None):
    """弹出命名空间清理窗口"""
    global _CLEAN_UI_INSTANCE
    if _CLEAN_UI_INSTANCE is not None:
        try:
            _CLEAN_UI_INSTANCE.close()
            _CLEAN_UI_INSTANCE.deleteLater()
        except Exception:
            pass
        _CLEAN_UI_INSTANCE = None

    _CLEAN_UI_INSTANCE = NamespaceCleanDialog(parent=parent)
    _CLEAN_UI_INSTANCE.show()
    return _CLEAN_UI_INSTANCE
