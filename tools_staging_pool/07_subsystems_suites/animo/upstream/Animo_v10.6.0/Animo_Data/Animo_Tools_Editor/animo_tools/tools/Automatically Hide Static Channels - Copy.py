import maya.cmds as cmds
from functools import partial

_seen_graph_editor_panels = set()


def _is_static_curve(curve):
    values = cmds.keyframe(curve, query=True, valueChange=True)
    if not values:
        return True
    return min(values) == max(values)


def _hide_static_channels(panel):
    selection = cmds.ls(selection=True)

    if not selection:
        return

    animated_plugs = []

    for obj in selection:
        curves = cmds.keyframe(obj, query=True, name=True) or []
        for curve in curves:
            if _is_static_curve(curve):
                continue
            plugs = cmds.listConnections(curve, source=False, destination=True, plugs=True) or []
            animated_plugs.extend(plugs)

    if not animated_plugs:
        return

    outliner_connection = panel + "FromOutliner"
    editor = panel + "GraphEd"

    cmds.selectionConnection(outliner_connection, edit=True, clear=True)
    for plug in animated_plugs:
        cmds.selectionConnection(outliner_connection, edit=True, select=plug)

    cmds.animCurveEditor(editor, edit=True, lockMainConnection=True)


def _watch_for_graph_editor(*args):
    current_panels = set(cmds.getPanel(scriptType="graphEditor") or [])

    closed_panels = _seen_graph_editor_panels - current_panels
    for panel in closed_panels:
        _seen_graph_editor_panels.discard(panel)

    new_panels = current_panels - _seen_graph_editor_panels

    if new_panels:
        _seen_graph_editor_panels.update(new_panels)
        for panel in new_panels:
            cmds.evalDeferred(partial(_hide_static_channels, panel))


def toggle_static_channel_watcher():
    if cmds.optionVar(exists="hideStaticChannelsJob"):
        job_num = cmds.optionVar(query="hideStaticChannelsJob")
        if cmds.scriptJob(exists=job_num):
            cmds.scriptJob(kill=job_num, force=True)
        cmds.optionVar(remove="hideStaticChannelsJob")

        for panel in cmds.getPanel(scriptType="graphEditor") or []:
            editor = panel + "GraphEd"
            if cmds.animCurveEditor(editor, exists=True):
                cmds.animCurveEditor(editor, edit=True, unlockMainConnection=True)

        cmds.inViewMessage(
            msg="Hide Static Channels: Off",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    job_num = cmds.scriptJob(event=["idleHigh", _watch_for_graph_editor], protected=True)
    cmds.optionVar(intValue=("hideStaticChannelsJob", job_num))
    cmds.inViewMessage(
        msg="Hide Static Channels: On",
        pos="midCenter",
        fade=True,
        fontSize=14,
        textColor=(0.6, 0.6, 0.6),
        fadeStayTime=800
    )


toggle_static_channel_watcher()