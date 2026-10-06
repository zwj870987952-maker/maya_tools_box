import maya.cmds as cmds
import os
import sys

_TOOL_FILENAME = 'Select Objects From Keys.py'

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
    with open(_tool_path, "r") as _f:
        _tool_code = _f.read()
    exec(compile(_tool_code, _tool_path, "exec"), {"__name__": "__main__", "__file__": _tool_path})
