from maya import mel
from maya import cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance
    PYSIDE_VERSION = 2


MARK_COLOR = "#8b0000"
MARK_OPACITY = 0.35
OVERLAY_OBJECT_NAME = "AnimoKeysTangentFrameOverlay"


def maya_to_qt(name, type_=QtWidgets.QWidget):
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        return wrapInstance(int(ptr), type_)
    raise RuntimeError("Failed to obtain a handle to '{}'.".format(name))


def _get_main_window():
    try:
        main_ptr = OpenMayaUI.MQtUtil.mainWindow()
        if not main_ptr:
            return None
        return wrapInstance(int(main_ptr), QtWidgets.QWidget)
    except (AttributeError, RuntimeError, TypeError):
        return None


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


def _widget_is_alive(widget):
    if widget is None:
        return False
    try:
        widget.objectName()
        return True
    except RuntimeError:
        return False


_OVERLAY_REF_ATTR = "_animo_keys_tangent_frame_overlay"


def _get_overlay_instance():
    return getattr(cmds, _OVERLAY_REF_ATTR, None)


def _set_overlay_instance(widget):
    setattr(cmds, _OVERLAY_REF_ATTR, widget)


class FrameColorOverlay(QtWidgets.QWidget):

    def __init__(self, parent):
        super(FrameColorOverlay, self).__init__(parent)

        self.setObjectName(OVERLAY_OBJECT_NAME)

        self._base = None
        self._transient = None
        self._fade_step_amount = 0.015

        self._fade_delay_timer = QtCore.QTimer(self)
        self._fade_delay_timer.setSingleShot(True)
        self._fade_delay_timer.timeout.connect(self._start_fade)

        self._fade_timer = QtCore.QTimer(self)
        self._fade_timer.setInterval(30)
        self._fade_timer.timeout.connect(self._fade_step)

        try:
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        except AttributeError:
            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        if parent:
            parent.installEventFilter(self)
            self.setGeometry(0, 0, parent.width(), parent.height())

        self.show()
        self.raise_()

    def eventFilter(self, obj, event):
        try:
            resize_event = QtCore.QEvent.Type.Resize
        except AttributeError:
            resize_event = QtCore.QEvent.Resize

        if obj == self.parent() and event.type() == resize_event:
            self.setGeometry(0, 0, obj.width(), obj.height())
        return False

    def set_layer(self, layer, color, opacity, frame=None, frame_range=None, auto_fade=True):
        parent = self.parent()
        if parent:
            self.setGeometry(0, 0, parent.width(), parent.height())

        state = {
            "color": QtGui.QColor(color),
            "opacity": opacity,
            "frame": frame,
            "frame_range": frame_range,
        }

        self._fade_delay_timer.stop()
        self._fade_timer.stop()

        if layer == "base":
            self._transient = None
            self._base = state
        else:
            self._transient = state

        self.show()
        self.raise_()
        self.update()

        if layer != "base" and auto_fade:
            self._fade_delay_timer.start(1000)

    def trigger_fade(self, delay=0):
        if self._transient is None:
            return
        self._fade_delay_timer.stop()
        self._fade_timer.stop()
        if delay > 0:
            self._fade_delay_timer.start(delay)
        else:
            self._start_fade()

    def _start_fade(self):
        if self._transient is None:
            return
        self._fade_timer.start()

    def _fade_step(self):
        if self._transient is None:
            self._fade_timer.stop()
            return
        self._transient["opacity"] -= self._fade_step_amount
        if self._transient["opacity"] <= 0:
            self._transient = None
            self._fade_timer.stop()
        self.update()

    def clear_all(self):
        self._fade_delay_timer.stop()
        self._fade_timer.stop()
        self._base = None
        self._transient = None
        self.update()

    def _paint_layer(self, painter, state, total, step, start):
        color = QtGui.QColor(state["color"])
        color.setAlphaF(max(0.0, min(1.0, state["opacity"])))

        frame_range = state["frame_range"]
        frame = state["frame"]

        if frame_range is not None:
            range_start, range_end = frame_range
            pos_start = (range_start - start) * step + (total * 0.005)
            pos_end = (range_end - start + 1) * step + (total * 0.005)
            rect = QtCore.QRectF(pos_start, 0, pos_end - pos_start, self.height())
            painter.fillRect(rect, color)
        elif frame is not None:
            pos = (frame - start + 0.5) * step + (total * 0.005)
            pen = QtGui.QPen(color)
            pen.setWidthF(max(step, 3))
            painter.setPen(pen)
            line = QtCore.QLineF(QtCore.QPointF(pos, 0), QtCore.QPointF(pos, self.height()))
            painter.drawLine(line)

    def paintEvent(self, event):
        if self._base is None and self._transient is None:
            return

        painter = QtGui.QPainter(self)
        try:
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        except AttributeError:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        total = self.width()
        step = (total - (total * 0.01)) / (end - start + 1)

        if self._base is not None:
            self._paint_layer(painter, self._base, total, step, start)

        if self._transient is not None:
            self._paint_layer(painter, self._transient, total, step, start)

        painter.end()


def _find_stray_overlays(parent, keep=None):
    strays = []
    search_root = _get_main_window() or parent
    if search_root is None:
        return strays
    try:
        for child in search_root.findChildren(QtWidgets.QWidget, OVERLAY_OBJECT_NAME):
            if child is not keep:
                strays.append(child)
    except RuntimeError:
        pass
    return strays


def _destroy_stray_overlays(parent, keep=None):
    for stray in _find_stray_overlays(parent, keep=keep):
        try:
            stray._fade_delay_timer.stop()
            stray._fade_timer.stop()
        except Exception:
            pass
        try:
            stray.hide()
            stray.setParent(None)
            stray.deleteLater()
        except Exception:
            pass


def _ensure_overlay():
    parent = get_timeline()

    overlay = _get_overlay_instance()

    if overlay is not None:
        if not _widget_is_alive(overlay):
            overlay = None
        elif overlay.parent() is not parent:
            overlay = None

    if overlay is None:
        overlay = FrameColorOverlay(parent)

    _set_overlay_instance(overlay)

    _destroy_stray_overlays(parent, keep=overlay)

    return overlay


def _with_recovery(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError:
            _set_overlay_instance(None)
            try:
                return func(*args, **kwargs)
            except RuntimeError:
                return None
    return wrapper


@_with_recovery
def mark_current_frame(auto_fade=True, color=None, opacity=None, layer="transient"):
    overlay = _ensure_overlay()

    use_color = color if color else MARK_COLOR
    use_opacity = opacity if opacity else MARK_OPACITY

    selected_range = get_selected_range()
    if selected_range:
        overlay.set_layer(layer, use_color, use_opacity, frame_range=selected_range, auto_fade=auto_fade)
    else:
        current_frame = cmds.currentTime(query=True)
        overlay.set_layer(layer, use_color, use_opacity, frame=current_frame, auto_fade=auto_fade)


@_with_recovery
def mark_range(start_frame, end_frame, auto_fade=True, color=None, opacity=None, layer="transient"):
    overlay = _ensure_overlay()

    use_color = color if color else MARK_COLOR
    use_opacity = opacity if opacity else MARK_OPACITY

    overlay.set_layer(layer, use_color, use_opacity, frame_range=(start_frame, end_frame), auto_fade=auto_fade)


@_with_recovery
def trigger_fade(delay=0, fast=False):
    overlay = _get_overlay_instance()
    if overlay is None:
        return
    if not _widget_is_alive(overlay):
        _set_overlay_instance(None)
        return
    if fast:
        overlay._fade_timer.setInterval(15)
        overlay._fade_step_amount = 0.04
    else:
        overlay._fade_timer.setInterval(30)
        overlay._fade_step_amount = 0.015
    overlay.trigger_fade(delay)


@_with_recovery
def clear_all():
    overlay = _ensure_overlay()
    overlay.clear_all()


if __name__ == "__main__":
    mark_current_frame()