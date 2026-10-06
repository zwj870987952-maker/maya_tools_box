import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_twosify_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "Animo_Twosify"))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Twosify")

_twosify_path = _get_twosify_path()
if _twosify_path not in sys.path:
    sys.path.insert(0, _twosify_path)

import update_selected_layer
reload(update_selected_layer)
