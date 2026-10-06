"""
DPI Scaling Utility for Maya Qt UIs

RULES:
- Use dpi() for: heights, widths, margins, padding, spacing, icon sizes
- Do NOT use dpi() for: font-size (pt), border-radius, border-width
  These look best at fixed pixel values regardless of DPI.

Example:
    button.setMinimumHeight(dpi(28))  # Scale height
    layout.setSpacing(dpi(6))         # Scale spacing
    button.setStyleSheet('''
        font-size: 8pt;        /* DON'T scale - pt is DPI-aware */
        border-radius: 5px;    /* DON'T scale - looks good fixed */
        padding: {}px {}px;    /* DO scale */
    '''.format(dpi(4), dpi(8)))
"""

try:
    from PySide6 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

BASE_DPI = 96.0

UI_SIZE_MULTIPLIER = 0.92

_scale_factor = None


def get_maya_main_window_widget():
    try:
        import maya.OpenMayaUI as mui
        maya_main_ptr = mui.MQtUtil.mainWindow()
        if not maya_main_ptr:
            return None
        return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)
    except Exception:
        return None


def get_reference_screen():
    app = QtWidgets.QApplication.instance()
    if not app:
        return None

    maya_widget = get_maya_main_window_widget()
    screen = get_screen_for_widget(maya_widget)
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


def get_screen_for_widget(widget):
    """Get the screen that contains the widget's center point."""
    if widget is None:
        return None
    
    try:
        app = QtWidgets.QApplication.instance()
        if not app:
            return None
        
        # Get the window's global position and size
        pos = widget.pos()
        size = widget.size()
        
        # Calculate center point in global coordinates
        center_x = pos.x() + size.width() // 2
        center_y = pos.y() + size.height() // 2
        center_point = QtCore.QPoint(center_x, center_y)
        
        # Find which screen contains this point
        screen = app.screenAt(center_point)
        if screen:
            return screen
        
        # Fallback to primary screen
        return app.primaryScreen()
    except:
        return None


def get_scale_factor_for_screen(screen=None):
    """Get the scale factor for a specific screen (always fresh, no caching)."""
    try:
        if screen:
            return (screen.logicalDotsPerInch() / BASE_DPI) * UI_SIZE_MULTIPLIER

        reference = get_reference_screen()
        if reference:
            return (reference.logicalDotsPerInch() / BASE_DPI) * UI_SIZE_MULTIPLIER
    except:
        pass

    return 1.0 * UI_SIZE_MULTIPLIER


def get_scale_factor():
    """Get the scale factor used for building UI."""
    global _scale_factor

    if _scale_factor is not None:
        return _scale_factor

    try:
        screen = get_reference_screen()
        if screen:
            _scale_factor = (screen.logicalDotsPerInch() / BASE_DPI) * UI_SIZE_MULTIPLIER
        else:
            _scale_factor = 1.0 * UI_SIZE_MULTIPLIER
    except:
        _scale_factor = 1.0 * UI_SIZE_MULTIPLIER

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
