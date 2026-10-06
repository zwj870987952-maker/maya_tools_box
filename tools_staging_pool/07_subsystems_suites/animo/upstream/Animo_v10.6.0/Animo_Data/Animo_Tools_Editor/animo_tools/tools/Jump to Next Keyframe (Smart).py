import maya.cmds as cmds
import maya.mel as mel

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

max = builtins.max
min = builtins.min


def is_mouse_in_graph_editor():
    panel = cmds.getPanel(underPointer=True)
    if not panel:
        return False
    panel_type = cmds.getPanel(typeOf=panel)
    if panel_type == "scriptedPanel":
        if cmds.scriptedPanel(panel, query=True, type=True) == "graphEditor":
            return True
    return False


def jump_to_next_keyframe():
    selected_keys = cmds.keyframe(q=True, selected=True) if is_mouse_in_graph_editor() else None

    if not selected_keys:
        mel.eval('NextKey;')
        return

    curve_names = cmds.keyframe(q=True, selected=True, name=True)

    if not curve_names:
        mel.eval('NextKey;')
        return

    key_time = max(selected_keys)
    current_time = cmds.currentTime(q=True)

    if current_time != key_time:
        cmds.currentTime(key_time)
        return

    first_key = cmds.findKeyframe(curve_names, which="first")
    last_key = cmds.findKeyframe(curve_names, which="last")

    if current_time == last_key:
        target_key = first_key
    else:
        target_key = cmds.findKeyframe(curve_names, which="next")

    cmds.currentTime(target_key)
    cmds.selectKey(curve_names, t=(target_key, target_key))


jump_to_next_keyframe()
