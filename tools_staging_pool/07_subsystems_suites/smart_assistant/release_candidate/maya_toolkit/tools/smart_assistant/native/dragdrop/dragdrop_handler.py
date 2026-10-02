"""Owned QObject filter retained until explicit stop; Qt6/Qt5 supported."""
_filter=None
def _qt():
    try:
        from PySide6 import QtWidgets,QtCore
        from shiboken6 import wrapInstance
    except ImportError:
        from PySide2 import QtWidgets,QtCore
        from shiboken2 import wrapInstance
    return QtWidgets,QtCore,wrapInstance
def start_dragdrop_monitor():
    global _filter
    if _filter is not None:return
    from maya import cmds,OpenMayaUI
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    QtWidgets,QtCore,wrapInstance=_qt();app=QtWidgets.QApplication.instance()
    ptr=OpenMayaUI.MQtUtil.mainWindow()
    if app is None or not ptr:raise RuntimeError('Maya main window unavailable')
    if QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Maya main thread required')
    main=wrapInstance(int(ptr),QtWidgets.QWidget)
    _filter=make_filter(main,app)
    app.installEventFilter(_filter)
def stop_dragdrop_monitor():
    global _filter
    if _filter is None:return
    QtWidgets,_,_=_qt();app=QtWidgets.QApplication.instance()
    if app:app.removeEventFilter(_filter)
    _filter.deleteLater();_filter=None
def supported(paths):
    from pathlib import Path
    from ...config_io import FILES,sequence
    if not paths:return False
    if len(paths)==1 and Path(paths[0]).is_dir():
        try:sequence(paths[0]);return True
        except (ValueError,OSError):return False
    return all(Path(p).is_file() and Path(p).suffix.lower() in FILES for p in paths)
def make_filter(main,parent=None):
    QtWidgets,QtCore,_=_qt()
    class DragDropEventFilter(QtCore.QObject):
        def eventFilter(self,obj,event):
            if not isinstance(obj,QtWidgets.QWidget) or not (obj is main or main.isAncestorOf(obj)):return False
            if event.type() not in (QtCore.QEvent.Drop,QtCore.QEvent.DragEnter,QtCore.QEvent.DragMove):return False
            mime=event.mimeData()
            if not mime.hasUrls():return False
            paths=[url.toLocalFile() for url in mime.urls()]
            if not supported(paths):return False
            if event.type()==QtCore.QEvent.Drop:
                from .file_actions import handle_drop
                try:handle_drop(paths)
                except Exception as e:
                    from maya import cmds
                    cmds.warning(str(e))
            event.acceptProposedAction();return True
    return DragDropEventFilter(parent)
