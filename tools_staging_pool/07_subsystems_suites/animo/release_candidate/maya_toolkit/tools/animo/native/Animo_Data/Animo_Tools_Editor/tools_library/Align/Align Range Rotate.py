import os
import sys
import importlib

import maya.cmds as cmds


def _get_animo_tools_dir():
    _version_script_dir = cmds.internalVar(userScriptDir=True)
    _scripts_dir = os.path.normpath(os.path.join(_version_script_dir, "..", "..", "scripts"))
    return os.path.join(_scripts_dir, "Animo_Data", "Animo_Space_Switcher")


_animo_tools_dir = _get_animo_tools_dir()

if not os.path.isdir(_animo_tools_dir):
    cmds.error("Animo Tool folder not found:\n{0}".format(_animo_tools_dir))

if _animo_tools_dir not in sys.path:
    sys.path.insert(0, _animo_tools_dir)

import align_objects_range_rotate
importlib.reload(align_objects_range_rotate)

cmds.undoInfo(openChunk=True, chunkName="Align Range Rotate")
try:
    align_objects_range_rotate.align_range_rotate()
finally:
    cmds.undoInfo(closeChunk=True)
