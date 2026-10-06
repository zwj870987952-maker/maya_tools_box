import maya.cmds as cmds
from functools import partial

_seen_graph_editor_panels = set()


def _is_static_curve(curve):
    values = cmds.keyframe(curve, query=True, valueChange=True)
    if not values:
        return True
    return min(values) == max(values)


def _hide_static_channels(panel):
    editor = panel + "GraphEd"
    outliner_connection = panel + "FromOutliner"

    if not cmds.animCurveEditor(editor, exists=True):
        return

    cmds.animCurveEditor(editor, edit=True, unlockMainConnection=True)

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

    cmds.selectionConnection(outliner_connection, edit=True, clear=True)
    for plug in animated_plugs:
        cmds.selectionConnection(outliner_connection, edit=True, select=plug)

    cmds.animCurveEditor(editor, edit=True, lockMainConnection=True)


def _panel_is_visible(panel):
    try:
        control = cmds.panel(panel, query=True, control=True)
    except RuntimeError:
        return False

    if not control or not cmds.control(control, exists=True):
        return False

    return cmds.control(control, query=True, visible=True)


def _watch_for_graph_editor(*args):
    all_panels = cmds.getPanel(scriptType="graphEditor") or []
    visible_panels = set(panel for panel in all_panels if _panel_is_visible(panel))

    no_longer_visible = _seen_graph_editor_panels - visible_panels
    for panel in no_longer_visible:
        _seen_graph_editor_panels.discard(panel)

    newly_visible = visible_panels - _seen_graph_editor_panels

    if newly_visible:
        _seen_graph_editor_panels.update(newly_visible)
        for panel in newly_visible:
            cmds.evalDeferred(partial(_hide_static_channels, panel))


def _refilter_visible_panels(*args):
    for panel in cmds.getPanel(scriptType="graphEditor") or []:
        if _panel_is_visible(panel):
            _hide_static_channels(panel)


def toggle_static_channel_watcher():
    if cmds.optionVar(exists="hideStaticChannelsJob"):
        job_num = cmds.optionVar(query="hideStaticChannelsJob")
        if cmds.scriptJob(exists=job_num):
            cmds.scriptJob(kill=job_num, force=True)
        cmds.optionVar(remove="hideStaticChannelsJob")

        sel_job_num = cmds.optionVar(query="hideStaticChannelsSelectionJob") if cmds.optionVar(exists="hideStaticChannelsSelectionJob") else None
        if sel_job_num is not None and cmds.scriptJob(exists=sel_job_num):
            cmds.scriptJob(kill=sel_job_num, force=True)
        if cmds.optionVar(exists="hideStaticChannelsSelectionJob"):
            cmds.optionVar(remove="hideStaticChannelsSelectionJob")

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

    sel_job_num = cmds.scriptJob(event=["SelectionChanged", _refilter_visible_panels], protected=True)
    cmds.optionVar(intValue=("hideStaticChannelsSelectionJob", sel_job_num))

    cmds.inViewMessage(
        msg="Hide Static Channels: On",
        pos="midCenter",
        fade=True,
        fontSize=14,
        textColor=(0.6, 0.6, 0.6),
        fadeStayTime=800
    )


toggle_static_channel_watcher()