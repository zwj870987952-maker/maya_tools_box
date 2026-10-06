import maya.cmds as cmds
import maya.mel as mel

def smart_go_to_next_key():
    graph_sel = cmds.keyframe(q=True, selected=True)
    
    if graph_sel:
        curve_name = cmds.keyframe(q=True, name=True)
        key_time = cmds.keyframe(q=True)[0]
        cur_time = cmds.currentTime(q=True)
        
        if cur_time != key_time:
            cmds.currentTime(key_time)
        else:
            next_key = cmds.findKeyframe(which="next")
            last_key = cmds.findKeyframe(which="last")
            first_key = cmds.findKeyframe(which="first")
            if cur_time == last_key:
                cmds.currentTime(first_key)
                cmds.selectKey(curve_name, t=(first_key, first_key))
            else:
                cmds.currentTime(next_key)
                cmds.selectKey(curve_name, t=(next_key, next_key))
    else:
        mel.eval('NextKey;')

smart_go_to_next_key()
