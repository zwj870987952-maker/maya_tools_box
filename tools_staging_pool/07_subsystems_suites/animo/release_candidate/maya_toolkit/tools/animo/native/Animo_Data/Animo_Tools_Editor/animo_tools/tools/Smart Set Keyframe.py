import maya.cmds as cmds


def smart_set_keyframe():
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

    current_time = cmds.currentTime(query=True)

    def has_existing_keys(node, attrs=None):
        try:
            if attrs:
                counts = cmds.keyframe(node, attribute=attrs, query=True, keyframeCount=True)
            else:
                counts = cmds.keyframe(node, query=True, keyframeCount=True)
        except RuntimeError:
            return False
        if not counts:
            return False
        if isinstance(counts, list):
            return any(c > 0 for c in counts)
        return counts > 0

    if is_graph_editor:
        curve_names = cmds.keyframe(query=True, name=True)
        key_selected = cmds.keyframe(query=True, selected=True)

        if curve_names:
            cmds.setKeyframe(curve_names, insert=True)
            if key_selected:
                cmds.selectKey(curve_names, time=(current_time, current_time))

        for node in cmds.ls(selection=True):
            if not has_existing_keys(node):
                cmds.setKeyframe(node)
        return

    channel_box_attrs = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    selection = cmds.ls(selection=True)

    for node in selection:
        if channel_box_attrs:
            if has_existing_keys(node, channel_box_attrs):
                cmds.setKeyframe(node, attribute=channel_box_attrs, insert=True)
            else:
                cmds.setKeyframe(node, attribute=channel_box_attrs)
        else:
            if has_existing_keys(node):
                cmds.setKeyframe(node, insert=True)
            else:
                cmds.setKeyframe(node)


smart_set_keyframe()