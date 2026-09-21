# -*- coding: utf-8 -*-
"""
UI 基础支撑层：跨版本兼容 PySide2/PySide6、安全获取 Maya 主窗口与统一深色样式表。
"""
from __future__ import absolute_import, division, print_function

import sys

# 兼容导入 PySide2 (Maya 2017~2024) / PySide6 (Maya 2025+)
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, Signal
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt
        from PySide2.QtCore import Signal
        PYSIDE_VERSION = 2
    except ImportError:
        QtCore = QtGui = QtWidgets = Qt = Signal = None
        PYSIDE_VERSION = 0


def get_maya_main_window():
    """
    安全获取 Maya 主窗口作为 Qt 对话框的父窗口指针，避免子窗口沉底或在任务栏产生孤儿图标。
    支持 Maya 2017 ~ 2026+。若处于无 GUI 环境或外部命令行，则安全返回 None。
    """
    if not QtWidgets:
        return None

    try:
        import maya.OpenMayaUI as omui
        ptr = omui.MQtUtil.mainWindow()
        if not ptr:
            return None

        # Maya 2025+ (Python 3.11 / PySide6)
        try:
            from shiboken6 import wrapInstance
            return wrapInstance(int(ptr), QtWidgets.QWidget)
        except ImportError:
            pass

        # Maya 2017~2024 (PySide2)
        try:
            from shiboken2 import wrapInstance
            return wrapInstance(int(ptr), QtWidgets.QWidget)
        except ImportError:
            pass

    except Exception:
        pass

    # 回退尝试查找活动顶层窗口
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            for w in app.topLevelWidgets():
                if "Maya" in w.windowTitle():
                    return w
    except Exception:
        pass

    return None


STANDARD_DARK_QSS = """
QDialog, QMainWindow, QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 12px;
    font-weight: bold;
    color: #9cdcfe;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #383838;
    color: #f0f0f0;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px 12px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #484848;
    border-color: #007acc;
}
QPushButton:pressed {
    background-color: #1f1f1f;
}
QPushButton:disabled {
    background-color: #2d2d2d;
    color: #777777;
    border-color: #3a3a3a;
}
QPushButton#PrimaryBtn {
    background-color: #0e639c;
    border: 1px solid #1177bb;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#PrimaryBtn:hover {
    background-color: #1177bb;
}
QPushButton#SuccessBtn {
    background-color: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#SuccessBtn:hover {
    background-color: #2ea043;
}
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 6px;
    color: #f0f0f0;
    selection-background-color: #094771;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #007acc;
}
QTableWidget, QTreeWidget, QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    gridline-color: #2e2e2e;
    selection-background-color: #094771;
    selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #252526;
    color: #cccccc;
    padding: 4px 8px;
    border: 1px solid #333333;
    font-weight: bold;
}
QProgressBar {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 3px;
    text-align: center;
    color: #ffffff;
}
QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 2px;
}
QScrollBar:vertical {
    border: none;
    background: #202020;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #555555;
}
"""


def apply_dark_theme(widget):
    """为指定的 Qt 对话框或主窗口应用统一的 Maya 工具箱深色样式表"""
    if widget and hasattr(widget, "setStyleSheet"):
        widget.setStyleSheet(STANDARD_DARK_QSS)
