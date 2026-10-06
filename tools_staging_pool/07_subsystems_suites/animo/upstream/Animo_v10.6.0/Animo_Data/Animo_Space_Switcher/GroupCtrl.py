from __future__ import print_function, division, absolute_import
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


def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)


def get_short_name(long_name):
    return long_name.split('|')[-1]


def get_unique_name(long_name):
    parts = long_name.split('|')
    if len(parts) > 1:
        return parts[-2] + '_' + parts[-1]
    return parts[-1]


def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group


def get_bounding_box_size(obj):
    try:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        
        if cmds.nodeType(obj) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
            shapes = [obj]
        
        if shapes:
            bbox = cmds.exactWorldBoundingBox(obj)
        else:
            bbox = cmds.xform(obj, q=True, bb=True, ws=True)
        
        width = abs(bbox[3] - bbox[0])
        height = abs(bbox[4] - bbox[1])
        depth = abs(bbox[5] - bbox[2])
        
        max_size = width
        if height > max_size:
            max_size = height
        if depth > max_size:
            max_size = depth
        
        if max_size < 0.01:
            max_size = 1.0
        
        return max_size
        
    except:
        return 1.0


def create_network_tracker(grp, grp_locator, ctrl_obj_pairs):
    print("Creating tracker for group: {0}".format(grp))
    print("Group locator: {0}".format(grp_locator))
    print("Control-object pairs: {0}".format(len(ctrl_obj_pairs)))
    
    tracker = cmds.createNode("network", name="esn_tracker_network")
    print("Created tracker: {0}".format(tracker))
    
    cmds.addAttr(tracker, ln="esn_group", at="message")
    cmds.connectAttr("{0}.message".format(grp), "{0}.esn_group".format(tracker), force=True)
    print("Connected to group")
    
    cmds.addAttr(tracker, ln="group_locator", at="message")
    cmds.connectAttr("{0}.message".format(grp_locator), "{0}.group_locator".format(tracker), force=True)
    print("Connected group_locator")
    
    for i, (ctrl, obj) in enumerate(ctrl_obj_pairs):
        ctrl_attr = "ctrl_{0}".format(i)
        obj_attr = "obj_{0}".format(i)
        
        cmds.addAttr(tracker, ln=ctrl_attr, at="message")
        cmds.addAttr(tracker, ln=obj_attr, at="message")
        
        cmds.connectAttr("{0}.message".format(ctrl), "{0}.{1}".format(tracker, ctrl_attr), force=True)
        cmds.connectAttr("{0}.message".format(obj), "{0}.{1}".format(tracker, obj_attr), force=True)
        print("Connected pair {0}: {1} -> {2}".format(i, ctrl, obj))


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


def btl_main():
    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = None
    
    try:
        sel = cmds.ls(sl=True, long=True)
        if len(sel) == 0:
            return
        
        obj_to_ctrl_map = {}
        
        for s in sel:
            unique_name = get_unique_name(s)
            ctrl_name = unique_name + "_esn_ctrl"
            if cmds.objExists(ctrl_name):
                cmds.delete(ctrl_name)
        
        total_size = 0
        valid_count = 0
        for s in sel:
            size = get_bounding_box_size(s)
            if size > 0.01:
                total_size += size
                valid_count += 1
        
        avg_size = total_size / valid_count if valid_count > 0 else 1.0
        master_size = avg_size * 3.0
        if master_size <= 0.0001 or master_size > 100000.0:
            master_size = 1.0
        
        spacify_group = get_or_create_spacify_group()
        
        grpLoc = cmds.spaceLocator()
        
        cmds.setAttr(grpLoc[0] + ".localScaleX", master_size)
        cmds.setAttr(grpLoc[0] + ".localScaleY", master_size)
        cmds.setAttr(grpLoc[0] + ".localScaleZ", master_size)
        cmds.makeIdentity(grpLoc[0], apply=True, translate=False, rotate=False, scale=True, normal=False)
        
        cmds.xform(grpLoc, rotateOrder=("xzy"))
        cmds.setAttr(grpLoc[0] + ".v", keyable=False, channelBox=False)
        cmds.setAttr(grpLoc[0] + ".overrideEnabled", 1)
        cmds.setAttr(grpLoc[0] + ".overrideColor", 13)
        
        add_to_esn_ctrls_set([grpLoc[0]])
        
        grp = cmds.group(n="esn_GRP_01")
        grp = cmds.ls(grp, long=True)[0]
        cmds.setAttr(grp + '.useOutlinerColor', True)
        cmds.setAttr(grp + ".outlinerColor", .7, .5, 1)
        
        grp = cmds.parent(grp, spacify_group)[0]
        grp = cmds.ls(grp, long=True)[0]
        
        pointCon = None
        for s in sel:
            pointCon = cmds.pointConstraint(s, grp, mo=False)
        
        cmds.refresh(suspend=True)
        refresh_suspended = True
        min_time = cmds.playbackOptions(q=True, min=True)
        max_time = cmds.playbackOptions(q=True, max=True)
        original_eval_mode = cmds.evaluationManager(q=True, mode=True)
        cmds.evaluationManager(mode='off')
        eval_mode_changed = True
        smart_bake(grp, min_time, max_time, source_objects=sel)
        cmds.delete(pointCon)
        
        ct = cmds.currentTime(q=True)
        
        objList = []
        locList = []
        for s in sel:
            short_name = get_short_name(s)
            if "_esn_ctrl" in short_name:
                obj = short_name.split("_esn_ctrl")[0]
                objList.append(obj)
                locList.append(s)
        
        add_to_esn_ctrls_set(locList)
        
        if len(sel) == 1:
            cmds.select(grpLoc[0])
            sel_orig = cmds.ls(sl=True, long=True)
            lastLoc = sel_orig[0]
            
            objList = []
            locList = []
            for s in sel:
                unique_name = get_unique_name(s)
                obj_size = get_bounding_box_size(s)
                
                loc = cmds.spaceLocator(n=unique_name + "_esn_ctrl")
                
                cmds.setAttr(loc[0] + ".scaleX", obj_size)
                cmds.setAttr(loc[0] + ".scaleY", obj_size)
                cmds.setAttr(loc[0] + ".scaleZ", obj_size)
                
                cmds.xform(loc, rotateOrder=("xzy"))
                cmds.setAttr(loc[0] + ".v", keyable=False, channelBox=False)
                cmds.setAttr(loc[0] + ".overrideEnabled", 1)
                cmds.setAttr(loc[0] + ".overrideColor", 18)
                cmds.setAttr(loc[0] + '.useOutlinerColor', True)
                cmds.setAttr(loc[0] + ".outlinerColor", .7, .5, 1)
                cmds.parentConstraint(s, loc, mo=False)
                cmds.parent(loc, lastLoc)
                locList.append(loc[0])
                obj_to_ctrl_map[s] = loc[0]
            
            min_anim = cmds.playbackOptions(q=True, ast=True)
            max_anim = cmds.playbackOptions(q=True, aet=True)
            smart_bake(locList, min_anim, max_anim, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
            
            add_to_esn_ctrls_set(locList)
            
            for obj_long, loc in obj_to_ctrl_map.items():
                smartConstraint(loc, obj_long)
            
        else:
            cmds.select(sel)
            cmds.select(grpLoc[0], add=True)
            
            blah = cmds.ls(sl=True, long=True)
            lastLoc = blah[-1]
            blah.pop(-1)
            cmds.select(blah)
            
            if objList:
                min_anim = cmds.playbackOptions(q=True, min=True)
                max_anim = cmds.playbackOptions(q=True, max=True)
                smart_bake(objList, min_anim, max_anim, source_objects=locList)
                cmds.currentTime(ct)
                cmds.select(objList, add=True)
                cmds.delete(locList)
            
            cmds.select(lastLoc, add=True)
            sel = cmds.ls(sl=True, long=True)
            
            if len(sel) == 0:
                return
            
            lastSel = sel.pop(-1)
            locList = []
            
            for s in sel:
                unique_name = get_unique_name(s)
                obj_size = get_bounding_box_size(s)
                
                loc = cmds.spaceLocator(n=unique_name + "_esn_ctrl")
                
                cmds.setAttr(loc[0] + ".scaleX", obj_size)
                cmds.setAttr(loc[0] + ".scaleY", obj_size)
                cmds.setAttr(loc[0] + ".scaleZ", obj_size)
                
                cmds.xform(loc, rotateOrder=("xzy"))
                cmds.setAttr(loc[0] + ".v", keyable=False, channelBox=False)
                cmds.setAttr(loc[0] + ".overrideEnabled", 1)
                cmds.setAttr(loc[0] + ".overrideColor", 18)
                cmds.setAttr(loc[0] + '.useOutlinerColor', True)
                cmds.setAttr(loc[0] + ".outlinerColor", .7, .5, 1)
                cmds.parentConstraint(s, loc, mo=False)
                cmds.parent(loc, lastSel)
                locList.append(loc[0])
                obj_to_ctrl_map[s] = loc[0]
            
            min_anim = cmds.playbackOptions(q=True, ast=True)
            max_anim = cmds.playbackOptions(q=True, aet=True)
            smart_bake(locList, min_anim, max_anim, attributes=("tx", "ty", "tz", "rx", "ry", "rz"), source_objects=sel)
            
            add_to_esn_ctrls_set(locList)
            
            for obj_long, loc in obj_to_ctrl_map.items():
                smartConstraint(loc, obj_long)
        
        grpLoc_long = cmds.ls(grpLoc[0], long=True)[0]
        ctrl_obj_pairs = [(cmds.ls(loc, long=True)[0], obj) for obj, loc in obj_to_ctrl_map.items()]
        create_network_tracker(grp, grpLoc_long, ctrl_obj_pairs)
        
        mel.eval("setToolTo $gScale;")
        cmds.modelEditor('modelPanel4', e=True, locators=True)
        cmds.delete(sc=True)
        cmds.select(grpLoc[0])
        cmds.filterCurve()
        cmds.selectKey(cl=True)
        
    except Exception as e:
        cmds.warning("Script error: " + str(e))
        
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
    btl_main()