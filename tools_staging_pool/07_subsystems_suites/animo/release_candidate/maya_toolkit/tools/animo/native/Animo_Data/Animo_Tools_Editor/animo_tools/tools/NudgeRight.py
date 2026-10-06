import maya.cmds as cmds
import maya.mel as mel

def nudge_right():
    t = cmds.currentTime(q=True)
    
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    playBackSlider = mel.eval("$tmpVar=$gPlayBackSlider")
    time_range = cmds.timeControl(playBackSlider, q=True, rangeArray=True)
    start = int(time_range[0])
    end = int(time_range[1]) - 1
    
    if (end - start) != 0:
        for obj in sel:
            keys_in_range = cmds.keyframe(obj, q=True, time=(start, end), timeChange=True)
            if keys_in_range:
                for key_time in reversed(keys_in_range):
                    cmds.keyframe(obj, edit=True, time=(key_time,), relative=True, timeChange=1)
        return
    
    graph_editor = "graphEditor1FromOutliner"
    if cmds.selectionConnection(graph_editor, exists=True):
        curves = cmds.selectionConnection(graph_editor, q=True, object=True)
    else:
        curves = None
    
    if curves:
        for curve in curves:
            selected_keys = cmds.keyframe(curve, q=True, selected=True, timeChange=True)
            if selected_keys:
                for key_time in reversed(selected_keys):
                    cmds.keyframe(curve, edit=True, time=(key_time,), relative=True, timeChange=1)
            else:
                if cmds.keyframe(curve, q=True, time=(t,)):
                    cmds.keyframe(curve, edit=True, time=(t,), relative=True, timeChange=1)
        cmds.currentTime(t + 1, edit=True)
        return
    
    selected_keys = cmds.keyframe(q=True, selected=True, timeChange=True)
    if selected_keys:
        for key_time in reversed(selected_keys):
            cmds.keyframe(edit=True, time=(key_time,), relative=True, timeChange=1)
        cmds.currentTime(t + 1, edit=True)
        return
    
    for obj in sel:
        if cmds.keyframe(obj, q=True, time=(t,)):
            cmds.keyframe(obj, edit=True, time=(t,), relative=True, timeChange=1)
    cmds.currentTime(t + 1, edit=True)

nudge_right()
