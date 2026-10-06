import maya.cmds as cmds


def get_selected_graph_curves():
    return list(set(cmds.keyframe(query=True, name=True, selected=True) or []))


def get_selected_channel_box_attrs():
    return cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True) or []


def get_hierarchy_from_selection():
    selection = cmds.ls(selection=True, long=True, type="transform")
    if not selection:
        return []
    hierarchy, visited = [], set()

    def walk(node):
        if node in visited:
            return
        visited.add(node)
        hierarchy.append(node)
        children = cmds.listRelatives(node, c=True, type='transform', f=True) or []
        for child in children:
            walk(child)

    for root in selection:
        walk(root)
    return hierarchy


def get_curves_from_attrs(objects, attrs):
    curves = []
    for obj in objects:
        for attr in attrs:
            full_attr = f"{obj}.{attr}"
            if cmds.objExists(full_attr):
                connected = cmds.listConnections(full_attr, type='animCurve', s=True, d=False) or []
                curves.extend(connected)
    return list(set(curves))


def get_animated_attrs(obj):
    attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
    animated = []
    for attr in attrs:
        full_attr = f"{obj}.{attr}"
        if cmds.listConnections(full_attr, type='animCurve', s=True, d=False):
            animated.append(attr)
    return animated


def get_all_curves_from_hierarchy(objects):
    curves = []
    for obj in objects:
        for attr in get_animated_attrs(obj):
            full_attr = f"{obj}.{attr}"
            connected = cmds.listConnections(full_attr, type='animCurve', s=True, d=False) or []
            curves.extend(connected)
    return list(set(curves))


def get_left_pivot_value(curve, first_time):
    prev_time = cmds.findKeyframe(curve, time=(first_time, first_time), which='previous')
    if prev_time is not None and prev_time != first_time:
        return cmds.keyframe(curve, query=True, time=(prev_time, prev_time), valueChange=True)[0]
    return cmds.keyframe(curve, query=True, time=(first_time, first_time), valueChange=True)[0]


def scale_curves_full_range(curves, start_scale=1.0, step=0.1):
    current_scale = start_scale
    for curve in curves:
        try:
            start = cmds.findKeyframe(curve, which='first')
            end = cmds.findKeyframe(curve, which='last')
            pivot_value = get_left_pivot_value(curve, start)
            cmds.scaleKey(curve, time=(start, end), valuePivot=pivot_value, valueScale=current_scale)
        except Exception:
            pass
        current_scale += step


def scale_curves_selected_keys(curves, start_scale=1.0, step=0.1):
    current_scale = start_scale
    for curve in curves:
        selected_times = sorted(cmds.keyframe(curve, query=True, selected=True, timeChange=True) or [])
        if not selected_times:
            continue
        pivot_value = get_left_pivot_value(curve, selected_times[0])
        time_ranges = [(t, t) for t in selected_times]
        try:
            cmds.scaleKey(curve, time=time_ranges, valuePivot=pivot_value, valueScale=current_scale)
        except Exception:
            pass
        current_scale += step


def scale_sequentially(start_scale=1.0, step=0.1):
    graph_curves = get_selected_graph_curves()

    if graph_curves:
        scale_curves_selected_keys(graph_curves, start_scale, step)
        return

    hierarchy = get_hierarchy_from_selection()
    if not hierarchy:
        cmds.warning("No transform objects selected.")
        return

    attrs = get_selected_channel_box_attrs()
    if attrs:
        curves = get_curves_from_attrs(hierarchy, attrs)
    else:
        curves = get_all_curves_from_hierarchy(hierarchy)

    if not curves:
        cmds.warning("No animation curves found.")
        return

    scale_curves_full_range(curves, start_scale, step)


scale_sequentially(start_scale=1.0, step=0.1)