#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya镜像工具
功能：将选中物体的位置、旋转、缩放镜像到对侧物体
"""

import maya.cmds as cmds
import maya.mel as mel
import re

class MirrorTool:
    def __init__(self):
        self.window_name = "mirrorToolWindow"
        self.window_title = "镜像工具"
        
        # 默认命名规则
        self.left_identifier = "_L"
        self.right_identifier = "_R"
        
        self.create_ui()
        
    def create_ui(self):
        # 如果窗口已存在，则删除
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        # 创建窗口
        cmds.window(self.window_name, title=self.window_title, widthHeight=(350, 280))
        
        # 主布局
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))
        
        # 命名规则设置
        cmds.frameLayout(label="命名规则设置", collapsable=True, marginWidth=5, marginHeight=5)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        # 左右标识符设置
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(80, 80, 80, 80), adjustableColumn=4, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0), (4, 'both', 0)])
        cmds.text(label="左:")
        self.left_identifier_field = cmds.textField(text=self.left_identifier, width=60)
        cmds.text(label="右:")
        self.right_identifier_field = cmds.textField(text=self.right_identifier, width=60)
        cmds.setParent('..')
        
        # 层级选项
        self.include_hierarchy = cmds.checkBox(label="层级", value=False)
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 镜像平面选项
        cmds.frameLayout(label="镜像平面", collapsable=False, marginWidth=5, marginHeight=5)
        cmds.columnLayout(adjustableColumn=True)
        self.mirror_plane = cmds.radioButtonGrp(
            label="平面选择:", 
            labelArray3=["XY", "YZ", "XZ"], 
            numberOfRadioButtons=3,
            select=1,
            columnWidth=[(1, 80), (2, 60), (3, 60), (4, 60)]
        )
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 镜像功能选项
        cmds.frameLayout(label="镜像功能", collapsable=False, marginWidth=5, marginHeight=5)
        cmds.columnLayout(adjustableColumn=True)
        self.mirror_function = cmds.radioButtonGrp(
            label="功能选择:", 
            labelArray3=["控制", "普通", "复制"], 
            numberOfRadioButtons=3,
            select=1,
            columnWidth=[(1, 80), (2, 60), (3, 60), (4, 60)]
        )
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 执行按钮
        cmds.button(label="执行镜像", command=self.execute_mirror, height=40)
        
        # 显示窗口
        cmds.showWindow(self.window_name)
    
    def update_naming_rules(self):
        """从UI获取命名规则设置"""
        self.left_identifier = cmds.textField(self.left_identifier_field, query=True, text=True)
        self.right_identifier = cmds.textField(self.right_identifier_field, query=True, text=True)
    
    def get_opposite_object(self, obj_name):
        """根据命名规则找到对侧物体"""
        # 更新命名规则
        self.update_naming_rules()
        
        # 严格按照填写的标识执行
        # 检查是否包含左侧标识符
        if self.left_identifier in obj_name:
            # 替换左侧标识为右侧标识
            return obj_name.replace(self.left_identifier, self.right_identifier)
        
        # 检查是否包含右侧标识符
        elif self.right_identifier in obj_name:
            # 替换右侧标识为左侧标识
            return obj_name.replace(self.right_identifier, self.left_identifier)
            
        # 如果没有找到匹配的命名规则，返回None
        return None
    
    def get_mirror_plane(self):
        """获取选择的镜像平面"""
        plane_value = cmds.radioButtonGrp(self.mirror_plane, query=True, select=True)
        if plane_value == 1:
            return "XY"
        elif plane_value == 2:
            return "YZ"
        else:
            return "XZ"
    
    def get_mirror_function(self):
        """获取选择的镜像功能"""
        function_value = cmds.radioButtonGrp(self.mirror_function, query=True, select=True)
        if function_value == 1:
            return "orientation"  # 控制 (原方向)
        elif function_value == 2:
            return "behavior"  # 普通 (原行为)
        else:
            return "copy"  # 复制
    
    def get_hierarchy_option(self):
        """获取是否包含层级结构的选项"""
        return cmds.checkBox(self.include_hierarchy, query=True, value=True)
    
    def get_all_children(self, obj):
        """获取物体的所有子物体（递归）"""
        children = cmds.listRelatives(obj, children=True, fullPath=True) or []
        all_children = list(children)
        
        for child in children:
            all_children.extend(self.get_all_children(child))
            
        return all_children
    
    def get_hierarchy_objects(self, root_objects):
        """获取包含层级结构的所有物体"""
        all_objects = list(root_objects)
        
        for obj in root_objects:
            children = self.get_all_children(obj)
            all_objects.extend(children)
            
        return all_objects
    
    def mirror_transform(self, source_obj, target_obj, mirror_plane, mirror_function):
        """执行镜像变换"""
        # 获取源物体的世界空间变换（位置和缩放）
        source_pos = cmds.xform(source_obj, query=True, worldSpace=True, translation=True)
        source_scale = cmds.xform(source_obj, query=True, worldSpace=True, scale=True)
        
        # 根据镜像平面计算镜像后的位置
        mirrored_pos = list(source_pos)  # 创建新列表
        
        # 镜像位置
        if mirror_plane == "XY":
            mirrored_pos[2] = -source_pos[2]  # 镜像Z轴
        elif mirror_plane == "YZ":
            mirrored_pos[0] = -source_pos[0]  # 镜像X轴
        elif mirror_plane == "XZ":
            mirrored_pos[1] = -source_pos[1]  # 镜像Y轴
        
        # 镜像旋转
        if mirror_function == "copy":
            # 复制镜像：位置镜像，旋转直接复制物体自身的旋转值
            # 获取源物体的局部旋转值（物体自身的旋转）
            source_local_rot = cmds.xform(source_obj, query=True, objectSpace=True, rotation=True)
            # 直接应用到目标物体
            try:
                # 先应用位置和缩放（世界空间）
                cmds.xform(target_obj, worldSpace=True, translation=mirrored_pos)
                cmds.xform(target_obj, worldSpace=True, scale=source_scale)
                # 然后应用局部旋转值
                cmds.xform(target_obj, objectSpace=True, rotation=source_local_rot)
                return True
            except Exception as e:
                cmds.warning(f"应用变换到 {target_obj} 时出错: {str(e)}")
                return False
        else:
            # 获取源物体的世界空间旋转值
            source_rot = cmds.xform(source_obj, query=True, worldSpace=True, rotation=True)
            # 创建新列表用于其他镜像模式
            mirrored_rot = list(source_rot)
            
            # 根据镜像功能和平面调整旋转值
            if mirror_function == "behavior":
                # 普通镜像(原行为)：保持物体的运动方向一致
                if mirror_plane == "XY":
                    mirrored_rot[0] = -source_rot[0] + 180
                    mirrored_rot[1] = -source_rot[1]
                    mirrored_rot[2] = source_rot[2] + 180
                elif mirror_plane == "YZ":
                    mirrored_rot[0] = -source_rot[0]
                    mirrored_rot[1] = -source_rot[1] + 180
                    mirrored_rot[2] = source_rot[2] + 180
                elif mirror_plane == "XZ":
                    mirrored_rot[0] = source_rot[0] + 180
                    mirrored_rot[1] = -source_rot[1] + 180
                    mirrored_rot[2] = -source_rot[2]
            elif mirror_function == "orientation":
                # 控制镜像(原方向)：简单地反转旋转值
                if mirror_plane == "XY":
                    mirrored_rot[0] = -source_rot[0]
                    mirrored_rot[1] = -source_rot[1]
                    mirrored_rot[2] = source_rot[2]
                elif mirror_plane == "YZ":
                    mirrored_rot[0] = -source_rot[0]
                    mirrored_rot[1] = source_rot[1]
                    mirrored_rot[2] = -source_rot[2]
                elif mirror_plane == "XZ":
                    mirrored_rot[0] = source_rot[0]
                    mirrored_rot[1] = -source_rot[1]
                    mirrored_rot[2] = -source_rot[2]
            
            # 应用变换到目标物体
            try:
                cmds.xform(target_obj, worldSpace=True, translation=mirrored_pos)
                cmds.xform(target_obj, worldSpace=True, rotation=mirrored_rot)
                cmds.xform(target_obj, worldSpace=True, scale=source_scale)
                return True
            except Exception as e:
                cmds.warning(f"应用变换到 {target_obj} 时出错: {str(e)}")
                return False
    
    def execute_mirror(self, *args):
        """执行镜像操作"""
        # 获取选中物体
        selected = cmds.ls(selection=True, long=True)
        
        if not selected:
            cmds.warning("请先选择一个物体")
            return
        
        # 获取镜像平面和功能
        mirror_plane = self.get_mirror_plane()
        mirror_function = self.get_mirror_function()
        include_hierarchy = self.get_hierarchy_option()
        
        # 如果包含层级结构，获取所有子物体
        if include_hierarchy:
            objects_to_process = self.get_hierarchy_objects(selected)
        else:
            objects_to_process = selected
        
        # 处理每个物体
        mirrored_count = 0
        skipped_count = 0
        
        # 首先处理父物体，然后处理子物体（按层级顺序）
        # 对物体列表按照层级深度排序（路径中的/数量）
        objects_to_process.sort(key=lambda x: x.count('/'))
        
        for obj in objects_to_process:
            # 获取短名称用于查找对侧物体
            short_name = obj.split('|')[-1]
            opposite_short_name = self.get_opposite_object(short_name)
            
            if opposite_short_name and cmds.objExists(opposite_short_name):
                # 获取对侧物体的完整路径
                # 如果有多个同名物体，使用第一个找到的
                all_matches = cmds.ls(opposite_short_name, long=True)
                if all_matches:
                    opposite_obj = all_matches[0]
                    # 执行镜像
                    success = self.mirror_transform(obj, opposite_obj, mirror_plane, mirror_function)
                    if success:
                        mirrored_count += 1
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        
        # 显示结果
        if mirrored_count > 0:
            result_message = f"成功镜像 {mirrored_count} 个物体"
            if skipped_count > 0:
                result_message += f"，跳过 {skipped_count} 个物体"
                
            cmds.inViewMessage(
                amg=result_message,
                pos='midCenter',
                fade=True,
                fadeOutTime=1.0
            )
        else:
            cmds.warning("没有找到任何可镜像的物体")

# 创建工具实例
def show_mirror_tool():
    MirrorTool()

# 当脚本直接运行时显示工具
if __name__ == "__main__":
    show_mirror_tool() 