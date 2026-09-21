import os
import sys
import json
from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

# 全局变量
FLOATING_TOOLBAR_WINDOW = None

def maya_main_window():
    """返回Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ToolButton(QtWidgets.QToolButton):
    """工具按钮，支持从Maya工具架拖拽"""
    def __init__(self, parent=None):
        super(ToolButton, self).__init__(parent)
        self.setAcceptDrops(True)
        self.command = None
        self.sourceElement = None
        self.setFixedSize(32, 32)
        self.setIconSize(QtCore.QSize(24, 24))
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            # 获取工具架按钮名称
            button_name = event.mimeData().text()
            self.process_maya_shelf_button(button_name)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def process_maya_shelf_button(self, button_name):
        """处理从Maya工具架拖拽的按钮"""
        try:
            if cmds.shelfButton(button_name, exists=True):
                # 获取命令
                self.command = cmds.shelfButton(button_name, query=True, command=True)
                
                # 获取源元素名称
                self.sourceElement = cmds.shelfButton(button_name, query=True, label=True) or button_name
                
                # 获取图标
                icon_path = cmds.shelfButton(button_name, query=True, image=True)
                if icon_path:
                    maya_path = os.environ.get("MAYA_LOCATION", "")
                    full_path = os.path.join(maya_path, "icons", icon_path)
                    if os.path.exists(full_path):
                        self.setIcon(QtGui.QIcon(full_path))
                    else:
                        self.setText(self.sourceElement)
                else:
                    self.setText(self.sourceElement)
            else:
                self.setText(button_name)
        except Exception as e:
            cmds.warning(f"处理工具架按钮失败: {str(e)}")
            self.setText(button_name)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.command:
            try:
                if self.command and self.command.endswith(";"):
                    mel.eval(self.command)
                elif self.command:
                    eval(self.command)
            except Exception as e:
                cmds.warning(f"执行命令失败: {str(e)}")
        super(ToolButton, self).mousePressEvent(event)
        
    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QtWidgets.QMenu(self)
        
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(self.edit_button)
        
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(self.delete_button)
        
        menu.exec_(event.globalPos())
        
    def edit_button(self):
        """编辑按钮属性"""
        dialog = QtWidgets.QDialog(self.parent())
        dialog.setWindowTitle("编辑工具按钮")
        dialog.setMinimumWidth(300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        form_layout = QtWidgets.QFormLayout()
        
        name_edit = QtWidgets.QLineEdit(self.sourceElement or "")
        form_layout.addRow("名称:", name_edit)
        
        command_edit = QtWidgets.QTextEdit(self.command or "")
        command_edit.setMinimumHeight(100)
        form_layout.addRow("命令:", command_edit)
        
        layout.addLayout(form_layout)
        
        button_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("保存")
        cancel_button = QtWidgets.QPushButton("取消")
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.sourceElement = name_edit.text()
            self.command = command_edit.toPlainText()
            
            if not self.icon():
                self.setText(self.sourceElement)
    
    def delete_button(self):
        """删除按钮"""
        parent_layout = self.parent().layout()
        if parent_layout:
            parent_layout.removeWidget(self)
            self.deleteLater()

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

class FloatingToolbar(QtWidgets.QDialog):
    """自定义悬浮工具架"""
    def __init__(self, parent=maya_main_window()):
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
        """清空工具架上的所有按钮"""
        for i in reversed(range(self.toolbar_flow.count())):
            item = self.toolbar_flow.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
                
    def save_config(self):
        """保存工具架配置"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存工具架配置", "", "工具架配置文件 (*.json)"
        )
        
        if not file_path:
            return
            
        config = []
        for i in range(self.toolbar_flow.count()):
            item = self.toolbar_flow.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ToolButton):
                button = item.widget()
                button_data = {
                    "command": button.command,
                    "source_element": button.sourceElement,
                    "text": button.text()
                }
                config.append(button_data)
                
        try:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
            cmds.warning(f"工具架配置已保存到: {file_path}")
        except Exception as e:
            cmds.warning(f"保存工具架配置失败: {str(e)}")
            
    def load_config(self):
        """加载工具架配置"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "加载工具架配置", "", "工具架配置文件 (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                
            self.clear_toolbar()
            
            for button_data in config:
                button = ToolButton()
                button.command = button_data.get("command", "")
                button.sourceElement = button_data.get("source_element", "")
                button.setText(button_data.get("text", ""))
                self.toolbar_flow.addWidget(button)
                
            cmds.warning(f"工具架配置已加载: {file_path}")
        except Exception as e:
            cmds.warning(f"加载工具架配置失败: {str(e)}")

def install_drag_support():
    """为Maya工具架按钮添加拖拽功能"""
    try:
        shelf_buttons = get_maya_shelf_buttons()
        for button_name in shelf_buttons:
            try:
                # 设置工具架按钮支持拖拽
                shelf_button = button_name
                if cmds.shelfButton(shelf_button, exists=True):
                    # 添加拖拽支持
                    orig_command = cmds.shelfButton(shelf_button, query=True, command=True) or ""
                    drag_command = f"""
import maya.cmds as cmds
from functools import partial
import maya.mel as mel

# 执行原始命令
orig_command = '''{orig_command}'''
if orig_command:
    if orig_command.endswith(';'):
        mel.eval(orig_command)
    else:
        eval(orig_command)

# 使用右键拖拽复制
if cmds.popupMenu('dragMenu_{shelf_button}', exists=True):
    cmds.deleteUI('dragMenu_{shelf_button}')

def startDrag(*args):
    cmds.warning('请拖动此按钮到悬浮工具架上')

"""
                    # 设置右键菜单为拖拽源
                    cmds.shelfButton(shelf_button, edit=True, dragCallback=f"python(\"print('拖拽开始: {shelf_button}')\")")
            except Exception as e:
                cmds.warning(f"为按钮 {button_name} 添加拖拽功能失败: {str(e)}")
    except Exception as e:
        cmds.warning(f"安装拖拽支持失败: {str(e)}")

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
    """显示悬浮工具架"""
    global FLOATING_TOOLBAR_WINDOW
    
    try:
        if FLOATING_TOOLBAR_WINDOW:
            FLOATING_TOOLBAR_WINDOW.close()
            FLOATING_TOOLBAR_WINDOW.deleteLater()
    except:
        pass
        
    FLOATING_TOOLBAR_WINDOW = FloatingToolbar()
    FLOATING_TOOLBAR_WINDOW.show()
    
    # 为Maya工具架按钮添加拖拽功能
    install_drag_support()
    
    return FLOATING_TOOLBAR_WINDOW

def help_dialog():
    """显示帮助信息"""
    help_text = """
    悬浮工具架使用指南:
    
    1. 从Maya工具架拖拽工具到悬浮工具架上
    2. 点击'+'按钮添加空白工具按钮
    3. 右键工具按钮可以编辑或删除
    4. 点击'保存'按钮保存工具架配置
    5. 点击'加载'按钮加载已保存的工具架配置
    6. 点击'清空'按钮清空工具架
    
    您可以通过拖动工具架的顶部移动工具架的位置。
    """
    
    cmds.confirmDialog(
        title="悬浮工具架帮助", 
        message=help_text, 
        button=["确定"], 
        defaultButton="确定"
    )

# 直接运行此脚本时显示工具架
if __name__ == "__main__":
    show_floating_toolbar()
    cmds.warning("悬浮工具架已启动，将工具从Maya工具架拖到悬浮工具架上即可使用。") 