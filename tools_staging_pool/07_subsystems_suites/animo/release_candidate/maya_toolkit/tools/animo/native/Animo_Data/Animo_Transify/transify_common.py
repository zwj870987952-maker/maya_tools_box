from __future__ import division
from __future__ import absolute_import

import json
import os
import glob
import sys
import platform
import copy
import time as time_module
import math

from maya import cmds
from maya import mel
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

try:
    import maya.api.OpenMaya as om2
    import maya.api.OpenMayaAnim as oma2
    API2_AVAILABLE = True
except ImportError:
    API2_AVAILABLE = False

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    _max = builtins.max
    _min = builtins.min
    _int = builtins.int
    _str = builtins.str
    _range = builtins.range
except Exception:
    _max = max
    _min = min
    _int = int
    _str = str
    _range = range

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtGui, QtCore
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1

import importlib

BASE_DPI = 96.0

_scale_factor = None


def get_screen_for_widget(widget):
    """Get the screen that contains the widget's center point."""
    if widget is None:
        return None
    
    try:
        app = QtWidgets.QApplication.instance()
        if not app:
            return None
        
        pos = widget.pos()
        size = widget.size()
        
        center_x = pos.x() + size.width() // 2
        center_y = pos.y() + size.height() // 2
        center_point = QtCore.QPoint(center_x, center_y)
        
        screen = app.screenAt(center_point)
        if screen:
            return screen
        
        return app.primaryScreen()
    except:
        return None


def get_scale_factor_for_screen(screen=None):
    """Get the scale factor for a specific screen (always fresh, no caching)."""
    try:
        if screen:
            return _max(1.0, _min(screen.logicalDotsPerInch() / BASE_DPI, 3.0))
        
        app = QtWidgets.QApplication.instance()
        if app:
            primary = app.primaryScreen()
            if primary:
                return _max(1.0, _min(primary.logicalDotsPerInch() / BASE_DPI, 3.0))
    except:
        pass
    
    return 1.0


def get_scale_factor():
    """Get the scale factor used for building UI."""
    global _scale_factor
    
    if cmds.optionVar(exists="esnTransifyScale"):
        override = cmds.optionVar(q="esnTransifyScale")
        if override:
            return _max(0.5, _min(override, 3.0))
    
    if _scale_factor is not None:
        return _scale_factor
    
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                _scale_factor = _max(1.0, _min(screen.logicalDotsPerInch() / BASE_DPI, 3.0))
            else:
                _scale_factor = 1.0
        else:
            _scale_factor = 1.0
    except:
        _scale_factor = 1.0
    
    return _scale_factor


def set_scale_factor(value):
    """Explicitly set the scale factor (call before building UI)."""
    global _scale_factor
    _scale_factor = value


def reset_scale_factor():
    """Reset scale factor so it will be recalculated."""
    global _scale_factor
    _scale_factor = None


def dpi(value):
    """Scale a PIXEL value by the screen DPI.
    
    Use for: heights, widths, margins, padding, spacing, icon sizes
    Do NOT use for: font-size, border-radius, border-width
    """
    return int(value * get_scale_factor())


def dpif(value):
    """Scale a pixel value by the screen DPI, return as float."""
    return value * get_scale_factor()


def scale_size(size):
    return dpi(size)


def is_macos():
    return platform.system() == "Darwin"


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(_int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def get_dialog_stylesheet():
    """Return the common stylesheet for styled dialogs with DPI scaling."""
    return """
        QDialog {{
            background-color: rgb(38, 38, 38);
            color: #E0E0E0;
        }}
        QLabel {{
            color: #E0E0E0;
            background: transparent;
        }}
        QPushButton {{
            background-color: #3A3A3A;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #E0E0E0;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
        QPushButton:hover {{
            background-color: #4A4A4A;
        }}
        QPushButton:pressed {{
            background-color: #2A2A2A;
        }}
        QPushButton#primaryBtn {{
            background-color: #3A7BC8;
            border: none;
        }}
        QPushButton#primaryBtn:hover {{
            background-color: #4A8BD8;
        }}
    """.format(dpi(8), dpi(16))


def show_styled_error(title, message):
    """Show a styled error dialog with OK button."""
    parent = get_maya_main_window()
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    dialog.setModal(True)
    dialog.setMinimumWidth(dpi(300))
    dialog.setStyleSheet(get_dialog_stylesheet())
    
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(dpi(20), dpi(20), dpi(20), dpi(20))
    layout.setSpacing(dpi(12))
    
    msg_label = QtWidgets.QLabel(message)
    msg_label.setWordWrap(True)
    layout.addWidget(msg_label)
    
    layout.addSpacing(dpi(8))
    
    btn_layout = QtWidgets.QHBoxLayout()
    btn_layout.addStretch()
    
    ok_btn = QtWidgets.QPushButton("OK")
    ok_btn.setObjectName("primaryBtn")
    ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
    ok_btn.setMinimumWidth(dpi(70))
    ok_btn.clicked.connect(dialog.accept)
    
    btn_layout.addWidget(ok_btn)
    layout.addLayout(btn_layout)
    
    dialog.exec_() if PYSIDE_VERSION == 2 else dialog.exec()


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=("TransifyUI_WindowPos", pos_str))


def load_window_position():
    if cmds.optionVar(exists="TransifyUI_WindowPos"):
        try:
            pos_str = cmds.optionVar(q="TransifyUI_WindowPos")
            x, y = pos_str.split(",")
            return QtCore.QPoint(_int(x), _int(y))
        except Exception:
            pass
    return None


def get_all_screens():
    """Get list of all available screens."""
    screens = []
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            if hasattr(app, 'screens'):
                screens = app.screens()
            elif hasattr(app, 'desktop'):
                desktop = app.desktop()
                for i in range(desktop.screenCount()):
                    screens.append(desktop.screenGeometry(i))
    except:
        pass
    return screens


def get_combined_screen_geometry():
    """Get the bounding rect of all screens combined."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return QtCore.QRect(0, 0, 1920, 1080)
    
    try:
        screens = get_all_screens()
        if not screens:
            return QtCore.QRect(0, 0, 1920, 1080)
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for screen in screens:
            if hasattr(screen, 'geometry'):
                geo = screen.geometry()
            else:
                geo = screen  # Already a QRect
            
            min_x = _min(min_x, geo.x())
            min_y = _min(min_y, geo.y())
            max_x = _max(max_x, geo.x() + geo.width())
            max_y = _max(max_y, geo.y() + geo.height())
        
        return QtCore.QRect(_int(min_x), _int(min_y), _int(max_x - min_x), _int(max_y - min_y))
    except:
        return QtCore.QRect(0, 0, 1920, 1080)


def is_position_visible(pos, window_width, window_height, margin=50):
    """Check if a window position would be at least partially visible on any screen."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return False
    
    try:
        screens = get_all_screens()
        if not screens:
            return False
        
        window_rect = QtCore.QRect(pos.x(), pos.y(), window_width, window_height)
        
        for screen in screens:
            if hasattr(screen, 'geometry'):
                screen_geo = screen.geometry()
            else:
                screen_geo = screen
            
            intersection = window_rect.intersected(screen_geo)
            if intersection.width() >= margin and intersection.height() >= margin:
                return True
        
        return False
    except:
        return False


def get_screen_at_position(pos):
    """Get the screen that contains the given position."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return None
    
    try:
        if hasattr(app, 'screenAt'):
            return app.screenAt(pos)
        else:
            screens = get_all_screens()
            for screen in screens:
                if hasattr(screen, 'geometry'):
                    geo = screen.geometry()
                else:
                    geo = screen
                if geo.contains(pos):
                    return screen
    except:
        pass
    return None


def get_center_of_primary_screen():
    """Get the center point of the primary screen."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return QtCore.QPoint(960, 540)
    
    try:
        if hasattr(app, 'primaryScreen'):
            screen = app.primaryScreen()
            if screen:
                geo = screen.geometry()
                return QtCore.QPoint(geo.x() + geo.width() // 2, geo.y() + geo.height() // 2)
        elif hasattr(app, 'desktop'):
            desktop = app.desktop()
            geo = desktop.screenGeometry()
            return QtCore.QPoint(geo.width() // 2, geo.height() // 2)
    except:
        pass
    return QtCore.QPoint(960, 540)


def get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


ANIMO_DATA_PATH = get_animo_data_path()
TRANSIFY_PATH = os.path.join(ANIMO_DATA_PATH, "Animo_Transify")

if TRANSIFY_PATH not in sys.path:
    sys.path.insert(0, TRANSIFY_PATH)


def load_transify_module(module_name):
    module_path = None
    for ext in (".py", ".pyc"):
        potential_path = os.path.join(TRANSIFY_PATH, module_name + ext)
        if os.path.exists(potential_path):
            module_path = potential_path
            break

    if not module_path:
        cmds.warning("{} script not found in: {}".format(module_name, TRANSIFY_PATH))
        return None

    if TRANSIFY_PATH not in sys.path:
        sys.path.insert(0, TRANSIFY_PATH)

    for mod_name in list(sys.modules.keys()):
        if mod_name == module_name:
            del sys.modules[mod_name]

    importlib.invalidate_caches()
    return importlib.import_module(module_name)