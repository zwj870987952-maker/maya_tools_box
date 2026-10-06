import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_nudge_keys_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Nudge_Keys"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Nudge_Keys")

_nudge_keys_path = _get_nudge_keys_path()
if _nudge_keys_path not in sys.path:
    sys.path.insert(0, _nudge_keys_path)

import nudge_keys_launcher
reload(nudge_keys_launcher)
