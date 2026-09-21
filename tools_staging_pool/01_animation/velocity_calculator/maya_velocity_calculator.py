import maya.cmds as cmds
import maya.mel as mel
import math

def get_linear_distance(start_pos, end_pos):
    """计算两点之间的直线距离"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(start_pos, end_pos)))

def get_average_velocity():
    """计算时间轴范围内的平均速度"""
    # 获取选择的对象
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("请先选择要计算速度的物体")
        return
    
    # 获取时间轴范围
    start_time = cmds.playbackOptions(query=True, minTime=True)
    end_time = cmds.playbackOptions(query=True, maxTime=True)
    
    # 获取当前时间单位（帧/秒）
    time_unit = cmds.currentUnit(query=True, time=True)
    
    # 获取起始和结束位置
    start_pos = cmds.xform(selection[0], query=True, worldSpace=True, translation=True)
    cmds.currentTime(start_time)
    end_pos = cmds.xform(selection[0], query=True, worldSpace=True, translation=True)
    cmds.currentTime(end_time)
    
    # 计算距离
    distance = get_linear_distance(start_pos, end_pos)
    
    # 计算时间差（转换为秒）
    if time_unit == "film":  # 24fps
        time_diff = (end_time - start_time) / 24.0
    elif time_unit == "game":  # 15fps
        time_diff = (end_time - start_time) / 15.0
    elif time_unit == "pal":  # 25fps
        time_diff = (end_time - start_time) / 25.0
    elif time_unit == "ntsc":  # 30fps
        time_diff = (end_time - start_time) / 30.0
    else:
        time_diff = end_time - start_time
    
    # 计算平均速度
    velocity = distance / time_diff if time_diff != 0 else 0
    
    # 显示结果
    cmds.inViewMessage(amg=f"平均速度: {velocity:.2f} 单位/秒", pos='midCenter', fade=True)

def get_instant_velocity():
    """计算当前帧的瞬时速度"""
    # 获取选择的对象
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("请先选择要计算速度的物体")
        return
    
    # 获取当前时间
    current_time = cmds.currentTime(query=True)
    
    # 获取当前时间单位
    time_unit = cmds.currentUnit(query=True, time=True)
    
    # 获取当前位置
    current_pos = cmds.xform(selection[0], query=True, worldSpace=True, translation=True)
    
    # 获取上一帧位置
    cmds.currentTime(current_time - 1)
    prev_pos = cmds.xform(selection[0], query=True, worldSpace=True, translation=True)
    cmds.currentTime(current_time)  # 恢复当前时间
    
    # 计算距离
    distance = get_linear_distance(prev_pos, current_pos)
    
    # 计算时间差（转换为秒）
    if time_unit == "film":  # 24fps
        time_diff = 1.0 / 24.0
    elif time_unit == "game":  # 15fps
        time_diff = 1.0 / 15.0
    elif time_unit == "pal":  # 25fps
        time_diff = 1.0 / 25.0
    elif time_unit == "ntsc":  # 30fps
        time_diff = 1.0 / 30.0
    else:
        time_diff = 1.0
    
    # 计算瞬时速度
    velocity = distance / time_diff if time_diff != 0 else 0
    
    # 显示结果
    cmds.inViewMessage(amg=f"瞬时速度: {velocity:.2f} 单位/秒", pos='midCenter', fade=True)

# 创建UI窗口
def create_ui():
    window_name = "velocityCalculator"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title="速度计算器", width=200)
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.button(label="计算平均速度", command=lambda x: get_average_velocity())
    cmds.button(label="计算瞬时速度", command=lambda x: get_instant_velocity())
    
    cmds.showWindow(window)

# 创建UI
create_ui() 