import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import json


MARK_COLOR = "#FF0000"
MARK_OPACITY = 0.12

_previous_channel_box_selection = None


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except Exception:
        return "unknown"


def load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")

    v = get_maya_version()
    n = "mark_frame"
    py = os.path.join(folder, n + ".py")
    pyc = os.path.join(folder, "{}_py{}.pyc".format(n, v))

    if not os.path.exists(py) and not os.path.exists(pyc):
        return None

    if folder not in sys.path:
        sys.path.insert(0, folder)

    if n in sys.modules:
        return sys.modules[n]

    try:
        import importlib
        return importlib.import_module(n)
    except Exception:
        return None


def get_state_file_path():
    folder = os.path.join(cmds.internalVar(userAppDir=True), "Animo_Data")

    if not os.path.exists(folder):
        os.makedirs(folder)

    return os.path.join(folder, "Animo_ChannelBox_Selection_Mode.json")


def load_state():
    path = get_state_file_path()

    if not os.path.exists(path):
        return False

    try:
        with open(path, "r") as state_file:
            data = json.load(state_file)
        return bool(data.get("enabled", False))
    except (IOError, ValueError):
        return False


def save_state(enabled):
    path = get_state_file_path()

    with open(path, "w") as state_file:
        json.dump({"enabled": enabled}, state_file)


def get_channel_box_selection():
    if not cmds.ls(selection=True):
        return []

    channel_box = mel.eval("$temp=$gChannelBoxName")

    main_attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
    shape_attrs = cmds.channelBox(channel_box, query=True, selectedShapeAttributes=True) or []
    history_attrs = cmds.channelBox(channel_box, query=True, selectedHistoryAttributes=True) or []

    return main_attrs + shape_attrs + history_attrs


def mark_timeline_red():
    marker_module = load_marker_module()

    if not marker_module:
        return

    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    marker_module.mark_range(int(start), int(end), auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
    cmds.refresh(force=True)


def clear_timeline_color():
    marker_module = load_marker_module()

    if not marker_module:
        return

    marker_module.trigger_fade(delay=0)


def _watch_channel_box_selection(*args):
    global _previous_channel_box_selection

    current_selection = get_channel_box_selection()
    has_selection_now = bool(current_selection)
    had_selection_before = bool(_previous_channel_box_selection)

    if has_selection_now and not had_selection_before:
        mark_timeline_red()
    elif not has_selection_now and had_selection_before:
        clear_timeline_color()

    _previous_channel_box_selection = current_selection


def start_channel_box_selection_mode():
    global _previous_channel_box_selection

    if cmds.optionVar(exists="animoChannelBoxSelectionJob"):
        job_num = cmds.optionVar(query="animoChannelBoxSelectionJob")
        if cmds.scriptJob(exists=job_num):
            cmds.scriptJob(kill=job_num, force=True)
        cmds.optionVar(remove="animoChannelBoxSelectionJob")

    _previous_channel_box_selection = None

    job_num = cmds.scriptJob(event=["idleHigh", _watch_channel_box_selection], protected=True)
    cmds.optionVar(intValue=("animoChannelBoxSelectionJob", job_num))


def stop_channel_box_selection_mode():
    if cmds.optionVar(exists="animoChannelBoxSelectionJob"):
        job_num = cmds.optionVar(query="animoChannelBoxSelectionJob")
        if cmds.scriptJob(exists=job_num):
            cmds.scriptJob(kill=job_num, force=True)
        cmds.optionVar(remove="animoChannelBoxSelectionJob")

    clear_timeline_color()


def toggle_channel_box_selection_mode():
    new_state = not load_state()
    save_state(new_state)

    if new_state:
        start_channel_box_selection_mode()
        cmds.inViewMessage(
            msg="ChannelBox Selection Mode: On",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
    else:
        stop_channel_box_selection_mode()
        cmds.inViewMessage(
            msg="ChannelBox Selection Mode: Off",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )


toggle_channel_box_selection_mode()