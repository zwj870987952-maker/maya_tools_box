import maya.cmds as cmds
import os
import sys

try:
    from importlib import reload
except ImportError:
    pass

def _get_select_opposite_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return script_dir
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools", "tools")

_select_opposite_path = _get_select_opposite_path()
if _select_opposite_path not in sys.path:
    sys.path.insert(0, _select_opposite_path)

import SelectAddOppositeCtrls
reload(SelectAddOppositeCtrls)
