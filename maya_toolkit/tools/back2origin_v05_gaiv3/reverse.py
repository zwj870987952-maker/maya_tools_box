import maya.cmds as cmds

def reverse(args):
    root_control = args['root_control']
    global_control = args['global_control']
    ik_controls = args['ik_controls']
    pv_controls = args['pv_controls']
    other_controls = args['other_controls']
    channels = args['channels']
    start_frame, end_frame = (args['start'], args['end'])
    ik_world_positions = {}
    pv_world_positions = {}
    other_world_positions = {}
    global_values = {}
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        global_values[frame] = {}
        for ch in channels:
            global_values[frame][ch] = cmds.getAttr(f'{global_control}.translate{ch}')
        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik):
                ik_world_positions[frame, i] = cmds.xform(ik, q=True, ws=True, t=True)
        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv):
                pv_world_positions[frame, i] = cmds.xform(pv, q=True, ws=True, t=True)
        for i, other in enumerate(other_controls):
            if cmds.objExists(other):
                other_world_positions[frame, i] = cmds.xform(other, q=True, ws=True, t=True)
    root_attributes = [f'translate{ch}' for ch in channels]
    global_attributes = [f'translate{ch}' for ch in channels]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for ch in channels:
            global_value = global_values[frame][ch]
            cmds.setAttr(f'{root_control}.translate{ch}', global_value)
        cmds.setKeyframe(root_control, at=root_attributes)
        for ch in channels:
            cmds.setAttr(f'{global_control}.translate{ch}', 0)
        cmds.setKeyframe(global_control, at=global_attributes)
    valid_ik_controls = [ik for ik in ik_controls if cmds.objExists(ik)]
    valid_pv_controls = [pv for pv in pv_controls if cmds.objExists(pv)]
    valid_other_controls = [other for other in other_controls if cmds.objExists(other)]
    for frame in range(int(start_frame), int(end_frame) + 1):
        cmds.currentTime(frame)
        for i, ik in enumerate(ik_controls):
            if cmds.objExists(ik) and (frame, i) in ik_world_positions:
                cmds.xform(ik, ws=True, t=ik_world_positions[frame, i])
        if valid_ik_controls:
            cmds.setKeyframe(valid_ik_controls, at=['translateX', 'translateY', 'translateZ'])
        for i, pv in enumerate(pv_controls):
            if cmds.objExists(pv) and (frame, i) in pv_world_positions:
                cmds.xform(pv, ws=True, t=pv_world_positions[frame, i])
        if valid_pv_controls:
            cmds.setKeyframe(valid_pv_controls, at=['translateX', 'translateY', 'translateZ'])
        for i, other in enumerate(other_controls):
            if cmds.objExists(other) and (frame, i) in other_world_positions:
                cmds.xform(other, ws=True, t=other_world_positions[frame, i])
        if valid_other_controls:
            cmds.setKeyframe(valid_other_controls, at=['translateX', 'translateY', 'translateZ'])
    frame_step = args['frame_step']
    all_objects = []
    if global_control:
        all_objects.append(global_control)
    if root_control:
        all_objects.append(root_control)
    all_objects.extend(valid_ik_controls)
    all_objects.extend(valid_pv_controls)
    all_objects.extend(valid_other_controls)
    for frame in range(int(start_frame + 1), int(end_frame)):
        if frame % frame_step != 0:
            cmds.cutKey(all_objects, time=(frame, frame), at='translate')
