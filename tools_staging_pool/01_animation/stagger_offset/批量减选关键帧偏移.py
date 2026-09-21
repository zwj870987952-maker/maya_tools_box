import maya.cmds as cmds

def offset_keyframes(selected_object, offset_value):
    # 获取选中物体的所有关键帧
    keyframes = cmds.keyframe(selected_object, q=True, selected=True)

    if keyframes:
        # 对每个关键帧进行时间偏移
        for keyframe in keyframes:
            new_time = keyframe + offset_value
            cmds.keyframe(selected_object, edit=True, time=(keyframe, keyframe), timeChange=new_time)

        print("{} 的关键帧偏移成功：{} 帧".format(selected_object, offset_value))
    else:
        print("{} 没有关键帧".format(selected_object))

def deselect_and_offset_frames(offset_value):
    # 获取当前选择的物体
    selected_objects = cmds.ls(selection=True, dag=True, long=True)

    if not selected_objects:
        cmds.warning("请先选择物体")
        return

    # 循环直到只剩下一个物体被选择
    while len(selected_objects) > 1:
        # 取消选择第一个物体
        first_object = selected_objects[0]
        cmds.select(first_object, deselect=True)

        # 获取剩余选中的物体
        remaining_objects = cmds.ls(selection=True, dag=True, long=True)

        # 如果剩余物体为空，显示警告并返回
        if not remaining_objects:
            cmds.warning("只选择了一个物体，没有剩余物体可选")
            return

        # 选择剩余物体的所有动画帧
        cmds.selectKey(remaining_objects, replace=True)

        # 调用挪动关键帧的脚本
        for remaining_object in remaining_objects:
            offset_keyframes(remaining_object, offset_value)

        # 更新当前选择的物体列表
        selected_objects = cmds.ls(selection=True, dag=True, long=True)

# 创建窗口和按钮
window_name = "selectFramesTool"
if cmds.window(window_name, exists=True):
    cmds.deleteUI(window_name, window=True)

cmds.window(window_name, title="帧批量偏移工具", widthHeight=(250, 80))
cmds.columnLayout(adjustableColumn=True)

# 添加输入框
offset_value_field = cmds.floatField(value=5.0, minValue=-1000.0, maxValue=1000.0, precision=2, step=0.1)
cmds.button(label="偏移", command=lambda x: deselect_and_offset_frames(cmds.floatField(offset_value_field, query=True, value=True)))

cmds.showWindow(window_name)
