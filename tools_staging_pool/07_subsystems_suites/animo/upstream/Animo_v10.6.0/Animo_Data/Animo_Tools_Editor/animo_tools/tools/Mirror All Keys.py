import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_animo_launcher_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Launcher"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Launcher")

_animo_launcher_path = _get_animo_launcher_path()
if _animo_launcher_path not in sys.path:
    sys.path.insert(0, _animo_launcher_path)

import mirror_all_keys
reload(mirror_all_keys)
