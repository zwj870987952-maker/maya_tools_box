"""
DPI Scaling Utilities for High-DPI Display Support
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance


def _get_maya_main_window_widget():
    try:
        import maya.OpenMayaUI as mui
        maya_main_ptr = mui.MQtUtil.mainWindow()
        if not maya_main_ptr:
            return None
        return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)
    except Exception:
        return None


def _get_screen_for_widget(widget):
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


def get_reference_screen():
    app = QtWidgets.QApplication.instance()
    if not app:
        return None

    maya_widget = _get_maya_main_window_widget()
    screen = _get_screen_for_widget(maya_widget)
    if screen:
        return screen

    try:
        handle = maya_widget.windowHandle() if maya_widget else None
        if handle:
            screen = handle.screen()
            if screen:
                return screen
    except Exception:
        pass

    return app.primaryScreen()


def get_dpi_scale():
    """Get the current DPI scale factor"""
    app = QtWidgets.QApplication.instance()
    if app:
        try:
            screen = get_reference_screen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                return dpi / 96.0
        except:
            pass
    return 1.0


def scale_size(base_size):
    """Scale a size value based on DPI"""
    return int(base_size * get_dpi_scale())


def scale_font_size(base_size):
    """Scale a font size (in pixels) based on DPI"""
    return int(base_size * get_dpi_scale())
