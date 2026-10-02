import os
import sys
import re
import codecs
import json
from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

try:
    from PySide6 import QtWidgets,QtCore,QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets,QtCore,QtGui
    from shiboken2 import wrapInstance

def maya_main_window():
    """返回Maya主窗口的QWidget实例"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ToolButton(QtWidgets.QToolButton):
    """自定义工具按钮类，支持拖放操作"""
    def __init__(self, parent=None):
        super(ToolButton, self).__init__(parent)
        self.setAcceptDrops(True)
        self.command = None
        self.sourceElement = None
        self.source_type = "python"
        self.setFixedSize(32, 32)
        self.setIconSize(QtCore.QSize(24, 24))

    def dragEnterEvent(self,event):
        from .session import drop_record
        try:drop_record(event.mimeData());event.acceptProposedAction()
        except Exception:event.ignore()

    def dropEvent(self,event):
        from .session import drop_record,apply_button
        try:apply_button(self,drop_record(event.mimeData()));event.acceptProposedAction()
        except Exception:event.ignore()

    def process_maya_shelf_button(self, button_name):
        from .session import shelf_record,apply_button
        apply_button(self,shelf_record(button_name))

    def resolve_maya_icon_path(self, icon_name):
        """解析Maya图标路径"""
        # 检查是否为完整路径
        if os.path.isfile(icon_name):
            return icon_name

        # 尝试在Maya图标路径中查找
        maya_path = os.environ.get("MAYA_LOCATION", "")
        icon_paths = [
            os.path.join(maya_path, "icons"),
            os.path.join(maya_path, "icons", "defaulticons"),
        ]

        for path in icon_paths:
            full_path = os.path.join(path, icon_name)
            if os.path.isfile(full_path):
                return full_path

        # 如果未找到图标，返回None
        return None

    def mousePressEvent(self,event):
        if event.button()==QtCore.Qt.LeftButton and self.command:
            from .session import execute_button
            try:execute_button(self,True)
            except Exception as e:QtWidgets.QMessageBox.warning(self,'执行失败',str(e))
        super(ToolButton,self).mousePressEvent(event)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QtWidgets.QMenu(self)

        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(self.edit_button)

        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(self.delete_button)

        menu.exec(event.globalPos())

    def edit_button(self):
        from .session import edit_button
        return edit_button(self)

    def delete_button(self):
        """删除按钮"""
        parent_layout = self.parent().layout()
        if parent_layout:
            parent_layout.removeWidget(self)
            self.deleteLater()

class FloatingToolbar(QtWidgets.QDialog):
    """自定义悬浮工具架"""
    def __init__(self, parent=None):
        super(FloatingToolbar, self).__init__(parent)
        self.setWindowTitle("悬浮工具架")
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 设置悬浮工具架的样式
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(60, 60, 60, 200);
                border-radius: 5px;
                border: 1px solid #555555;
            }
            QToolButton {
                background-color: rgba(80, 80, 80, 200);
                border-radius: 3px;
                border: 1px solid #666666;
            }
            QToolButton:hover {
                background-color: rgba(100, 100, 100, 200);
                border: 1px solid #888888;
            }
            QToolButton:pressed {
                background-color: rgba(40, 40, 40, 200);
            }
        """)

        # 用于窗口拖动的变量
        self.drag_position = None

        # 创建布局
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(2)

        # 创建顶部标题栏
        self.title_bar = QtWidgets.QWidget()
        self.title_bar_layout = QtWidgets.QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar_layout.setSpacing(2)

        self.title_label = QtWidgets.QLabel("悬浮工具架")
        self.title_label.setStyleSheet("color: #CCCCCC;")

        self.close_button = QtWidgets.QToolButton()
        self.close_button.setText("X")
        self.close_button.setFixedSize(16, 16)
        self.close_button.clicked.connect(self.close)

        self.title_bar_layout.addWidget(self.title_label)
        self.title_bar_layout.addStretch()
        self.title_bar_layout.addWidget(self.close_button)

        self.main_layout.addWidget(self.title_bar)

        # 创建工具栏区域
        self.toolbar_flow = FlowLayout()
        self.toolbar_flow.setSpacing(2)

        self.toolbar_widget = QtWidgets.QWidget()
        self.toolbar_widget.setLayout(self.toolbar_flow)

        self.main_layout.addWidget(self.toolbar_widget)

        # 创建底部按钮
        self.bottom_bar = QtWidgets.QWidget()
        self.bottom_bar_layout = QtWidgets.QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_bar_layout.setSpacing(2)

        self.add_button = QtWidgets.QToolButton()
        self.add_button.setText("+")
        self.add_button.setToolTip("添加空白工具按钮")
        self.add_button.clicked.connect(self.add_empty_button)

        self.clear_button = QtWidgets.QToolButton()
        self.clear_button.setText("清空")
        self.clear_button.setToolTip("清空工具架")
        self.clear_button.clicked.connect(self.clear_toolbar)

        self.save_button = QtWidgets.QToolButton()
        self.save_button.setText("保存")
        self.save_button.setToolTip("保存工具架配置")
        self.save_button.clicked.connect(self.save_config)

        self.load_button = QtWidgets.QToolButton()
        self.load_button.setText("加载")
        self.load_button.setToolTip("加载工具架配置")
        self.load_button.clicked.connect(self.load_config)

        self.bottom_bar_layout.addWidget(self.add_button)
        self.bottom_bar_layout.addWidget(self.clear_button)
        self.bottom_bar_layout.addWidget(self.save_button)
        self.bottom_bar_layout.addWidget(self.load_button)

        self.main_layout.addWidget(self.bottom_bar)

        # 初始添加一些空按钮
        for i in range(10):
            self.add_empty_button()

        # 设置窗口大小
        self.resize(200, 150)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def closeEvent(self,event):
        from . import session
        if session.window is self:session.disable_drag();session.window=None
        super(FloatingToolbar,self).closeEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def add_empty_button(self):
        """添加一个空白的工具按钮"""
        button = ToolButton()
        button.setText("")
        self.toolbar_flow.addWidget(button)

    def clear_toolbar(self):
        while self.toolbar_flow.count():
            item=self.toolbar_flow.takeAt(0)
            widget=item.widget()
            if widget:widget.setParent(None);widget.deleteLater()

    def save_config(self):
        from .session import snapshot
        from .config_io import write
        value,_=QtWidgets.QFileDialog.getSaveFileName(self,'保存到新的JSON文件','','JSON (*.json)')
        if not value:return
        try:write(value,snapshot(self))
        except Exception as e:QtWidgets.QMessageBox.warning(self,'保存失败',str(e))

    def load_config(self):
        from .session import replace_buttons
        from .config_io import read
        value,_=QtWidgets.QFileDialog.getOpenFileName(self,'加载完整工具栏配置','','JSON (*.json)')
        if not value:return
        try:replace_buttons(self,read(value))
        except Exception as e:QtWidgets.QMessageBox.warning(self,'加载失败',str(e))

class FlowLayout(QtWidgets.QLayout):
    """流式布局，用于工具按钮的排列"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin = self.contentsMargins()
        size += QtCore.QSize(2 * margin.top(), 2 * margin.top())
        return size

    def _doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX

            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

def install_tool_draggers():
    from .session import enable_drag
    return enable_drag()

def get_maya_shelf_buttons():
    """获取Maya工具架上的所有按钮"""
    shelf_buttons = []

    # 尝试获取所有工具架的名称
    shelves = cmds.layout("ShelfLayout", query=True, childArray=True) or []

    for shelf in shelves:
        # 确保当前工具架是可见的
        if cmds.shelfLayout(shelf, query=True, visible=True):
            # 获取当前工具架上的所有按钮
            shelf_children = cmds.shelfLayout(shelf, query=True, childArray=True) or []

            for child in shelf_children:
                # 检查是否为工具架按钮
                if cmds.shelfButton(child, exists=True):
                    shelf_buttons.append(child)

    return shelf_buttons

def show_floating_toolbar():
    from .session import show
    return show()
