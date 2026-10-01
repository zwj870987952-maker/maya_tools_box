try:
    from PySide6 import QtGui, QtCore, QtUiTools, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtUiTools, QtWidgets
    from shiboken2 import wrapInstance
