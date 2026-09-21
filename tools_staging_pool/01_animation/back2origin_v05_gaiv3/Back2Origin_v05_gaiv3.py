########添加反向操作功能，添加识别场景中对应关键字对象并填入功能，增加对象空间名称切换功能


import maya.cmds as cmds
import os
import shutil
import webbrowser
import re

# 控制器关键字库 - 用于自动识别场景中的控制器
CONTROLLER_KEYWORDS = {
    "root_control": ["RootX_M"],
    "ik_controls": ["IKLeg_R", "IKLeg_L"],
    "pv_controls": ["PoleLeg_R", "PoleLeg_L"],
    "other_controls": [],
    "global_control": ["Main"]
}

# 自动识别控制器函数
def auto_identify_controllers():
    # 获取场景中所有变换节点
    all_transforms = cmds.ls(type="transform")
    
    # 初始化结果字典
    identified_controllers = {
        "root_control": "",
        "ik_controls": [],
        "pv_controls": [],
        "other_controls": [],
        "global_control": ""
    }
    
    # 初始化命名空间集合
    namespaces = set([""])  # 默认包含根命名空间
    
    # 为每种控制器类型查找匹配项
    for controller_type, keywords in CONTROLLER_KEYWORDS.items():
        if not keywords:  # 跳过空关键字列表
            continue
            
        for keyword in keywords:
            # 创建不区分大小写的正则表达式模式
            # 模式匹配任何命名空间后跟关键字的控制器
            pattern = re.compile(f"(.*:)?({keyword})$", re.IGNORECASE)
            
            # 查找匹配的控制器
            for transform in all_transforms:
                match = pattern.match(transform)
                if match:
                    # 提取命名空间
                    namespace = match.group(1) or ""
                    if namespace.endswith(':'):
                        namespace = namespace[:-1]
                    namespaces.add(namespace)
                    
                    if controller_type in ["root_control", "global_control"]:
                        identified_controllers[controller_type] = transform
                        break  # 找到第一个匹配项后停止
                    else:
                        identified_controllers[controller_type].append(transform)
    
    return identified_controllers, list(namespaces)

# 填充UI控件的函数
def fill_controller_fields():
    identified_controllers, _ = auto_identify_controllers()
    
    # 填充Root Control字段
    if identified_controllers["root_control"]:
        cmds.textFieldButtonGrp('rootControlField', e=True, text=identified_controllers["root_control"])
    
    # 填充IK Controls字段
    if identified_controllers["ik_controls"]:
        cmds.textFieldButtonGrp('ikControlsField', e=True, text=", ".join(identified_controllers["ik_controls"]))
    
    # 填充Pole Vector Controls字段
    if identified_controllers["pv_controls"]:
        cmds.textFieldButtonGrp('pvControlsField', e=True, text=", ".join(identified_controllers["pv_controls"]))
    
    # 填充Other Controls字段
    if identified_controllers["other_controls"]:
        cmds.textFieldButtonGrp('otherControlsField', e=True, text=", ".join(identified_controllers["other_controls"]))
    
    # 填充Global Control字段
    if identified_controllers["global_control"]:
        cmds.textFieldButtonGrp('globalControlField', e=True, text=identified_controllers["global_control"])

# 按命名空间过滤并填充控制器字段
def fill_by_namespace(namespace):
    # 获取场景中所有变换节点
    all_transforms = cmds.ls(type="transform")
    
    # 初始化结果字典
    identified_controllers = {
        "root_control": "",
        "ik_controls": [],
        "pv_controls": [],
        "other_controls": [],
        "global_control": ""
    }
    
    # 命名空间前缀（对于根命名空间是空字符串）
    ns_prefix = f"{namespace}:" if namespace else ""
    
    # 为每种控制器类型查找匹配项
    for controller_type, keywords in CONTROLLER_KEYWORDS.items():
        if not keywords:  # 跳过空关键字列表
            continue
            
        for keyword in keywords:
            # 创建不区分大小写的正则表达式模式
            # 精确匹配指定命名空间的控制器
            pattern = re.compile(f"^{re.escape(ns_prefix)}({keyword})$", re.IGNORECASE)
            
            # 查找匹配的控制器
            for transform in all_transforms:
                if pattern.match(transform):
                    if controller_type in ["root_control", "global_control"]:
                        identified_controllers[controller_type] = transform
                        break  # 找到第一个匹配项后停止
                    else:
                        identified_controllers[controller_type].append(transform)
    
    # 填充UI字段
    if identified_controllers["root_control"]:
        cmds.textFieldButtonGrp('rootControlField', e=True, text=identified_controllers["root_control"])
    
    if identified_controllers["ik_controls"]:
        cmds.textFieldButtonGrp('ikControlsField', e=True, text=", ".join(identified_controllers["ik_controls"]))
    
    if identified_controllers["pv_controls"]:
        cmds.textFieldButtonGrp('pvControlsField', e=True, text=", ".join(identified_controllers["pv_controls"]))
    
    if identified_controllers["other_controls"]:
        cmds.textFieldButtonGrp('otherControlsField', e=True, text=", ".join(identified_controllers["other_controls"]))
    
    if identified_controllers["global_control"]:
        cmds.textFieldButtonGrp('globalControlField', e=True, text=identified_controllers["global_control"])

# 更新Object菜单中的命名空间列表
def refresh_namespaces_menu():
    # 删除现有菜单项
    object_menu = 'objectMenu'
    items = cmds.menu(object_menu, q=True, itemArray=True) or []
    for item in items:
        if item != 'refreshNamespacesItem':  # 保留刷新按钮
            try:
                cmds.deleteUI(item)
            except:
                pass  # 忽略可能的删除错误
    
    # 强制更新场景中的所有对象
    cmds.refresh()
    
    # 获取当前命名空间
    _, namespaces = auto_identify_controllers()
    
    # 添加分隔线
    cmds.menuItem(parent=object_menu, divider=True, dividerLabel='Namespaces')
    
    # 为每个命名空间添加菜单项
    for ns in sorted(namespaces):
        label = "Root Namespace" if ns == "" else ns
        # 使用partial函数确保lambda能正确捕获ns的值
        import functools
        command_func = functools.partial(fill_by_namespace, ns)
        cmds.menuItem(parent=object_menu, label=label, 
                     command=lambda x, func=command_func: func())
                     
    # 如果没有找到命名空间，添加提示
    if len(namespaces) == 1 and "" in namespaces:
        cmds.menuItem(parent=object_menu, label="No matching namespaces found", enable=False)

def save_script_to_maya_default():
    if os.name == 'nt':  # Windows
        username = os.getlogin()
        source_script_path = f'C:\\Users\\{username}\\Documents\\maya\\scripts\\Back2Origin_v05.py'
    else:  # macOS
        username = os.getenv('USER')
        source_script_path = f'/Users/{username}/Documents/Back2Origin_v05.py'

    maya_app_dir = os.getenv('MAYA_APP_DIR')
    if os.name == 'nt':  # Windows
        script_dir = os.path.join(maya_app_dir, 'scripts')
    else:  # macOS
        script_dir = f'/Users/{username}/Library/Preferences/maya/scripts'

    destination_script_path = os.path.join(script_dir, 'Back2Origin_v05.py')

    # Check if source and destination are the same
    if os.path.abspath(source_script_path) != os.path.abspath(destination_script_path):
        shutil.copy(source_script_path, destination_script_path)
        print(f"Script saved to: {destination_script_path}")
    else:
        print("Source and destination paths are the same. No need to copy.")

save_script_to_maya_default()

def show_about():
    cmds.confirmDialog(
        title="About Back2Origin",
        message=("Back2Origin is a tool designed to help game animators convert forward-moving animations "
                 "into root motion for seamless integration into game engines like Unity and Unreal.\n\n"
                 "Key Features:\n"
                 "- Dynamic root motion conversion\n"
                 "- Frame-by-frame recalculation of IK and pole vector controls\n"
                 "- Customizable bake options for game engine compatibility\n"
                 "- Designed for fast and efficient workflows.\n\n"
                 "For questions or suggestions, contact via email: jk529079@gmail.com with the title [Query]."),
        button=['OK']
    )

def show_contact():
    cmds.confirmDialog(title="Contact", message="For inquiries, contact:\nEmail: jk529079@gmail.com", button=['OK'])



def open_gumroad_page(url):
    webbrowser.open(url)

# Function for selecting the root control
def select_root_control():
    selection = cmds.ls(selection=True)
    if len(selection) == 1:
        cmds.textFieldButtonGrp('rootControlField', e=True, text=selection[0])
    else:
        cmds.warning("Please select exactly one root control.")

# Function for selecting IK controls
def select_ik_controls():
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('ikControlsField', e=True, text=", ".join(selection))
    else:
        cmds.warning("Please select one or more IK controls.")

# Function for selecting Pole Vector controls
def select_pv_controls():
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('pvControlsField', e=True, text=", ".join(selection))
    else:
        cmds.warning("Please select one or more Pole Vector controls.")

# Function for selecting Other Controls (e.g., dropped weapons or props)
def select_other_controls():
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('otherControlsField', e=True, text=", ".join(selection))
    else:
        cmds.warning("Please select one or more Other controls.")

# Function for selecting Global Control
def select_global_control():
    selection = cmds.ls(selection=True)
    if len(selection) == 1:
        cmds.textFieldButtonGrp('globalControlField', e=True, text=selection[0])
    else:
        cmds.warning("Please select exactly one global control.")

# Function to clear Root Control field
def clear_root_control():
    cmds.textFieldButtonGrp('rootControlField', e=True, text="")

# Function to clear IK Controls field
def clear_ik_controls():
    cmds.textFieldButtonGrp('ikControlsField', e=True, text="")

# Function to clear Pole Vector Controls field
def clear_pv_controls():
    cmds.textFieldButtonGrp('pvControlsField', e=True, text="")

# Function to clear Other Controls field
def clear_other_controls():
    cmds.textFieldButtonGrp('otherControlsField', e=True, text="")

# Function to clear Global Control field
def clear_global_control():
    cmds.textFieldButtonGrp('globalControlField', e=True, text="")

# Function to clear all fields
def clear_all():
    clear_root_control()
    clear_ik_controls()
    clear_pv_controls()
    clear_other_controls()
    clear_global_control()
    cmds.checkBoxGrp("channelCheckBoxGrp", e=True, value1=False, value2=False)  # Clear checkboxes
    cmds.warning("Selections cleared!")

# Toggle enabling/disabling of Start/End Frame fields based on Bake from Timeslider checkbox
def toggle_start_end_frames():
    bake_from_timeslider = cmds.checkBox('bakeFromTimesliderCheckBox', q=True, value=True)
    cmds.intFieldGrp('startFrameField', e=True, enable=not bake_from_timeslider)
    cmds.intFieldGrp('endFrameField', e=True, enable=not bake_from_timeslider)

# 优化后的Back2Origin烘焙和关键帧功能

# Core Back2Origin conversion logic with optimizations
def run_root_motion_conversion():
    root_control = cmds.textFieldButtonGrp('rootControlField', q=True, text=True)
    ik_controls = cmds.textFieldButtonGrp('ikControlsField', q=True, text=True).split(", ")
    pv_controls = cmds.textFieldButtonGrp('pvControlsField', q=True, text=True).split(", ")
    other_controls = cmds.textFieldButtonGrp('otherControlsField', q=True, text=True).split(", ")
    global_control = cmds.textFieldButtonGrp('globalControlField', q=True, text=True)
    frame_step = cmds.intFieldGrp('frameStepField', q=True, value1=True)

    channels = []
    if cmds.checkBoxGrp("channelCheckBoxGrp", q=True, value1=True):
        channels.append("X")
    if cmds.checkBoxGrp("channelCheckBoxGrp", q=True, value2=True):
        channels.append("Z")

    if not root_control:
        cmds.error("Error: Root control is required.")
        return

    bake_from_timeslider = cmds.checkBox('bakeFromTimesliderCheckBox', q=True, value=True)
    if bake_from_timeslider:  # "On" selected
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
    else:
        start_frame = cmds.intFieldGrp('startFrameField', q=True, value1=True)
        end_frame = cmds.intFieldGrp('endFrameField', q=True, value1=True)
        cmds.playbackOptions(min=start_frame, max=end_frame)

    # 保存当前评估模式并优化
    current_eval_mode = cmds.evaluationManager(query=True, mode=True)[0]
    cmds.evaluationManager(mode="off")
    # 暂停刷新以提高性能
    cmds.refresh(suspend=True)

    try:
        ik_positions, pv_positions = calculate_ik_positions(root_control, ik_controls, pv_controls, start_frame, end_frame)
        other_positions = calculate_other_positions(root_control, other_controls, start_frame, end_frame)
        root_positions = calculate_root_world_positions(root_control, channels, start_frame, end_frame)
        zero_out_root_control(root_control, channels, start_frame, end_frame)
        reapply_ik_positions(ik_controls, pv_controls, ik_positions, pv_positions, root_control, start_frame, end_frame)
        reapply_other_positions(other_controls, other_positions, root_control, start_frame, end_frame)
        reapply_root_world_positions(global_control, root_positions, channels, start_frame, end_frame)
        optimize_keyframes(root_control, global_control, ik_controls, pv_controls, other_controls, frame_step, start_frame, end_frame)
    finally:
        # 恢复刷新和评估模式
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode=current_eval_mode)

# Functions to calculate and reapply positions of IK, PV, and Other controls
def calculate_ik_positions(root_control, ik_controls, pv_controls, start_frame, end_frame):
    ik_positions = {}
    pv_positions = {}

    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)

        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik):
                ik_pos = cmds.xform(ik, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_ik_pos = [(ik_pos[0] - root_pos[0]), (ik_pos[1] - root_pos[1]), (ik_pos[2] - root_pos[2])]
                ik_positions[(frame, i)] = relative_ik_pos

        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv):
                pv_pos = cmds.xform(pv, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_pv_pos = [(pv_pos[0] - root_pos[0]), (pv_pos[1] - root_pos[1]), (pv_pos[2] - root_pos[2])]
                pv_positions[(frame, i)] = relative_pv_pos

    return ik_positions, pv_positions

def calculate_other_positions(root_control, other_controls, start_frame, end_frame):
    other_positions = {}

    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)

        for i, other in enumerate(other_controls):
            if cmds.objExists(other):
                other_pos = cmds.xform(other, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_other_pos = [(other_pos[0] - root_pos[0]), (other_pos[1] - root_pos[1]), (other_pos[2] - root_pos[2])]
                other_positions[(frame, i)] = relative_other_pos

    return other_positions

def calculate_root_world_positions(root_control, channels, start_frame, end_frame):
    root_positions = {}

    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
        root_positions[frame] = {ch: root_pos[{"X": 0, "Z": 2}[ch]] for ch in channels}

    return root_positions

def zero_out_root_control(root_control, channels, start_frame, end_frame):
    # 优化：收集属性列表，一次性设置关键帧
    attributes = [f"translate{ch}" for ch in channels]
    
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for ch in channels:
            cmds.setAttr(f"{root_control}.translate{ch}", 0)
        # 一次性设置所有通道的关键帧
        cmds.setKeyframe(root_control, at=attributes)

def reapply_ik_positions(ik_controls, pv_controls, ik_positions, pv_positions, root_control, start_frame, end_frame):
    # 用于收集有效的IK和PV控制器
    valid_ik_controls = [ik for ik in ik_controls if cmds.objExists(ik)]
    valid_pv_controls = [pv for pv in pv_controls if cmds.objExists(pv)]
    
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)

        # 处理IK控制器
        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik):
                relative_ik_pos = ik_positions[(frame, i)]
                new_ik_pos = [root_pos[0] + relative_ik_pos[0], root_pos[1] + relative_ik_pos[1], root_pos[2] + relative_ik_pos[2]]
                cmds.xform(ik, ws=True, t=new_ik_pos)
        
        # 一次性为所有IK控制器设置关键帧
        if valid_ik_controls:
            cmds.setKeyframe(valid_ik_controls, at=["translateX", "translateY", "translateZ"])

        # 处理PV控制器
        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv):
                relative_pv_pos = pv_positions[(frame, i)]
                new_pv_pos = [root_pos[0] + relative_pv_pos[0], root_pos[1] + relative_pv_pos[1], root_pos[2] + relative_pv_pos[2]]
                cmds.xform(pv, ws=True, t=new_pv_pos)
        
        # 一次性为所有PV控制器设置关键帧
        if valid_pv_controls:
            cmds.setKeyframe(valid_pv_controls, at=["translateX", "translateY", "translateZ"])

def reapply_other_positions(other_controls, other_positions, root_control, start_frame, end_frame):
    # 收集有效的其他控制器
    valid_other_controls = [other for other in other_controls if cmds.objExists(other)]
    
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)

        for i, other in enumerate(other_controls):
            if cmds.objExists(other):
                relative_other_pos = other_positions[(frame, i)]
                new_other_pos = [root_pos[0] + relative_other_pos[0], root_pos[1] + relative_other_pos[1], root_pos[2] + relative_other_pos[2]]
                cmds.xform(other, ws=True, t=new_other_pos)
        
        # 一次性为所有其他控制器设置关键帧
        if valid_other_controls:
            cmds.setKeyframe(valid_other_controls, at=["translateX", "translateY", "translateZ"])

def reapply_root_world_positions(global_control, root_positions, channels, start_frame, end_frame):
    if not global_control:
        return
        
    # 收集所有需要设置关键帧的属性
    attributes = [f"translate{ch}" for ch in channels]
    
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for ch in channels:
            cmds.setAttr(f"{global_control}.translate{ch}", root_positions[frame][ch])
        # 一次性设置所有通道的关键帧
        cmds.setKeyframe(global_control, at=attributes)

def optimize_keyframes(root_control, global_control, ik_controls, pv_controls, other_controls, frame_step, start_frame, end_frame):
    # 收集所有对象和通道，以便批量处理
    objects_to_optimize = [root_control]
    if global_control:
        objects_to_optimize.append(global_control)
    
    for ik in ik_controls:
        if cmds.objExists(ik):
            objects_to_optimize.append(ik)
    for pv in pv_controls:
        if cmds.objExists(pv):
            objects_to_optimize.append(pv)
    for other in other_controls:
        if cmds.objExists(other):
            objects_to_optimize.append(other)
    
    # 根据帧步长删除关键帧
    for frame in range(int(start_frame + 1), int(end_frame)):  # 跳过首尾帧
        if frame % frame_step != 0:
            cmds.cutKey(objects_to_optimize, time=(frame, frame), at='translate')

# Function to return global motion back to root control - optimized
def return_to_root():
    root_control = cmds.textFieldButtonGrp('rootControlField', q=True, text=True)
    global_control = cmds.textFieldButtonGrp('globalControlField', q=True, text=True)
    ik_controls = cmds.textFieldButtonGrp('ikControlsField', q=True, text=True).split(", ")
    pv_controls = cmds.textFieldButtonGrp('pvControlsField', q=True, text=True).split(", ")
    other_controls = cmds.textFieldButtonGrp('otherControlsField', q=True, text=True).split(", ")
    
    channels = []
    if cmds.checkBoxGrp("channelCheckBoxGrp", q=True, value1=True):
        channels.append("X")
    if cmds.checkBoxGrp("channelCheckBoxGrp", q=True, value2=True):
        channels.append("Z")
        
    if not root_control or not global_control:
        cmds.error("Error: Both Root control and Global control are required.")
        return
        
    bake_from_timeslider = cmds.checkBox('bakeFromTimesliderCheckBox', q=True, value=True)
    if bake_from_timeslider:  # "On" selected
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
    else:
        start_frame = cmds.intFieldGrp('startFrameField', q=True, value1=True)
        end_frame = cmds.intFieldGrp('endFrameField', q=True, value1=True)
        cmds.playbackOptions(min=start_frame, max=end_frame)
    
    # 性能优化：暂停UI刷新并设置评估模式
    current_eval_mode = cmds.evaluationManager(query=True, mode=True)[0]
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        # 步骤1：记录所有控制器的初始位置
        ik_world_positions = {}
        pv_world_positions = {}
        other_world_positions = {}
        global_values = {}
        
        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            
            # 记录global control值
            global_values[frame] = {}
            for ch in channels:
                global_values[frame][ch] = cmds.getAttr(f"{global_control}.translate{ch}")
            
            # 记录所有控制器的世界位置
            for i, ik in enumerate(ik_controls):
                if cmds.objExists(ik):
                    ik_world_positions[(frame, i)] = cmds.xform(ik, q=True, ws=True, t=True)
                    
            for i, pv in enumerate(pv_controls):
                if cmds.objExists(pv):
                    pv_world_positions[(frame, i)] = cmds.xform(pv, q=True, ws=True, t=True)
                    
            for i, other in enumerate(other_controls):
                if cmds.objExists(other):
                    other_world_positions[(frame, i)] = cmds.xform(other, q=True, ws=True, t=True)
        
        # 步骤2：将动作从global control转移到root control
        root_attributes = [f"translate{ch}" for ch in channels]
        global_attributes = [f"translate{ch}" for ch in channels]
        
        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            
            # 复制global control的值到root control
            for ch in channels:
                global_value = global_values[frame][ch]
                cmds.setAttr(f"{root_control}.translate{ch}", global_value)
            cmds.setKeyframe(root_control, at=root_attributes)
            
            # 将global control归零
            for ch in channels:
                cmds.setAttr(f"{global_control}.translate{ch}", 0)
            cmds.setKeyframe(global_control, at=global_attributes)
        
        # 步骤3：重新应用世界位置到所有控制器
        # 收集有效控制器
        valid_ik_controls = [ik for ik in ik_controls if cmds.objExists(ik)]
        valid_pv_controls = [pv for pv in pv_controls if cmds.objExists(pv)]
        valid_other_controls = [other for other in other_controls if cmds.objExists(other)]
        
        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            
            # 重新应用IK控制器的世界位置
            for i, ik in enumerate(ik_controls):
                if cmds.objExists(ik) and (frame, i) in ik_world_positions:
                    cmds.xform(ik, ws=True, t=ik_world_positions[(frame, i)])
            
            # 一次性为所有IK控制器设置关键帧
            if valid_ik_controls:
                cmds.setKeyframe(valid_ik_controls, at=["translateX", "translateY", "translateZ"])
                    
            # 重新应用PV控制器的世界位置
            for i, pv in enumerate(pv_controls):
                if cmds.objExists(pv) and (frame, i) in pv_world_positions:
                    cmds.xform(pv, ws=True, t=pv_world_positions[(frame, i)])
            
            # 一次性为所有PV控制器设置关键帧
            if valid_pv_controls:
                cmds.setKeyframe(valid_pv_controls, at=["translateX", "translateY", "translateZ"])
                    
            # 重新应用其他控制器的世界位置
            for i, other in enumerate(other_controls):
                if cmds.objExists(other) and (frame, i) in other_world_positions:
                    cmds.xform(other, ws=True, t=other_world_positions[(frame, i)])
            
            # 一次性为所有其他控制器设置关键帧
            if valid_other_controls:
                cmds.setKeyframe(valid_other_controls, at=["translateX", "translateY", "translateZ"])
        
        # 步骤4：优化关键帧 - 批量处理
        frame_step = cmds.intFieldGrp('frameStepField', q=True, value1=True)
        all_objects = []
        if global_control:
            all_objects.append(global_control)
        if root_control:
            all_objects.append(root_control)
        all_objects.extend(valid_ik_controls)
        all_objects.extend(valid_pv_controls)
        all_objects.extend(valid_other_controls)
        
        # 根据帧步长一次性移除关键帧
        for frame in range(int(start_frame + 1), int(end_frame)):  # 跳过首尾帧
            if frame % frame_step != 0:
                cmds.cutKey(all_objects, time=(frame, frame), at='translate')
    
    finally:
        # 恢复UI刷新和评估模式
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode=current_eval_mode)

# Help descriptions
def show_root_help():
    cmds.confirmDialog(title='Root Control Help', message='Select the main control responsible for root motion.', button=['OK'])

def show_ik_help():
    cmds.confirmDialog(title='IK Controls Help', message='Select one or more IK controls that are part of the rig.', button=['OK'])

def show_pv_help():
    cmds.confirmDialog(title='Pole Vector Controls Help', message='Select the pole vector controls corresponding to the IK handles.', button=['OK'])

def show_other_help():
    cmds.confirmDialog(title='Other Controls Help', message='Select any additional controls like props or other rig elements.\n\n'
    'Reminder: \n'
    'If you wish the other controls to move along with the root control, ensure they are parented to an object or group constrained to the root control after the conversion.', 
    button=['OK'])

def show_global_help():
    cmds.confirmDialog(title='Global Control Help', message='Select the control that manages the global position of the character.', button=['OK'])

# Main UI function with Help menu included
def show_back2origin_ui():
    if cmds.window("back2OriginWindow", exists=True):
        cmds.deleteUI("back2OriginWindow", window=True)

    window = cmds.window("back2OriginWindow", title="Back2Origin - v0.5(Beta)", widthHeight=(500, 600))
    cmds.columnLayout(adjustableColumn=True)

    # Add Menu
    menu_bar = cmds.menuBarLayout()

    # Edit Menu
    cmds.menu(label="Edit")
    cmds.menuItem(label="Clear All", command="clear_all()")
    cmds.menuItem(label="Auto-Identify Controllers", command=lambda x: fill_controller_fields())
    
    # Object Menu
    object_menu = cmds.menu('objectMenu', label="Object", parent=menu_bar)
    cmds.menuItem('refreshNamespacesItem', label="Refresh Scene", command=lambda x: refresh_namespaces_menu())

    # Help Menu
    cmds.menu(label="Help")
    cmds.menuItem(label="About", command="show_about()")
    cmds.menuItem(label="Contact", command="show_contact()")
    cmds.menuItem(label="Gumroad Page", command=lambda _: cmds.launch(web="https://jk529079.gumroad.com/"))

    # Root Control Field
    cmds.separator(height=20, style='none')
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp("rootControlField", label="Root Control     ", buttonLabel="Select", bc=select_root_control)
    cmds.button(label="Clear", command=lambda x: clear_root_control())  # Clear button
    cmds.button(label="?", command=lambda x: show_root_help())  # Help button after clear
    cmds.setParent("..")

    # IK Controls Field
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp("ikControlsField", label="IK Controls     ", buttonLabel="Select", bc=select_ik_controls)
    cmds.button(label="Clear", command=lambda x: clear_ik_controls())  # Clear button
    cmds.button(label="?", command=lambda x: show_ik_help())  # Help button after clear
    cmds.setParent("..")

    # Pole Vector Controls Field
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp("pvControlsField", label="Pole Vector Controls     ", buttonLabel="Select", bc=select_pv_controls)
    cmds.button(label="Clear", command=lambda x: clear_pv_controls())  # Clear button
    cmds.button(label="?", command=lambda x: show_pv_help())  # Help button after clear
    cmds.setParent("..")

    # Other Controls Field
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp("otherControlsField", label="Other Controls     ", buttonLabel="Select", bc=select_other_controls)
    cmds.button(label="Clear", command=lambda x: clear_other_controls())  # Clear button
    cmds.button(label="?", command=lambda x: show_other_help())  # Help button after clear
    cmds.setParent("..")

    # Separator
    cmds.separator(height=20, style='in')

    # Bake Options Section
    cmds.frameLayout(label="Bake Options", collapsable=True, collapse=False)
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp("globalControlField", label="Global Control    ", buttonLabel="Select", bc=select_global_control)
    cmds.button(label="Clear", command=lambda x: clear_global_control())  # Clear button
    cmds.button(label="?", command=lambda x: show_global_help())  # Help button after clear
    cmds.setParent("..")

    # Use formLayout to vertically align "Channel" and "Bake from Timeslider"
    form = cmds.formLayout()

    # Channel Checkboxes
    channel_checkboxes = cmds.checkBoxGrp("channelCheckBoxGrp", numberOfCheckBoxes=2, label="Channel    ", labelArray2=["X", "Z"], valueArray2=[0, 1])

    # Bake from Timeslider Checkbox without label
    bake_from_timeslider_label = cmds.text(label="Bake from Timeslider")
    bake_from_timeslider_checkbox = cmds.checkBox('bakeFromTimesliderCheckBox', label='', value=False, cc=lambda x: toggle_start_end_frames())

    # Properly align the text and checkboxes
    cmds.formLayout(form, edit=True,
        attachForm=[(channel_checkboxes, 'top', 0), (channel_checkboxes, 'left', 10),
                    (bake_from_timeslider_label, 'left', 25), (bake_from_timeslider_checkbox, 'left', 153)],
        attachControl=[(bake_from_timeslider_label, 'top', 10, channel_checkboxes),
                       (bake_from_timeslider_checkbox, 'top', 10, channel_checkboxes)])

    cmds.setParent("..")

    # Start and End Frame Fields
    cmds.intFieldGrp('startFrameField', label='Start Frame', value1=cmds.playbackOptions(q=True, min=True), enable=True)
    cmds.intFieldGrp('endFrameField', label='End Frame', value1=cmds.playbackOptions(q=True, max=True), enable=True)

    # Frame Step Field
    cmds.intFieldGrp('frameStepField', label='Frame Step', value1=1)

    # Convert Button
    cmds.setParent("..")
    cmds.separator(height=20, style='in')
    cmds.button(label="Convert to Root Motion", command=lambda x: run_root_motion_conversion(), height=50, width=350, bgc=[0, 0.5, 0.5])
    
    # Return to Root Button
    cmds.separator(height=10, style='none')
    cmds.button(label="Return Global Motion to Root", command=lambda x: return_to_root(), height=40, width=350, bgc=[0.5, 0, 0.5])

    # Footer
    cmds.separator(height=10, style='none')
    cmds.text(label="Developed by: Jeremy Wang", align="center")
    cmds.text(label="Version 0.5 (Beta)", align="center")

    # 创建UI后自动识别控制器
    fill_controller_fields()
    
    # 初始化命名空间菜单
    refresh_namespaces_menu()
    
    cmds.showWindow(window)

# Run the UI
show_back2origin_ui()
