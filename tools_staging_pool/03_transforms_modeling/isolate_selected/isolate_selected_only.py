# -*- coding: utf-8 -*-
"""
Maya工具: 只显示选中的物体(不包括子层级)
功能: 隔离显示当前选中的物体,但不显示其子物体
作者: Maya工具集
版本: 1.0
"""

import maya.cmds as cmds
import maya.mel as mel


def isolate_selected_only():
    """
    只显示当前选中的物体,不显示子层级物体
    """
    # 获取当前选中的物体
    selected = cmds.ls(selection=True, long=True)
    
    if not selected:
        cmds.warning("请先选择要隔离显示的物体!")
        return
    
    # 获取当前激活的视图面板
    current_panel = cmds.getPanel(withFocus=True)
    
    # 如果不是模型面板,尝试获取一个模型面板
    if not cmds.getPanel(typeOf=current_panel) == 'modelPanel':
        model_panels = cmds.getPanel(type='modelPanel')
        if model_panels:
            current_panel = model_panels[0]
        else:
            cmds.warning("找不到可用的视图面板!")
            return
    
    # 收集所有选中物体的子物体
    all_children = []
    for obj in selected:
        children = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
        all_children.extend(children)
    
    # 过滤掉那些也在选中列表中的子物体
    # 只隐藏那些不在选中列表中的子物体
    children_to_hide = []
    if all_children:
        for child in all_children:
            # 如果这个子物体不在选中列表中,才需要隐藏
            if child not in selected:
                children_to_hide.append(child)
    
    # 隐藏需要隐藏的子物体
    if children_to_hide:
        for child in children_to_hide:
            try:
                # 检查物体是否存在且可见性属性可访问
                if cmds.objExists(child):
                    # 设置子物体为不可见
                    cmds.setAttr(child + ".visibility", 0)
            except:
                pass
    
    # 开启隔离选择模式
    isolate_state = cmds.isolateSelect(current_panel, query=True, state=True)
    
    if isolate_state:
        # 如果已经在隔离模式,先关闭
        cmds.isolateSelect(current_panel, state=False)
    
    # 开启隔离选择
    cmds.isolateSelect(current_panel, state=True)
    
    # 添加选中的物体到隔离集合
    for obj in selected:
        cmds.isolateSelect(current_panel, addSelected=True)
    
    cmds.select(selected, replace=True)
    
    print("已隔离显示: {}".format(", ".join([obj.split("|")[-1] for obj in selected])))
    if children_to_hide:
        print("已隐藏 {} 个未选中的子物体".format(len(children_to_hide)))


def restore_visibility():
    """
    恢复所有物体的可见性
    """
    # 获取当前激活的视图面板
    current_panel = cmds.getPanel(withFocus=True)
    
    # 如果不是模型面板,尝试获取一个模型面板
    if not cmds.getPanel(typeOf=current_panel) == 'modelPanel':
        model_panels = cmds.getPanel(type='modelPanel')
        if model_panels:
            current_panel = model_panels[0]
        else:
            return
    
    # 关闭隔离选择
    cmds.isolateSelect(current_panel, state=False)
    
    # 恢复所有物体的可见性
    all_transforms = cmds.ls(type='transform', long=True)
    for obj in all_transforms:
        try:
            if cmds.objExists(obj):
                cmds.setAttr(obj + ".visibility", 1)
        except:
            pass
    
    print("已恢复所有物体的可见性")


def create_isolate_ui():
    """
    创建工具UI界面
    """
    window_name = "isolateSelectedOnlyWindow"
    
    # 如果窗口已存在,删除它
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    # 创建窗口
    window = cmds.window(
        window_name,
        title="隔离显示工具",
        widthHeight=(300, 120),
        sizeable=False
    )
    
    # 创建布局
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 10))
    
    cmds.separator(height=10, style='none')
    
    # 创建按钮
    cmds.button(
        label="只显示选中物体(不含子物体)",
        height=35,
        backgroundColor=(0.4, 0.6, 0.8),
        command=lambda x: isolate_selected_only()
    )
    
    cmds.button(
        label="恢复显示所有物体",
        height=35,
        backgroundColor=(0.6, 0.8, 0.4),
        command=lambda x: restore_visibility()
    )
    
    cmds.separator(height=5, style='none')
    
    # 显示窗口
    cmds.showWindow(window)


# 主执行函数
def main():
    """
    主函数 - 创建UI
    """
    create_isolate_ui()


# 如果直接运行此脚本
if __name__ == "__main__":
    main()
