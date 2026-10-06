from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import json
import os
import sys
from maya import mel

MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40


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


def get_xform_json_path():
    anim_tools_folder = os.path.join(os.path.expanduser("~"), "Documents", "animTools")

    if not os.path.exists(anim_tools_folder):
        os.makedirs(anim_tools_folder)

    return os.path.join(anim_tools_folder, "Xform_Animation_Data.json")


def get_long_name(obj):
    long = cmds.ls(obj, long=True)
    return long[0] if long else obj


def get_short_name(obj):
    return obj.split("|")[-1].split(":")[-1]


def get_object_keyframes(obj, start_frame, end_frame):
    keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
    if keys:
        return sorted(set([int(k) for k in keys]))
    return []


def write_payload(meta, transform_data):
    json_path = get_xform_json_path()
    payload = {
        "meta": meta,
        "data": transform_data
    }
    with open(json_path, 'w') as json_file:
        json.dump(payload, json_file, indent=4)
    return json_path


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


def create_snapshot_locator():
    locator = cmds.spaceLocator(name="xformCopyLocator#")[0]
    hide_locator(locator)
    return locator


def read_locator_world_transform(obj, locator):
    cmds.matchTransform(locator, obj, position=True, rotation=True)
    translate = cmds.getAttr(locator + ".translate")[0]
    rotate = cmds.getAttr(locator + ".rotate")[0]
    return list(translate), list(rotate)


def cleanup_locators(locators):
    existing = [l for l in locators if l and cmds.objExists(l)]
    if existing:
        try:
            cmds.delete(existing)
        except Exception:
            pass


def copy_xform_data():
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        cmds.inViewMessage(
            amg='Please select something!',
            pos='midCenter',
            fade=True
        )
        return

    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    start_range = int(timeRange[0])
    end_range = int(timeRange[1] - 1)

    try:
        if end_range - start_range == 0:
            copy_current_frame_transforms(selection)
        else:
            copy_animation_range(selection, start_range, end_range)
    finally:
        try:
            cmds.select(selection, replace=True)
        except Exception:
            pass


def copy_current_frame_transforms(selection):
    marker = load_mark_frame()
    if marker:
        marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)

    current_frame = int(cmds.currentTime(q=True))

    animation_data = {}

    cmds.undoInfo(openChunk=True, chunkName="Copy Xform Single Frame")
    try:
        locators = []
        try:
            for obj in selection:
                long_obj = get_long_name(obj)
                try:
                    locator = create_snapshot_locator()
                    locators.append(locator)

                    translate, rotate = read_locator_world_transform(long_obj, locator)
                    key = get_short_name(long_obj)

                    animation_data[key] = {
                        "keyframes": [current_frame],
                        str(current_frame): {
                            "translate": [round(v, 6) for v in translate],
                            "rotate": [round(v, 6) for v in rotate]
                        }
                    }

                except Exception as e:
                    cmds.warning("Failed to get transform data for {0}: {1}".format(long_obj, str(e)))
        finally:
            cleanup_locators(locators)
    finally:
        cmds.undoInfo(closeChunk=True)

    meta = {
        "mode": "single",
        "start_frame": current_frame,
        "end_frame": current_frame
    }

    try:
        write_payload(meta, animation_data)

        cmds.inViewMessage(
            amg='Xform Copied ({0} object{1})'.format(
                len(animation_data), "s" if len(animation_data) != 1 else ""
            ),
            pos='botCenter',
            fade=True
        )

    except Exception as e:
        cmds.error("Failed to save JSON file: {0}".format(str(e)))


def copy_animation_range(selection, start_frame, end_frame):
    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)

    animation_data = {}
    current_time = cmds.currentTime(q=True)

    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.undoInfo(openChunk=True, chunkName="Copy Xform Range")

    try:
        try:
            cmds.evaluationManager(mode="off")
        except Exception:
            pass
        try:
            cmds.refresh(suspend=True)
        except Exception:
            pass

        locators = {}
        try:
            for obj in selection:
                long_obj = get_long_name(obj)
                key = get_short_name(long_obj)
                animation_data[key] = {
                    "keyframes": get_object_keyframes(long_obj, start_frame, end_frame)
                }
                locators[long_obj] = create_snapshot_locator()

            for frame in range(start_frame, end_frame + 1):
                cmds.currentTime(frame)

                for obj in selection:
                    long_obj = get_long_name(obj)
                    key = get_short_name(long_obj)
                    locator = locators[long_obj]

                    translate, rotate = read_locator_world_transform(long_obj, locator)

                    animation_data[key][str(frame)] = {
                        "translate": [round(v, 6) for v in translate],
                        "rotate": [round(v, 6) for v in rotate]
                    }
        finally:
            cleanup_locators(list(locators.values()))

        meta = {
            "mode": "range",
            "start_frame": start_frame,
            "end_frame": end_frame
        }

        write_payload(meta, animation_data)

        cmds.inViewMessage(
            amg='Xform Copied ({0} object{1})'.format(
                len(animation_data), "s" if len(animation_data) != 1 else ""
            ),
            pos='botCenter',
            fade=True
        )

    finally:
        try:
            cmds.currentTime(current_time)
        except Exception:
            pass
        try:
            cmds.refresh(suspend=False)
        except Exception:
            pass
        try:
            if original_eval_mode:
                cmds.evaluationManager(mode=original_eval_mode[0])
        except Exception:
            pass
        cmds.undoInfo(closeChunk=True)


copy_xform_data()