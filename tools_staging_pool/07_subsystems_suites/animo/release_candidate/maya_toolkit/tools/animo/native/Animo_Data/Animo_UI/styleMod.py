'''
    Animo UI Style Module
'''

import maya.cmds as cmds
import os
import json

try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets

from . import dpi_scale


def _get_prefs_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data", "Animo_Prefs")


def get_user_scale():
    """Get user's preferred UI scale (1.0 = default, 1.3 = 30% bigger, etc.)"""
    try:
        prefs_path = _get_prefs_path()
        pref_file = os.path.join(prefs_path, "size_prefs.json")
        if os.path.exists(pref_file):
            with open(pref_file, 'r') as f:
                data = json.load(f)
                return data.get("scale", 1.0)
    except:
        pass
    return 1.0


def set_user_scale(scale):
    """Set user's preferred UI scale"""
    try:
        prefs_path = _get_prefs_path()
        if not os.path.exists(prefs_path):
            os.makedirs(prefs_path)
        pref_file = os.path.join(prefs_path, "size_prefs.json")
        with open(pref_file, 'w') as f:
            json.dump({"scale": scale}, f)
        return True
    except:
        return False


def get_dpi_scale():
    try:
        scale = dpi_scale.get_scale_factor()
        return max(0.5, min(scale, 3.0))
    except:
        pass
    return 1.0


USER_SCALE = get_user_scale()
DPI_SCALE = get_dpi_scale() * USER_SCALE


def scaled(value):
    return int(value * DPI_SCALE)


ICON_SIZE_BASE = 24  # 7% smaller
ICON_WIDTH = scaled(ICON_SIZE_BASE)
ICON_HEIGHT = scaled(ICON_SIZE_BASE)
ICON_SPACING = scaled(8)  # Horizontal mode spacing
ICON_SPACING_VERTICAL = scaled(12)  # More space for vertical mode
TOOLBAR_WIDTH = scaled(34)  # For vertical mode
TOOLBAR_HEIGHT = scaled(38)  # For horizontal mode - taller to center icons better

TOOLBAR_BG_COLOR = [0.22, 0.22, 0.22]
TOOLBAR_BG_COLOR_LIGHT = [0.25, 0.25, 0.25]  # For timeline modes
TOOLBAR_BG_COLOR_LIGHTER = [0.27, 0.27, 0.27]  # For shelf/statusline modes