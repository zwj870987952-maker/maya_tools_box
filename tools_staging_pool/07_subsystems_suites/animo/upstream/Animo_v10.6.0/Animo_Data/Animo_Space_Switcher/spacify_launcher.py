from __future__ import print_function, division, absolute_import

import os
import sys

def get_script_path():
    possible_paths = [
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2022", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2023", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2024", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2025", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "2022", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "2023", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "2024", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "2025", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "2022", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "2023", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "2024", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "2025", "scripts", "Animo_Data", "Animo_Space_Switcher"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

script_dir = get_script_path()
if script_dir and script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    reload
except NameError:
    from importlib import reload

MODULE_NAMES = [
    "spacify_core",
    "spacify_styles",
    "spacify_buttons",
    "spacify_actions",
    "tab_spaces",
    "tab_attribute",
    "tab_offset",
    "tab_xform",
    "AttributeSpaceSwitcher",
    "WorldSpace",
    "NewPivot",
    "TempIK",
    "ShiftSceneKeys",
    "CleanAndBake",
    "CameraSpace",
    "ControlsColor",
    "ChangeCtrlShape",
    "copy_xform",
    "copy_xform_range",
    "align_objects",
    "align_objects_translate",
    "align_objects_rotate",
    "align_objects_range",
    "align_objects_range_translate",
    "align_objects_range_rotate",
    "sequential_key_offset",
    "spacify_ui",
]

for mod_name in MODULE_NAMES:
    if mod_name in sys.modules:
        try:
            del sys.modules[mod_name]
        except Exception:
            pass

import spacify_ui
reload(spacify_ui)
from spacify_ui import SpacifyUI, get_maya_main_window

spacify_ui_instance = None


def create_spacify_ui():
    global spacify_ui_instance
    
    if spacify_ui_instance is not None:
        try:
            spacify_ui_instance.close()
            spacify_ui_instance.deleteLater()
        except Exception:
            pass
        spacify_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "SpacifyUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    spacify_ui_instance = SpacifyUI()
    spacify_ui_instance.show()
    return spacify_ui_instance


create_spacify_ui()