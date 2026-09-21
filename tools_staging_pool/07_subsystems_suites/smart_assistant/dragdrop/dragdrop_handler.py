import maya.OpenMayaUI as omui
from . import file_actions

# 统一导入QtWidgets和QtCore，保证全局可用
try:
    from shiboken2 import wrapInstance
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from shiboken import wrapInstance
    from PySide import QtGui as QtWidgets
    from PySide import QtCore

_dragdrop_installed = False

def start_dragdrop_monitor():
    global _dragdrop_installed
    if _dragdrop_installed:
        return
    main_window_ptr = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    main_window.installEventFilter(DragDropEventFilter(main_window))
    _dragdrop_installed = True

class DragDropEventFilter(QtWidgets.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Drop:
            mime = event.mimeData()
            if mime.hasUrls():
                paths = [url.toLocalFile() for url in mime.urls()]
                file_actions.handle_drop(paths)
                return True
        return False 