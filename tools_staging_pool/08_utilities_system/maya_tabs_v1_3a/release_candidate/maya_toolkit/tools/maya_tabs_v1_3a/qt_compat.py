"""Private Qt5/6 facade; never monkeypatch global QtWidgets."""
import types
try:
    from PySide6 import QtCore,QtGui,QtWidgets as _widgets
    import shiboken6 as shiboken
except ImportError:
    from PySide2 import QtCore,QtGui,QtWidgets as _widgets
    import shiboken2 as shiboken
QtWidgets=types.SimpleNamespace(**vars(_widgets))
for name in ('QAction','QShortcut','QUndoCommand','QUndoStack'):
    if not hasattr(QtWidgets,name) and hasattr(QtGui,name):setattr(QtWidgets,name,getattr(QtGui,name))
isValid=shiboken.isValid
Signal=QtCore.Signal;wrapInstance=shiboken.wrapInstance
