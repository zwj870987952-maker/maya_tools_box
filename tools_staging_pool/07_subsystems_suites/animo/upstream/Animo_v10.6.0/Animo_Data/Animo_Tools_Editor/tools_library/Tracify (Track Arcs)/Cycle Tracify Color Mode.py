import os
import sys

import maya.cmds as cmds

COLOR_MODES = [0, 1, 2, 3, 4]


def _get_animo_data_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data")


def cycle_tracify_color_mode():
    animo_data_path = _get_animo_data_path()
    tracify_dir = os.path.join(animo_data_path, "Animo_Launcher")

    if not os.path.exists(os.path.join(tracify_dir, "tracify_launcher.py")):
        cmds.error("Cycle Tracify Color Mode: Could not find tracify_launcher.py in {}".format(tracify_dir))
        return

    if tracify_dir not in sys.path:
        sys.path.insert(0, tracify_dir)

    tracify_launcher = sys.modules.get("tracify_launcher")
    if tracify_launcher is None:
        import tracify_launcher

    current_mode = tracify_launcher.load_color_mode()
    next_index = (COLOR_MODES.index(current_mode) + 1) % len(COLOR_MODES) if current_mode in COLOR_MODES else 0
    next_mode = COLOR_MODES[next_index]

    tracify_launcher.save_color_mode(next_mode)
    tracify = tracify_launcher.get_tracify()
    if tracify:
        tracify.setColorMode(next_mode)


cycle_tracify_color_mode()
