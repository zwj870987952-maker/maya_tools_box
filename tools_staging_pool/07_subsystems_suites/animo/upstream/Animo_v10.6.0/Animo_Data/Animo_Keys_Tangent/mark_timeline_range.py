import shiboken2
from six import integer_types
from maya import mel
from maya import cmds
from maya import OpenMayaUI
from PySide2 import QtWidgets, QtGui, QtCore


def maya_to_qt(name, type_=QtWidgets.QWidget):
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        ptr = integer_types[-1](ptr)
        return shiboken2.wrapInstance(ptr, type_)
    raise RuntimeError("Failed to obtain a handle to '{}'.".format(name))


def get_timeline():
    timeline_path = mel.eval("$tmpVar=$gPlayBackSlider")
    timeline = maya_to_qt(timeline_path)
    for child in timeline.children():
        if isinstance(child, QtWidgets.QWidget):
            return child
    return timeline


class RangeColorOverlay(QtWidgets.QWidget):
    instance = None
    
    def __init__(self, parent):
        super(RangeColorOverlay, self).__init__(parent)
        
        self._color = None
        self._opacity = 0.15
        
        self._fade_delay_timer = QtCore.QTimer(self)
        self._fade_delay_timer.setSingleShot(True)
        self._fade_delay_timer.timeout.connect(self._start_fade)
        
        self._fade_timer = QtCore.QTimer(self)
        self._fade_timer.setInterval(30)
        self._fade_timer.timeout.connect(self._fade_step)
        
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        
        if parent:
            parent.installEventFilter(self)
            self.setGeometry(0, 0, parent.width(), parent.height())
        
        self.lower()
        self.show()
    
    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.setGeometry(0, 0, obj.width(), obj.height())
        return False
    
    def set_color(self, color, opacity):
        self._fade_delay_timer.stop()
        self._fade_timer.stop()
        
        parent = self.parent()
        if parent:
            self.setGeometry(0, 0, parent.width(), parent.height())
        
        self._color = QtGui.QColor(color)
        self._opacity = opacity
        
        self.show()
        self.raise_()
        self.lower()
        self.repaint()
        
        self._fade_delay_timer.start(1000)
    
    def _start_fade(self):
        self._fade_timer.start()
    
    def _fade_step(self):
        self._opacity -= 0.015
        if self._opacity <= 0:
            self._opacity = 0
            self._fade_timer.stop()
            self._color = None
        self.update()
    
    def paintEvent(self, event):
        if self._color is None:
            return
        
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        color = QtGui.QColor(self._color)
        color.setAlphaF(self._opacity)
        
        painter.fillRect(self.rect(), color)
        painter.end()


def mark_timeline_range():
    if RangeColorOverlay.instance is None:
        parent = get_timeline()
        RangeColorOverlay.instance = RangeColorOverlay(parent)
    
    RangeColorOverlay.instance.set_color("#8b0000", 0.15)


mark_timeline_range()