import maya.cmds as cmds
import os
import sys

TOOL_NAME = "tween_slider"
TOOLS_PATH = "Animo_Sliders"

def _get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")

_animo_data_path = _get_animo_data_path()
if _animo_data_path not in sys.path:
    sys.path.insert(0, _animo_data_path)

import importlib
tween_slider = importlib.import_module(TOOLS_PATH + "." + TOOL_NAME)
from Animo_Sliders import slider_utils

def tween_preset(value):
    selection = cmds.ls(selection=True)
    if not selection:
        return
    try:
        tween_slider.initialize_tween_undo()
        if not tween_slider.storedAnimCurves:
            return
        bias = (value + 100) / 200.0
        bias = tween_slider._amplify_overshoot_bias(bias)
        tween_slider.execute_tween_on_curves(bias)
        tween_slider.commit_tween_on_curves()
    finally:
        slider_utils.safe_undo_chunk_close()

tween_preset(33.3333)
