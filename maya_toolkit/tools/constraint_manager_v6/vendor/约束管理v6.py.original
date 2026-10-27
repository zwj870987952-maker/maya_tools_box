#############
####优化识别节点和属性逻辑，保证适用任何带名称空间和不带的名字
####把设置静止位置，修改约束轴，选中属性，选中约束节点功能转移到ui按钮中
####添加自定义权重数值，添加条目颜色设置
####优化约束识别方法，提高准确性
########添加节点显示模式，添加选中约束物


import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import re

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ConstraintTool(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ConstraintTool, self).__init__(parent)
        self.setWindowTitle("约束权重工具")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        self.saved_list_buttons = []

        # 添加整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: #383838;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #505050;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QLineEdit {
                background-color: #2B2B2B;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 3px;
                color: #E0E0E0;
            }
            QListWidget {
                background-color: #2B2B2B;
                border: 1px solid #606060;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #4B4B4B;
            }
            QListWidget::item:hover {
                background-color: #3B3B3B;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.load_saved_lists()

    def create_widgets(self):
        self.attr_list = CustomListWidget()
        self.attr_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.btn_refresh = QtWidgets.QPushButton("刷新")
        self.btn_add = QtWidgets.QPushButton("添加")
        self.btn_clear = QtWidgets.QPushButton("清空")
        self.btn_mode0 = QtWidgets.QPushButton("0")
        self.btn_mode1 = QtWidgets.QPushButton("(1) 0")
        self.btn_mode2 = QtWidgets.QPushButton("1")
        self.input_custom_weight = QtWidgets.QLineEdit()
        self.input_custom_weight.setPlaceholderText("输入权重值")
        self.btn_custom_weight = QtWidgets.QPushButton("设置权重")
        self.btn_save_list = QtWidgets.QPushButton("保存列表")
        
        # 新增功能按钮
        self.btn_disconnect = QtWidgets.QPushButton("断开")
        self.btn_restore = QtWidgets.QPushButton("恢复")
        self.btn_reverse = QtWidgets.QPushButton("反向")
        self.btn_rebuild = QtWidgets.QPushButton("重建")
        
        self.btn_set_rest_position = QtWidgets.QPushButton("设置静止位置")
        self.btn_modify_axis = QtWidgets.QPushButton("修改约束轴")
        self.btn_select_attrs = QtWidgets.QPushButton("约束物体")
        self.btn_select_attrs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.btn_select_attrs.customContextMenuRequested.connect(self.show_select_menu)
        self.btn_select_constraint_node = QtWidgets.QPushButton("选中约束节点")
        
        self.checkbox_set_keyframe = QtWidgets.QCheckBox("设置关键帧")
        self.checkbox_set_keyframe.setChecked(True)
    
        self.color_buttons = []
        colors = ["#000000", "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    
        self.default_color_button = QtWidgets.QPushButton("默认")
        self.default_color_button.setFixedSize(40, 15)
        self.default_color_button.clicked.connect(lambda: self.change_item_color("#e0e0e0"))
        self.color_buttons.append(self.default_color_button)
    
        for color in colors:
            btn = QtWidgets.QPushButton()
            btn.setStyleSheet(f"background-color: {color};")
            btn.setFixedSize(40, 15)
            btn.clicked.connect(self.create_color_changer(color))
            self.color_buttons.append(btn)
    
        self.saved_list_layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel("请选择一种方式修改权重属性：")
    
        self.create_context_menu()

        # 修改一些按钮的样式
        self.btn_mode0.setStyleSheet("""
            QPushButton {
                background-color: #AA5555;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #BB6666;
            }
            QPushButton:pressed {
                background-color: #994444;
            }
        """)  # 红色调
        
        self.btn_mode1.setStyleSheet("""
            QPushButton {
                background-color: #55AA55;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #66BB66;
            }
            QPushButton:pressed {
                background-color: #449944;
            }
        """)  # 绿色调
        
        self.btn_mode2.setStyleSheet("""
            QPushButton {
                background-color: #5555AA;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6666BB;
            }
            QPushButton:pressed {
                background-color: #444499;
            }
        """)  # 蓝色调
        
        # 设置功能按钮组的统一样式
        action_buttons_style = """
            QPushButton {
                background-color: #456789;
                color: white;
                font-weight: bold;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #56789A;
            }
            QPushButton:pressed {
                background-color: #345678;
            }
        """
        self.btn_set_rest_position.setStyleSheet(action_buttons_style)
        self.btn_modify_axis.setStyleSheet(action_buttons_style)
        self.btn_select_attrs.setStyleSheet(action_buttons_style)
        self.btn_select_constraint_node.setStyleSheet(action_buttons_style)
        
        # 主要操作按钮样式
        main_buttons_style = """
            QPushButton {
                background-color: #666666;
                font-weight: bold;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """
        self.btn_refresh.setStyleSheet(main_buttons_style)
        self.btn_add.setStyleSheet(main_buttons_style)
        self.btn_clear.setStyleSheet(main_buttons_style)
        self.btn_save_list.setStyleSheet(main_buttons_style)
        
        # 设置新增按钮样式
        self.btn_disconnect.setStyleSheet(main_buttons_style)
        self.btn_restore.setStyleSheet(main_buttons_style)
        self.btn_reverse.setStyleSheet(main_buttons_style)
        self.btn_rebuild.setStyleSheet(main_buttons_style)
        
        # 设置列表的样式
        self.attr_list.setAlternatingRowColors(True)
        self.attr_list.setStyleSheet("""
            QListWidget {
                alternate-background-color: #333333;
            }
            QListWidget::item:alternate {
                background-color: #2D2D2D;
            }
            QListWidget::item:selected:alternate {
                background-color: #4B4B4B;
            }
        """)

        # 添加显示模式切换按钮
        self.btn_toggle_display = QtWidgets.QPushButton("切换显示模式")
        self.btn_toggle_display.setCheckable(True)  # 使按钮可以切换状态
        self.btn_toggle_display.setChecked(True)  # 默认选中约束节点模式
        self.btn_toggle_display.setStyleSheet("""
            QPushButton:checked {
                background-color: #557799;
                font-weight: bold;
            }
        """)
        
        # 添加显示模式标签
        self.display_mode_label = QtWidgets.QLabel("当前模式: 约束节点")

        # 添加数据存储字典
        self.constraint_data = {}  # 用于存储约束相关的数据

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        btn_layout = QtWidgets.QHBoxLayout()
        new_btn_layout = QtWidgets.QHBoxLayout()  # 新增按钮布局
        mode_layout = QtWidgets.QHBoxLayout()
        action_btn_layout = QtWidgets.QHBoxLayout()
        color_layout = QtWidgets.QHBoxLayout()
        custom_weight_layout = QtWidgets.QHBoxLayout()
        color_layout.setSpacing(0.4)
    
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_save_list)
        
        # 新增按钮布局
        new_btn_layout.addWidget(self.btn_disconnect)
        new_btn_layout.addWidget(self.btn_restore)
        new_btn_layout.addWidget(self.btn_reverse)
        new_btn_layout.addWidget(self.btn_rebuild)
        
        action_btn_layout.addWidget(self.btn_set_rest_position)
        action_btn_layout.addWidget(self.btn_modify_axis)
        action_btn_layout.addWidget(self.btn_select_attrs)
        action_btn_layout.addWidget(self.btn_select_constraint_node)
        
        mode_layout.addWidget(self.btn_mode0)
        mode_layout.addWidget(self.btn_mode1)
        mode_layout.addWidget(self.btn_mode2)

        custom_weight_layout.addWidget(self.input_custom_weight)
        custom_weight_layout.addWidget(self.btn_custom_weight)
        
        for btn in self.color_buttons:
            color_layout.addWidget(btn)
        
        main_layout.addWidget(QtWidgets.QLabel("选中的约束节点的权重属性："))
        main_layout.addLayout(self.saved_list_layout)
        main_layout.addWidget(self.attr_list)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(new_btn_layout)  # 添加新增按钮布局
        main_layout.addLayout(action_btn_layout)
    
        label_and_checkbox_layout = QtWidgets.QHBoxLayout()
        label_and_checkbox_layout.addWidget(self.label)
        label_and_checkbox_layout.addWidget(self.checkbox_set_keyframe)
        main_layout.addLayout(label_and_checkbox_layout)
    
        main_layout.addLayout(mode_layout)
        main_layout.addLayout(custom_weight_layout)
        main_layout.addLayout(color_layout)

        # 添加显示模式相关控件
        display_mode_layout = QtWidgets.QHBoxLayout()
        display_mode_layout.addWidget(self.btn_toggle_display)
        display_mode_layout.addWidget(self.display_mode_label)
        display_mode_layout.addStretch()
        
        # 在列表上方添加显示模式控件
        main_layout.insertLayout(1, display_mode_layout)  # 插入到标签之后
        
        # 添加一些间距和对齐
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        btn_layout.setSpacing(5)
        new_btn_layout.setSpacing(5)  # 设置新增按钮布局间距
        mode_layout.setSpacing(5)
        action_btn_layout.setSpacing(5)

    def create_connections(self):
        self.btn_refresh.clicked.connect(self.refresh_constraints)
        self.btn_add.clicked.connect(self.add_selected_constraints)
        self.btn_clear.clicked.connect(self.clear_constraints)
        self.btn_mode0.clicked.connect(lambda: self.run_tool(1))  # 设置为0
        self.btn_mode1.clicked.connect(lambda: self.run_tool(2))  # 设置为(1) 0
        self.btn_mode2.clicked.connect(lambda: self.run_tool(3))  # 设置为1
        self.btn_custom_weight.clicked.connect(self.set_custom_weight)
        self.btn_save_list.clicked.connect(self.save_list)
        self.attr_list.itemDoubleClicked.connect(self.get_constraint_info_and_run_tool)
        
        # 新增按钮连接（暂时连接空函数，待后续实现功能）
        self.btn_disconnect.clicked.connect(self.disconnect_constraints)
        self.btn_restore.clicked.connect(self.restore_constraints)
        self.btn_reverse.clicked.connect(self.reverse_constraints)
        self.btn_rebuild.clicked.connect(self.rebuild_constraints)
    
        self.btn_set_rest_position.clicked.connect(self.set_rest_position)
        self.btn_modify_axis.clicked.connect(self.modify_constrained_axis)
        self.btn_select_attrs.clicked.connect(self.select_target_objects)
        self.btn_select_constraint_node.clicked.connect(self.select_constraint_node)

        # 添加显示模式切换连接
        self.btn_toggle_display.clicked.connect(self.toggle_display_mode)

    def get_constraint_weights(self, selected_objects):
        """
        获取选中物体的约束权重信息
        
        Args:
            selected_objects (list): Maya中选中的物体列表
            
        Returns:
            list: 所有找到的权重属性列表
        """
        weight_attrs = []
        object_constraints_info = {}

        # 遍历选定的对象
        for obj in selected_objects:
            object_constraints_info[obj] = {
                'constraints': [],
                'valid_weight_attrs': []
            }

            # 查找所有与选定对象连接的约束节点（源和目标）
            constraints = cmds.listConnections(obj, source=True, destination=True, type='constraint') or []
            constraints = list(set(constraints))  # 直接去重

            if constraints:
                for constraint in constraints:
                    # 确保我们只添加唯一的约束节点
                    if constraint not in object_constraints_info[obj]['constraints']:
                        object_constraints_info[obj]['constraints'].append(constraint)
                        
                        # 获取约束相关的物体信息
                        constrained_object = cmds.listRelatives(constraint, parent=True)[0]
                        
                        # 获取目标物体的新方法
                        target_objects = []
                        # 获取约束类型
                        constraint_type = cmds.nodeType(constraint)
                        
                        # 根据约束类型获取目标连接
                        if constraint_type == "parentConstraint":
                            targets = cmds.parentConstraint(constraint, q=True, targetList=True)
                        elif constraint_type == "pointConstraint":
                            targets = cmds.pointConstraint(constraint, q=True, targetList=True)
                        elif constraint_type == "orientConstraint":
                            targets = cmds.orientConstraint(constraint, q=True, targetList=True)
                        elif constraint_type == "scaleConstraint":
                            targets = cmds.scaleConstraint(constraint, q=True, targetList=True)
                        elif constraint_type == "aimConstraint":
                            targets = cmds.aimConstraint(constraint, q=True, targetList=True)
                        else:
                            # 对于其他类型的约束，尝试通过连接关系查找目标
                            targets = cmds.listConnections(constraint + ".target", source=True, destination=False) or []
                        
                        if targets:
                            target_objects.extend(targets)
                        
                        # 存储约束数据
                        self.constraint_data[constraint] = {
                            'constrained_object': constrained_object,
                            'target_objects': target_objects
                        }

                    # 只列出附加属性
                    attrs = cmds.listAttr(constraint, userDefined=True)
                    if attrs:
                        for attr in attrs:
                            try:
                                # 获取属性的类型
                                attr_type = cmds.getAttr(f'{constraint}.{attr}', type=True)
                                
                                # 如果属性类型是 'float' 或 'double'，表示是一个可能的权重属性
                                if attr_type in ['float', 'double']:
                                    # 为了去重，检查该权重属性是否已经被添加
                                    full_attr_name = f"{constraint}.{attr}"
                                    if full_attr_name not in weight_attrs:
                                        weight_attrs.append(full_attr_name)
                            except Exception as e:
                                # 如果获取属性类型或值失败，跳过该属性
                                pass

        return weight_attrs

    def set_custom_weight(self):
        selected_items = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return
    
        try:
            value = float(self.input_custom_weight.text())
        except ValueError:
            cmds.warning("请输入有效的数值。")
            return
    
        set_keyframe = self.checkbox_set_keyframe.isChecked()
    
        if self.btn_toggle_display.isChecked():
            # 约束节点模式：获取所有节点的权重属性
            for item in selected_items:
                # 获取约束节点的所有权重属性
                weight_attrs = self.get_constraint_weights([item])
                if weight_attrs:
                    for attr in weight_attrs:
                        if cmds.objExists(attr):
                            cmds.setAttr(attr, value)
                            if set_keyframe:
                                cmds.setKeyframe(attr)
                            print(f"{attr}: 设置为 {value}" + (" 并添加关键帧。" if set_keyframe else "。"))
        else:
            # 权重属性模式：直接修改属性值
            for attr in selected_items:
                if cmds.objExists(attr):
                    cmds.setAttr(attr, value)
                    if set_keyframe:
                        cmds.setKeyframe(attr)
                    print(f"{attr}: 设置为 {value}" + (" 并添加关键帧。" if set_keyframe else "。"))

    def create_context_menu(self):
        self.attr_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.attr_list.customContextMenuRequested.connect(self.show_context_menu)
        self.btn_clear.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.btn_clear.customContextMenuRequested.connect(self.show_clear_button_context_menu)

    def show_context_menu(self, pos):
        context_menu = QtWidgets.QMenu(self)
        remove_action = context_menu.addAction("删除选定项")
        remove_target_action = context_menu.addAction("移除目标")
        remove_target_offset_action = context_menu.addAction("移除目标（保持偏移）")

        action = context_menu.exec_(self.attr_list.mapToGlobal(pos))
        if action == remove_action:
            self.remove_selected_items()
        elif action == remove_target_action:
            self.remove_target(maintain_offset=False)
            self.remove_selected_items()
        elif action == remove_target_offset_action:
            self.remove_target(maintain_offset=True)
            self.remove_selected_items()

    def show_clear_button_context_menu(self, pos):
        context_menu = QtWidgets.QMenu(self)
        delete_constraint_action = context_menu.addAction("删除约束节点")

        action = context_menu.exec_(self.btn_clear.mapToGlobal(pos))
        if action == delete_constraint_action:
            self.delete_selected_constraints()

    def load_saved_lists(self):
        locators = cmds.ls(type="locator")
        for loc in locators:
            parent = cmds.listRelatives(loc, parent=True)[0]
            if parent.endswith("_list"):
                self.add_saved_list_button(parent)

    def add_saved_list_button(self, locator_name):
        list_name = locator_name.replace("_list", "")
        btn = QtWidgets.QPushButton(list_name)
        btn.clicked.connect(lambda: self.load_list_from_locator(locator_name))
        self.saved_list_layout.addWidget(btn)
        self.saved_list_buttons.append(btn)

    def load_list_from_locator(self, locator_name):
        self.attr_list.clear()
        if cmds.objExists(locator_name):
            list_data = cmds.getAttr(locator_name + ".notes")
            if list_data:
                items = list_data.split(',')
                for item_data in items:
                    parts = item_data.split('|')
                    if len(parts) >= 2:
                        text = parts[0]
                        color = parts[1]
                        constraint_node = parts[2] if len(parts) > 2 else ''
                        weight_attrs_str = parts[3] if len(parts) > 3 else ''
                        weight_attrs = weight_attrs_str.split(';') if weight_attrs_str else []
                        
                        # 创建列表项
                        list_item = CustomListWidgetItem(text, constraint_node, weight_attrs)
                        list_item.setForeground(QtGui.QColor(color))
                        self.attr_list.addItem(list_item)

    def add_selected_constraints(self):
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("请先选择一个或多个约束节点。")
            return

        weight_attrs = self.get_constraint_weights(selected_objects)
        if weight_attrs:
            # 获取当前列表中的所有条目
            existing_items = set()
            for i in range(self.attr_list.count()):
                item = self.attr_list.item(i)
                if not item.is_separator:
                    existing_items.add(item.text())

            if self.btn_toggle_display.isChecked():
                # 约束节点模式：只添加唯一的约束节点
                constraint_nodes = []
                for attr in weight_attrs:
                    constraint_node, _, _ = self.parse_constraint_attr(attr)
                    if constraint_node and constraint_node not in existing_items and constraint_node not in constraint_nodes:
                        constraint_nodes.append(constraint_node)
                        
                        # 获取该约束节点的所有权重属性
                        node_weight_attrs = [a for a in weight_attrs if a.startswith(constraint_node + '.')]
                        
                        item = CustomListWidgetItem(constraint_node, constraint_node, node_weight_attrs)
                        item.setForeground(QtGui.QColor("#e0e0e0"))  # 默认颜色
                        self.attr_list.addItem(item)
                        
            else:
                # 权重属性模式：按约束节点分组添加权重属性
                constraint_groups = {}
                for attr in weight_attrs:
                    if attr not in existing_items:
                        constraint_node, _, _ = self.parse_constraint_attr(attr)
                        if constraint_node not in constraint_groups:
                            constraint_groups[constraint_node] = []
                        constraint_groups[constraint_node].append(attr)
                
                # 按约束节点分组添加
                constraint_node_list = list(constraint_groups.keys())
                for i, constraint_node in enumerate(constraint_node_list):
                    attrs = constraint_groups[constraint_node]
                    for attr in attrs:
                        item = CustomListWidgetItem(attr, constraint_node, [attr])
                        item.setForeground(QtGui.QColor("#e0e0e0"))  # 默认颜色
                        self.attr_list.addItem(item)
                    

    def clear_constraints(self):
        self.attr_list.clear()
        self.constraint_data.clear()  # 清空约束数据

    def refresh_constraints(self):
        self.clear_constraints()
        self.add_selected_constraints()

    def parse_constraint_attr(self, attr):
        parts = attr.split('.')
        if len(parts) != 2:
            return None, None, None

        constraint_node = parts[0]
        target_weight = parts[1]
        if 'W' in target_weight:
            target_name = target_weight.split('W')[0]
            return constraint_node, target_name, target_weight
        return None, None, None

    def get_constraint_info_and_run_tool(self, item):
        is_constraint_mode = self.btn_toggle_display.isChecked()
        
        if is_constraint_mode:
            # 约束节点模式：直接选择节点
            constraint_node = item.text()
            if cmds.objExists(constraint_node):
                cmds.select(constraint_node)
                print(f"选择约束节点: {constraint_node}")
            else:
                cmds.warning(f"约束节点不存在：{constraint_node}")
        else:
            # 权重属性模式：原有的处理逻辑
            attr = item.text()
            constraint_node, target_name, target_weight = self.parse_constraint_attr(attr)
            if constraint_node and target_weight:
                cmds.select(clear=True)
                full_attr_name = f"{constraint_node}.{target_weight}"
                if cmds.objExists(full_attr_name):
                    cmds.select(full_attr_name, add=True)
                    print(f"选择属性通道: {full_attr_name}")
                else:
                    cmds.warning(f"属性通道不存在：{full_attr_name}")
            else:
                cmds.warning(f"无法解析属性: {attr}")

    def remove_selected_items(self):
        for item in self.attr_list.selectedItems():
            self.attr_list.takeItem(self.attr_list.row(item))

    def find_and_select_constraint_attributes(self):
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("请先选择一个物体。")
            return

        weight_attrs = self.get_constraint_weights(selected_objects)
        if weight_attrs:
            for i in range(self.attr_list.count()):
                item = self.attr_list.item(i)
                if item.text() in weight_attrs:
                    item.setSelected(True)

    def select_constraint_node(self):
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个权重通道。")
            return

        constraint_nodes = set()
        for attr in selected_attrs:
            constraint_node, _, _ = self.parse_constraint_attr(attr)
            if constraint_node:
                constraint_nodes.add(constraint_node)

        if constraint_nodes:
            cmds.select(list(constraint_nodes))

    def remove_target(self, maintain_offset=False):
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个权重通道。")
            return

        for attr in selected_attrs:
            constraint_node, target_name, _ = self.parse_constraint_attr(attr)
            if constraint_node and target_name:
                node_type = cmds.nodeType(constraint_node)
                cmds.select(target_name, r=True)
                constrained_object = cmds.listRelatives(constraint_node, parent=True)[0]
                cmds.select(constrained_object, add=True)

                mel_cmd = ""
                if node_type == "pointConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"point", "0"}}'
                elif node_type == "orientConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"orient", "0"}}'
                elif node_type == "parentConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"parent", "0"}}'
                elif node_type == "scaleConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"scale", "0"}}'
                elif node_type == "aimConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"aim", "0"}}'
                elif node_type == "geometryConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"geometry", "0"}}'
                elif node_type == "normalConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"normal", "0"}}'
                elif node_type == "tangentConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"tangent", "0"}}'
                elif node_type == "poleVectorConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"poleVector", "0"}}'
                elif node_type == "pointOnPolyConstraint":
                    mel_cmd = f'doRemoveConstraintTarget {"1" if maintain_offset else "0"} {{"pointOnPoly", "0"}}'
                else:
                    cmds.warning(f"无法识别的约束类型：{node_type}")
                    continue

                mel.eval(mel_cmd)
            else:
                cmds.warning(f"无法解析属性：{attr}")

    def set_rest_position(self):
        """设置静止位置"""
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个条目。")
            return

        constrained_objects = set()
        for attr in selected_attrs:
            if self.btn_toggle_display.isChecked():
                # 约束节点模式
                constraint_node = attr
            else:
                # 权重属性模式
                constraint_node, _, _ = self.parse_constraint_attr(attr)
            
            if constraint_node and constraint_node in self.constraint_data:
                constrained_objects.add(self.constraint_data[constraint_node]['constrained_object'])

        if constrained_objects:
            # 选中所有被约束的物体并设置静止位置
            cmds.select(list(constrained_objects))
            mel.eval('SetRestPosition')
            print(f"为以下物体设置静止位置: {list(constrained_objects)}")

    def modify_constrained_axis(self, maintain_offset=True):
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个条目。")
            return

        for attr in selected_attrs:
            if self.btn_toggle_display.isChecked():
                # 约束节点模式
                constraint_node = attr
                if constraint_node in self.constraint_data:
                    target_objects = self.constraint_data[constraint_node]['target_objects']
                    constrained_object = self.constraint_data[constraint_node]['constrained_object']
                else:
                    continue
            else:
                # 权重属性模式
                constraint_node, target_name, _ = self.parse_constraint_attr(attr)
                if not (constraint_node and constraint_node in self.constraint_data):
                    continue
                target_objects = self.constraint_data[constraint_node]['target_objects']
                constrained_object = self.constraint_data[constraint_node]['constrained_object']
            
            # 获取约束类型
            node_type = cmds.nodeType(constraint_node)
            
            # 选择目标物体和被约束物体
            if target_objects and constrained_object:
                cmds.select(target_objects[0], r=True)  # 选择第一个目标物体
                cmds.select(constrained_object, add=True)
                
                # 根据约束类型执行相应的命令
                mel_cmd = ""
                if node_type in ["pointConstraint", "orientConstraint", "parentConstraint", "scaleConstraint", "aimConstraint"]:
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                elif node_type == "geometryConstraint":
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                elif node_type == "normalConstraint":
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                elif node_type == "tangentConstraint":
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                elif node_type == "poleVectorConstraint":
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                elif node_type == "pointOnPolyConstraint":
                    mel_cmd = f'doModifyConstraintAxes {"1" if maintain_offset else "0"} {{"1","1","1","1"}}'
                else:
                    cmds.warning(f"无法识别的约束类型：{node_type}")
                    continue

                mel.eval(mel_cmd)
                print(f"修改约束轴: {constraint_node}")
            else:
                cmds.warning(f"无法找到目标物体或被约束物体：{constraint_node}")

    def delete_selected_constraints(self):
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个权重通道。")
            return

        for attr in selected_attrs:
            constraint_node, _, _ = self.parse_constraint_attr(attr)
            if constraint_node:
                cmds.delete(constraint_node)
                print(f"删除约束节点：{constraint_node}")
            else:
                cmds.warning(f"无法解析属性：{attr}")
        
        self.refresh_constraints()

    def save_list(self):
        list_name, ok = QtWidgets.QInputDialog.getText(self, "保存列表", "输入列表名称：")
        if ok and list_name:
            locator_name = list_name + "_list"
            if not cmds.objExists(locator_name):
                locator = cmds.spaceLocator(name=locator_name)[0]
                cmds.addAttr(locator, longName="notes", dataType="string")
            
            list_data = []
            for i in range(self.attr_list.count()):
                item = self.attr_list.item(i)
                if not item.is_separator:
                    color = item.foreground().color().name()
                    # 保存约束节点和权重属性信息
                    constraint_node = getattr(item, 'constraint_node', '')
                    weight_attrs = getattr(item, 'weight_attrs', [])
                    weight_attrs_str = ';'.join(weight_attrs) if weight_attrs else ''
                    list_data.append(f"{item.text()}|{color}|{constraint_node}|{weight_attrs_str}")
            
            list_data_str = ','.join(list_data)
            cmds.setAttr(locator_name + ".notes", list_data_str, type="string")
    
            self.add_saved_list_button(locator_name)

    def create_color_changer(self, color):
        def change_color():
            for item in self.attr_list.selectedItems():
                item.setForeground(QtGui.QColor(color))
        return change_color
                                                
    def change_item_color(self, color):
        for item in self.attr_list.selectedItems():
            item.setForeground(QtGui.QColor(color))

    def run_tool(self, mode):
        selected_items = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return

        all_items = [self.attr_list.item(i).text() for i in range(self.attr_list.count())]
        if not all_items:
            cmds.warning("没有找到任何条目。")
            return

        set_keyframe = self.checkbox_set_keyframe.isChecked()

        if self.btn_toggle_display.isChecked():
            # 约束节点模式：获取所有节点的权重属性
            for item in all_items:
                # 获取约束节点的所有权重属性
                weight_attrs = self.get_constraint_weights([item])
                if weight_attrs:
                    for attr in weight_attrs:
                        if cmds.objExists(attr):
                            if mode == 1:  # 设置为0
                                if item in selected_items:
                                    value = 0.0
                                else:
                                    continue  # 跳过未选中的条目
                            elif mode == 2:  # 设置为(1) 0
                                value = 1.0 if item in selected_items else 0.0
                            elif mode == 3:  # 设置为1
                                if item in selected_items:
                                    value = 1.0
                                else:
                                    continue  # 跳过未选中的条目
                            
                            cmds.setAttr(attr, value)
                            if set_keyframe:
                                cmds.setKeyframe(attr)
                            print(f"{attr}: 设置为 {value}" + (" 并添加关键帧。" if set_keyframe else "。"))
        else:
            # 权重属性模式：直接修改属性值
            for attr in all_items:
                if cmds.objExists(attr):
                    if mode == 1:  # 设置为0
                        if attr in selected_items:
                            value = 0.0
                        else:
                            continue  # 跳过未选中的条目
                    elif mode == 2:  # 设置为(1) 0
                        value = 1.0 if attr in selected_items else 0.0
                    elif mode == 3:  # 设置为1
                        if attr in selected_items:
                            value = 1.0
                        else:
                            continue  # 跳过未选中的条目
                    
                    cmds.setAttr(attr, value)
                    if set_keyframe:
                        cmds.setKeyframe(attr)
                    print(f"{attr}: 设置为 {value}" + (" 并添加关键帧。" if set_keyframe else "。"))

    def toggle_display_mode(self):
        is_constraint_mode = self.btn_toggle_display.isChecked()
        self.display_mode_label.setText("当前模式: " + ("约束节点" if is_constraint_mode else "权重属性"))
        self.refresh_display()

    def refresh_display(self):
        """根据当前模式刷新显示内容"""
        current_items = []
        for i in range(self.attr_list.count()):
            item = self.attr_list.item(i)
            if not item.is_separator:
                current_items.append((item.text(), item.foreground().color(), item.constraint_node, item.weight_attrs))

        self.attr_list.clear()
        is_constraint_mode = self.btn_toggle_display.isChecked()

        if is_constraint_mode:
            # 显示约束节点
            constraint_nodes = {}
            constraint_node_list = []
            for attr, color, constraint_node, weight_attrs in current_items:
                if constraint_node:
                    # 如果同一个约束节点有多个权重属性，使用第一个出现的颜色
                    if constraint_node not in constraint_nodes:
                        constraint_nodes[constraint_node] = (color, weight_attrs)
                        constraint_node_list.append(constraint_node)
                        item = CustomListWidgetItem(constraint_node, constraint_node, weight_attrs)
                        item.setForeground(color)
                        self.attr_list.addItem(item)
            
        else:
            # 从约束节点模式切换回权重属性模式
            if current_items and not current_items[0][0].count('.'):  # 检查是否是约束节点模式的数据
                # 获取所有约束节点的权重属性
                constraint_groups = {}
                for node, color, constraint_node, weight_attrs in current_items:
                    if cmds.objExists(node):
                        if not weight_attrs:
                            weight_attrs = self.get_constraint_weights([node])
                        if constraint_node not in constraint_groups:
                            constraint_groups[constraint_node] = []
                        constraint_groups[constraint_node].extend(weight_attrs)
                
                # 按约束节点分组添加
                constraint_node_list = list(constraint_groups.keys())
                for i, constraint_node in enumerate(constraint_node_list):
                    attrs = constraint_groups[constraint_node]
                    for attr in attrs:
                        item = CustomListWidgetItem(attr, constraint_node, [attr])
                        # 使用约束节点的颜色，如果颜色是默认的浅灰色，则使用默认颜色
                        if color.name() == "#e0e0e0":
                            item.setForeground(QtGui.QColor("#e0e0e0"))  # 默认颜色
                        else:
                            item.setForeground(color)
                        self.attr_list.addItem(item)
                    
            else:
                # 如果已经是权重属性格式，直接恢复显示
                constraint_groups = {}
                for attr, color, constraint_node, weight_attrs in current_items:
                    if constraint_node not in constraint_groups:
                        constraint_groups[constraint_node] = []
                    constraint_groups[constraint_node].append((attr, color))
                
                # 按约束节点分组添加
                constraint_node_list = list(constraint_groups.keys())
                for i, constraint_node in enumerate(constraint_node_list):
                    attrs = constraint_groups[constraint_node]
                    for attr, color in attrs:
                        item = CustomListWidgetItem(attr, constraint_node, [attr])
                        # 如果颜色是默认的浅灰色，则使用默认颜色
                        if color.name() == "#e0e0e0":
                            item.setForeground(QtGui.QColor("#e0e0e0"))  # 默认颜色
                        else:
                            item.setForeground(color)
                        self.attr_list.addItem(item)
                    

    def show_select_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        select_constrained = menu.addAction("被约束物体")
        select_current = menu.addAction("条目物体")
        
        action = menu.exec_(self.btn_select_attrs.mapToGlobal(pos))
        if action == select_constrained:
            self.select_constrained_objects()
        elif action == select_current:
            self.select_current_items()

    def select_constrained_objects(self):
        """选中被约束的物体"""
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个条目。")
            return

        constrained_objects = set()
        for attr in selected_attrs:
            if self.btn_toggle_display.isChecked():
                # 约束节点模式
                constraint_node = attr
            else:
                # 权重属性模式
                constraint_node, _, _ = self.parse_constraint_attr(attr)
            
            if constraint_node and constraint_node in self.constraint_data:
                constrained_objects.add(self.constraint_data[constraint_node]['constrained_object'])

        if constrained_objects:
            cmds.select(list(constrained_objects))
            print(f"选中被约束物体: {list(constrained_objects)}")

    def select_target_objects(self):
        """选中实施约束的物体"""
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个条目。")
            return

        target_objects = set()
        for attr in selected_attrs:
            if self.btn_toggle_display.isChecked():
                # 约束节点模式
                constraint_node = attr
            else:
                # 权重属性模式
                constraint_node, _, _ = self.parse_constraint_attr(attr)
            
            if constraint_node and constraint_node in self.constraint_data:
                target_objects.update(self.constraint_data[constraint_node]['target_objects'])

        if target_objects:
            cmds.select(list(target_objects))
            print(f"选中实施约束物体: {list(target_objects)}")

    def select_current_items(self):
        """选中当前条目对应的物体"""
        selected_attrs = [item.text() for item in self.attr_list.selectedItems()]
        if not selected_attrs:
            cmds.warning("请先选择一个或多个条目。")
            return

        cmds.select(clear=True)  # 清除当前选择
        if self.btn_toggle_display.isChecked():
            # 约束节点模式：直接选择约束节点
            for attr in selected_attrs:
                if cmds.objExists(attr):
                    cmds.select(attr, add=True)
            print(f"选中约束节点: {selected_attrs}")
        else:
            # 权重属性模式：选择属性
            for attr in selected_attrs:
                if cmds.objExists(attr):
                    cmds.select(attr, add=True)
            print(f"选中属性: {selected_attrs}")

    def get_constraint_info(self, constraint_node):
        """获取约束节点的详细信息"""
        if not cmds.objExists(constraint_node):
            return None
        
        try:
            constraint_type = cmds.nodeType(constraint_node)
            
            # 获取被约束物体（约束节点的父级）
            constrained_objects = []
            parent = cmds.listRelatives(constraint_node, parent=True)
            if parent:
                constrained_objects = parent
            
            # 获取目标物体（使用targetList查询）
            target_objects = []
            if constraint_type == "parentConstraint":
                target_objects = cmds.parentConstraint(constraint_node, q=True, targetList=True) or []
            elif constraint_type == "pointConstraint":
                target_objects = cmds.pointConstraint(constraint_node, q=True, targetList=True) or []
            elif constraint_type == "orientConstraint":
                target_objects = cmds.orientConstraint(constraint_node, q=True, targetList=True) or []
            elif constraint_type == "scaleConstraint":
                target_objects = cmds.scaleConstraint(constraint_node, q=True, targetList=True) or []
            elif constraint_type == "aimConstraint":
                target_objects = cmds.aimConstraint(constraint_node, q=True, targetList=True) or []
            else:
                # 通用方法：通过连接关系查找目标物体
                target_objects = []
                # 查找所有target连接
                target_attrs = cmds.listAttr(constraint_node, userDefined=False, connectable=True)
                for attr in target_attrs:
                    if attr.startswith('target[') and attr.endswith('].targetParentMatrix'):
                        connections = cmds.listConnections(constraint_node + "." + attr, source=True, destination=False)
                        if connections:
                            target_objects.extend(connections)
            
            # 去重
            target_objects = list(set(target_objects))
            
            return {
                'type': constraint_type,
                'constrained_objects': constrained_objects,
                'target_objects': target_objects
            }
        except Exception as e:
            print(f"获取约束信息失败 {constraint_node}：{str(e)}")
            return None

    def disconnect_constraints(self):
        """断开约束功能"""
        selected_items = [item for item in self.attr_list.selectedItems() if not item.is_separator]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return
        
        disconnected_count = 0
        for item in selected_items:
            if item.is_disconnected:
                print(f"条目 {item.text()} 已经处于断开状态，跳过。")
                continue
                
            constraint_node = item.constraint_node
            if not constraint_node or not cmds.objExists(constraint_node):
                cmds.warning(f"约束节点不存在：{constraint_node}")
                continue
            
            try:
                # 获取约束信息
                constraint_info = self.get_constraint_info(constraint_node)
                if not constraint_info:
                    cmds.warning(f"无法获取约束信息：{constraint_node}")
                    continue
                
                # 保存断开时的信息
                item.disconnected_info = {
                    'constraint_type': constraint_info['type'],
                    'constrained_objects': constraint_info['constrained_objects'],
                    'target_objects': constraint_info['target_objects'],
                    'weight_values': {},  # 保存权重值
                    'original_color': item.foreground().color().name()
                }
                
                # 保存权重值
                for attr in item.weight_attrs:
                    if cmds.objExists(attr):
                        try:
                            weight_value = cmds.getAttr(attr)
                            item.disconnected_info['weight_values'][attr] = weight_value
                        except:
                            pass
                
                # 删除约束节点
                cmds.delete(constraint_node)
                
                # 标记为断开状态
                item.is_disconnected = True
                item.setForeground(QtGui.QColor("#FF6666"))  # 红色表示断开状态
                item.setText(f"[断开] {item.text()}")
                
                disconnected_count += 1
                print(f"已断开约束：{constraint_node}")
                
            except Exception as e:
                cmds.warning(f"断开约束失败 {constraint_node}：{str(e)}")
                continue
        
        if disconnected_count > 0:
            print(f"成功断开 {disconnected_count} 个约束")
            # 刷新显示
            self.attr_list.viewport().update()
    
    def restore_constraints(self):
        """恢复约束功能"""
        selected_items = [item for item in self.attr_list.selectedItems() if not item.is_separator]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return
        
        restored_count = 0
        for item in selected_items:
            if not item.is_disconnected:
                print(f"条目 {item.text()} 未处于断开状态，跳过。")
                continue
            
            if not item.disconnected_info:
                cmds.warning(f"条目 {item.text()} 缺少断开信息，无法恢复。")
                continue
            
            try:
                constraint_type = item.disconnected_info['constraint_type']
                constrained_objects = item.disconnected_info['constrained_objects']
                target_objects = item.disconnected_info['target_objects']
                weight_values = item.disconnected_info['weight_values']
                original_color = item.disconnected_info['original_color']
                
                # 检查物体是否存在
                missing_objects = []
                for obj in constrained_objects + target_objects:
                    if not cmds.objExists(obj):
                        missing_objects.append(obj)
                
                if missing_objects:
                    cmds.warning(f"恢复约束失败，以下物体不存在：{', '.join(missing_objects)}")
                    continue
                
                # 根据约束类型重新创建约束
                new_constraint = None
                if constraint_type == "parentConstraint":
                    new_constraint = cmds.parentConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "pointConstraint":
                    new_constraint = cmds.pointConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "orientConstraint":
                    new_constraint = cmds.orientConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "scaleConstraint":
                    new_constraint = cmds.scaleConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "aimConstraint":
                    new_constraint = cmds.aimConstraint(target_objects, constrained_objects, maintainOffset=True)
                else:
                    cmds.warning(f"不支持的约束类型：{constraint_type}")
                    continue
                
                if new_constraint:
                    # 恢复权重值
                    for attr, weight_value in weight_values.items():
                        new_attr = attr.replace(item.constraint_node, new_constraint[0])
                        if cmds.objExists(new_attr):
                            try:
                                cmds.setAttr(new_attr, weight_value)
                            except:
                                pass
                    
                    # 更新条目信息
                    item.constraint_node = new_constraint[0]
                    item.is_disconnected = False
                    item.setForeground(QtGui.QColor(original_color))
                    item.setText(item.text().replace("[断开] ", ""))
                    
                    # 更新约束数据
                    if new_constraint[0] in self.constraint_data:
                        self.constraint_data[new_constraint[0]] = {
                            'constrained_object': constrained_objects[0] if constrained_objects else '',
                            'target_objects': target_objects
                        }
                    
                    restored_count += 1
                    print(f"已恢复约束：{new_constraint[0]} (类型: {constraint_type})")
                
            except Exception as e:
                cmds.warning(f"恢复约束失败 {item.text()}：{str(e)}")
                continue
        
        if restored_count > 0:
            print(f"成功恢复 {restored_count} 个约束")
            # 刷新显示
            self.attr_list.viewport().update()
    
    def reverse_constraints(self):
        """反向约束功能"""
        selected_items = [item for item in self.attr_list.selectedItems() if not item.is_separator]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return
        
        reversed_count = 0
        for item in selected_items:
            try:
                # 获取约束信息
                if item.is_disconnected:
                    # 断开状态：使用保存的断开信息
                    if not item.disconnected_info:
                        cmds.warning(f"条目 {item.text()} 缺少断开信息，无法反向。")
                        continue
                    
                    constraint_type = item.disconnected_info['constraint_type']
                    constrained_objects = item.disconnected_info['constrained_objects']
                    target_objects = item.disconnected_info['target_objects']
                    weight_values = item.disconnected_info['weight_values']
                    original_color = item.disconnected_info['original_color']
                    
                    # 打印原始关系
                    print(f"原始约束关系：{', '.join(target_objects)} 约束 {', '.join(constrained_objects)}")
                    print(f"反向后关系：{', '.join(constrained_objects)} 约束 {', '.join(target_objects)}")
                    
                    # 检查物体是否存在
                    missing_objects = []
                    for obj in constrained_objects + target_objects:
                        if not cmds.objExists(obj):
                            missing_objects.append(obj)
                    
                    if missing_objects:
                        cmds.warning(f"反向约束失败，以下物体不存在：{', '.join(missing_objects)}")
                        continue
                    
                    # 创建反向约束（逐个处理多目标约束）
                    # 反向：原被约束对象 -> 新目标对象，原目标对象 -> 新被约束对象
                    new_constraints = []
                    for target_obj in target_objects:
                        if constraint_type == "parentConstraint":
                            new_constraint = cmds.parentConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "pointConstraint":
                            new_constraint = cmds.pointConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "orientConstraint":
                            new_constraint = cmds.orientConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "scaleConstraint":
                            new_constraint = cmds.scaleConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "aimConstraint":
                            new_constraint = cmds.aimConstraint(target_obj, constrained_objects, maintainOffset=True)
                        else:
                            cmds.warning(f"不支持的约束类型：{constraint_type}")
                            continue
                        
                        if new_constraint:
                            new_constraints.extend(new_constraint)
                    
                    if new_constraints:
                        # 恢复权重值（只处理第一个约束的权重）
                        if new_constraints and weight_values:
                            for attr, weight_value in weight_values.items():
                                new_attr = attr.replace(item.constraint_node, new_constraints[0])
                                if cmds.objExists(new_attr):
                                    try:
                                        cmds.setAttr(new_attr, weight_value)
                                    except:
                                        pass
                        
                        # 更新条目信息（使用第一个约束节点）
                        item.constraint_node = new_constraints[0]
                        item.is_disconnected = False
                        item.setForeground(QtGui.QColor(original_color))
                        item.setText(f"[反向] {item.text().replace('[断开] ', '')}")
                        
                        # 更新约束数据
                        if new_constraints[0] in self.constraint_data:
                            self.constraint_data[new_constraints[0]] = {
                                'constrained_object': target_objects[0] if target_objects else '',
                                'target_objects': constrained_objects
                            }
                        
                        reversed_count += 1
                        print(f"已创建反向约束：{', '.join(new_constraints)} (类型: {constraint_type})")
                
                else:
                    # 正常状态：获取当前约束信息
                    constraint_node = item.constraint_node
                    if not constraint_node or not cmds.objExists(constraint_node):
                        cmds.warning(f"约束节点不存在：{constraint_node}")
                        continue
                    
                    constraint_info = self.get_constraint_info(constraint_node)
                    if not constraint_info:
                        cmds.warning(f"无法获取约束信息：{constraint_node}")
                        continue
                    
                    constraint_type = constraint_info['type']
                    constrained_objects = constraint_info['constrained_objects']
                    target_objects = constraint_info['target_objects']
                    
                    # 打印原始关系
                    print(f"原始约束关系：{', '.join(target_objects)} 约束 {', '.join(constrained_objects)}")
                    print(f"反向后关系：{', '.join(constrained_objects)} 约束 {', '.join(target_objects)}")
                    
                    # 检查物体是否存在
                    missing_objects = []
                    for obj in constrained_objects + target_objects:
                        if not cmds.objExists(obj):
                            missing_objects.append(obj)
                    
                    if missing_objects:
                        cmds.warning(f"反向约束失败，以下物体不存在：{', '.join(missing_objects)}")
                        continue
                    
                    # 保存权重值
                    weight_values = {}
                    for attr in item.weight_attrs:
                        if cmds.objExists(attr):
                            try:
                                weight_value = cmds.getAttr(attr)
                                weight_values[attr] = weight_value
                            except:
                                pass
                    
                    # 删除原约束
                    cmds.delete(constraint_node)
                    
                    # 创建反向约束（逐个处理多目标约束）
                    # 反向：原被约束对象 -> 新目标对象，原目标对象 -> 新被约束对象
                    new_constraints = []
                    for target_obj in target_objects:
                        if constraint_type == "parentConstraint":
                            new_constraint = cmds.parentConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "pointConstraint":
                            new_constraint = cmds.pointConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "orientConstraint":
                            new_constraint = cmds.orientConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "scaleConstraint":
                            new_constraint = cmds.scaleConstraint(target_obj, constrained_objects, maintainOffset=True)
                        elif constraint_type == "aimConstraint":
                            new_constraint = cmds.aimConstraint(target_obj, constrained_objects, maintainOffset=True)
                        else:
                            cmds.warning(f"不支持的约束类型：{constraint_type}")
                            continue
                        
                        if new_constraint:
                            new_constraints.extend(new_constraint)
                    
                    if new_constraints:
                        # 恢复权重值（只处理第一个约束的权重）
                        if new_constraints and weight_values:
                            for attr, weight_value in weight_values.items():
                                new_attr = attr.replace(constraint_node, new_constraints[0])
                                if cmds.objExists(new_attr):
                                    try:
                                        cmds.setAttr(new_attr, weight_value)
                                    except:
                                        pass
                        
                        # 更新条目信息（使用第一个约束节点）
                        item.constraint_node = new_constraints[0]
                        item.setText(f"[反向] {item.text()}")
                        
                        # 更新约束数据
                        if new_constraints[0] in self.constraint_data:
                            self.constraint_data[new_constraints[0]] = {
                                'constrained_object': target_objects[0] if target_objects else '',
                                'target_objects': constrained_objects
                            }
                        
                        reversed_count += 1
                        print(f"已创建反向约束：{', '.join(new_constraints)} (类型: {constraint_type})")
                
            except Exception as e:
                cmds.warning(f"反向约束失败 {item.text()}：{str(e)}")
                continue
        
        if reversed_count > 0:
            print(f"成功反向 {reversed_count} 个约束")
            # 刷新显示
            self.attr_list.viewport().update()
    
    def rebuild_constraints(self):
        """重建约束功能"""
        selected_items = [item for item in self.attr_list.selectedItems() if not item.is_separator]
        if not selected_items:
            cmds.warning("请先选择一个或多个条目。")
            return
        
        rebuilt_count = 0
        for item in selected_items:
            constraint_node = item.constraint_node
            if not constraint_node or not cmds.objExists(constraint_node):
                cmds.warning(f"约束节点不存在：{constraint_node}")
                continue
            
            try:
                # 获取约束信息
                constraint_info = self.get_constraint_info(constraint_node)
                if not constraint_info:
                    cmds.warning(f"无法获取约束信息：{constraint_node}")
                    continue
                
                constraint_type = constraint_info['type']
                constrained_objects = constraint_info['constrained_objects']
                target_objects = constraint_info['target_objects']
                
                # 检查物体是否存在
                missing_objects = []
                for obj in constrained_objects + target_objects:
                    if not cmds.objExists(obj):
                        missing_objects.append(obj)
                
                if missing_objects:
                    cmds.warning(f"重建约束失败，以下物体不存在：{', '.join(missing_objects)}")
                    continue
                
                # 保存权重值
                weight_values = {}
                for attr in item.weight_attrs:
                    if cmds.objExists(attr):
                        try:
                            weight_value = cmds.getAttr(attr)
                            weight_values[attr] = weight_value
                        except:
                            pass
                
                # 删除原约束
                cmds.delete(constraint_node)
                
                # 重新创建约束
                new_constraint = None
                if constraint_type == "parentConstraint":
                    new_constraint = cmds.parentConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "pointConstraint":
                    new_constraint = cmds.pointConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "orientConstraint":
                    new_constraint = cmds.orientConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "scaleConstraint":
                    new_constraint = cmds.scaleConstraint(target_objects, constrained_objects, maintainOffset=True)
                elif constraint_type == "aimConstraint":
                    new_constraint = cmds.aimConstraint(target_objects, constrained_objects, maintainOffset=True)
                else:
                    cmds.warning(f"不支持的约束类型：{constraint_type}")
                    continue
                
                if new_constraint:
                    # 恢复权重值
                    for attr, weight_value in weight_values.items():
                        new_attr = attr.replace(constraint_node, new_constraint[0])
                        if cmds.objExists(new_attr):
                            try:
                                cmds.setAttr(new_attr, weight_value)
                            except:
                                pass
                    
                    # 更新条目信息
                    item.constraint_node = new_constraint[0]
                    item.setText(item.text().replace("[断开] ", "").replace("[反向] ", ""))
                    
                    # 更新约束数据
                    if new_constraint[0] in self.constraint_data:
                        self.constraint_data[new_constraint[0]] = {
                            'constrained_object': constrained_objects[0] if constrained_objects else '',
                            'target_objects': target_objects
                        }
                    
                    rebuilt_count += 1
                    print(f"已重建约束：{new_constraint[0]} (类型: {constraint_type})")
                
            except Exception as e:
                cmds.warning(f"重建约束失败 {constraint_node}：{str(e)}")
                continue
        
        if rebuilt_count > 0:
            print(f"成功重建 {rebuilt_count} 个约束")
            # 刷新显示
            self.attr_list.viewport().update()

class CustomListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, text, constraint_node=None, weight_attrs=None, is_separator=False):
        super(CustomListWidgetItem, self).__init__(text)
        self.constraint_node = constraint_node
        self.weight_attrs = weight_attrs or []
        self.is_separator = is_separator
        
        # 断开状态相关属性
        self.is_disconnected = False
        self.disconnected_info = {}  # 存储断开时的约束信息
        
        if is_separator:
            self.setFlags(QtCore.Qt.NoItemFlags)
            self.setBackground(QtGui.QColor("#555555"))
            self.setForeground(QtGui.QColor("#888888"))
            self.setText("────────────────────────────────")
            self.setSizeHint(QtCore.QSize(0, 1))

class WeightIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(WeightIconDelegate, self).__init__(parent)
        self.list_widget = parent
    
    def paint(self, painter, option, index):
        # 从列表控件获取项
        if self.list_widget:
            item = self.list_widget.item(index.row())
            if item and hasattr(item, 'weight_attrs') and item.weight_attrs:
                # 绘制权重图标（在文字前面）
                rect = option.rect
                icon_spacing = 2
                start_x = rect.left() + 5  # 从左边开始绘制
                
                # 先绘制图标
                for i, attr in enumerate(item.weight_attrs):
                    if cmds.objExists(attr):
                        try:
                            weight_value = cmds.getAttr(attr)
                            # 四舍五入到整数
                            rounded_value = round(weight_value)
                            
                            # 根据权重值选择颜色
                            if rounded_value == 0:
                                color = QtGui.QColor("#666666")  # 灰色
                            elif rounded_value == 1:
                                color = QtGui.QColor("#00FF00")  # 绿色
                            else:
                                color = QtGui.QColor("#FFAA00")  # 橙色
                            
                            # 绘制长条图标
                            bar_width = 20
                            bar_height = 12
                            icon_rect = QtCore.QRect(start_x + i * (bar_width + icon_spacing), 
                                                   rect.center().y() - bar_height//2, 
                                                   bar_width, bar_height)
                            painter.setBrush(QtGui.QBrush(color))
                            painter.setPen(QtGui.QPen(color, 1))
                            painter.drawRect(icon_rect)
                            
                            # 绘制权重数值
                            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
                            painter.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
                            text_rect = QtCore.QRect(icon_rect.x() + 2, icon_rect.y() + 1, 
                                                    bar_width - 4, bar_height - 2)
                            painter.drawText(text_rect, QtCore.Qt.AlignCenter, str(rounded_value))
                        except:
                            pass
                
                # 调整文字位置，为图标留出空间
                if item.weight_attrs:
                    bar_width = 20
                    text_offset = len(item.weight_attrs) * (bar_width + icon_spacing) + 10
                    option.rect = QtCore.QRect(rect.x() + text_offset, rect.y(), 
                                             rect.width() - text_offset, rect.height())
        
        # 绘制背景
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, QtGui.QColor("#4B4B4B"))
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(option.rect, QtGui.QColor("#3B3B3B"))
        
        # 绘制文字，保持用户设置的颜色
        if item:
            text_color = item.foreground().color()
            painter.setPen(QtGui.QPen(text_color))
            painter.setFont(option.font)
            
            # 绘制文字
            text_rect = option.rect.adjusted(5, 0, -5, 0)
            painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, item.text())

class CustomListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # 设置自定义委托
        self.setItemDelegate(WeightIconDelegate(self))
        # 启用悬停提示
        self.setMouseTracking(True)
        self.current_hover_item = None
    
    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item != self.current_hover_item:
            self.current_hover_item = item
            if item and hasattr(item, 'constraint_node') and item.constraint_node:
                # 获取约束信息
                tooltip_text = self.get_constraint_tooltip(item)
                self.setToolTip(tooltip_text)
            else:
                self.setToolTip("")
        super(CustomListWidget, self).mouseMoveEvent(event)
    
    def get_constraint_tooltip(self, item):
        """获取约束的提示信息"""
        if not hasattr(item, 'constraint_node') or not item.constraint_node:
            return ""
        
        constraint_node = item.constraint_node
        tooltip_parts = [f"约束节点: {constraint_node}"]
        
        # 获取约束数据
        if hasattr(self.parent(), 'constraint_data') and constraint_node in self.parent().constraint_data:
            data = self.parent().constraint_data[constraint_node]
            if 'constrained_object' in data:
                tooltip_parts.append(f"被约束物体: {data['constrained_object']}")
            if 'target_objects' in data and data['target_objects']:
                targets = ', '.join(data['target_objects'])
                tooltip_parts.append(f"目标物体: {targets}")
        
        # 添加权重信息
        if hasattr(item, 'weight_attrs') and item.weight_attrs:
            weight_info = []
            for attr in item.weight_attrs:
                if cmds.objExists(attr):
                    try:
                        weight_value = cmds.getAttr(attr)
                        weight_info.append(f"{attr.split('.')[-1]}: {weight_value:.2f}")
                    except:
                        pass
            if weight_info:
                tooltip_parts.append(f"权重: {' | '.join(weight_info)}")
        
        return '\n'.join(tooltip_parts)

if __name__ == "__main__":
    try:
        constraint_tool_ui.close()
        constraint_tool_ui.deleteLater()
    except:
        pass

    constraint_tool_ui = ConstraintTool(parent=maya_main_window())
    constraint_tool_ui.show() 