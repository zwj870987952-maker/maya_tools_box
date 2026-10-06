from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

try:
    from PySide6.QtGui import QGuiApplication
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2.QtGui import QGuiApplication
        PYSIDE_VERSION = 2
    except ImportError:
        PYSIDE_VERSION = 1
        QGuiApplication = None

try:
    import maya.cmds as cmds
    IN_MAYA = True
except ImportError:
    IN_MAYA = False

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

max = builtins.max
min = builtins.min

def get_maya_version():
    if not IN_MAYA:
        return 2024
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except:
        return 2022

def get_dpi_scale():
    maya_version = get_maya_version()
    
    dpi = 96.0
    base_scale = 1.0
    got_screen_info = False
    
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                try:
                    dpi = screen.logicalDotsPerInch()
                    got_screen_info = True
                except (RuntimeError, AttributeError):
                    pass
            
            if got_screen_info:
                base_scale = dpi / 96.0
                
    except (RuntimeError, AttributeError):
        pass
    except Exception:
        pass
    
    if maya_version >= 2025:
        if base_scale > 2.0:
            return max(1.0, min(base_scale * 1.15, 3.0))
        return max(1.0, min(base_scale, 3.0))
    
    if maya_version >= 2022 and maya_version <= 2024:
        return max(1.0, min(base_scale, 3.0))
    
    return max(1.0, min(base_scale, 3.0))

def scale_size(size):
    return int(size * get_dpi_scale())

def scale_font_size(size):
    return int(size * get_dpi_scale())
