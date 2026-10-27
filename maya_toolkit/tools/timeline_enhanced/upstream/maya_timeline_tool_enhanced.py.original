# -*- coding: utf-8 -*-
"""
Maya Timeline Tool Enhanced Version
增强版Maya时间轴工具，包含更多高级功能
"""

import maya.cmds as cmds
import maya.mel as mel
import json
import os

class TimelineToolEnhanced(object):
    def __init__(self):
        self.window_name = "timelineToolEnhancedWindow"
        self.frame_count = 100
        self.start_frame = 1
        self.blocks = {}
        self.selected_blocks = set()  # 选中的方块
        self.dragging_block = None
        self.drag_source_frame = None
        self.clipboard = {}  # 剪贴板
        
        # 界面尺寸设置
        self.frame_width = 25
        self.frame_height = 35
        self.block_size = 18
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), "timeline_config.json")
        
        # 预定义的方块类型
        self.block_types = {
            "keyframe": {"color": (1.0, 0.3, 0.3), "label": "K", "name": "关键帧"},
            "breakdown": {"color": (0.3, 1.0, 0.3), "label": "B", "name": "分解帧"},
            "inbetween": {"color": (0.3, 0.3, 1.0), "label": "I", "name": "中间帧"},
            "hold": {"color": (1.0, 1.0, 0.3), "label": "H", "name": "保持帧"},
            "camera": {"color": (1.0, 0.6, 0.0), "label": "C", "name": "镜头"},
            "effect": {"color": (0.8, 0.0, 0.8), "label": "E", "name": "特效"},
        }
        
    def create_ui(self):
        """创建增强版界面"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        cmds.window(self.window_name,
                   title="Timeline Tool Enhanced",
                   widthHeight=(900, 300),
                   resizeToFitChildren=True,
                   menuBar=True)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主布局
        main_layout = cmds.columnLayout(adjustableColumn=True,
                                      columnOffset=("both", 10))
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建控制面板
        self.create_control_panel()
        
        # 创建方块类型面板
        self.create_block_type_panel()
        
        # 创建时间轴区域
        self.create_timeline_area()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 加载配置
        self.load_config()
        
        cmds.showWindow(self.window_name)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        file_menu = cmds.menu(label="文件")
        cmds.menuItem(label="新建", command=self.new_project)
        cmds.menuItem(label="打开配置", command=self.load_config_dialog)
        cmds.menuItem(label="保存配置", command=self.save_config_dialog)
        cmds.menuItem(divider=True)
        cmds.menuItem(label="退出", command=self.close_window)
        
        edit_menu = cmds.menu(label="编辑")
        cmds.menuItem(label="全选方块", command=self.select_all_blocks)
        cmds.menuItem(label="取消选择", command=self.deselect_all_blocks)
        cmds.menuItem(divider=True)
        cmds.menuItem(label="复制选中方块", command=self.copy_selected_blocks)
        cmds.menuItem(label="粘贴方块", command=self.paste_blocks)
        cmds.menuItem(label="删除选中方块", command=self.delete_selected_blocks)
        
        view_menu = cmds.menu(label="视图")
        cmds.menuItem(label="缩放到适合", command=self.fit_timeline)
        cmds.menuItem(label="重置视图", command=self.reset_view)
        
        help_menu = cmds.menu(label="帮助")
        cmds.menuItem(label="使用说明", command=self.show_help)
        cmds.menuItem(label="关于", command=self.show_about)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar_layout = cmds.rowLayout(numberOfColumns=8,
                                      columnWidth8=(50, 50, 50, 50, 50, 50, 50, 50),
                                      columnAlign=(1, "center"),
                                      height=40)
        
        # 工具按钮
        cmds.iconTextButton(label="选择", style="iconAndTextVertical",
                           image="selectObject.png", command=self.set_select_mode)
        cmds.iconTextButton(label="添加", style="iconAndTextVertical", 
                           image="addClip.png", command=self.set_add_mode)
        cmds.iconTextButton(label="删除", style="iconAndTextVertical",
                           image="removeClip.png", command=self.set_delete_mode)
        cmds.iconTextButton(label="复制", style="iconAndTextVertical",
                           image="copyClip.png", command=self.copy_selected_blocks)
        cmds.iconTextButton(label="粘贴", style="iconAndTextVertical",
                           image="pasteClip.png", command=self.paste_blocks)
        cmds.separator(style="in")
        cmds.iconTextButton(label="播放", style="iconAndTextVertical",
                           image="play.png", command=self.play_timeline)
        cmds.iconTextButton(label="停止", style="iconAndTextVertical",
                           image="stop.png", command=self.stop_timeline)
        
        cmds.setParent('..')
        
    def create_control_panel(self):
        """创建控制面板"""
        control_frame = cmds.frameLayout(label="时间轴控制",
                                       collapsable=True,
                                       marginHeight=5,
                                       marginWidth=5,
                                       collapse=False)
        
        cmds.rowLayout(numberOfColumns=8,
                      columnWidth8=(60, 60, 60, 60, 80, 80, 80, 100),
                      columnAlign=(1, "right"))
        
        cmds.text(label="起始帧:")
        self.start_frame_field = cmds.intField(value=self.start_frame,
                                             minValue=1,
                                             changeCommand=self.on_start_frame_changed)
        
        cmds.text(label="帧数:")
        self.frame_count_field = cmds.intField(value=self.frame_count,
                                             minValue=10,
                                             maxValue=1000,
                                             changeCommand=self.on_frame_count_changed)
        
        cmds.text(label="当前帧:")
        self.current_frame_field = cmds.intField(value=1,
                                               changeCommand=self.on_current_frame_changed)
        
        cmds.button(label="同步Maya", command=self.sync_with_maya)
        cmds.button(label="清空选择", command=self.deselect_all_blocks)
        cmds.button(label="清空所有", command=self.clear_all_blocks)
        
        cmds.setParent('..')
        cmds.setParent('..')
        
    def create_block_type_panel(self):
        """创建方块类型面板"""
        type_frame = cmds.frameLayout(label="方块类型",
                                    collapsable=True,
                                    marginHeight=5,
                                    marginWidth=5,
                                    collapse=False)
        
        type_layout = cmds.rowLayout(numberOfColumns=len(self.block_types),
                                   columnWidth=[(i+1, 80) for i in range(len(self.block_types))])
        
        self.type_buttons = {}
        for i, (type_key, type_data) in enumerate(self.block_types.items()):
            button = cmds.button(label=f"{type_data['label']}\n{type_data['name']}",
                               backgroundColor=type_data['color'],
                               height=35,
                               command=lambda x, t=type_key: self.set_current_block_type(t))
            self.type_buttons[type_key] = button
            
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 设置默认选择
        self.current_block_type = "keyframe"
        
    def create_timeline_area(self):
        """创建时间轴区域"""
        timeline_frame = cmds.frameLayout(label="时间轴",
                                        collapsable=False,
                                        marginHeight=5,
                                        marginWidth=5)
        
        # 创建滚动区域
        scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=16,
                                        childResizable=True,
                                        height=150)
        
        # 创建时间轴容器 - 使用formLayout避免列数限制
        self.timeline_layout = cmds.formLayout()
        
        self.create_frames()
        
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        
    def create_status_bar(self):
        """创建状态栏"""
        status_layout = cmds.rowLayout(numberOfColumns=3,
                                     columnWidth3=(200, 200, 300),
                                     columnAlign=(1, "left"))
        
        self.status_text = cmds.text(label="就绪", align="left")
        self.selection_text = cmds.text(label="选中: 0 个方块", align="left")
        self.frame_info_text = cmds.text(label="当前帧: 1", align="left")
        
        cmds.setParent('..')
        
    def create_frames(self):
        """创建时间轴的每一帧"""
        self.frame_layouts = {}
        self.frame_buttons = {}
        
        for i in range(self.frame_count):
            frame_num = self.start_frame + i
            
            # 创建每帧的垂直布局
            frame_layout = cmds.columnLayout(adjustableColumn=True,
                                          columnAlign="center",
                                          parent=self.timeline_layout,
                                          width=self.frame_width)
            
            # 帧数标签
            cmds.text(label=str(frame_num),
                     height=15,
                     font="smallFixedWidthFont")
            
            # 方块区域
            block_button = cmds.button(label="",
                                     width=self.block_size,
                                     height=self.block_size,
                                     backgroundColor=(0.25, 0.25, 0.25),
                                     command=lambda x, f=frame_num: self.on_frame_clicked(f))
            
            # 添加右键菜单
            cmds.popupMenu(parent=block_button)
            cmds.menuItem(label="添加方块", command=lambda x, f=frame_num: self.add_block_at_frame(f))
            cmds.menuItem(label="删除方块", command=lambda x, f=frame_num: self.delete_block_at_frame(f))
            cmds.menuItem(divider=True)
            cmds.menuItem(label="选择此方块", command=lambda x, f=frame_num: self.select_block_at_frame(f))
            cmds.menuItem(label="编辑方块属性", command=lambda x, f=frame_num: self.edit_block_properties(f))
            
            self.frame_layouts[frame_num] = frame_layout
            self.frame_buttons[frame_num] = block_button
            
            cmds.setParent('..')  # 返回到timeline_layout
            
            # 使用formLayout设置位置
            left_pos = i * self.frame_width
            cmds.formLayout(self.timeline_layout, edit=True,
                           attachForm=[(frame_layout, 'top', 0),
                                     (frame_layout, 'bottom', 0),
                                     (frame_layout, 'left', left_pos)])
            
    # 各种事件处理函数
    def on_frame_clicked(self, frame_num):
        """帧点击处理"""
        # 检查是否按住Ctrl键进行多选
        modifiers = cmds.getModifiers()
        ctrl_pressed = modifiers & 4  # Ctrl键
        
        if frame_num in self.blocks:
            if ctrl_pressed:
                # 多选模式
                if frame_num in self.selected_blocks:
                    self.selected_blocks.remove(frame_num)
                else:
                    self.selected_blocks.add(frame_num)
            else:
                # 单选模式
                if self.dragging_block is not None:
                    # 正在拖拽，放置方块
                    self.drop_block(frame_num)
                else:
                    # 开始拖拽
                    self.start_drag(frame_num)
        else:
            # 空帧
            if self.dragging_block is not None:
                self.drop_block(frame_num)
            else:
                self.add_block_at_frame(frame_num)
                
        self.update_status()
        self.update_blocks_display()
        
    def start_drag(self, frame_num):
        """开始拖拽"""
        if frame_num in self.blocks:
            self.dragging_block = self.blocks[frame_num]
            self.drag_source_frame = frame_num
            self.update_status(f"拖拽帧 {frame_num} 的方块...")
            
    def drop_block(self, target_frame):
        """放置方块"""
        if self.dragging_block is not None and self.drag_source_frame is not None:
            # 如果目标帧已有方块，询问是否替换
            if target_frame in self.blocks:
                result = cmds.confirmDialog(title="确认",
                                          message=f"帧 {target_frame} 已有方块，是否替换？",
                                          button=["替换", "取消"],
                                          defaultButton="替换",
                                          cancelButton="取消",
                                          dismissString="取消")
                if result == "取消":
                    self.cancel_drag()
                    return
                    
            # 移动方块
            if self.drag_source_frame in self.blocks:
                del self.blocks[self.drag_source_frame]
                
            self.blocks[target_frame] = self.dragging_block
            
            # 重置拖拽状态
            self.dragging_block = None
            self.drag_source_frame = None
            
            self.update_status(f"方块已移动到帧 {target_frame}")
            
    def cancel_drag(self):
        """取消拖拽"""
        self.dragging_block = None
        self.drag_source_frame = None
        self.update_status("取消拖拽")
        
    def add_block_at_frame(self, frame_num):
        """在指定帧添加方块"""
        if self.current_block_type in self.block_types:
            block_data = self.block_types[self.current_block_type].copy()
            self.blocks[frame_num] = block_data
            self.update_status(f"在帧 {frame_num} 添加了 {block_data['name']}")
            self.update_blocks_display()
            
    def delete_block_at_frame(self, frame_num):
        """删除指定帧的方块"""
        if frame_num in self.blocks:
            del self.blocks[frame_num]
            if frame_num in self.selected_blocks:
                self.selected_blocks.remove(frame_num)
            self.update_status(f"删除了帧 {frame_num} 的方块")
            self.update_blocks_display()
            
    def select_block_at_frame(self, frame_num):
        """选择指定帧的方块"""
        if frame_num in self.blocks:
            self.selected_blocks.clear()
            self.selected_blocks.add(frame_num)
            self.update_blocks_display()
            self.update_status(f"选中帧 {frame_num} 的方块")
            
    def edit_block_properties(self, frame_num):
        """编辑方块属性"""
        if frame_num not in self.blocks:
            return
            
        # 创建属性编辑对话框
        if cmds.window("blockPropertiesWindow", exists=True):
            cmds.deleteUI("blockPropertiesWindow")
            
        window = cmds.window("blockPropertiesWindow",
                           title=f"编辑帧 {frame_num} 方块属性",
                           widthHeight=(300, 200))
        
        layout = cmds.columnLayout(adjustableColumn=True, margin=10)
        
        block_data = self.blocks[frame_num]
        
        cmds.text(label="方块标签:")
        label_field = cmds.textField(text=block_data.get('label', ''))
        
        cmds.text(label="方块名称:")
        name_field = cmds.textField(text=block_data.get('name', ''))
        
        cmds.text(label="颜色:")
        color = block_data.get('color', (0.5, 0.5, 0.5))
        color_slider_r = cmds.floatSlider(min=0, max=1, value=color[0], step=0.01)
        color_slider_g = cmds.floatSlider(min=0, max=1, value=color[1], step=0.01)
        color_slider_b = cmds.floatSlider(min=0, max=1, value=color[2], step=0.01)
        
        def apply_changes(*args):
            new_label = cmds.textField(label_field, query=True, text=True)
            new_name = cmds.textField(name_field, query=True, text=True)
            new_color = (
                cmds.floatSlider(color_slider_r, query=True, value=True),
                cmds.floatSlider(color_slider_g, query=True, value=True),
                cmds.floatSlider(color_slider_b, query=True, value=True)
            )
            
            self.blocks[frame_num]['label'] = new_label
            self.blocks[frame_num]['name'] = new_name
            self.blocks[frame_num]['color'] = new_color
            
            self.update_blocks_display()
            cmds.deleteUI("blockPropertiesWindow")
            
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 150))
        cmds.button(label="应用", command=apply_changes)
        cmds.button(label="取消", command=lambda x: cmds.deleteUI("blockPropertiesWindow"))
        
        cmds.showWindow(window)
        
    def set_current_block_type(self, block_type):
        """设置当前方块类型"""
        self.current_block_type = block_type
        
        # 更新按钮外观
        for type_key, button in self.type_buttons.items():
            if type_key == block_type:
                cmds.button(button, edit=True, backgroundColor=(1.0, 1.0, 1.0))
            else:
                color = self.block_types[type_key]['color']
                cmds.button(button, edit=True, backgroundColor=color)
                
        self.update_status(f"当前方块类型: {self.block_types[block_type]['name']}")
        
    def update_blocks_display(self):
        """更新方块显示"""
        for i in range(self.frame_count):
            frame_num = self.start_frame + i
            
            if frame_num in self.frame_buttons:
                button = self.frame_buttons[frame_num]
                
                if frame_num in self.blocks:
                    block_data = self.blocks[frame_num]
                    color = block_data.get('color', (0.5, 0.5, 0.5))
                    label = block_data.get('label', '●')
                    
                    # 如果是拖拽中的方块，显示特殊颜色
                    if frame_num == self.drag_source_frame and self.dragging_block is not None:
                        color = (1.0, 1.0, 0.0)  # 黄色
                        label = "拖拽"
                    # 如果是选中的方块，添加边框效果
                    elif frame_num in self.selected_blocks:
                        # Maya GUI限制，无法直接添加边框，用亮度调整表示选中
                        color = tuple(min(1.0, c + 0.2) for c in color)
                        
                    cmds.button(button,
                               edit=True,
                               backgroundColor=color,
                               label=label)
                else:
                    cmds.button(button,
                               edit=True,
                               backgroundColor=(0.25, 0.25, 0.25),
                               label="")
                               
    def update_status(self, message=None):
        """更新状态栏"""
        if message:
            cmds.text(self.status_text, edit=True, label=message)
            
        # 更新选择信息
        selected_count = len(self.selected_blocks)
        cmds.text(self.selection_text, edit=True, 
                 label=f"选中: {selected_count} 个方块")
        
        # 更新当前帧信息
        current_frame = cmds.intField(self.current_frame_field, query=True, value=True)
        cmds.text(self.frame_info_text, edit=True, 
                 label=f"当前帧: {current_frame}")
                 
    # 菜单命令实现
    def new_project(self, *args):
        """新建项目"""
        result = cmds.confirmDialog(title="新建项目",
                                  message="确定要清空当前所有数据吗？",
                                  button=["确定", "取消"],
                                  defaultButton="确定",
                                  cancelButton="取消")
        if result == "确定":
            self.clear_all_blocks()
            
    def save_config_dialog(self, *args):
        """保存配置对话框"""
        self.save_config()
        cmds.confirmDialog(title="保存",
                         message="配置已保存",
                         button=["确定"])
                         
    def load_config_dialog(self, *args):
        """加载配置对话框"""
        self.load_config()
        cmds.confirmDialog(title="加载",
                         message="配置已加载",
                         button=["确定"])
                         
    def save_config(self):
        """保存配置到文件"""
        config = {
            "start_frame": self.start_frame,
            "frame_count": self.frame_count,
            "blocks": {}
        }
        
        # 转换方块数据为可序列化格式
        for frame, block_data in self.blocks.items():
            config["blocks"][str(frame)] = block_data
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            cmds.warning(f"保存配置失败: {e}")
            
    def load_config(self):
        """从文件加载配置"""
        if not os.path.exists(self.config_file):
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.start_frame = config.get("start_frame", 1)
            self.frame_count = config.get("frame_count", 100)
            
            # 加载方块数据
            self.blocks.clear()
            blocks_data = config.get("blocks", {})
            for frame_str, block_data in blocks_data.items():
                frame_num = int(frame_str)
                self.blocks[frame_num] = block_data
                
            # 更新界面
            cmds.intField(self.start_frame_field, edit=True, value=self.start_frame)
            cmds.intField(self.frame_count_field, edit=True, value=self.frame_count)
            self.refresh_timeline()
            
        except Exception as e:
            cmds.warning(f"加载配置失败: {e}")
            
    # 其他实用功能
    def sync_with_maya(self, *args):
        """与Maya时间轴同步"""
        maya_start = cmds.playbackOptions(query=True, minTime=True)
        maya_end = cmds.playbackOptions(query=True, maxTime=True)
        
        self.start_frame = int(maya_start)
        self.frame_count = int(maya_end - maya_start + 1)
        
        cmds.intField(self.start_frame_field, edit=True, value=self.start_frame)
        cmds.intField(self.frame_count_field, edit=True, value=self.frame_count)
        
        self.refresh_timeline()
        self.update_status("已与Maya时间轴同步")
        
    def play_timeline(self, *args):
        """播放时间轴"""
        cmds.play(forward=True)
        
    def stop_timeline(self, *args):
        """停止播放"""
        cmds.play(state=False)
        
    def select_all_blocks(self, *args):
        """选择所有方块"""
        self.selected_blocks = set(self.blocks.keys())
        self.update_blocks_display()
        self.update_status(f"已选中所有 {len(self.selected_blocks)} 个方块")
        
    def deselect_all_blocks(self, *args):
        """取消选择所有方块"""
        self.selected_blocks.clear()
        self.update_blocks_display()
        self.update_status("已取消选择")
        
    def copy_selected_blocks(self, *args):
        """复制选中的方块"""
        if not self.selected_blocks:
            self.update_status("没有选中的方块")
            return
            
        self.clipboard.clear()
        for frame_num in self.selected_blocks:
            if frame_num in self.blocks:
                self.clipboard[frame_num] = self.blocks[frame_num].copy()
                
        self.update_status(f"已复制 {len(self.clipboard)} 个方块")
        
    def paste_blocks(self, *args):
        """粘贴方块"""
        if not self.clipboard:
            self.update_status("剪贴板为空")
            return
            
        # 获取粘贴的起始位置（当前帧）
        current_frame = cmds.intField(self.current_frame_field, query=True, value=True)
        
        # 计算偏移量
        min_frame = min(self.clipboard.keys())
        offset = current_frame - min_frame
        
        # 粘贴方块
        pasted_count = 0
        for original_frame, block_data in self.clipboard.items():
            new_frame = original_frame + offset
            if new_frame >= self.start_frame and new_frame < self.start_frame + self.frame_count:
                self.blocks[new_frame] = block_data.copy()
                pasted_count += 1
                
        self.update_blocks_display()
        self.update_status(f"已粘贴 {pasted_count} 个方块")
        
    def delete_selected_blocks(self, *args):
        """删除选中的方块"""
        if not self.selected_blocks:
            self.update_status("没有选中的方块")
            return
            
        deleted_count = 0
        for frame_num in list(self.selected_blocks):
            if frame_num in self.blocks:
                del self.blocks[frame_num]
                deleted_count += 1
                
        self.selected_blocks.clear()
        self.update_blocks_display()
        self.update_status(f"已删除 {deleted_count} 个方块")
        
    def clear_all_blocks(self, *args):
        """清空所有方块"""
        self.blocks.clear()
        self.selected_blocks.clear()
        self.dragging_block = None
        self.drag_source_frame = None
        self.update_blocks_display()
        self.update_status("已清空所有方块")
        
    # 界面刷新和事件处理
    def on_start_frame_changed(self, *args):
        """起始帧改变"""
        self.start_frame = cmds.intField(self.start_frame_field, query=True, value=True)
        self.refresh_timeline()
        
    def on_frame_count_changed(self, *args):
        """帧数改变"""
        self.frame_count = cmds.intField(self.frame_count_field, query=True, value=True)
        self.refresh_timeline()
        
    def on_current_frame_changed(self, *args):
        """当前帧改变"""
        current_frame = cmds.intField(self.current_frame_field, query=True, value=True)
        cmds.currentTime(current_frame)
        self.update_status()
        
    def refresh_timeline(self):
        """刷新时间轴"""
        if cmds.layout(self.timeline_layout, exists=True):
            cmds.deleteUI(self.timeline_layout)
            
        self.timeline_layout = cmds.formLayout()
        
        self.create_frames()
        self.update_blocks_display()
        
    # 帮助和关于
    def show_help(self, *args):
        """显示帮助"""
        help_text = """
Maya 时间轴工具增强版使用说明:

基本操作:
- 左键点击空帧: 添加当前类型的方块
- 左键点击方块: 开始拖拽
- 拖拽状态下点击其他帧: 放置方块
- Ctrl+点击: 多选方块
- 右键菜单: 更多操作选项

快捷键:
- Ctrl+A: 全选方块
- Ctrl+C: 复制选中方块
- Ctrl+V: 粘贴方块
- Delete: 删除选中方块

菜单功能:
- 文件菜单: 新建、保存、加载配置
- 编辑菜单: 选择、复制、粘贴、删除操作
- 视图菜单: 视图控制选项

方块类型:
- K: 关键帧 (红色)
- B: 分解帧 (绿色)
- I: 中间帧 (蓝色)
- H: 保持帧 (黄色)
- C: 镜头 (橙色)
- E: 特效 (紫色)
        """
        
        cmds.confirmDialog(title="使用说明",
                         message=help_text,
                         button=["确定"])
                         
    def show_about(self, *args):
        """显示关于"""
        about_text = """
Maya 时间轴工具增强版

版本: 1.0
作者: Maya工具开发者

这是一个功能强大的Maya时间轴辅助工具，
支持方块的创建、编辑、拖拽和管理功能。

适用于动画时序规划、关键帧标记等工作流程。
        """
        
        cmds.confirmDialog(title="关于",
                         message=about_text,
                         button=["确定"])
                         
    def close_window(self, *args):
        """关闭窗口"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
    # 模式设置方法
    def set_select_mode(self, *args):
        self.update_status("选择模式")
        
    def set_add_mode(self, *args):
        self.update_status("添加模式")
        
    def set_delete_mode(self, *args):
        self.update_status("删除模式")
        
    def fit_timeline(self, *args):
        self.update_status("缩放到适合")
        
    def reset_view(self, *args):
        self.update_status("重置视图")

def show_timeline_tool_enhanced():
    """显示增强版时间轴工具"""
    tool = TimelineToolEnhanced()
    tool.create_ui()
    return tool

if __name__ == "__main__":
    show_timeline_tool_enhanced()
