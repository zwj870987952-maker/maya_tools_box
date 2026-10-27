"""Real installed Qt bindings, selected lazily by upstream UI modules."""
try:
    from PySide6 import QtWidgets,QtCore,QtGui
except ImportError:
    from PySide2 import QtWidgets,QtCore,QtGui
