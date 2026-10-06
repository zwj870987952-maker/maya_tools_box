import maya.cmds as cmds
import os
import sys
import importlib.util
import importlib.machinery

_MODULE_NAME = 'tweenify_launcher'
_TOOL_FILENAME = 'tweenify_launcher.py'


def get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


def _load_module_from_file(module_name, file_path):
    if module_name in sys.modules:
        del sys.modules[module_name]

    if file_path.lower().endswith(".pyc"):
        loader = importlib.machinery.SourcelessFileLoader(module_name, file_path)
        spec = importlib.util.spec_from_loader(module_name, loader, origin=file_path)
    else:
        spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:
        raise ImportError("Could not create module spec for {0}".format(file_path))

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


ANIMO_DATA_PATH = get_animo_data_path()
_animo_launcher_dir = os.path.join(ANIMO_DATA_PATH, "Animo_Launcher")
_tool_path = os.path.join(_animo_launcher_dir, _TOOL_FILENAME)

if not os.path.isfile(_tool_path):
    cmds.error("Animo Tool not found: {0}\nExpected it in: {1}".format(_TOOL_FILENAME, _animo_launcher_dir))
else:
    if _animo_launcher_dir not in sys.path:
        sys.path.insert(0, _animo_launcher_dir)
    _load_module_from_file(_MODULE_NAME, _tool_path)