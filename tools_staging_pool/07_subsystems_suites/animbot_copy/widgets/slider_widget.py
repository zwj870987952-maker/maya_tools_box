"""
AnimBot signature multi-segment dot slider widget with spring-back mechanics.
Features:
- Dark rounded groove (#3C3C3C)
- Draggable center pill button with 2-letter compact abbreviation (e.g. 'TW', 'EA', 'MR', 'TO', 'CN')
- Stepped square dot buttons on both sides for direct percentage jumping
- Spring-back behavior: automatically returns to center default (0.0) upon mouse release
- Group color highlighting and mode context menus
- Dynamic tool switching synchronized with WorkspaceManager and Toolbar
- Conflict detection: disables modes that already exist on other active sliders (ghosted / unselectable)
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle
from .menu import AnimBotMenu

class AnimBotSlider(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(float)
    steppedTriggered = QtCore.Signal(float)
    modeChanged = QtCore.Signal(str)
    sliderToolSwitched = QtCore.Signal(str, str) # old_tool_id, new_tool_id

    def __init__(self, mode_label="TW", accent_color=AnimBotColors.YELLOW, min_val=-100.0, max_val=100.0, default_val=0.0, modes=None, tool_id=None, get_occupied_modes_func=None, parent=None):
        super().__init__(parent)
        self.tool_id = tool_id or "slider_tween"
        self.mode_abbr = mode_label[:2].upper()
        self.mode_label = mode_label
        self.accent_color = accent_color
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.default_val = default_val
        self.modes = modes or [] # List of dicts: [{"id":..., "abbr":..., "label":...}]
        self.get_occupied_modes_func = get_occupied_modes_func
        
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_val = 0.0
        
        self.setFixedSize(250, AnimBotStyle.SLIDER_HEIGHT)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Left dots (-100, -75, -50, -25) and Right dots (25, 50, 75, 100)
        self.left_steps = [-100.0, -75.0, -50.0, -25.0]
        self.right_steps = [25.0, 50.0, 75.0, 100.0]
        
        self.hovered_dot = None
        self.hovered_handle = False
        
        self.handle_width = 34
        self.handle_height = 24
        
        # Spring-back timer for smooth return to default position
        self.spring_timer = QtCore.QTimer(self)
        self.spring_timer.setInterval(16)  # ~60 fps
        self.spring_timer.timeout.connect(self._step_spring_back)

    def show_context_menu(self, global_pos):
        """Build and show context menu synchronized with workspace tools (ghosted if occupied)."""
        menu = AnimBotMenu(self.mode_label, self)
        
        occupied_tools = set()
        if callable(self.get_occupied_modes_func):
            occupied_tools = self.get_occupied_modes_func(self)
            
        for m in self.modes:
            m_id = m.get("id") if isinstance(m, dict) else str(m)
            m_abbr = m.get("abbr", m_id[:2].upper()) if isinstance(m, dict) else str(m)[:2].upper()
            m_label = m.get("label", m_id) if isinstance(m, dict) else str(m)
            
            is_self = (m_id == self.tool_id)
            is_occupied = (m_id in occupied_tools and not is_self)
            
            menu_text = f"{m_abbr}  {m_label}"
            act = menu.addAction(menu_text)
            
            if is_self:
                font = act.font()
                font.setBold(True)
                act.setFont(font)
            elif is_occupied:
                # Ghosted / dimmed in Qt, cannot be selected
                act.setEnabled(False)
                
            act.triggered.connect(lambda checked=False, tid=m_id, abbr=m_abbr, lbl=m_label: self._trigger_mode_switch(tid, abbr, lbl))
            
        menu.exec_(global_pos)

    def _trigger_mode_switch(self, new_tool_id, new_abbr, new_label):
        if new_tool_id == self.tool_id:
            return
        self.sliderToolSwitched.emit(self.tool_id, new_tool_id)

    def get_handle_rect(self):
        w = self.width()
        h = self.height()
        norm = (self.value - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0.5
        norm = max(0.0, min(1.0, norm))
        
        travel = w - self.handle_width - 10
        cx = 5 + norm * travel + self.handle_width / 2
        cy = h / 2
        
        return QtCore.QRectF(cx - self.handle_width / 2, cy - self.handle_height / 2, self.handle_width, self.handle_height)

    def get_dot_rects(self):
        w = self.width()
        h = self.height()
        left_area_w = (w - self.handle_width) / 2 - 12
        right_area_x = w / 2 + self.handle_width / 2 + 6
        
        dots = []
        for i, val in enumerate(self.left_steps):
            x = 10 + i * (left_area_w / len(self.left_steps)) + (left_area_w / len(self.left_steps)) / 2
            is_outer = (i == 0)
            dots.append((val, QtCore.QRectF(x - 5, h / 2 - 5, 10, 10), is_outer))
            
        for i, val in enumerate(self.right_steps):
            x = right_area_x + i * (left_area_w / len(self.right_steps)) + (left_area_w / len(self.right_steps)) / 2
            is_outer = (i == len(self.right_steps) - 1)
            dots.append((val, QtCore.QRectF(x - 5, h / 2 - 5, 10, 10), is_outer))
            
        return dots

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # 1. Background Groove (#3C3C3C)
        groove_rect = QtCore.QRectF(0, (h - 30) / 2, w, 30)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(AnimBotColors.BG_SLIDER_GROOVE))
        painter.drawRoundedRect(groove_rect, AnimBotStyle.SLIDER_RADIUS, AnimBotStyle.SLIDER_RADIUS)
        
        # 2. Draw Stepped Square Dots
        for val, rect, is_outer in self.get_dot_rects():
            dot_color = QtGui.QColor(self.accent_color)
            cx, cy = rect.center().x(), rect.center().y()
            
            if self.hovered_dot == val:
                painter.setBrush(dot_color)
                painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
                painter.drawRect(QtCore.QRectF(cx - 3.5, cy - 3.5, 7, 7))
            else:
                dot_size = 5.5 if is_outer else 3.5
                painter.setBrush(dot_color)
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawRect(QtCore.QRectF(cx - dot_size/2, cy - dot_size/2, dot_size, dot_size))

        # 3. Center Pill Handle
        handle_rect = self.get_handle_rect()
        is_active = self.hovered_handle or self.is_dragging
        
        handle_bg = QtGui.QColor("#222222" if is_active else "#2B2B2B")
        handle_border = QtGui.QColor(self.accent_color if is_active else "#555555")
        
        painter.setPen(QtGui.QPen(handle_border, 1.2))
        painter.setBrush(handle_bg)
        painter.drawRoundedRect(handle_rect, 6, 6)
        
        # Compact 2-letter abbreviation display (or int value during drag)
        painter.setPen(QtGui.QColor(self.accent_color if is_active else AnimBotColors.TEXT_MAIN))
        font = QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold)
        painter.setFont(font)
        
        display_text = f"{int(self.value)}" if self.is_dragging else self.mode_abbr
        painter.drawText(handle_rect, QtCore.Qt.AlignCenter, display_text)
        
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.spring_timer.stop()
            handle_rect = self.get_handle_rect()
            if handle_rect.contains(event.position()):
                self.is_dragging = True
                self.drag_start_x = event.position().x()
                self.drag_start_val = self.value
                self.update()
                return
                
            for val, rect, _ in self.get_dot_rects():
                if rect.adjusted(-4, -4, 4, 4).contains(event.position()):
                    self.set_value(val)
                    self.steppedTriggered.emit(val)
                    self.start_spring_back()
                    return
                    
            self.is_dragging = True
            self._update_val_from_mouse_x(event.position().x())
            self.update()

        elif event.button() == QtCore.Qt.RightButton:
            self.show_context_menu(self.mapToGlobal(event.pos()))

    def mouseMoveEvent(self, event):
        pos = event.position()
        if self.is_dragging:
            self._update_val_from_mouse_x(pos.x())
            self.update()
            return
            
        handle_rect = self.get_handle_rect()
        self.hovered_handle = handle_rect.contains(pos)
        
        old_hover = self.hovered_dot
        self.hovered_dot = None
        for val, rect, _ in self.get_dot_rects():
            if rect.adjusted(-4, -4, 4, 4).contains(pos):
                self.hovered_dot = val
                break
                
        if old_hover != self.hovered_dot or self.hovered_handle:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                self.start_spring_back()

    def leaveEvent(self, event):
        self.hovered_dot = None
        self.hovered_handle = False
        self.update()

    def _update_val_from_mouse_x(self, mouse_x):
        w = self.width()
        travel = w - self.handle_width - 10
        norm = (mouse_x - 5 - self.handle_width / 2) / travel
        norm = max(0.0, min(1.0, norm))
        new_val = self.min_val + norm * (self.max_val - self.min_val)
        self.set_value(new_val)

    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.valueChanged.emit(self.value)
        self.setToolTip(f"{self.mode_label}: {self.value:.1f}%")
        self.update()

    def start_spring_back(self):
        """Initiate spring back animation towards default_val."""
        self.spring_timer.start()

    def _step_spring_back(self):
        """Interpolate smoothly towards default center (0.0)."""
        diff = self.default_val - self.value
        if abs(diff) < 2.0:
            self.value = self.default_val
            self.spring_timer.stop()
            self.update()
        else:
            self.value += diff * 0.45
            self.update()
