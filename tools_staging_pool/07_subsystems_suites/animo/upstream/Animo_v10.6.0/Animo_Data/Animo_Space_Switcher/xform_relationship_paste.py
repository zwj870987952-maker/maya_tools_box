from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import json
import os
import sys

SPATIAL_LINK_DATA_FILE = "animo_xform_relationship"
MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40
BAKE_KEYS_OPTION_VAR = "XformAlignUI_bakeKeys"


def get_data_file_path():
    user_app_dir = cmds.internalVar(userAppDir=True)
    return os.path.join(user_app_dir, "scripts", "Animo_Data", "Animo_Prefs", SPATIAL_LINK_DATA_FILE)


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


def load_spatial_data():
    file_path = get_data_file_path()
    if not os.path.isfile(file_path):
        return None
    with open(file_path) as f:
        return json.load(f)


def find_node(long_name):
    if cmds.objExists(long_name):
        return long_name
    short_name = long_name.split('|')[-1]
    matches = cmds.ls(short_name, long=True) or cmds.ls("*:" + short_name, long=True)
    return matches[0] if matches else None


def get_timeline_range():
    playback_slider = mel.eval('$tmp = $gPlayBackSlider')
    range_array = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(range_array[0])
    end = int(range_array[1]) - 1
    if end > start:
        return start, end
    return None


def is_bake_keys_enabled():
    if cmds.optionVar(exists=BAKE_KEYS_OPTION_VAR):
        return cmds.optionVar(q=BAKE_KEYS_OPTION_VAR) == 1
    return True


def get_object_keyframes(objects, start_frame, end_frame):
    keyframes = set()
    for obj in objects:
        keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
        if keys:
            keyframes.update([int(k) for k in keys])
    return sorted(keyframes)


def apply_spatial_link_current_frame():
    spatial_data = load_spatial_data()
    if not spatial_data:
        cmds.inViewMessage(
            amg='<span style="color:#f58b3a;">No data found. Copy first.</span>',
            pos='botCenter',
            fade=True
        )
        return
    
    xform_list = spatial_data.get("xformNodesListInfo", [])
    if not xform_list:
        return
    
    bake_keys_mode = is_bake_keys_enabled()
    timeline_range = get_timeline_range()
    
    if timeline_range:
        if bake_keys_mode:
            apply_at_keyframes(xform_list, timeline_range[0], timeline_range[1])
        else:
            apply_to_range(xform_list, timeline_range[0], timeline_range[1])
    else:
        apply_single_frame(xform_list)


def apply_single_frame(xform_list):
    marker = load_mark_frame()
    if marker:
        marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    nodes_to_key = []
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Relationship")
    
    try:
        if len(xform_list) == 1:
            node = find_node(xform_list[0]["nodeName"])
            if node:
                cmds.xform(node, matrix=xform_list[0]["matrix"], worldSpace=True)
                nodes_to_key.append(node)
        else:
            driver_info = xform_list[-1]
            driver_node = find_node(driver_info["nodeName"])
            
            if not driver_node:
                cmds.warning("Driver node not found")
                return
            
            stored_driver_matrix = om.MMatrix(driver_info["matrix"])
            current_driver_matrix = om.MMatrix(cmds.xform(driver_node, query=True, matrix=True, worldSpace=True))
            stored_driver_inverse = stored_driver_matrix.inverse()
            
            for node_info in xform_list[:-1]:
                driven_node = find_node(node_info["nodeName"])
                if not driven_node:
                    continue
                
                stored_driven_matrix = om.MMatrix(node_info["matrix"])
                target_matrix = stored_driven_matrix * stored_driver_inverse * current_driver_matrix
                
                cmds.xform(driven_node, matrix=list(target_matrix), worldSpace=True)
                nodes_to_key.append(driven_node)
        
        if nodes_to_key:
            cmds.setKeyframe(nodes_to_key, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
    
    finally:
        cmds.undoInfo(closeChunk=True)


def apply_to_range(xform_list, start_frame, end_frame):
    if len(xform_list) < 2:
        cmds.warning("Need at least 2 objects for range paste")
        return
    
    driver_info = xform_list[-1]
    driver_node = find_node(driver_info["nodeName"])
    
    if not driver_node:
        cmds.warning("Driver node not found")
        return
    
    driven_nodes = []
    stored_matrices = []
    
    for node_info in xform_list[:-1]:
        node = find_node(node_info["nodeName"])
        if node:
            driven_nodes.append(node)
            stored_matrices.append(om.MMatrix(node_info["matrix"]))
    
    if not driven_nodes:
        cmds.warning("No driven nodes found")
        return
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    stored_driver_matrix = om.MMatrix(driver_info["matrix"])
    stored_driver_inverse = stored_driver_matrix.inverse()
    current_frame = cmds.currentTime(query=True)
    
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Relationship Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame, edit=True)
            
            current_driver_matrix = om.MMatrix(cmds.xform(driver_node, query=True, matrix=True, worldSpace=True))
            
            for i, driven_node in enumerate(driven_nodes):
                target_matrix = stored_matrices[i] * stored_driver_inverse * current_driver_matrix
                cmds.xform(driven_node, matrix=list(target_matrix), worldSpace=True)
            
            cmds.setKeyframe(driven_nodes, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
    
    finally:
        try:
            cmds.currentTime(current_frame, edit=True)
        except:
            pass
        try:
            cmds.refresh(suspend=False)
        except:
            pass
        try:
            if original_eval_mode:
                cmds.evaluationManager(mode=original_eval_mode[0])
        except:
            pass
        try:
            cmds.undoInfo(closeChunk=True)
        except:
            pass


def apply_at_keyframes(xform_list, start_frame, end_frame):
    if len(xform_list) < 2:
        cmds.warning("Need at least 2 objects for bake keys")
        return
    
    driver_info = xform_list[-1]
    driver_node = find_node(driver_info["nodeName"])
    
    if not driver_node:
        cmds.warning("Driver node not found")
        return
    
    driven_nodes = []
    stored_matrices = []
    
    for node_info in xform_list[:-1]:
        node = find_node(node_info["nodeName"])
        if node:
            driven_nodes.append(node)
            stored_matrices.append(om.MMatrix(node_info["matrix"]))
    
    if not driven_nodes:
        cmds.warning("No driven nodes found")
        return
    
    object_keyframes = get_object_keyframes(driven_nodes, start_frame, end_frame)
    driver_keyframes = get_object_keyframes([driver_node], start_frame, end_frame)
    
    if object_keyframes and len(object_keyframes) >= len(driver_keyframes):
        keyframes = object_keyframes
    elif driver_keyframes:
        keyframes = driver_keyframes
    else:
        cmds.warning("No keyframes found on driven or driver objects.")
        return
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(keyframes[0], keyframes[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    stored_driver_matrix = om.MMatrix(driver_info["matrix"])
    stored_driver_inverse = stored_driver_matrix.inverse()
    current_frame = cmds.currentTime(query=True)
    
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Relationship At Keys")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in keyframes:
            cmds.currentTime(frame, edit=True)
            
            current_driver_matrix = om.MMatrix(cmds.xform(driver_node, query=True, matrix=True, worldSpace=True))
            
            for i, driven_node in enumerate(driven_nodes):
                target_matrix = stored_matrices[i] * stored_driver_inverse * current_driver_matrix
                cmds.xform(driven_node, matrix=list(target_matrix), worldSpace=True)
            
            cmds.setKeyframe(driven_nodes, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
    
    finally:
        try:
            cmds.currentTime(current_frame, edit=True)
        except:
            pass
        try:
            cmds.refresh(suspend=False)
        except:
            pass
        try:
            if original_eval_mode:
                cmds.evaluationManager(mode=original_eval_mode[0])
        except:
            pass
        try:
            cmds.undoInfo(closeChunk=True)
        except:
            pass


apply_spatial_link_current_frame()
