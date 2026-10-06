import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_space_switcher_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Space_Switcher"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Space_Switcher")

_space_switcher_path = _get_space_switcher_path()
if _space_switcher_path not in sys.path:
    sys.path.insert(0, _space_switcher_path)

import align_objects_range_rotate
reload(align_objects_range_rotate)
align_objects_range_rotate.align_range_rotate()
