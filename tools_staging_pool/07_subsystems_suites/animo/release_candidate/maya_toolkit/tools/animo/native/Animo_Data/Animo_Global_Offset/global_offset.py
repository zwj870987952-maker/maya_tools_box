import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import time


MARK_COLOR = "#3A8A9E"
MARK_OPACITY = 0.40

STORAGE_PREFIX = "_animo_global_offset"


def is_graph_editor_focused():
    try:
        panel = cmds.getPanel(withFocus=True)
        if panel and 'graphEditor' in panel:
            return True
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
    except:
        pass
    return False


def is_mouse_over_graph_editor():
    try:
        panel = cmds.getPanel(underPointer=True)
        if panel and 'graphEditor' in panel:
            return True
    except:
        pass
    return False


def find_layer_plug_for_attr(obj_name, layer_attrs, attr):
    for plug in layer_attrs:
        node = plug.split('.')[0]
        if node == obj_name:
            if plug.split('.', 1)[-1] == attr:
                return plug
            continue
        try:
            long_names = cmds.ls(node, long=True) or []
        except:
            long_names = []
        if obj_name in long_names and plug.split('.', 1)[-1] == attr:
            return plug
    return None


def get_current_anim_layer(root_layer, all_layers):
    for layer in all_layers:
        try:
            if cmds.animLayer(layer, query=True, preferred=True):
                return layer
        except:
            pass
    
    for layer in all_layers:
        try:
            if cmds.animLayer(layer, query=True, selected=True):
                return layer
        except:
            pass
    
    return root_layer


def build_layer_context():
    try:
        root_layer = cmds.animLayer(query=True, root=True)
    except:
        root_layer = None
    
    all_layers = cmds.ls(type="animLayer") or []
    
    layer_attrs = {}
    for layer in all_layers:
        try:
            layer_attrs[layer] = cmds.animLayer(layer, query=True, attribute=True) or []
        except:
            layer_attrs[layer] = []
    
    current_layer = get_current_anim_layer(root_layer, all_layers)
    
    return {
        'root_layer': root_layer,
        'all_layers': all_layers,
        'layer_attrs': layer_attrs,
        'current_layer': current_layer,
    }


def resolve_base_curve(obj, attr):
    plug = "{}.{}".format(obj, attr)
    src = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
    if not src:
        return None
    src_plug = src[0]
    src_node = src_plug.split(".")[0]
    src_attr = src_plug.split(".", 1)[-1]
    try:
        src_node_type = cmds.nodeType(src_node)
    except:
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
                except:
                    a_type = None
                if a_type and a_type.startswith("animCurve"):
                    return a_node
        return None
    if src_node_type and src_node_type.startswith("animCurve"):
        return src_node
    return None


def resolve_target_curve(obj, attr, context):
    plug = "{}.{}".format(obj, attr)
    root_layer = context['root_layer']
    current_layer = context['current_layer']
    
    owning_layers = []
    for layer in context['all_layers']:
        if find_layer_plug_for_attr(obj, context['layer_attrs'].get(layer, []), attr):
            owning_layers.append(layer)
    
    if not owning_layers:
        conns = cmds.listConnections(plug, source=True, destination=False, type="animCurve", skipConversionNodes=True) or []
        return conns[0] if conns else None
    
    if current_layer and root_layer and current_layer == root_layer:
        target_layer = root_layer
    elif current_layer in owning_layers:
        target_layer = current_layer
    else:
        target_layer = owning_layers[0]
    
    if target_layer == root_layer:
        return resolve_base_curve(obj, attr)
    
    matched_plug = find_layer_plug_for_attr(obj, context['layer_attrs'].get(target_layer, []), attr)
    if matched_plug:
        try:
            curve = cmds.animLayer(target_layer, query=True, findCurveForPlug=matched_plug)
        except:
            curve = None
        if curve:
            return curve[0] if isinstance(curve, list) else curve
    return None


def refresh_marker_if_needed():
    stored_range = get_storage('range')
    if not stored_range:
        return
    
    last_refresh = get_storage('last_marker_refresh')
    now = time.time()
    
    if last_refresh is not None and (now - last_refresh) < 1.0:
        return
    
    marker = None
    try:
        marker = load_marker_module()
    except:
        marker = None
    
    if not marker:
        return
    
    start_time, end_time = stored_range
    
    try:
        marker.mark_range(start_time, end_time, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY, layer="base")
        cmds.refresh(force=True)
    except:
        pass
    
    set_storage('last_marker_refresh', now)


def idle_check():
    if not is_enabled():
        return
    
    if get_storage('applying'):
        return
    
    stored_range = get_storage('range')
    if stored_range:
        _start_time, _end_time = stored_range
        process_pending_captures(_start_time, _end_time)
    
    refresh_marker_if_needed()
    
    current_time = cmds.currentTime(q=True)
    last_time = get_storage('last_time')
    
    if last_time is not None and abs(current_time - last_time) > 0.001:
        set_storage('last_time', current_time)
        return
    
    apply_offset_at_current_time()
    
    if not is_mouse_over_graph_editor():
        return
    
    selected_key_count = cmds.keyframe(query=True, selected=True, keyframeCount=True)
    if not selected_key_count:
        return
    
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    
    if original_snapshot is None or not stored_range:
        return
    
    selected = cmds.ls(selection=True)
    if not selected:
        return
    
    start_time, end_time = stored_range
    refresh_active_layer_targets(selected, start_time, end_time)
    current_offsets = get_storage('offsets') or {}
    original_snapshot = ensure_snapshot_coverage(selected, start_time, end_time, current_time)
    
    for obj in selected:
        if obj not in original_snapshot:
            continue
        
        for attr, entry in original_snapshot[obj].items():
            keys = entry.get('keys')
            if not keys:
                continue
            
            curve = entry.get('curve')
            target = curve if curve else "{}.{}".format(obj, attr)
            offset_key = "{}:{}".format(obj, attr)
            stored_offset = current_offsets.get(offset_key, 0)
            
            key_times_list = list(keys.keys())
            min_t = min(key_times_list)
            max_t = max(key_times_list)
            
            try:
                current_times = cmds.keyframe(target, q=True, timeChange=True, time=(min_t, max_t))
                current_values = cmds.keyframe(target, q=True, valueChange=True, time=(min_t, max_t))
            except:
                current_times = None
                current_values = None
            
            if current_times and current_values and len(current_times) == len(current_values):
                current_map = dict(zip(current_times, current_values))
            else:
                current_map = {}
            
            for key_time, original_val in keys.items():
                current_key_val = current_map.get(key_time)
                if current_key_val is None:
                    continue
                
                detected_offset = current_key_val - original_val
                
                if abs(detected_offset - stored_offset) > 1e-6:
                    apply_offset_at_frame_graph(key_time, obj, attr, detected_offset)
                    return


def apply_offset_at_frame_graph(frame_time, changed_obj, changed_attr, new_offset):
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    
    if original_snapshot is None or not stored_range:
        return
    
    if get_storage('applying'):
        return
    
    set_storage('applying', True)
    
    if changed_obj not in original_snapshot:
        set_storage('applying', False)
        return
    
    if changed_attr not in original_snapshot[changed_obj]:
        set_storage('applying', False)
        return
    
    entry = original_snapshot[changed_obj][changed_attr]
    keys = entry.get('keys')
    if not keys:
        set_storage('applying', False)
        return
    
    curve = entry.get('curve')
    target = curve if curve else "{}.{}".format(changed_obj, changed_attr)
    
    cmds.undoInfo(stateWithoutFlush=False)
    
    try:
        for t, orig_val in keys.items():
            new_key_val = orig_val + new_offset
            cmds.keyframe(target, edit=True, time=(t, t), valueChange=new_key_val, absolute=True)
        
        current_offsets = get_storage('offsets') or {}
        offset_key = "{}:{}".format(changed_obj, changed_attr)
        current_offsets[offset_key] = new_offset
        set_storage('offsets', current_offsets)
    
    finally:
        cmds.undoInfo(stateWithoutFlush=True)
        set_storage('applying', False)


def get_storage(key):
    name = "{}_{}".format(STORAGE_PREFIX, key)
    if hasattr(cmds, name):
        return getattr(cmds, name)
    return None


def set_storage(key, value):
    name = "{}_{}".format(STORAGE_PREFIX, key)
    setattr(cmds, name, value)


def clear_storage():
    for attr in ['jobs', 'snapshot', 'range', 'callback', 'idle_callback', 'selection_callback', 'applying', 'last_time', 'offsets', 'last_marker_refresh', 'last_active_layer', 'pending_capture', 'undo_chunk_open', 'undo_chunk_last_update', 'pending_graph_change', 'pending_graph_change_time', 'pending_undo_resync', 'last_undo_redo_time', 'session_change_count', 'max_session_change_count']:
        name = "{}_{}".format(STORAGE_PREFIX, attr)
        if hasattr(cmds, name):
            delattr(cmds, name)


_MAYA_VERSION_CACHE = {}
_MARKER_MODULE_CACHE = {}


def get_maya_version():
    if 'value' in _MAYA_VERSION_CACHE:
        return _MAYA_VERSION_CACHE['value']
    try:
        v = cmds.about(version=True).split()[0]
    except:
        v = "unknown"
    _MAYA_VERSION_CACHE['value'] = v
    return v


def load_marker_module():
    if 'module' in _MARKER_MODULE_CACHE:
        return _MARKER_MODULE_CACHE['module']
    
    v = get_maya_version()
    n = "mark_frame"
    
    candidate_folders = []
    
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        candidate_folders.append(folder)
        parent_folder = os.path.dirname(folder)
        candidate_folders.append(os.path.join(parent_folder, "Animo_Keys_Tangent"))
    except NameError:
        pass
    
    candidate_folders.append(os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent"))
    
    marker_folder = None
    for candidate in candidate_folders:
        py = os.path.join(candidate, n + ".py")
        pyc = os.path.join(candidate, "{}_py{}.pyc".format(n, v))
        if os.path.exists(py) or os.path.exists(pyc):
            marker_folder = candidate
            break
    
    if marker_folder is None:
        _MARKER_MODULE_CACHE['module'] = None
        return None
    
    if marker_folder not in sys.path:
        sys.path.insert(0, marker_folder)
    
    if n in sys.modules:
        del sys.modules[n]
    
    try:
        import importlib
        mod = importlib.import_module(n)
    except:
        mod = None
    
    _MARKER_MODULE_CACHE['module'] = mod
    return mod


def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
    except:
        pass
    return False


def get_graph_editor_key_range():
    if not is_graph_editor_active():
        return None
    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None
    
    min_time = min(selected_keys)
    max_time = max(selected_keys)
    
    if abs(max_time - min_time) < 0.001:
        return None
    
    return (min_time, max_time)


def get_playback_range():
    return int(cmds.playbackOptions(q=True, minTime=True)), int(cmds.playbackOptions(q=True, maxTime=True))


def get_timeline_range():
    playback_slider = mel.eval('$animoGlobalOffsetSlider=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(time_range[0])
    end = int(time_range[1] - 1)
    if end - start > 0:
        return start, end
    return None


def get_active_range():
    graph_range = get_graph_editor_key_range()
    if graph_range:
        return int(graph_range[0]), int(graph_range[1])
    timeline_range = get_timeline_range()
    if timeline_range:
        return timeline_range
    return get_playback_range()


STANDARD_KEYABLE_ATTRS = ['translateX', 'translateY', 'translateZ',
                          'rotateX', 'rotateY', 'rotateZ',
                          'scaleX', 'scaleY', 'scaleZ']


def get_keyable_attrs(obj):
    attrs = []
    for attr in STANDARD_KEYABLE_ATTRS:
        if cmds.objExists("{}.{}".format(obj, attr)):
            attrs.append(attr)
    
    user_attrs = cmds.listAttr(obj, keyable=True, unlocked=True)
    if user_attrs:
        for attr in user_attrs:
            if attr not in attrs:
                attrs.append(attr)
    return attrs


def interpolate_value(key_data, target_time):
    if not key_data:
        return None
    
    times = sorted(key_data.keys())
    
    for t in times:
        if abs(t - target_time) < 0.001:
            return key_data[t]
    
    if target_time <= times[0]:
        return key_data[times[0]]
    
    if target_time >= times[-1]:
        return key_data[times[-1]]
    
    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        if t1 <= target_time <= t2:
            v1, v2 = key_data[t1], key_data[t2]
            ratio = (target_time - t1) / (t2 - t1)
            return v1 + ratio * (v2 - v1)
    
    return None


def capture_snapshot(objects, start_time, end_time):
    snapshot = {}
    context = build_layer_context()
    
    for obj in objects:
        snapshot[obj] = {}
        
        attrs = get_keyable_attrs(obj)
        for attr in attrs:
            curve = resolve_target_curve(obj, attr, context)
            target = curve if curve else "{}.{}".format(obj, attr)
            
            key_times = cmds.keyframe(target, q=True, timeChange=True, time=(start_time, end_time))
            if key_times:
                try:
                    key_values = cmds.keyframe(target, q=True, valueChange=True, time=(start_time, end_time))
                except:
                    key_values = None
                
                if key_values and len(key_values) == len(key_times):
                    snapshot[obj][attr] = {"curve": curve, "keys": dict(zip(key_times, key_values))}
                else:
                    snapshot[obj][attr] = {"curve": curve, "keys": {}}
                    for t in key_times:
                        try:
                            val = cmds.keyframe(target, q=True, valueChange=True, time=(t, t))[0]
                            snapshot[obj][attr]["keys"][t] = val
                        except:
                            pass
    
    return snapshot


def ensure_snapshot_coverage(selected, start_time, end_time, current_time=None):
    snapshot = get_storage('snapshot') or {}
    changed = False
    
    for obj in selected:
        if obj not in snapshot:
            obj_snapshot = capture_snapshot([obj], start_time, end_time)
            if obj_snapshot.get(obj):
                snapshot[obj] = obj_snapshot[obj]
                changed = True
            continue
        
        for attr, entry in snapshot[obj].items():
            curve = entry.get('curve')
            target = curve if curve else "{}.{}".format(obj, attr)
            keys = entry.get('keys', {})
            
            current_key_times = cmds.keyframe(target, q=True, timeChange=True, time=(start_time, end_time))
            times_to_cover = set(current_key_times) if current_key_times else set()
            
            if current_time is not None and start_time <= current_time <= end_time:
                times_to_cover.add(current_time)
            
            for t in times_to_cover:
                if t in keys:
                    continue
                
                expected_orig = interpolate_value(keys, t)
                if expected_orig is None:
                    continue
                
                keys[t] = expected_orig
                changed = True
    
    if changed:
        set_storage('snapshot', snapshot)
    
    return snapshot


def process_pending_captures(start_time, end_time, batch_size=5):
    pending = get_storage('pending_capture')
    if not pending:
        return
    
    snapshot = get_storage('snapshot') or {}
    
    remaining = list(pending)
    batch = []
    while remaining and len(batch) < batch_size:
        obj = remaining.pop(0)
        if obj in snapshot:
            continue
        batch.append(obj)
    
    if not batch:
        set_storage('pending_capture', remaining)
        return
    
    obj_snapshot = capture_snapshot(batch, start_time, end_time)
    
    for obj in batch:
        if obj_snapshot.get(obj):
            snapshot[obj] = obj_snapshot[obj]
    
    set_storage('snapshot', snapshot)
    set_storage('pending_capture', remaining)


def refresh_active_layer_targets(selected, start_time, end_time):
    try:
        root_layer = cmds.animLayer(query=True, root=True)
    except:
        root_layer = None
    
    all_layers = cmds.ls(type="animLayer") or []
    current_layer = get_current_anim_layer(root_layer, all_layers)
    
    last_layer = get_storage('last_active_layer')
    layer_unchanged = (last_layer == current_layer)
    
    set_storage('last_active_layer', current_layer)
    
    snapshot = get_storage('snapshot') or {}
    offsets = get_storage('offsets') or {}
    changed = False
    offsets_changed = False
    context = None
    
    for obj in selected:
        if obj not in snapshot:
            continue
        
        for attr, entry in snapshot[obj].items():
            stored_curve = entry.get('curve')
            
            if layer_unchanged and stored_curve is not None:
                continue
            
            if context is None:
                layer_attrs = {}
                for layer in all_layers:
                    try:
                        layer_attrs[layer] = cmds.animLayer(layer, query=True, attribute=True) or []
                    except:
                        layer_attrs[layer] = []
                
                context = {
                    'root_layer': root_layer,
                    'all_layers': all_layers,
                    'layer_attrs': layer_attrs,
                    'current_layer': current_layer,
                }
            
            current_curve = resolve_target_curve(obj, attr, context)
            
            if current_curve == stored_curve:
                continue
            
            target = current_curve if current_curve else "{}.{}".format(obj, attr)
            
            new_keys = {}
            key_times = cmds.keyframe(target, q=True, timeChange=True, time=(start_time, end_time))
            if key_times:
                try:
                    key_values = cmds.keyframe(target, q=True, valueChange=True, time=(start_time, end_time))
                except:
                    key_values = None
                
                if key_values and len(key_values) == len(key_times):
                    new_keys = dict(zip(key_times, key_values))
                else:
                    for t in key_times:
                        try:
                            val = cmds.keyframe(target, q=True, valueChange=True, time=(t, t))[0]
                            new_keys[t] = val
                        except:
                            pass
            
            entry['curve'] = current_curve
            entry['keys'] = new_keys
            changed = True
            
            offset_key = "{}:{}".format(obj, attr)
            if offset_key in offsets:
                offsets[offset_key] = 0
                offsets_changed = True
    
    if changed:
        set_storage('snapshot', snapshot)
    if offsets_changed:
        set_storage('offsets', offsets)
    
    return snapshot


def apply_offset_at_current_time():
    if get_storage('applying'):
        return
    
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    
    if original_snapshot is None or not stored_range:
        return
    
    selected = cmds.ls(selection=True)
    if not selected:
        return
    
    current_time = cmds.currentTime(q=True)
    start_time, end_time = stored_range
    
    if current_time < start_time or current_time > end_time:
        return
    
    refresh_active_layer_targets(selected, start_time, end_time)
    original_snapshot = ensure_snapshot_coverage(selected, start_time, end_time, current_time)
    
    current_offsets = get_storage('offsets') or {}
    offsets_to_apply = []
    
    for obj in selected:
        if obj not in original_snapshot:
            continue
        
        for attr, entry in original_snapshot[obj].items():
            keys = entry.get('keys')
            if not keys:
                continue
            
            keyed_time = None
            for t in keys:
                if abs(t - current_time) < 0.001:
                    keyed_time = t
                    break
            
            if keyed_time is None:
                continue
            
            curve = entry.get('curve')
            target = curve if curve else "{}.{}".format(obj, attr)
            
            try:
                current_vals = cmds.keyframe(target, q=True, time=(keyed_time, keyed_time), valueChange=True)
                if not current_vals:
                    continue
                current_val = current_vals[0]
            except:
                continue
            
            expected_val = keys[keyed_time]
            
            offset = current_val - expected_val
            offset_key = "{}:{}".format(obj, attr)
            stored_offset = current_offsets.get(offset_key, 0)
            
            if abs(offset - stored_offset) < 1e-9:
                continue
            
            offsets_to_apply.append((obj, attr, offset, keys, target, offset_key))
    
    if not offsets_to_apply:
        return
    
    set_storage('applying', True)
    cmds.undoInfo(openChunk=True, chunkName="Global Offset")
    
    try:
        for obj, attr, offset, keys, target, offset_key in offsets_to_apply:
            for t, original_val in keys.items():
                new_key_val = original_val + offset
                cmds.keyframe(target, edit=True, time=(t, t), valueChange=new_key_val, absolute=True)
            
            current_offsets[offset_key] = offset
        
        set_storage('offsets', current_offsets)
        set_storage('last_time', current_time)
    
    finally:
        cmds.undoInfo(closeChunk=True)
        set_storage('applying', False)


def on_selection_changed():
    if not is_enabled():
        return
    
    if get_storage('applying'):
        return
    
    stored_range = get_storage('range')
    if not stored_range:
        return
    
    selected = cmds.ls(selection=True)
    if not selected:
        return
    
    snapshot = get_storage('snapshot') or {}
    pending = get_storage('pending_capture') or []
    pending_set = set(pending)
    added = False
    
    for obj in selected:
        if obj not in snapshot and obj not in pending_set:
            pending.append(obj)
            pending_set.add(obj)
            added = True
    
    if added:
        set_storage('pending_capture', pending)


def kill_jobs():
    jobs = get_storage('jobs')
    if jobs:
        for job_id in jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    cmds.scriptJob(kill=job_id, force=True)
            except:
                pass
    set_storage('jobs', [])


def is_enabled():
    jobs = get_storage('jobs')
    if jobs:
        for job_id in jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    return True
            except:
                pass
    return False


def enable():
    kill_jobs()
    
    marker = None
    try:
        marker = load_marker_module()
    except:
        marker = None
    
    fade_marker(marker)
    
    selected = cmds.ls(selection=True)
    start_time, end_time = get_active_range()
    
    if marker:
        try:
            marker.mark_range(start_time, end_time, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY, layer="base")
            cmds.refresh(force=True)
        except:
            pass
        set_storage('last_marker_refresh', time.time())
    
    snapshot = {}
    
    set_storage('snapshot', snapshot)
    set_storage('pending_capture', list(selected) if selected else [])
    set_storage('range', (start_time, end_time))
    set_storage('idle_callback', idle_check)
    set_storage('selection_callback', on_selection_changed)
    set_storage('applying', False)
    set_storage('offsets', {})
    set_storage('last_time', cmds.currentTime(q=True))
    
    try:
        _root_layer = cmds.animLayer(query=True, root=True)
    except:
        _root_layer = None
    _all_layers = cmds.ls(type="animLayer") or []
    set_storage('last_active_layer', get_current_anim_layer(_root_layer, _all_layers))
    
    idle_callback_func = get_storage('idle_callback')
    selection_callback_func = get_storage('selection_callback')
    
    job_events = [
        ("idle", idle_callback_func),
        ("SelectionChanged", selection_callback_func),
    ]
    
    created_jobs = []
    for event_name, event_func in job_events:
        try:
            job_id = cmds.scriptJob(runOnce=False, killWithScene=True, event=[event_name, event_func])
            created_jobs.append(job_id)
        except Exception as e:
            print("Failed to register scriptJob for event '{}': {}".format(event_name, e))
    
    set_storage('jobs', created_jobs)


def fade_marker(marker):
    if not marker:
        return
    try:
        if hasattr(marker, 'clear_all'):
            marker.clear_all()
        else:
            marker.trigger_fade(delay=0, fast=True)
    except:
        pass


def restore_keys(original_snapshot, current_offsets):
    for obj in original_snapshot:
        for attr, entry in original_snapshot[obj].items():
            keys = entry.get('keys')
            if not keys:
                continue
            
            offset_key = "{}:{}".format(obj, attr)
            offset = current_offsets.get(offset_key, 0)
            if abs(offset) < 1e-9:
                continue
            
            curve = entry.get('curve')
            target = curve if curve else "{}.{}".format(obj, attr)
            
            for t, original_val in keys.items():
                try:
                    cmds.keyframe(target, edit=True, time=(t, t), valueChange=original_val, absolute=True)
                except:
                    pass


def reapply_offsets(original_snapshot, current_offsets):
    for obj in original_snapshot:
        for attr, entry in original_snapshot[obj].items():
            keys = entry.get('keys')
            if not keys:
                continue
            
            offset_key = "{}:{}".format(obj, attr)
            offset = current_offsets.get(offset_key, 0)
            
            if abs(offset) < 1e-9:
                continue
            
            curve = entry.get('curve')
            target = curve if curve else "{}.{}".format(obj, attr)
            
            for t, original_val in keys.items():
                new_val = original_val + offset
                try:
                    cmds.keyframe(target, edit=True, time=(t, t), valueChange=new_val, absolute=True)
                except:
                    pass


def disable():
    marker = None
    try:
        marker = load_marker_module()
    except:
        marker = None
    
    kill_jobs()
    clear_storage()
    fade_marker(marker)


def force_reset():
    kill_jobs()
    clear_storage()
    
    marker = None
    try:
        marker = load_marker_module()
    except:
        marker = None
    
    fade_marker(marker)


def toggle():
    if is_enabled():
        disable()
    else:
        enable()


def run():
    toggle()