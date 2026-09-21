#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya脚本: 重置物体坐标中心轴
功能: 将选中物体的轴心点重置到其几何中心或边界框中心，并可重置轴向
作者: Claude
"""

import maya.cmds as cmds

def reset_pivot_to_center():
    """
    将选中物体的轴心点重置到几何中心
    """
    # 获取当前选中的对象
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 获取物体的边界框信息
        bbox = cmds.exactWorldBoundingBox(obj)
        
        # 计算边界框的中心点
        center_x = (bbox[0] + bbox[3]) / 2.0
        center_y = (bbox[1] + bbox[4]) / 2.0
        center_z = (bbox[2] + bbox[5]) / 2.0
        
        # 暂时保存当前旋转
        rotation = cmds.xform(obj, query=True, rotation=True)
        
        # 设置轴心点到边界框中心
        cmds.xform(obj, centerPivots=True)
        
        # 如果要设置到确切的边界框中心，可以使用下面的代码
        # cmds.xform(obj, worldSpace=True, pivots=[center_x, center_y, center_z])
        
        # 恢复旋转
        cmds.xform(obj, rotation=rotation)
        
        print("已重置 '%s' 的轴心点到中心" % obj)

def reset_pivot_to_origin():
    """
    将选中物体的轴心点重置到原点 (0,0,0)
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 暂时保存当前旋转
        rotation = cmds.xform(obj, query=True, rotation=True)
        
        # 设置轴心点到原点
        cmds.xform(obj, worldSpace=True, pivots=[0, 0, 0])
        
        # 恢复旋转
        cmds.xform(obj, rotation=rotation)
        
        print("已重置 '%s' 的轴心点到原点 (0,0,0)" % obj)

def reset_pivot_to_parent():
    """
    将选中物体的轴心点重置到父物体的轴心点位置
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 获取父物体
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        
        if not parent:
            cmds.warning("物体 '%s' 没有父物体" % obj)
            continue
        
        # 暂时保存当前旋转
        rotation = cmds.xform(obj, query=True, rotation=True)
        
        # 获取父物体的轴心点
        parent_pivot = cmds.xform(parent[0], query=True, worldSpace=True, pivots=True)
        
        # 设置轴心点到父物体的轴心点
        cmds.xform(obj, worldSpace=True, pivots=[parent_pivot[0], parent_pivot[1], parent_pivot[2]])
        
        # 恢复旋转
        cmds.xform(obj, rotation=rotation)
        
        print("已重置 '%s' 的轴心点到父物体 '%s' 的轴心点" % (obj, parent[0]))

def reset_rotation_axes():
    """
    重置选中物体的旋转轴方向为默认方向
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 保存当前物体的变换信息
        pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
        scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
        pivot = cmds.xform(obj, query=True, worldSpace=True, pivots=True)[:3]  # 只取前三个值，对应xyz
        
        # 保存原始父级
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        
        # 如果有父级，暂时解除父子关系
        if parent:
            cmds.parent(obj, world=True)
        
        # 使用makeIdentity重置轴向，不影响物体位置
        cmds.makeIdentity(obj, apply=True, rotate=True)
        
        # 恢复物体位置和缩放
        cmds.xform(obj, worldSpace=True, translation=pos)
        cmds.xform(obj, worldSpace=True, scale=scale)
        cmds.xform(obj, worldSpace=True, pivots=pivot)
        
        # 恢复父子关系
        if parent:
            cmds.parent(obj, parent[0])
        
        print("已重置 '%s' 的旋转轴方向" % obj)

def align_to_world():
    """
    将物体的轴向与世界坐标系对齐
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 保存当前位置、缩放和轴心点
        pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
        scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
        pivot = cmds.xform(obj, query=True, worldSpace=True, pivots=True)[:3]  # 只取前三个值，对应xyz
        
        # 保存原始父级
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        
        # 如果有父级，暂时解除父子关系
        if parent:
            cmds.parent(obj, world=True)
        
        # 将旋转设置为(0,0,0)，与世界坐标系对齐
        cmds.xform(obj, worldSpace=True, rotation=[0, 0, 0])
        
        # 恢复位置、缩放和轴心点
        cmds.xform(obj, worldSpace=True, translation=pos)
        cmds.xform(obj, worldSpace=True, scale=scale)
        cmds.xform(obj, worldSpace=True, pivots=pivot)
        
        # 恢复父子关系
        if parent:
            cmds.parent(obj, parent[0])
        
        print("已将 '%s' 的轴向与世界坐标系对齐" % obj)

def match_to_joint_orient():
    """
    将轴向匹配到Joint Orient
    适用于骨骼和控制器的对齐
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if len(selected_objects) != 2:
        cmds.warning("请选择两个物体，先选源骨骼，后选目标物体")
        return
    
    source_joint = selected_objects[0]
    target_obj = selected_objects[1]
    
    # 检查源物体是否为骨骼
    if not cmds.objectType(source_joint, isType="joint"):
        cmds.warning("源物体不是骨骼，无法获取jointOrient属性")
        return
    
    # 获取源骨骼的jointOrient
    joint_orient = cmds.getAttr(source_joint + ".jointOrient")[0]
    
    # 保存目标物体的当前位置、缩放和轴心点
    pos = cmds.xform(target_obj, query=True, worldSpace=True, translation=True)
    scale = cmds.xform(target_obj, query=True, worldSpace=True, scale=True)
    pivot = cmds.xform(target_obj, query=True, worldSpace=True, pivots=True)[:3]
    
    # 保存原始父级
    parent = cmds.listRelatives(target_obj, parent=True, fullPath=True)
    
    # 如果有父级，暂时解除父子关系
    if parent:
        cmds.parent(target_obj, world=True)
    
    # 应用骨骼的jointOrient作为目标物体的旋转
    cmds.xform(target_obj, worldSpace=True, rotation=joint_orient)
    
    # 恢复位置、缩放和轴心点
    cmds.xform(target_obj, worldSpace=True, translation=pos)
    cmds.xform(target_obj, worldSpace=True, scale=scale)
    cmds.xform(target_obj, worldSpace=True, pivots=pivot)
    
    # 恢复父子关系
    if parent:
        cmds.parent(target_obj, parent[0])
    
    print("已将 '%s' 的轴向匹配到骨骼 '%s' 的方向" % (target_obj, source_joint))

def reset_object_completely():
    """
    完全重置物体：将轴心点重置到几何中心，轴向与世界坐标系对齐
    """
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        # 保存当前位置和缩放
        pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
        scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
        
        # 保存原始父级
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        
        # 如果有父级，暂时解除父子关系
        if parent:
            cmds.parent(obj, world=True)
        
        # 冻结旋转 - 重置旋转轴
        cmds.makeIdentity(obj, apply=True, rotate=True)
        
        # 重置轴心点到中心
        cmds.xform(obj, centerPivots=True)
        
        # 将旋转设置为(0,0,0)，与世界坐标系对齐
        cmds.xform(obj, worldSpace=True, rotation=[0, 0, 0])
        
        # 恢复位置和缩放
        cmds.xform(obj, worldSpace=True, translation=pos)
        cmds.xform(obj, worldSpace=True, scale=scale)
        
        # 恢复父子关系
        if parent:
            cmds.parent(obj, parent[0])
        
        print("已完全重置 '%s' 的轴心点和轴向" % obj)

def create_ui():
    """
    创建用户界面
    """
    window_name = "resetPivotWindow"
    
    # 如果窗口已存在，则删除
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    # 创建窗口
    window = cmds.window(window_name, title="重置坐标中心轴", widthHeight=(250, 320))
    
    cmds.columnLayout(adjustableColumn=True, columnAlign="center")
    cmds.text(label="选择物体后点击以下按钮重置", height=30)
    cmds.separator(height=10)
    
    # 轴心点部分
    cmds.frameLayout(label="轴心点位置", collapsable=False, marginWidth=5, marginHeight=5)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="重置到几何中心", command=lambda x: reset_pivot_to_center(), height=30)
    cmds.button(label="重置到原点 (0,0,0)", command=lambda x: reset_pivot_to_origin(), height=30)
    cmds.button(label="重置到父物体轴心", command=lambda x: reset_pivot_to_parent(), height=30)
    cmds.setParent('..')  # 返回到父布局
    cmds.setParent('..')  # 返回到父布局
    
    # 轴向部分
    cmds.frameLayout(label="轴向方向", collapsable=False, marginWidth=5, marginHeight=5)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="重置旋转轴", command=lambda x: reset_rotation_axes(), height=30)
    cmds.button(label="轴向对齐世界坐标系", command=lambda x: align_to_world(), height=30)
    cmds.button(label="轴向匹配到骨骼方向", command=lambda x: match_to_joint_orient(), height=30, 
              annotation="先选择源骨骼，再选择目标物体")
    cmds.setParent('..')  # 返回到父布局
    cmds.setParent('..')  # 返回到父布局
    
    # 综合操作
    cmds.frameLayout(label="综合操作", collapsable=False, marginWidth=5, marginHeight=5)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="完全重置物体", command=lambda x: reset_object_completely(), height=30, 
              backgroundColor=[0.8, 0.6, 0.6])
    cmds.setParent('..')  # 返回到父布局
    cmds.setParent('..')  # 返回到父布局
    
    cmds.separator(height=10)
    cmds.button(label="关闭", command=lambda x: cmds.deleteUI(window_name), height=25)
    
    cmds.showWindow(window)

# 启动用户界面
if __name__ == "__main__":
    create_ui() 