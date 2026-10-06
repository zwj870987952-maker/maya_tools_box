

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from maya import mel
import maya.utils
import sys
import platform
import time

try:
    import __builtin__ as builtins
except ImportError:
    import builtins
try:
    max = builtins.max 
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass

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

IS_MACOS = platform.system() == "Darwin"
try:
    MAYA_VERSION = int(cmds.about(version=True))
except:
    MAYA_VERSION = 2020









def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except:
        return 2022


BASE_DPI = 96.0
_scale_factor = None
_cursor_position = None

def get_scale_factor():
    global _scale_factor, _cursor_position
    
    try:
        current_cursor = QtGui.QCursor.pos()
        if _cursor_position is not None and _scale_factor is not None:
            if abs(current_cursor.x() - _cursor_position.x()) < 100 and \
               abs(current_cursor.y() - _cursor_position.y()) < 100:
                return _scale_factor
        _cursor_position = current_cursor
    except:
        if _scale_factor is not None:
            return _scale_factor
    
    try:
        app = QtWidgets.QApplication.instance()
        raw_scale = 1.0
        
        if app:
            screen = None
            
            if PYSIDE_VERSION == 6:
                screen = app.screenAt(current_cursor)
                if not screen:
                    screen = QGuiApplication.primaryScreen()
            else:
                if hasattr(app, 'screenAt'):
                    screen = app.screenAt(current_cursor)
                if not screen and hasattr(app, 'primaryScreen'):
                    screen = app.primaryScreen()
            
            if screen:
                device_ratio = screen.devicePixelRatio()
                logical_dpi = screen.logicalDotsPerInch() / BASE_DPI
                raw_scale = max(device_ratio, logical_dpi)
            else:
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    raw_scale = desktop.logicalDpiX() / BASE_DPI
        
        base_size = 1.08
        
        if raw_scale > 1.0:
            _scale_factor = base_size * raw_scale * 1.05
        else:
            _scale_factor = base_size
            
    except:
        _scale_factor = 0.9
    
    return _scale_factor

def reset_scale_factor():
    global _scale_factor, _cursor_position
    _scale_factor = None
    _cursor_position = None

def dpi(value):
    return int(value * get_scale_factor())

def scale_size(size):
    return dpi(size)

_left_dragging = False
_left_original_values = {}
_left_pivot_values = {}
_left_stored_keys_sel = []
_left_stored_anim_curves = []
_left_stored_key_indexes = {}
_left_last_scale_value = 1.0

_right_dragging = False
_right_original_values = {}
_right_pivot_values = {}
_right_stored_keys_sel = []
_right_stored_anim_curves = []
_right_stored_key_indexes = {}
_right_last_scale_value = 1.0
_right_keys_created_at_current_time = {}

_avg_original_values = {}
_avg_dragging = False
_avg_stored_keys_sel = []
_avg_stored_anim_curves = []
_avg_stored_key_indexes = {}
_avg_last_scale_value = 1.0

pushClick = False
openChunk = True
originalValues = {}
storedSelection = []
storedAnimCurves = []
storedKeysSel = []

blendPushClick = False
blendOpenChunk = True
blendStoredKeyValues = {}
blendStoredKeyTimes = {}
blendStoredIndexes = {}
blendStoredAnimCurves = []
blendStoredKeysSel = []
blendLastValue = 0
blendScaleValue = 1

cascadePushClick = False
cascadeOpenChunk = True
cascadeStoredKeyValues = {}
cascadeStoredAnimCurves = []
cascadeStoredKeysSel = []

def safe_undo_chunk_close():
    try:
        if IS_MACOS:
            cmds.refresh()
            maya.utils.processIdleEvents()
        cmds.undoInfo(closeChunk=True)
    except:
        pass

def safe_undo_chunk_open(chunk_name="Tween Operation"):
    try:
        cmds.undoInfo(openChunk=True, chunkName=chunk_name)
        if IS_MACOS:
            maya.utils.processIdleEvents()
    except:
        pass

def set_key_tangents_smart(curves_and_times):
    if not curves_and_times:
        return
    
    step_count = 0
    checked_count = 0
    max_check_threshold = 30
    
    
    for curve, key_times in curves_and_times.items():
        if checked_count >= max_check_threshold:
            break
            
        try:
            all_keys = cmds.keyframe(curve, query=True, timeChange=True)
            if not all_keys or len(all_keys) < 2:
                continue
            
            for key_time in key_times:
                current_key_index = None
                for i, kt in enumerate(all_keys):
                    if abs(kt - key_time) < 0.001:
                        current_key_index = i
                        break
                
                if current_key_index is None:
                    continue
                
                checked_count += 1
                
                if current_key_index > 0:
                    prev_out_tangent = cmds.keyTangent(curve, index=(current_key_index-1,), 
                                                     query=True, outTangentType=True)
                    if prev_out_tangent and prev_out_tangent[0] == 'step':
                        step_count += 1
                
                if current_key_index < len(all_keys) - 1:
                    next_in_tangent = cmds.keyTangent(curve, index=(current_key_index+1,), 
                                                    query=True, inTangentType=True)
                    if next_in_tangent and next_in_tangent[0] == 'step':
                        step_count += 1
                
                if checked_count >= max_check_threshold:
                    break
        except:
            continue
    
    
    if step_count >= max_check_threshold:
        for curve, key_times in curves_and_times.items():
            try:
                all_keys = cmds.keyframe(curve, query=True, timeChange=True)
                if not all_keys:
                    continue
                
                for key_time in key_times:
                    current_key_index = None
                    for i, kt in enumerate(all_keys):
                        if abs(kt - key_time) < 0.001:
                            current_key_index = i
                            break
                    
                    if current_key_index is not None:
                        cmds.keyTangent(curve, index=(current_key_index,), 
                                      outTangentType='step')
            except:
                continue
    else:
        for curve, key_times in curves_and_times.items():
            try:
                all_keys = cmds.keyframe(curve, query=True, timeChange=True)
                if not all_keys or len(all_keys) < 2:
                    continue
                
                for key_time in key_times:
                    current_key_index = None
                    for i, kt in enumerate(all_keys):
                        if abs(kt - key_time) < 0.001:
                            current_key_index = i
                            break
                    
                    if current_key_index is None:
                        continue
                        
                    prev_is_step = False
                    next_is_step = False
                    
                    if current_key_index > 0:
                        prev_out_tangent = cmds.keyTangent(curve, index=(current_key_index-1,), 
                                                         query=True, outTangentType=True)
                        if prev_out_tangent and prev_out_tangent[0] == 'step':
                            prev_is_step = True
                    
                    if current_key_index < len(all_keys) - 1:
                        next_in_tangent = cmds.keyTangent(curve, index=(current_key_index+1,), 
                                                        query=True, inTangentType=True)
                        if next_in_tangent and next_in_tangent[0] == 'step':
                            next_is_step = True
                    
                    if prev_is_step or next_is_step:
                        cmds.keyTangent(curve, index=(current_key_index,), 
                                      outTangentType='step')
            except:
                continue

def copy_current_keyframe():
    current_time = cmds.currentTime(q=True)

    selection = cmds.ls(sl=True)
    if not selection:
        cmds.warning("No object selected.")
        return

    copy_data = []

    for obj in selection:
        anim_curves = cmds.listConnections(obj, type='animCurve', d=False, s=True) or []
        for curve in anim_curves:
            try:
                connections = cmds.listConnections(curve + ".output", plugs=True)
                if connections:
                    attr = connections[0]
                    value = cmds.getAttr(attr, time=current_time)
                    copy_data.append("{0}|{1}|{2}".format(attr, value, current_time))
            except:
                continue

    if copy_data:
        cmds.optionVar(stringArray=('tweenMachine_copyData', copy_data))
    else:
        cmds.warning("No animation data found to copy.")

def get_anim_curves():
    anim_curves = cmds.keyframe(query=True, name=True, selected=True)
    get_from = "graphEditor"
    
    if not anim_curves:
        get_from = "channelBox"
        selected_objects = cmds.ls(selection=True)
        
        if selected_objects:
            channel_box = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
            selected_attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True)
            
            if selected_attrs:
                anim_curves = []
                for obj in selected_objects:
                    for attr in selected_attrs:
                        connections = cmds.listConnections(
                            '{}.{}'.format(obj, attr),
                            source=True,
                            destination=False,
                            type='animCurve'
                        )
                        if connections:
                            anim_curves.extend(connections)
                
                if anim_curves:
                    anim_curves = list(set(anim_curves))
    
    if not anim_curves:
        get_from = "timeline"
        play_back_slider = mel.eval('$temp=$gPlayBackSlider')
        anim_curves = cmds.timeControl(play_back_slider, query=True, animCurveNames=True)
    
    return [anim_curves, get_from]

def get_timeline_range():
    play_back_slider = mel.eval('$temp_playBackSlider=$gPlayBackSlider')
    time_range = cmds.timeControl(play_back_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return [start_range, end_range]

def get_keys_sel(anim_curves, get_from):
    if not anim_curves:
        return []
    
    keys_sel = []
    if get_from == "graphEditor":
        for node in anim_curves:
            keys = cmds.keyframe(node, selected=True, query=True, timeChange=True)
            keys_sel.append(keys if keys else [])
    else:
        range_val = get_timeline_range()
        for node in anim_curves:
            if not cmds.objExists(node):
                keys_sel.append([])
                continue
                
            all_keys = cmds.keyframe(node, query=True, timeChange=True)
            if all_keys:
                range_keys = [k for k in all_keys if range_val[0] <= k < range_val[1]]
                keys_sel.append(range_keys)
            else:
                keys_sel.append([])
    return keys_sel

def get_key_indexes(curve, key_times):
    if not cmds.objExists(curve) or not key_times:
        return []
    
    all_key_times = cmds.keyframe(curve, query=True, timeChange=True)
    if not all_key_times:
        return []
    
    indexes = []
    for key_time in key_times:
        for i, curve_time in enumerate(all_key_times):
            if abs(key_time - curve_time) < 0.001:
                indexes.append(i)
                break
    return indexes

def setup_blend_key_transform_data():
    global blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
    
    blendStoredKeyValues = {}
    blendStoredKeyTimes = {}
    blendStoredIndexes = {}
    
    for n, curve in enumerate(blendStoredAnimCurves):
        if not cmds.objExists(curve) or not blendStoredKeysSel[n]:
            continue
            
        keyValues = cmds.keyframe(curve, query=True, valueChange=True)
        keyTimes = cmds.keyframe(curve, query=True, timeChange=True)
        
        if not keyValues or not keyTimes:
            continue
        
        if len(keyTimes) == 1:
            inOffsetTime = 1
            inOffsetVal = 0  
            outOffsetTime = 1
            outOffsetVal = 0                    
        else:                        
            inOffsetTime = keyTimes[1] - keyTimes[0]
            inOffsetVal = keyValues[1] - keyValues[0]
            outOffsetTime = keyTimes[-1] - keyTimes[-2]
            outOffsetVal = keyValues[-1] - keyValues[-2]
        
        keyValues.insert(0, keyValues[0] - inOffsetVal)
        keyTimes.insert(0, keyTimes[0] - inOffsetTime)
        keyValues.insert(0, keyValues[0] - inOffsetVal)
        keyTimes.insert(0, keyTimes[0] - inOffsetTime)
        
        keyValues.append(keyValues[-1] + outOffsetVal)
        keyTimes.append(keyTimes[-1] + outOffsetTime)
        keyValues.append(keyValues[-1] + outOffsetVal)
        keyTimes.append(keyTimes[-1] + outOffsetTime)
        
        blendStoredKeyValues[curve] = keyValues
        blendStoredKeyTimes[curve] = keyTimes
        
        indexes = []
        keysSelTemp = list(blendStoredKeysSel[n])
        
        firstTime = True
        for i, keyTime in enumerate(keyTimes):
            for j, selTime in enumerate(keysSelTemp):
                if abs(selTime - keyTime) < 0.001:
                    if firstTime:
                        indexes.append([])
                        firstTime = False
                    indexes[-1].append(i)
                    keysSelTemp.pop(j)
                    break
            else:
                firstTime = True
        
        for i, segment in enumerate(indexes):
            indexes[i].insert(0, segment[0] - 1)
            indexes[i].append(segment[-1] + 1)
        
        blendStoredIndexes[curve] = indexes

def execute_blend_key_transform(slider_val):
    global blendLastValue, blendScaleValue
    
    if not blendStoredAnimCurves:
        return
    
    tValue = (slider_val + 100) / 100.0
    
    if tValue <= 1: 
        p = tValue
    else:          
        p = 2 - tValue
    
    if p == 0:
        p = 0.0000001
    
    if blendPushClick and blendLastValue != 0:
        blendScaleValue = (1.0 / blendLastValue) * p
    else:
        blendScaleValue = p
    
    for n, curve in enumerate(blendStoredAnimCurves):
        if curve not in blendStoredIndexes or not cmds.objExists(curve):
            continue
            
        keyValues = blendStoredKeyValues[curve]
        keyTimes = blendStoredKeyTimes[curve]
        segments = blendStoredIndexes[curve]
        
        for s, segment in enumerate(segments):
            fv = keyValues[segment[0]]
            lv = keyValues[segment[-1]]
            
            has_real_left_neighbor = segment[0] > 1
            has_real_right_neighbor = segment[-1] < len(keyValues) - 2
            
            if not has_real_left_neighbor and not has_real_right_neighbor:
                selected_keys_in_segment = segment[1:-1]
                if len(selected_keys_in_segment) >= 2:
                    fv = keyValues[selected_keys_in_segment[0]]
                    lv = keyValues[selected_keys_in_segment[-1]]
            elif not has_real_left_neighbor and len(segment) > 3:
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    fv = keyValues[selected_keys_in_segment[0]]
            elif not has_real_right_neighbor and len(segment) > 3:
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    lv = keyValues[selected_keys_in_segment[-1]]
            
            if tValue <= 1:
                pivot = fv
            else:
                pivot = lv
            
            for i, keyIndex in enumerate(segment):
                if 1 <= i <= len(segment) - 2:
                    realIndex = keyIndex - 2
                    
                    if 0 <= realIndex < len(cmds.keyframe(curve, query=True, timeChange=True) or []):
                        try:
                            cmds.scaleKey(curve, index=(realIndex, realIndex), 
                                        valuePivot=pivot, valueScale=blendScaleValue)
                        except:
                            try:
                                currentVal = cmds.keyframe(curve, index=(realIndex, realIndex), 
                                                         query=True, valueChange=True)[0]
                                newValue = pivot + (currentVal - pivot) * blendScaleValue
                                cmds.keyframe(curve, edit=True, index=(realIndex, realIndex), 
                                            valueChange=newValue)
                            except:
                                continue
    
    blendLastValue = p

def set_step_tangents_if_needed_right():
    pass

def cache_left_original_values():
    global _left_original_values, _left_pivot_values, _left_stored_keys_sel, _left_stored_anim_curves
    global _left_stored_key_indexes, _left_last_scale_value
    
    _left_original_values = {}
    _left_pivot_values = {}
    _left_stored_key_indexes = {}
    _left_last_scale_value = 1.0
    
    get_curves = get_anim_curves()
    _left_stored_anim_curves = get_curves[0]
    get_from = get_curves[1]
    
    if not _left_stored_anim_curves:
        return
        
    _left_stored_keys_sel = get_keys_sel(_left_stored_anim_curves, get_from)
    
    has_selected_keys = any(key_list for key_list in _left_stored_keys_sel if key_list)
    
    if not has_selected_keys:
        current_time = cmds.currentTime(query=True)
        curves_with_new_keys = {}
        for curve in _left_stored_anim_curves:
            if cmds.objExists(curve):
                existing_keys = cmds.keyframe(curve, query=True, timeChange=True)
                key_exists = existing_keys and current_time in existing_keys
                
                cmds.setKeyframe(curve, time=current_time, insert=True)
                
                if not key_exists:
                    curves_with_new_keys[curve] = [current_time]
        
        if curves_with_new_keys:
            for curve, times in curves_with_new_keys.items():
                for key_time in times:
                    prev_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="next")
                    
                    in_tangent_type = "auto"
                    out_tangent_type = "auto"
                    step_detected = False
                    
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key),
                                                               query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    if not step_detected and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key),
                                                               query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    cmds.keyTangent(curve, time=(key_time, key_time),
                                   inTangentType=in_tangent_type, outTangentType=out_tangent_type)
        
        _left_stored_keys_sel = []
        for curve in _left_stored_anim_curves:
            if cmds.objExists(curve):
                _left_stored_keys_sel.append([current_time])
            else:
                _left_stored_keys_sel.append([])
    
    for n, curve in enumerate(_left_stored_anim_curves):
        if not cmds.objExists(curve) or not _left_stored_keys_sel[n]:
            continue
        
        sel_times = _left_stored_keys_sel[n]
        
        _left_stored_key_indexes[curve] = get_key_indexes(curve, sel_times)
        
        original_pairs = []
        for time_val in sel_times:
            try:
                value = cmds.keyframe(curve, time=(time_val, time_val), q=True, valueChange=True)[0]
                original_pairs.append((time_val, value))
            except:
                continue
        
        if not original_pairs:
            continue
            
        _left_original_values[curve] = original_pairs
        
        first_time = sel_times[0]
        prev_keys = cmds.keyframe(curve, q=True, time=(-99999, first_time-0.01), timeChange=True)
        if prev_keys:
            pivot_val = cmds.keyframe(curve, time=(prev_keys[-1], prev_keys[-1]), q=True, valueChange=True)[0]
        else:
            pivot_val = original_pairs[0][1]
        _left_pivot_values[curve] = pivot_val

def scale_left_keys(slider_val):
    global _left_original_values, _left_pivot_values, _left_stored_key_indexes, _left_last_scale_value
    
    if not _left_original_values:
        cache_left_original_values()
    if not _left_original_values:
        return

    if slider_val >= 0:
        scale_factor = 1 + slider_val
    else:
        scale_factor = 1 + slider_val * 2

    if abs(_left_last_scale_value) > 0.0001:
        relative_scale = scale_factor / _left_last_scale_value
    else:
        relative_scale = scale_factor

    for curve in _left_original_values:
        if not cmds.objExists(curve):
            continue
            
        pivot_val = _left_pivot_values[curve]
        key_indexes = _left_stored_key_indexes.get(curve, [])
        
        if key_indexes:
            try:
                for key_index in key_indexes:
                    cmds.scaleKey(curve, index=(key_index, key_index), 
                                valuePivot=pivot_val, valueScale=relative_scale)
            except:
                tvs = _left_original_values[curve]
                for i, (t, orig_val) in enumerate(tvs):
                    distance = orig_val - pivot_val
                    new_val = pivot_val + distance * scale_factor
                    try:
                        cmds.keyframe(curve, edit=True, time=(t,t), valueChange=new_val)
                    except:
                        continue
        else:
            tvs = _left_original_values[curve]
            for i, (t, orig_val) in enumerate(tvs):
                distance = orig_val - pivot_val
                new_val = pivot_val + distance * scale_factor
                try:
                    cmds.keyframe(curve, edit=True, time=(t,t), valueChange=new_val)
                except:
                    continue
    
    _left_last_scale_value = scale_factor

def cache_right_original_values():
    global _right_original_values, _right_pivot_values, _right_stored_keys_sel, _right_stored_anim_curves
    global _right_stored_key_indexes, _right_last_scale_value, _right_keys_created_at_current_time
    
    _right_original_values = {}
    _right_pivot_values = {}
    _right_stored_key_indexes = {}
    _right_last_scale_value = 1.0
    _right_keys_created_at_current_time = {}
    
    get_curves = get_anim_curves()
    _right_stored_anim_curves = get_curves[0]
    get_from = get_curves[1]
    
    if not _right_stored_anim_curves:
        return
        
    _right_stored_keys_sel = get_keys_sel(_right_stored_anim_curves, get_from)
    
    has_selected_keys = any(key_list for key_list in _right_stored_keys_sel if key_list)
    
    if not has_selected_keys:
        current_time = cmds.currentTime(query=True)
        for curve in _right_stored_anim_curves:
            if cmds.objExists(curve):
                existing_keys = cmds.keyframe(curve, query=True, timeChange=True)
                key_exists = existing_keys and current_time in existing_keys
                
                cmds.setKeyframe(curve, time=current_time, insert=True)
                
                _right_keys_created_at_current_time[curve] = not key_exists
        
        curves_with_new_keys = {}
        for curve, was_created in _right_keys_created_at_current_time.items():
            if was_created:
                curves_with_new_keys[curve] = [current_time]
        
        if curves_with_new_keys:
            for curve, times in curves_with_new_keys.items():
                for key_time in times:
                    prev_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="next")
                    
                    in_tangent_type = "auto"
                    out_tangent_type = "auto"
                    step_detected = False
                    
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key),
                                                               query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    if not step_detected and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key),
                                                               query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    cmds.keyTangent(curve, time=(key_time, key_time),
                                   inTangentType=in_tangent_type, outTangentType=out_tangent_type)
        
        _right_stored_keys_sel = []
        for curve in _right_stored_anim_curves:
            if cmds.objExists(curve):
                _right_stored_keys_sel.append([current_time])
            else:
                _right_stored_keys_sel.append([])
    
    for n, curve in enumerate(_right_stored_anim_curves):
        if not cmds.objExists(curve) or not _right_stored_keys_sel[n]:
            continue
        
        sel_times = _right_stored_keys_sel[n]
        
        _right_stored_key_indexes[curve] = get_key_indexes(curve, sel_times)
        
        original_pairs = []
        for time_val in sel_times:
            try:
                value = cmds.keyframe(curve, time=(time_val, time_val), q=True, valueChange=True)[0]
                original_pairs.append((time_val, value))
            except:
                continue
        
        if not original_pairs:
            continue
            
        _right_original_values[curve] = original_pairs
        
        last_time = sel_times[-1]
        next_keys = cmds.keyframe(curve, q=True, time=(last_time+0.01, 99999), timeChange=True)
        if next_keys:
            pivot_val = cmds.keyframe(curve, time=(next_keys[0], next_keys[0]), q=True, valueChange=True)[0]
        else:
            pivot_val = original_pairs[-1][1]
        _right_pivot_values[curve] = pivot_val

def scale_right_keys(slider_val):
    global _right_original_values, _right_pivot_values, _right_stored_key_indexes, _right_last_scale_value
    if not _right_original_values:
        cache_right_original_values()
    if not _right_original_values:
        return

    if slider_val >= 0:
        scale_factor = 1 + slider_val
    else:
        scale_factor = 1 + slider_val * 2

    if abs(_right_last_scale_value) > 0.0001:
        relative_scale = scale_factor / _right_last_scale_value
    else:
        relative_scale = scale_factor

    for curve in _right_original_values:
        if not cmds.objExists(curve):
            continue
            
        pivot_val = _right_pivot_values[curve]
        key_indexes = _right_stored_key_indexes.get(curve, [])
        
        if key_indexes:
            try:
                for key_index in key_indexes:
                    cmds.scaleKey(curve, index=(key_index, key_index), 
                                valuePivot=pivot_val, valueScale=relative_scale)
            except:
                tvs = _right_original_values[curve]
                for i, (t, orig_val) in enumerate(tvs):
                    distance = orig_val - pivot_val
                    new_val = pivot_val + distance * scale_factor
                    try:
                        cmds.keyframe(curve, edit=True, time=(t,t), valueChange=new_val)
                    except:
                        continue
        else:
            tvs = _right_original_values[curve]
            for i, (t, orig_val) in enumerate(tvs):
                distance = orig_val - pivot_val
                new_val = pivot_val + distance * scale_factor
                try:
                    cmds.keyframe(curve, edit=True, time=(t,t), valueChange=new_val)
                except:
                    continue
    
    _right_last_scale_value = scale_factor

def cache_avg_original_values():
    global _avg_original_values, _avg_stored_keys_sel, _avg_stored_anim_curves, _avg_stored_key_indexes, _avg_last_scale_value
    _avg_original_values = {}
    _avg_stored_key_indexes = {}
    _avg_last_scale_value = 1.0
    
    get_curves = get_anim_curves()
    _avg_stored_anim_curves = get_curves[0]
    get_from = get_curves[1]
    
    if not _avg_stored_anim_curves:
        return
        
    _avg_stored_keys_sel = get_keys_sel(_avg_stored_anim_curves, get_from)
    
    has_selected_keys = any(key_list for key_list in _avg_stored_keys_sel if key_list)
    
    if not has_selected_keys:
        current_time = cmds.currentTime(query=True)
        curves_with_new_keys = {}
        for curve in _avg_stored_anim_curves:
            if cmds.objExists(curve):
                existing_keys = cmds.keyframe(curve, query=True, timeChange=True)
                key_exists = existing_keys and current_time in existing_keys
                
                cmds.setKeyframe(curve, time=current_time, insert=True)
                
                if not key_exists:
                    curves_with_new_keys[curve] = [current_time]
        
        if curves_with_new_keys:
            for curve, times in curves_with_new_keys.items():
                for key_time in times:
                    prev_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="next")
                    
                    in_tangent_type = "auto"
                    out_tangent_type = "auto"
                    step_detected = False
                    
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key),
                                                               query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    if not step_detected and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key),
                                                               query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                step_detected = True
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    cmds.keyTangent(curve, time=(key_time, key_time),
                                   inTangentType=in_tangent_type, outTangentType=out_tangent_type)
        
        _avg_stored_keys_sel = []
        for curve in _avg_stored_anim_curves:
            if cmds.objExists(curve):
                _avg_stored_keys_sel.append([current_time])
            else:
                _avg_stored_keys_sel.append([])
    
    for n, curve in enumerate(_avg_stored_anim_curves):
        if not cmds.objExists(curve) or not _avg_stored_keys_sel[n]:
            continue
        
        sel_times = _avg_stored_keys_sel[n]
        
        _avg_stored_key_indexes[curve] = get_key_indexes(curve, sel_times)
        
        original_pairs = []
        for time_val in sel_times:
            try:
                value = cmds.keyframe(curve, time=(time_val, time_val), q=True, valueChange=True)[0]
                original_pairs.append((time_val, value))
            except:
                continue
        
        if original_pairs:
            _avg_original_values[curve] = original_pairs

def scale_avg_keys(slider_val):
    global _avg_original_values, _avg_stored_key_indexes, _avg_last_scale_value
    if not _avg_original_values:
        cache_avg_original_values()
    if not _avg_original_values:
        return

    if slider_val < 0:
        scale_factor = 1 + slider_val * 2
    else:
        scale_factor = 1 + slider_val

    if abs(_avg_last_scale_value) > 0.0001:
        relative_scale = scale_factor / _avg_last_scale_value
    else:
        relative_scale = scale_factor

    for curve, tvs in _avg_original_values.items():
        if not cmds.objExists(curve):
            continue
            
        values = [v for _, v in tvs]
        key_indexes = _avg_stored_key_indexes.get(curve, [])
        
        if len(values) == 1:
            single_val = values[0]
            single_time = tvs[0][0]
            
            all_keys = cmds.keyframe(curve, query=True, timeChange=True)
            all_values = cmds.keyframe(curve, query=True, valueChange=True)
            
            if all_keys and len(all_keys) > 1:
                try:
                    key_index = all_keys.index(single_time)
                    
                    neighbor_values = []
                    if key_index > 0:
                        neighbor_values.append(all_values[key_index - 1])
                    if key_index < len(all_keys) - 1:
                        neighbor_values.append(all_values[key_index + 1])
                    
                    if neighbor_values:
                        pivot = sum(neighbor_values) / len(neighbor_values)
                    else:
                        pivot = 0.0
                        
                except ValueError:
                    pivot = 0.0
            else:
                pivot = 0.0
            
            if key_indexes:
                try:
                    cmds.scaleKey(curve, index=(key_indexes[0], key_indexes[0]), 
                                valuePivot=pivot, valueScale=relative_scale)
                except:
                    new_val = (single_val - pivot) * scale_factor + pivot
                    try:
                        cmds.keyframe(curve, edit=True, time=(single_time, single_time), valueChange=new_val)
                    except:
                        continue
            else:
                new_val = (single_val - pivot) * scale_factor + pivot
                try:
                    cmds.keyframe(curve, edit=True, time=(single_time, single_time), valueChange=new_val)
                except:
                    continue
                
        else:
            min_val, max_val = min(values), max(values)
            pivot = (min_val + max_val) / 2.0

            if key_indexes:
                try:
                    for key_index in key_indexes:
                        cmds.scaleKey(curve, index=(key_index, key_index), 
                                    valuePivot=pivot, valueScale=relative_scale)
                except:
                    new_values = [(v - pivot) * scale_factor + pivot for _, v in tvs]
                    times = [t for t, _ in tvs]

                    for t, v in zip(times, new_values):
                        try:
                            cmds.keyframe(curve, edit=True, time=(t, t), valueChange=v)
                        except:
                            continue
            else:
                new_values = [(v - pivot) * scale_factor + pivot for _, v in tvs]
                times = [t for t, _ in tvs]

                for t, v in zip(times, new_values):
                    try:
                        cmds.keyframe(curve, edit=True, time=(t, t), valueChange=v)
                    except:
                        continue
    
    _avg_last_scale_value = scale_factor


def copy_current_keyframe():
    global copied_key_data
    
    current_time = cmds.currentTime(q=True)

    selection = cmds.ls(sl=True)
    if not selection:
        cmds.warning("No object selected.")
        return

    copied_key_data = []

    for obj in selection:
        anim_curves = cmds.listConnections(obj, type='animCurve', d=False, s=True) or []
        for curve in anim_curves:
            try:
                attr = cmds.listConnections(curve + ".output", plugs=True)[0]
                value = cmds.getAttr(attr, time=current_time)
                copied_key_data.append((attr, value, current_time))
            except:
                continue

    if not copied_key_data:
        cmds.warning("No animation data found to copy.")

def paste_and_clear_keys():
    global copied_key_data
    
    try:
        if not copied_key_data:
            cmds.warning("No keyframe data found. Please copy a keyframe first.")
            return
    except NameError:
        cmds.warning("No keyframe data found. Please copy a keyframe first.")
        return

    current_time = cmds.currentTime(q=True)

    for attr, value, copied_time in copied_key_data:
        try:
            cmds.setKeyframe(attr, time=current_time, value=value)

            if current_time != copied_time:
                start = min(copied_time, current_time) + 1
                end = max(copied_time, current_time) - 1
                if start <= end:
                    cmds.cutKey(attr, time=(start, end), option="keys")

        except:
            continue

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class CustomSlider(QtWidgets.QSlider):
    def __init__(self, label="EA", handle_color=(80, 200, 120), icon_color=(80, 200, 120), parent=None):
        super(CustomSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        
        self.label_text = label
        self.handle_color = QtGui.QColor(*handle_color)
        self.icon_color = QtGui.QColor(*icon_color)
        
        self.setMinimumHeight(dpi(20))
        self.setMaximumHeight(dpi(20))
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
    def setLabel(self, label):
        self.label_text = label
        self.update()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        icon_size = dpi(5)
        num_dots = 7
        total_items = num_dots + 2
        
        margin = dpi(7)
        available_width = rect.width() - (2 * margin)
        item_spacing = available_width / (total_items - 1)
        
        icon_left = margin
        icon_y = rect.height() // 2 - icon_size // 2
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_left, icon_y, icon_size, icon_size, 1, 1)
        
        track_start = margin + item_spacing
        track_end = rect.width() - margin - item_spacing
        track_y = rect.height() // 2
        
        dot_color = QtGui.QColor(self.handle_color)
        dot_color.setAlpha(180)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        
        dot_spacing = (track_end - track_start) / (num_dots - 1)
        dot_radius = dpi(1.3)
        
        for i in range(num_dots):
            dot_x = track_start + i * dot_spacing
            painter.drawEllipse(QtCore.QPointF(dot_x, track_y), dot_radius, dot_radius)
        
        min_val = self.minimum()
        max_val = self.maximum()
        curr_val = self.value()
        
        if max_val != min_val:
            normalized = float(curr_val - min_val) / float(max_val - min_val)
        else:
            normalized = 0.5
            
        handle_x = track_start + normalized * (track_end - track_start)
        handle_y = track_y
        
        handle_size = dpi(20)
        handle_rect = QtCore.QRectF(
            handle_x - handle_size / 2,
            handle_y - handle_size / 2,
            handle_size,
            handle_size
        )
        
        painter.setBrush(self.handle_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(handle_rect, 3, 3)
        
        painter.setPen(QtGui.QColor(40, 40, 40))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(handle_rect, QtCore.Qt.AlignCenter, self.label_text)
        
        icon_right = rect.width() - margin - icon_size
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_right, icon_y, icon_size, icon_size, 1, 1)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            
            icon_size = dpi(5)
            margin = dpi(7)
            icon_y = rect.height() // 2 - icon_size // 2
            
            left_icon_rect = QtCore.QRect(margin, icon_y, icon_size, icon_size)
            
            icon_right = rect.width() - margin - icon_size
            right_icon_rect = QtCore.QRect(icon_right, icon_y, icon_size, icon_size)
            
            if left_icon_rect.contains(click_pos):
                self.setValue(self.minimum())
                self.sliderReleased.emit()
                return
            
            if right_icon_rect.contains(click_pos):
                self.setValue(self.maximum())
                self.sliderReleased.emit()
                return
        
        QtWidgets.QSlider.mousePressEvent(self, event)


class SimplifiedTweenUI(QtWidgets.QDialog):
    option_var_name = "SimplifiedTweenUI_lastPos"

    def __init__(self, parent=get_maya_main_window()):
            QtWidgets.QDialog.__init__(self, parent)
            
            if IS_MACOS:
                self.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint |
                    QtCore.Qt.Window |
                    QtCore.Qt.WindowStaysOnTopHint
                )
            else:
                self.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint |
                    QtCore.Qt.Window
                )


            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setFixedSize(dpi(171), dpi(188))
            self.setWindowOpacity(0.69)
            
            self.tween_mouse_pressed = False
            self.blend_mouse_pressed = False
            self.scale_mouse_pressed = False
            self.cascade_mouse_pressed = False
            
            self.shift_pressed = False
            self.ctrl_pressed = False
            
            self.maya_main_window = get_maya_main_window()
            
            self.build_ui()
            self.apply_dark_theme()

            self.old_pos = None
            
            
            
            
            
            self.last_update_time = 0
            self.update_throttle_ms = 1
            
            if IS_MACOS:
                self._background_check_timer = QtCore.QTimer()
                self._background_check_timer.timeout.connect(self._background_mouse_check)
                self._background_check_timer.start(200)





    def closeEvent(self, event):
        if hasattr(self, '_close_timer') and self._close_timer.isActive():
            self._close_timer.stop()
        if hasattr(self, '_background_check_timer') and self._background_check_timer.isActive():
            self._background_check_timer.stop()
        QtWidgets.QDialog.closeEvent(self, event)

    def check_mouse_position(self):
        return
    
    def _background_mouse_check(self):
        if (self.tween_mouse_pressed or self.blend_mouse_pressed or 
            self.scale_mouse_pressed or self.cascade_mouse_pressed):
            return
        
        cursor_pos = QtGui.QCursor.pos()
        widget_rect = self.geometry()
        
        tolerance = scale_size(50)
        expanded_rect = widget_rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)
        
        if not expanded_rect.contains(cursor_pos):
            if not hasattr(self, '_outside_count'):
                self._outside_count = 0
            self._outside_count += 1
            
            if self._outside_count >= 3:
                if hasattr(self, '_background_check_timer'):
                    self._background_check_timer.stop()
                self.close()
        else:
            self._outside_count = 0

    def force_deactivate_window(self):
        if (self.tween_mouse_pressed or self.blend_mouse_pressed or 
            self.scale_mouse_pressed or self.cascade_mouse_pressed):
            return
        
        cursor_pos = QtGui.QCursor.pos()
        widget_rect = self.geometry()
        
        tolerance = scale_size(40) if IS_MACOS else scale_size(27)
        
        expanded_rect = widget_rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)
        
        if not expanded_rect.contains(cursor_pos):
            self.close()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QtWidgets.QFrame()
        self.frame.setStyleSheet("background-color: rgba(46, 46, 46, 253); border-radius: 15px;")
        
        self.inner_layout = QtWidgets.QVBoxLayout(self.frame)
        self.inner_layout.setContentsMargins(dpi(5), dpi(5), dpi(5), dpi(5))
        self.inner_layout.setSpacing(dpi(3))

        title_label = QtWidgets.QLabel("")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 7pt; color: #E0E0E0; background-color: transparent;")
        self.inner_layout.addWidget(title_label)

        tween_layout = QtWidgets.QVBoxLayout()
        self.tween_label = QtWidgets.QLabel("Tween:")
        self.tween_label.setStyleSheet("font-size: 8pt; background-color: transparent;")
        tween_layout.addWidget(self.tween_label)
        
        self.tween_slider = CustomSlider("TW", (80, 200, 120), (80, 200, 120))
        self.tween_slider.setMinimum(-100)
        self.tween_slider.setMaximum(100)
        self.tween_slider.setValue(0)
        self.tween_slider.setFixedHeight(dpi(20))
        self.tween_slider.valueChanged.connect(self.tween_slider_changed)
        tween_layout.addWidget(self.tween_slider)
        self.inner_layout.addLayout(tween_layout)

        blend_layout = QtWidgets.QVBoxLayout()
        self.blend_label = QtWidgets.QLabel("Blend to Neighbors:")
        self.blend_label.setStyleSheet("font-size: 8pt; background-color: transparent;")
        blend_layout.addWidget(self.blend_label)
        
        self.blend_slider = CustomSlider("BN", (220, 200, 50), (220, 200, 50))
        self.blend_slider.setMinimum(-100)
        self.blend_slider.setMaximum(100)
        self.blend_slider.setValue(0)
        self.blend_slider.setFixedHeight(dpi(20))
        self.blend_slider.valueChanged.connect(self.blend_slider_changed)
        blend_layout.addWidget(self.blend_slider)
        self.inner_layout.addLayout(blend_layout)

        scale_layout = QtWidgets.QVBoxLayout()
        self.scale_label = QtWidgets.QLabel("Scale Left:")
        self.scale_label.setStyleSheet("font-size: 8pt; background-color: transparent;")
        scale_layout.addWidget(self.scale_label)
        
        self.scale_slider = CustomSlider("SL", (220, 140, 60), (220, 140, 60))
        self.scale_slider.setMinimum(-100)
        self.scale_slider.setMaximum(100)
        self.scale_slider.setValue(0)
        self.scale_slider.setFixedHeight(dpi(20))
        self.scale_slider.valueChanged.connect(self.scale_slider_changed)
        scale_layout.addWidget(self.scale_slider)
        self.inner_layout.addLayout(scale_layout)

        cascade_layout = QtWidgets.QVBoxLayout()
        self.cascade_label = QtWidgets.QLabel("Cascade:")
        self.cascade_label.setStyleSheet("font-size: 8pt; background-color: transparent;")
        cascade_layout.addWidget(self.cascade_label)
        
        self.cascade_slider = CustomSlider("CA", (200, 100, 200), (200, 100, 200))
        self.cascade_slider.setMinimum(0)
        self.cascade_slider.setMaximum(200)
        self.cascade_slider.setValue(100)
        self.cascade_slider.setFixedHeight(dpi(20))
        self.cascade_slider.valueChanged.connect(self.cascade_slider_changed)
        cascade_layout.addWidget(self.cascade_slider)
        self.inner_layout.addLayout(cascade_layout)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("font-size: 7pt; color: #BBBBBB; background-color: transparent;")
        self.inner_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.frame)
        
        self.tween_slider.installEventFilter(self)
        self.blend_slider.installEventFilter(self)
        self.scale_slider.installEventFilter(self)
        self.cascade_slider.installEventFilter(self)
        
        self.setMouseTracking(True)
        self.frame.setMouseTracking(True)
        for child in self.findChildren(QtWidgets.QWidget):
            child.setMouseTracking(True)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog { 
                background-color: transparent;
            }
        """)
        
        self.tween_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 6px;
                background: #3C3C3C;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                border: 1px solid #B8A000;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFEB3B;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #FFD700, stop: 1 #3C3C3C);
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3C3C3C, stop: 1 #FFD700);
                border-radius: 3px;
            }
        """)
        
        self.blend_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 6px;
                background: #3C3C3C;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FF7F32;
                border: 1px solid #CC6626;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFA055;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #FF7F32, stop: 1 #3C3C3C);
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3C3C3C, stop: 1 #FF7F32);
                border-radius: 3px;
            }
        """)
        
        self.scale_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 6px;
                background: #3C3C3C;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #9C27B0;
                border: 1px solid #7B1FA2;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #BA68C8;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #9C27B0, stop: 1 #3C3C3C);
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3C3C3C, stop: 1 #9C27B0);
                border-radius: 3px;
            }
        """)
        
        self.cascade_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 6px;
                background: #3C3C3C;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00BCD4;
                border: 1px solid #0097A7;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #4DD0E1;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3C3C3C, stop: 1 #00BCD4);
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00BCD4, stop: 1 #3C3C3C);
                border-radius: 3px;
            }
        """)


    def fade_to(self, target_opacity):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.anim.start()

    def enterEvent(self, event):
        QtWidgets.QDialog.enterEvent(self, event)

    def leaveEvent(self, event):
        if (self.tween_mouse_pressed or self.blend_mouse_pressed or 
            self.scale_mouse_pressed or self.cascade_mouse_pressed):
            QtWidgets.QDialog.leaveEvent(self, event)
            return
            
        if not hasattr(self, '_close_timer'):
            self._close_timer = QtCore.QTimer()
            self._close_timer.timeout.connect(self._check_and_close)
        
        check_interval = 50 if IS_MACOS else 100
        if not self._close_timer.isActive():
            self._close_timer.start(check_interval)
        
        QtWidgets.QDialog.leaveEvent(self, event)
    
    def enterEvent(self, event):
        if hasattr(self, '_close_timer') and self._close_timer.isActive():
            self._close_timer.stop()
        self._outside_count = 0
        QtWidgets.QDialog.enterEvent(self, event)
    
    def _check_and_close(self):
        if (self.tween_mouse_pressed or self.blend_mouse_pressed or 
            self.scale_mouse_pressed or self.cascade_mouse_pressed):
            return
            
        cursor_pos = QtGui.QCursor.pos()
        widget_rect = self.geometry()
        
        tolerance = scale_size(40) if IS_MACOS else scale_size(27)
        
        expanded_rect = widget_rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)
        
        if not expanded_rect.contains(cursor_pos):
            if hasattr(self, '_close_timer'):
                self._close_timer.stop()
            self.close()

    

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'globalPosition'):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            if hasattr(event, 'globalPosition'):
                self.show_context_menu(event.globalPosition().toPoint())
            else:
                self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                color: #cccccc;
                padding: 8px 25px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QMenu::item:pressed {
                background-color: #4a4a4a;
            }
        """)
        
        linear_action = menu.addAction("Fast Linear Inbetween")
        linear_action.triggered.connect(self.fast_linear_inbetween)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        if PYSIDE_VERSION >= 6:
            getattr(menu, 'exec')(pos)
        else:
            menu.exec_(pos)
    
    def fast_linear_inbetween(self):
        cmds.undoInfo(openChunk=True, chunkName="Fast Linear Inbetween")
        
        try:
            cmds.waitCursor(state=True)
            
            current_time = cmds.currentTime(query=True)
            
            selected = cmds.ls(selection=True)
            
            if not selected:
                cmds.undoInfo(closeChunk=True)
                cmds.waitCursor(state=False)
                return
            
            for obj in selected:
                attrs = cmds.listAttr(obj, keyable=True) or []
                
                for attr in attrs:
                    full_attr = "{}.{}".format(obj, attr)
                    
                    keyframes = cmds.keyframe(full_attr, query=True, timeChange=True) or []
                    
                    if keyframes:
                        key_at_current = any(abs(key - current_time) < 0.001 for key in keyframes)
                        
                        if key_at_current:
                            cmds.cutKey(full_attr, time=(current_time, current_time), clear=True)
                            keyframes = cmds.keyframe(full_attr, query=True, timeChange=True) or []
                        
                        prev_key = None
                        next_key = None
                        
                        for key in keyframes:
                            if key < current_time:
                                prev_key = key
                            elif key > current_time and next_key is None:
                                next_key = key
                                break
                        
                        if prev_key is not None:
                            cmds.keyTangent(full_attr, time=(prev_key, prev_key), inTangentType='linear', outTangentType='linear')
                        
                        if next_key is not None:
                            cmds.keyTangent(full_attr, time=(next_key, next_key), inTangentType='linear', outTangentType='linear')
                    
                    cmds.setKeyframe(full_attr, time=current_time)
                    
                    if prev_key is not None:
                        cmds.keyTangent(full_attr, time=(prev_key, prev_key), outTangentType='step')
                    
                    if next_key is not None:
                        cmds.keyTangent(full_attr, time=(next_key, next_key), outTangentType='step')
                    
                    cmds.keyTangent(full_attr, time=(current_time, current_time), outTangentType='step')
        
        finally:
            cmds.undoInfo(closeChunk=True)
            cmds.waitCursor(state=False)
        
        self.close()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, 'globalPosition'):
                current_pos = event.globalPosition().toPoint()
            else:
                current_pos = event.globalPos()
            
            delta = current_pos - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = current_pos

    def mouseReleaseEvent(self, event):
        self.old_pos = None



    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.shift_pressed = True
        elif event.key() == QtCore.Qt.Key_Control:
            self.ctrl_pressed = True
        elif event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ControlModifier:
            self.execute_copy_with_undo()
        elif event.key() == QtCore.Qt.Key_V and event.modifiers() == QtCore.Qt.ControlModifier:
            self.execute_paste_with_undo()
        QtWidgets.QDialog.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.shift_pressed = False
        elif event.key() == QtCore.Qt.Key_Control:
            self.ctrl_pressed = False
        QtWidgets.QDialog.keyReleaseEvent(self, event)



    def update_labels(self):
        if self.shift_pressed:
            self.scale_label.setText("Scale Right:")
            self.scale_slider.setLabel("SR")
        elif self.ctrl_pressed:
            self.scale_label.setText("Scale Average:")
            self.scale_slider.setLabel("SA")
        else:
            self.scale_label.setText("Scale Left:")
            self.scale_slider.setLabel("SL")

    def eventFilter(self, obj, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
        self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
        self.update_labels()

        delay = 10 if IS_MACOS else 1

        if obj == self.tween_slider:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() != QtCore.Qt.LeftButton:
                    return False
                    
                self.tween_mouse_pressed = True
                
                getCurves = get_anim_curves()
                anim_curves = getCurves[0]
                if anim_curves and len(anim_curves) > 400:
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.tween_needs_cursor_restore = True
                else:
                    self.tween_needs_cursor_restore = False
                
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                return False
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.tween_mouse_pressed = False
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                release_delay = 100 if IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self.tween_slider_released)
                return False
        elif obj == self.blend_slider:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() != QtCore.Qt.LeftButton:
                    return False
                    
                self.blend_mouse_pressed = True
                
                getCurves = get_anim_curves()
                anim_curves = getCurves[0]
                if anim_curves and len(anim_curves) > 400:
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.blend_needs_cursor_restore = True
                else:
                    self.blend_needs_cursor_restore = False
                
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                return False
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.blend_mouse_pressed = False
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                release_delay = 100 if IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self.blend_slider_released)
                return False
        elif obj == self.scale_slider:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.scale_mouse_pressed = True
                
                getCurves = get_anim_curves()
                anim_curves = getCurves[0]
                if anim_curves and len(anim_curves) > 400:
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.scale_needs_cursor_restore = True
                else:
                    self.scale_needs_cursor_restore = False
                
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                return False
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.scale_mouse_pressed = False
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                release_delay = 100 if IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self.scale_slider_released)
                return False
        elif obj == self.cascade_slider:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.cascade_mouse_pressed = True
                
                getCurves = get_anim_curves()
                anim_curves = getCurves[0]
                if anim_curves and len(anim_curves) > 400:
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.cascade_needs_cursor_restore = True
                else:
                    self.cascade_needs_cursor_restore = False
                
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                return False
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.cascade_mouse_pressed = False
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
                release_delay = 100 if IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self.cascade_slider_released)
                return False
        return False

    
    def tween_slider_changed(self, value):
        if not self.tween_mouse_pressed:
            return
        
        self.tween_slider_logic(value)

    def tween_slider_logic(self, value):
        global pushClick, openChunk, originalValues, storedAnimCurves, storedKeysSel
        self.status_label.setText("Tween: {0}".format(value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        if not self.tween_mouse_pressed:
            return
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if time_since_last < self.update_throttle_ms and pushClick:
            return
        
        self.last_update_time = current_time
        
        selected = cmds.ls(selection=True)
        
        if selected and len(selected) <= 25:
            if not pushClick:
                pushClick = True
                openChunk = True
                
                if IS_MACOS:
                    QtCore.QTimer.singleShot(20, self._initialize_tween_undo)
                else:
                    self._initialize_tween_undo()
            
            if openChunk:
                bias = (value + 100) / 200.0
                self.execute_tween_on_curves(bias)

    def _initialize_tween_undo(self):
        global originalValues, storedAnimCurves, storedKeysSel, openChunk
        
        safe_undo_chunk_open("Tween")
        originalValues = {}
        
        getCurves = get_anim_curves()
        storedAnimCurves = getCurves[0]
        getFrom = getCurves[1]
        
        if not storedAnimCurves:
            openChunk = False
            return
            
        storedKeysSel = get_keys_sel(storedAnimCurves, getFrom)
        
        hasSelectedKeys = any(keyList for keyList in storedKeysSel if keyList)
        
        
        if not hasSelectedKeys:
            current_time = cmds.currentTime(query=True)
            for curve in storedAnimCurves:
                if cmds.objExists(curve):
                    existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                    keyExists = existingKeys and current_time in existingKeys
                    
                    
                    cmds.setKeyframe(curve, time=current_time, insert=True)
                    
                    if not keyExists:
                        prev_key = cmds.findKeyframe(curve, time=(current_time,current_time), which="previous")
                        next_key = cmds.findKeyframe(curve, time=(current_time,current_time), which="next")
                        
                        
                        in_tangent_type = "auto"
                        out_tangent_type = "auto"
                        
                        step_detected = False
                        
                        if prev_key is not None:
                            try:
                                prev_out_tangent = cmds.keyTangent(curve, time=(prev_key,prev_key), 
                                                                 query=True, outTangentType=True)[0]
                                if prev_out_tangent == "step":
                                    step_detected = True
                                    in_tangent_type = "auto"
                                    out_tangent_type = "step"
                            except:
                                pass
                        
                        if not step_detected and next_key is not None:
                            try:
                                next_out_tangent = cmds.keyTangent(curve, time=(next_key,next_key), 
                                                                 query=True, outTangentType=True)[0]
                                if next_out_tangent == "step":
                                    step_detected = True
                                    in_tangent_type = "auto"
                                    out_tangent_type = "step"
                            except:
                                pass
                        
                        cmds.keyTangent(curve, time=(current_time, current_time),
                                      inTangentType=in_tangent_type, outTangentType=out_tangent_type)
            
            storedKeysSel = []
            for curve in storedAnimCurves:
                if cmds.objExists(curve):
                    storedKeysSel.append([current_time])
                else:
                    storedKeysSel.append([])
        
        for n, curve in enumerate(storedAnimCurves):
            if not cmds.objExists(curve) or not storedKeysSel[n]:
                continue
                
            originalValues[curve] = {}
            for key_time in storedKeysSel[n]:
                try:
                    original_val = cmds.keyframe(curve, query=True, time=(key_time, key_time), 
                                               valueChange=True)[0]
                    originalValues[curve][key_time] = original_val
                except:
                    continue

    def blend_slider_changed(self, value):
        if not self.blend_mouse_pressed:
            return
            
        self.blend_slider_logic(value)

    def blend_slider_logic(self, value):
        global blendPushClick, blendOpenChunk, blendStoredAnimCurves, blendStoredKeysSel
        self.status_label.setText("Blend: {0}".format(value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        if not self.blend_mouse_pressed:
            return
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if time_since_last < self.update_throttle_ms and blendPushClick:
            return
        
        self.last_update_time = current_time
            
        selected = cmds.ls(selection=True)
        
        if selected and len(selected) <= 65:
            if not blendPushClick:
                blendPushClick = True
                blendOpenChunk = True
                cmds.undoInfo(openChunk=True)
                
                getCurves = get_anim_curves()
                blendStoredAnimCurves = getCurves[0]
                getFrom = getCurves[1]
                
                if not blendStoredAnimCurves:
                    return
                    
                blendStoredKeysSel = get_keys_sel(blendStoredAnimCurves, getFrom)
                
                hasSelectedKeys = any(keyList for keyList in blendStoredKeysSel if keyList)
                
                if not hasSelectedKeys:
                    currentTime = cmds.currentTime(query=True)
                    for curve in blendStoredAnimCurves:
                        if cmds.objExists(curve):
                            existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                            keyExists = existingKeys and currentTime in existingKeys
                            
                            cmds.setKeyframe(curve, time=currentTime, insert=True)
                            
                            if not keyExists:
                                prev_key = cmds.findKeyframe(curve, time=(currentTime,currentTime), which="previous")
                                next_key = cmds.findKeyframe(curve, time=(currentTime,currentTime), which="next")
                                
                                in_tangent_type = "auto"
                                out_tangent_type = "auto"
                                
                                step_detected = False
                                
                                if prev_key is not None:
                                    try:
                                        prev_out_tangent = cmds.keyTangent(curve, time=(prev_key,prev_key), 
                                                                         query=True, outTangentType=True)[0]
                                        if prev_out_tangent == "step":
                                            step_detected = True
                                            in_tangent_type = "auto"
                                            out_tangent_type = "step"
                                    except:
                                        pass
                                
                                if not step_detected and next_key is not None:
                                    try:
                                        next_out_tangent = cmds.keyTangent(curve, time=(next_key,next_key), 
                                                                         query=True, outTangentType=True)[0]
                                        if next_out_tangent == "step":
                                            step_detected = True
                                            in_tangent_type = "auto"
                                            out_tangent_type = "step"
                                    except:
                                        pass
                                
                                cmds.keyTangent(curve, time=(currentTime, currentTime),
                                              inTangentType=in_tangent_type, outTangentType=out_tangent_type)
                    
                    blendStoredKeysSel = []
                    for curve in blendStoredAnimCurves:
                        if cmds.objExists(curve):
                            blendStoredKeysSel.append([currentTime])
                        else:
                            blendStoredKeysSel.append([])
                
                setup_blend_key_transform_data()
            
            execute_blend_key_transform(value)
        else:
            pass


    def _initialize_blend_undo(self):
        global blendStoredAnimCurves, blendStoredKeysSel, blendOpenChunk
        
        safe_undo_chunk_open("Blend to Neighbors")
        
        getCurves = get_anim_curves()
        blendStoredAnimCurves = getCurves[0]
        getFrom = getCurves[1]
        
        if not blendStoredAnimCurves:
            blendOpenChunk = False
            return
            
        blendStoredKeysSel = get_keys_sel(blendStoredAnimCurves, getFrom)
        
        hasSelectedKeys = any(keyList for keyList in blendStoredKeysSel if keyList)
        
        if not hasSelectedKeys:
            currentTime = cmds.currentTime(query=True)
            curves_with_new_keys = {}
            for curve in blendStoredAnimCurves:
                if cmds.objExists(curve):
                    existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                    keyExists = existingKeys and currentTime in existingKeys
                    
                    cmds.setKeyframe(curve, time=currentTime, insert=True)
                    
                    if not keyExists:
                        curves_with_new_keys[curve] = [currentTime]
            
            if curves_with_new_keys:
                set_key_tangents_smart(curves_with_new_keys)
            
            blendStoredKeysSel = []
            for curve in blendStoredAnimCurves:
                if cmds.objExists(curve):
                    blendStoredKeysSel.append([currentTime])
                else:
                    blendStoredKeysSel.append([])
        
        setup_blend_key_transform_data()

    def blend_slider_released(self):
        if not self.blend_mouse_pressed:
            final_value = self.blend_slider.value()
            
            selected = cmds.ls(selection=True)
            
            if final_value != 0:
                if selected and len(selected) > 65:
                    self.apply_blend_to_all_objects(final_value)
                
            self.reset_blend_slider()
            if hasattr(self, 'blend_needs_cursor_restore') and self.blend_needs_cursor_restore:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.blend_needs_cursor_restore = False
            delay = 10 if IS_MACOS else 1
            QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def reset_blend_slider(self):
        global blendPushClick, blendOpenChunk, blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
        global blendStoredAnimCurves, blendStoredKeysSel, blendLastValue, blendScaleValue
        
        self.blend_slider.blockSignals(True)
        self.blend_slider.setValue(0)
        self.blend_slider.blockSignals(False)
        
        if blendPushClick and blendOpenChunk:
            try:
                safe_undo_chunk_close()
            except:
                pass
            blendOpenChunk = False
        blendPushClick = False
        blendStoredKeyValues = {}
        blendStoredKeyTimes = {}
        blendStoredIndexes = {}
        blendStoredAnimCurves = []
        blendStoredKeysSel = []
        blendLastValue = 0
        blendScaleValue = 1
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def apply_blend_to_all_objects(self, value):
        global blendPushClick, blendOpenChunk, blendStoredAnimCurves, blendStoredKeysSel
        
        if not blendPushClick:
            blendPushClick = True
            blendOpenChunk = True
            safe_undo_chunk_open("Blend to Neighbors")
            
            getCurves = get_anim_curves()
            blendStoredAnimCurves = getCurves[0]
            getFrom = getCurves[1]
            
            if not blendStoredAnimCurves:
                return
                
            blendStoredKeysSel = get_keys_sel(blendStoredAnimCurves, getFrom)
            
            hasSelectedKeys = any(keyList for keyList in blendStoredKeysSel if keyList)
            
            if not hasSelectedKeys:
                currentTime = cmds.currentTime(query=True)
                curves_with_new_keys = {}
                for curve in blendStoredAnimCurves:
                    if cmds.objExists(curve):
                        existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                        keyExists = existingKeys and currentTime in existingKeys
                        
                        cmds.setKeyframe(curve, time=currentTime, insert=True)
                        
                        if not keyExists:
                            curves_with_new_keys[curve] = [currentTime]
                
                if curves_with_new_keys:
                    for curve, times in curves_with_new_keys.items():
                        for key_time in times:
                            prev_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="previous")
                            next_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="next")
                            
                            in_tangent_type = "auto"
                            out_tangent_type = "auto"
                            step_detected = False
                            
                            if prev_key is not None:
                                try:
                                    prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key),
                                                                       query=True, outTangentType=True)[0]
                                    if prev_out_tangent == "step":
                                        step_detected = True
                                        in_tangent_type = "auto"
                                        out_tangent_type = "step"
                                except:
                                    pass
                            
                            if not step_detected and next_key is not None:
                                try:
                                    next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key),
                                                                       query=True, outTangentType=True)[0]
                                    if next_out_tangent == "step":
                                        step_detected = True
                                        in_tangent_type = "auto"
                                        out_tangent_type = "step"
                                except:
                                    pass
                            
                            cmds.keyTangent(curve, time=(key_time, key_time),
                                           inTangentType=in_tangent_type, outTangentType=out_tangent_type)
                
                blendStoredKeysSel = []
                for curve in blendStoredAnimCurves:
                    if cmds.objExists(curve):
                        blendStoredKeysSel.append([currentTime])
                    else:
                        blendStoredKeysSel.append([])
            
            setup_blend_key_transform_data()
        
        cmds.waitCursor(state=True)
        
        try:
            execute_blend_key_transform(value)
        finally:
            cmds.waitCursor(state=False)

    def tween_slider_released(self):
        if not self.tween_mouse_pressed:
            final_value = self.tween_slider.value()
            
            selected = cmds.ls(selection=True)
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
            
            if final_value != 0:
                if shift_pressed:
                    if selected and len(selected) > 65:
                        self.apply_blend_to_all_objects(final_value)
                else:
                    if selected and len(selected) > 25:
                        self.apply_tween_to_all_objects(final_value)
                
            self.reset_tween_slider()
            if hasattr(self, 'tween_needs_cursor_restore') and self.tween_needs_cursor_restore:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.tween_needs_cursor_restore = False
            delay = 10 if IS_MACOS else 1
            QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def reset_tween_slider(self):
        global pushClick, openChunk, originalValues, storedSelection, storedAnimCurves, storedKeysSel
        global blendPushClick, blendOpenChunk, blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
        global blendStoredAnimCurves, blendStoredKeysSel, blendLastValue, blendScaleValue
        
        final_value = self.tween_slider.value()
        if final_value != 0 and pushClick and openChunk:
            selected = cmds.ls(selection=True)
            if selected and len(selected) <= 25:
                bias = (final_value + 100) / 200.0
                self.execute_tween_on_curves(bias)
        
        self.tween_slider.blockSignals(True)
        self.tween_slider.setValue(0)
        self.tween_slider.blockSignals(False)
        
        if pushClick and openChunk:
            try:
                safe_undo_chunk_close()
            except:
                pass
            openChunk = False
        pushClick = False
        originalValues = {}
        storedSelection = []
        storedAnimCurves = []
        storedKeysSel = []
        
        if blendPushClick and blendOpenChunk and self.shift_pressed:
            try:
                safe_undo_chunk_close()
            except:
                pass
            blendOpenChunk = False
            blendPushClick = False
            blendStoredKeyValues = {}
            blendStoredKeyTimes = {}
            blendStoredIndexes = {}
            blendStoredAnimCurves = []
            blendStoredKeysSel = []
            blendLastValue = 0
            blendScaleValue = 1
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def apply_tween_to_all_objects(self, value):
        global pushClick, openChunk, originalValues, storedAnimCurves, storedKeysSel
        
        if not pushClick:
            pushClick = True
            openChunk = True
            safe_undo_chunk_open("Tween")
            originalValues = {}
            
            getCurves = get_anim_curves()
            storedAnimCurves = getCurves[0]
            getFrom = getCurves[1]
            
            if not storedAnimCurves:
                return
                
            storedKeysSel = get_keys_sel(storedAnimCurves, getFrom)
            
            hasSelectedKeys = any(keyList for keyList in storedKeysSel if keyList)
            
            if not hasSelectedKeys:
                current_time = cmds.currentTime(query=True)
                curves_with_new_keys = {}
                for curve in storedAnimCurves:
                    if cmds.objExists(curve):
                        existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                        keyExists = existingKeys and current_time in existingKeys
                        
                        cmds.setKeyframe(curve, time=current_time, insert=True)
                        
                        if not keyExists:
                            curves_with_new_keys[curve] = [current_time]
                
                if curves_with_new_keys:
                    for curve, times in curves_with_new_keys.items():
                        for key_time in times:
                            prev_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="previous")
                            next_key = cmds.findKeyframe(curve, time=(key_time, key_time), which="next")
                            
                            in_tangent_type = "auto"
                            out_tangent_type = "auto"
                            step_detected = False
                            
                            if prev_key is not None:
                                try:
                                    prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key),
                                                                       query=True, outTangentType=True)[0]
                                    if prev_out_tangent == "step":
                                        step_detected = True
                                        in_tangent_type = "auto"
                                        out_tangent_type = "step"
                                except:
                                    pass
                            
                            if not step_detected and next_key is not None:
                                try:
                                    next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key),
                                                                       query=True, outTangentType=True)[0]
                                    if next_out_tangent == "step":
                                        step_detected = True
                                        in_tangent_type = "auto"
                                        out_tangent_type = "step"
                                except:
                                    pass
                            
                            cmds.keyTangent(curve, time=(key_time, key_time),
                                           inTangentType=in_tangent_type, outTangentType=out_tangent_type)
                
                storedKeysSel = []
                for curve in storedAnimCurves:
                    if cmds.objExists(curve):
                        storedKeysSel.append([current_time])
                    else:
                        storedKeysSel.append([])
            
            for n, curve in enumerate(storedAnimCurves):
                if not cmds.objExists(curve) or not storedKeysSel[n]:
                    continue
                    
                originalValues[curve] = {}
                for key_time in storedKeysSel[n]:
                    try:
                        original_val = cmds.keyframe(curve, query=True, time=(key_time, key_time), 
                                                   valueChange=True)[0]
                        originalValues[curve][key_time] = original_val
                    except:
                        continue
        
        cmds.waitCursor(state=True)
        
        try:
            bias = (value + 100) / 200.0
            self.execute_tween_on_curves(bias)
        finally:
            cmds.waitCursor(state=False)

    def execute_tween_on_curves(self, bias):
        global originalValues, storedAnimCurves, storedKeysSel
        
        if not storedAnimCurves:
            return
        
        for n, curve in enumerate(storedAnimCurves):
            if not cmds.objExists(curve) or not storedKeysSel[n]:
                continue
            
            for key_time in storedKeysSel[n]:
                if curve not in originalValues or key_time not in originalValues[curve]:
                    continue
                    
                original_val = originalValues[curve][key_time]
                
                all_keys = cmds.keyframe(curve, query=True, timeChange=True)
                if not all_keys:
                    continue
                
                all_keys = sorted(all_keys)
                
                prev_time = None
                next_time = None
                
                for k in all_keys:
                    if k < key_time:
                        prev_time = k
                    elif k > key_time:
                        next_time = k
                        break
                
                prev_value = None
                next_value = None
                
                if prev_time is not None:
                    try:
                        prev_value = cmds.keyframe(curve, query=True, time=(prev_time,), valueChange=True)[0]
                    except:
                        prev_value = None
                
                if next_time is not None:
                    try:
                        next_value = cmds.keyframe(curve, query=True, time=(next_time,), valueChange=True)[0]
                    except:
                        next_value = None
                
                tweened_value = original_val
                
                if prev_value is not None and next_value is not None:
                    tweened_value = prev_value + (next_value - prev_value) * bias
                    
                elif prev_value is not None:
                    if bias < 0.5:
                        blend_factor = (0.5 - bias) * 2
                        tweened_value = original_val + (prev_value - original_val) * blend_factor
                        
                elif next_value is not None:
                    if bias > 0.5:
                        blend_factor = (bias - 0.5) * 2
                        tweened_value = original_val + (next_value - original_val) * blend_factor
                
                
                try:
                    cmds.keyframe(curve, edit=True, time=(key_time, key_time), valueChange=tweened_value)
                except:
                    continue

    
    def scale_slider_changed(self, value):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
        ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
        
        if not self.scale_mouse_pressed:
            return
        
        if ctrl_pressed:
            self.scale_avg_logic(value)
        elif shift_pressed:
            self.scale_right_logic(value)
        else:
            self.scale_left_logic(value)

    def scale_left_logic(self, value):
        global _left_dragging
        slider_val = value / 100.0
        self.status_label.setText("Scale Left: {0}".format(value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if not _left_dragging:
            _left_dragging = True
            self.last_update_time = current_time
            safe_undo_chunk_open("Scale Left")
            if IS_MACOS:
                QtCore.QTimer.singleShot(20, lambda: cache_left_original_values())
                QtCore.QTimer.singleShot(40, lambda: scale_left_keys(slider_val))
            else:
                cache_left_original_values()
                scale_left_keys(slider_val)
        else:
            if time_since_last >= self.update_throttle_ms:
                self.last_update_time = current_time
                scale_left_keys(slider_val)

    def scale_right_logic(self, value):
        global _right_dragging
        slider_val = value / 100.0
        self.status_label.setText("Scale Right: {0}".format(value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if not _right_dragging:
            _right_dragging = True
            self.last_update_time = current_time
            safe_undo_chunk_open("Scale Right")
            if IS_MACOS:
                QtCore.QTimer.singleShot(20, lambda: cache_right_original_values())
                QtCore.QTimer.singleShot(40, lambda: scale_right_keys(slider_val))
            else:
                cache_right_original_values()
                scale_right_keys(slider_val)
        else:
            if time_since_last >= self.update_throttle_ms:
                self.last_update_time = current_time
                scale_right_keys(slider_val)

    def scale_avg_logic(self, value):
        global _avg_dragging
        slider_val = value / 100.0
        self.status_label.setText("Scale Average: {0}".format(value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if not _avg_dragging:
            _avg_dragging = True
            self.last_update_time = current_time
            safe_undo_chunk_open("Scale Average")
            if IS_MACOS:
                QtCore.QTimer.singleShot(20, lambda: cache_avg_original_values())
                QtCore.QTimer.singleShot(40, lambda: scale_avg_keys(slider_val))
            else:
                cache_avg_original_values()
                scale_avg_keys(slider_val)
        else:
            if time_since_last >= self.update_throttle_ms:
                self.last_update_time = current_time
                scale_avg_keys(slider_val)

    def scale_slider_released(self):
        if not self.scale_mouse_pressed:
            self.reset_scale_slider()
            if hasattr(self, 'scale_needs_cursor_restore') and self.scale_needs_cursor_restore:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.scale_needs_cursor_restore = False
            
            if IS_MACOS:
                QtCore.QTimer.singleShot(50, self.close)
            else:
                delay = 10
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def reset_scale_slider(self):
        global _left_dragging, _left_original_values, _left_pivot_values, _left_stored_keys_sel, _left_stored_anim_curves
        global _right_dragging, _right_original_values, _right_pivot_values, _right_stored_keys_sel, _right_stored_anim_curves
        global _right_stored_key_indexes, _right_last_scale_value, _right_keys_created_at_current_time
        global _avg_dragging, _avg_original_values, _avg_stored_keys_sel, _avg_stored_anim_curves, _avg_stored_key_indexes, _avg_last_scale_value
        
        self.scale_slider.blockSignals(True)
        self.scale_slider.setValue(0)
        self.scale_slider.blockSignals(False)
        
        if _left_dragging:
            try:
                safe_undo_chunk_close()
            except:
                pass
            _left_dragging = False
        _left_original_values = {}
        _left_pivot_values = {}
        _left_stored_keys_sel = []
        _left_stored_anim_curves = []
        
        if _right_dragging:
            set_step_tangents_if_needed_right()
            try:
                safe_undo_chunk_close()
            except:
                pass
            _right_dragging = False
        _right_original_values = {}
        _right_pivot_values = {}
        _right_stored_keys_sel = []
        _right_stored_anim_curves = []
        _right_stored_key_indexes = {}
        _right_last_scale_value = 1.0
        _right_keys_created_at_current_time = {}
        
        if _avg_dragging:
            try:
                safe_undo_chunk_close()
            except:
                pass
            _avg_dragging = False
        _avg_original_values = {}
        _avg_stored_keys_sel = []
        _avg_stored_anim_curves = []
        _avg_stored_key_indexes = {}
        _avg_last_scale_value = 1.0
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def cascade_slider_changed(self, value):
        if not self.cascade_mouse_pressed:
            return
        self.cascade_slider_logic(value)

    def cascade_slider_logic(self, value):
        global cascadePushClick, cascadeOpenChunk, cascadeStoredAnimCurves, cascadeStoredKeysSel, cascadeStoredKeyValues
        
        t_value = value / 100.0
        show_value = abs(round((t_value - 1.0) * 100.0, 2))
        if show_value >= 1 or show_value == 0:
            show_value = int(round(show_value))
        self.status_label.setText("Cascade: {0}%".format(show_value))
        
        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        
        if not self.cascade_mouse_pressed:
            return
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if time_since_last < self.update_throttle_ms and cascadePushClick:
            return
        
        self.last_update_time = current_time
        
        if not cascadePushClick:
            cascadePushClick = True
            if cascadeOpenChunk:
                safe_undo_chunk_open("Cascade Keys")
                cascadeOpenChunk = False
            
            getCurves = get_anim_curves()
            cascadeStoredAnimCurves = getCurves[0]
            getFrom = getCurves[1]
            
            if not cascadeStoredAnimCurves:
                return
            
            cascadeStoredKeysSel = get_keys_sel(cascadeStoredAnimCurves, getFrom)
            
            cascadeStoredKeyValues = {}
            
            for n, curve in enumerate(cascadeStoredAnimCurves):
                if not cmds.objExists(curve) or not cascadeStoredKeysSel[n]:
                    continue
                
                all_key_values = cmds.keyframe(curve, query=True, valueChange=True)
                
                if all_key_values:
                    cascadeStoredKeyValues[curve] = list(all_key_values)
        
        apply_cascade_keys(t_value)

    def cascade_slider_released(self):
        if not self.cascade_mouse_pressed:
            self.reset_cascade_slider()
            if hasattr(self, 'cascade_needs_cursor_restore') and self.cascade_needs_cursor_restore:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.cascade_needs_cursor_restore = False
            
            if IS_MACOS:
                QtCore.QTimer.singleShot(50, self.close)
            else:
                delay = 10
                QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

    def reset_cascade_slider(self):
        global cascadePushClick, cascadeOpenChunk, cascadeStoredKeyValues, cascadeStoredAnimCurves, cascadeStoredKeysSel
        
        final_value = self.cascade_slider.value()
        if final_value != 100 and cascadePushClick:
            t_value = final_value / 100.0
            apply_cascade_keys(t_value)
        
        self.cascade_slider.blockSignals(True)
        self.cascade_slider.setValue(100)
        self.cascade_slider.blockSignals(False)
        
        if cascadePushClick:
            cascadePushClick = False
            if not cascadeOpenChunk:
                safe_undo_chunk_close()
                cascadeOpenChunk = True
            cascadeStoredKeyValues = {}
            cascadeStoredAnimCurves = []
            cascadeStoredKeysSel = []
        
        if IS_MACOS:
            QtCore.QTimer.singleShot(50, self.close)
        else:
            delay = 10
            QtCore.QTimer.singleShot(delay, self.force_deactivate_window)

def apply_cascade_keys(t_value):
    global cascadeStoredAnimCurves, cascadeStoredKeysSel, cascadeStoredKeyValues
    
    if not cascadeStoredAnimCurves:
        return
    
    for n, curve in enumerate(cascadeStoredAnimCurves):
        if not cmds.objExists(curve) or not cascadeStoredKeysSel[n]:
            continue
        
        all_key_values = cmds.keyframe(curve, query=True, valueChange=True)
        all_key_times = cmds.keyframe(curve, query=True, timeChange=True)
        
        if not all_key_values or not all_key_times:
            continue
        
        original_values = cascadeStoredKeyValues.get(curve, [])
        if not original_values:
            continue
        
        for selected_time in cascadeStoredKeysSel[n]:
            selected_idx = None
            for i, key_time in enumerate(all_key_times):
                if abs(key_time - selected_time) < 0.001:
                    selected_idx = i
                    break
            
            if selected_idx is None or selected_idx >= len(original_values):
                continue
            
            selected_original_value = original_values[selected_idx]
            
            left_neighbor_value = None
            right_neighbor_value = None
            
            if selected_idx > 0:
                left_neighbor_value = original_values[selected_idx - 1]
            
            if selected_idx < len(original_values) - 1:
                right_neighbor_value = original_values[selected_idx + 1]
            
            if left_neighbor_value is None and right_neighbor_value is None:
                continue
            
            if left_neighbor_value is None:
                left_neighbor_value = selected_original_value
            if right_neighbor_value is None:
                right_neighbor_value = selected_original_value
            
            keys_to_move = []
            target_value = selected_original_value
            
            if t_value < 1.0:
                blend_factor = 1.0 - t_value
                target_value = selected_original_value + (left_neighbor_value - selected_original_value) * blend_factor
                keys_to_move = list(range(selected_idx, len(original_values)))
            else:
                blend_factor = t_value - 1.0
                target_value = selected_original_value + (right_neighbor_value - selected_original_value) * blend_factor
                keys_to_move = list(range(0, selected_idx + 1))
            
            movement_offset = target_value - selected_original_value
            
            for key_idx in keys_to_move:
                if key_idx >= len(original_values):
                    continue
                
                new_value = original_values[key_idx] + movement_offset
                
                try:
                    cmds.keyframe(curve, edit=True, index=(key_idx, key_idx), 
                                valueChange=new_value)
                except:
                    continue

def toggle_simplified_tween_ui():
    global simplified_tween_ui
    
    try:
        if simplified_tween_ui.isVisible():
            return
    except:
        pass
    
    try:
        simplified_tween_ui.close()
        simplified_tween_ui.deleteLater()
    except:
        pass
    
    reset_scale_factor()
    
    cursor_pos = QtGui.QCursor.pos()
    
    simplified_tween_ui = SimplifiedTweenUI()
    
    ui_x = cursor_pos.x() - scale_size(85)
    ui_y = cursor_pos.y() - scale_size(85)
    
    simplified_tween_ui.move(ui_x, ui_y)
    
    simplified_tween_ui.show()

toggle_simplified_tween_ui()