import os
import sys

import maya.cmds as cmds

DEFAULT_TRAIL_COLOR = (0.85, 0.12, 0.11)
DEFAULT_KEYS_COLOR = (0.95, 0.45, 0.45)
DEFAULT_COLOR_MODE = 1
DEFAULT_DOT_SIZE = 5
DEFAULT_LINE_WIDTH = 4
DEFAULT_CAMERA_SPACE = False


def _get_animo_data_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data")


def reset_tracify_to_default():
    animo_data_path = _get_animo_data_path()
    tracify_dir = os.path.join(animo_data_path, "Animo_Launcher")

    if not os.path.exists(os.path.join(tracify_dir, "tracify_launcher.py")):
        cmds.error("Reset Tracify To Default: Could not find tracify_launcher.py in {}".format(tracify_dir))
        return

    if tracify_dir not in sys.path:
        sys.path.insert(0, tracify_dir)

    tracify_launcher = sys.modules.get("tracify_launcher")
    if tracify_launcher is None:
        import tracify_launcher

    tracify_launcher.save_custom_colors(DEFAULT_TRAIL_COLOR, DEFAULT_KEYS_COLOR)

    tracify_launcher.save_color_mode(DEFAULT_COLOR_MODE)

    tracify_launcher.save_dot_size(DEFAULT_DOT_SIZE)
    tracify_launcher.save_line_width(DEFAULT_LINE_WIDTH)

    tracify_launcher.save_camera_space(DEFAULT_CAMERA_SPACE)

    tracify = tracify_launcher.get_tracify()
    if tracify:
        try:
            tracify.COLORS[0] = DEFAULT_TRAIL_COLOR
            tracify.KEY_COLOR = DEFAULT_KEYS_COLOR
            if hasattr(tracify, "_colorIndex"):
                tracify._colorIndex = 0

            if tracify._isPluginLoaded():
                nodes = cmds.ls(type="tracifyNode") or []
                for node in nodes:
                    cmds.setAttr(node + ".lineColorR", DEFAULT_TRAIL_COLOR[0])
                    cmds.setAttr(node + ".lineColorG", DEFAULT_TRAIL_COLOR[1])
                    cmds.setAttr(node + ".lineColorB", DEFAULT_TRAIL_COLOR[2])
                    cmds.setAttr(node + ".keyColorR", DEFAULT_KEYS_COLOR[0])
                    cmds.setAttr(node + ".keyColorG", DEFAULT_KEYS_COLOR[1])
                    cmds.setAttr(node + ".keyColorB", DEFAULT_KEYS_COLOR[2])
                cmds.refresh()

            tracify.setColorMode(DEFAULT_COLOR_MODE)
            tracify.setPointSize(float(DEFAULT_DOT_SIZE))
            tracify.setLineWidth(float(DEFAULT_LINE_WIDTH))
            tracify.setCameraSpace(DEFAULT_CAMERA_SPACE)
        except Exception:
            pass


reset_tracify_to_default()
