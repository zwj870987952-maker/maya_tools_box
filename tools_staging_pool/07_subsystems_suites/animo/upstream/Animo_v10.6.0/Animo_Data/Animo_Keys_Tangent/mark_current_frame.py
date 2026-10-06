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


def get_timeline_path():
    return mel.eval("$tmpVar=$gPlayBackSlider")


def get_timeline():
    timeline_path = get_timeline_path()
    timeline = maya_to_qt(timeline_path)
    for child in timeline.children():
        if isinstance(child, QtWidgets.QWidget):
            return child
    return timeline


def get_selected_range():
    timeline_path = get_timeline_path()
    range_visible = cmds.timeControl(timeline_path, query=True, rangeVisible=True)
    if range_visible:
        range_array = cmds.timeControl(timeline_path, query=True, rangeArray=True)
        start_frame = int(range_array[0])
        end_frame = int(range_array[1]) - 1
        if end_frame > start_frame:
            return (start_frame, end_frame)
    return None


class FrameColorOverlay(QtWidgets.QWidget):
    instance = None
    
    def __init__(self, parent):
        super(FrameColorOverlay, self).__init__(parent)
        
        self._color = None
        self._opacity = 0.4
        self._marked_frame = None
        self._frame_range = None
        
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
    
    def set_color(self, color, opacity, frame=None, frame_range=None, auto_fade=True):
        self._fade_delay_timer.stop()
        self._fade_timer.stop()
        
        parent = self.parent()
        if parent:
            self.setGeometry(0, 0, parent.width(), parent.height())
        
        self._color = QtGui.QColor(color)
        self._opacity = opacity
        self._marked_frame = frame
        self._frame_range = frame_range
        
        self.show()
        self.raise_()
        self.lower()
        self.repaint()
        
        if auto_fade:
            self._fade_delay_timer.start(1000)
    
    def trigger_fade(self, delay=0):
        self._fade_delay_timer.stop()
        self._fade_timer.stop()
        if delay > 0:
            self._fade_delay_timer.start(delay)
        else:
            self._start_fade()
    
    def _start_fade(self):
        self._fade_timer.start()
    
    def _fade_step(self):
        self._opacity -= 0.015
        if self._opacity <= 0:
            self._opacity = 0
            self._fade_timer.stop()
            self._color = None
            self._marked_frame = None
            self._frame_range = None
        self.update()
    
    def paintEvent(self, event):
        if self._color is None:
            return
        
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        color = QtGui.QColor(self._color)
        color.setAlphaF(self._opacity)
        
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        total = self.width()
        step = (total - (total * 0.01)) / (end - start + 1)
        
        if self._frame_range is not None:
            range_start, range_end = self._frame_range
            pos_start = (range_start - start) * step + (total * 0.005)
            pos_end = (range_end - start + 1) * step + (total * 0.005)
            rect = QtCore.QRectF(pos_start, 0, pos_end - pos_start, self.height())
            painter.fillRect(rect, color)
        elif self._marked_frame is not None:
            pos = (self._marked_frame - start + 0.5) * step + (total * 0.005)
            pen = QtGui.QPen(color)
            pen.setWidthF(max(step, 3))
            painter.setPen(pen)
            line = QtCore.QLineF(QtCore.QPointF(pos, 0), QtCore.QPointF(pos, self.height()))
            painter.drawLine(line)
        
        painter.end()


def _ensure_overlay():
    if FrameColorOverlay.instance is None:
        parent = get_timeline()
        FrameColorOverlay.instance = FrameColorOverlay(parent)


def mark_current_frame(auto_fade=True):
    _ensure_overlay()
    
    selected_range = get_selected_range()
    if selected_range:
        FrameColorOverlay.instance.set_color("#8b0000", 0.3, frame_range=selected_range, auto_fade=auto_fade)
    else:
        current_frame = cmds.currentTime(query=True)
        FrameColorOverlay.instance.set_color("#8b0000", 0.4, frame=current_frame, auto_fade=auto_fade)


def mark_range(start_frame, end_frame, auto_fade=True):
    _ensure_overlay()
    FrameColorOverlay.instance.set_color("#8b0000", 0.3, frame_range=(start_frame, end_frame), auto_fade=auto_fade)


def trigger_fade(delay=0):
    if FrameColorOverlay.instance is not None:
        FrameColorOverlay.instance.trigger_fade(delay)


if __name__ == "__main__":
    mark_current_frame()
