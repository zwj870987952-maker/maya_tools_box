from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import json
import os
import sys
from maya import mel


MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40
SPARSE_KEYS_OPTION_VAR = "XformAlignUI_bakeKeys"


def load_mark_frame():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Space_Switcher")

    if folder not in sys.path:
        sys.path.insert(0, folder)

    try:
        import mark_frame
        return mark_frame
    except ImportError:
        return None


def should_paste_sparse_keys_only():
    if cmds.optionVar(exists=SPARSE_KEYS_OPTION_VAR):
        return cmds.optionVar(q=SPARSE_KEYS_OPTION_VAR) == 1
    return True


def get_object_keyframes(objects, start_frame, end_frame):
    keyframes = set()
    for obj in objects:
        keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
        if keys:
            keyframes.update([int(k) for k in keys])
    return sorted(keyframes)


def get_xform_json_path():
    anim_tools_folder = os.path.join(os.path.expanduser("~"), "Documents", "animTools")
    return os.path.join(anim_tools_folder, "Xform_Animation_Data.json")


def get_long_name(obj):
    long = cmds.ls(obj, long=True)
    return long[0] if long else obj


def get_short_name(obj):
    return obj.split("|")[-1].split(":")[-1]


def get_transform_data(payload):
    if "data" in payload:
        return payload["data"]
    return {k: v for k, v in payload.items() if k != "meta"}


def get_meta(payload, transform_data):
    if "meta" in payload:
        return payload["meta"]

    all_frames = []
    for obj_data in transform_data.values():
        for k in obj_data.keys():
            if k != "keyframes" and k.lstrip('-').isdigit():
                all_frames.append(int(k))

    if all_frames:
        return {"mode": "range", "start_frame": min(all_frames), "end_frame": max(all_frames)}

    return {"mode": "single", "start_frame": int(cmds.currentTime(q=True)), "end_frame": int(cmds.currentTime(q=True))}


def build_time_remap(meta, dest_start, dest_end):
    src_start = meta.get("start_frame", dest_start)
    src_end = meta.get("end_frame", dest_end)
    src_span = src_end - src_start
    dest_span = dest_end - dest_start

    if src_span <= 0:
        def to_source(frame):
            return src_start

        def to_dest(frame):
            return dest_start

        return to_source, to_dest

    if dest_span <= 0:
        offset = dest_start - src_start

        def to_source(frame):
            return frame - offset

        def to_dest(frame):
            return frame + offset

        return to_source, to_dest

    scale = src_span / float(dest_span)
    inv_scale = dest_span / float(src_span)

    def to_source(frame):
        return int(round(src_start + (frame - dest_start) * scale))

    def to_dest(frame):
        return int(round(dest_start + (frame - src_start) * inv_scale))

    return to_source, to_dest


def resolve_objects_from_json(payload):
    resolved = []
    transform_data = get_transform_data(payload)
    for short_name in transform_data.keys():
        matches = cmds.ls(short_name, long=True)
        if not matches:
            matches = cmds.ls("*:" + short_name, long=True)
        if matches:
            resolved.append(matches[0])
        else:
            cmds.warning("Object '{0}' from JSON not found in scene.".format(short_name))
    return resolved


def is_single_frame_snapshot(meta, transform_data):
    if meta.get("mode") == "single":
        return True
    for obj_data in transform_data.values():
        if "keyframes" in obj_data:
            return False
        frame_keys = [k for k in obj_data.keys() if k != "keyframes"]
        if len(frame_keys) != 1:
            return False
    return True


def build_paste_mapping(selected_objects, transform_data):
    json_keys = list(transform_data.keys())

    if not json_keys:
        return []

    if len(json_keys) == 1:
        return [(get_long_name(obj), json_keys[0]) for obj in selected_objects]

    name_matched = [(get_long_name(obj), get_short_name(obj)) for obj in selected_objects
                    if get_short_name(obj) in transform_data]

    if name_matched:
        return name_matched

    if len(selected_objects) == len(json_keys):
        return list(zip([get_long_name(obj) for obj in selected_objects], json_keys))

    cmds.warning(
        "Selection count ({0}) does not match stored object count ({1}) "
        "and no name matches were found. Paste aborted.".format(
            len(selected_objects), len(json_keys)
        )
    )
    return []


def sort_mapping_by_hierarchy(mapping):
    return sorted(mapping, key=lambda pair: pair[0].count("|"))


def get_timeline_range():
    playback_slider = mel.eval('$tmp=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(time_range[0])
    end = int(time_range[1]) - 1
    if end > start:
        return start, end
    return None


def get_frame_data(transform_data, source_key, frame, to_source=None):
    obj_data = transform_data.get(source_key, {})

    if frame is None:
        available = [k for k in obj_data.keys() if k != "keyframes"]
        if available:
            return obj_data[available[0]]
        return None

    lookup_frame = to_source(frame) if to_source else frame
    frame_str = str(lookup_frame)
    if frame_str in obj_data:
        return obj_data[frame_str]
    return None


MAX_XFORM_PASSES = 6
TRANSLATE_MATCH_TOLERANCE = 1e-4
ROTATE_MATCH_TOLERANCE = 1e-3


def _values_match(values_a, values_b, tolerance):
    for value_a, value_b in zip(values_a, values_b):
        if abs(value_a - value_b) > tolerance:
            return False
    return True


def hide_locator(locator):
    try:
        cmds.setAttr(locator + ".visibility", False)
    except Exception:
        pass
    try:
        cmds.setAttr(locator + ".hiddenInOutliner", True)
    except Exception:
        pass
    try:
        mel.eval("AEdagNodeCommonRefreshOutliners();")
    except Exception:
        pass


def create_pose_locator():
    locator = cmds.spaceLocator(name="xformPasteLocator#")[0]
    hide_locator(locator)
    return locator


def create_pose_locators(mapping):
    locator_map = {}
    for target_obj, _ in mapping:
        if target_obj not in locator_map:
            locator_map[target_obj] = create_pose_locator()
    return locator_map


def cleanup_pose_locators(locator_map):
    locators = [l for l in locator_map.values() if l and cmds.objExists(l)]
    if locators:
        try:
            cmds.delete(locators)
        except Exception:
            pass


def query_world_transform(obj, locator):
    cmds.matchTransform(locator, obj, position=True, rotation=True)
    translate = cmds.getAttr(locator + ".translate")[0]
    rotate = cmds.getAttr(locator + ".rotate")[0]
    return list(translate), list(rotate)


def apply_pose(obj, translate, rotate, locator):
    cmds.setAttr(locator + ".translate", *translate)
    cmds.setAttr(locator + ".rotate", *rotate)
    cmds.matchTransform(obj, locator, position=True, rotation=True)


def apply_pose_converged(mapping, transform_data, frame, locator_map, to_source=None):
    for _ in range(MAX_XFORM_PASSES):
        settled = True
        for target_obj, source_key in mapping:
            data = get_frame_data(transform_data, source_key, frame, to_source)
            if data is None:
                continue
            target_translate = data["translate"]
            target_rotate = data["rotate"]
            locator = locator_map[target_obj]
            current_translate, current_rotate = query_world_transform(target_obj, locator)
            if _values_match(current_translate, target_translate, TRANSLATE_MATCH_TOLERANCE) and \
               _values_match(current_rotate, target_rotate, ROTATE_MATCH_TOLERANCE):
                continue
            apply_pose(target_obj, target_translate, target_rotate, locator)
            settled = False
        if settled:
            break


def clear_existing_keys(mapping, start_frame, end_frame):
    targets = sorted(set(obj for obj, _ in mapping))
    for target_obj in targets:
        try:
            cmds.cutKey(target_obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"),
                        time=(start_frame, end_frame), option="keys")
        except Exception:
            pass


def clear_existing_keys_at_frames(mapping, frames):
    targets = sorted(set(obj for obj, _ in mapping))
    for target_obj in targets:
        for frame in frames:
            try:
                cmds.cutKey(target_obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"),
                            time=(frame, frame), option="keys")
            except Exception:
                pass


def filter_target_curves(mapping, start_frame=None, end_frame=None):
    targets = sorted(set(obj for obj, _ in mapping))
    if not targets:
        return
    try:
        if start_frame is not None and end_frame is not None:
            cmds.filterCurve(targets, time=(start_frame, end_frame))
        else:
            cmds.filterCurve(targets)
    except Exception:
        pass


def suspend_evaluation():
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    try:
        cmds.evaluationManager(mode="off")
    except Exception:
        pass
    try:
        cmds.refresh(suspend=True)
    except Exception:
        pass
    return original_eval_mode


def resume_evaluation(original_eval_mode):
    try:
        cmds.refresh(suspend=False)
    except Exception:
        pass
    try:
        if original_eval_mode:
            cmds.evaluationManager(mode=original_eval_mode[0])
    except Exception:
        pass


def paste_transforms():
    original_selection = cmds.ls(selection=True, long=True)
    selected_objects = original_selection

    json_path = get_xform_json_path()

    if not os.path.exists(json_path):
        cmds.inViewMessage(
            amg='No data found. Copy first.',
            pos='midCenter',
            fade=True
        )
        return

    try:
        with open(json_path, 'r') as json_file:
            payload = json.load(json_file)
    except Exception as e:
        cmds.error("Failed to load JSON file: {0}".format(str(e)))
        return

    transform_data = get_transform_data(payload)
    meta = get_meta(payload, transform_data)

    if not selected_objects:
        selected_objects = resolve_objects_from_json(payload)
        if not selected_objects:
            cmds.inViewMessage(
                amg='No objects found in scene matching stored data.',
                pos='midCenter',
                fade=True
            )
            return

    mapping = build_paste_mapping(selected_objects, transform_data)
    if not mapping:
        return

    mapping = sort_mapping_by_hierarchy(mapping)

    single_frame_source = is_single_frame_snapshot(meta, transform_data)
    timeline_range = get_timeline_range()

    try:
        if single_frame_source and not timeline_range:
            paste_single_frame_data(mapping, transform_data)
            return

        if not timeline_range:
            fallback_frame = int(cmds.currentTime(q=True))
            timeline_range = (meta.get("start_frame", fallback_frame), meta.get("end_frame", fallback_frame))

        start_frame, end_frame = timeline_range
        sparse_keys_mode = should_paste_sparse_keys_only()

        if sparse_keys_mode:
            paste_at_keyframes(mapping, transform_data, meta, start_frame, end_frame)
        else:
            paste_animation_range(mapping, transform_data, meta, start_frame, end_frame)
    finally:
        try:
            if original_selection:
                cmds.select(original_selection, replace=True)
            else:
                cmds.select(selected_objects, replace=True)
        except Exception:
            pass


def paste_at_keyframes(mapping, transform_data, meta, start_frame, end_frame):
    to_source, to_dest = build_time_remap(meta, start_frame, end_frame)

    target_objects = [obj for obj, _ in mapping]
    existing_keyframes = get_object_keyframes(target_objects, start_frame, end_frame)

    if existing_keyframes:
        keyframes = existing_keyframes
    else:
        stored_keyframes = set()
        for _, source_key in mapping:
            obj_data = transform_data.get(source_key, {})
            if "keyframes" in obj_data:
                for k in obj_data["keyframes"]:
                    dest_k = to_dest(k)
                    if start_frame <= dest_k <= end_frame:
                        stored_keyframes.add(dest_k)
        keyframes = sorted(stored_keyframes)

    if not keyframes:
        cmds.warning("Bake Only Keys is enabled, but no keyframes were found on the selection or in the copied data. Uncheck Bake Only Keys to paste every frame instead.")
        return

    marker = load_mark_frame()
    if marker:
        marker.mark_range(keyframes[0], keyframes[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)

    current_time = cmds.currentTime(q=True)

    cmds.undoInfo(openChunk=True, chunkName="Paste Xform At Keys")
    try:
        original_eval_mode = suspend_evaluation()
        try:
            locator_map = create_pose_locators(mapping)
            try:
                clear_existing_keys_at_frames(mapping, keyframes)

                for frame in keyframes:
                    cmds.currentTime(frame)

                    apply_pose_converged(mapping, transform_data, frame, locator_map, to_source)

                    for target_obj, source_key in mapping:
                        data = get_frame_data(transform_data, source_key, frame, to_source)
                        if data is None:
                            continue
                        cmds.setKeyframe(target_obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)

                filter_target_curves(mapping, keyframes[0], keyframes[-1])
            finally:
                cleanup_pose_locators(locator_map)
        finally:
            resume_evaluation(original_eval_mode)
            try:
                cmds.currentTime(current_time)
            except Exception:
                pass
    finally:
        cmds.undoInfo(closeChunk=True)


def paste_single_frame_data(mapping, transform_data):
    marker = load_mark_frame()
    if marker:
        marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)

    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Single Frame")

    try:
        locator_map = create_pose_locators(mapping)
        try:
            apply_pose_converged(mapping, transform_data, None, locator_map)

            for target_obj, source_key in mapping:
                data = get_frame_data(transform_data, source_key, None)
                if data is None:
                    continue
                try:
                    cmds.setKeyframe(target_obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"))
                except Exception as e:
                    cmds.warning("Failed to apply transforms to {0}: {1}".format(target_obj, str(e)))
        finally:
            cleanup_pose_locators(locator_map)

    finally:
        cmds.undoInfo(closeChunk=True)


def paste_animation_range(mapping, transform_data, meta, start_frame, end_frame):
    to_source, to_dest = build_time_remap(meta, start_frame, end_frame)

    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)

    current_time = cmds.currentTime(q=True)

    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Animation Range")
    try:
        original_eval_mode = suspend_evaluation()
        try:
            locator_map = create_pose_locators(mapping)
            try:
                clear_existing_keys(mapping, start_frame, end_frame)

                for frame in range(start_frame, end_frame + 1):
                    cmds.currentTime(frame)

                    apply_pose_converged(mapping, transform_data, frame, locator_map, to_source)

                    for target_obj, source_key in mapping:
                        data = get_frame_data(transform_data, source_key, frame, to_source)
                        if data is None:
                            continue
                        cmds.setKeyframe(target_obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)

                filter_target_curves(mapping, start_frame, end_frame)
            finally:
                cleanup_pose_locators(locator_map)
        finally:
            resume_evaluation(original_eval_mode)
            try:
                cmds.currentTime(current_time)
            except Exception:
                pass
    finally:
        cmds.undoInfo(closeChunk=True)


paste_transforms()
