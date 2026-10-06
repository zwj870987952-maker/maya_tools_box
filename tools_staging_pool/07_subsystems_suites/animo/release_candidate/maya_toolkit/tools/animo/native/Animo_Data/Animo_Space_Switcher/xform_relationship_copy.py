from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.api.OpenMaya as om
import json
import os
import sys

SPATIAL_LINK_DATA_FILE = "animo_xform_relationship"
MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40


def get_data_file_path():
    user_app_dir = cmds.internalVar(userAppDir=True)
    prefs_folder = os.path.join(user_app_dir, "scripts", "Animo_Data", "Animo_Prefs")
    
    if not os.path.exists(prefs_folder):
        os.makedirs(prefs_folder)
    
    return os.path.join(prefs_folder, SPATIAL_LINK_DATA_FILE)


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


def is_transform_node(node):
    node_type = cmds.nodeType(node)
    return node_type in ['transform', 'joint']


def get_world_matrix(node):
    return cmds.xform(node, query=True, matrix=True, worldSpace=True)


def capture_spatial_link():
    selection = cmds.ls(sl=True, long=True)
    selection = [obj for obj in selection if is_transform_node(obj)]
    
    if len(selection) < 2:
        cmds.inViewMessage(
            amg='<span style="color:#f58b3a;">Please select at least 2 objects</span>',
            pos='botCenter',
            fade=True
        )
        return
    
    marker = load_mark_frame()
    if marker:
        marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    current_frame = cmds.currentTime(query=True)
    
    xform_nodes_list = []
    for obj in selection:
        world_matrix = get_world_matrix(obj)
        xform_nodes_list.append({
            "nodeName": obj,
            "matrix": world_matrix
        })
    
    data = {
        "frames": [current_frame],
        "xformNodesListInfo": xform_nodes_list
    }
    
    file_path = get_data_file_path()
    with open(file_path, 'w') as outFile:
        json.dump(data, outFile, indent=4)
    
    cmds.inViewMessage(
        amg='<span style="color:#4ca6e6;">Xform Relationship Copied</span>',
        pos='botCenter',
        fade=True
    )


capture_spatial_link()
