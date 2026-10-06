import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_fast_bake_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Fast_Bake"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Fast_Bake")

_fast_bake_path = _get_fast_bake_path()
if _fast_bake_path not in sys.path:
    sys.path.insert(0, _fast_bake_path)

import fast_bake_5s
reload(fast_bake_5s)
