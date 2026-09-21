"""Qt compatibility helpers for Maya PySide6/PySide2 environments."""

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance


def get_qt_enum(owner, name):
    """Return a Qt enum value across PySide2 and PySide6."""
    parts = name.split(".")
    value = owner
    for part in parts:
        value = getattr(value, part)
    return value


def qt_enum(*candidates):
    """Resolve the first available Qt enum path."""
    for owner, name in candidates:
        try:
            return get_qt_enum(owner, name)
        except AttributeError:
            continue
    raise AttributeError("None of the Qt enum candidates exist.")


def maya_main_window():
    """Return Maya's main window as a QWidget, or None outside Maya."""
    try:
        from maya import OpenMayaUI as omui
    except ImportError:
        return None

    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is None:
        return None

    try:
        integer_type = long
    except NameError:
        integer_type = int

    return wrapInstance(integer_type(main_window_ptr), QtWidgets.QWidget)
