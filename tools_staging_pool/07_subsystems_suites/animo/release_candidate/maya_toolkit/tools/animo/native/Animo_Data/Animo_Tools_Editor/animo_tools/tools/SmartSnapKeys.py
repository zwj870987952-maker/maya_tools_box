from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

max = builtins.max 
min = builtins.min 


def snap_keys_to_frames():
    cmds.waitCursor(state=True)
    
    try:
        curves_to_process, time_constraint = determine_processing_scope()
        
        if not curves_to_process:
            return 0
        
        unsnapped_keys = get_all_unsnapped_keys(curves_to_process, time_constraint)
        
        if not unsnapped_keys:
            return 0
        
        snapped_count = process_unsnapped_keys_batch(unsnapped_keys, time_constraint)
        
        if snapped_count > 0:
            select_and_cut_unsnapped_keys(curves_to_process, time_constraint)
        
        return snapped_count
    
    finally:
        cmds.waitCursor(state=False)

def determine_processing_scope():
    selected_keys_exist = False
    selected_curves = None
    
    try:
        visible_panels = cmds.getPanel(visiblePanels=True)
        graph_editor_visible = "graphEditor1" in visible_panels
        
        test_selection = cmds.keyframe(query=True, selected=True)
        if test_selection is not None and len(test_selection) > 0 and graph_editor_visible:
            selected_curves = cmds.keyframe(query=True, selected=True, name=True)
            if selected_curves:
                has_unsnapped = False
                for curve in selected_curves:
                    selected_times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
                    if selected_times:
                        for time in selected_times:
                            if time != int(time):
                                has_unsnapped = True
                                break
                    if has_unsnapped:
                        break
                selected_keys_exist = has_unsnapped
    except:
        pass
    
    time_range = get_time_range_selection()
    
    if selected_keys_exist and selected_curves:
        return selected_curves, 'selected_keys'
    elif selected_curves:
        return selected_curves, 'all_keys'
    elif time_range:
        all_curves = cmds.ls(type='animCurve')
        return all_curves, time_range
    else:
        cmds.inViewMessage(amg='Select keys in Timeline or Graph Editor', pos='midCenter', fade=True)
        return None, None

def get_time_range_selection():
    try:
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        range_visible = cmds.timeControl(playBackSlider, query=True, rangeVisible=True)
        
        if range_visible:
            timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
            if timeRange and len(timeRange) >= 2:
                StartRange = int(timeRange[0])
                EndRange = int(timeRange[1] - 1)
                return (StartRange, EndRange)
        return None
    except:
        return None

def get_all_unsnapped_keys(curves, time_constraint):
    unsnapped_keys = []
    batch_size = 100
    
    for i in range(0, len(curves), batch_size):
        batch_curves = curves[i:i+batch_size]
        
        for curve in batch_curves:
            try:
                if time_constraint == 'selected_keys':
                    key_times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
                elif isinstance(time_constraint, tuple):
                    start_time, end_time = time_constraint
                    key_times = cmds.keyframe(curve, time=(start_time, end_time), 
                                            query=True, timeChange=True)
                else:
                    key_times = cmds.keyframe(curve, query=True, timeChange=True)
                
                if not key_times:
                    continue
                
                for key_time in key_times:
                    if key_time != int(key_time):
                        nearest_frame = round(key_time)
                        
                        if isinstance(time_constraint, tuple):
                            start_time, end_time = time_constraint
                            if nearest_frame < start_time or nearest_frame > end_time:
                                continue
                        
                        unsnapped_keys.append((curve, key_time, nearest_frame))
                        
            except:
                continue
    
    return unsnapped_keys

def process_unsnapped_keys_batch(unsnapped_keys, time_constraint):
    total_snapped = 0
    keys_by_curve = {}
    
    for curve, key_time, nearest_frame in unsnapped_keys:
        if curve not in keys_by_curve:
            keys_by_curve[curve] = []
        keys_by_curve[curve].append((key_time, nearest_frame))
    
    for curve, key_data in keys_by_curve.items():
        try:
            curve_snapped = 0
            target_values = {}
            
            for key_time, nearest_frame in key_data:
                if nearest_frame not in target_values:
                    existing_keys = cmds.keyframe(curve, time=(nearest_frame, nearest_frame),
                                                query=True, timeChange=True)
                    if existing_keys:
                        target_values[nearest_frame] = cmds.keyframe(curve, 
                                                                   time=(nearest_frame, nearest_frame),
                                                                   query=True, valueChange=True)[0]
                    else:
                        target_values[nearest_frame] = cmds.keyframe(curve, 
                                                                   time=(nearest_frame, nearest_frame),
                                                                   query=True, eval=True)[0]
            
            for key_time, nearest_frame in key_data:
                try:
                    cmds.keyframe(curve, time=(key_time, key_time), 
                                timeChange=nearest_frame, relative=False)
                    cmds.keyframe(curve, time=(nearest_frame, nearest_frame), 
                                valueChange=target_values[nearest_frame])
                    curve_snapped += 1
                    total_snapped += 1
                except:
                    continue
                    
        except:
            continue
    
    return total_snapped

def select_and_cut_unsnapped_keys(curves, time_constraint):
    try:
        if isinstance(time_constraint, tuple):
            start_time, end_time = time_constraint
            cmds.selectKey(clear=True)
            cmds.selectKey(unsnappedKeys=True, t=(start_time, end_time))
            cmds.cutKey()
            
        elif time_constraint == 'selected_keys':
            all_selected_times = []
            
            for curve in curves:
                try:
                    selected_times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
                    if selected_times:
                        for time in selected_times:
                            if time != int(time):
                                all_selected_times.append(time)
                except:
                    continue
            
            if all_selected_times:
                start_time = min(all_selected_times)
                end_time = max(all_selected_times)
                
                cmds.selectKey(clear=True)
                cmds.selectKey(unsnappedKeys=True, t=(start_time, end_time))
                cmds.cutKey()
            
        elif time_constraint == 'all_keys':
            cmds.selectKey(clear=True)
            for curve in curves:
                cmds.selectKey(curve, unsnappedKeys=True, add=True)
            cmds.cutKey()
        
    except Exception as e:
        pass

def snap_keys_fast():
    return snap_keys_to_frames()

snapped_count = snap_keys_to_frames()
    