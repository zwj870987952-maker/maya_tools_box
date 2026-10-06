from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import platform

PY2 = sys.version_info[0] == 2
IS_MAC = platform.system() == "Darwin"

if PY2:
    string_types = (str, unicode)
    text_type = unicode
else:
    string_types = (str,)
    text_type = str

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6 import QtSvg
    from PySide6.QtSvg import QSvgRenderer
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2 import QtSvg
    from PySide2.QtSvg import QSvgRenderer
    PYSIDE_VERSION = 2


def get_maya_main_window():
    import maya.OpenMayaUI as omui
    
    if PYSIDE_VERSION == 6:
        from shiboken6 import wrapInstance
    else:
        from shiboken2 import wrapInstance
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    
    if main_window_ptr is None:
        return None
    
    if PY2:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def load_own_module(caller_file, module_filename, unique_name):
    import importlib.util
    import os as _os
    
    module_dir = _os.path.dirname(_os.path.abspath(caller_file))
    module_path = _os.path.join(module_dir, module_filename)
    
    spec = importlib.util.spec_from_file_location(unique_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
