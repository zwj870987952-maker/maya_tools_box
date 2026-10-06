try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

from . import styleMod as style


class AnimoSlider(QtWidgets.QSlider):
    
    statusChanged = QtCore.Signal(str)
    
    def __init__(self, label="TW", handle_color=(80, 200, 120), slider_type="tween", parent=None):
        super(AnimoSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        
        self.label_text = label
        self.original_label = label
        self.handle_color = QtGui.QColor(*handle_color)
        self.icon_color = QtGui.QColor(*handle_color)
        self.slider_type = slider_type
        
        self.mouse_pressed = False
        self.last_update_time = 0
        self.update_throttle_ms = 1
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.needs_cursor_restore = False
        
        self._slider_modules = None
        
        self.setMinimumHeight(style.scaled(21))
        self.setMaximumHeight(style.scaled(21))
        self.setMinimumWidth(style.scaled(200))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.valueChanged.connect(self._onValueChanged)
        
        if self.slider_type == "scale":
            QtWidgets.QApplication.instance().installEventFilter(self)
    
    def set_slider_modules(self, tween_mod, blend_mod, scale_mod, cascade_mod, utils_mod):
        self._slider_modules = {
            'tween': tween_mod,
            'blend': blend_mod,
            'scale': scale_mod,
            'cascade': cascade_mod,
            'utils': utils_mod
        }
    
    def setLabel(self, label):
        self.label_text = label
        self.update()
    
    def eventFilter(self, obj, event):
        if self.slider_type == "scale":
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Shift:
                    self.shift_pressed = True
                    self._updateScaleLabel()
                elif event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = True
                    self._updateScaleLabel()
            elif event.type() == QtCore.QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Shift:
                    self.shift_pressed = False
                    self._updateScaleLabel()
                elif event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = False
                    self._updateScaleLabel()
        return False
    
    def _updateScaleLabel(self):
        if self.slider_type == "scale":
            if self.ctrl_pressed:
                self.setLabel("SA")
            elif self.shift_pressed:
                self.setLabel("SR")
            else:
                self.setLabel("SL")
    
    def _onValueChanged(self, value):
        if not self.mouse_pressed or not self._slider_modules:
            return
        
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
        self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
        
        if self.slider_type == "tween":
            self.last_update_time, status = self._slider_modules['tween'].slider_logic(
                value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_type == "blend":
            self.last_update_time, status = self._slider_modules['blend'].slider_logic(
                value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_type == "scale":
            self._updateScaleLabel()
            if self.ctrl_pressed:
                self.last_update_time, status = self._slider_modules['scale'].scale_avg_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            elif self.shift_pressed:
                self.last_update_time, status = self._slider_modules['scale'].scale_right_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            else:
                self.last_update_time, status = self._slider_modules['scale'].scale_left_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_type == "cascade":
            self.last_update_time, status = self._slider_modules['cascade'].slider_logic(
                value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        icon_size = style.scaled(6)
        num_dots = 7
        total_items = num_dots + 2
        
        margin = style.scaled(8)
        available_width = rect.width() - (2 * margin)
        item_spacing = available_width / (total_items - 1)
        
        icon_left = margin
        icon_y = rect.height() // 2 - icon_size // 2
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_left, icon_y, icon_size, icon_size, 1, 1)
        
        track_start = margin + item_spacing
        track_end = rect.width() - margin - item_spacing
        track_y = rect.height() // 2
        
        dot_color = QtGui.QColor(self.handle_color)
        dot_color.setAlpha(220)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        
        dot_spacing = (track_end - track_start) / (num_dots - 1)
        dot_radius = style.scaled(2.15)
        
        for i in range(num_dots):
            dot_x = track_start + i * dot_spacing
            painter.drawEllipse(QtCore.QPointF(dot_x, track_y), dot_radius, dot_radius)
        
        min_val = self.minimum()
        max_val = self.maximum()
        curr_val = self.value()
        
        if max_val != min_val:
            normalized = float(curr_val - min_val) / float(max_val - min_val)
        else:
            normalized = 0.5
            
        handle_x = track_start + normalized * (track_end - track_start)
        handle_y = track_y
        
        handle_size = style.scaled(22)
        handle_rect = QtCore.QRectF(
            handle_x - handle_size / 2,
            handle_y - handle_size / 2,
            handle_size,
            handle_size
        )
        
        painter.setBrush(self.handle_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(handle_rect, 3, 3)
        
        painter.setPen(QtGui.QColor(40, 40, 40))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(handle_rect, QtCore.Qt.AlignCenter, self.label_text)
        
        icon_right = rect.width() - margin - icon_size
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_right, icon_y, icon_size, icon_size, 1, 1)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            
            icon_size = style.scaled(6)
            margin = style.scaled(8)
            icon_y = rect.height() // 2 - icon_size // 2
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - (2 * margin)
            item_spacing = available_width / (total_items - 1)
            track_start = margin + item_spacing
            track_end = rect.width() - margin - item_spacing
            
            left_icon_rect = QtCore.QRect(margin, icon_y, icon_size, icon_size)
            
            icon_right = rect.width() - margin - icon_size
            right_icon_rect = QtCore.QRect(icon_right, icon_y, icon_size, icon_size)
            
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
            self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
            
            if self._slider_modules:
                getCurves = self._slider_modules['utils'].get_anim_curves()
                anim_curves = getCurves[0]
                if anim_curves and len(anim_curves) > 400:
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.needs_cursor_restore = True
                else:
                    self.needs_cursor_restore = False
            
            self.mouse_pressed = True
            self._updateScaleLabel()
            
            release_delay = 100 if self._slider_modules and self._slider_modules['utils'].IS_MACOS else 50
            
            if left_icon_rect.contains(click_pos):
                self.setValue(self.minimum())
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            elif right_icon_rect.contains(click_pos):
                self.setValue(self.maximum())
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            else:
                normalized = (click_pos.x() - track_start) / (track_end - track_start)
                normalized = max(0.0, min(1.0, normalized))
                new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
                self.setValue(int(new_value))

    def mouseMoveEvent(self, event):
        if self.mouse_pressed and event.buttons() & QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            margin = style.scaled(8)
            icon_size = style.scaled(6)
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - (2 * margin)
            item_spacing = available_width / (total_items - 1)
            
            track_start = margin + item_spacing
            track_end = rect.width() - margin - item_spacing
            
            normalized = (click_pos.x() - track_start) / (track_end - track_start)
            normalized = max(0.0, min(1.0, normalized))
            
            new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
            self.setValue(int(new_value))
            
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
            self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
            self._updateScaleLabel()
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.mouse_pressed:
            release_delay = 100 if self._slider_modules and self._slider_modules['utils'].IS_MACOS else 50
            QtCore.QTimer.singleShot(release_delay, self._onRelease)
    
    def contextMenuEvent(self, event):
        if self.slider_type == "scale":
            QtWidgets.QToolTip.showText(
                event.globalPos(),
                "Scale Left\n"
                "Hold Shift — Scale Right\n"
                "Hold Ctrl — Scale Average",
                self
            )
        else:
            super(AnimoSlider, self).contextMenuEvent(event)
    
    def _onRelease(self):
        self.mouse_pressed = False
        
        if self._slider_modules:
            if self.slider_type == "tween":
                self._slider_modules['tween'].reset_slider(self)
            elif self.slider_type == "blend":
                self._slider_modules['blend'].reset_slider(self)
            elif self.slider_type == "scale":
                self._slider_modules['scale'].reset_slider(self)
                self.setLabel(self.original_label)
            elif self.slider_type == "cascade":
                self._slider_modules['cascade'].reset_slider(self)
        
        self.statusChanged.emit("")
        
        if self.needs_cursor_restore:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.needs_cursor_restore = False
