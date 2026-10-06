import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_keys_tangent_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Keys_Tangent"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Keys_Tangent")

_keys_tangent_path = _get_keys_tangent_path()
if _keys_tangent_path not in sys.path:
    sys.path.insert(0, _keys_tangent_path)

import linear_tangent_global
reload(linear_tangent_global)
