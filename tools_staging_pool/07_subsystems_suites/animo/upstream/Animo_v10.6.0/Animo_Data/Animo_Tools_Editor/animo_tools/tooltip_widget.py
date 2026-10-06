from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

dpi_utils = compat.load_own_module(__file__, 'dpi_utils.py', 'animo_tools_editor_dpi_utils_via_tooltip')
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size
get_dpi_scale = dpi_utils.get_dpi_scale

class AnimoTooltip(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(AnimoTooltip, self).__init__(parent)
        
        self.setWindowFlags(
            QtCore.Qt.ToolTip |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        
        self._movie = None
        self._hide_timer = QtCore.QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_tooltip)
        self._hide_delay = 120
        self._trigger_button = None
        self._dpi_scale = get_dpi_scale()
        self._source_widget = None
        
        self._distance_check_timer = QtCore.QTimer(self)
        self._distance_check_timer.timeout.connect(self._check_mouse_distance)
        self._distance_check_timer.setInterval(50)
        
        self._setup_ui()
        self._apply_style()
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.applicationStateChanged.connect(self._on_app_state_changed)

    def _on_app_state_changed(self, state):
        if state != QtCore.Qt.ApplicationActive:
            self.hide_tooltip()

    def set_source_widget(self, widget):
        self._source_widget = widget
    
    def set_trigger_button(self, button):
        self._trigger_button = button
    
    def _check_mouse_distance(self):
        if not self.isVisible():
            self._distance_check_timer.stop()
            return
        
        self.raise_()
        
        cursor_pos = QtGui.QCursor.pos()
        tooltip_rect = self.geometry()
        
        margin = 25
        expanded_rect = tooltip_rect.adjusted(-margin, -margin, margin, margin)
        
        if self._source_widget:
            try:
                source_rect = QtCore.QRect(
                    self._source_widget.mapToGlobal(QtCore.QPoint(0, 0)),
                    self._source_widget.size()
                )
                expanded_rect = expanded_rect.united(source_rect.adjusted(-margin, -margin, margin, margin))
            except RuntimeError:
                pass
        
        if self._trigger_button:
            try:
                button_rect = QtCore.QRect(
                    self._trigger_button.mapToGlobal(QtCore.QPoint(0, 0)),
                    self._trigger_button.size()
                )
                expanded_rect = expanded_rect.united(button_rect.adjusted(-margin, -margin, margin, margin))
            except RuntimeError:
                pass
        
        if expanded_rect.contains(cursor_pos):
            self._hide_timer.stop()
        elif not self._hide_timer.isActive():
            self._hide_timer.start(self._hide_delay)

    def enterEvent(self, event):
        self._hide_timer.stop()
        super(AnimoTooltip, self).enterEvent(event)

    def leaveEvent(self, event):
        if not self._hide_timer.isActive():
            self._hide_timer.start(self._hide_delay)
        super(AnimoTooltip, self).leaveEvent(event)

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._max_content_width = scale_size(380)
        
        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("tooltipContainer")
        self.main_layout.addWidget(self.container)
        
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(
            scale_size(12), scale_size(10), scale_size(12), scale_size(10)
        )
        self.container_layout.setSpacing(0)
        
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(scale_size(10))
        
        icon_size = scale_size(28)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(icon_size, icon_size)
        self.icon_label.setObjectName("iconLabel")
        self.icon_label.hide()
        self.header_layout.addWidget(self.icon_label)
        
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumWidth(self._max_content_width)
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        self.shortcut_label = QtWidgets.QLabel()
        self.shortcut_label.setObjectName("shortcutLabel")
        self.header_layout.addWidget(self.shortcut_label)
        
        self.container_layout.addLayout(self.header_layout)
        
        self.separator1 = QtWidgets.QFrame()
        self.separator1.setFixedHeight(1)
        self.separator1.setObjectName("separator")
        self.container_layout.addWidget(self.separator1)
        
        self.description_label = QtWidgets.QLabel()
        self.description_label.setObjectName("descriptionLabel")
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumWidth(self._max_content_width)
        self.container_layout.addWidget(self.description_label)
        
        self.gif_label = QtWidgets.QLabel()
        self.gif_label.setObjectName("gifLabel")
        self.gif_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gif_label.hide()
        self.container_layout.addWidget(self.gif_label)
        
        self.info_frame = QtWidgets.QFrame()
        self.info_frame.setObjectName("infoFrame")
        self.info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(scale_size(2))
        self.container_layout.addWidget(self.info_frame)

    def _apply_style(self):
        title_font = scale_font_size(14)
        shortcut_font = scale_font_size(12)
        desc_font = scale_font_size(11)
        info_font = scale_font_size(11)
        border_radius = scale_size(5)
        top_padding = scale_size(6)
        
        style = """
            QFrame#tooltipContainer {{
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
            }}
            QLabel#iconLabel {{
                background: transparent;
            }}
            QLabel#titleLabel {{
                color: #4aa3df;
                font-size: {title_font}px;
                font-weight: bold;
                background: transparent;
            }}
            QLabel#shortcutLabel {{
                color: #888888;
                font-size: {shortcut_font}px;
                background: transparent;
            }}
            QLabel#descriptionLabel {{
                color: #b0b0b0;
                font-size: {desc_font}px;
                background: transparent;
                padding-top: {top_padding}px;
                padding-bottom: 2px;
            }}
            QFrame#separator {{
                background-color: #555555;
                border: none;
            }}
            QLabel#gifLabel {{
                background: transparent;
                padding-top: {top_padding}px;
            }}
            QFrame#infoFrame {{
                background: transparent;
            }}
        """.format(
            border_radius=border_radius,
            title_font=title_font,
            shortcut_font=shortcut_font,
            desc_font=desc_font,
            top_padding=top_padding
        )
        self.setStyleSheet(style)
        self._info_font_size = info_font

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def set_content(self, title="", description="", gif_path="", 
                    info_lines=None, shortcut="", icon_pixmap=None, gif_width=None):
        
        self.title_label.setText(title)
        self.title_label.setVisible(bool(title))
        
        self.shortcut_label.setText(shortcut)
        self.shortcut_label.setVisible(bool(shortcut))
        
        icon_size = scale_size(28)
        if icon_pixmap and not icon_pixmap.isNull():
            self.icon_label.setPixmap(icon_pixmap.scaled(
                icon_size, icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            ))
            self.icon_label.show()
        else:
            self.icon_label.hide()
        
        self.description_label.setText(description)
        self.description_label.setVisible(bool(description))
        
        self.separator1.setVisible(bool(title) and bool(description or gif_path or info_lines))
        
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        if gif_path and os.path.exists(gif_path):
            self._movie = QtGui.QMovie(gif_path)
            self._movie.setCacheMode(QtGui.QMovie.CacheAll)
            
            self._movie.jumpToFrame(0)
            native_size = self._movie.currentImage().size()
            native_width = native_size.width()
            native_height = native_size.height()
            
            if native_width > 0 and native_height > 0:
                target_width = int(gif_width) if gif_width else native_width
                target_width = min(target_width, self._max_content_width)
                target_height = int(round(native_height * (target_width / float(native_width))))
                
                self._movie.setScaledSize(QtCore.QSize(target_width, target_height))
                self.gif_label.setFixedSize(target_width, target_height)
            
            self.gif_label.setMovie(self._movie)
            self._movie.start()
            self.gif_label.show()
        else:
            self.gif_label.clear()
            self.gif_label.hide()
        
        self._clear_layout(self.info_layout)
        
        if info_lines:
            spacer = QtWidgets.QWidget()
            spacer.setFixedHeight(scale_size(8))
            self.info_layout.addWidget(spacer)
            for line in info_lines:
                info_label = QtWidgets.QLabel("• " + line)
                info_label.setWordWrap(True)
                info_label.setMaximumWidth(self._max_content_width)
                info_label.setStyleSheet(
                    "color: #909090; font-size: {0}px; background: transparent;".format(
                        self._info_font_size
                    )
                )
                self.info_layout.addWidget(info_label)
            self.info_frame.show()
        else:
            self.info_frame.hide()
        
        self.adjustSize()

    def show_at_widget(self, widget):
        widget_pos = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        
        screen = QtWidgets.QApplication.screenAt(widget_pos)
        if screen:
            screen_geo = screen.availableGeometry()
        else:
            screen_geo = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        x = widget_pos.x()
        y = widget_pos.y() + scale_size(5)
        
        if x + self.width() > screen_geo.right():
            x = screen_geo.right() - self.width() - scale_size(10)
        
        if y + self.height() > screen_geo.bottom():
            y = widget.mapToGlobal(QtCore.QPoint(0, 0)).y() - self.height() - scale_size(5)
        
        self.move(x, y)
        self.show()
        self.raise_()
        self._hide_timer.start(self._hide_delay)
        self._distance_check_timer.start()
    
    def show_at_cursor(self, offset_x=15, offset_y=15):
        cursor_pos = QtGui.QCursor.pos()
        
        screen = QtWidgets.QApplication.screenAt(cursor_pos)
        if screen:
            screen_geo = screen.availableGeometry()
        else:
            screen_geo = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        x = cursor_pos.x() + scale_size(offset_x)
        y = cursor_pos.y() + scale_size(offset_y)
        
        if x + self.width() > screen_geo.right():
            x = cursor_pos.x() - self.width() - scale_size(offset_x)
        
        if y + self.height() > screen_geo.bottom():
            y = cursor_pos.y() - self.height() - scale_size(offset_y)
        
        self.move(x, y)
        self.show()
        self.raise_()
        self._hide_timer.start(self._hide_delay)
        self._distance_check_timer.start()

    def hide_tooltip(self):
        self._hide_timer.stop()
        self._distance_check_timer.stop()
        if self._movie:
            self._movie.stop()
        self.hide()
        self.deleteLater()

