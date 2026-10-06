from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel

try:
    from spacify_core import SPACIFY_STATE
except:
    SPACIFY_STATE = {"only_keys": False}


start_time = 0
eval_mode = []
source_objects = []
aim_locators = []
up_locators = []
base_system = []
cleanup_list = []
current_time = 0


def get_all_keyframe_times(objects):
    all_keys = set()
    for obj in objects:
        if cmds.objExists(obj):
            keys = cmds.keyframe(obj, q=True) or []
            for k in keys:
                all_keys.add(k)
    return sorted(list(all_keys))


def initialize_performance():
    global start_time, eval_mode
    start_time = cmds.timerX()
    cmds.refresh(suspend=True)
    eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.evaluationManager(mode='off')


def finalize_performance():
    global start_time, eval_mode
    
    try:
        cmds.timerX(startTime=start_time)
    except:
        pass
    
    try:
        cmds.refresh(suspend=False)
    except:
        pass
    
    try:
        if eval_mode:
            cmds.evaluationManager(mode=eval_mode[0])
    except:
        pass


def set_outliner_color(objects, color):
    for obj in objects:
        try:
            cmds.setAttr('{}.useOutlinerColor'.format(obj), True)
            cmds.setAttr('{}.outlinerColor'.format(obj), color[0], color[1], color[2])
        except:
            pass


def set_locator_scale(scale_value):
    objects = cmds.ls(selection=True)
    scale_value = convert_units(scale_value) * convert_units(1)
    
    if not objects:
        return
    
    for obj in objects:
        try:
            cmds.setAttr('{}.localScaleX'.format(obj), scale_value)
            cmds.setAttr('{}.localScaleY'.format(obj), scale_value)
            cmds.setAttr('{}.localScaleZ'.format(obj), scale_value)
        except:
            pass


def convert_units(value):
    unit = cmds.currentUnit(query=True, linear=True)
    
    coefficients = {
        'mm': 0.1,
        'cm': 1,
        'm': 100,
        'km': 100000,
        'in': 2.54,
        'ft': 30.48,
        'yd': 91.44,
        'mi': 160934.4
    }
    
    coeff = coefficients.get(unit, 1)
    return value / coeff


def get_active_camera():
    current_panel = cmds.getPanel(withFocus=True)
    try:
        camera_name = cmds.modelEditor(current_panel, query=True, camera=True)
    except:
        camera_name = 'persp'
    
    return camera_name


def calculate_distance(obj1, obj2):
    pos1 = cmds.xform(obj1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(obj2, query=True, worldSpace=True, translation=True)
    
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    dz = pos1[2] - pos2[2]
    
    distance = (dx**2 + dy**2 + dz**2)**0.5
    return distance


def scale_to_viewport(scale_factor):
    is_orthographic = False
    distance = 50
    scale_factor = convert_units(scale_factor) / convert_units(1) / convert_units(1)
    
    selection = cmds.ls(selection=True, head=1)
    if not selection:
        return
    
    camera_name = get_active_camera()
    camera_scale = 1
    
    try:
        camera_scale = cmds.getAttr('{}.cameraScale'.format(camera_name))
    except:
        pass
    
    try:
        distance = calculate_distance(selection[0], camera_name)
    except:
        pass
    
    try:
        is_orthographic = cmds.getAttr('{}.orthographic'.format(camera_name))
        ortho_width = cmds.getAttr('{}.orthographicWidth'.format(camera_name))
    except:
        ortho_width = 50
    
    if not is_orthographic:
        set_locator_scale((distance / 25) * scale_factor * camera_scale)
    else:
        set_locator_scale((ortho_width / 25) * scale_factor * camera_scale)


def create_object_set(objects, set_name):
    selected = cmds.ls(selection=True)
    result = None
    
    cmds.select(objects, replace=True)
    
    if cmds.objExists(set_name) and cmds.objectType(set_name) == 'objectSet':
        cmds.sets(edit=True, forceElement=set_name)
        result = set_name
    else:
        result = cmds.sets(name=set_name)
    
    if selected:
        cmds.select(selected, replace=True)
    
    return result


def store_selection():
    global source_objects
    source_objects = cmds.ls(selection=True)


def bake_animation(objects_to_bake, key_source_objects=None):
    """
    Bake animation on objects.
    If key_source_objects provided with Only Keys mode:
    - Constraints should already exist with maintain offset
    - We just go to each key time and set a key on the constrained objects
    """
    global source_objects
    only_keys = SPACIFY_STATE.get("only_keys", False)
    current_eval_mode = cmds.evaluationManager(query=True, mode=True)
    
    try:
        if current_eval_mode[0] != 'off':
            cmds.evaluationManager(mode='off')
        
        min_time = cmds.playbackOptions(query=True, animationStartTime=True)
        max_time = cmds.playbackOptions(query=True, animationEndTime=True)
        
        try:
            mel.eval('waitCursor -state on')
            
            if not only_keys:
                cmds.bakeResults(objects_to_bake, simulation=True, sampleBy=1, 
                                time=(min_time, max_time))
            else:
                # Get keyframe times from source objects
                key_source = key_source_objects if key_source_objects else source_objects
                key_times = get_all_keyframe_times(key_source)
                
                if not key_times:
                    key_times = [min_time, max_time]
                
                ct = cmds.currentTime(q=True)
                
                # Go to each key time and set a key on the objects
                # The objects should already be constrained with maintainOffset
                for t in key_times:
                    cmds.currentTime(t, update=True)
                    for obj in objects_to_bake:
                        if cmds.objExists(obj):
                            # Make sure blendParent is on if it exists
                            if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                                try:
                                    cmds.setAttr(obj + '.blendParent1', 1)
                                except:
                                    pass
                            # Set keyframe - this captures the constraint-driven position
                            cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
                
                cmds.currentTime(ct)
        finally:
            try:
                mel.eval('waitCursor -state off')
            except:
                pass
    finally:
        try:
            if current_eval_mode[0] != 'off':
                cmds.evaluationManager(mode=current_eval_mode[0])
        except:
            pass


def lock_rotation_channels():
    objects = cmds.ls(selection=True)
    
    if not objects:
        return
    
    for obj in objects:
        cmds.setAttr('{}.rx'.format(obj), keyable=False, channelBox=False)
        cmds.setAttr('{}.ry'.format(obj), keyable=False, channelBox=False)
        cmds.setAttr('{}.rz'.format(obj), keyable=False, channelBox=False)


def create_locator_pairs():
    global source_objects, aim_locators, up_locators
    
    selection = cmds.ls(selection=True, long=True)
    store_selection()
    
    aim_locators = []
    up_locators = []
    short_names = []
    source_objects = selection
    
    for joint in source_objects:
        if '|' in joint:
            short_name = joint.split('|')[-1]
        else:
            short_name = joint
        short_names.append(short_name)
    
    for i, joint in enumerate(source_objects):
        aim_loc = cmds.spaceLocator(name='{}_Aim'.format(short_names[i]))[0]
        aim_locators.append(aim_loc)
        
        cmds.setAttr('{}.scaleX'.format(aim_loc), keyable=False)
        cmds.setAttr('{}.scaleY'.format(aim_loc), keyable=False)
        cmds.setAttr('{}.scaleZ'.format(aim_loc), keyable=False)
        cmds.setAttr('{}.visibility'.format(aim_loc), keyable=False)
        
        cmds.select(joint, replace=True)
        cmds.select(aim_loc, add=True)
        constraint = cmds.parentConstraint(maintainOffset=False, weight=1)[0]
        cmds.delete(constraint)
        
        cmds.setAttr('{}.overrideEnabled'.format(aim_loc), 1)
        cmds.setAttr('{}.overrideColor'.format(aim_loc), 17)
        
        up_loc = cmds.spaceLocator(name='{}_Up'.format(short_names[i]))[0]
        up_locators.append(up_loc)
        
        cmds.setAttr('{}.scaleX'.format(up_loc), keyable=False)
        cmds.setAttr('{}.scaleY'.format(up_loc), keyable=False)
        cmds.setAttr('{}.scaleZ'.format(up_loc), keyable=False)
        cmds.setAttr('{}.visibility'.format(up_loc), keyable=False)
        
        cmds.select(joint, replace=True)
        cmds.select(up_loc, add=True)
        constraint = cmds.parentConstraint(maintainOffset=False, weight=1)[0]
        cmds.delete(constraint)
        
        cmds.setAttr('{}.overrideEnabled'.format(up_loc), 1)
        cmds.setAttr('{}.overrideColor'.format(up_loc), 20)
    
    set_outliner_color(aim_locators, [1.0, 1.0, 0.0])
    set_outliner_color(up_locators, [1.0, 0.4, 0.4])
    
    cmds.select(aim_locators, replace=True)
    
    set_locator_scale(20)
    cmds.select(aim_locators, replace=True)
    
    return aim_locators + up_locators


def setup_aim_constraints():
    global source_objects, aim_locators, up_locators, current_time
    
    constraints = []
    
    for i in range(len(source_objects)):
        cmds.select(source_objects[i], replace=True)
        cmds.select(aim_locators[i], add=True)
        constraint = cmds.parentConstraint(maintainOffset=True, weight=1)[0]
        constraints.append(constraint)
        
        cmds.select(source_objects[i], replace=True)
        cmds.select(up_locators[i], add=True)
        constraint = cmds.parentConstraint(maintainOffset=True, weight=1)[0]
        constraints.append(constraint)
    
    all_locators = aim_locators + up_locators
    # Bake - goes to each key time and sets key on constrained locators
    bake_animation(all_locators, key_source_objects=source_objects)
    
    if constraints:
        cmds.delete(constraints)
    
    for i in range(len(source_objects)):
        cmds.select(aim_locators[i], replace=True)
        cmds.select(source_objects[i], add=True)
        try:
            cmds.aimConstraint(maintainOffset=True, weight=1,
                             aimVector=(1, 0, 0),
                             upVector=(0, 1, 0),
                             worldUpType='object',
                             worldUpObject=up_locators[i])
        except:
            pass
    
    cmds.select(all_locators, replace=True)
    
    cmds.cutKey(all_locators, clear=True, time=(':', ), 
                attribute=['rx', 'ry', 'rz'])
    cmds.rotate(0, 0, 0, all_locators, absolute=True)
    
    lock_rotation_channels()
    cmds.select(clear=True)
    cmds.select(aim_locators, replace=True)
    
    cmds.currentTime(current_time)
    
    return all_locators


def toggle_locators_selection(*args):
    global aim_locators, up_locators
    
    current_selection = cmds.ls(selection=True, long=True)
    
    if not current_selection:
        return
    
    aim_toggle_list = []
    up_toggle_list = []
    
    for sel in current_selection:
        if sel.endswith('_Aim'):
            base_name = sel.rsplit('_Aim', 1)[0]
            up_loc = base_name + '_Up'
            if cmds.objExists(up_loc):
                up_toggle_list.append(up_loc)
                
        elif sel.endswith('_Up'):
            base_name = sel.rsplit('_Up', 1)[0]
            aim_loc = base_name + '_Aim'
            if cmds.objExists(aim_loc):
                aim_toggle_list.append(aim_loc)
    
    if up_toggle_list:
        cmds.select(up_toggle_list, replace=True)
    elif aim_toggle_list:
        cmds.select(aim_toggle_list, replace=True)


def apply_constraints_and_bake(*args):
    reposition_window_name = 'RepositionAimLocatorsUI'
    
    if cmds.window(reposition_window_name, exists=True):
        cmds.deleteUI(reposition_window_name, window=True)
    
    try:
        initialize_performance()
        setup_aim_constraints()
    except Exception as e:
        cmds.confirmDialog(
            title='Aim Space Error',
            message='An error occurred while applying aim space constraints.\n\nDetails: {}'.format(str(e)),
            button=['OK'],
            defaultButton='OK',
            icon='warning'
        )
    finally:
        finalize_performance()


def show_reposition_window():
    reposition_window_name = 'RepositionAimLocatorsUI'
    
    if cmds.window(reposition_window_name, exists=True):
        cmds.deleteUI(reposition_window_name, window=True)
    
    cmds.refresh()
    
    maya_version = int(cmds.about(version=True))
    
    if maya_version >= 2026:
        window_width = 220
    else:
        window_width = 200
    
    reposition_window = cmds.window(
        reposition_window_name,
        title='Reposition Aim Locators',
        widthHeight=(window_width, 105),
        sizeable=False,
        minimizeButton=False,
        maximizeButton=False,
        backgroundColor=[0.12, 0.12, 0.12],
        retain=False
    )
    
    main_layout = cmds.columnLayout(
        adjustableColumn=True,
        columnAttach=('both', 8),
        rowSpacing=3,
        backgroundColor=[0.15, 0.15, 0.15]
    )
    
    cmds.separator(height=4, style='none')
    
    cmds.text(
        label='Reposition locators, then click GO',
        align='center',
        font='boldLabelFont',
        height=24,
        backgroundColor=[0.15, 0.15, 0.15]
    )
    
    cmds.separator(height=3, style='none')
    
    cmds.button(
        label='Toggle Locators Selection',
        height=30,
        backgroundColor=[0.25, 0.35, 0.45],
        command=toggle_locators_selection
    )
    
    cmds.separator(height=3, style='none')
    
    cmds.button(
        label='G O !',
        height=32,
        backgroundColor=[0.8, 0.3, 0.35],
        command=apply_constraints_and_bake
    )
    
    cmds.setParent('..')
    
    main_layout_height = 4 + 24 + 3 + 30 + 3 + 32 + 4
    cmds.window(reposition_window, edit=True, height=main_layout_height + 30)
    
    cmds.showWindow(reposition_window)


def create_aim_rig(locator_size=1.0):
    global source_objects, aim_locators, up_locators, base_system, cleanup_list, current_time
    
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning('Please select one or more objects to create aim space locators.')
        return
    
    current_selection = cmds.ls(selection=True)
    
    existing_aim = []
    existing_up = []
    
    for sel in current_selection:
        if sel.endswith('_Aim'):
            existing_aim.append(sel)
        elif sel.endswith('_Up'):
            existing_up.append(sel)
    
    if existing_aim or existing_up:
        all_existing_locators = existing_aim + existing_up
        
        source_objects = []
        aim_locators = []
        up_locators = []
        
        for loc in all_existing_locators:
            if loc.endswith('_Aim'):
                base_name = loc.rsplit('_Aim', 1)[0].split('|')[-1]
                aim_locators.append(loc)
                
                up_loc_name = loc.rsplit('_Aim', 1)[0] + '_Up'
                if cmds.objExists(up_loc_name):
                    up_locators.append(up_loc_name)
                
                if cmds.objExists(base_name):
                    source_obj = base_name
                    long_names = cmds.ls(source_obj, long=True)
                    if long_names:
                        source_objects.append(long_names[0])
                        
            elif loc.endswith('_Up'):
                base_name = loc.rsplit('_Up', 1)[0].split('|')[-1]
                up_locators.append(loc)
                
                aim_loc_name = loc.rsplit('_Up', 1)[0] + '_Aim'
                if cmds.objExists(aim_loc_name) and aim_loc_name not in aim_locators:
                    aim_locators.append(aim_loc_name)
                
                if cmds.objExists(base_name):
                    source_obj = base_name
                    long_names = cmds.ls(source_obj, long=True)
                    if long_names and long_names[0] not in source_objects:
                        source_objects.append(long_names[0])
        
        aim_locators = list(set(aim_locators))
        up_locators = list(set(up_locators))
        source_objects = list(set(source_objects))
        
        current_time = cmds.currentTime(query=True)
        
        toggle_locators_selection()
        show_reposition_window()
        return
    
    current_time = cmds.currentTime(query=True)
    
    source_objects = []
    aim_locators = []
    up_locators = []
    base_system = []
    cleanup_list = []
    
    source_objects = cmds.ls(selection=True)
    
    cmds.manipMoveContext('Move', edit=True, mode=0)
    mel.eval('setToolTo moveSuperContext')
    
    all_locators = create_locator_pairs()
    
    selected = cmds.ls(selection=True)
    cmds.select(all_locators, replace=True)
    scale_to_viewport(locator_size)
    
    cmds.select(clear=True)
    cmds.select(selected, replace=True)
    
    aim_locators = all_locators[:len(all_locators)//2]
    up_locators = all_locators[len(all_locators)//2:]
    
    create_object_set(all_locators, 'esn_ctrls_set')
    
    cleanup_list = all_locators
    
    cmds.select(aim_locators, replace=True)
    
    show_reposition_window()


def btl_main():
    create_aim_rig(locator_size=1.0)


if __name__ == '__main__':
    btl_main()