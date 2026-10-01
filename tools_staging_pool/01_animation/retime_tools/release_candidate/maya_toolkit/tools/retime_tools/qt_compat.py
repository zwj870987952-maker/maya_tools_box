"""Private binding facade. Original optional licensing modules are not altered."""
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance


def _wrapinstance(pointer, base=QtWidgets.QWidget):
    return wrapInstance(int(pointer), base)
