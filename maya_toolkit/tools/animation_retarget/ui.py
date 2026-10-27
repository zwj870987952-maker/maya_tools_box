from maya_toolkit.core.ui_base import QtWidgets, QtCore, QtGui, get_maya_main_window

def _menu_exec(menu, position):
    method = getattr(menu, 'exec', None) or menu.exec_
    return method(position)

def _event_pos(event):
    return event.position().toPoint() if hasattr(event, 'position') else event.pos()

_WINDOW = None

def show_ui(parent=None):
    global _WINDOW
    import maya.cmds as cmds
    if cmds.about(batch=True) or QtWidgets is None or QtWidgets.QApplication.instance() is None:
        raise RuntimeError('请在真实 Maya 图形界面中打开此工具')
    if _WINDOW is not None:
        try:
            _WINDOW.close()
            _WINDOW.deleteLater()
        except RuntimeError:
            pass
    _WINDOW = AutoAlignUI()
    _WINDOW.setParent(parent or get_maya_main_window())
    _WINDOW.setWindowFlags(QtCore.Qt.Window)
    _WINDOW.show()
    return _WINDOW

"""
Maya动画重定向工具
功能：将一个物体的动画数据转移到另一个物体上
特点：
- 支持多对象批量处理
- 可视化的通道模式设置
- 灵活的右键菜单配置
- 数据配置的保存和加载
- 支持自定义属性的传递
"""
import maya.cmds as cmds
import json
import os

class CustomListWidgetItem(QtWidgets.QListWidgetItem):
    """
    自定义列表项，用于存储和显示每对物体的对齐模式
    modes包含四种通道：
    - translate(位移)
    - rotate(旋转)
    - scale(缩放)
    - other(其他)

    每个通道支持不同的模式：
    - constraint: 约束（绿色）
    - numeric: 数值复制（黄色）
    - none: 不处理（灰色）
    """

    def __init__(self, text, parent=None):
        super(CustomListWidgetItem, self).__init__(text, parent)
        self.modes = {'translate': 'constraint', 'rotate': 'constraint', 'scale': 'constraint', 'other': 'none'}
        self.set_flags()

    def set_flags(self):
        colors = {'constraint': QtGui.QColor('green'), 'numeric': QtGui.QColor('yellow'), 'none': QtGui.QColor('gray')}
        self.translate_flag = colors.get(self.modes['translate'], QtGui.QColor('gray'))
        self.rotate_flag = colors.get(self.modes['rotate'], QtGui.QColor('gray'))
        self.scale_flag = colors.get(self.modes['scale'], QtGui.QColor('gray'))
        self.other_flag = colors.get(self.modes['other'], QtGui.QColor('gray'))

    def set_mode(self, channel, mode):
        self.modes[channel] = mode
        self.set_flags()

    def toggle_mode(self, channel, available_modes):
        current_mode = self.modes[channel]
        mode_list = [mode for mode in ['constraint', 'numeric', 'none'] if mode in available_modes]
        if current_mode in mode_list:
            next_mode_index = (mode_list.index(current_mode) + 1) % len(mode_list)
        else:
            next_mode_index = 0
        next_mode = mode_list[next_mode_index]
        self.set_mode(channel, next_mode)

class CustomItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    自定义列表代理
    功能：
    1. 负责绘制列表项的视觉效果
    2. 为每个通道绘制不同颜色的圆点标识
    3. 处理鼠标点击事件来切换不同通道的模式
    """

    def paint(self, painter, option, index):
        item = self.parent().itemFromIndex(index)
        if isinstance(item, CustomListWidgetItem):
            rect = option.rect
            painter.save()
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(rect, QtGui.QColor('#505053'))
            spacing = 5
            size = 10
            flags = [item.translate_flag, item.rotate_flag, item.scale_flag, item.other_flag]
            total_width = len(flags) * size + (len(flags) - 1) * spacing
            start_x = rect.left() + spacing
            center_y = rect.top() + rect.height() // 2
            for i, flag in enumerate(flags):
                painter.setBrush(flag)
                painter.drawEllipse(QtCore.QRect(start_x + i * (size + spacing), center_y - size // 2, size, size))
            painter.setPen(QtGui.QColor('white'))
            painter.drawText(rect.adjusted(total_width + spacing * 2, 0, 0, 0), QtCore.Qt.AlignVCenter, item.text())
            painter.restore()
        else:
            super(CustomItemDelegate, self).paint(painter, option, index)

    def channel_at_position(self, item, position):
        rect = self.parent().visualItemRect(item)
        spacing = 5
        size = 10
        start_x = rect.left() + spacing
        center_y = rect.top() + rect.height() // 2
        channels = ['translate', 'rotate', 'scale', 'other']
        for i, channel in enumerate(channels):
            ellipse_rect = QtCore.QRect(start_x + i * (size + spacing), center_y - size // 2, size, size)
            if ellipse_rect.contains(position):
                return channel
        return None

class CustomListWidget(QtWidgets.QListWidget):
    """
    自定义列表控件
    功能：
    1. 处理鼠标事件
    2. 管理列表项的显示和交互
    3. 支持拖拽排序
    """

    def __init__(self, *args, **kwargs):
        super(CustomListWidget, self).__init__(*args, **kwargs)
        self.setItemDelegate(CustomItemDelegate(self))
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def mousePressEvent(self, event):
        index = self.indexAt(_event_pos(event))
        if index.isValid():
            item = self.itemFromIndex(index)
            if isinstance(item, CustomListWidgetItem):
                delegate = self.itemDelegate()
                channel = delegate.channel_at_position(item, _event_pos(event))
                if channel:
                    for selected_item in self.selectedItems():
                        if isinstance(selected_item, CustomListWidgetItem):
                            available_modes = self.get_available_modes(channel)
                            selected_item.toggle_mode(channel, available_modes)
                    self.viewport().update()
                    return
        super(CustomListWidget, self).mousePressEvent(event)

    def get_available_modes(self, channel):
        if channel in ['translate', 'rotate', 'scale']:
            return ['constraint', 'numeric', 'none']
        elif channel == 'other':
            return ['numeric', 'none']
        return []

class EditDialog(QtWidgets.QDialog):
    """
    编辑对话框
    功能：
    1. 提供文本编辑界面
    2. 用于批量编辑对象名称
    """
    text_changed = QtCore.Signal(str)

    def __init__(self, items_text, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setWindowTitle('编辑对象名称')
        self.setGeometry(100, 100, 400, 300)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setText(items_text)
        self.layout.addWidget(self.text_edit)
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def accept(self):
        self.text_changed.emit(self.text_edit.toPlainText())
        super(EditDialog, self).accept()

    def reject(self):
        super(EditDialog, self).reject()

class AutoAlignUI(QtWidgets.QWidget):
    """
    主界面类
    核心功能：
    1. 录入：添加选中的两个物体到列表
    2. 定位和对位：生成定位器并根据设置执行动画重定向
    3. 烘焙：烘焙动画数据
    4. 保存/读取：支持保存和加载对齐设置
    """

    def __init__(self):
        super(AutoAlignUI, self).__init__()
        self.setWindowTitle('自动对齐工具')
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet('\n            QWidget {\n                background-color: #2D2D30;\n                color: #FFFFFF;\n            }\n            QPushButton {\n                background-color: #3E3E42;\n                border: none;\n                padding: 5px 10px;\n                border-radius: 3px;\n            }\n            QPushButton:hover {\n                background-color: #505053;\n            }\n            QPushButton:pressed {\n                background-color: #2D2D30;\n            }\n            QListWidget {\n                background-color: #3E3E42;\n                border: none;\n            }\n            QListWidget::item {\n                padding: 5px;\n            }\n            QListWidget::item:selected {\n                background-color: #505053;\n                color: #FFFFFF;\n            }\n        ')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.input_layout = QtWidgets.QHBoxLayout()
        self.input_button = QtWidgets.QPushButton('录入')
        self.clear_button = QtWidgets.QPushButton('清空')
        self.edit_button = QtWidgets.QPushButton('编辑')
        self.input_layout.addWidget(self.input_button)
        self.input_layout.addWidget(self.clear_button)
        self.input_layout.addWidget(self.edit_button)
        self.save_load_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton('保存')
        self.load_button = QtWidgets.QPushButton('读取')
        self.save_load_layout.addWidget(self.save_button)
        self.save_load_layout.addWidget(self.load_button)
        self.record_list = CustomListWidget()
        self.button_layout = QtWidgets.QHBoxLayout()
        self.align_button = QtWidgets.QPushButton('对位')
        self.bake_button = QtWidgets.QPushButton('烘焙')
        self.button_layout.addWidget(self.align_button)
        self.button_layout.addWidget(self.bake_button)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.save_load_layout)
        self.layout.addWidget(self.record_list)
        self.layout.addLayout(self.button_layout)
        self.input_button.clicked.connect(self.add_selection)
        self.clear_button.clicked.connect(self.clear_list)
        self.edit_button.clicked.connect(self.edit_list)
        self.align_button.clicked.connect(self.align_objects_only)
        self.bake_button.clicked.connect(lambda checked=False: self.bake_animation(smart=False))
        self.record_list.itemDoubleClicked.connect(self.select_objects)
        self.save_button.clicked.connect(self.save_data)
        self.load_button.clicked.connect(self.load_data)
        self.record_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.record_list.customContextMenuRequested.connect(self.show_context_menu)
        self.bake_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bake_button.customContextMenuRequested.connect(self.show_bake_menu)
        self.load_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.load_button.customContextMenuRequested.connect(self.show_load_menu)
        preview_button = QtWidgets.QPushButton('只读预检')
        self.button_layout.addWidget(preview_button)
        preview_button.clicked.connect(self.preview_operation)

    def add_selection(self):
        selected_objects = cmds.ls(selection=True)
        if len(selected_objects) != 2:
            cmds.confirmDialog(title='错误', message='请选择两组对象', button=['OK'])
            return
        item = CustomListWidgetItem(f'{selected_objects[0]} , {selected_objects[1]}')
        self.record_list.addItem(item)

    def clear_list(self):
        self.record_list.clear()

    def edit_list(self):
        items_text = '\n'.join((item.text() for item in [self.record_list.item(index) for index in range(self.record_list.count())]))
        dialog = EditDialog(items_text, self)
        dialog.text_changed.connect(self.update_list)
        dialog.setWindowModality(QtCore.Qt.NonModal)
        dialog.show()

    def update_list(self, edited_text):
        self.record_list.clear()
        for line in edited_text.splitlines():
            if line.strip():
                item = CustomListWidgetItem(line.strip())
                self.record_list.addItem(item)

    def show_bake_menu(self, position):
        """
        显示烘焙菜单
        选项：
        1. 默认烘焙 - 使用Maya默认设置
        2. 智能烘焙 - 使用Maya自带智能烘焙功能
        """
        menu = QtWidgets.QMenu()
        default_bake = menu.addAction('默认烘焙')
        smart_bake = menu.addAction('智能烘焙')
        action = _menu_exec(menu, self.bake_button.mapToGlobal(position))
        if action == default_bake:
            self.bake_animation(smart=False)
        elif action == smart_bake:
            self.bake_animation(smart=True)

    def show_load_menu(self, position):
        """
        显示加载按钮的右键菜单
        选项：
        1. 从JSON文件加载
        2. 从信息节点加载
        3. 应用位置信息
        """
        menu = QtWidgets.QMenu()
        load_json_action = menu.addAction('从JSON文件加载')
        load_info_action = menu.addAction('从信息节点加载')
        apply_pose_action = menu.addAction('应用位置信息')
        action = _menu_exec(menu, self.load_button.mapToGlobal(position))
        if action == load_json_action:
            self.load_data()
        elif action == load_info_action:
            self.load_from_info_node()
        elif action == apply_pose_action:
            self.apply_pose_info()

    def show_context_menu(self, position):
        """
        显示右键菜单
        功能：
        1. 提供通道模式快速切换
        2. 支持批量修改选中项
        3. 提供删除功能
        """
        menu = QtWidgets.QMenu()
        translate_menu = menu.addMenu('位移')
        translate_constraint_action = translate_menu.addAction('约束')
        translate_numeric_action = translate_menu.addAction('数值复制')
        translate_none_action = translate_menu.addAction('不处理')
        rotate_menu = menu.addMenu('旋转')
        rotate_constraint_action = rotate_menu.addAction('约束')
        rotate_numeric_action = rotate_menu.addAction('数值复制')
        rotate_none_action = rotate_menu.addAction('不处理')
        scale_menu = menu.addMenu('缩放')
        scale_constraint_action = scale_menu.addAction('约束')
        scale_numeric_action = scale_menu.addAction('数值复制')
        scale_none_action = scale_menu.addAction('不处理')
        other_menu = menu.addMenu('其他')
        other_numeric_action = other_menu.addAction('数值复制')
        other_none_action = other_menu.addAction('不处理')
        delete_action = menu.addAction('删除')
        selected_items = self.record_list.selectedItems()
        action = _menu_exec(menu, self.record_list.viewport().mapToGlobal(position))
        if action in [translate_constraint_action, translate_numeric_action, translate_none_action]:
            mode = 'constraint' if action == translate_constraint_action else 'numeric' if action == translate_numeric_action else 'none'
            for item in selected_items:
                if isinstance(item, CustomListWidgetItem):
                    item.set_mode('translate', mode)
        elif action in [rotate_constraint_action, rotate_numeric_action, rotate_none_action]:
            mode = 'constraint' if action == rotate_constraint_action else 'numeric' if action == rotate_numeric_action else 'none'
            for item in selected_items:
                if isinstance(item, CustomListWidgetItem):
                    item.set_mode('rotate', mode)
        elif action in [scale_constraint_action, scale_numeric_action, scale_none_action]:
            mode = 'constraint' if action == scale_constraint_action else 'numeric' if action == scale_numeric_action else 'none'
            for item in selected_items:
                if isinstance(item, CustomListWidgetItem):
                    item.set_mode('scale', mode)
        elif action in [other_numeric_action, other_none_action]:
            mode = 'numeric' if action == other_numeric_action else 'none'
            for item in selected_items:
                if isinstance(item, CustomListWidgetItem):
                    item.set_mode('other', mode)
        elif action == delete_action:
            for item in selected_items:
                self.record_list.takeItem(self.record_list.row(item))

    def select_objects(self, item):
        """
        选择对象
        功能：
        1. 双击列表项时选择对应的Maya物体
        2. 支持错误检查和提示
        """
        item_text = item.text()
        if ' , ' not in item_text:
            cmds.warning(f'列表项格式错误: {item_text}')
            return
        obj_a, obj_b = item_text.split(' , ')
        cmds.select([obj_a.strip(), obj_b.strip()])

    def _pairs(self, all_rows=False):
        from .contracts import pairs
        items = [] if all_rows else self.record_list.selectedItems()
        items = items or [self.record_list.item(i) for i in range(self.record_list.count())]
        return pairs([{'text': item.text(), 'modes': item.modes} for item in items], allow_empty=True)

    def _run(self, **kwargs):
        from .tool import AnimationRetargetTool
        result = AnimationRetargetTool().run(**kwargs)
        if result.success:
            if result.warnings:
                cmds.warning('\n'.join(result.warnings))
            cmds.confirmDialog(title='完成', message=result.message, button=['OK'])
            return result.data
        cmds.confirmDialog(title='错误', message=result.message + '\n场景操作可能已部分完成；请检查并按 Undo 撤回。', button=['OK'])
        return None

    def _rebuild(self, rows):
        self.record_list.clear()
        for row in rows:
            item = CustomListWidgetItem(row['source'] + ' , ' + row['target'])
            item.modes = dict(row['modes'])
            item.set_flags()
            self.record_list.addItem(item)

    def align_objects_only(self):
        try:
            self._run(action='align', pairs=self._pairs())
        except Exception as error:
            cmds.warning(str(error))

    def bake_animation(self, smart=False):
        try:
            self._run(action='bake', pairs=self._pairs(), smart=bool(smart))
        except Exception as error:
            cmds.warning(str(error))

    def load_from_info_node(self):
        data = self._run(action='load_scene')
        if data is not None:
            self._rebuild(data['pairs'])

    def apply_pose_info(self):
        try:
            self._run(action='restore_pose', pairs=self._pairs())
        except Exception as error:
            cmds.warning(str(error))

    def save_data(self):
        path = cmds.fileDialog2(dialogStyle=2, fileMode=0, caption='保存为新 JSON 文件（不覆盖）', fileFilter='JSON Files (*.json)')
        if path:
            try:
                self._run(action='save_config', pairs=self._pairs(all_rows=True), path=path[0])
            except Exception as error:
                cmds.warning(str(error))

    def load_data(self):
        path = cmds.fileDialog2(dialogStyle=2, fileMode=1, caption='读取配置', fileFilter='JSON Files (*.json)')
        if path:
            data = self._run(action='load_config', path=path[0])
            if data is not None:
                self._rebuild(data['pairs'])

    def preview_operation(self):
        try:
            from .tool import AnimationRetargetTool
            result = AnimationRetargetTool().run(action='align', pairs=self._pairs(), dry_run=True)
            cmds.confirmDialog(title='只读预检', message=result.message, button=['OK'])
        except Exception as error:
            cmds.warning(str(error))
