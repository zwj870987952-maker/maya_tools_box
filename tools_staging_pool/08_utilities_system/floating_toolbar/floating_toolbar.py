import os
import sys
import re
import codecs
import json
from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets, QtCore, QtGui
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
        self.setFixedSize(32, 32)
        self.setIconSize(QtCore.QSize(24, 24))
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-maya-data") or event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-maya-data"):
            source_data = event.mimeData().data("application/x-maya-data")
            data_stream = QtCore.QDataStream(source_data, QtCore.QIODevice.ReadOnly)
            
            command = data_stream.readQString()
            source_element = data_stream.readQString()
            icon_path = data_stream.readQString()
            
            self.command = command
            self.sourceElement = source_element
            
            if icon_path and os.path.exists(icon_path):
                self.setIcon(QtGui.QIcon(icon_path))
            else:
                self.setText(source_element)
                
            event.acceptProposedAction()
        elif event.mimeData().hasFormat("text/plain"):
            # 处理从Maya原生工具架拖拽
            shelf_button_name = event.mimeData().text()
            self.process_maya_shelf_button(shelf_button_name)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def process_maya_shelf_button(self, button_name):
        """处理从Maya工具架拖拽的按钮"""
        try:
            # 从按钮名称获取工具架的命令和图标
            if cmds.shelfButton(button_name, exists=True):
                # 获取命令
                command = cmds.shelfButton(button_name, query=True, command=True)
                self.command = command
                
                # 获取源元素名称
                source_element = cmds.shelfButton(button_name, query=True, label=True) or button_name
                self.sourceElement = source_element
                
                # 获取图标
                icon_path = cmds.shelfButton(button_name, query=True, image=True)
                if icon_path:
                    # 处理Maya的图标路径
                    maya_icon_path = self.resolve_maya_icon_path(icon_path)
                    if maya_icon_path and os.path.exists(maya_icon_path):
                        self.setIcon(QtGui.QIcon(maya_icon_path))
                    else:
                        self.setText(source_element)
                else:
                    self.setText(source_element)
            else:
                cmds.warning(f"找不到工具架按钮: {button_name}")
                self.setText(button_name)
        except Exception as e:
            cmds.warning(f"处理工具架按钮失败: {str(e)}")
            self.setText(button_name)
    
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
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.command:
            # 执行存储的命令
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
            if item.widget():
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
                
                # 存储图标信息
                if button.icon() and not button.icon().isNull():
                    icon_name = f"icon_{i}.png"
                    icon_dir = os.path.dirname(file_path)
                    icon_path = os.path.join(icon_dir, icon_name)
                    
                    # 保存图标到文件
                    pixmap = button.icon().pixmap(32, 32)
                    pixmap.save(icon_path, "PNG")
                    
                    button_data["icon"] = icon_path
                    
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
                
                icon_path = button_data.get("icon", "")
                if icon_path and os.path.exists(icon_path):
                    button.setIcon(QtGui.QIcon(icon_path))
                else:
                    button.setText(button_data.get("text", ""))
                    
                self.toolbar_flow.addWidget(button)
                
            cmds.warning(f"工具架配置已加载: {file_path}")
        except Exception as e:
            cmds.warning(f"加载工具架配置失败: {str(e)}")
            
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
    """增强Maya工具架按钮，使其可以被拖拽到悬浮工具架"""
    try:
        main_window = maya_main_window()
        
        # 查找Maya的工具架区域
        shelf_area = None
        for widget in main_window.findChildren(QtWidgets.QWidget):
            if widget.objectName() == "ShelfLayout":
                shelf_area = widget
                break
        
        if not shelf_area:
            cmds.warning("无法找到Maya工具架区域")
            return
            
        # 为所有工具架按钮添加拖拽功能
        maya_shelfs = [shelf for shelf in shelf_area.children() if isinstance(shelf, QtWidgets.QWidget)]
        
        for shelf in maya_shelfs:
            shelf_buttons = [button for button in shelf.findChildren(QtWidgets.QWidget) if "ShelfButton" in button.objectName()]
            
            for button in shelf_buttons:
                try:
                    # 获取原始的按钮名称
                    button_name = button.objectName()
                    
                    # 设置拖拽功能
                    button.setDragEnabled(True)
                    button.setMimeType("text/plain")
                    
                    # 定义拖拽开始事件
                    def start_drag(button_name=button_name):
                        drag = QtGui.QDrag(button)
                        mime_data = QtCore.QMimeData()
                        mime_data.setText(button_name)
                        drag.setMimeData(mime_data)
                        drag.exec_(QtCore.Qt.CopyAction)
                        
                    # 为按钮添加自定义的拖拽事件
                    button.mousePressEvent_original = button.mousePressEvent
                    
                    def mousePressEvent_new(event, button_name=button_name, original=button.mousePressEvent):
                        if event.button() == QtCore.Qt.LeftButton:
                            drag = QtGui.QDrag(button)
                            mime_data = QtCore.QMimeData()
                            mime_data.setText(button_name)
                            drag.setMimeData(mime_data)
                            
                            # 获取按钮图标作为拖拽时的图标
                            try:
                                icon_path = cmds.shelfButton(button_name, query=True, image=True)
                                if icon_path:
                                    pixmap = QtGui.QPixmap(icon_path)
                                    if not pixmap.isNull():
                                        drag.setPixmap(pixmap)
                            except:
                                pass
                                
                            drag.exec_(QtCore.Qt.CopyAction)
                        else:
                            original(event)
                            
                    button.mousePressEvent = mousePressEvent_new
                    
                except Exception as e:
                    cmds.warning(f"为按钮 {button.objectName()} 添加拖拽功能失败: {str(e)}")
    except Exception as e:
        cmds.warning(f"安装工具拖拽处理器失败: {str(e)}")

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
    global floating_toolbar_window
    
    try:
        if 'floating_toolbar_window' in globals() and floating_toolbar_window:
            floating_toolbar_window.close()
            floating_toolbar_window.deleteLater()
    except:
        pass
        
    floating_toolbar_window = FloatingToolbar()
    floating_toolbar_window.show()
    
    # 安装工具拖拽处理器
    install_tool_draggers()
    
    return floating_toolbar_window 