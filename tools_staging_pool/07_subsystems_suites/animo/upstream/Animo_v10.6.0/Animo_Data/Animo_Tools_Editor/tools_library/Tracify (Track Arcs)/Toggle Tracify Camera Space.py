import os
import sys

import maya.cmds as cmds


def _get_animo_data_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data")


animo_data_path = _get_animo_data_path()
tracify_dir = os.path.join(animo_data_path, "Animo_Launcher")

if tracify_dir not in sys.path:
    sys.path.insert(0, tracify_dir)

import tracify_launcher


def _is_panel_visible(panel):
    try:
        control = cmds.panel(panel, query=True, control=True)
        if control and cmds.control(control, exists=True):
            return cmds.control(control, query=True, visible=True)
    except Exception:
        pass
    return False


def _focus_best_viewport():
    panels = cmds.getPanel(type="modelPanel") or []
    visible_panels = [p for p in panels if _is_panel_visible(p)]

    for panel in visible_panels:
        try:
            cam = cmds.modelPanel(panel, query=True, camera=True)
        except Exception:
            continue
        if not cam or not cmds.objExists(cam):
            continue
        try:
            if cmds.camera(cam, query=True, orthographic=True):
                continue
        except Exception:
            continue
        cmds.setFocus(panel)
        return

    if visible_panels:
        cmds.setFocus(visible_panels[0])


_focus_best_viewport()

tracify_launcher.toggle_camera_space()

ui_instance = getattr(tracify_launcher, "_tracify_ui_instance", None)
if ui_instance is not None:
    try:
        new_state = tracify_launcher.load_camera_space()
        ui_instance.camera_space_checkbox.blockSignals(True)
        ui_instance.camera_space_checkbox.setChecked(new_state)
        ui_instance.camera_space_checkbox.blockSignals(False)
    except Exception:
        pass
