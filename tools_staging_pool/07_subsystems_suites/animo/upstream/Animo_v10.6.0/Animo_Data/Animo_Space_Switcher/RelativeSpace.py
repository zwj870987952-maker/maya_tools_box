import maya.cmds as cmds
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
            cmds.bakeResults(objects, sm=True, t=(start_time, end_time), pok=True)
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


def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)

def encode_long_name(long_name):
    return long_name.replace('|', '_PIPE_')

def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')

def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group
            
def smartConstraint(ctrl=None, object=None):
    transAttr = None
    rotAttr = None
    scaleAttr = None
    translate = True
    rotate = True
    scale = False
    maintainOffset = True 

    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')     
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')      
    if scale:
        scaleAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='scale*')     

    rotSkip = []
    transSkip = []

    for axis in ['x','y','z']:
        if transAttr and not 'translate'+axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate'+axis.upper() in rotAttr:
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

def create_relative_space_ctrls():
    sel = cmds.ls(sl=True, long=True)

    if len(sel) < 2:
        if len(sel) == 0:
            cmds.warning("Please select at least two objects.")
        else:
            cmds.warning("Please select at least two objects: the objects to constrain and the parent object as the last selection.")
        return
    
    lastSel = sel.pop(-1)
    locList = []
    conList = []
    grpList = []
    objectMap = {}
    spacify_group = None
    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = None
    
    try:
        original_eval_mode = cmds.evaluationManager(query=True, mode=True)
        cmds.evaluationManager(mode="off")
        eval_mode_changed = True
        cmds.refresh(suspend=True)
        refresh_suspended = True
        
        spacify_group = get_or_create_spacify_group()
        
        for s in sel:
            encoded_name = encode_long_name(s)
            loc_name = encoded_name + "_esn_ctrl"
            
            loc = cmds.spaceLocator(n=loc_name)[0]
            cmds.setAttr(loc + ".overrideEnabled", 1)
            cmds.setAttr(loc + ".overrideColor", 18)  
            cmds.setAttr(loc + '.useOutlinerColor', True)
            cmds.setAttr(loc + ".outlinerColor", .8, .3, .5)        
            locList.append(loc)            

            cmds.setAttr(loc + ".sx", keyable=False, channelBox=False)
            cmds.setAttr(loc + ".sy", keyable=False, channelBox=False)
            cmds.setAttr(loc + ".sz", keyable=False, channelBox=False)
            
            grp = cmds.group(n=encoded_name + "_esn_ctrl_grp")
            grpList.append(grp)
            cmds.setAttr(grp + '.useOutlinerColor', True)
            cmds.setAttr(grp + ".outlinerColor", .7, .5, 1)

            cmds.matchTransform(loc, s, pos=True)
            cmds.matchTransform(loc, s, rot=True)
            con = cmds.parentConstraint(s, loc, mo=False)[0]
            conList.append(con)
            cmds.parentConstraint(lastSel, grp, mo=False)
            
            cmds.parent(grp, spacify_group)
            
            objectMap[loc] = s
           
        min_time = cmds.playbackOptions(q=True, ast=True)
        max_time = cmds.playbackOptions(q=True, aet=True)
        smart_bake(locList, min_time, max_time, source_objects=sel)
        add_to_esn_ctrls_set(grpList)
        cmds.delete(conList)
        conList = []  # Clear so cleanup doesn't try to delete again
            
        for loc in locList:
            obj = objectMap[loc]
            smartConstraint(loc, obj)      
            
        cmds.select(locList)
        
    except Exception as e:
        cmds.warning("Error creating relative space controls: " + str(e))
        
        # Delete any constraints we created
        for con in conList:
            if cmds.objExists(con):
                try:
                    cmds.delete(con)
                except:
                    pass
        
        # Delete any groups we created (will also delete locators inside)
        for grp in grpList:
            if cmds.objExists(grp):
                try:
                    cmds.delete(grp)
                except:
                    pass
                    
    finally:
        if refresh_suspended:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
        
        if eval_mode_changed and original_eval_mode:
            try:
                cmds.evaluationManager(mode=original_eval_mode[0])
            except:
                pass


if __name__ == "__main__":
    create_relative_space_ctrls()
