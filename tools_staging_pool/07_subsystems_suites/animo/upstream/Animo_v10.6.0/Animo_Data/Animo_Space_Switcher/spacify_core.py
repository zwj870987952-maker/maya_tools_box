from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import os
import sys
import platform

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance

try:
    from importlib import reload
except ImportError:
    pass


SPACIFY_STATE = {
    "offset_field": None,
    "offset_value": None,
    "camera": None,
    "camera_field": None,
    "color_slider": None,
    "hue_slider": None
}


def get_animo_data_path():
    possible_paths = [
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2022", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2023", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2024", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2025", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
        os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


spacify_data_path = get_animo_data_path()

if spacify_data_path and spacify_data_path not in sys.path:
    sys.path.insert(0, spacify_data_path)
elif not spacify_data_path:
    cmds.warning("Spacify: Could not find Animo_Data/Animo_Space_Switcher folder")


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
