try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui


TOOLTIP_STYLE = """
    QToolTip {
        background-color: #000000;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
"""


class DelayedTooltipFilter(QtCore.QObject):
    
    def __init__(self):
        super(DelayedTooltipFilter, self).__init__()
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(500)
        self._current_widget = None
        self._timer.timeout.connect(self._showTooltip)
    
    def _showTooltip(self):
        if self._current_widget and self._current_widget.toolTip():
            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(),
                self._current_widget.toolTip(),
                self._current_widget
            )
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self._current_widget = obj
            self._timer.start()
        elif event.type() == QtCore.QEvent.Leave:
            self._timer.stop()
            self._current_widget = None
            QtWidgets.QToolTip.hideText()
        return False


tooltip_filter = DelayedTooltipFilter()
