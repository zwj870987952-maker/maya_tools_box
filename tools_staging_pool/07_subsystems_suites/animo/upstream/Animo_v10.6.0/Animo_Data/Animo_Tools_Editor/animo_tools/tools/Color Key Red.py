import maya.cmds as cmds
import maya.mel as mel


def color_key_red():
    existing_selection = cmds.keyframe(query=True, selected=True)

    if existing_selection:
        cmds.keyframe(edit=True, breakdown=False)
        cmds.keyframe(edit=True, tickDrawSpecial=False)
        return

    selection = cmds.ls(selection=True)
    if not selection:
        return

    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start_time = time_range[0]
    end_time = time_range[1]

    if end_time - start_time <= 1:
        current_time = cmds.currentTime(query=True)
        start_time = current_time
        end_time = current_time

    cmds.selectKey(clear=True)
    cmds.selectKey(selection, add=True, keyframe=True, time=(start_time, end_time))
    cmds.keyframe(edit=True, breakdown=False)
    cmds.keyframe(edit=True, tickDrawSpecial=False)
    cmds.selectKey(clear=True)


color_key_red()