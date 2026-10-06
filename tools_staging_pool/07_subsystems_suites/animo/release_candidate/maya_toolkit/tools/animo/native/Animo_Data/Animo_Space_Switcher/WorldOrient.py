try:
    import __builtin__ as builtins
except ImportError:
    import builtins
try:
    max = builtins.max 
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass

from maya import cmds
import maya.mel as mel
import sys

try:
    from spacify_core import SPACIFY_STATE
except:
    SPACIFY_STATE = {"only_keys": False}


def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)


def esn_alignObjects(null, sel_obj):
    """
    Bake locator animation from object.
    - Only Keys mode: matchTransform + setKeyframe at each key
    - Normal mode: parentConstraint + bakeResults
    """
    only_keys = SPACIFY_STATE.get("only_keys", False)
    CT = cmds.currentTime(q=True)
    
    if only_keys:
        # Only Keys mode - matchTransform at each keyframe
        min_key = cmds.findKeyframe(sel_obj, which="first")
        max_key = cmds.findKeyframe(sel_obj, which="last")
        keys = cmds.keyframe(sel_obj, q=True, t=(min_key, max_key))
        
        if keys:
            keys = builtins.set(keys)
            for key in keys:
                cmds.currentTime(key)
                cmds.matchTransform(null, sel_obj, pos=True, rot=True)
                cmds.setKeyframe(null, at=('rx', 'ry', 'rz'))
            cmds.currentTime(CT)
        else:
            cmds.matchTransform(null, sel_obj, pos=True, rot=True)
    else:
        # Normal mode - constraint + bake every frame
        cmds.matchTransform(null, sel_obj, pos=True, rot=True)
        con = cmds.parentConstraint(sel_obj, null, mo=True)[0]
        min_time = cmds.playbackOptions(q=True, ast=True)
        max_time = cmds.playbackOptions(q=True, aet=True)
        cmds.bakeResults(null, sm=True, pok=True, t=(min_time, max_time), at=('rx', 'ry', 'rz'))
        cmds.delete(con)


def orient_main():
    Panel = cmds.getPanel(withFocus=True)
    if Panel is None:
        Panel = cmds.getPanel(withFocus=True)
    if "modelPanel" not in Panel:
        Panel = cmds.getPanel(withFocus=True)
    
    sel = cmds.ls(sl=True)
    if builtins.len(sel) == 0:
        sys.exit()
    
    # Delete existing controls
    for s in sel:
        if cmds.objExists(s + "_esn_ctrl"):
            cmds.delete(s + "_esn_ctrl")
    
    sel = cmds.ls(sl=True)
    if builtins.len(sel) == 0:
        sys.exit()
    
    # Ensure objects have at least one keyframe
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
        # Handle existing _esn_ctrl - bake back to objects
        for s in sel:
            if "_esn_ctrl" in s:
                if not refresh_suspended:
                    cmds.refresh(suspend=True)
                    refresh_suspended = True
                if not eval_mode_changed:
                    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
                    cmds.evaluationManager(mode="off")
                    eval_mode_changed = True
                obj = s.split("_esn_ctrl")[0]
                objList.append(obj)
                keys = cmds.keyframe(s, q=True)
                cmds.cutKey(obj)
                firstKey = cmds.findKeyframe(s, which="first")
                cmds.setKeyframe(obj, t=(firstKey, firstKey))
                orientQuery = cmds.attributeQuery("blendOrient1", node=obj, exists=True)
                if orientQuery:
                    cmds.setAttr(obj + ".blendOrient1", 1)
                else:
                    parentQuery = cmds.attributeQuery("blendParent1", node=obj, exists=True)
                    if parentQuery:
                        cmds.setAttr(obj + ".blendParent1", 1)
                if keys:
                    keys = builtins.list(builtins.set(keys))
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.setKeyframe(obj)
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
                cmds.evaluationManager(mode=original_eval_mode[0])
            except:
                pass
    
    sel = cmds.ls(sl=True)
    if builtins.len(sel) == 0:
        sys.exit()
    
    # Main creation logic
    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.refresh(suspend=True)
    refresh_suspended = True
    cmds.evaluationManager(mode="off")
    eval_mode_changed = True
    cmds.waitCursor(state=True)
    
    try:
        selection = cmds.ls(sl=True)
        nullList = []
        
        for sel_obj in selection:
            CBsel = cmds.channelBox("mainChannelBox", q=True, sma=True)
            null = cmds.spaceLocator(n=sel_obj + "_esn_ctrl")
            roo = cmds.xform(sel_obj, q=True, roo=True)
            cmds.xform(null, rotateOrder=roo)
            cmds.setAttr(".sx", keyable=False, channelBox=False)
            cmds.setAttr(".sy", keyable=False, channelBox=False)
            cmds.setAttr(".sz", keyable=False, channelBox=False)
            cmds.setAttr(".v", keyable=False, channelBox=False)
            cmds.setAttr(".overrideEnabled", 1)
            cmds.setAttr(".overrideColor", 18)
            cmds.setAttr('.useOutlinerColor', True)
            cmds.setAttr(".outlinerColor", 1, 0.5, 0.5)
            nullList.append(null[0])
            
            # Bake locator from object animation
            esn_alignObjects(null[0], sel_obj)
            
            # Constrain based on channel box selection
            if CBsel:
                if CBsel == ['rx']:
                    cmds.orientConstraint(null, sel_obj, sk=("y", "z"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('ry', 'rz'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ry", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rz", keyable=False, channelBox=False, lock=True)
                elif CBsel == ['ry']:
                    cmds.orientConstraint(null, sel_obj, sk=("x", "z"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('rx', 'rz'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rz", keyable=False, channelBox=False, lock=True)
                elif CBsel == ['rz']:
                    cmds.orientConstraint(null, sel_obj, sk=("y", "x"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('ry', 'rx'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ry", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rx", keyable=False, channelBox=False, lock=True)
                elif CBsel == ['rx', 'ry']:
                    cmds.orientConstraint(null, sel_obj, sk=("z"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('rz'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rz", keyable=False, channelBox=False, lock=True)
                elif CBsel == ['rx', 'rz']:
                    cmds.orientConstraint(null, sel_obj, sk=("y"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('ry'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ry", keyable=False, channelBox=False, lock=True)
                elif CBsel == ['ry', 'rz']:
                    cmds.orientConstraint(null, sel_obj, sk=("x"))
                    cmds.pointConstraint(sel_obj, null)
                    cmds.cutKey(null[0], at=('rx'))
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".rx", keyable=False, channelBox=False, lock=True)
                else:
                    cmds.orientConstraint(null, sel_obj)
                    cmds.pointConstraint(sel_obj, null)
                    cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                    cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
            else:
                cmds.orientConstraint(null, sel_obj)
                cmds.pointConstraint(sel_obj, null)
                cmds.setAttr(null[0] + ".tx", keyable=False, channelBox=False, lock=True)
                cmds.setAttr(null[0] + ".ty", keyable=False, channelBox=False, lock=True)
                cmds.setAttr(null[0] + ".tz", keyable=False, channelBox=False, lock=True)
        
        cmds.select(nullList)
        add_to_esn_ctrls_set(nullList)
        cmds.filterCurve()
        cmds.selectKey(cl=True)
        
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
    cmds.modelEditor(Panel, e=True, locators=True)


if __name__ == "__main__":
    orient_main()
