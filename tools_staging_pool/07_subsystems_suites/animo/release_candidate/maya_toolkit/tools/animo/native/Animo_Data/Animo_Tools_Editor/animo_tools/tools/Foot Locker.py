from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
from maya import mel


TRANSLATE_ROTATE_ATTRS = ("tx", "ty", "tz", "rx", "ry", "rz")

LONG_TO_SHORT_ATTR = {
    "translateX": "tx",
    "translateY": "ty",
    "translateZ": "tz",
    "rotateX": "rx",
    "rotateY": "ry",
    "rotateZ": "rz",
}

MAX_XFORM_PASSES = 6
XFORM_MATCH_TOLERANCE = 1e-5


def get_timeline_range():
    playback_slider = mel.eval('$tmp=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(time_range[0])
    end = int(time_range[1]) - 1
    if end > start:
        return start, end
    return None


def get_selected_channels():
    if not cmds.channelBox("mainChannelBox", exists=True):
        return None
    selected = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True)
    if not selected:
        return None
    short_attrs = []
    for attr in selected:
        short = LONG_TO_SHORT_ATTR.get(attr)
        if short:
            short_attrs.append(short)
    return short_attrs if short_attrs else None


def get_long_name(obj):
    long = cmds.ls(obj, long=True)
    return long[0] if long else obj


def sort_by_hierarchy(objects):
    return sorted(objects, key=lambda obj: obj.count("|"))


def _matrices_match(matrix_a, matrix_b, tolerance=XFORM_MATCH_TOLERANCE):
    for value_a, value_b in zip(matrix_a, matrix_b):
        if abs(value_a - value_b) > tolerance:
            return False
    return True


def capture_source_matrices(objects):
    matrices = {}
    for obj in objects:
        matrices[obj] = cmds.xform(obj, query=True, worldSpace=True, matrix=True)
    return matrices


def apply_matrices_converged(objects, source_matrices):
    for _ in range(MAX_XFORM_PASSES):
        settled = True
        for obj in objects:
            target_matrix = source_matrices[obj]
            current_matrix = cmds.xform(obj, query=True, worldSpace=True, matrix=True)
            if _matrices_match(current_matrix, target_matrix):
                continue
            cmds.xform(obj, worldSpace=True, matrix=target_matrix)
            settled = False
        if settled:
            break


def apply_locked_channels(objects, source_matrices, allowed_channels):
    preserved_values = {}
    for obj in objects:
        preserved_values[obj] = {}
        for attr in TRANSLATE_ROTATE_ATTRS:
            if attr not in allowed_channels:
                try:
                    preserved_values[obj][attr] = cmds.getAttr(obj + "." + attr)
                except Exception:
                    pass

    apply_matrices_converged(objects, source_matrices)

    for obj in objects:
        for attr, value in preserved_values[obj].items():
            try:
                cmds.setAttr(obj + "." + attr, value)
            except Exception:
                pass


def key_channels(obj, allowed_channels, frame):
    try:
        cmds.setKeyframe(obj, attribute=allowed_channels, time=frame)
    except Exception:
        pass


def foot_locker():
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        return

    timeline_range = get_timeline_range()

    if not timeline_range:
        cmds.inViewMessage(
            amg='<span style="color:#ffffff;">Please select a range in the timeline.</span>',
            pos='midCenter',
            fade=True
        )
        return

    start_frame, end_frame = timeline_range

    objects = sort_by_hierarchy([get_long_name(obj) for obj in selection])

    allowed_channels = get_selected_channels()
    if not allowed_channels:
        allowed_channels = list(TRANSLATE_ROTATE_ATTRS)

    source_matrices = capture_source_matrices(objects)

    current_time = cmds.currentTime(query=True)

    cmds.undoInfo(openChunk=True, chunkName="Foot Locker")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)

    try:
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame)

            if len(allowed_channels) == len(TRANSLATE_ROTATE_ATTRS):
                apply_matrices_converged(objects, source_matrices)
            else:
                apply_locked_channels(objects, source_matrices, allowed_channels)

            for obj in objects:
                key_channels(obj, allowed_channels, frame)

    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


foot_locker()