from __future__ import division
from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import json
import os
import sys
import platform

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtGui import QGuiApplication
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtGui, QtCore
        from PySide2.QtGui import QGuiApplication
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1
        QGuiApplication = QtGui.QApplication

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    int = builtins.int
    str = builtins.str
    range = builtins.range
except Exception:
    pass


def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except Exception:
        return 2022


def get_dpi_scale():
    maya_version = get_maya_version()
    
    dpi = 96.0
    base_scale = 1.0
    got_screen_info = False
    
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                try:
                    dpi = screen.logicalDotsPerInch()
                    got_screen_info = True
                except (RuntimeError, AttributeError):
                    pass
        
        if got_screen_info:
            base_scale = dpi / 96.0
            
    except (RuntimeError, AttributeError):
        pass
    except Exception:
        pass
    
    if maya_version >= 2025:
        if base_scale > 2.0:
            return max(1.0, min(base_scale * 1.15, 3.0))
        return max(1.0, min(base_scale, 3.0))
    
    if maya_version >= 2022 and maya_version <= 2024:
        return max(1.0, min(base_scale, 3.0))
    
    return max(1.0, min(base_scale, 3.0))


def get_manual_scale_override():
    if cmds.optionVar(exists="esnTwosifyScale"):
        scale = cmds.optionVar(q="esnTwosifyScale")
        return max(0.5, min(scale, 3.0))
    return None


def get_final_dpi_scale():
    manual_override = get_manual_scale_override()
    if manual_override:
        return manual_override
    return get_dpi_scale()


def scale_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())


def scale_font_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())


def is_macos():
    return platform.system() == 'Darwin'


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=('TwosifyUI_WindowPos', pos_str))


def load_window_position():
    if cmds.optionVar(exists='TwosifyUI_WindowPos'):
        try:
            pos_str = cmds.optionVar(q='TwosifyUI_WindowPos')
            x, y = pos_str.split(',')
            return QtCore.QPoint(int(x), int(y))
        except Exception:
            pass
    return None


def get_esn_twosify_node():
    node = "esnTwosifyData"
    if not cmds.objExists(node):
        current_selection = cmds.ls(selection=True)
        node = cmds.createNode("network", name=node)
        cmds.addAttr(node, longName="cameraObj", dataType="string")
        cmds.addAttr(node, longName="masterObj", dataType="string")
        try:
            cmds.setAttr("{0}.isHistoricallyInteresting".format(node), 1)
            cmds.lockNode(node, lock=False)
        except Exception:
            pass
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
    return node


def save_twosify_camera_master(camera_text, master_text):
    node = get_esn_twosify_node()
    try:
        cmds.setAttr("{0}.cameraObj".format(node), camera_text, type="string")
        cmds.setAttr("{0}.masterObj".format(node), master_text, type="string")
    except Exception:
        pass


def load_twosify_camera_master():
    node = get_esn_twosify_node()
    camera_text = ""
    master_text = ""
    if cmds.objExists("{0}.cameraObj".format(node)):
        try:
            camera_text = cmds.getAttr("{0}.cameraObj".format(node)) or ""
        except Exception:
            camera_text = ""
    if cmds.objExists("{0}.masterObj".format(node)):
        try:
            master_text = cmds.getAttr("{0}.masterObj".format(node)) or ""
        except Exception:
            master_text = ""
    return camera_text, master_text


def set_outliner_color(obj, color=(0.75, 0.5, 0.9)):
    if not cmds.objExists(obj):
        return
    try:
        cmds.setAttr("{}.useOutlinerColor".format(obj), 1)
        cmds.setAttr("{}.outlinerColor".format(obj), color[0], color[1], color[2], type="double3")
    except Exception:
        pass


def get_frames_on_ones():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    return list(range(min_time, max_time + 1))


def set_keys_ones_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_on_ones()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def get_frames_every_three():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    return list(range(min_time, max_time + 1, 3))


def set_keys_threes_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_every_three()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def generate_twos_threes_pattern():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    pattern = [2, 3]
    step_index = 0
    frames = []
    time = min_time
    while time <= max_time:
        frames.append(time)
        time += pattern[step_index % len(pattern)]
        step_index += 1
    return frames


def set_keys_twos_threes_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = generate_twos_threes_pattern()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def get_frames_three_four():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    pattern = [3, 4]
    step_index = 0
    frames = []
    time = min_time
    while time <= max_time:
        frames.append(time)
        time += pattern[step_index % len(pattern)]
        step_index += 1
    return frames


def set_keys_threes_fours_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_three_four()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def set_keys_twos_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = list(range(min_time, max_time + 1, 2))
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def get_frames_every_four():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    return list(range(min_time, max_time + 1, 4))


def set_keys_fours_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_every_four()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def get_frames_every_five():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    return list(range(min_time, max_time + 1, 5))


def set_keys_fives_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_every_five()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def get_frames_every_six():
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    return list(range(min_time, max_time + 1, 6))


def set_keys_sixes_anim_layer():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    min_time = int(cmds.playbackOptions(q=True, min=True))
    max_time = int(cmds.playbackOptions(q=True, max=True))
    frames_list = get_frames_every_six()
    cur_time = cmds.currentTime(q=True)
    cmds.waitCursor(state=True)
    try:
        cmds.cutKey(sel, t=(min_time, max_time), clear=True)
        cmds.currentTime(frames_list[0])
        cmds.setKeyframe()
        if len(frames_list) > 1:
            cmds.setKeyframe(i=True, t=(frames_list[1:]))
        cmds.currentTime(cur_time)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


copied_key_times = []


def get_desktop_path():
    docs_dir = os.path.join(os.path.expanduser("~"))
    anim_tools_folder = os.path.join(docs_dir, "animTools")
    try:
        os.makedirs(anim_tools_folder)
    except OSError:
        pass
    return anim_tools_folder


def show_feedback_message(message):
    try:
        cmds.inViewMessage(
            amg=message,
            pos='botCenter',
            fade=True,
            fadeStayTime=1500,
            fadeOutTime=500
        )
    except Exception:
        pass


def get_selected_channelbox_attrs():
    try:
        channel_box = mel.eval('$tmp=$gChannelBoxName')
        main_selected = cmds.channelBox(channel_box, q=True, selectedMainAttributes=True) or []
        shape_selected = cmds.channelBox(channel_box, q=True, selectedShapeAttributes=True) or []
        output_selected = cmds.channelBox(channel_box, q=True, selectedOutputAttributes=True) or []
        history_selected = cmds.channelBox(channel_box, q=True, selectedHistoryAttributes=True) or []
        return list(set(main_selected + shape_selected + output_selected + history_selected))
    except Exception:
        return []


def get_all_keyable_attrs(obj):
    try:
        all_attrs = cmds.listAttr(obj, keyable=True, visible=True, unlocked=True) or []
        return all_attrs
    except Exception:
        return []


def copy_key_times_script():
    global copied_key_times
    sel = cmds.ls(sl=True)
    if len(sel) == 0:
        return
    Min_t = int(cmds.playbackOptions(q=True, min=True))
    Max_t = int(cmds.playbackOptions(q=True, max=True))
    allKeys = cmds.keyframe(sel, q=True, t=(Min_t, Max_t))
    if allKeys:
        key_times = list(set(allKeys))
        key_times.sort()
    else:
        key_times = []
    copied_key_times = key_times[:]
    desktop_path = get_desktop_path()
    json_filename = "esn_key_times.json"
    json_path = os.path.join(desktop_path, json_filename)
    json_data = {
        "key_times": key_times,
        "playback_range": [Min_t, Max_t],
        "source_objects": sel,
        "has_keys": len(key_times) > 0
    }
    try:
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
    except Exception:
        pass
    show_feedback_message("Copied Key Time")


def copy_key_times_smart():
    selected = cmds.ls(sl=True)
    if not selected:
        cmds.warning("No objects selected.")
        return
    result = {}
    for obj in selected:
        attrs = get_selected_channelbox_attrs()
        if not attrs:
            attrs = get_all_keyable_attrs(obj)
        if not attrs:
            continue
        obj_data = {}
        for attr in attrs:
            full_attr = "{}.{}".format(obj, attr)
            if cmds.objExists(full_attr):
                key_times = cmds.keyframe(full_attr, q=True, timeChange=True)
                if key_times:
                    obj_data[attr] = key_times
        if obj_data:
            result[obj] = obj_data
    if not result:
        cmds.warning("No keyed attributes found on selected objects.")
        return
    desktop_path = get_desktop_path()
    json_filename = "maya_key_timing.json"
    json_path = os.path.join(desktop_path, json_filename)
    try:
        with open(json_path, "w") as f:
            json.dump(result, f, indent=4)
    except Exception:
        pass
    show_feedback_message("Copied Key Time")


def clean_range_script():
    global copied_key_times
    desktop_path = get_desktop_path()
    json_filename = "esn_key_times.json"
    json_path = os.path.join(desktop_path, json_filename)
    json_data = {}
    allKeys = []
    if not os.path.exists(json_path):
        allKeys = copied_key_times[:]
        if not allKeys:
            cmds.warning("No key times found. Please use Copy button first.")
            return
    else:
        try:
            with open(json_path, "r") as f:
                json_data = json.load(f)
            allKeys = json_data.get("key_times", [])
            if not allKeys:
                cmds.warning("No key times found in JSON file. Please use Copy button first.")
                return
        except Exception:
            cmds.warning("Error reading JSON file. Using fallback if available.")
            allKeys = copied_key_times[:]
            if not allKeys:
                cmds.warning("No fallback key times available.")
                return
    sel = cmds.ls(sl=True)
    if len(sel) == 0:
        return
    CT = cmds.currentTime(q=1)
    stored_range = json_data.get("playback_range", [int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))])
    Minn = stored_range[0]
    Maxx = stored_range[1]
    objects = cmds.ls(sl=1)
    cmds.waitCursor(state=True)
    try:
        objWithNoKeys = []
        for obj in objects:
            keyframes = cmds.keyframe(obj, q=1)
            if keyframes is None:
                objWithNoKeys.append(obj)
        if objWithNoKeys and allKeys:
            for obj in objWithNoKeys:
                cmds.setKeyframe(obj, t=allKeys[0])
        allFrames = range(Minn, Maxx + 1)
        for key in allKeys:
            cmds.setKeyframe(objects, i=True, t=key)
        for frame in allFrames:
            if frame not in allKeys:
                cmds.cutKey(objects, t=(frame, frame))
        cmds.currentTime(CT)
    except Exception:
        pass
    finally:
        cmds.waitCursor(state=False)


def paste_key_times_smart():
    desktop_path = get_desktop_path()
    json_filename = "maya_key_timing.json"
    json_path = os.path.join(desktop_path, json_filename)
    if not os.path.exists(json_path):
        cmds.warning("JSON file not found. Please use Smart Copy first.")
        return
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception:
        return
    if not data:
        cmds.warning("JSON is empty or invalid.")
        return
    selected = cmds.ls(sl=True)
    if not selected:
        cmds.warning("Please select at least one object.")
        return
    time_start = cmds.playbackOptions(q=True, min=True)
    time_end = cmds.playbackOptions(q=True, max=True)
    timeline_min = float(time_start)
    timeline_max = float(time_end)
    ref_obj = next(iter(data))
    for obj in selected:
        obj_key_data = data.get(obj, data[ref_obj])
        for attr, ref_times in obj_key_data.items():
            full_attr = "{}.{}".format(obj, attr)
            if not cmds.objExists(full_attr):
                continue
            filtered_ref_times = [t for t in ref_times if timeline_min <= t <= timeline_max]
            ref_set = set(filtered_ref_times)
            actual_times = cmds.keyframe(full_attr, q=True, timeChange=True)
            actual_set = set(actual_times) if actual_times else set()
            to_add = [t for t in sorted(ref_set - actual_set) if timeline_min <= t <= timeline_max]
            to_remove = [t for t in sorted(actual_set - ref_set) if timeline_min <= t <= timeline_max]
            for t in to_add:
                cmds.setKeyframe(full_attr, time=t, insert=True)
            for t in to_remove:
                cmds.cutKey(full_attr, time=(t, t), option="keys")


def create_twos_layer():
    sel = cmds.ls(sl=True)
    if sel:
        root_layer = cmds.animLayer(query=True, root=True) or []
        animLayers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
        cmds.waitCursor(state=True)
        animLayerName = cmds.animLayer("TWOS", selected=True)
        for layer in animLayers:
            mel.eval('animLayerEditorOnSelect {0} 0;'.format(layer))
        attrs = cmds.listAnimatable()
        for attr in attrs:
            cmds.animLayer(animLayerName, e=True, attribute=attr)
        cmds.waitCursor(state=False)
    else:
        cmds.confirmDialog(title="Error", message="Please select something to create an animLayer.")


def add_selected_to_anim_layer():
    sel = cmds.ls(sl=True)
    if sel:
        try:
            animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)[0]
            attrs = cmds.listAnimatable()
            for attr in attrs:
                cmds.animLayer(animLayerName, e=True, attribute=attr)
        except Exception:
            pass


def select_objects_in_selected_anim_layer():
    selected_anim_layers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)
    if not selected_anim_layers:
        return
    objects = []
    for anim_layer in selected_anim_layers:
        anim_layer_attrs = cmds.animLayer(anim_layer, query=True, attribute=True)
        if anim_layer_attrs:
            for attr in anim_layer_attrs:
                obj = attr.split('.')[0]
                objects.append(obj)
    if objects:
        objects = list(set(objects))
        cmds.select(objects)


def convert_to_twos():
    animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
    if animLayerName:
        animLayerName = animLayerName[0]
    else:
        return
    rootLayer = cmds.animLayer(q=True, root=True)
    animLayers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
    min_time = cmds.playbackOptions(q=True, min=True)
    max_time = cmds.playbackOptions(q=True, max=True)
    sel = cmds.ls(sl=True)
    try:
        cmds.selectKey(cl=True)
    except Exception:
        pass
    if sel:
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        StartRange = timeRange[0]
        EndRange = timeRange[1] - 1
        StartRange = int(StartRange)
        EndRange = int(EndRange)
        if (EndRange - StartRange == 0):
            if animLayers[0] == rootLayer:
                cmds.confirmDialog(title='Error', message='Please make sure to have an animLayer selected!', button="Got it!")
            else:
                cmds.animLayer(animLayerName, edit=True, override=True)
                cmds.animLayer(animLayerName, e=True, weight=0)
                curTime = cmds.currentTime(q=True)
                keys = cmds.keyframe(q=True, t=(min_time, max_time))
                if keys:
                    cmds.waitCursor(state=True)
                    keys = list(set(keys))
                    keys.sort()
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.setKeyframe()
                    cmds.currentTime(curTime)
                    cmds.refresh(suspend=False)
                    cmds.animLayer(animLayerName, e=True, weight=1)
                    cmds.keyTangent(ott="step", itt="auto")
                    cmds.waitCursor(state=False)
                else:
                    cmds.confirmDialog(title='Error', message='Please set some keys!', button="Got it!")
        else:
            if animLayers[0] == rootLayer:
                cmds.confirmDialog(title='Error', message='Please make sure to have an animLayer selected!', button="Got it!")
            else:
                cmds.animLayer(animLayerName, edit=True, override=True)
                cmds.animLayer(animLayerName, e=True, weight=0)
                curTime = cmds.currentTime(q=True)
                keys = cmds.keyframe(q=True, t=(StartRange, EndRange))
                if keys:
                    cmds.waitCursor(state=True)
                    keys = list(set(keys))
                    keys.sort()
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.setKeyframe()
                    cmds.currentTime(curTime)
                    cmds.refresh(suspend=False)
                    cmds.animLayer(animLayerName, e=True, weight=1)
                    cmds.keyTangent(ott="step", itt="step")
                    cmds.waitCursor(state=False)
                else:
                    cmds.confirmDialog(title='Error', message='Please set some keys!', button="Got it!")
    else:
        cmds.confirmDialog(title='Error', message='Please select something!', button="Got it!")


def simple_smart_constraint(ctrl=None, object=None, connect_to_attach_cam=False, attach_cam_object=None):
    transAttr = None
    rotAttr = None
    translate = True
    rotate = True
    scale = False
    maintainOffset = True
    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')
    rotSkip = []
    transSkip = []
    for axis in ['x', 'y', 'z']:
        if transAttr and not 'translate' + axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate' + axis.upper() in rotAttr:
            rotSkip.append(axis)
    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'
    constraints = []
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(cmds.parentConstraint(ctrl, object, maintainOffset=maintainOffset))
    else:
        if transAttr:
            constraints.append(cmds.pointConstraint(ctrl, object, skip=transSkip, maintainOffset=maintainOffset))
        if rotAttr:
            constraints.append(cmds.orientConstraint(ctrl, object, skip=rotSkip, maintainOffset=maintainOffset))
    return constraints


def smart_constraint_create_attach_cam(ctrl=None, object=None):
    if not ctrl or not object:
        return
    if not cmds.objExists(ctrl):
        return
    if not cmds.objExists(object):
        return
    transAttr = None
    rotAttr = None
    translate = True
    rotate = True
    maintainOffset = True
    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')
    rotSkip = []
    transSkip = []
    for axis in ['x', 'y', 'z']:
        if transAttr and not 'translate' + axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate' + axis.upper() in rotAttr:
            rotSkip.append(axis)
    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'
    constraints = []
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(cmds.parentConstraint(ctrl, object, maintainOffset=maintainOffset))
    else:
        if transAttr:
            constraints.append(cmds.pointConstraint(ctrl, object, skip=transSkip, maintainOffset=maintainOffset))
        if rotAttr:
            constraints.append(cmds.orientConstraint(ctrl, object, skip=rotSkip, maintainOffset=maintainOffset))
    try:
        if cmds.attributeQuery('Attach_Cam', node=object, exists=True):
            pass
        else:
            cmds.addAttr(object, longName='Attach_Cam', attributeType='enum',
                         enumName='Off:On', defaultValue=1, keyable=True)
    except Exception:
        pass
    for constraint in constraints:
        if constraint:
            if isinstance(constraint, list):
                constraint_node = constraint[0]
            else:
                constraint_node = constraint
            if cmds.attributeQuery('Attach_Cam', node=object, exists=True):
                weightAttrs = cmds.listAttr(constraint_node, string='*W*')
                if weightAttrs:
                    for weightAttr in weightAttrs:
                        if 'W0' in weightAttr or 'Weight' in weightAttr:
                            try:
                                cmds.connectAttr("{}.Attach_Cam".format(object), "{}.{}".format(constraint_node, weightAttr), force=True)
                            except Exception:
                                pass
    return constraints


def create_circle(master_name=None):
    if master_name:
        base_name = "{}_esn_cam_attach".format(master_name)
    else:
        base_name = "Follow_Cam_esn_cam_attach"
    counter = 1
    circle_name = "{}_{:02d}".format(base_name, counter)
    while cmds.objExists(circle_name):
        counter += 1
        circle_name = "{}_{:02d}".format(base_name, counter)
    circle = cmds.circle(normal=(0, 1, 0), name=circle_name)[0]
    circle_shape = cmds.listRelatives(circle, shapes=True)[0]
    cmds.setAttr(circle_shape + ".overrideEnabled", 1)
    cmds.setAttr(circle_shape + ".overrideColor", 17)
    cmds.setAttr(circle + ".visibility", lock=True)
    cmds.setAttr(circle + ".visibility", keyable=False, channelBox=False)
    for axis in ['X', 'Y', 'Z']:
        scale_attr = circle + ".scale" + axis
        cmds.setAttr(scale_attr, keyable=False)
        cmds.setAttr(scale_attr, channelBox=False)
    cmds.setAttr(circle + ".displayHandle", 1)
    return circle


def create_locator():
    base_name = "Follow_Cam_Loc"
    counter = 1
    locator_name = "{}_{:02d}".format(base_name, counter)
    while cmds.objExists(locator_name):
        counter += 1
        locator_name = "{}_{:02d}".format(base_name, counter)
    locator = cmds.spaceLocator(name=locator_name)[0]
    locator_shape = cmds.listRelatives(locator, shapes=True)[0]
    cmds.setAttr(locator_shape + ".overrideEnabled", 1)
    cmds.setAttr(locator_shape + ".overrideColor", 13)
    cmds.setAttr(locator + ".visibility", lock=True)
    cmds.setAttr(locator + ".visibility", keyable=False, channelBox=False)
    for axis in ['X', 'Y', 'Z']:
        scale_attr = locator + ".scale" + axis
        cmds.setAttr(scale_attr, keyable=False)
        cmds.setAttr(scale_attr, channelBox=False)
    cmds.setAttr(locator + ".displayHandle", 1)
    return locator


def get_keys_time(objs=None):
    if objs is None:
        objs = cmds.ls(selection=True)
    if not objs:
        return []
    keys_time = cmds.keyframe(objs, query=True, timeChange=True) or []
    return sorted(list(set(keys_time)))


class TwosifyUI(QtWidgets.QDialog):
    option_var_name = "TwosifyUI_lastPos"
    
    def __init__(self, parent=get_maya_main_window()):
        super(TwosifyUI, self).__init__(parent)
        self.setObjectName("TwosifyUIWindow")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        self.current_mode = "KEYS TIME"
        self.current_view = "Make It Stepped"
        
        self.setup_ui()
        self.load_camera_master_fields()
        self.apply_theme()
        self.restore_position()
        self.apply_rounded_corners()
        
        self.fade_to(0.87)
    
    def setup_ui(self):
        window_width = scale_size(280)
        window_height = scale_size(360)
        self.setFixedSize(window_width, window_height)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(scale_size(14), scale_size(14), scale_size(14), scale_size(14))
        main_layout.setSpacing(0)
        
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(0)
        
        spacer_left = QtWidgets.QWidget()
        spacer_left.setFixedSize(scale_size(26), scale_size(26))
        title_bar.addWidget(spacer_left)
        
        title_bar.addStretch()
        
        self.title_label = QtWidgets.QLabel("Twosify")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11pt;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_bar.addWidget(self.title_label)
        
        title_bar.addStretch()
        
        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(scale_size(26), scale_size(26))
        close_button.setText("x")
        close_button.setCursor(QtCore.Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
                color: #666666;
                font-size: 16pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        main_layout.addLayout(title_bar)
        
        main_layout.addSpacing(scale_size(14))
        
        self.section_label = QtWidgets.QLabel("Stepped")
        self.section_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(self.section_label)
        
        main_layout.addSpacing(scale_size(6))
        
        self.view_dropdown = QtWidgets.QComboBox()
        self.view_dropdown.addItems(["Make It Stepped", "Attach to Camera"])
        self.view_dropdown.setFixedHeight(scale_size(33))
        self.view_dropdown.setCursor(QtCore.Qt.PointingHandCursor)
        self.view_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #2A2A3D;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 5px 11px;
                font-size: 8pt;
            }
            QComboBox:hover {
                background-color: #3A3A4D;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3D;
                color: #FFFFFF;
                selection-background-color: #4A7AC9;
                border: none;
                font-size: 8pt;
            }
        """)
        self.view_dropdown.currentTextChanged.connect(self.on_view_changed)
        main_layout.addWidget(self.view_dropdown)
        
        main_layout.addSpacing(scale_size(10))
        
        self.stacked_widget = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.stepped_widget = self.create_stepped_view()
        self.camera_widget = self.create_camera_view()
        
        self.stacked_widget.addWidget(self.stepped_widget)
        self.stacked_widget.addWidget(self.camera_widget)
        
        main_layout.addStretch()
    
    def create_stepped_view(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(scale_size(10))
        
        self.anim_layer_button = QtWidgets.QPushButton("C R E A T E   A N I M L A Y E R")
        self.anim_layer_button.setFixedHeight(scale_size(33))
        self.anim_layer_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.anim_layer_button.setStyleSheet("""
            QPushButton {
                background-color: #4A7AC9;
                border: none;
                color: #FFFFFF;
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #5A8AD9;
            }
            QPushButton:pressed {
                background-color: #3A6AB9;
            }
        """)
        self.anim_layer_button.clicked.connect(self.create_anim_layer_action)
        self.anim_layer_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.anim_layer_button.customContextMenuRequested.connect(self.show_anim_layer_menu)
        layout.addWidget(self.anim_layer_button)
        
        layout.addSpacing(scale_size(6))
        
        self.mode_label = QtWidgets.QLabel("KEYS TIME")
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        layout.addWidget(self.mode_label)
        
        layout.addSpacing(scale_size(4))
        
        self.mode_dropdown = QtWidgets.QComboBox()
        self.mode_dropdown.addItems(["KEYS TIME", "CHANNELS KEYS TIME"])
        self.mode_dropdown.setFixedHeight(scale_size(33))
        self.mode_dropdown.setCursor(QtCore.Qt.PointingHandCursor)
        self.mode_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #2A2A3D;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 5px 11px;
                font-size: 8pt;
            }
            QComboBox:hover {
                background-color: #3A3A4D;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3D;
                color: #FFFFFF;
                selection-background-color: #4A7AC9;
                border: none;
                font-size: 8pt;
            }
        """)
        self.mode_dropdown.currentTextChanged.connect(self.on_mode_changed)
        layout.addWidget(self.mode_dropdown)
        
        layout.addSpacing(scale_size(8))
        
        copy_paste_container = QtWidgets.QWidget()
        copy_paste_layout = QtWidgets.QHBoxLayout(copy_paste_container)
        copy_paste_layout.setContentsMargins(0, 0, 0, 0)
        copy_paste_layout.setSpacing(scale_size(7))
        
        self.copy_button = QtWidgets.QPushButton("C O P Y")
        self.copy_button.setFixedHeight(scale_size(35))
        self.copy_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3D;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #3A3A4D;
            }
            QPushButton:pressed {
                background-color: #1A1A2D;
            }
        """)
        self.copy_button.clicked.connect(self.copy_action)
        copy_paste_layout.addWidget(self.copy_button)
        
        self.paste_button = QtWidgets.QPushButton("P A S T E")
        self.paste_button.setFixedHeight(scale_size(35))
        self.paste_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.paste_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3D;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #3A3A4D;
            }
            QPushButton:pressed {
                background-color: #1A1A2D;
            }
        """)
        self.paste_button.clicked.connect(self.paste_action)
        copy_paste_layout.addWidget(self.paste_button)
        
        layout.addWidget(copy_paste_container)
        
        layout.addSpacing(scale_size(8))
        
        self.update_layer_button = QtWidgets.QPushButton("U P D A T E   S E L E C T E D   L A Y E R")
        self.update_layer_button.setFixedHeight(scale_size(35))
        self.update_layer_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_layer_button.setStyleSheet("""
            QPushButton {
                background-color: #4A7AC9;
                border: none;
                color: #FFFFFF;
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #5A8AD9;
            }
            QPushButton:pressed {
                background-color: #3A6AB9;
            }
        """)
        self.update_layer_button.clicked.connect(self.update_layer_action)
        layout.addWidget(self.update_layer_button)
        
        return widget
    
    def create_camera_view(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(scale_size(8))
        
        cam_container = QtWidgets.QWidget()
        cam_layout = QtWidgets.QHBoxLayout(cam_container)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_layout.setSpacing(scale_size(7))
        
        self.assign_cam_button = QtWidgets.QPushButton("Camera")
        self.assign_cam_button.setFixedHeight(scale_size(30))
        self.assign_cam_button.setFixedWidth(scale_size(80))
        self.assign_cam_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.assign_cam_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3D;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3A3A4D;
            }
            QPushButton:pressed {
                background-color: #1A1A2D;
            }
        """)
        self.assign_cam_button.clicked.connect(self.assign_camera)
        cam_layout.addWidget(self.assign_cam_button)
        
        self.camera_field = QtWidgets.QLineEdit()
        self.camera_field.setFixedHeight(scale_size(30))
        self.camera_field.setStyleSheet("""
            QLineEdit {
                background-color: #252530;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 5px 10px;
                font-size: 8pt;
            }
        """)
        self.camera_field.textChanged.connect(self.save_camera_master_fields)
        cam_layout.addWidget(self.camera_field)
        
        layout.addWidget(cam_container)
        
        master_container = QtWidgets.QWidget()
        master_layout = QtWidgets.QHBoxLayout(master_container)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(scale_size(7))
        
        self.assign_master_button = QtWidgets.QPushButton("Master")
        self.assign_master_button.setFixedHeight(scale_size(30))
        self.assign_master_button.setFixedWidth(scale_size(80))
        self.assign_master_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.assign_master_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3D;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3A3A4D;
            }
            QPushButton:pressed {
                background-color: #1A1A2D;
            }
        """)
        self.assign_master_button.clicked.connect(self.assign_master_ctrl)
        master_layout.addWidget(self.assign_master_button)
        
        self.master_field = QtWidgets.QLineEdit()
        self.master_field.setFixedHeight(scale_size(30))
        self.master_field.setStyleSheet("""
            QLineEdit {
                background-color: #252530;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 5px 10px;
                font-size: 8pt;
            }
        """)
        self.master_field.textChanged.connect(self.save_camera_master_fields)
        master_layout.addWidget(self.master_field)
        
        layout.addWidget(master_container)
        
        keys_container = QtWidgets.QWidget()
        keys_layout = QtWidgets.QHBoxLayout(keys_container)
        keys_layout.setContentsMargins(0, 0, 0, 0)
        keys_layout.setSpacing(scale_size(7))
        
        self.assign_keys_button = QtWidgets.QPushButton("Keys")
        self.assign_keys_button.setFixedHeight(scale_size(30))
        self.assign_keys_button.setFixedWidth(scale_size(80))
        self.assign_keys_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.assign_keys_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3D;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3A3A4D;
            }
            QPushButton:pressed {
                background-color: #1A1A2D;
            }
        """)
        self.assign_keys_button.clicked.connect(self.assign_keys_time)
        keys_layout.addWidget(self.assign_keys_button)
        
        self.keys_field = QtWidgets.QLineEdit()
        self.keys_field.setFixedHeight(scale_size(30))
        self.keys_field.setStyleSheet("""
            QLineEdit {
                background-color: #252530;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 5px 10px;
                font-size: 8pt;
            }
        """)
        keys_layout.addWidget(self.keys_field)
        
        layout.addWidget(keys_container)
        
        layout.addSpacing(scale_size(10))
        
        self.attach_cam_button = QtWidgets.QPushButton("A T T A C H   T O   C A M E R A")
        self.attach_cam_button.setFixedHeight(scale_size(35))
        self.attach_cam_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.attach_cam_button.setStyleSheet("""
            QPushButton {
                background-color: #4A7AC9;
                border: none;
                color: #FFFFFF;
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #5A8AD9;
            }
            QPushButton:pressed {
                background-color: #3A6AB9;
            }
        """)
        self.attach_cam_button.clicked.connect(self.attach_to_camera_action)
        layout.addWidget(self.attach_cam_button)
        
        return widget
    
    def show_anim_layer_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A3D;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4A7AC9;
            }
        """)
        
        add_sel_action = menu.addAction("Add Selection to AnimLayer")
        select_objects_action = menu.addAction("Select Objects in AnimLayer")
        menu.addSeparator()
        keys_1s_action = menu.addAction("Set Keys On 1s")
        keys_2s_action = menu.addAction("Set Keys On 2s")
        keys_3s_action = menu.addAction("Set Keys On 3s")
        keys_4s_action = menu.addAction("Set Keys On 4s")
        keys_5s_action = menu.addAction("Set Keys On 5s")
        keys_6s_action = menu.addAction("Set Keys On 6s")
        keys_23s_action = menu.addAction("Set Keys On 2s-3s")
        keys_34s_action = menu.addAction("Set Keys On 3s-4s")
        
        add_sel_action.triggered.connect(self.add_selection_to_layer)
        select_objects_action.triggered.connect(self.select_objects_in_layer_action)
        keys_1s_action.triggered.connect(self.set_keys_1s)
        keys_2s_action.triggered.connect(self.set_keys_2s)
        keys_3s_action.triggered.connect(self.set_keys_3s)
        keys_4s_action.triggered.connect(self.set_keys_4s)
        keys_5s_action.triggered.connect(self.set_keys_5s)
        keys_6s_action.triggered.connect(self.set_keys_6s)
        keys_23s_action.triggered.connect(self.set_keys_23s)
        keys_34s_action.triggered.connect(self.set_keys_34s)
        
        menu.exec_(self.anim_layer_button.mapToGlobal(pos))
    
    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                color: white;
                border-radius: 14px;
            }
        """)
    
    def apply_rounded_corners(self):
        radius = 14
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    
    def resizeEvent(self, event):
        super(TwosifyUI, self).resizeEvent(event)
        self.apply_rounded_corners()
    
    def fade_to(self, target_opacity, duration=300, easing=None):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        if easing is None:
            self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        else:
            self.anim.setEasingCurve(easing)
        self.anim.start()
    
    def on_view_changed(self, text):
        self.current_view = text
        if text == "Make It Stepped":
            self.section_label.setText("Stepped")
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.section_label.setText("Camera")
            self.stacked_widget.setCurrentIndex(1)
    
    def on_mode_changed(self, text):
        self.current_mode = text
        self.mode_label.setText(text)
    
    def create_anim_layer_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            create_twos_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def add_selection_to_layer(self):
        cmds.undoInfo(openChunk=True)
        try:
            add_selected_to_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_1s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_ones_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_2s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_twos_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_3s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_threes_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_4s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_fours_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_5s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_fives_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_6s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_sixes_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_23s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_twos_threes_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def set_keys_34s(self):
        cmds.undoInfo(openChunk=True)
        try:
            set_keys_threes_fours_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def copy_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            if self.current_mode == "KEYS TIME":
                copy_key_times_script()
            else:
                copy_key_times_smart()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def paste_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            if self.current_mode == "KEYS TIME":
                clean_range_script()
            else:
                paste_key_times_smart()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def update_layer_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            add_selected_to_anim_layer()
            convert_to_twos()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def select_objects_in_layer_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            select_objects_in_selected_anim_layer()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def assign_camera(self):
        selection = cmds.ls(selection=True)
        if selection:
            selected_obj = selection[0]
            is_camera = False
            if cmds.nodeType(selected_obj) == 'camera':
                camera_transform = cmds.listRelatives(selected_obj, parent=True)[0]
                self.camera_field.setText(camera_transform)
                is_camera = True
            elif cmds.listRelatives(selected_obj, shapes=True, type='camera'):
                self.camera_field.setText(selected_obj)
                is_camera = True
            
            if not is_camera:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Invalid Selection")
                msg_box.setText("Please select a camera.")
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: rgb(38, 38, 38);
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                        font-size: 10pt;
                    }
                    QPushButton {
                        background-color: #4A7AC9;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 20px;
                        font-size: 9pt;
                    }
                    QPushButton:hover {
                        background-color: #5A8AD9;
                    }
                """)
                msg_box.exec_()
        self.clear_focus()
    
    def assign_master_ctrl(self):
        selection = cmds.ls(selection=True)
        if selection:
            master_string = ', '.join(selection)
            self.master_field.setText(master_string)
        self.clear_focus()
    
    def assign_keys_time(self):
        selection = cmds.ls(selection=True)
        if selection:
            keys_time = get_keys_time(objs=selection)
            if keys_time:
                keys_string = ', '.join([str(int(key)) for key in keys_time])
                self.keys_field.setText(keys_string)
            else:
                self.keys_field.setText("No keys found")
        self.clear_focus()
    
    def attach_to_camera_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            cam_obj = self.camera_field.text()
            master_text = self.master_field.text()
            keys_time_text = self.keys_field.text()
            
            empty_fields = []
            if not cam_obj or cam_obj.strip() == "":
                empty_fields.append("Camera")
            if not master_text or master_text.strip() == "":
                empty_fields.append("Master")
            if not keys_time_text or keys_time_text.strip() == "":
                empty_fields.append("Keys")
            
            if empty_fields:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Missing Fields")
                msg_box.setText("Please fill in the following fields:\n" + ", ".join(empty_fields))
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: rgb(38, 38, 38);
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                        font-size: 10pt;
                    }
                    QPushButton {
                        background-color: #4A7AC9;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 20px;
                        font-size: 9pt;
                    }
                    QPushButton:hover {
                        background-color: #5A8AD9;
                    }
                """)
                msg_box.exec_()
                cmds.undoInfo(closeChunk=True)
                self.clear_focus()
                return
            
            is_camera = False
            if cmds.objExists(cam_obj):
                if cmds.nodeType(cam_obj) == 'camera':
                    is_camera = True
                elif cmds.listRelatives(cam_obj, shapes=True, type='camera'):
                    is_camera = True
            
            if not is_camera:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Invalid Camera")
                msg_box.setText("The Camera field must contain a valid camera.")
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: rgb(38, 38, 38);
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                        font-size: 10pt;
                    }
                    QPushButton {
                        background-color: #4A7AC9;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 20px;
                        font-size: 9pt;
                    }
                    QPushButton:hover {
                        background-color: #5A8AD9;
                    }
                """)
                msg_box.exec_()
                cmds.undoInfo(closeChunk=True)
                self.clear_focus()
                return
            
            master_list = [m.strip() for m in master_text.split(',') if m.strip()]
            valid_masters = [m for m in master_list if m != cam_obj.strip() and cmds.objExists(m)]
            
            if not valid_masters:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Invalid Selection")
                msg_box.setText("No valid Master objects found. Objects must exist and cannot be the same as the Camera.")
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: rgb(38, 38, 38);
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                        font-size: 10pt;
                    }
                    QPushButton {
                        background-color: #4A7AC9;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 20px;
                        font-size: 9pt;
                    }
                    QPushButton:hover {
                        background-color: #5A8AD9;
                    }
                """)
                msg_box.exec_()
                cmds.undoInfo(closeChunk=True)
                self.clear_focus()
                return
            
            sel = cmds.ls(sl=True)
            for s in sel:
                if cmds.objExists(s + "_esn_cam_attach_01"):
                    cmds.confirmDialog(
                        title='Warning',
                        message='You have already done a setup on the selected objects. \n Please remove the old setup.',
                        button=['OK'],
                        defaultButton='OK',
                        icon='warning'
                    )
                    return
            
            try:
                keys_time = [float(key.strip()) for key in keys_time_text.split(',') if key.strip()]
            except ValueError:
                return
            
            cmds.currentTime(keys_time[0])
            
            if not cmds.objExists(cam_obj):
                return
            
            follow_cam_grp = "FOLLOW_CAM_GRP"
            if not cmds.objExists(follow_cam_grp):
                cmds.group(n=follow_cam_grp, empty=True)
                try:
                    set_outliner_color("FOLLOW_CAM_GRP", (0.75, 0.5, 0.9))
                except Exception:
                    pass
            
            for master_obj in valid_masters:
                if not cmds.objExists(master_obj):
                    continue
                
                circle_ctrl = create_circle(master_name=master_obj)
                loc_ctrl = create_locator()
                
                cmds.parent(loc_ctrl, circle_ctrl)
                cmds.parent(circle_ctrl, follow_cam_grp)
                
                smart_constraint_create_attach_cam(cam_obj, circle_ctrl)
                
                for axis in ['X', 'Y', 'Z']:
                    tran_attr = circle_ctrl + ".translate" + axis
                    cmds.setAttr(tran_attr, keyable=False)
                    cmds.setAttr(tran_attr, channelBox=False)
                
                for axis in ['X', 'Y', 'Z']:
                    rot_attr = circle_ctrl + ".rotate" + axis
                    cmds.setAttr(rot_attr, keyable=False)
                    cmds.setAttr(rot_attr, channelBox=False)
                
                try:
                    cmds.refresh(suspend=True)
                    cmds.evaluationManager(mode="off")
                    cmds.waitCursor(state=True)
                    cur_time = cmds.currentTime(q=True)
                    
                    for key in keys_time:
                        cmds.currentTime(key)
                        cmds.matchTransform(loc_ctrl, master_obj, pos=True, rot=True)
                        cmds.setKeyframe(loc_ctrl, at=("tx", "ty", "tz", "rx", "ry", "rz"))
                    
                    cmds.currentTime(cur_time)
                    cmds.refresh(suspend=False)
                    cmds.evaluationManager(mode="parallel")
                    cmds.waitCursor(state=False)
                except Exception:
                    cmds.refresh(suspend=False)
                    cmds.evaluationManager(mode="parallel")
                    cmds.waitCursor(state=False)
                    continue
                
                cmds.keyTangent(loc_ctrl, at=("tx", "ty", "tz", "rx", "ry", "rz"), itt="auto", ott="step")
                
                master_keys = cmds.keyframe(master_obj, query=True, timeChange=True) or []
                if not master_keys:
                    cmds.setKeyframe(master_obj, at=("tx", "ty", "tz", "rx", "ry", "rz"))
                
                constraints = simple_smart_constraint(loc_ctrl, master_obj, connect_to_attach_cam=True, attach_cam_object=circle_ctrl)
                
                if constraints:
                    if cmds.attributeQuery('blendParent1', node=master_obj, exists=True):
                        if not master_keys:
                            cmds.setAttr("{}.blendParent1".format(master_obj), 1)
                        
                        if cmds.attributeQuery('Attach_Cam', node=circle_ctrl, exists=True):
                            try:
                                cmds.connectAttr("{}.Attach_Cam".format(circle_ctrl), "{}.blendParent1".format(master_obj), force=True)
                            except Exception:
                                pass
            self.keys_field.setText("")
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def save_camera_master_fields(self):
        try:
            save_twosify_camera_master(self.camera_field.text(), self.master_field.text())
        except Exception:
            pass
    
    def load_camera_master_fields(self):
        try:
            camera_text, master_text = load_twosify_camera_master()
            if camera_text:
                self.camera_field.setText(camera_text)
            if master_text:
                self.master_field.setText(master_text)
        except Exception:
            pass
    
    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass
    
    def restore_position(self):
        saved_pos = load_window_position()
        if saved_pos:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen().geometry()
            else:
                screen = QtWidgets.QApplication.desktop().screenGeometry()
            
            window_width = self.width()
            window_height = self.height()
            
            if (saved_pos.x() >= 0 and saved_pos.y() >= 0 and
                saved_pos.x() < screen.width() - window_width and
                saved_pos.y() < screen.height() - window_height):
                self.move(saved_pos)
    
    def closeEvent(self, event):
        save_window_position(self.pos())
        super(TwosifyUI, self).closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'globalPosition'):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, 'globalPosition'):
                delta = event.globalPosition().toPoint() - self.old_pos
                self.old_pos = event.globalPosition().toPoint()
            else:
                delta = event.globalPos() - self.old_pos
                self.old_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
    def enterEvent(self, event):
        self.fade_to(0.87, 50, QtCore.QEasingCurve.OutQuad)
        super(TwosifyUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.fade_to(0.77, 300)
        super(TwosifyUI, self).leaveEvent(event)


twosify_ui_instance = None


def create_twosify_ui():
    global twosify_ui_instance
    
    if twosify_ui_instance is not None:
        try:
            twosify_ui_instance.close()
            twosify_ui_instance.deleteLater()
        except Exception:
            pass
        twosify_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "TwosifyUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    twosify_ui_instance = TwosifyUI()
    twosify_ui_instance.show()
    return twosify_ui_instance


def ui():
    return create_twosify_ui()


create_twosify_ui()