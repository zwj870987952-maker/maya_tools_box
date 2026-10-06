from maya import cmds
import maya.OpenMaya as om
import math
import maya.mel as mel
import sys

try:
    from spacify_core import SPACIFY_STATE
except:
    SPACIFY_STATE = {"only_keys": False}


def get_all_keyframe_times(objects):
    all_keys = set()
    for obj in objects:
        if cmds.objExists(obj):
            keys = cmds.keyframe(obj, q=True) or []
            for k in keys:
                all_keys.add(k)
    return sorted(list(all_keys))


def smart_bake(objects, start_time=None, end_time=None, attributes=None, source_objects=None):
    """
    Bake animation on objects.
    If source_objects provided with Only Keys mode:
    - Constraints should already exist with maintain offset
    - We just go to each key time and set a key on the constrained objects
    - Use dgeval to force constraint evaluation without unsuspending refresh
    """
    only_keys = SPACIFY_STATE.get("only_keys", False)
    
    if not objects:
        return
    
    if isinstance(objects, str):
        objects = [objects]
    
    if not only_keys:
        if start_time is None:
            start_time = cmds.playbackOptions(q=True, ast=True)
        if end_time is None:
            end_time = cmds.playbackOptions(q=True, aet=True)
        
        if attributes:
            cmds.bakeResults(objects, sm=True, pok=True, t=(start_time, end_time), at=attributes)
        else:
            cmds.bakeResults(objects, sm=True, pok=True, t=(start_time, end_time))
    else:
        key_source = source_objects if source_objects else objects
        if isinstance(key_source, str):
            key_source = [key_source]
        
        key_times = get_all_keyframe_times(key_source)
        
        if not key_times:
            if start_time is None:
                start_time = cmds.playbackOptions(q=True, ast=True)
            if end_time is None:
                end_time = cmds.playbackOptions(q=True, aet=True)
            key_times = [start_time, end_time]
        
        current_time = cmds.currentTime(q=True)
        
        # Go to each key time and set a key on the objects
        # Use dgeval to force constraint evaluation without unsuspending refresh
        for t in key_times:
            cmds.currentTime(t, update=True)
            for obj in objects:
                if cmds.objExists(obj):
                    # Force constraint evaluation using dgeval
                    cmds.dgeval(obj + '.translate', obj + '.rotate')
                    # Make sure blendParent is on if it exists
                    if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                        try:
                            cmds.setAttr(obj + '.blendParent1', 1)
                        except:
                            pass
                    # Set keyframe - this captures the constraint-driven position
                    cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
        
        cmds.currentTime(current_time)


def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)

def get_evaluation_mode():
    return cmds.evaluationManager(query=True, mode=True)[0]

def set_evaluation_mode(mode):
    current_mode = get_evaluation_mode()
    if current_mode != mode:
        cmds.evaluationManager(mode=mode)
    return current_mode

def restore_evaluation_mode(original_mode):
    set_evaluation_mode(original_mode)

def get_long_name(obj):
    long_names = cmds.ls(obj, long=True)
    return long_names[0] if long_names else obj

def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group

def get_bounding_box_size(obj):
    bbox = cmds.exactWorldBoundingBox(obj)
    width = bbox[3] - bbox[0]
    height = bbox[4] - bbox[1]
    depth = bbox[5] - bbox[2]
    raw_size = max(width, height, depth)

    scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
    avg_scale = (abs(scale[0]) + abs(scale[1]) + abs(scale[2])) / 3.0
    if 0.0001 < avg_scale < 10000.0:
        size = raw_size / avg_scale
    else:
        size = raw_size

    return abs(size)

def set_locator_size(locator, source_object):
    bbox_size = get_bounding_box_size(source_object) * 0.6
    if bbox_size <= 0.0001 or bbox_size > 100000.0:
        bbox_size = 1.0
    locator_shape = cmds.listRelatives(locator, shapes=True)[0]
    cmds.setAttr(locator_shape + ".localScaleX", bbox_size)
    cmds.setAttr(locator_shape + ".localScaleY", bbox_size)
    cmds.setAttr(locator_shape + ".localScaleZ", bbox_size)

def smartConstraint(ctrl=None, object=None, maintainOffset=False):
    # Suppress cycle warnings during constraint creation
    cycle_check_was_on = cmds.cycleCheck(q=True, e=True)
    if cycle_check_was_on:
        cmds.cycleCheck(e=False)
    
    try:
        transAttr = None
        rotAttr = None
        scaleAttr = None
        translate = True
        rotate = True
        scale = False

        if translate:
            transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')
        if rotate:
            rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')
        if scale:
            scaleAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='scale*')

        rotSkip = []
        transSkip = []

        for axis in ['x', 'y', 'z']:
            if transAttr and not 'translate' + axis.upper() in transAttr:
                transSkip.append(axis)
            if rotAttr and not 'rotate' + axis.upper() in rotAttr:
                rotSkip.append(axis)

        if not transSkip:
            transSkip = 'none'
        if not rotSkip:
            rotSkip = 'none'

        constraints = []
        if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
            constraints.append(cmds.parentConstraint(ctrl, object, maintainOffset=maintainOffset))
        else:
            if transAttr:
                constraints.append(cmds.pointConstraint(ctrl, object, skip=transSkip, maintainOffset=maintainOffset))
            if rotAttr:
                constraints.append(cmds.orientConstraint(ctrl, object, skip=rotSkip, maintainOffset=maintainOffset))

        return constraints
    finally:
        if cycle_check_was_on:
            cmds.cycleCheck(e=True)

def esn_alignObjects():
    CT = cmds.currentTime(q=True)

    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = int(timeRange[0])
    EndRange = int(timeRange[1] - 1)
    min_key = cmds.findKeyframe(which="first")
    max_key = cmds.findKeyframe(which="last")
    keys = cmds.keyframe(q=True, t=(min_key, max_key))
    firstSel = cmds.ls(sl=True, long=True)[0]

    if keys:
        keys = set(keys)
        for key in keys:
            cmds.currentTime(key)
            cmds.matchTransform(pos=True, rot=True)
            cmds.setKeyframe(at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
        cmds.currentTime(CT)
        cmds.select(firstSel)
    else:
        cmds.matchTransform(pos=True, rot=True)

def delete_esn_ctrl(obj_long_name):
    base_name = obj_long_name.split('|')[-1]
    potential_ctrl = base_name + "_esn_ctrl"

    all_ctrls = cmds.ls(potential_ctrl, long=True)
    for ctrl in all_ctrls:
        if cmds.objExists(ctrl):
            cmds.delete(ctrl)

def encode_long_name(long_name):
    return long_name.replace('|', '_PIPE_')

def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')

def get_ctrl_name_for_object(obj_long_name):
    encoded_name = encode_long_name(obj_long_name)
    return encoded_name + "_esn_ctrl"

def get_object_from_ctrl(ctrl_long_name):
    base_name = ctrl_long_name.split('|')[-1]
    if "_esn_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_ctrl")[0]
        return decode_long_name(encoded_obj)
    return None

def btl_ctrl_mode():
    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        sys.exit()

    for s in sel:
        delete_esn_ctrl(s)

    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        sys.exit()

    for s in sel:
        keys = cmds.keyframe(s, q=True)
        if not keys:
            cmds.setKeyframe(s)

    ct = cmds.currentTime(q=True)
    objList = []

    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = None

    try:
        for s in sel:
            base_name = s.split('|')[-1]
            if "_esn_ctrl" in base_name:
                if not refresh_suspended:
                    cmds.refresh(suspend=True)
                    refresh_suspended = True
                if not eval_mode_changed:
                    original_eval_mode = set_evaluation_mode("off")
                    eval_mode_changed = True

                obj_long = get_object_from_ctrl(s)

                if obj_long and cmds.objExists(obj_long):
                    objList.append(obj_long)
                    keys = cmds.keyframe(s, q=True)
                    cmds.cutKey(obj_long)
                    firstKey = cmds.findKeyframe(s, which="first")
                    cmds.setKeyframe(obj_long, t=(firstKey, firstKey))

                    orientQuery = cmds.attributeQuery("blendOrient1", node=obj_long, exists=True)
                    if orientQuery:
                        cmds.setAttr(obj_long + ".blendOrient1", 1)
                    else:
                        parentQuery = cmds.attributeQuery("blendParent1", node=obj_long, exists=True)
                        if parentQuery:
                            cmds.setAttr(obj_long + ".blendParent1", 1)

                    if keys:
                        keys = list(set(keys))
                        for key in keys:
                            cmds.currentTime(key)
                            cmds.setKeyframe(obj_long)

                    cmds.delete(s)

                cmds.select(objList)
                cmds.currentTime(ct)
    finally:
        if refresh_suspended:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
        if eval_mode_changed and original_eval_mode:
            try:
                restore_evaluation_mode(original_eval_mode)
            except:
                pass

    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        sys.exit()

    CT = cmds.currentTime(q=True)

    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.refresh(suspend=True)
    refresh_suspended = True
    set_evaluation_mode('off')
    eval_mode_changed = True
    cmds.waitCursor(state=True)

    try:
        spacify_group = get_or_create_spacify_group()
        selection = cmds.ls(sl=True, long=True)
        nullList = []

        for sel_obj in selection:
            ctrl_name = get_ctrl_name_for_object(sel_obj)
            null = cmds.spaceLocator(name=ctrl_name)
            null_long = cmds.ls(null[0], long=True)[0]

            set_locator_size(null_long, sel_obj)
            cmds.setAttr(null_long + ".sx", keyable=False, channelBox=False)
            cmds.setAttr(null_long + ".sy", keyable=False, channelBox=False)
            cmds.setAttr(null_long + ".sz", keyable=False, channelBox=False)
            cmds.setAttr(null_long + ".v", keyable=False, channelBox=False)
            cmds.setAttr(null_long + ".overrideEnabled", 1)
            cmds.setAttr(null_long + ".overrideColor", 18)
            cmds.setAttr(null_long + '.useOutlinerColor', True)
            cmds.setAttr(null_long + ".outlinerColor", 1, 0.5, 0.5)

            null_long = cmds.parent(null_long, spacify_group)[0]
            null_long = cmds.ls(null_long, long=True)[0]
            nullList.append(null_long)
            cmds.select(sel_obj, add=True)
            esn_alignObjects()
            smartConstraint(null_long, sel_obj, maintainOffset=False)

        cmds.select(nullList)
    finally:
        if refresh_suspended:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
        try:
            cmds.waitCursor(state=False)
        except:
            pass
        if eval_mode_changed and original_eval_mode:
            try:
                cmds.evaluationManager(mode=original_eval_mode[0])
            except:
                pass

    mel.eval("setToolTo $gScale;")
    cmds.delete(sc=True)
    cmds.modelEditor('modelPanel4', e=True, locators=True)

def btl_main():
    # Suppress cycle warnings during constraint operations
    cycle_check_was_on = cmds.cycleCheck(q=True, e=True)
    if cycle_check_was_on:
        cmds.cycleCheck(e=False)
    
    Panel = cmds.getPanel(withFocus=True)

    if Panel == None:
        Panel = cmds.getPanel(withFocus=True)

    if "modelPanel" not in Panel:
        Panel = cmds.getPanel(withFocus=True)

    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        if cycle_check_was_on:
            cmds.cycleCheck(e=True)
        sys.exit()

    for s in sel:
        delete_esn_ctrl(s)

    ct = cmds.currentTime(q=True)

    objList = []
    locList = []

    for s in sel:
        base_name = s.split('|')[-1]
        if "_esn_ctrl" in base_name:
            obj_long = get_object_from_ctrl(s)

            if obj_long and cmds.objExists(obj_long):
                objList.append(obj_long)
                locList.append(s)

    if objList:
        try:
            cmds.refresh(suspend=True)
            original_eval_mode = set_evaluation_mode("off")

            min_time = cmds.playbackOptions(q=True, min=True)
            max_time = cmds.playbackOptions(q=True, max=True)
            smart_bake(objList, min_time, max_time)
            cmds.currentTime(ct)
            cmds.select(objList, add=True)
            cmds.delete(locList)
        finally:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
            try:
                restore_evaluation_mode(original_eval_mode)
            except:
                pass

    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        if cycle_check_was_on:
            cmds.cycleCheck(e=True)
        sys.exit()

    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = int(timeRange[0])
    EndRange = int(timeRange[1] - 1)

    min_time = cmds.playbackOptions(q=True, ast=True)
    max_time = cmds.playbackOptions(q=True, aet=True)

    cmds.refresh(suspend=True)
    original_eval_mode = set_evaluation_mode('off')

    spacify_group = get_or_create_spacify_group()
    ctrlList = []
    conList = []

    try:
        if (EndRange - StartRange == 0):
            for s in sel:
                ctrl_name = get_ctrl_name_for_object(s)
                ctrl = cmds.spaceLocator(name=ctrl_name)[0]
                ctrl_long = cmds.ls(ctrl, long=True)[0]

                set_locator_size(ctrl_long, s)
                cmds.setAttr(ctrl_long + ".sx", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".sy", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".sz", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".v", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".overrideEnabled", 1)
                cmds.setAttr(ctrl_long + ".overrideColor", 18)
                cmds.setAttr(ctrl_long + '.useOutlinerColor', True)
                cmds.setAttr(ctrl_long + ".outlinerColor", 1, 0.5, 0.5)

                ctrl_long = cmds.parent(ctrl_long, spacify_group)[0]
                ctrl_long = cmds.ls(ctrl_long, long=True)[0]
                ctrlList.append(ctrl_long)
                cmds.matchTransform(ctrl_long, s)

                con = cmds.parentConstraint(s, ctrl_long, mo=True)
                conList.append(con[0])
                cmds.select(cl=True)
                cmds.select(ctrl_long, add=True)

            smart_bake(ctrlList, min_time, max_time, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
            add_to_esn_ctrls_set(ctrlList)
            
            # Delete the object->locator constraints BEFORE creating locator->object constraints
            cmds.delete(conList)
            conList = []

            for idx, s in enumerate(sel):
                smartConstraint(ctrlList[idx], s, maintainOffset=True)

            cmds.select(ctrlList)
            mel.eval("setToolTo $gScale;")
            cmds.delete(sc=True)
        else:
            for s in sel:
                ctrl_name = get_ctrl_name_for_object(s)
                ctrl = cmds.spaceLocator(name=ctrl_name)[0]
                ctrl_long = cmds.ls(ctrl, long=True)[0]

                set_locator_size(ctrl_long, s)
                cmds.setAttr(ctrl_long + ".sx", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".sy", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".sz", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".v", keyable=False, channelBox=False)
                cmds.setAttr(ctrl_long + ".overrideEnabled", 1)
                cmds.setAttr(ctrl_long + ".overrideColor", 18)
                cmds.setAttr(ctrl_long + '.useOutlinerColor', True)
                cmds.setAttr(ctrl_long + ".outlinerColor", 1, 0.5, 0.5)

                ctrl_long = cmds.parent(ctrl_long, spacify_group)[0]
                ctrl_long = cmds.ls(ctrl_long, long=True)[0]
                ctrlList.append(ctrl_long)
                cmds.matchTransform(ctrl_long, s)

                con = cmds.parentConstraint(s, ctrl_long, mo=True)
                conList.append(con[0])
                cmds.select(cl=True)
                cmds.select(ctrl_long, add=True)

            smart_bake(ctrlList, StartRange, EndRange, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
            add_to_esn_ctrls_set(ctrlList)
            
            # Delete the object->locator constraints BEFORE creating locator->object constraints
            cmds.delete(conList)
            conList = []

            for idx, s in enumerate(sel):
                smartConstraint(ctrlList[idx], s, maintainOffset=True)

            cmds.select(ctrlList)
            mel.eval("setToolTo $gScale;")
            cmds.delete(sc=True)
            
    except Exception as e:
        cmds.warning("Error creating world space controls: " + str(e))
        
        # Delete any constraints we created
        for con in conList:
            if cmds.objExists(con):
                try:
                    cmds.delete(con)
                except:
                    pass
        
        # Delete any locators we created
        for ctrl in ctrlList:
            if cmds.objExists(ctrl):
                try:
                    cmds.delete(ctrl)
                except:
                    pass
                    
    finally:
        try:
            cmds.refresh(suspend=False)
        except:
            pass
        try:
            restore_evaluation_mode(original_eval_mode)
        except:
            pass

    cmds.modelEditor(Panel, e=True, locators=True)
    cmds.filterCurve()
    cmds.selectKey(cl=True)
    
    # Restore cycle check setting
    if cycle_check_was_on:
        cmds.cycleCheck(e=True)

mods = cmds.getModifiers()

if __name__ == "__main__":
    btl_main()