import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as cmds
import maya.mel as mel
import builtins

max = builtins.max
min = builtins.min


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


def get_anim_curves_for_object(obj_name):
    sel_list = om2.MSelectionList()
    try:
        sel_list.add(obj_name)
    except:
        return []
    
    dep_node = sel_list.getDependNode(0)
    anim_curves = []
    
    it_dg = om2.MItDependencyGraph(
        dep_node,
        om2.MFn.kAnimCurve,
        om2.MItDependencyGraph.kUpstream,
        om2.MItDependencyGraph.kDepthFirst,
        om2.MItDependencyGraph.kNodeLevel
    )
    
    while not it_dg.isDone():
        anim_curves.append(it_dg.currentNode())
        it_dg.next()
    
    return anim_curves


def get_keyframe_times_from_curves(anim_curves):
    key_times = set()
    
    for curve_obj in anim_curves:
        fn_anim = oma2.MFnAnimCurve(curve_obj)
        
        if not fn_anim.isTimeInput:
            continue
        
        num_keys = fn_anim.numKeys
        
        for i in range(num_keys):
            time_input = fn_anim.input(i)
            if isinstance(time_input, om2.MTime):
                key_times.add(time_input.value)
            else:
                key_times.add(float(time_input))
    
    return sorted(list(key_times))


def get_all_keyframe_times(objects):
    all_times = set()
    
    for obj in objects:
        curves = get_anim_curves_for_object(obj)
        times = get_keyframe_times_from_curves(curves)
        all_times.update(times)
    
    return sorted(list(all_times))


def get_keyframe_times_in_range(objects, start_time, end_time):
    all_times = get_all_keyframe_times(objects)
    return [t for t in all_times if start_time <= t <= end_time]


def object_has_animation(obj_name):
    curves = get_anim_curves_for_object(obj_name)
    return len(curves) > 0


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
    original_key_selection = {}
    
    for obj in original_selected_objects:
        obj_selected_keys = cmds.keyframe(obj, q=True, sl=True)
        if obj_selected_keys:
            attrs = cmds.listAttr(obj, keyable=True, scalar=True) or []
            obj_key_info = {}
            for attr in attrs:
                try:
                    attr_keys = cmds.keyframe(obj + '.' + attr, q=True, sl=True)
                    if attr_keys:
                        obj_key_info[attr] = attr_keys
                except:
                    continue
            if obj_key_info:
                original_key_selection[obj] = obj_key_info
    
    min_selected_time = min(selected_keys)
    max_selected_time = max(selected_keys)
    graph_editor_range = (min_selected_time, max_selected_time)
    
    return graph_editor_range, original_key_selection, original_selected_objects


def get_timeline_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return start_range, end_range


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


def set_keys_on_objects(objects_with_keys, static_objects, key_times, original_objects):
    sel_list = om2.MSelectionList()
    
    if objects_with_keys:
        for obj in objects_with_keys:
            sel_list.add(obj)
        om2.MGlobal.setActiveSelectionList(sel_list)
        cmds.setKeyframe(i=True, t=key_times)
    
    if static_objects:
        sel_list.clear()
        for obj in static_objects:
            sel_list.add(obj)
        om2.MGlobal.setActiveSelectionList(sel_list)
        cmds.setKeyframe(t=key_times)
    
    sel_list.clear()
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
    
    cur_time = oma2.MAnimControl.currentTime()
    all_keys = get_all_keyframe_times(objects)
    
    if all_keys:
        first_key_time = om2.MTime(all_keys[0], om2.MTime.uiUnit())
        oma2.MAnimControl.setCurrentTime(first_key_time)
        cmds.setKeyframe()
        oma2.MAnimControl.setCurrentTime(cur_time)
    
    cmds.waitCursor(state=True)


def cleanup_scene():
    cmds.waitCursor(state=False)
    cmds.refresh(suspend=False)


def share_keys_main():
    objects = validate_selection()
    
    graph_editor_range, original_key_selection, original_selected_objects = get_graph_editor_selection()
    
    if objects:
        prepare_scene(objects)
    
    start_range, end_range = get_timeline_range()
    min_time, max_time = get_animation_range(objects if objects else [])
    
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


share_keys_main()