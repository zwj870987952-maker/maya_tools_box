import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import json
import builtins

try:
    int = builtins.int
    list = builtins.list
except Exception:
    pass

MARK_COLOR = "#FFA500"
MARK_OPACITY = 0.25


def force_rig_refresh():
    frame = cmds.currentTime(q=True)

    cmds.refresh(suspend=True)
    cmds.undoInfo(stateWithoutFlush=False)
    try:
        cmds.currentTime(frame - 0.001, edit=True, update=True)
        cmds.currentTime(frame, edit=True, update=True)
    finally:
        cmds.undoInfo(stateWithoutFlush=True)
        cmds.refresh(suspend=False)

    cmds.refresh(force=True)


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
    return os.path.join(clipboard_dir, "keys_clipboard.json")


def load_clipboard():
    path = get_clipboard_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def get_channelbox_attrs():
    try:
        channel_box = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        return cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
    except Exception:
        return []


def get_graph_editor_selected_attrs():
    try:
        items = cmds.selectionConnection('graphEditor1FromOutliner', query=True, obj=True) or []
    except Exception:
        return set()
    attrs = set()
    for item in items:
        if "." in item:
            node = item.split(".", 1)[0]
            try:
                node_type = cmds.nodeType(node)
            except Exception:
                node_type = None
            if node_type and (node_type.startswith("animBlendNode") or node_type == "unitConversion" or node_type.startswith("animCurve")):
                target_plug = resolve_curve_target_plug(item)
                if target_plug and "." in target_plug:
                    attrs.add(target_plug.split(".", 1)[1])
            else:
                attrs.add(item.split(".", 1)[-1])
        else:
            target_plug = resolve_curve_target_plug(item)
            if target_plug and "." in target_plug:
                attrs.add(target_plug.split(".", 1)[1])
    return attrs


def get_selected_key_attrs():
    if not is_graph_editor_active():
        return set()
    curves = cmds.keyframe(query=True, selected=True, name=True) or []
    attrs = set()
    for curve in curves:
        target_plug = resolve_curve_target_plug(curve)
        if target_plug and "." in target_plug:
            attrs.add(target_plug.split(".", 1)[1])
    return attrs


def resolve_source_curve(curves, target_attr, allow_single_fallback=True):
    if not curves:
        return None
    if target_attr in curves and curves[target_attr] and curves[target_attr].get("keys"):
        return curves[target_attr]
    if allow_single_fallback and len(curves) == 1:
        only_curve = list(curves.values())[0]
        if only_curve and only_curve.get("keys"):
            return only_curve
    return None


def resolve_object_curve(object_curves, copied_objects, selected_objects, index, obj, attr, curves, allow_single_fallback=True):
    if object_curves:
        if obj in object_curves and attr in object_curves[obj]:
            return object_curves[obj][attr]
        if copied_objects and len(copied_objects) == len(selected_objects) and index < len(copied_objects):
            src_obj = copied_objects[index]
            if src_obj in object_curves and attr in object_curves[src_obj]:
                return object_curves[src_obj][attr]
    return resolve_source_curve(curves, attr, allow_single_fallback)


# ---------------------------------------------------------------------------
# Anim layer caching, built once per paste run - see Smart_Paste_Keys.py for
# why this matters (uncached per-attribute animLayer queries were the main
# source of multi-minute pastes with several layers).
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


def get_current_anim_layer(root_layer):
    if not root_layer:
        return None
    try:
        selected_layers = cmds.treeView('AnimLayerTabanimLayerEditor', query=True, selectItem=True) or []
    except Exception:
        selected_layers = []
    return selected_layers[0] if selected_layers else root_layer


def resolve_destination_anim_layer(obj, attr, source_layer, source_obj=None):
    root_layer = get_cached_root_layer()

    owning_layers = []
    for layer in get_cached_layers():
        if find_layer_plug_for_attr(obj, layer, attr):
            owning_layers.append(layer)

    current_layer = get_current_anim_layer(root_layer)

    if current_layer and root_layer and current_layer == root_layer:
        return root_layer

    if current_layer in owning_layers:
        return current_layer

    if not owning_layers:
        return None

    if source_layer in owning_layers:
        return source_layer

    if source_layer is None and root_layer:
        return root_layer

    return owning_layers[0]


def resolve_written_curve(obj, attr, target_layer):
    plug = obj + "." + attr
    root_layer = get_cached_root_layer()

    if target_layer and target_layer != root_layer:
        matched_plug = find_layer_plug_for_attr(obj, target_layer, attr)
        if matched_plug:
            try:
                curve = cmds.animLayer(target_layer, query=True, findCurveForPlug=matched_plug)
            except Exception:
                curve = None
            if curve:
                return curve[0] if isinstance(curve, list) else curve
        return None

    src = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
    if not src:
        return None
    src_plug = src[0]
    src_node = src_plug.split(".")[0]
    src_attr = src_plug.split(".", 1)[-1]
    try:
        src_node_type = cmds.nodeType(src_node)
    except Exception:
        src_node_type = None

    if src_node_type and src_node_type.startswith("animBlendNode"):
        suffix = src_attr
        if suffix.startswith("output"):
            suffix = suffix[len("output"):]
        input_a_plug = src_node + ".inputA" + suffix
        if cmds.objExists(input_a_plug):
            a_src = cmds.listConnections(input_a_plug, source=True, destination=False, plugs=True) or []
            if a_src:
                a_node = a_src[0].split(".")[0]
                try:
                    a_type = cmds.nodeType(a_node)
                except Exception:
                    a_type = None
                if a_type and a_type.startswith("animCurve"):
                    return a_node
        return None

    if src_node_type and src_node_type.startswith("animCurve"):
        return src_node

    return None


def get_local_reference_value(plug, curve, target_layer, t):
    if curve:
        try:
            val = cmds.getAttr(curve + ".output", time=t)
            if not isinstance(val, list):
                return val
        except Exception:
            pass

    if target_layer is None:
        try:
            val = cmds.getAttr(plug, time=t)
            if not isinstance(val, list):
                return val
        except Exception:
            pass
        return None

    return 0.0


def apply_curve_to_plug(plug, curve_data, base_time):
    if not curve_data:
        return None
    keys = curve_data.get("keys", [])
    if not keys:
        return None

    obj, attr = plug.split(".", 1)
    source_layer = curve_data.get("source_layer")
    source_obj = curve_data.get("_source_obj")
    target_layer = resolve_destination_anim_layer(obj, attr, source_layer, source_obj)

    for entry in keys:
        t = base_time + entry.get("time_offset", 0.0)
        value = entry.get("value")
        if value is None:
            continue
        try:
            if target_layer is None:
                cmds.setKeyframe(plug, time=t, value=value)
            else:
                cmds.setKeyframe(plug, time=t, value=value, animLayer=target_layer)
        except Exception:
            continue

    written_curve = resolve_written_curve(obj, attr, target_layer)

    if target_layer is not None and written_curve:
        for entry in keys:
            t = base_time + entry.get("time_offset", 0.0)
            value = entry.get("value")
            if value is None:
                continue
            try:
                cmds.keyframe(written_curve, edit=True, time=(t, t), valueChange=value, absolute=True)
            except Exception:
                pass

    tangent_target = written_curve if written_curve else plug

    if curve_data.get("weighted"):
        try:
            cmds.keyTangent(tangent_target, edit=True, weightedTangents=True)
        except Exception:
            pass

    for entry in keys:
        t = base_time + entry.get("time_offset", 0.0)
        itt = entry.get("itt", "auto")
        ott = entry.get("ott", "auto")
        try:
            cmds.keyTangent(tangent_target, time=(t, t), edit=True, inTangentType=itt, outTangentType=ott)
        except Exception:
            pass
        if "in_angle" in entry or "out_angle" in entry:
            kwargs = {}
            for key, flag in (("in_angle", "inAngle"), ("out_angle", "outAngle"), ("in_weight", "inWeight"), ("out_weight", "outWeight")):
                v = entry.get(key)
                if v is not None:
                    kwargs[flag] = v
            if kwargs:
                try:
                    cmds.keyTangent(tangent_target, time=(t, t), edit=True, **kwargs)
                except Exception:
                    pass

    return written_curve


def drop_marker(start, end):
    marker_module = load_marker_module()
    if marker_module:
        marker_module.mark_range(int(start), int(end), auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
        marker_module.trigger_fade(delay=500)


# ---------------------------------------------------------------------------
# FAST PATH: relative-pasting a plain pose clipboard. No tangent handling,
# no per-key looping (there's only one key), no redundant curve reads.
# ---------------------------------------------------------------------------
def paste_pose_relative_fast(selected_objects, clipboard):
    anchors = clipboard.get("anchors", {}) or {}
    copied_objects = clipboard.get("objects") or list(anchors.keys())

    channel_attrs = get_channelbox_attrs()
    graph_attrs = get_graph_editor_selected_attrs()
    selected_key_attrs = get_selected_key_attrs()

    if channel_attrs:
        explicit_attrs = channel_attrs
    elif selected_key_attrs:
        explicit_attrs = list(selected_key_attrs)
    elif graph_attrs:
        explicit_attrs = list(graph_attrs)
    else:
        explicit_attrs = None

    timeline_range = get_selected_range()
    ct = timeline_range[0] if timeline_range else cmds.currentTime(q=True)

    pasted_any = False
    for index, obj in enumerate(selected_objects):
        if obj in anchors:
            src_vals = anchors[obj]
        elif index < len(copied_objects) and copied_objects[index] in anchors:
            src_vals = anchors[copied_objects[index]]
        else:
            continue

        attrs = explicit_attrs if explicit_attrs else src_vals.keys()
        for attr in attrs:
            first_key_value = src_vals.get(attr)
            if first_key_value is None:
                continue
            plug = obj + "." + attr
            if not cmds.objExists(plug):
                continue

            target_layer = resolve_destination_anim_layer(obj, attr, None, None)
            existing_curve = resolve_written_curve(obj, attr, target_layer)
            reference_value = get_local_reference_value(plug, existing_curve, target_layer, ct)

            try:
                if target_layer is None:
                    cmds.setKeyframe(plug, time=ct, value=first_key_value)
                else:
                    cmds.setKeyframe(plug, time=ct, value=first_key_value, animLayer=target_layer)
                pasted_any = True
            except Exception:
                continue

            if reference_value is not None:
                offset = reference_value - first_key_value
                if offset != 0:
                    dest_curve = resolve_written_curve(obj, attr, target_layer)
                    try:
                        cmds.keyframe(dest_curve if dest_curve else plug, edit=True, time=(ct, ct), relative=True, valueChange=offset)
                    except Exception:
                        pass

    cmds.selectKey(clear=True)

    if pasted_any:
        drop_marker(ct, ct)

    return True


def paste_keys_relative():
    selected_objects = cmds.ls(selection=True) or []
    if not selected_objects:
        cmds.inViewMessage(amg="Please select something!", pos="midCenter", fade=True)
        return

    clipboard = load_clipboard()
    if not clipboard or not clipboard.get("anchors"):
        cmds.inViewMessage(amg="Nothing to paste!", pos="midCenter", fade=True)
        return

    if not all(isinstance(v, dict) for v in clipboard["anchors"].values()):
        cmds.inViewMessage(amg="Clipboard is outdated, please Copy again!", pos="midCenter", fade=True)
        return

    cmds.undoInfo(openChunk=True, chunkName="Paste Keys Relative")
    try:
        if clipboard.get("pose_only"):
            return paste_pose_relative_fast(selected_objects, clipboard)

        span = clipboard.get("span", 0.0)
        anchors = clipboard.get("anchors", {})
        curves = clipboard.get("curves", {})
        object_curves = clipboard.get("object_curves", {})
        copied_objects = clipboard.get("objects", [])
        channel_attrs = get_channelbox_attrs()
        graph_attrs = get_graph_editor_selected_attrs()
        selected_key_attrs = get_selected_key_attrs()

        all_keyable_attrs = set()
        for obj in selected_objects:
            all_keyable_attrs.update(cmds.listAttr(obj, keyable=True, unlocked=True) or [])

        if graph_attrs and all_keyable_attrs and graph_attrs >= all_keyable_attrs:
            graph_attrs = set()

        use_pose_refresh = bool(channel_attrs) or (not graph_attrs and not selected_key_attrs)
        is_graph_source = bool(clipboard.get("from_graph_editor"))

        if channel_attrs:
            attrs_to_paste = channel_attrs
        elif selected_key_attrs:
            attrs_to_paste = list(selected_key_attrs)
        elif graph_attrs:
            attrs_to_paste = list(graph_attrs)
        else:
            attr_union = {attr for obj_attrs in object_curves.values() for attr in obj_attrs}
            if not attr_union:
                attr_union = set(curves.keys())
            if not attr_union:
                attr_union = {attr for obj_attrs in anchors.values() for attr in obj_attrs}
            attrs_to_paste = sorted(attr_union)

        timeline_range = get_selected_range()
        ct = timeline_range[0] if timeline_range else cmds.currentTime(q=True)

        pasted_plugs = []
        for index, obj in enumerate(selected_objects):
            for attr in attrs_to_paste:
                plug = obj + "." + attr
                if not cmds.objExists(plug):
                    continue

                curve_data = resolve_object_curve(object_curves, copied_objects, selected_objects, index, obj, attr, curves, True)
                if not curve_data:
                    continue

                source_layer = curve_data.get("source_layer")
                source_obj = curve_data.get("_source_obj")
                target_layer = resolve_destination_anim_layer(obj, attr, source_layer, source_obj)

                keys = curve_data.get("keys", [])
                first_key_value = keys[0].get("value") if keys else None

                existing_curve = resolve_written_curve(obj, attr, target_layer)
                reference_value = get_local_reference_value(plug, existing_curve, target_layer, ct)

                if is_graph_source:
                    try:
                        cmds.cutKey(existing_curve if existing_curve else plug, time=(ct, ct + span), clear=True)
                    except Exception:
                        pass

                dest_curve = apply_curve_to_plug(plug, curve_data, ct)

                if reference_value is not None and first_key_value is not None:
                    offset = reference_value - first_key_value
                    if offset != 0:
                        try:
                            cmds.keyframe(dest_curve if dest_curve else plug, edit=True, time=(ct, ct + span), relative=True, valueChange=offset)
                        except Exception:
                            pass

                pasted_plugs.append(plug)

        if is_graph_source and pasted_plugs:
            cmds.selectKey(clear=True)
            for plug in pasted_plugs:
                try:
                    cmds.selectKey(plug, time=(ct, ct + span), add=True)
                except Exception:
                    pass
        elif not is_graph_source:
            cmds.selectKey(clear=True)

        drop_marker(ct, ct + span)

        return use_pose_refresh
    finally:
        cmds.undoInfo(closeChunk=True)


if paste_keys_relative():
    force_rig_refresh()
