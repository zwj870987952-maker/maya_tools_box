from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from maya import cmds
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
        
        # Temporarily unsuspend refresh so constraints can evaluate
        cmds.refresh(suspend=False)
        
        for t in key_times:
            cmds.currentTime(t, update=True)
            cmds.refresh(force=True)
            for obj in objects:
                if cmds.objExists(obj):
                    if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                        try:
                            cmds.setAttr(obj + '.blendParent1', 1)
                        except:
                            pass
                    cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
        
        # Re-suspend refresh
        cmds.refresh(suspend=True)
        
        cmds.currentTime(current_time)


# Global lock to prevent multiple simultaneous executions
_FK_CHAIN_RUNNING = False
    
def add_to_esn_fk_set(locators):
    set_name = "esn_fk_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)

def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)

def get_evaluation_mode():
    try:
        return cmds.evaluationManager(query=True, mode=True)[0]
    except:
        return "off"

def set_evaluation_mode(mode):
    try:
        current_mode = get_evaluation_mode()
        if current_mode != mode:
            cmds.evaluationManager(mode=mode)
        return current_mode
    except:
        return "off"

def restore_evaluation_mode(original_mode):
    try:
        set_evaluation_mode(original_mode)
    except:
        pass

def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group

def smartConstraint(ctrl=None, object=None, maintainOffset=False):
    transAttr = None
    rotAttr = None
    translate = True
    rotate = True

    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')     
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')

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

def encode_long_name(long_name):
    return long_name.replace('|', '_PIPE_')

def get_ctrl_name_for_object(obj_long_name):
    encoded_name = encode_long_name(obj_long_name)
    return encoded_name + "_esn_fk_ctrl"

def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')

def get_object_from_ctrl(ctrl_long_name):
    base_name = ctrl_long_name.split('|')[-1]
    if "_esn_fk_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_fk_ctrl")[0]
        return decode_long_name(encoded_obj)
    elif "_esn_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_ctrl")[0]
        return decode_long_name(encoded_obj)
    return None

def delete_esn_ctrl(obj_long_name):
    base_name = obj_long_name.split('|')[-1]
    potential_ctrl = base_name + "_esn_ctrl"
    
    all_ctrls = cmds.ls(potential_ctrl, long=True)
    for ctrl in all_ctrls:
        if cmds.objExists(ctrl):
            try:
                cmds.delete(ctrl)
            except:
                pass

def btl_main():
    global _FK_CHAIN_RUNNING
    
    if _FK_CHAIN_RUNNING:
        return
    
    _FK_CHAIN_RUNNING = True
    
    try:
        sel = cmds.ls(sl=True, long=True, type='transform')
        
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects in hierarchy order to create an FK chain.")
            return
        
        Panel = cmds.getPanel(withFocus=True)
        if Panel == None or "modelPanel" not in Panel:
            Panel = "modelPanel4"
        
        for s in sel:
            delete_esn_ctrl(s)
        
        ct = cmds.currentTime(q=True)
        
        objList = []
        locList = []
        
        for s in sel:
            base_name = s.split('|')[-1]
            if "_esn_fk_ctrl" in base_name:
                obj_long = get_object_from_ctrl(s)
                if obj_long and cmds.objExists(obj_long):
                    objList.append(obj_long)
                    locList.append(s)
        
        if objList:
            original_eval_mode = set_evaluation_mode("off")
            try:
                cmds.refresh(suspend=True)
                min_time = cmds.playbackOptions(q=True, min=True)
                max_time = cmds.playbackOptions(q=True, max=True)
                smart_bake(objList, min_time, max_time, source_objects=locList)
                cmds.currentTime(ct)
                cmds.select(objList)
                cmds.delete(locList)
            finally:
                try:
                    cmds.refresh(suspend=False)
                except:
                    pass
                restore_evaluation_mode(original_eval_mode)
            
            sel = cmds.ls(sl=True, long=True, type='transform')
            if len(sel) == 0:
                return
        
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        StartRange = int(timeRange[0])
        EndRange = int(timeRange[1] - 1)
        
        min_time = cmds.playbackOptions(q=True, ast=True)
        max_time = cmds.playbackOptions(q=True, aet=True)
        
        original_eval_mode = set_evaluation_mode('off')
        
        try:
            cmds.refresh(suspend=True)
            
            spacify_group = get_or_create_spacify_group()
            ctrlList = []
            conList = []
            
            if (EndRange - StartRange == 0):
                # Create locators
                for s in sel:
                    ctrl_name = get_ctrl_name_for_object(s)
                    ctrl = cmds.spaceLocator(name=ctrl_name)[0]
                    
                    cmds.xform(ctrl, rotateOrder="xzy")
                    cmds.setAttr(ctrl + ".sx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".sy", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".sz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".v", keyable=False, channelBox=False)
                    cmds.setAttr(ctrl + ".overrideEnabled", 1)
                    cmds.setAttr(ctrl + ".overrideColor", 18)
                    cmds.setAttr(ctrl + '.useOutlinerColor', True)
                    cmds.setAttr(ctrl + ".outlinerColor", 1, 0.5, 0.5)
                    
                    cmds.matchTransform(ctrl, s, pos=True, rot=True)
                    ctrlList.append(ctrl)
                
                # Parent all locators to SPACIFY group
                for ctrl in ctrlList:
                    cmds.parent(ctrl, spacify_group)
                
                # Build FK hierarchy
                ctrlList_updated = []
                for i in range(len(ctrlList)):
                    if i == 0:
                        ctrl_long = cmds.ls(ctrlList[i], long=True)[0]
                        ctrlList_updated.append(ctrl_long)
                    else:
                        parent_ctrl = ctrlList_updated[i - 1]
                        child_ctrl_short = ctrlList[i].split('|')[-1]
                        child_parented = cmds.parent(child_ctrl_short, parent_ctrl)[0]
                        child_long = cmds.ls(child_parented, long=True)[0]
                        ctrlList_updated.append(child_long)
                        ctrlList_updated[i - 1] = cmds.ls(parent_ctrl, long=True)[0]
                
                ctrlList = ctrlList_updated
                
                # Constrain all locators to original objects
                for idx, s in enumerate(sel):
                    con = cmds.parentConstraint(s, ctrlList[idx], mo=False)
                    conList.append(con[0])
                
                # Bake all locators in one operation
                smart_bake(ctrlList, min_time, max_time, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
                cmds.delete(conList)
                
                add_to_esn_fk_set(ctrlList)
                
                # Now make locators drive the original objects
                for idx, s in enumerate(sel):
                    smartConstraint(ctrlList[idx], s, maintainOffset=True)
                
                cmds.select(ctrlList)
                mel.eval("setToolTo $gScale;")
                try:
                    cmds.delete(sc=True)
                except:
                    pass
            else:
                # Create locators
                for s in sel:
                    ctrl_name = get_ctrl_name_for_object(s)
                    ctrl = cmds.spaceLocator(name=ctrl_name)[0]
                    
                    cmds.xform(ctrl, rotateOrder="xzy")
                    cmds.setAttr(ctrl + ".sx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".sy", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".sz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(ctrl + ".v", keyable=False, channelBox=False)
                    cmds.setAttr(ctrl + ".overrideEnabled", 1)
                    cmds.setAttr(ctrl + ".overrideColor", 18)
                    cmds.setAttr(ctrl + '.useOutlinerColor', True)
                    cmds.setAttr(ctrl + ".outlinerColor", 1, 0.5, 0.5)
                    
                    cmds.matchTransform(ctrl, s, pos=True, rot=True)
                    ctrlList.append(ctrl)
                
                # Parent all locators to SPACIFY group
                for ctrl in ctrlList:
                    cmds.parent(ctrl, spacify_group)
                
                # Build FK hierarchy
                ctrlList_updated = []
                for i in range(len(ctrlList)):
                    if i == 0:
                        ctrl_long = cmds.ls(ctrlList[i], long=True)[0]
                        ctrlList_updated.append(ctrl_long)
                    else:
                        parent_ctrl = ctrlList_updated[i - 1]
                        child_ctrl_short = ctrlList[i].split('|')[-1]
                        child_parented = cmds.parent(child_ctrl_short, parent_ctrl)[0]
                        child_long = cmds.ls(child_parented, long=True)[0]
                        ctrlList_updated.append(child_long)
                        ctrlList_updated[i - 1] = cmds.ls(parent_ctrl, long=True)[0]
                
                ctrlList = ctrlList_updated
                
                # Constrain all locators to original objects
                for idx, s in enumerate(sel):
                    con = cmds.parentConstraint(s, ctrlList[idx], mo=False)
                    conList.append(con[0])
                
                # Bake all locators in one operation
                smart_bake(ctrlList, StartRange, EndRange, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
                cmds.delete(conList)
                
                add_to_esn_fk_set(ctrlList)
                
                # Now make locators drive the original objects
                for idx, s in enumerate(sel):
                    smartConstraint(ctrlList[idx], s, maintainOffset=True)
                
                cmds.select(ctrlList)
                mel.eval("setToolTo $gScale;")
            try:
                cmds.delete(sc=True)
            except:
                pass
        
            try:
                cmds.modelEditor(Panel, e=True, locators=True)
            except:
                pass
            try:
                cmds.filterCurve()
            except:
                pass
            try:
                cmds.selectKey(cl=True)
            except:
                pass
        finally:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
            restore_evaluation_mode(original_eval_mode)
        
        cmds.currentTime(ct)
    finally:
        _FK_CHAIN_RUNNING = False

# Uncomment the line below to run directly from script editor:
# btl_main()