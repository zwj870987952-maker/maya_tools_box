####优化UI，优化操作逻辑，优化效率
##添加识别通道，识别父子关系进行工作

import maya.cmds as cmds
import os
import json
import tempfile
import time

# =====================
# 默认参数，现在会通过UI进行调整
DEFAULT_MAX_ATTEMPTS = 10      # int, 最大判定尝试次数
DEFAULT_FULL_CHECK_ATTEMPTS = 5  # int, 前N次判定位移和旋转，后续只判定位移
TEMP_FILE_NAME = "maya_world_transform_data.json"  # 临时文件名
# =====================

world_transform_data = {}

def get_temp_file_path():
    """获取临时文件路径"""
    temp_dir = tempfile.gettempdir()  # 获取系统临时文件夹
    return os.path.join(temp_dir, TEMP_FILE_NAME)

def copy_world_transform():
    global world_transform_data
    world_transform_data = {}
    selected = cmds.ls(selection=True, long=True)
    if not selected:
        cmds.warning("请先选择至少一个对象")
        return
        
    # 复制所选对象的世界坐标
    for obj in selected:
        short_name = cmds.ls(obj, shortNames=True)[0]
        pos = cmds.xform(obj, q=True, ws=True, t=True)
        rot = cmds.xform(obj, q=True, ws=True, ro=True)
        world_transform_data[obj] = {'pos': pos, 'rot': rot, 'short_name': short_name}
    
    # 保存到临时文件
    temp_file = get_temp_file_path()
    try:
        with open(temp_file, 'w') as f:
            json.dump(world_transform_data, f)
        print(f"已复制 {len(selected)} 个对象的世界坐标，并保存到: {temp_file}")
    except Exception as e:
        cmds.warning(f"保存到临时文件失败: {e}")

def is_close(a, b, tol=0.01):  # 位置判断
    return all(abs(x - y) < tol for x, y in zip(a, b))

def angle_close(a, b, tol=0.01):  # 旋转判断，自动归一化
    def norm_angle(x):
        x = x % 360
        if x > 180:
            x -= 360
        return x
    return all(abs(norm_angle(x) - norm_angle(y)) < tol for x, y in zip(a, b))

def get_object_keyframes(obj):
    """获取对象的所有关键帧"""
    keyframes = set()
    
    # 获取对象的动画曲线
    animCurves = cmds.listConnections(obj, type="animCurve", s=True, d=False) or []
    
    # 从每条曲线获取关键帧
    for curve in animCurves:
        times = cmds.keyframe(curve, q=True, timeChange=True) or []
        keyframes.update(times)
    
    return sorted(list(keyframes))

def get_hierarchy_level(obj_path):
    """获取对象在层级中的深度（用于排序）"""
    # 计算路径中'|'的数量，表示层级深度
    return obj_path.count('|')

def sort_objects_by_hierarchy(objects_dict):
    """按层级排序对象（父对象优先）"""
    # 创建(对象路径, 数据)元组列表
    items = list(objects_dict.items())
    # 按层级深度排序（层级浅的优先）
    sorted_items = sorted(items, key=lambda x: get_hierarchy_level(x[0]))
    # 返回排序后的字典
    return dict(sorted_items)

def get_selected_channels():
    """获取用户选中的通道类型"""
    # 初始化结果
    paste_position = False
    paste_rotation = False
    
    # 获取所有选中的通道
    selected_channels = cmds.channelBox("mainChannelBox", q=True, selectedMainAttributes=True) or []
    
    # 检查是否选中了位移或旋转通道
    has_other_channels = False
    for channel in selected_channels:
        if channel.startswith("translate"):
            paste_position = True
        elif channel.startswith("rotate"):
            paste_rotation = True
        else:
            has_other_channels = True
    
    # 如果没有选择任何通道，或者只选了其他类型的通道但没有选位移和旋转，则默认位移和旋转都处理
    if not selected_channels or (not paste_position and not paste_rotation and has_other_channels):
        paste_position = True
        paste_rotation = True
    
    return paste_position, paste_rotation

def paste_world_transform():
    global world_transform_data
    
    # 从UI获取参数
    max_attempts = int(cmds.intSliderGrp("maxAttemptsSlider", q=True, value=True))
    full_check_attempts = int(cmds.intSliderGrp("fullCheckAttemptsSlider", q=True, value=True))
    only_keyframes = cmds.checkBox("keyframesOnlyCheckBox", q=True, value=True)
    
    # 获取选中的通道类型
    paste_position, paste_rotation = get_selected_channels()
    
    # 显示将要粘贴的通道类型
    paste_types = []
    if paste_position:
        paste_types.append("位移")
    if paste_rotation:
        paste_types.append("旋转")
    print(f"将粘贴以下属性: {', '.join(paste_types)}")
    
    # 尝试从临时文件加载数据
    temp_file = get_temp_file_path()
    if os.path.exists(temp_file):
        try:
            with open(temp_file, 'r') as f:
                world_transform_data = json.load(f)
        except Exception as e:
            cmds.warning(f"从临时文件加载数据失败: {e}")
    
    if not world_transform_data:
        cmds.warning("没有可用的世界坐标数据，请先复制")
        return
    
    # 获取当前选择的对象
    selected = cmds.ls(selection=True, long=True)
    
    # 确定要处理的对象
    objects_to_process = {}
    if selected:
        # 如果有选择对象，只处理选择的且在复制数据中的对象
        for obj in selected:
            if obj in world_transform_data:
                objects_to_process[obj] = world_transform_data[obj]
    else:
        # 如果没有选择对象，处理所有复制的对象
        for obj, data in world_transform_data.items():
            if cmds.objExists(obj):
                objects_to_process[obj] = data
    
    if not objects_to_process:
        cmds.warning("没有找到可处理的对象")
        return
    
    # 按层级排序对象（父对象优先）
    objects_to_process = sort_objects_by_hierarchy(objects_to_process)
    
    # 如果只处理关键帧，获取所有对象的关键帧
    all_keyframes = {}
    if only_keyframes:
        for obj in objects_to_process:
            obj_keyframes = get_object_keyframes(obj)
            if obj_keyframes:
                all_keyframes[obj] = obj_keyframes
        
        if not any(all_keyframes.values()):
            cmds.warning("没有找到任何关键帧，将处理所有帧")
            only_keyframes = False
    
    # 获取时间轴选择范围 - 改进版
    current_time = cmds.currentTime(q=True)
    frames_to_process = []
    
    try:
        # 尝试获取时间滑块选择范围
        time_slider_range = cmds.timeControl('timeControl1', q=True, rangeArray=True)
        
        # 更严谨的多帧判断：只要开始和结束不同，就视为多帧
        if time_slider_range and len(time_slider_range) >= 2 and time_slider_range[1] - time_slider_range[0] >= 1:
            start_frame = int(time_slider_range[0])
            end_frame = int(time_slider_range[1])
            # 修正：不包含结束帧，与Maya时间滑块选择行为一致
            frames_to_process = range(start_frame, end_frame)
            print(f"处理时间范围: {start_frame} - {end_frame-1} (共{end_frame-start_frame}帧)")
        else:
            frames_to_process = [current_time]
            print(f"处理当前帧: {current_time}")
    except Exception as e:
        # 如果获取时间范围失败，回退到使用播放选项
        try:
            start_frame = int(cmds.playbackOptions(q=True, min=True))
            end_frame = int(cmds.playbackOptions(q=True, max=True))
            
            # 检查是否有高亮选择的范围
            highlight_range = cmds.timeControl('timeControl1', q=True, rangeVisible=True)
            
            if highlight_range:
                # 修正：不包含结束帧
                frames_to_process = range(start_frame, end_frame)
                print(f"处理播放范围: {start_frame} - {end_frame-1} (共{end_frame-start_frame}帧)")
            else:
                frames_to_process = [current_time]
                print(f"处理当前帧: {current_time}")
        except Exception as e2:
            # 如果还是失败，只处理当前帧
            frames_to_process = [current_time]
            cmds.warning(f"获取时间范围失败，只处理当前帧: {current_time}")
            print(f"错误信息: {e}, {e2}")
    
    # 如果只处理关键帧，过滤帧列表
    if only_keyframes and frames_to_process != [current_time]:
        filtered_frames = set()
        for obj, keyframes in all_keyframes.items():
            for kf in keyframes:
                if kf in frames_to_process:
                    filtered_frames.add(kf)
        
        if filtered_frames:
            frames_to_process = sorted(list(filtered_frames))
            print(f"只处理关键帧: 找到 {len(frames_to_process)} 个关键帧")
        else:
            cmds.warning("在选定范围内没有找到关键帧，将处理当前帧")
            frames_to_process = [current_time]
    
    # 记录开始时间
    start_time = time.time()
    
    # 创建进度窗口
    total_frames = len(frames_to_process)
    if total_frames > 1:
        progress_window = cmds.progressWindow(title="处理世界坐标",
                           progress=0,
                           status=f"准备处理 {total_frames} 帧...",
                           isInterruptable=True,
                           maxValue=100)
    
    try:
        # 处理每一帧
        for frame_index, frame in enumerate(frames_to_process):
            # 检查是否取消
            if total_frames > 1 and cmds.progressWindow(query=True, isCancelled=True):
                break
            
            # 更新进度 - 简化计算方式
            if total_frames > 1:
                # 直接计算百分比
                percent_complete = int((frame_index + 1) * 100 / total_frames)
                cmds.progressWindow(edit=True, 
                                   progress=percent_complete, 
                                   status=f"处理帧 {frame} ({frame_index+1}/{total_frames}) - {percent_complete}%")
            
            # 设置当前帧
            cmds.currentTime(frame)
            
            # 处理当前帧
            failed_objs = []
            last_attempt_failed = True
            
            for attempt in range(max_attempts):
                failed_objs = []
                
                # 粘贴所有对象的坐标 - 已按层级排序，父对象优先
                for obj, data in objects_to_process.items():
                    if not cmds.objExists(obj):
                        continue
                    
                    # 根据选择的通道类型粘贴坐标
                    if paste_position:
                        cmds.xform(obj, ws=True, t=data['pos'])
                    if paste_rotation:
                        cmds.xform(obj, ws=True, ro=data['rot'])
                    
                    # 检查粘贴结果
                    failed = False
                    
                    # 只检查我们实际粘贴的属性
                    if paste_position:
                        cur_pos = cmds.xform(obj, q=True, ws=True, t=True)
                        if not is_close(cur_pos, data['pos']):
                            failed = True
                    
                    if paste_rotation and attempt < full_check_attempts:
                        cur_rot = cmds.xform(obj, q=True, ws=True, ro=True)
                        if not angle_close(cur_rot, data['rot']):
                            failed = True
                    
                    if failed:
                        # 获取当前位置和旋转用于错误报告
                        cur_pos = cmds.xform(obj, q=True, ws=True, t=True) if paste_position else None
                        cur_rot = cmds.xform(obj, q=True, ws=True, ro=True) if paste_rotation else None
                        failed_objs.append((obj, data, cur_pos, cur_rot))
                
                # 如果所有对象都成功，或者已经是最后一次尝试
                if not failed_objs or attempt == max_attempts - 1:
                    # 在当前帧添加关键帧，只为实际粘贴的属性添加关键帧
                    for obj in objects_to_process:
                        if cmds.objExists(obj):
                            try:
                                attributes = []
                                if paste_position:
                                    attributes.extend(['translateX', 'translateY', 'translateZ'])
                                if paste_rotation:
                                    attributes.extend(['rotateX', 'rotateY', 'rotateZ'])
                                
                                if attributes:
                                    cmds.setKeyframe(obj, attribute=attributes)
                            except Exception as e:
                                cmds.warning(f"为对象 {obj} 设置关键帧失败: {e}")
                    
                    last_attempt_failed = len(failed_objs) > 0
                    break
            
            # 只在最后一次尝试后打印未成功对象
            if last_attempt_failed and failed_objs:
                print(f"帧 {frame}: 以下对象在多次尝试后仍未完全还原，但已设置关键帧：")
                for obj, data, cur_pos, cur_rot in failed_objs:
                    short_name = data.get('short_name') or cmds.ls(obj, shortNames=True)[0]
                    print(f"  - {short_name}")
                    
                    if paste_position and cur_pos:
                        print(f"    目标位置: {['%.3f'%v for v in data['pos']]}")
                        print(f"    当前位置: {['%.3f'%v for v in cur_pos]}")
                    
                    if paste_rotation and cur_rot:
                        print(f"    目标旋转: {['%.3f'%v for v in data['rot']]}")
                        print(f"    当前旋转: {['%.3f'%v for v in cur_rot]}")
                
                cmds.warning(f"帧 {frame}: 有对象未能完全还原，但已应用最接近的结果。")
    finally:
        # 关闭进度窗口
        if total_frames > 1:
            cmds.progressWindow(endProgress=True)
    
    # 完成后返回到原始帧
    cmds.currentTime(current_time)
    
    # 计算总耗时
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"已完成 {len(frames_to_process)} 帧的坐标还原和关键帧设置，耗时: {elapsed_time:.2f} 秒")

    # 更新状态标签
    paste_info = "位移" if paste_position else ""
    paste_info += "和旋转" if paste_rotation and paste_info else "旋转" if paste_rotation else ""
    cmds.text("statusLabel", e=True, label=f"已完成{paste_info}粘贴，处理{len(frames_to_process)}帧，耗时: {elapsed_time:.2f}秒")

def show_world_transform_ui():
    """创建美观的用户界面"""
    # 检查窗口是否已存在
    if cmds.window("worldTransformWin", exists=True):
        cmds.deleteUI("worldTransformWin")
    
    # 创建主窗口 - 使用固定背景色
    window = cmds.window("worldTransformWin", title="世界坐标复制/还原工具", widthHeight=(400, 320), bgc=(0.2, 0.2, 0.22))
    
    # 主布局
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))
    
    # 标题区域
    cmds.text("titleLabel", label="世界坐标复制/还原工具", font="boldLabelFont", height=30, align="center")
    cmds.separator(height=10, style="double")
    
    # 参数设置区域
    cmds.frameLayout(label="参数设置", collapsable=True, collapse=False, marginWidth=5, marginHeight=5)
    params_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
    
    # 最大尝试次数 - 使用滑动条
    cmds.intSliderGrp("maxAttemptsSlider", 
                     label="最大尝试次数:", 
                     field=True,
                     minValue=1, 
                     maxValue=20, 
                     value=DEFAULT_MAX_ATTEMPTS,
                     fieldMinValue=1,
                     fieldMaxValue=50)
    
    # 完整检查尝试次数 - 使用滑动条
    cmds.intSliderGrp("fullCheckAttemptsSlider", 
                     label="完整检查尝试次数:", 
                     field=True,
                     minValue=1, 
                     maxValue=10, 
                     value=DEFAULT_FULL_CHECK_ATTEMPTS,
                     fieldMinValue=1,
                     fieldMaxValue=20)
    
    # 只处理关键帧复选框
    cmds.checkBox("keyframesOnlyCheckBox", label="只处理关键帧", value=False)
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    # 操作按钮区域
    cmds.frameLayout(label="操作", collapsable=False, marginWidth=5, marginHeight=5)
    buttons_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    
    # 使用图标按钮
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190), adjustableColumn=1)
    cmds.button("copyBtn", label="复制世界坐标", height=50, 
               command=lambda x: copy_world_transform(),
               bgc=(0.3, 0.3, 0.35))
    cmds.button("pasteBtn", label="粘贴世界坐标", height=50, 
               command=lambda x: paste_world_transform(),
               bgc=(0.3, 0.3, 0.35))
    cmds.setParent('..')
    
    # 添加通道选择提示
    cmds.text(label="提示: 在通道栏中选择特定通道可以只粘贴对应属性", align="center", height=30)
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    # 状态区域
    cmds.separator(height=10)
    cmds.text("statusLabel", label="就绪", align="center")
    
    # 显示窗口
    cmds.showWindow("worldTransformWin")

# 启动UI
show_world_transform_ui() 