import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import json
import builtins

try:
    max = builtins.max
    min = builtins.min
    int = builtins.int
except Exception:
    pass

MARK_COLOR = "#FFA500"
MARK_OPACITY = 0.25


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except Exception:
        return "unknown"


def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        return cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True)
    except Exception:
        return False


def resolve_curve_target_plug(item):
    if "." in item:
        node, incoming_attr = item.split(".", 1)
    else:
        node, incoming_attr = item, None
    visited = set()
    for _ in range(30):
        if node in visited:
            return None
        visited.add(node)

        pairs = cmds.listConnections(node, source=False, destination=True, plugs=True, connections=True) or []
        candidates = []
        for i in range(0, len(pairs), 2):
            src_plug = pairs[i]
            dst_plug = pairs[i + 1]
            src_attr = src_plug.split(".", 1)[-1]
            base_attr = src_attr.split("[")[0]
            if base_attr.startswith("output"):
                candidates.append((base_attr, dst_plug))

        if not candidates:
            return None

        next_plug = None
        if incoming_attr is not None:
            suffix = incoming_attr
            if suffix.startswith("input"):
                suffix = suffix[len("input"):]
            if suffix[:1] in ("A", "B"):
                suffix = suffix[1:]
            wanted = "output" + suffix
            for base_attr, dst_plug in candidates:
                if base_attr == wanted:
                    next_plug = dst_plug
                    break

        if next_plug is None:
            next_plug = candidates[0][1]

        next_node = next_plug.split(".")[0]
        try:
            next_node_type = cmds.nodeType(next_node)
        except Exception:
            return None
        if next_node_type.startswith("animBlendNode") or next_node_type == "unitConversion":
            incoming_attr = next_plug.split(".", 1)[-1]
            node = next_node
            continue
        return next_plug
    return None


def is_mouse_over_graph_editor():
    try:
        panel = cmds.getPanel(underPointer=True)
        return bool(panel and 'graphEditor' in panel)
    except Exception:
        return False


def get_timeline_path():
    return mel.eval("$tmpVar=$gPlayBackSlider")


def get_selected_range():
    timeline_path = get_timeline_path()
    range_visible = cmds.timeControl(timeline_path, query=True, rangeVisible=True)
    if range_visible:
        range_array = cmds.timeControl(timeline_path, query=True, rangeArray=True)
        start_frame = int(range_array[0])
        end_frame = int(range_array[1]) - 1
        if end_frame > start_frame:
            return (start_frame, end_frame)
    return None


def find_animo_data_root(start_path):
    path = start_path
    while True:
        if os.path.basename(path) == "Animo_Data":
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def load_marker_module():
    try:
        script_folder = os.path.dirname(os.path.abspath(__file__))
        animo_data_root = find_animo_data_root(script_folder)
        if animo_data_root:
            marker_folder = os.path.join(animo_data_root, "Animo_Keys_Tangent")
        else:
            marker_folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")
    except NameError:
        marker_folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")

    v = get_maya_version()
    n = "mark_frame"
    py = os.path.join(marker_folder, n + ".py")
    pyc = os.path.join(marker_folder, "{}_py{}.pyc".format(n, v))

    if not os.path.exists(py) and not os.path.exists(pyc):
        return None

    if marker_folder not in sys.path:
        sys.path.insert(0, marker_folder)

    if n in sys.modules:
        del sys.modules[n]

    try:
        import importlib
        return importlib.import_module(n)
    except Exception:
        return None


def get_clipboard_path():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        animo_data_path = os.path.normpath(os.path.join(folder, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        animo_data_path = os.path.join(script_dir, "Animo_Data")

    clipboard_dir = os.path.join(animo_data_path, "Animo_Keys_Clipboard")
    if not os.path.exists(clipboard_dir):
        try:
            os.makedirs(clipboard_dir)
        except Exception:
            pass
    return os.path.join(clipboard_dir, "keys_clipboard.json")


# ---------------------------------------------------------------------------
# Anim layer caching. Everything here is computed at most ONCE per copy run
# (previously several helpers re-queried Maya per object/per attribute,
# which is what made anything touching anim layers crawl).
# ---------------------------------------------------------------------------
_layer_cache = {"root": "unset", "layer_attrs": {}, "layers": None}


def get_cached_root_layer():
    if _layer_cache["root"] == "unset":
        try:
            _layer_cache["root"] = cmds.animLayer(query=True, root=True)
        except Exception:
            _layer_cache["root"] = None
    return _layer_cache["root"]


def get_cached_layers():
    if _layer_cache["layers"] is None:
        _layer_cache["layers"] = cmds.ls(type="animLayer") or []
    return _layer_cache["layers"]


def get_cached_layer_attrs(layer):
    layer_attrs = _layer_cache["layer_attrs"]
    if layer not in layer_attrs:
        try:
            layer_attrs[layer] = cmds.animLayer(layer, query=True, attribute=True) or []
        except Exception:
            layer_attrs[layer] = []
    return layer_attrs[layer]


def find_layer_plug_for_attr(obj_name, layer, attr):
    if not layer:
        return None
    for plug in get_cached_layer_attrs(layer):
        node = plug.split('.')[0]
        if node == obj_name:
            if plug.split('.', 1)[-1] == attr:
                return plug
            continue
        try:
            long_names = cmds.ls(node, long=True) or []
        except Exception:
            long_names = []
        if obj_name in long_names and plug.split('.', 1)[-1] == attr:
            return plug
    return None


def get_layer_curve_for_plug(layer, plug):
    if not layer:
        return None
    try:
        curve = cmds.animLayer(layer, query=True, findCurveForPlug=plug)
    except Exception:
        return None
    if not curve:
        return None
    return curve[0] if isinstance(curve, list) else curve


def resolve_curve_for_object_attr(obj, attr):
    root_layer = get_cached_root_layer()

    for layer in get_cached_layers():
        if layer == root_layer:
            continue
        matched_plug = find_layer_plug_for_attr(obj, layer, attr)
        if matched_plug:
            curve = get_layer_curve_for_plug(layer, matched_plug)
            if curve:
                return curve

    if root_layer:
        matched_plug = find_layer_plug_for_attr(obj, root_layer, attr)
        if matched_plug:
            curve = get_layer_curve_for_plug(root_layer, matched_plug)
            if curve:
                return curve

    plug = obj + "." + attr
    conns = cmds.listConnections(plug, source=True, destination=False, type="animCurve", skipConversionNodes=True) or []
    return conns[0] if conns else None


def find_layer_owning_curve(obj, attr, curve):
    for layer in get_cached_layers():
        matched_plug = find_layer_plug_for_attr(obj, layer, attr)
        if matched_plug:
            layer_curve = get_layer_curve_for_plug(layer, matched_plug)
            if layer_curve == curve:
                return layer
    return None


def is_curve_weighted(curve):
    if not curve:
        return False
    try:
        result = cmds.keyTangent(curve, query=True, weightedTangents=True)
        if result:
            return bool(result[0])
    except Exception:
        pass
    return False


def get_tangent_at_time(curve, t):
    if not curve:
        return "auto", "auto"
    key_times = cmds.keyframe(curve, query=True, time=(t, t)) or []
    if not key_times:
        return "auto", "auto"
    itt = cmds.keyTangent(curve, time=(t, t), query=True, inTangentType=True)
    ott = cmds.keyTangent(curve, time=(t, t), query=True, outTangentType=True)
    return (itt[0] if itt else "auto"), (ott[0] if ott else "auto")


def get_curve_keyframes(curve, start, end, weighted):
    """Reads every key in [start, end] with ONE batched query per data field
    instead of separate queries per key (the old code issued 4+ cmds calls
    PER KEY, which is brutally slow on long ranges)."""
    if not curve:
        return []

    times = cmds.keyframe(curve, query=True, time=(start, end)) or []
    if not times:
        return []

    values = cmds.keyframe(curve, query=True, time=(start, end), valueChange=True) or []
    itts = cmds.keyTangent(curve, query=True, time=(start, end), inTangentType=True) or []
    otts = cmds.keyTangent(curve, query=True, time=(start, end), outTangentType=True) or []

    need_weight_info = weighted or any(t == "fixed" for t in itts) or any(t == "fixed" for t in otts)
    if need_weight_info:
        in_angles = cmds.keyTangent(curve, query=True, time=(start, end), inAngle=True) or []
        out_angles = cmds.keyTangent(curve, query=True, time=(start, end), outAngle=True) or []
        in_weights = cmds.keyTangent(curve, query=True, time=(start, end), inWeight=True) or []
        out_weights = cmds.keyTangent(curve, query=True, time=(start, end), outWeight=True) or []

    data = []
    for idx, t in enumerate(times):
        value = values[idx] if idx < len(values) else None
        if value is None:
            continue
        itt = itts[idx] if idx < len(itts) else "auto"
        ott = otts[idx] if idx < len(otts) else "auto"
        entry = {"time_offset": t - start, "value": value, "itt": itt, "ott": ott}
        if need_weight_info:
            entry["in_angle"] = in_angles[idx] if idx < len(in_angles) else None
            entry["out_angle"] = out_angles[idx] if idx < len(out_angles) else None
            entry["in_weight"] = in_weights[idx] if idx < len(in_weights) else None
            entry["out_weight"] = out_weights[idx] if idx < len(out_weights) else None
        data.append(entry)
    return data


def write_clipboard(clipboard):
    try:
        with open(get_clipboard_path(), "w") as f:
            json.dump(clipboard, f)
    except Exception:
        pass


def drop_marker(start, end):
    marker_module = load_marker_module()
    if marker_module:
        marker_module.mark_range(int(start), int(end), auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
        marker_module.trigger_fade(delay=500)


# ---------------------------------------------------------------------------
# FAST PATH: plain "copy the current pose" - no range, no key selection.
# This is the overwhelmingly common case and it should do the absolute
# minimum: read current values, done. No layer walking, no tangent
# queries, no curve resolution.
# ---------------------------------------------------------------------------
def copy_pose_fast(selected_objects):
    t = cmds.currentTime(query=True)

    anchors = {}
    for obj in selected_objects:
        attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
        if not attrs:
            continue
        obj_vals = {}
        for attr in attrs:
            try:
                value = cmds.getAttr(obj + "." + attr)
            except Exception:
                continue
            if isinstance(value, list):
                continue
            obj_vals[attr] = value
        if obj_vals:
            anchors[obj] = obj_vals

    clipboard = {
        "base_time": t,
        "span": 0.0,
        "anchors": anchors,
        "curves": {},
        "object_curves": {},
        "objects": selected_objects,
        "from_graph_editor": False,
        "pose_only": True,
    }
    write_clipboard(clipboard)

    try:
        mel.eval("timeSliderCopyKey;")
    except Exception:
        pass

    drop_marker(t, t)


def copy_keys():
    selected_objects = cmds.ls(selection=True) or []
    if not selected_objects:
        cmds.inViewMessage(amg="Please select something!", pos="midCenter", fade=True)
        return

    graph_selected_keys = cmds.keyframe(q=True, sl=True) if is_graph_editor_active() else None
    timeline_range = get_selected_range()

    if is_mouse_over_graph_editor() and graph_selected_keys:
        selected_keys = graph_selected_keys
        timeline_range = None
    elif timeline_range:
        selected_keys = None
    elif graph_selected_keys:
        selected_keys = graph_selected_keys
        timeline_range = None
    else:
        selected_keys = None

    if not selected_keys and not timeline_range:
        copy_pose_fast(selected_objects)
        return

    curves = {}
    object_curves = {}

    if selected_keys:
        try:
            mel.eval("GraphCopy;")
        except Exception:
            pass
        start = min(selected_keys)
        end = max(selected_keys)

        selected_curve_names = cmds.keyframe(q=True, sl=True, name=True) or []
        copied_attrs = set()
        curve_by_obj_attr = {}
        for curve_name in selected_curve_names:
            target_plug = resolve_curve_target_plug(curve_name)
            if target_plug and "." in target_plug:
                target_obj, target_attr = target_plug.split(".", 1)
                copied_attrs.add(target_attr)
                curve_by_obj_attr[(target_obj, target_attr)] = curve_name

        for obj in selected_objects:
            for attr in copied_attrs:
                plug = obj + "." + attr
                if not cmds.objExists(plug):
                    continue
                curve = curve_by_obj_attr.get((obj, attr))
                if not curve or not cmds.objExists(curve):
                    curve = resolve_curve_for_object_attr(obj, attr)
                if not curve:
                    continue
                is_weighted = is_curve_weighted(curve)
                curve_keys = get_curve_keyframes(curve, start, end, is_weighted)
                source_layer = find_layer_owning_curve(obj, attr, curve)
                if not curve_keys:
                    continue
                curve_data = {"weighted": is_weighted, "keys": curve_keys, "_source_obj": obj, "_source_attr": attr, "source_layer": source_layer}
                object_curves.setdefault(obj, {})[attr] = curve_data
                if attr not in curves:
                    curves[attr] = curve_data
    else:
        try:
            mel.eval("timeSliderCopyKey;")
        except Exception:
            pass
        start, end = timeline_range

        copied_attrs = set()
        for obj in selected_objects:
            attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
            for attr in attrs:
                plug = obj + "." + attr
                if not cmds.objExists(plug):
                    continue
                curve = resolve_curve_for_object_attr(obj, attr)
                if not curve:
                    continue
                key_times = cmds.keyframe(curve, q=True, time=(start, end), timeChange=True)
                if key_times:
                    copied_attrs.add(attr)

        for obj in selected_objects:
            for attr in copied_attrs:
                plug = obj + "." + attr
                if not cmds.objExists(plug):
                    continue
                curve = resolve_curve_for_object_attr(obj, attr)
                if not curve:
                    continue
                is_weighted = is_curve_weighted(curve)
                curve_keys = get_curve_keyframes(curve, start, end, is_weighted)
                source_layer = find_layer_owning_curve(obj, attr, curve)
                if not curve_keys:
                    continue
                curve_data = {"weighted": is_weighted, "keys": curve_keys, "_source_obj": obj, "_source_attr": attr, "source_layer": source_layer}
                object_curves.setdefault(obj, {})[attr] = curve_data
                if attr not in curves:
                    curves[attr] = curve_data

    anchors = {}
    for obj in selected_objects:
        attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
        for attr in attrs:
            plug = obj + "." + attr
            if not cmds.objExists(plug):
                continue
            try:
                value = cmds.getAttr(plug, time=start)
            except Exception:
                continue
            if isinstance(value, list):
                continue
            anchors.setdefault(obj, {})[attr] = value
            if not selected_keys and attr not in object_curves.get(obj, {}):
                anchor_curve = resolve_curve_for_object_attr(obj, attr)
                itt, ott = get_tangent_at_time(anchor_curve, start)
                anchor_source_layer = find_layer_owning_curve(obj, attr, anchor_curve) if anchor_curve else None
                pose_curve = {"weighted": False, "keys": [{"time_offset": 0.0, "value": value, "itt": itt, "ott": ott}], "_source_obj": obj, "_source_attr": attr, "source_layer": anchor_source_layer}
                object_curves.setdefault(obj, {})[attr] = pose_curve
                if attr not in curves:
                    curves[attr] = pose_curve

    clipboard = {"base_time": start, "span": end - start, "anchors": anchors, "curves": curves, "objects": selected_objects, "object_curves": object_curves, "from_graph_editor": bool(selected_keys)}
    write_clipboard(clipboard)
    drop_marker(start, end)


copy_keys()
