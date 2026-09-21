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

from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
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
        # 初始化默认模式
        self.modes = {
            'translate': 'constraint',  # 位移默认为约束
            'rotate': 'constraint',     # 旋转默认为约束
            'scale': 'constraint',      # 缩放默认为约束
            'other': 'none'        # 其他属性默认不处理
        }
        self.set_flags()

    def set_flags(self):
        # 设置不同模式的颜色标识
        colors = {
            'constraint': QtGui.QColor('green'), # 约束用绿色表示
            'numeric': QtGui.QColor('yellow'),   # 数值复制用黄色表示
            'none': QtGui.QColor('gray')         # 不处理用灰色表示
        }
        # 为每个通道分配颜色
        self.translate_flag = colors.get(self.modes['translate'], QtGui.QColor('gray'))
        self.rotate_flag = colors.get(self.modes['rotate'], QtGui.QColor('gray'))
        self.scale_flag = colors.get(self.modes['scale'], QtGui.QColor('gray'))
        self.other_flag = colors.get(self.modes['other'], QtGui.QColor('gray'))

    def set_mode(self, channel, mode):
        # 设置指定通道的模式
        self.modes[channel] = mode
        self.set_flags()

    def toggle_mode(self, channel, available_modes):
        # 切换指定通道的模式
        current_mode = self.modes[channel]
        mode_list = [mode for mode in ['constraint', 'numeric', 'none'] if mode in available_modes]
        # 循环切换模式
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
                painter.fillRect(rect, QtGui.QColor("#505053"))

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
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.itemFromIndex(index)
            if isinstance(item, CustomListWidgetItem):
                delegate = self.itemDelegate()
                channel = delegate.channel_at_position(item, event.pos())
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
        self.setWindowTitle("编辑对象名称")
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
        self.setWindowTitle("自动对齐工具")
        self.setGeometry(100, 100, 400, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3E3E42;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505053;
            }
            QPushButton:pressed {
                background-color: #2D2D30;
            }
            QListWidget {
                background-color: #3E3E42;
                border: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #505053;
                color: #FFFFFF;
            }
        """)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.input_layout = QtWidgets.QHBoxLayout()
        self.input_button = QtWidgets.QPushButton("录入")
        self.clear_button = QtWidgets.QPushButton("清空")
        self.edit_button = QtWidgets.QPushButton("编辑")
        self.input_layout.addWidget(self.input_button)
        self.input_layout.addWidget(self.clear_button)
        self.input_layout.addWidget(self.edit_button)

        self.save_load_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("保存")
        self.load_button = QtWidgets.QPushButton("读取")
        self.save_load_layout.addWidget(self.save_button)
        self.save_load_layout.addWidget(self.load_button)

        self.record_list = CustomListWidget()

        self.button_layout = QtWidgets.QHBoxLayout()
        self.align_button = QtWidgets.QPushButton("对位")
        self.bake_button = QtWidgets.QPushButton("烘焙")
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
        self.bake_button.clicked.connect(self.bake_animation)
        self.record_list.itemDoubleClicked.connect(self.select_objects)
        self.save_button.clicked.connect(self.save_data)
        self.load_button.clicked.connect(self.load_data)

        self.record_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.record_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # 添加烘焙按钮的右键菜单
        self.bake_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bake_button.customContextMenuRequested.connect(self.show_bake_menu)
        
        # 添加加载按钮的右键菜单
        self.load_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.load_button.customContextMenuRequested.connect(self.show_load_menu)

    def add_selection(self):
        selected_objects = cmds.ls(selection=True)
        if len(selected_objects) != 2:
            cmds.confirmDialog(title='错误', message='请选择两组对象', button=['OK'])
            return
        item = CustomListWidgetItem(f"{selected_objects[0]} , {selected_objects[1]}")
        self.record_list.addItem(item)

    def clear_list(self):
        self.record_list.clear()

    def edit_list(self):
        items_text = "\n".join(item.text() for item in [self.record_list.item(index) for index in range(self.record_list.count())])
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

    def create_rematch_group(self):
        """
        创建Rematch组及其子组
        返回：
        - rematch_group: 主组
        - info_node: 信息存储节点
        """
        # 创建主组
        if not cmds.objExists('Rematch'):
            rematch_group = cmds.group(empty=True, name='Rematch')
        else:
            rematch_group = 'Rematch'
            
        # 创建信息存储节点
        if not cmds.objExists('Rematch|RematchInfo'):
            info_node = cmds.createNode('transform', name='RematchInfo', parent=rematch_group)
        else:
            info_node = 'Rematch|RematchInfo'
            
        return rematch_group, info_node

    def get_valid_objects(self, obj_a, obj_b):
        """
        验证并获取有效的物体名称
        参数：
        - obj_a: 源物体名称
        - obj_b: 目标物体名称
        返回：
        - (valid_obj_a, valid_obj_b): 有效的物体名称对，如果无效则返回(None, None)
        """
        # 验证物体是否存在
        if not cmds.objExists(obj_a):
            cmds.warning(f"找不到源物体: {obj_a}")
            return None, None
        if not cmds.objExists(obj_b):
            cmds.warning(f"找不到目标物体: {obj_b}")
            return None, None
            
        return obj_a, obj_b

    def align_objects_only(self):
        """
        执行对位操作
        步骤：
        1. 获取选中的列表项
        2. 根据列表项中的模式设置执行对位操作
        3. 记录当前帧的位置信息
        """
        selected_items = self.record_list.selectedItems()
        if not selected_items:
            items_to_process = [self.record_list.item(index) for index in range(self.record_list.count())]
        else:
            items_to_process = selected_items
        
        constraint_nodes = []
        rematch_group, info_node = self.create_rematch_group()
        
        # 处理每个对象对
        for item in items_to_process:
            item_text = item.text()
            if " , " not in item_text:
                cmds.warning(f"列表项格式错误: {item_text}")
                continue
                
            obj_a, obj_b = item_text.split(" , ")
            obj_a = obj_a.strip()
            obj_b = obj_b.strip()
            
            # 验证物体名称
            valid_obj_a, valid_obj_b = self.get_valid_objects(obj_a, obj_b)
            if not valid_obj_a or not valid_obj_b:
                continue
            
            if isinstance(item, CustomListWidgetItem):
                # 根据模式设置应用约束
                if item.modes['translate'] == 'constraint':
                    try:
                        point_constraint = cmds.pointConstraint(valid_obj_a, valid_obj_b, maintainOffset=True)
                        constraint_nodes.extend(point_constraint)
                    except Exception as e:
                        cmds.warning(f"跳过位移约束: {e}")
                
                if item.modes['rotate'] == 'constraint':
                    try:
                        orient_constraint = cmds.orientConstraint(valid_obj_a, valid_obj_b, maintainOffset=True)
                        constraint_nodes.extend(orient_constraint)
                    except Exception as e:
                        cmds.warning(f"跳过旋转约束: {e}")
                
                if item.modes['scale'] == 'constraint':
                    try:
                        scale_constraint = cmds.scaleConstraint(valid_obj_a, valid_obj_b, maintainOffset=True)
                        constraint_nodes.extend(scale_constraint)
                    except Exception as e:
                        cmds.warning(f"跳过缩放约束: {e}")
                
                # 记录当前帧的位置信息
                self.record_pose_info(info_node, valid_obj_a, valid_obj_b, item)

        # 创建约束选择集
        if constraint_nodes:
            cmds.select(constraint_nodes)
            cmds.sets(name='Constraint_SelectionSet')

        # 处理数值复制模式
        self.apply_numeric_copy(items_to_process)

    def record_pose_info(self, info_node, obj_a, obj_b, item):
        """
        记录当前帧的位置信息
        参数：
        - info_node: 信息存储节点
        - obj_a: 源物体
        - obj_b: 目标物体
        - item: 列表项
        """
        # 验证物体名称
        valid_obj_a, valid_obj_b = self.get_valid_objects(obj_a, obj_b)
        if not valid_obj_a or not valid_obj_b:
            return
            
        # 创建属性组
        attr_group = f"{valid_obj_a}_{valid_obj_b}"
        if not cmds.attributeQuery(attr_group, node=info_node, exists=True):
            cmds.addAttr(info_node, longName=attr_group, attributeType='compound', numberOfChildren=4)
            cmds.addAttr(info_node, longName=f"{attr_group}_pairInfo", dataType='string', parent=attr_group)
            cmds.addAttr(info_node, longName=f"{attr_group}_modes", dataType='string', parent=attr_group)
            cmds.addAttr(info_node, longName=f"{attr_group}_sourcePose", dataType='string', parent=attr_group)
            cmds.addAttr(info_node, longName=f"{attr_group}_targetPose", dataType='string', parent=attr_group)
        
        # 记录配对信息
        cmds.setAttr(f"{info_node}.{attr_group}_pairInfo", item.text(), type='string')
        
        # 记录模式信息
        modes_json = json.dumps(item.modes)
        cmds.setAttr(f"{info_node}.{attr_group}_modes", modes_json, type='string')
        
        # 记录源物体位置信息
        source_pose = {}
        for attr in ['translate', 'rotate', 'scale']:
            for axis in ['X', 'Y', 'Z']:
                attr_name = f'{attr}{axis}'
                value = cmds.getAttr(f'{valid_obj_a}.{attr_name}')
                source_pose[attr_name] = value
        
        # 记录源物体其他属性
        other_attrs = []
        user_attrs = cmds.listAttr(valid_obj_a, userDefined=True) or []
        for attr in user_attrs:
            try:
                value = cmds.getAttr(f'{valid_obj_a}.{attr}')
                other_attrs.append(f'{attr}:{value}')
            except:
                continue
        source_pose['otherAttributes'] = ','.join(other_attrs)
        
        # 记录目标物体位置信息
        target_pose = {}
        for attr in ['translate', 'rotate', 'scale']:
            for axis in ['X', 'Y', 'Z']:
                attr_name = f'{attr}{axis}'
                value = cmds.getAttr(f'{valid_obj_b}.{attr_name}')
                target_pose[attr_name] = value
        
        # 记录目标物体其他属性
        other_attrs = []
        user_attrs = cmds.listAttr(valid_obj_b, userDefined=True) or []
        for attr in user_attrs:
            try:
                value = cmds.getAttr(f'{valid_obj_b}.{attr}')
                other_attrs.append(f'{attr}:{value}')
            except:
                continue
        target_pose['otherAttributes'] = ','.join(other_attrs)
        
        # 保存位置信息
        cmds.setAttr(f"{info_node}.{attr_group}_sourcePose", json.dumps(source_pose), type='string')
        cmds.setAttr(f"{info_node}.{attr_group}_targetPose", json.dumps(target_pose), type='string')

    def bake_animation(self, smart=False):
        """
        烘焙动画
        参数:
        - smart: 是否使用智能烘焙
        """
        start_time = int(cmds.playbackOptions(q=True, min=True))
        end_time = int(cmds.playbackOptions(q=True, max=True))
        
        # 获取选中的物体
        selected_items = self.record_list.selectedItems()
        if not selected_items:
            items_to_process = [self.record_list.item(index) for index in range(self.record_list.count())]
        else:
            items_to_process = selected_items
        
        objects_to_bake = []
        for item in items_to_process:
            item_text = item.text()
            if " , " not in item_text:
                continue
            _, obj_b = item_text.split(" , ")
            obj_b = obj_b.strip()
            # 验证物体是否存在
            if cmds.objExists(obj_b):
                objects_to_bake.append(obj_b)
            else:
                cmds.warning(f"找不到目标物体: {obj_b}")
        
        if not objects_to_bake:
            cmds.warning("没有对象可烘焙")
            return
        
        # 执行烘焙
        cmds.select(objects_to_bake)
        
        if smart:
            # 使用Maya智能烘焙（只开启智能烘焙选项，其他选项保持默认）
            try:
                cmds.bakeResults(
                    objects_to_bake,
                    time=(start_time, end_time),
                    sampleBy=1,
                    oversamplingRate=1,
                    disableImplicitControl=True,
                    preserveOutsideKeys=True,
                    sparseAnimCurveBake=False,
                    removeBakedAttributeFromLayer=False,
                    removeBakedAnimFromLayer=False,
                    bakeOnOverrideLayer=False,
                    minimizeRotation=True,
                    controlPoints=False,
                    shape=True,
                    simulation=True,
                    smart=True  # 只有这个选项设为True，其他都是默认值
                )
            except Exception as e:
                # 如果上面的方法失败，尝试使用mel命令
                mel_cmd = f'performBakeSimulationArgList 8 {{ "1", "{start_time}", "{end_time}", "1", "0", "1", "1", "1", "0", "1", "mll", "0", "" }};'
                cmds.mel.eval(mel_cmd)
        else:
            # 使用Maya默认烘焙参数
            cmds.bakeResults(
                objects_to_bake,
                time=(start_time, end_time),
                simulation=True
            )
        
        # 删除约束
        try:
            constraints = cmds.sets('Constraint_SelectionSet', q=True)
            if constraints:
                cmds.delete(constraints)
                cmds.delete('Constraint_SelectionSet')
                cmds.confirmDialog(title='成功', message='烘焙完成并删除约束', button=['OK'])
        except:
            cmds.confirmDialog(title='成功', message='烘焙完成', button=['OK'])

    def apply_numeric_copy(self, items_to_process):
        """
        处理数值复制模式
        步骤：
        1. 获取动画时间范围
        2. 查找所有需要进行数值复制的通道
        3. 批量处理所有关键帧
        """
        start_time = int(cmds.playbackOptions(q=True, min=True))
        end_time = int(cmds.playbackOptions(q=True, max=True))
        
        # 收集所有需要处理的对象和通道
        numeric_operations = []
        for item in items_to_process:
            item_text = item.text()
            if " , " not in item_text:
                cmds.warning(f"列表项格式错误: {item_text}")
                continue
                
            obj_a, obj_b = item_text.split(" , ")
            obj_a = obj_a.strip()
            obj_b = obj_b.strip()
            
            # 验证物体名称
            valid_obj_a, valid_obj_b = self.get_valid_objects(obj_a, obj_b)
            if not valid_obj_a or not valid_obj_b:
                continue
            
            if isinstance(item, CustomListWidgetItem):
                channels = []
                if item.modes['translate'] == 'numeric':
                    channels.append('translate')
                if item.modes['rotate'] == 'numeric':
                    channels.append('rotate')
                if item.modes['scale'] == 'numeric':
                    channels.append('scale')
                if item.modes['other'] == 'numeric':
                    channels.append('other')
                
                if channels:
                    numeric_operations.append((valid_obj_a, valid_obj_b, channels))
        
        if not numeric_operations:
            return
            
        # 收集所有需要处理的关键帧
        all_keyframes = set()
        for obj_a, _, _ in numeric_operations:
            try:
                keyframes = cmds.keyframe(obj_a, query=True, timeChange=True)
                if keyframes:
                    all_keyframes.update(keyframes)
            except Exception as e:
                cmds.warning(f"获取关键帧错误: {e}")

        # 按时间顺序处理关键帧
        for frame in sorted(all_keyframes):
            if frame < start_time or frame > end_time:
                continue
                
            cmds.currentTime(frame)
            
            # 处理所有数值复制操作
            for obj_a, obj_b, channels in numeric_operations:
                for channel in channels:
                    self.copy_numeric_keys(obj_a, obj_b, channel, frame)
        
        cmds.currentTime(start_time)

    def copy_numeric_keys(self, obj_a, obj_b, channel, frame):
        """
        复制数值数据
        功能：
        1. 处理标准属性（位移、旋转、缩放）
        2. 处理自定义属性
        3. 支持多维属性的复制
        """
        if channel == 'other':
            attributes = cmds.listAttr(obj_a, keyable=True, userDefined=True)
        else:
            attributes = [f"{channel}X", f"{channel}Y", f"{channel}Z"]
        if not attributes:
            return
        for attr in attributes:
            if cmds.attributeQuery(attr, node=obj_b, exists=True):
                try:
                    value = cmds.getAttr(f'{obj_a}.{attr}', time=frame)
                    if isinstance(value, (list, tuple)):
                        for i, v in enumerate(value):
                            cmds.setKeyframe(obj_b, time=frame, attribute=attr, value=v)
                    else:
                        cmds.setKeyframe(obj_b, time=frame, attribute=attr, value=value)
                except Exception as e:
                    cmds.warning(f"跳过属性 {attr} 在帧 {frame} 错误: {e}")

    def show_bake_menu(self, position):
        """
        显示烘焙菜单
        选项：
        1. 默认烘焙 - 使用Maya默认设置
        2. 智能烘焙 - 使用Maya自带智能烘焙功能
        """
        menu = QtWidgets.QMenu()
        default_bake = menu.addAction("默认烘焙")
        smart_bake = menu.addAction("智能烘焙")
        
        action = menu.exec_(self.bake_button.mapToGlobal(position))
        
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
        load_json_action = menu.addAction("从JSON文件加载")
        load_info_action = menu.addAction("从信息节点加载")
        apply_pose_action = menu.addAction("应用位置信息")
        
        action = menu.exec_(self.load_button.mapToGlobal(position))
        
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
        translate_menu = menu.addMenu("位移")
        translate_constraint_action = translate_menu.addAction("约束")
        translate_numeric_action = translate_menu.addAction("数值复制")
        translate_none_action = translate_menu.addAction("不处理")

        rotate_menu = menu.addMenu("旋转")
        rotate_constraint_action = rotate_menu.addAction("约束")
        rotate_numeric_action = rotate_menu.addAction("数值复制")
        rotate_none_action = rotate_menu.addAction("不处理")

        scale_menu = menu.addMenu("缩放")
        scale_constraint_action = scale_menu.addAction("约束")
        scale_numeric_action = scale_menu.addAction("数值复制")
        scale_none_action = scale_menu.addAction("不处理")

        other_menu = menu.addMenu("其他")
        other_numeric_action = other_menu.addAction("数值复制")
        other_none_action = other_menu.addAction("不处理")

        delete_action = menu.addAction("删除")

        selected_items = self.record_list.selectedItems()
        action = menu.exec_(self.record_list.viewport().mapToGlobal(position))

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
        if " , " not in item_text:
            cmds.warning(f"列表项格式错误: {item_text}")
            return
        obj_a, obj_b = item_text.split(" , ")
        cmds.select([obj_a.strip(), obj_b.strip()])

    def load_from_info_node(self):
        """
        从信息存储节点加载数据
        步骤：
        1. 查找信息存储节点
        2. 根据节点信息重建列表
        3. 恢复通道模式设置
        """
        if not cmds.objExists('Rematch|RematchInfo'):
            cmds.warning("场景中没有找到Rematch|RematchInfo节点")
            return
            
        info_node = 'Rematch|RematchInfo'
        self.record_list.clear()
        
        # 获取所有属性组
        attrs = cmds.listAttr(info_node, userDefined=True) or []
        for attr in attrs:
            if not attr.endswith('_pairInfo'):
                continue
                
            # 获取配对信息
            pair_info = cmds.getAttr(f"{info_node}.{attr}")
            
            # 获取模式信息
            modes_attr = attr.replace('_pairInfo', '_modes')
            modes_json = cmds.getAttr(f"{info_node}.{modes_attr}")
            modes = json.loads(modes_json)
            
            # 创建新的列表项
            item = CustomListWidgetItem(pair_info)
            item.modes = modes
            item.set_flags()
            self.record_list.addItem(item)
            
        cmds.confirmDialog(title='成功', message='已从信息节点加载数据', button=['OK'])

    def apply_pose_info(self):
        """
        应用位置信息
        将记录的位置信息应用到对应的物体上
        """
        if not cmds.objExists('Rematch|RematchInfo'):
            cmds.warning("场景中没有找到Rematch|RematchInfo节点")
            return
            
        info_node = 'Rematch|RematchInfo'
        
        # 获取所有属性组
        attrs = cmds.listAttr(info_node, userDefined=True) or []
        for attr in attrs:
            if not attr.endswith('_pairInfo'):
                continue
                
            # 获取配对信息
            pair_info = cmds.getAttr(f"{info_node}.{attr}")
            obj_a, obj_b = pair_info.split(" , ")
            obj_a = obj_a.strip()
            obj_b = obj_b.strip()
            
            # 验证物体名称
            valid_obj_a, valid_obj_b = self.get_valid_objects(obj_a, obj_b)
            if not valid_obj_a or not valid_obj_b:
                continue
            
            if not cmds.objExists(valid_obj_a) or not cmds.objExists(valid_obj_b):
                cmds.warning(f"找不到物体: {valid_obj_a} 或 {valid_obj_b}")
                continue
            
            # 获取源物体位置信息
            source_pose_attr = attr.replace('_pairInfo', '_sourcePose')
            source_pose_json = cmds.getAttr(f"{info_node}.{source_pose_attr}")
            source_pose = json.loads(source_pose_json)
            
            # 获取目标物体位置信息
            target_pose_attr = attr.replace('_pairInfo', '_targetPose')
            target_pose_json = cmds.getAttr(f"{info_node}.{target_pose_attr}")
            target_pose = json.loads(target_pose_json)
            
            # 应用源物体位置信息
            for attr in ['translate', 'rotate', 'scale']:
                for axis in ['X', 'Y', 'Z']:
                    attr_name = f'{attr}{axis}'
                    try:
                        value = source_pose[attr_name]
                        cmds.setAttr(f'{valid_obj_a}.{attr_name}', value)
                    except Exception as e:
                        cmds.warning(f"跳过属性 {attr_name} 错误: {str(e)}")
            
            # 应用源物体其他属性
            try:
                other_attrs = source_pose['otherAttributes'].split(',')
                for attr_value in other_attrs:
                    if not attr_value:
                        continue
                    attr, value = attr_value.split(':')
                    if cmds.attributeQuery(attr, node=valid_obj_a, exists=True):
                        # 根据属性类型处理
                        attr_type = cmds.getAttr(f'{valid_obj_a}.{attr}', type=True)
                        if attr_type in ['float', 'double', 'int']:
                            cmds.setAttr(f'{valid_obj_a}.{attr}', float(value))
                        else:
                            # 处理其他类型
                            try:
                                cmds.setAttr(f'{valid_obj_a}.{attr}', value)
                            except:
                                pass
            except Exception as e:
                cmds.warning(f"跳过自定义属性错误: {str(e)}")
            
            # 应用目标物体位置信息
            for attr in ['translate', 'rotate', 'scale']:
                for axis in ['X', 'Y', 'Z']:
                    attr_name = f'{attr}{axis}'
                    try:
                        value = target_pose[attr_name]
                        cmds.setAttr(f'{valid_obj_b}.{attr_name}', value)
                    except Exception as e:
                        cmds.warning(f"跳过属性 {attr_name} 错误: {str(e)}")
            
            # 应用目标物体其他属性
            try:
                other_attrs = target_pose['otherAttributes'].split(',')
                for attr_value in other_attrs:
                    attr, value = attr_value.split(':')
                    if cmds.attributeQuery(attr, node=valid_obj_b, exists=True):
                        cmds.setAttr(f'{valid_obj_b}.{attr}', float(value))
            except Exception as e:
                cmds.warning(f"跳过自定义属性错误: {str(e)}")
                            
        cmds.confirmDialog(title='成功', message='已应用位置信息', button=['OK'])

    def save_data(self):
        """
        保存配置数据
        内容：
        1. 对象对的列表
        2. 每对对象的通道模式设置
        """
        items_data = []
        for index in range(self.record_list.count()):
            item = self.record_list.item(index)
            item_text = item.text()
            if isinstance(item, CustomListWidgetItem):
                modes = item.modes
            else:
                modes = {}
            items_data.append({"text": item_text, "modes": modes})
        data_json = json.dumps(items_data, indent=4)
        file_path = cmds.fileDialog2(dialogStyle=2, fileMode=0, caption="保存数据文件", fileFilter="JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path[0], 'w') as file:
                    file.write(data_json)
                cmds.confirmDialog(title='成功', message='数据已保存', button=['OK'])
            except Exception as e:
                cmds.confirmDialog(title='错误', message=f'保存失败: {str(e)}', button=['OK'])

    def load_data(self):
        """
        加载配置数据
        步骤：
        1. 读取JSON文件
        2. 重建列表项
        3. 恢复通道模式设置
        """
        file_path = cmds.fileDialog2(dialogStyle=2, fileMode=1, caption="读取数据文件", fileFilter="JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path[0], 'r') as file:
                    data_json = file.read()
                items_data = json.loads(data_json)
                self.record_list.clear()
                for item_data in items_data:
                    item = CustomListWidgetItem(item_data["text"])
                    if "modes" in item_data:
                        item.modes = item_data["modes"]
                        item.set_flags()
                    self.record_list.addItem(item)
                cmds.confirmDialog(title='成功', message='数据已加载', button=['OK'])
            except Exception as e:
                cmds.confirmDialog(title='错误', message=f'读取失败: {str(e)}', button=['OK'])

def maya_main_window():
    """
    获取Maya主窗口
    用途：使工具窗口始终显示在Maya窗口之上
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

if __name__ == "__main__":
    try:
        app.close()
    except:
        pass

    app = AutoAlignUI()
    app.setParent(maya_main_window())
    app.setWindowFlags(QtCore.Qt.Window)
    app.show()
