import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel
import builtins
import os
import sys

max = builtins.max
min = builtins.min

MARK_COLOR = "#32CD32"
MARK_OPACITY = 0.25

_cache = {
    'layer_attrs': {},
    'long_names': {},
    'anim_layers': None,
    'current_layer': 'unset',
    'root_layer': 'unset',
    'obj_times': {},
}


def reset_caches():
    _cache['layer_attrs'].clear()
    _cache['long_names'].clear()
    _cache['anim_layers'] = None
    _cache['current_layer'] = 'unset'
    _cache['root_layer'] = 'unset'
    _cache['obj_times'].clear()


def get_cached_anim_layers():
    if _cache['anim_layers'] is None:
        _cache['anim_layers'] = cmds.ls(type='animLayer') or []
    return _cache['anim_layers']


def get_cached_layer_attrs(layer):
    layer_attrs = _cache['layer_attrs']
    if layer not in layer_attrs:
        layer_attrs[layer] = cmds.animLayer(layer, query=True, attribute=True) or []
    return layer_attrs[layer]


def get_cached_long_name(node):
    long_names = _cache['long_names']
    if node not in long_names:
        try:
            long_names[node] = cmds.ls(node, long=True) or []
        except Exception:
            long_names[node] = []
    return long_names[node]


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except Exception:
        return "unknown"


def load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(folder)
        marker_folder = os.path.join(parent_folder, "Animo_Keys_Tangent")
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


def get_selection_list():
    return om2.MGlobal.getActiveSelectionList()


def get_selected_objects():
    sel_list = get_selection_list()
    objects = []
    for i in range(sel_list.length()):
        try:
            dag_path = sel_list.getDagPath(i)
            objects.append(dag_path.fullPathName())
        except:
            dep_node = sel_list.getDependNode(i)
            fn_dep = om2.MFnDependencyNode(dep_node)
            objects.append(fn_dep.name())
    return objects


def get_cached_root_layer():
    if _cache['root_layer'] == 'unset':
        _cache['root_layer'] = cmds.animLayer(query=True, root=True)
    return _cache['root_layer']


def get_current_anim_layer():
    if _cache['current_layer'] != 'unset':
        return _cache['current_layer']

    root_layer = get_cached_root_layer()
    if not root_layer:
        _cache['current_layer'] = None
        return None

    try:
        selected_layers = cmds.treeView('AnimLayerTabanimLayerEditor', query=True, selectItem=True) or []
    except Exception:
        selected_layers = []

    if selected_layers:
        _cache['current_layer'] = selected_layers[0]
    else:
        _cache['current_layer'] = root_layer

    return _cache['current_layer']


def get_layer_attrs_for_object(obj_name, layer):
    attrs = get_cached_layer_attrs(layer)
    matched = []
    for attr in attrs:
        node = attr.split('.')[0]
        if node == obj_name:
            matched.append(attr)
            continue
        long_names = get_cached_long_name(node)
        if obj_name in long_names:
            matched.append(attr)
    return matched


def get_keyframe_times_for_layer(obj_name, layer):
    times = set()
    attrs = get_layer_attrs_for_object(obj_name, layer)
    for attr in attrs:
        curve = cmds.animLayer(layer, query=True, findCurveForPlug=attr)
        if not curve:
            continue
        curve_list = curve if isinstance(curve, list) else [curve]
        for curve_node in curve_list:
            curve_times = cmds.keyframe(curve_node, query=True, timeChange=True) or []
            times.update(curve_times)
    return times


def get_direct_keyframe_times_for_plug(plug):
    return cmds.keyframe(plug, q=True, timeChange=True) or []


def get_layer_curve_for_plug(layer, plug):
    if not layer:
        return []
    try:
        curve = cmds.animLayer(layer, query=True, findCurveForPlug=plug)
    except Exception:
        curve = None
    if not curve:
        return []
    return curve if isinstance(curve, list) else [curve]


def get_base_keyframe_times_for_object(obj_name, root_layer):
    times = set()
    attrs = cmds.listAttr(obj_name, keyable=True, unlocked=True) or []
    for attr in attrs:
        plug = obj_name + '.' + attr
        curve_list = get_layer_curve_for_plug(root_layer, plug)
        if curve_list:
            for curve_node in curve_list:
                curve_times = cmds.keyframe(curve_node, query=True, timeChange=True) or []
                times.update(curve_times)
        else:
            times.update(get_direct_keyframe_times_for_plug(plug))
    return times


def get_keyframe_times_for_current_layer(obj_name, current_layer, root_layer):
    attrs = get_layer_attrs_for_object(obj_name, current_layer)
    if attrs:
        return get_keyframe_times_for_layer(obj_name, current_layer)

    return get_base_keyframe_times_for_object(obj_name, root_layer)


def compute_keyframe_times_for_object(obj):
    obj_times = _cache['obj_times']
    if obj in obj_times:
        return obj_times[obj]

    current_layer = get_current_anim_layer()
    root_layer = get_cached_root_layer()

    if current_layer:
        times = get_keyframe_times_for_current_layer(obj, current_layer, root_layer)
    else:
        times = get_base_keyframe_times_for_object(obj, root_layer)

    obj_times[obj] = times
    return times


def get_all_keyframe_times(objects):
    all_times = set()
    for obj in objects:
        all_times.update(compute_keyframe_times_for_object(obj))
    return sorted(list(all_times))


def get_keyframe_times_in_range(objects, start_time, end_time):
    all_times = get_all_keyframe_times(objects)
    return [t for t in all_times if start_time <= t <= end_time]


def object_has_animation(obj_name):
    return bool(compute_keyframe_times_for_object(obj_name))


def validate_selection():
    objects = get_selected_objects()
    if len(objects) == 0:
        return None
    
    all_times = get_all_keyframe_times(objects)
    if not all_times:
        return None
    
    return objects


def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
        return False
    except:
        return False


def get_graph_editor_selection():
    if not is_graph_editor_active():
        return None, {}, []
    
    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None, {}, []
    
    original_selected_objects = get_selected_objects()
    
    selected_curves = cmds.keyframe(q=True, sl=True, name=True) or []
    
    original_key_selection = {}
    for curve in selected_curves:
        curve_key_times = cmds.keyframe(curve, q=True, sl=True, timeChange=True) or []
        if not curve_key_times:
            continue
        plugs = cmds.listConnections(curve, s=False, d=True, p=True) or []
        for plug in plugs:
            if '.' not in plug:
                continue
            obj, attr = plug.split('.', 1)
            original_key_selection.setdefault(obj, {})[attr] = curve_key_times
    
    min_selected_time = min(selected_keys)
    max_selected_time = max(selected_keys)
    graph_editor_range = (min_selected_time, max_selected_time)
    
    return graph_editor_range, original_key_selection, original_selected_objects


def get_timeline_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    range_visible = cmds.timeControl(playback_slider, query=True, rangeVisible=True)
    if range_visible:
        time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        start_range = int(time_range[0])
        end_range = int(time_range[1] - 1)
        if end_range > start_range:
            return start_range, end_range
    return 0, 0


def get_animation_range(objects):
    if objects:
        all_times = get_all_keyframe_times(objects)
        if all_times:
            return all_times[0], all_times[-1]
    
    min_time = cmds.playbackOptions(q=True, animationStartTime=True)
    max_time = cmds.playbackOptions(q=True, animationEndTime=True)
    return min_time, max_time


def categorize_objects(objects):
    objects_with_keys = []
    static_objects = []
    
    for obj in objects:
        if object_has_animation(obj):
            objects_with_keys.append(obj)
        else:
            static_objects.append(obj)
    
    return objects_with_keys, static_objects


def get_animated_and_static_attrs(obj):
    attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
    animated = []
    static = []
    for attr in attrs:
        plug = obj + '.' + attr
        try:
            key_count = cmds.keyframe(plug, q=True, keyframeCount=True)
        except Exception:
            key_count = 0
        if key_count:
            animated.append(attr)
        else:
            static.append(attr)
    return animated, static


def bake_keys_at_times(obj_attr_map, key_times):
    if not obj_attr_map:
        return

    for obj, attrs in obj_attr_map.items():
        target_attrs = attrs if attrs else (cmds.listAttr(obj, keyable=True, unlocked=True) or [])
        for attr in target_attrs:
            plug = obj + '.' + attr
            for t in sorted(key_times):
                try:
                    value = cmds.getAttr(plug, time=t)
                except Exception:
                    continue
                try:
                    cmds.setKeyframe(plug, t=(t, t), v=value)
                except Exception:
                    pass


def set_keys_on_objects(objects_with_keys, static_objects, key_times, original_objects):
    sel_list = om2.MSelectionList()

    bake_map = {}

    if objects_with_keys:
        for obj in objects_with_keys:
            animated_attrs, static_attrs = get_animated_and_static_attrs(obj)
            if animated_attrs:
                cmds.setKeyframe(obj, at=animated_attrs, i=True, t=key_times)
            if static_attrs:
                bake_map[obj] = static_attrs

    if static_objects:
        for obj in static_objects:
            bake_map[obj] = None

    bake_keys_at_times(bake_map, key_times)

    for obj in original_objects:
        sel_list.add(obj)
    om2.MGlobal.setActiveSelectionList(sel_list)


def restore_graph_editor_selection(original_key_selection, original_selected_objects):
    if not original_key_selection:
        return
    
    sel_list = om2.MSelectionList()
    for obj in original_selected_objects:
        try:
            sel_list.add(obj)
        except:
            pass
    om2.MGlobal.setActiveSelectionList(sel_list)
    
    for obj, attr_dict in original_key_selection.items():
        for attr, key_times in attr_dict.items():
            try:
                cmds.selectKey(obj + '.' + attr, t=key_times, add=True)
            except:
                try:
                    cmds.selectKey(obj + '.' + attr, t=(min(key_times), max(key_times)), add=True)
                except:
                    pass


def prepare_scene(objects):
    cmds.selectKey(cl=True)
    
    all_keys = get_all_keyframe_times(objects)
    
    if all_keys:
        first_key_time = all_keys[0]
        cmds.setKeyframe(objects, i=True, t=(first_key_time, first_key_time))
    
    cmds.waitCursor(state=True)


def cleanup_scene():
    cmds.waitCursor(state=False)
    cmds.refresh(suspend=False)


def get_marker_range(objects, graph_editor_range, start_range, end_range):
    if graph_editor_range:
        return int(graph_editor_range[0]), int(graph_editor_range[1])
    elif (end_range - start_range) > 0:
        return start_range, end_range
    else:
        min_time, max_time = get_animation_range(objects if objects else [])
        return int(min_time), int(max_time)


def share_keys():
    cmds.undoInfo(openChunk=True, chunkName="Share Keys")
    
    try:
        objects = validate_selection()
        
        graph_editor_range, original_key_selection, original_selected_objects = get_graph_editor_selection()
        
        start_range, end_range = get_timeline_range()
        min_time, max_time = get_animation_range(objects if objects else [])
        
        if objects:
            prepare_scene(objects)
        
        if graph_editor_range:
            key_times = get_keyframe_times_in_range(objects if objects else [], graph_editor_range[0], graph_editor_range[1])
        elif (end_range - start_range) > 0:
            key_times = get_keyframe_times_in_range(objects if objects else [], start_range, end_range)
        else:
            key_times = get_keyframe_times_in_range(objects if objects else [], min_time, max_time)
        
        if not objects:
            cmds.warning("Please select an object.")
            cleanup_scene()
            return
        
        if key_times:
            objects_with_keys, static_objects = categorize_objects(objects)
            set_keys_on_objects(objects_with_keys, static_objects, key_times, objects)
        
        cleanup_scene()
        
        restore_graph_editor_selection(original_key_selection, original_selected_objects)
    
    finally:
        cmds.undoInfo(closeChunk=True)


def run():
    reset_caches()
    
    marker_module = load_marker_module()
    
    objects = validate_selection()
    graph_editor_range, _, _ = get_graph_editor_selection()
    start_range, end_range = get_timeline_range()
    
    if marker_module and objects:
        marker_start, marker_end = get_marker_range(objects, graph_editor_range, start_range, end_range)
        marker_module.mark_range(marker_start, marker_end, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
    
    share_keys()
    
    if marker_module:
        marker_module.trigger_fade(delay=500)


run()