# -*- coding: utf-8 -*-
"""
Maya 生产力工具箱主控制台 (Maya Toolkit Launcher)
整合 6 大核心生产力工具，提供一站式图形化启动、分类筛选与工具架快捷集成。
"""
from __future__ import absolute_import, division, print_function

import os
import sys

try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    cmds = mel = None
    MAYA_AVAILABLE = False

from ..core.ui_base import (
    QtWidgets,
    QtCore,
    QtGui,
    Qt,
    get_maya_main_window,
    apply_dark_theme,
)
from ..framework.registry import ToolRegistry

_LAUNCHER_INSTANCE = None


class ToolCardWidget(QtWidgets.QFrame):
    """单个工具的卡片展示控件"""

    def __init__(self, tool_instance, parent=None):
        super(ToolCardWidget, self).__init__(parent)
        self.tool = tool_instance
        self.setObjectName("ToolCard")
        self.setStyleSheet("""
            QFrame#ToolCard {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame#ToolCard:hover {
                border-color: #007acc;
                background-color: #2a2d2e;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 顶部标题栏（分类徽章 + 工具名称 + 版本）
        top_row = QtWidgets.QHBoxLayout()

        cat_badge = QtWidgets.QLabel(self.tool.category.upper())
        cat_badge.setStyleSheet("""
            background-color: #0e639c;
            color: #ffffff;
            font-size: 10px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
        """)

        title_label = QtWidgets.QLabel(self.tool.tool_name)
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")

        ver_label = QtWidgets.QLabel("v" + getattr(self.tool, "version", "1.0.0"))
        ver_label.setStyleSheet("color: #888888; font-size: 10px;")

        top_row.addWidget(cat_badge)
        top_row.addWidget(title_label)
        top_row.addStretch()
        top_row.addWidget(ver_label)
        layout.addLayout(top_row)

        # 中间：描述文本
        desc_label = QtWidgets.QLabel(self.tool.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #bbbbbb; font-size: 11px; line-height: 1.4;")
        layout.addWidget(desc_label)

        # 底部操作栏
        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.addStretch()

        id_tag = QtWidgets.QLabel("ID: {}".format(self.tool.tool_id))
        id_tag.setStyleSheet("color: #666666; font-size: 10px; font-family: Consolas, monospace;")
        bottom_row.addWidget(id_tag)
        bottom_row.addSpacing(8)

        self.btn_launch = QtWidgets.QPushButton("🚀 打开界面")
        self.btn_launch.setObjectName("PrimaryBtn")
        self.btn_launch.setCursor(Qt.PointingHandCursor)
        self.btn_launch.setFixedWidth(100)
        self.btn_launch.clicked.connect(self._on_launch_clicked)
        bottom_row.addWidget(self.btn_launch)

        layout.addLayout(bottom_row)

    def _on_launch_clicked(self):
        try:
            self.tool.show_ui(parent=self.window())
        except Exception as e:
            if QtWidgets:
                QtWidgets.QMessageBox.critical(
                    self, "启动失败", "无法启动工具 [{}]:\n{}".format(self.tool.tool_name, str(e))
                )


class MayaToolkitLauncher(QtWidgets.QDialog):
    """Maya 工具箱主控制台主窗口"""

    WINDOW_TITLE = "Maya 生产力工具箱 (Toolkit Launcher v2.0)"

    def __init__(self, parent=None):
        super(MayaToolkitLauncher, self).__init__(parent or get_maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(720, 680)
        self.setMinimumSize(580, 500)
        self.cards = []

        apply_dark_theme(self)
        self._build_ui()
        self._populate_tools()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. 顶部 Hero Banner
        banner_box = QtWidgets.QFrame()
        banner_box.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2936, stop:1 #223344);
                border: 1px solid #2d455d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        b_layout = QtWidgets.QHBoxLayout(banner_box)

        title_vbox = QtWidgets.QVBoxLayout()
        h_title = QtWidgets.QLabel("Maya 生产力工具箱 (Maya Toolkit)")
        h_font = QtGui.QFont()
        h_font.setBold(True)
        h_font.setPointSize(12)
        h_title.setFont(h_font)
        h_title.setStyleSheet("color: #ffffff;")

        h_sub = QtWidgets.QLabel("工业级 Maya 生产力工具集 & 大模型 (LLM / Agent) 脚本调用统一框架")
        h_sub.setStyleSheet("color: #9cdcfe; font-size: 11px;")

        title_vbox.addWidget(h_title)
        title_vbox.addWidget(h_sub)
        b_layout.addLayout(title_vbox)
        b_layout.addStretch()

        btn_shelf = QtWidgets.QPushButton("⭐ 安装到工具架")
        btn_shelf.setObjectName("SuccessBtn")
        btn_shelf.setToolTip("一键在当前 Maya 工具架上生成快速启动按钮")
        btn_shelf.clicked.connect(self._on_install_shelf_clicked)
        b_layout.addWidget(btn_shelf)

        main_layout.addWidget(banner_box)

        # 2. 搜索与分类过滤栏
        filter_row = QtWidgets.QHBoxLayout()

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索工具名称、ID 或功能关键词...")
        self.search_edit.textChanged.connect(self._filter_tools)
        filter_row.addWidget(self.search_edit)

        self.cat_combo = QtWidgets.QComboBox()
        self.cat_combo.addItems(["全部类别 (All)", "Pipeline", "Modeling", "Rigging", "Animation"])
        self.cat_combo.currentIndexChanged.connect(self._filter_tools)
        self.cat_combo.setFixedWidth(150)
        filter_row.addWidget(self.cat_combo)

        main_layout.addLayout(filter_row)

        # 3. 中间工具滚动卡片列表
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area)

        # 4. 底部状态与链接栏
        status_row = QtWidgets.QHBoxLayout()
        self.lbl_count = QtWidgets.QLabel("共加载 0 个工具")
        self.lbl_count.setStyleSheet("color: #777777; font-size: 11px;")
        status_row.addWidget(self.lbl_count)
        status_row.addStretch()

        lbl_tip = QtWidgets.QLabel("支持大模型调取: maya_toolkit.execute_tool(tool_id, args)")
        lbl_tip.setStyleSheet("color: #4ec9b0; font-size: 11px; font-family: Consolas, monospace;")
        status_row.addWidget(lbl_tip)

        main_layout.addLayout(status_row)

    def _populate_tools(self):
        # 清空已有
        for card in self.cards:
            card.setParent(None)
        self.cards = []

        tools = ToolRegistry.list_tools()
        for t_info in tools:
            tool_obj = ToolRegistry.get(t_info["tool_id"])
            if tool_obj:
                card = ToolCardWidget(tool_obj, parent=self.cards_container)
                self.cards.append(card)
                # 插入到最下方 stretch 之前
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        self._filter_tools()

    def _filter_tools(self):
        kw = self.search_edit.text().strip().lower()
        selected_cat = self.cat_combo.currentText().split(" ")[0]

        visible_count = 0
        for card in self.cards:
            t = card.tool
            matches_kw = (
                not kw
                or kw in t.tool_id.lower()
                or kw in t.tool_name.lower()
                or kw in t.description.lower()
            )
            matches_cat = (
                selected_cat == "全部类别"
                or selected_cat.lower() == t.category.lower()
            )

            if matches_kw and matches_cat:
                card.show()
                visible_count += 1
            else:
                card.hide()

        self.lbl_count.setText("显示 {} / {} 个工具".format(visible_count, len(self.cards)))

    def _on_install_shelf_clicked(self):
        install_shelf_button()


def install_shelf_button(root_dir=None):
    """一键在当前活动工具架上创建统一工具箱启动按钮"""
    if not MAYA_AVAILABLE or not cmds:
        print("[Maya Toolkit] 仅在 Maya GUI 环境下支持工具架按钮安装。")
        return None

    current_dir = root_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    norm_root = os.path.normpath(current_dir).replace("\\", "/")

    current_shelf = "Custom"
    try:
        shelf_top = mel.eval("global string $gShelfTopLevel; string $res = $gShelfTopLevel;")
        if shelf_top and cmds.tabLayout(shelf_top, exists=True):
            current_shelf = cmds.tabLayout(shelf_top, query=True, selectTab=True) or "Custom"
    except Exception:
        pass

    if not cmds.shelfLayout(current_shelf, exists=True):
        print("[Maya Toolkit] 当前处于无 GUI 工具架环境，跳过安装。")
        return None

    btn_tag = "MayaToolkitMainShelfBtn"

    try:
        children = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
        for child in children:
            if cmds.shelfButton(child, exists=True):
                tag = cmds.shelfButton(child, query=True, docTag=True)
                if tag == btn_tag:
                    cmds.deleteUI(child)
    except Exception:
        pass

    cmd_code = (
        "import sys\n"
        "root = r'{root}'\n"
        "if root not in sys.path:\n"
        "    sys.path.insert(0, root)\n"
        "import maya_toolkit\n"
        "maya_toolkit.show_ui()\n"
    ).format(root=norm_root)

    icon_path = os.path.join(norm_root, "icons", "toolbox.png")
    if not os.path.isfile(icon_path):
        icon_path = os.path.join(norm_root, "icons", "render_phong.png")
    if not os.path.isfile(icon_path):
        icon_path = "commandButton.png"

    btn = cmds.shelfButton(
        parent=current_shelf,
        label="Maya生产力工具箱",
        annotation="【Maya 生产力工具箱】一站式启动 FBX 比对/材质传递/权重复制/旋转修正/命名空间清理",
        imageOverlayLabel="BOX",
        image=icon_path,
        command=cmd_code,
        sourceType="python",
        docTag=btn_tag
    )

    try:
        cmds.inViewMessage(
            amg="<span style=\"color:#4cd964;font-weight:bold;\">Maya 生产力工具箱</span> 已成功安装到工具架: <span style=\"color:#ffd60a;\">[{}]</span>".format(current_shelf),
            pos="midCenter",
            fade=True,
            fadeInTime=100,
            fadeOutTime=200,
            fadeStayTime=2500
        )
    except Exception:
        pass

    print("[Maya Toolkit] 已在工具架 [{}] 创建统一工具箱启动按钮。".format(current_shelf))
    return btn


def show_launcher(parent=None):
    """打开 Maya 工具箱主控制台单例窗口"""
    global _LAUNCHER_INSTANCE
    if _LAUNCHER_INSTANCE is not None:
        try:
            _LAUNCHER_INSTANCE.close()
            _LAUNCHER_INSTANCE.deleteLater()
        except Exception:
            pass
        _LAUNCHER_INSTANCE = None

    _LAUNCHER_INSTANCE = MayaToolkitLauncher(parent=parent)
    _LAUNCHER_INSTANCE.show()
    return _LAUNCHER_INSTANCE
