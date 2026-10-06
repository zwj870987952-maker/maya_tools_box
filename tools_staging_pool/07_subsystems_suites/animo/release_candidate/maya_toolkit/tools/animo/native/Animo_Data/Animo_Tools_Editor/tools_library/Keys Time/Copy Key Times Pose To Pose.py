import os
import sys
import importlib
import importlib.util

import maya.cmds as cmds


def _get_animo_data_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data")


def _run_animo_script(tool_folder, script_name):
    animo_data_path = _get_animo_data_path()
    tool_path = os.path.join(animo_data_path, tool_folder)
    script_path = os.path.join(tool_path, script_name + ".py")

    if not os.path.exists(script_path):
        cmds.error("Could not find {}.py in {}".format(script_name, tool_path))
        return

    if tool_path not in sys.path:
        sys.path.insert(0, tool_path)

    if script_name in sys.modules:
        del sys.modules[script_name]

    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[script_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(script_name, None)
        raise


_run_animo_script("Animo_Keys_Time", "copy_key_times_pose_to_pose")
