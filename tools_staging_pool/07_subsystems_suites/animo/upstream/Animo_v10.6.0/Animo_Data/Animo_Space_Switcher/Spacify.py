from __future__ import print_function, division, absolute_import

import os
import sys

def get_maya_version():
    import maya.cmds as cmds
    return int(cmds.about(version=True))

MAYA_VERSION = get_maya_version()

def get_script_path():
    # Try to find using __file__ first
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(script_dir):
            return script_dir
    except:
        pass
    
    # Fallback: search common locations
    home = os.path.expanduser("~")
    
    base_paths = [
        os.path.join(home, "Documents", "maya"),
        os.path.join(home, "maya"),
        os.path.join(home, "Library", "Preferences", "Autodesk", "maya"),
    ]
    
    sub_paths = [
        "scripts",
        "{0}/scripts".format(MAYA_VERSION),
    ]
    
    for base in base_paths:
        for sub in sub_paths:
            path = os.path.join(base, sub, "Animo_Data", "Animo_Space_Switcher")
            if os.path.exists(path):
                return path
    
    return None


def import_versioned_module(module_name, script_dir):
    """Import module - checks .py first, then version-specific .pyc, then generic .pyc"""
    
    if script_dir is None:
        return None
    
    # Clear cached modules
    if module_name in sys.modules:
        del sys.modules[module_name]
    versioned_name = "{0}_py{1}".format(module_name, MAYA_VERSION)
    if versioned_name in sys.modules:
        del sys.modules[versioned_name]
    
    # Check for .py file first (priority)
    py_path = os.path.join(script_dir, module_name + ".py")
    if os.path.exists(py_path):
        module = __import__(module_name)
        return module
    
    # Check for version-specific .pyc (e.g. spacify_core_py2026.pyc)
    pyc_versioned_path = os.path.join(script_dir, versioned_name + ".pyc")
    if os.path.exists(pyc_versioned_path):
        try:
            module = __import__(versioned_name)
            # Register under original name so other imports work
            sys.modules[module_name] = module
            return module
        except Exception:
            pass  # Fall through to generic .pyc
    
    # Check for generic .pyc
    pyc_path = os.path.join(script_dir, module_name + ".pyc")
    if os.path.exists(pyc_path):
        try:
            module = __import__(module_name)
            return module
        except Exception:
            pass
    
    # Fallback - try normal import (might find it elsewhere in sys.path)
    try:
        module = __import__(module_name)
        return module
    except Exception:
        return None


script_dir = get_script_path()
if script_dir and script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Only modules needed for UI - NOT action modules like TempIK, WorldSpace, etc.
UI_MODULE_NAMES = [
    "dpi_scale",
    "spacify_core",
    "spacify_styles",
    "spacify_buttons",
    "spacify_actions",
    "tab_spaces",
    "tab_attribute",
    "tab_offset",
    "tab_xform",
    "AttributeSpaceSwitcher",
    "CameraSpace",
    "ControlsColor",
    "ChangeCtrlShape",
    "spacify_ui",
]

# Import only UI modules with version support
for mod_name in UI_MODULE_NAMES:
    try:
        import_versioned_module(mod_name, script_dir)
    except Exception as e:
        pass  # Some modules may not exist, that's ok

# Get spacify_ui from sys.modules (it was registered there by import_versioned_module)
spacify_ui = sys.modules.get("spacify_ui")
if spacify_ui is None:
    raise ImportError("Could not import spacify_ui")

SpacifyUI = spacify_ui.SpacifyUI
get_maya_main_window = spacify_ui.get_maya_main_window

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


def show_ui():
    """Show/reopen the Spacify UI. Called for screen change DPI adjustment."""
    return create_spacify_ui()


create_spacify_ui()
