"""
AnimBot drag grip handle widget.
Displays subtle double-column dot grip indicator at the far left of the toolbar.
Allows dragging to move or undock the toolbar.
"""

from PySide6 import QtWidgets, QtCore, QtGui

class AnimBotDragGrip(QtWidgets.QWidget):
    dragRequested = QtCore.Signal(QtCore.QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnimBotDragGrip")
        self.setFixedSize(14, 28)
        self.setCursor(QtCore.Qt.SizeAllCursor)
        self.setToolTip("拖拽移动 / 悬浮工具栏 (Drag to move or float toolbar)")
        self.setMouseTracking(True)
        
        self._is_dragging = False
        self._drag_start_pos = QtCore.QPoint()
        self._hovered = False

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        dot_color = QtGui.QColor("#AAAAAA" if self._hovered else "#5A5A5A")
        painter.setBrush(dot_color)
        painter.setPen(QtCore.Qt.NoPen)
        
        # 2 columns x 4 rows of grip dots
        start_x = 4.0
        spacing_x = 4.0
        start_y = 5.0
        spacing_y = 5.0
        dot_size = 2.2
        
        for col in range(2):
            x = start_x + col * spacing_x
            for row in range(4):
                y = start_y + row * spacing_y
                painter.drawEllipse(QtCore.QRectF(x, y, dot_size, dot_size))
                
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            delta = event.globalPosition().toPoint() - self._drag_start_pos
            if delta.manhattanLength() > 10:
                self.dragRequested.emit(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._is_dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)
