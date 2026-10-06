import maya.cmds as cmds
import maya.mel as mel
import os
import sys


IN_TANGENT = "linear"
OUT_TANGENT = "linear"
MARK_COLOR = "#1E90FF"
MARK_OPACITY = 0.20


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except Exception:
        return "unknown"


def load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")
    
    v = get_maya_version()
    n = "mark_frame"
    py = os.path.join(folder, n + ".py")
    pyc = os.path.join(folder, "{}_py{}.pyc".format(n, v))
    
    if not os.path.exists(py) and not os.path.exists(pyc):
        return None
    
    if folder not in sys.path:
        sys.path.insert(0, folder)
    
    if n in sys.modules:
        return sys.modules[n]
    
    try:
        import importlib
        return importlib.import_module(n)
    except Exception:
        return None


def get_graph_editor_key_range():
    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None
    
    min_time = min(selected_keys)
    max_time = max(selected_keys)
    
    if abs(max_time - min_time) < 0.001:
        return None
    
    return (int(min_time), int(max_time))


def linear_tangent():
    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = int(timeRange[0])
    EndRange = int(timeRange[1] - 1)
    ct = cmds.currentTime(q=True)
    
    curveSel = cmds.keyframe(q=True, sl=True)
    
    if curveSel:
        cmds.keyTangent(ott=OUT_TANGENT, itt=IN_TANGENT)
    else:
        if (EndRange - StartRange == 0):
            cmds.keyTangent(ott=OUT_TANGENT, itt=IN_TANGENT, t=(ct, ct))
        else:
            cmds.keyTangent(ott=OUT_TANGENT, itt=IN_TANGENT, t=(StartRange, EndRange))


def run():
    marker_module = load_marker_module()
    
    if marker_module:
        graph_range = get_graph_editor_key_range()
        if graph_range:
            marker_module.mark_range(graph_range[0], graph_range[1], auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        else:
            marker_module.mark_current_frame(auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
    
    linear_tangent()
    
    if marker_module:
        marker_module.trigger_fade(delay=500)


run()
