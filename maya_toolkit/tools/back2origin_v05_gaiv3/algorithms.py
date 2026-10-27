import maya.cmds as cmds

def calculate_ik_positions(root_control, ik_controls, pv_controls, start_frame, end_frame):
    ik_positions = {}
    pv_positions = {}
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik):
                ik_pos = cmds.xform(ik, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_ik_pos = [ik_pos[0] - root_pos[0], ik_pos[1] - root_pos[1], ik_pos[2] - root_pos[2]]
                ik_positions[frame, i] = relative_ik_pos
        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv):
                pv_pos = cmds.xform(pv, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_pv_pos = [pv_pos[0] - root_pos[0], pv_pos[1] - root_pos[1], pv_pos[2] - root_pos[2]]
                pv_positions[frame, i] = relative_pv_pos
    return (ik_positions, pv_positions)

def calculate_other_positions(root_control, other_controls, start_frame, end_frame):
    other_positions = {}
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for i, other in enumerate(other_controls):
            if cmds.objExists(other):
                other_pos = cmds.xform(other, q=True, ws=True, t=True)
                root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
                relative_other_pos = [other_pos[0] - root_pos[0], other_pos[1] - root_pos[1], other_pos[2] - root_pos[2]]
                other_positions[frame, i] = relative_other_pos
    return other_positions

def calculate_root_world_positions(root_control, channels, start_frame, end_frame):
    root_positions = {}
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
        root_positions[frame] = {ch: root_pos[{'X': 0, 'Z': 2}[ch]] for ch in channels}
    return root_positions

def zero_out_root_control(root_control, channels, start_frame, end_frame):
    attributes = [f'translate{ch}' for ch in channels]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for ch in channels:
            cmds.setAttr(f'{root_control}.translate{ch}', 0)
        cmds.setKeyframe(root_control, at=attributes)

def reapply_ik_positions(ik_controls, pv_controls, ik_positions, pv_positions, root_control, start_frame, end_frame):
    valid_ik_controls = [ik for ik in ik_controls if cmds.objExists(ik)]
    valid_pv_controls = [pv for pv in pv_controls if cmds.objExists(pv)]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik):
                relative_ik_pos = ik_positions[frame, i]
                new_ik_pos = [root_pos[0] + relative_ik_pos[0], root_pos[1] + relative_ik_pos[1], root_pos[2] + relative_ik_pos[2]]
                cmds.xform(ik, ws=True, t=new_ik_pos)
        if valid_ik_controls:
            cmds.setKeyframe(valid_ik_controls, at=['translateX', 'translateY', 'translateZ'])
        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv):
                relative_pv_pos = pv_positions[frame, i]
                new_pv_pos = [root_pos[0] + relative_pv_pos[0], root_pos[1] + relative_pv_pos[1], root_pos[2] + relative_pv_pos[2]]
                cmds.xform(pv, ws=True, t=new_pv_pos)
        if valid_pv_controls:
            cmds.setKeyframe(valid_pv_controls, at=['translateX', 'translateY', 'translateZ'])

def reapply_other_positions(other_controls, other_positions, root_control, start_frame, end_frame):
    valid_other_controls = [other for other in other_controls if cmds.objExists(other)]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        root_pos = cmds.xform(root_control, q=True, ws=True, t=True)
        for i, other in enumerate(other_controls):
            if cmds.objExists(other):
                relative_other_pos = other_positions[frame, i]
                new_other_pos = [root_pos[0] + relative_other_pos[0], root_pos[1] + relative_other_pos[1], root_pos[2] + relative_other_pos[2]]
                cmds.xform(other, ws=True, t=new_other_pos)
        if valid_other_controls:
            cmds.setKeyframe(valid_other_controls, at=['translateX', 'translateY', 'translateZ'])

def reapply_root_world_positions(global_control, root_positions, channels, start_frame, end_frame):
    if not global_control:
        return
    attributes = [f'translate{ch}' for ch in channels]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for ch in channels:
            cmds.setAttr(f'{global_control}.translate{ch}', root_positions[frame][ch])
        cmds.setKeyframe(global_control, at=attributes)

def optimize_keyframes(root_control, global_control, ik_controls, pv_controls, other_controls, frame_step, start_frame, end_frame):
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
    for frame in range(int(start_frame + 1), int(end_frame)):
        if frame % frame_step != 0:
            cmds.cutKey(objects_to_optimize, time=(frame, frame), at='translate')
