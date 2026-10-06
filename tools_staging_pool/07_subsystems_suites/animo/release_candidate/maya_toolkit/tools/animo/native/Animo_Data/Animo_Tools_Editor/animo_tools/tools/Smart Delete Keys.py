import maya.cmds as cmds
import maya.mel as mel


def smart_delete_keys():
    panel = cmds.getPanel(underPointer=True)
    is_graph_editor = False

    if panel:
        if 'graphEditor' in panel:
            is_graph_editor = True
        else:
            try:
                panel_type = cmds.getPanel(typeOf=panel)
                if panel_type == 'scriptedPanel':
                    scripted_type = cmds.scriptedPanel(panel, query=True, type=True)
                    if scripted_type == 'graphEditor':
                        is_graph_editor = True
            except RuntimeError:
                is_graph_editor = False

    selected_curves = cmds.keyframe(query=True, selected=True, name=True)

    if is_graph_editor and selected_curves:
        for curve in selected_curves:
            indices = cmds.keyframe(curve, query=True, selected=True, indexValue=True) or []
            for index in sorted(indices, reverse=True):
                cmds.cutKey(curve, index=(index, index), clear=True)
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
        cmds.cutKey(selection, time=(current_time, current_time), clear=True)
    else:
        cmds.cutKey(selection, time=(start_time, end_time), clear=True)


smart_delete_keys()