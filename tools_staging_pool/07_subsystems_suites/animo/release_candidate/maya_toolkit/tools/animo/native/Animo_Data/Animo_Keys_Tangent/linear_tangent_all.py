import maya.cmds as cmds
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


def linear_tangent_all():
    selection = cmds.ls(sl=True)
    if not selection:
        return
    
    cmds.keyTangent(selection, edit=True, itt=IN_TANGENT, ott=OUT_TANGENT)


def run():
    marker_module = load_marker_module()
    
    if marker_module:
        start = cmds.playbackOptions(q=True, minTime=True)
        end = cmds.playbackOptions(q=True, maxTime=True)
        marker_module.mark_range(int(start), int(end), auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
    
    linear_tangent_all()
    
    if marker_module:
        marker_module.trigger_fade(delay=500)


run()
