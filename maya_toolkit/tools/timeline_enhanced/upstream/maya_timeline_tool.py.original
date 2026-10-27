# -*- coding: utf-8 -*-
"""
Maya Timeline Tool
一个类似Maya时间轴的交互界面工具，支持方块的拖拽功能
"""

import maya.cmds as cmds
import maya.mel as mel

class TimelineTool(object):
    def __init__(self):
        self.window_name = "timelineToolWindow"
        self.frame_count = 100  # 默认100帧
        self.start_frame = 1
        self.blocks = {}  # 存储每帧的方块信息 {frame: block_data}
        self.dragging_block = None
        self.drag_source_frame = None
        
        # 界面尺寸设置
        self.frame_width = 20
        self.frame_height = 30
        self.block_size = 15
        
    def create_ui(self):
        """创建主界面"""
        # 如果窗口已存在，删除它
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        # 创建主窗口
        cmds.window(self.window_name, 
                   title="Timeline Tool",
                   widthHeight=(800, 200),
                   resizeToFitChildren=True)
        
        # 创建主布局
        main_layout = cmds.columnLayout(adjustableColumn=True, 
                                      columnOffset=("both", 10))
        
        # 创建控制面板
        self.create_control_panel()
        
        # 创建时间轴区域
        self.create_timeline_area()
        
        # 显示窗口
        cmds.showWindow(self.window_name)
        
    def create_control_panel(self):
        """创建控制面板"""
        control_frame = cmds.frameLayout(label="控制面板", 
                                       collapsable=True,
                                       marginHeight=5,
                                       marginWidth=5)
        
        cmds.rowLayout(numberOfColumns=6, 
                      columnWidth6=(80, 60, 80, 60, 100, 100),
                      columnAlign=(1, "right"),
                      columnAttach=[(1, "both", 0), (2, "both", 0), 
                                  (3, "both", 0), (4, "both", 0),
                                  (5, "both", 0), (6, "both", 0)])
        
        cmds.text(label="起始帧:")
        self.start_frame_field = cmds.intField(value=self.start_frame, 
                                             minValue=1,
                                             changeCommand=self.on_start_frame_changed)
        
        cmds.text(label="帧数:")
        self.frame_count_field = cmds.intField(value=self.frame_count,
                                             minValue=10,
                                             maxValue=500,
                                             changeCommand=self.on_frame_count_changed)
        
        cmds.button(label="添加方块", 
                   command=self.add_random_block)
        
        cmds.button(label="清空所有方块",
                   command=self.clear_all_blocks)
        
        cmds.setParent('..')  # 返回到control_frame
        cmds.setParent('..')  # 返回到main_layout
        
    def create_timeline_area(self):
        """创建时间轴区域"""
        timeline_frame = cmds.frameLayout(label="时间轴", 
                                        collapsable=False,
                                        marginHeight=5,
                                        marginWidth=5)
        
        # 创建滚动区域
        scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=16,
                                        childResizable=True,
                                        height=120)
        
        # 创建时间轴容器 - 使用formLayout避免列数限制
        self.timeline_layout = cmds.formLayout()
        
        # 创建每一帧的界面
        self.create_frames()
        
        cmds.setParent('..')  # 返回到scroll_layout
        cmds.setParent('..')  # 返回到timeline_frame
        cmds.setParent('..')  # 返回到main_layout
        
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
            
            # 方块区域（用按钮模拟）
            block_button = cmds.button(label="",
                                     width=self.block_size,
                                     height=self.block_size,
                                     backgroundColor=(0.3, 0.3, 0.3),
                                     command=lambda x, f=frame_num: self.on_frame_clicked(f))
            
            self.frame_layouts[frame_num] = frame_layout
            self.frame_buttons[frame_num] = block_button
            
            cmds.setParent('..')  # 返回到timeline_layout
            
            # 使用formLayout设置位置
            left_pos = i * self.frame_width
            cmds.formLayout(self.timeline_layout, edit=True,
                           attachForm=[(frame_layout, 'top', 0),
                                     (frame_layout, 'bottom', 0),
                                     (frame_layout, 'left', left_pos)])
            
    def on_start_frame_changed(self, *args):
        """起始帧改变时的回调"""
        self.start_frame = cmds.intField(self.start_frame_field, query=True, value=True)
        self.refresh_timeline()
        
    def on_frame_count_changed(self, *args):
        """帧数改变时的回调"""
        self.frame_count = cmds.intField(self.frame_count_field, query=True, value=True)
        self.refresh_timeline()
        
    def refresh_timeline(self):
        """刷新时间轴显示"""
        # 删除现有的时间轴
        if cmds.layout(self.timeline_layout, exists=True):
            cmds.deleteUI(self.timeline_layout)
            
        # 重新创建时间轴
        self.timeline_layout = cmds.formLayout()
        
        self.create_frames()
        self.update_blocks_display()
        
    def on_frame_clicked(self, frame_num):
        """帧被点击时的处理"""
        if frame_num in self.blocks:
            # 如果这一帧有方块，开始拖拽
            self.start_drag(frame_num)
        else:
            # 如果这一帧没有方块，且正在拖拽中，则放置方块
            if self.dragging_block is not None:
                self.drop_block(frame_num)
            else:
                # 否则在这一帧添加方块
                self.add_block(frame_num)
    
    def start_drag(self, frame_num):
        """开始拖拽方块"""
        if frame_num in self.blocks:
            self.dragging_block = self.blocks[frame_num]
            self.drag_source_frame = frame_num
            
            # 改变按钮外观表示正在拖拽
            cmds.button(self.frame_buttons[frame_num], 
                       edit=True,
                       backgroundColor=(1.0, 1.0, 0.0),  # 黄色表示拖拽中
                       label="拖拽中")
            
            cmds.warning("开始拖拽帧 %d 的方块，点击其他帧来放置" % frame_num)
    
    def drop_block(self, target_frame):
        """放置方块到目标帧"""
        if self.dragging_block is not None and self.drag_source_frame is not None:
            # 从源帧移除方块
            if self.drag_source_frame in self.blocks:
                del self.blocks[self.drag_source_frame]
                
            # 在目标帧添加方块
            self.blocks[target_frame] = self.dragging_block
            
            # 重置拖拽状态
            self.dragging_block = None
            self.drag_source_frame = None
            
            # 更新显示
            self.update_blocks_display()
            
            cmds.warning("方块已移动到帧 %d" % target_frame)
    
    def add_block(self, frame_num, block_data=None):
        """在指定帧添加方块"""
        if block_data is None:
            block_data = {"color": (0.0, 0.8, 0.0), "label": "Block"}
            
        self.blocks[frame_num] = block_data
        self.update_blocks_display()
        
        cmds.warning("在帧 %d 添加了方块" % frame_num)
    
    def add_random_block(self, *args):
        """随机添加方块"""
        import random
        frame_num = random.randint(self.start_frame, 
                                 self.start_frame + self.frame_count - 1)
        
        colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
                 (1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)]
        
        color = random.choice(colors)
        block_data = {"color": color, "label": "●"}
        
        self.add_block(frame_num, block_data)
    
    def clear_all_blocks(self, *args):
        """清空所有方块"""
        self.blocks.clear()
        self.dragging_block = None
        self.drag_source_frame = None
        self.update_blocks_display()
        cmds.warning("已清空所有方块")
    
    def update_blocks_display(self):
        """更新方块显示"""
        for i in range(self.frame_count):
            frame_num = self.start_frame + i
            
            if frame_num in self.frame_buttons:
                button = self.frame_buttons[frame_num]
                
                if frame_num in self.blocks:
                    # 显示方块
                    block_data = self.blocks[frame_num]
                    color = block_data.get("color", (0.0, 0.8, 0.0))
                    label = block_data.get("label", "●")
                    
                    cmds.button(button, 
                               edit=True,
                               backgroundColor=color,
                               label=label)
                else:
                    # 显示空帧
                    cmds.button(button,
                               edit=True, 
                               backgroundColor=(0.3, 0.3, 0.3),
                               label="")

def show_timeline_tool():
    """显示时间轴工具的主函数"""
    tool = TimelineTool()
    tool.create_ui()
    return tool

# 运行工具
if __name__ == "__main__":
    show_timeline_tool()
