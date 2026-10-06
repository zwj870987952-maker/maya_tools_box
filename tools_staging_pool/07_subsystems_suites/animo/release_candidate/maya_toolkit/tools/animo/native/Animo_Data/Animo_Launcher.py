import os
import maya.cmds as cmds
import runpy

version_script_dir = cmds.internalVar(userScriptDir=True)
script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
toggle_py = os.path.join(script_dir, "Animo_Data", "Animo_Launcher", "toggle.py")

if os.path.exists(toggle_py):
    runpy.run_path(toggle_py, run_name="__main__")