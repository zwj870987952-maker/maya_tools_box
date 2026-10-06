import maya.cmds as cmds
import os
import sys
import importlib
import importlib.util
import importlib.machinery

TOOL_NAME = "reset_transform"
TOOLS_PATH = "Animo_Reset"


def _animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


def _maya_version():
    return int(cmds.about(version=True)[:4])


def _run_tool(tool_folder, launcher_name):
    animo_data_path = _animo_data_path()
    maya_version = _maya_version()
    tool_path = os.path.normpath(os.path.join(animo_data_path, tool_folder))

    if tool_path not in sys.path:
        sys.path.insert(0, tool_path)

    if launcher_name in sys.modules:
        del sys.modules[launcher_name]

    py_path = os.path.normpath(os.path.join(tool_path, launcher_name + ".py"))
    pyc_versioned = os.path.normpath(os.path.join(tool_path, "{}_py{}.pyc".format(launcher_name, maya_version)))
    pyc_path = os.path.normpath(os.path.join(tool_path, launcher_name + ".pyc"))

    if os.path.exists(py_path):
        target_path = py_path
    elif os.path.exists(pyc_versioned):
        target_path = pyc_versioned
    elif os.path.exists(pyc_path):
        target_path = pyc_path
    else:
        cmds.warning("Could not find {} in {}".format(launcher_name, tool_path))
        return

    if target_path.lower().endswith(".pyc"):
        loader = importlib.machinery.SourcelessFileLoader(launcher_name, target_path)
        spec = importlib.util.spec_from_loader(launcher_name, loader, origin=target_path)
    else:
        spec = importlib.util.spec_from_file_location(launcher_name, target_path)

    module = importlib.util.module_from_spec(spec)
    sys.modules[launcher_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        sys.modules.pop(launcher_name, None)
        cmds.warning("Failed to run {}: {}".format(launcher_name, str(e)))


cmds.undoInfo(openChunk=True)
try:
    _run_tool(TOOLS_PATH, TOOL_NAME)
finally:
    cmds.undoInfo(closeChunk=True)
