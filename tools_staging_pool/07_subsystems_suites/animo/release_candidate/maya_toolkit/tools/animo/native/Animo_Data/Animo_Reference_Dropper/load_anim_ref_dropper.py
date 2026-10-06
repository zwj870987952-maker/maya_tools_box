import os
import maya.cmds as cmds

version_script_dir = cmds.internalVar(userScriptDir=True)
script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
animo_data_path = os.path.join(script_dir, "Animo_Data")

plugin_path = os.path.join(animo_data_path, "Animo_Reference_Dropper", "anim_ref_dropper_plugin.py")

if cmds.pluginInfo(plugin_path, query=True, loaded=True):
    cmds.unloadPlugin(plugin_path)

cmds.loadPlugin(plugin_path)