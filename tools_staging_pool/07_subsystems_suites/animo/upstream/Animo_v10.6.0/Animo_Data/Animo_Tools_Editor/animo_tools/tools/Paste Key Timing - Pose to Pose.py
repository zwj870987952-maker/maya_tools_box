import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_keys_time_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Keys_Time"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Keys_Time")

_keys_time_path = _get_keys_time_path()
if _keys_time_path not in sys.path:
    sys.path.insert(0, _keys_time_path)

import paste_key_times_pose_to_pose
reload(paste_key_times_pose_to_pose)
