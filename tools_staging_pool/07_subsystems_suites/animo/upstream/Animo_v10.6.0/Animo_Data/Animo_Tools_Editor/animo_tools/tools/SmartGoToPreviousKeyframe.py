import maya.cmds as cmds
import maya.mel as mel

def smart_go_to_previous_keyframe():
    graph_sel = cmds.keyframe(q=True, selected=True)
    
    if graph_sel:
        curve_name = cmds.keyframe(q=True, name=True)
        key_time = cmds.keyframe(q=True)[0]
        cur_time = cmds.currentTime(q=True)
        
        if cur_time != key_time:
            cmds.currentTime(key_time)
        else:
            prev_key = cmds.findKeyframe(which="previous")
            last_key = cmds.findKeyframe(which="last")
            first_key = cmds.findKeyframe(which="first")
            if cur_time == first_key:
                cmds.currentTime(last_key)
                cmds.selectKey(curve_name, t=(last_key, last_key))
            else:
                cmds.currentTime(prev_key)
                cmds.selectKey(curve_name, t=(prev_key, prev_key))
    else:
        mel.eval('PreviousKey;')

smart_go_to_previous_keyframe()
