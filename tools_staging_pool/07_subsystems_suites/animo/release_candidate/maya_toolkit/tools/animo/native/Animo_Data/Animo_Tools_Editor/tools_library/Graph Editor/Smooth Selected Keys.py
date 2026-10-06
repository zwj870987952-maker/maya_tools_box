import maya.cmds as cmds
import os
import sys

_TOOL_FILENAME = 'AnimoSmoothKeysPlugin.py'

def _get_animo_tools_dir():
    try:
        _script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(_script_dir)
    except NameError:
        _version_script_dir = cmds.internalVar(userScriptDir=True)
        _scripts_dir = os.path.normpath(os.path.join(_version_script_dir, "..", "..", "scripts"))
        return os.path.join(_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools", "tools")

_animo_tools_dir = _get_animo_tools_dir()
_tool_path = os.path.join(_animo_tools_dir, _TOOL_FILENAME)

if not os.path.isfile(_tool_path):
    cmds.error(
        "Animo Tool not found: {0}\n"
        "Expected it in your Animo Tools folder:\n{1}".format(_TOOL_FILENAME, _animo_tools_dir)
    )
else:
    if not cmds.pluginInfo(_tool_path, query=True, loaded=True):
        _prevUndoFlushState = cmds.undoInfo(query=True, stateWithoutFlush=True)
        cmds.undoInfo(stateWithoutFlush=True)
        try:
            cmds.loadPlugin(_tool_path, quiet=True)
        finally:
            cmds.undoInfo(stateWithoutFlush=_prevUndoFlushState)
    cmds.smoothKeysAPI(strength=0.5, iterations=1)