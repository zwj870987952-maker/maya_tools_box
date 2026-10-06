import maya.cmds as cmds
import os

def load_and_run():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = cmds.internalVar(userScriptDir=True)
    plugin_path = os.path.join(folder, "resetPosePlugin.py")
    if not cmds.pluginInfo(plugin_path, q=True, loaded=True):
        cmds.loadPlugin(plugin_path)
    cmds.resetPose()

load_and_run()