"""Explicit native suite lifecycle and scene API; no import-time window or scene changes."""
from pathlib import Path
import maya.cmds as cmds
from .bundle.GETOOLS_SOURCE import Settings
from .bundle.GETOOLS_SOURCE.modules import GeneralWindow,Options,CenterOfMass
WINDOW=None
COM=None

class BoolValue:
    def __init__(self,value=False):self.value=value
    def Get(self):return self.value

def com_instance():
    global COM
    if COM is None:
        options=Options.PluginVariables();options.menuCheckboxEulerFilter=BoolValue(False)
        COM=CenterOfMass.CenterOfMass(options)
    return COM

def show():
    global WINDOW
    if cmds.about(batch=True):raise RuntimeError('Interactive Maya required')
    WINDOW=GeneralWindow.GeneralWindow()
    WINDOW.RUN_DOCKED(str(Path(__file__).parent/'bundle'),forced=True)
    return WINDOW

def close():
    global WINDOW
    if cmds.dockControl(Settings.dockName,exists=True):cmds.deleteUI(Settings.dockName,control=True)
    if cmds.window(Settings.windowName,exists=True):cmds.deleteUI(Settings.windowName)
    WINDOW=None

def overlap_instance():
    if WINDOW is None or not cmds.window(Settings.windowName,exists=True):raise RuntimeError('Open the candidate GETools window before configuring/baking its existing UI controls')
    return WINDOW.moduleOverlappy
