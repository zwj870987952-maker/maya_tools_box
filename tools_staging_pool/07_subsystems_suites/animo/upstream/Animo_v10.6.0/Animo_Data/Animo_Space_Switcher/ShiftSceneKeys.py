from maya import cmds

OPTION_VAR_NAME = 'shiftKeysToolOffset'

def save_offset_value(*args):
    if cmds.intFieldGrp('offsetField', exists=True):
        offset_value = cmds.intFieldGrp('offsetField', query=True, value1=True)
        cmds.optionVar(intValue=(OPTION_VAR_NAME, offset_value))

def save_offset_value_from_control(control_name, *args):
    if cmds.intFieldGrp(control_name, exists=True):
        offset_value = cmds.intFieldGrp(control_name, query=True, value1=True)
        cmds.optionVar(intValue=(OPTION_VAR_NAME, offset_value))

def load_offset_value():
    if cmds.optionVar(exists=OPTION_VAR_NAME):
        return cmds.optionVar(query=OPTION_VAR_NAME)
    return 1000

def get_locked_attributes(obj):
    locked_attrs = {}
    
    obj_type = cmds.objectType(obj)
    shape_type = None
    
    if obj_type == 'transform':
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if shapes:
            shape_type = cmds.objectType(shapes[0])
    
    is_camera = (obj_type == 'camera' or shape_type == 'camera')
    if not is_camera:
        return locked_attrs
    
    attrs = cmds.listAttr(obj, keyable=True, unlocked=False) or []
    
    for attr in attrs:
        full_attr = "{0}.{1}".format(obj, attr)
        if cmds.getAttr(full_attr, lock=True):
            connections = cmds.listConnections(full_attr, source=True, destination=False, type='animCurve')
            if connections:
                locked_attrs[attr] = True
    
    return locked_attrs

def unlock_attributes(obj, attrs):
    for attr in attrs:
        try:
            cmds.setAttr("{0}.{1}".format(obj, attr), lock=False)
        except:
            pass

def lock_attributes(obj, attrs):
    for attr in attrs:
        try:
            cmds.setAttr("{0}.{1}".format(obj, attr), lock=True)
        except:
            pass

def shift_animation_keys(time_change, mode='all'):
    cmds.waitCursor(state=True)
    
    shifted_count = 0
    skipped_count = 0
    unlocked_layers = []
    unlocked_objects = {}
    
    try:
        if mode == 'selected':
            selection = cmds.ls(selection=True)
            if not selection:
                cmds.warning("Nothing selected. Please select objects with animation.")
                return
            
            for obj in selection:
                locked_attrs = get_locked_attributes(obj)
                
                if locked_attrs:
                    unlock_attributes(obj, list(locked_attrs.keys()))
                    unlocked_objects[obj] = list(locked_attrs.keys())
                
                try:
                    cmds.keyframe(obj, edit=True, relative=True, timeChange=time_change)
                    shifted_count += 1
                except RuntimeError as e:
                    if "Cannot move keys" in str(e):
                        skipped_count += 1
                    else:
                        raise
                
                if obj in unlocked_objects:
                    lock_attributes(obj, unlocked_objects[obj])
            
            try:
                min_time = cmds.playbackOptions(q=True, minTime=True)
                cmds.currentTime(min_time + time_change)
            except:
                pass
                        
        elif mode == 'animlayers':
            curves_to_shift = set()
            anim_layers = cmds.ls(type='animLayer')
            
            if anim_layers:
                for layer in anim_layers:
                    try:
                        if cmds.animLayer(layer, query=True, lock=True):
                            cmds.animLayer(layer, edit=True, lock=False)
                            unlocked_layers.append(layer)
                    except:
                        pass
                
                for layer in anim_layers:
                    blend_nodes = cmds.animLayer(layer, query=True, blendNodes=True) or []
                    for blend_node in blend_nodes:
                        if cmds.objExists(blend_node):
                            connections = cmds.listConnections(blend_node, source=True, destination=False) or []
                            for curve in connections:
                                if curve and cmds.objExists(curve) and cmds.nodeType(curve).startswith('animCurve'):
                                    try:
                                        if not cmds.referenceQuery(curve, isNodeReferenced=True):
                                            curves_to_shift.add(curve)
                                    except:
                                        curves_to_shift.add(curve)
            
            for curve in curves_to_shift:
                try:
                    cmds.keyframe(curve, edit=True, relative=True, timeChange=time_change)
                    shifted_count += 1
                except RuntimeError as e:
                    if "Cannot move keys" in str(e):
                        skipped_count += 1
            
            try:
                min_time = cmds.playbackOptions(q=True, minTime=True)
                cmds.currentTime(min_time + time_change)
            except:
                pass
                        
        else:
            curves_to_shift = set()
            
            anim_curves = cmds.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU',
                                       'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU'])
            
            all_animated_objects = set()
            for curve in anim_curves:
                connections = cmds.listConnections(curve, destination=True, source=False, plugs=True) or []
                for conn in connections:
                    if '.' in conn:
                        obj = conn.split('.')[0]
                        if cmds.objExists(obj):
                            all_animated_objects.add(obj)
            
            for obj in all_animated_objects:
                try:
                    if cmds.referenceQuery(obj, isNodeReferenced=True):
                        continue
                except:
                    pass
                
                locked_attrs = get_locked_attributes(obj)
                if locked_attrs:
                    unlock_attributes(obj, list(locked_attrs.keys()))
                    unlocked_objects[obj] = list(locked_attrs.keys())
            
            for curve in anim_curves:
                try:
                    if not cmds.referenceQuery(curve, isNodeReferenced=True):
                        curves_to_shift.add(curve)
                    else:
                        skipped_count += 1
                except:
                    curves_to_shift.add(curve)
            
            anim_layers = cmds.ls(type='animLayer')
            if anim_layers:
                for layer in anim_layers:
                    try:
                        if cmds.animLayer(layer, query=True, lock=True):
                            cmds.animLayer(layer, edit=True, lock=False)
                            unlocked_layers.append(layer)
                    except:
                        pass
                
                for layer in anim_layers:
                    blend_nodes = cmds.animLayer(layer, query=True, blendNodes=True) or []
                    for blend_node in blend_nodes:
                        if cmds.objExists(blend_node):
                            connections = cmds.listConnections(blend_node, source=True, destination=False) or []
                            for curve in connections:
                                if curve and cmds.objExists(curve) and cmds.nodeType(curve).startswith('animCurve'):
                                    try:
                                        if not cmds.referenceQuery(curve, isNodeReferenced=True):
                                            curves_to_shift.add(curve)
                                    except:
                                        curves_to_shift.add(curve)
            
            for curve in curves_to_shift:
                try:
                    cmds.keyframe(curve, edit=True, relative=True, timeChange=time_change)
                    shifted_count += 1
                except RuntimeError as e:
                    if "Cannot move keys" in str(e):
                        skipped_count += 1
            
            for obj, attrs in unlocked_objects.items():
                lock_attributes(obj, attrs)
            
            try:
                min_time = cmds.playbackOptions(q=True, minTime=True)
                max_time = cmds.playbackOptions(q=True, maxTime=True)
                anim_start = cmds.playbackOptions(q=True, animationStartTime=True)
                anim_end = cmds.playbackOptions(q=True, animationEndTime=True)
                
                cmds.playbackOptions(
                    minTime=min_time + time_change,
                    maxTime=max_time + time_change,
                    animationStartTime=anim_start + time_change,
                    animationEndTime=anim_end + time_change
                )
                
                cmds.currentTime(min_time + time_change)
            except:
                pass
        
        message = "Shifted {0} animation curves by {1} frames.".format(shifted_count, time_change)
        if skipped_count > 0:
            message += "\n\nSkipped {0} locked or referenced curves.".format(skipped_count)
        if unlocked_layers:
            message += "\n\nUnlocked {0} animation layer(s).".format(len(unlocked_layers))
        if unlocked_objects:
            message += "\n\nTemporarily unlocked {0} camera(s) with locked attributes.".format(len(unlocked_objects))
        
        cmds.confirmDialog(
            title='Shift Complete',
            message=message,
            button=['OK'],
            defaultButton='OK',
            backgroundColor=(0.15, 0.15, 0.15)
        )
    
    except Exception as e:
        cmds.warning("Error during shift operation: {0}".format(str(e)))
        import traceback
        traceback.print_exc()
    
    finally:
        cmds.waitCursor(state=False)

def apply_shift(*args):
    offset_value = cmds.intFieldGrp('offsetField', query=True, value1=True)
    
    if offset_value == 0:
        cmds.warning("Offset value cannot be 0.")
        return
    
    result = cmds.confirmDialog(
        title='Apply Shift',
        message='Shift animation by {0} frames:'.format(offset_value),
        button=['Selected', 'All Scene', 'Cancel'],
        defaultButton='All Scene',
        cancelButton='Cancel',
        dismissString='Cancel',
        backgroundColor=(0.15, 0.15, 0.15)
    )
    
    if result == 'Selected':
        shift_animation_keys(offset_value, mode='selected')
    elif result == 'All Scene':
        shift_animation_keys(offset_value, mode='all')

def create_ui():
    window_name = 'shiftKeysWindow'
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title='Shift Animation Keys', widthHeight=(300, 180), sizeable=False, backgroundColor=(0.15, 0.15, 0.15), closeCommand=save_offset_value)
    
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAttach=('both', 15), backgroundColor=(0.15, 0.15, 0.15))
    
    cmds.separator(height=10, style='none')
    cmds.text(label='Frame Offset:', align='left', font='boldLabelFont')
    cmds.separator(height=5, style='none')
    
    saved_offset = load_offset_value()
    cmds.intFieldGrp('offsetField', numberOfFields=1, value1=saved_offset, columnWidth=(1, 280), changeCommand=save_offset_value)
    
    cmds.separator(height=15)
    
    cmds.button(label='Apply Shift', command=apply_shift, height=40)
    
    cmds.separator(height=10, style='none')
    
    cmds.showWindow(window)


def apply_shift_from_ui(offset_field_control):
    offset_value = cmds.intFieldGrp(offset_field_control, query=True, value1=True)
    
    if offset_value == 0:
        cmds.warning("Offset value cannot be 0.")
        return
    
    result = cmds.confirmDialog(
        title="Apply Shift",
        message="Shift animation by {0} frames:".format(offset_value),
        button=["Selected", "All Scene", "Cancel"],
        defaultButton="All Scene",
        cancelButton="Cancel",
        dismissString="Cancel",
        backgroundColor=(0.15, 0.15, 0.15)
    )
    
    if result == "Selected":
        shift_animation_keys(offset_value, mode="selected")
    elif result == "All Scene":
        shift_animation_keys(offset_value, mode="all")

def apply_shift_with_value(offset_value):
    if offset_value == 0:
        cmds.warning("Offset value cannot be 0.")
        return
    
    result = cmds.confirmDialog(
        title="Apply Shift",
        message="Shift animation by {0} frames:".format(offset_value),
        button=["Selected", "All Scene", "Cancel"],
        defaultButton="All Scene",
        cancelButton="Cancel",
        dismissString="Cancel",
        backgroundColor=(0.15, 0.15, 0.15)
    )
    
    if result == "Selected":
        shift_animation_keys(offset_value, mode="selected")
    elif result == "All Scene":
        shift_animation_keys(offset_value, mode="all")