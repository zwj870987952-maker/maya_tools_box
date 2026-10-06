import maya.cmds as cmds
import os
import sys

_ROTATE_ORDER = 'yxz'

def _get_animo_space_switcher_dir():
    _version_script_dir = cmds.internalVar(userScriptDir=True)
    _scripts_dir = os.path.normpath(os.path.join(_version_script_dir, "..", "..", "scripts"))
    return os.path.join(_scripts_dir, "Animo_Data", "Animo_Space_Switcher")

_animo_dir = _get_animo_space_switcher_dir()

if not os.path.isdir(_animo_dir):
    cmds.error(
        "Animo Space Switcher folder not found:\n{0}".format(_animo_dir)
    )
else:
    if _animo_dir not in sys.path:
        sys.path.insert(0, _animo_dir)
    import AttributeSpaceSwitcher
    AttributeSpaceSwitcher.change_ro_enhanced(_ROTATE_ORDER)
