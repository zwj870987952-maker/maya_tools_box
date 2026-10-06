"""
Qt Compatibility Layer for PySide2/PySide6
"""
from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    PYSIDE_VERSION = 2
