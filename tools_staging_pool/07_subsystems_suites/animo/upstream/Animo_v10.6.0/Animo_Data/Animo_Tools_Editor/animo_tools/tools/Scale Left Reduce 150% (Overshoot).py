import maya.cmds as cmds
import os
import sys

TOOL_NAME = "scale_slider"
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
scale_slider = importlib.import_module(TOOLS_PATH + "." + TOOL_NAME)

class _FakeSlider(object):
    def __init__(self, value):
        self._value = value
    def value(self):
        return self._value
    def setValue(self, value):
        pass
    def blockSignals(self, blocked):
        pass

def run_preset(value):
    scale_slider.slider_logic(value, True, 0, 0, False, False)
    scale_slider.reset_slider(_FakeSlider(value))

run_preset(-150)
