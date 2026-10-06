from __future__ import print_function, division, absolute_import

import os
import platform
import maya.cmds as cmds

from spacify_core import (
    QtWidgets, QtCore, QtGui, 
    spacify_data_path, get_maya_main_window, SPACIFY_STATE, reload
)
from spacify_styles import get_tab_style
from tab_spaces import create_spaces_tab
from tab_offset import create_animation_tab
from dpi_scale import dpi, reset_scale_factor, get_screen_for_widget, get_scale_factor_for_screen, set_scale_factor
import spacify_actions as actions


class SpacifyUI(QtWidgets.QDialog):
    option_var_name = "SpacifyUI_lastPos"
    option_var_tab = "SpacifyUI_lastTab"
    option_var_auto_collapse = "SpacifyUI_autoCollapse"
    
    # Base width (at 100% / 96 DPI)
    BASE_WIDTH = 282

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(SpacifyUI, self).__init__(parent)
        self.setObjectName("SpacifyUIWindow")
        
        if platform.system() == 'Darwin':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        self.is_collapsed = False
        self.auto_collapse_enabled = False
        self._collapse_timer = QtCore.QTimer()
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.timeout.connect(self._delayed_collapse)
        
        # Screen change detection - store the scale factor we're building with RIGHT NOW
        from dpi_scale import get_scale_factor
        self._built_with_scale = get_scale_factor()
        self._current_screen = None
        self._screen_check_timer = QtCore.QTimer()
        self._screen_check_timer.setSingleShot(True)
        self._screen_check_timer.timeout.connect(self._check_screen_change)
        self._is_reopening = False
        
        if cmds.optionVar(exists=self.option_var_auto_collapse):
            self.auto_collapse_enabled = bool(cmds.optionVar(q=self.option_var_auto_collapse))
        
        self.load_modules()
        self.build_ui()
        self.apply_theme()
        
        # Set fixed width, let height adjust to content
        self.setFixedWidth(dpi(self.BASE_WIDTH))
        self.adjustSize()
        self._full_height = self.height()
        self._collapsed_height = dpi(54)
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        if cmds.optionVar(exists=self.option_var_name):
            pos_str = cmds.optionVar(q=self.option_var_name)
            try:
                x, y = [int(v) for v in pos_str.split(",")]
                self.move(x, y)
            except Exception:
                pass
        
        self.fade_to(0.87)
        self.apply_rounded_corners()
        
        # Store initial screen after window is positioned
        QtCore.QTimer.singleShot(100, self._store_initial_screen)

    def closeEvent(self, event):
        pos = self.pos()
        pos_str = "{0},{1}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        cmds.optionVar(iv=(self.option_var_auto_collapse, int(self.auto_collapse_enabled)))
        
        if hasattr(self, '_script_jobs'):
            for job_id in self._script_jobs:
                try:
                    if cmds.scriptJob(exists=job_id):
                        cmds.scriptJob(kill=job_id, force=True)
                except:
                    pass
        
        super(SpacifyUI, self).closeEvent(event)

    def load_modules(self):
        # Modules are already loaded by Spacify.py/spacify_launcher.py
        # Just get references from sys.modules
        pass

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(18))
        main_layout.setSpacing(0)

        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(dpi(9))
        
        title_bar.addStretch()
        
        icon_button = QtWidgets.QPushButton()
        icon_button.setFixedSize(dpi(30), dpi(30))
        
        icon_path = os.path.join(spacify_data_path, "spacify_icon.png") if spacify_data_path else ""
        if icon_path and os.path.exists(icon_path):
            icon_button.setIcon(QtGui.QIcon(icon_path))
            icon_button.setIconSize(QtCore.QSize(dpi(24), dpi(24)))
            icon_button.setStyleSheet("""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {0}px;
                }}
                QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.1); }}
                QPushButton:pressed {{ background-color: rgba(255, 255, 255, 0.2); }}
            """.format(dpi(15)))
        else:
            icon_button.setText("S")
            icon_button.setStyleSheet("""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {0}px;
                    color: white;
                    font-weight: bold;
                    font-size: 14pt;
                }}
            """.format(dpi(15)))
            icon_button.setEnabled(False)
        
        title_bar.addWidget(icon_button)
        
        title_label = QtWidgets.QLabel("SPACIFY")
        title_label.setStyleSheet("font-weight: bold; font-size: 13pt; color: white;")
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()

        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(dpi(30), dpi(30))
        
        exit_icon_path = os.path.join(spacify_data_path, "exit.png") if spacify_data_path else ""
        if exit_icon_path and os.path.exists(exit_icon_path):
            close_button.setIcon(QtGui.QIcon(exit_icon_path))
            close_button.setIconSize(QtCore.QSize(dpi(20), dpi(20)))
            close_button.setStyleSheet("""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {0}px;
                }}
                QPushButton:hover {{ background-color: #333333; }}
                QPushButton:pressed {{ background-color: #222222; }}
            """.format(dpi(15)))
        else:
            close_button.setText("×")
            close_button.setStyleSheet("""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {0}px;
                    color: white;
                    font-size: 20pt;
                }}
                QPushButton:hover {{ background-color: rgba(231, 76, 60, 0.8); }}
                QPushButton:pressed {{ background-color: rgba(192, 57, 43, 1.0); }}
            """.format(dpi(15)))
        
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        main_layout.addLayout(title_bar)

        self.content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, dpi(18), 0, 0)
        content_layout.setSpacing(0)
        
        self._build_tabs(content_layout)
        
        main_layout.addWidget(self.content_widget)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
        # Check for screen change after drag ends
        self._screen_check_timer.start(200)
    
    def _store_initial_screen(self):
        """Store the initial screen the window is on."""
        screen = get_screen_for_widget(self)
        if screen:
            self._current_screen = screen.name()
    
    def _check_screen_change(self):
        """Check if window moved to a different screen with different DPI."""
        if self._is_reopening:
            return
        
        # Cooldown - don't check if we just reopened
        import time
        current_time = time.time()
        last_reopen = getattr(self, '_last_reopen_time', 0)
        if current_time - last_reopen < 2.0:  # 2 second cooldown
            return
        
        new_screen = get_screen_for_widget(self)
        if not new_screen:
            return
        
        new_screen_name = new_screen.name()
        new_scale = get_scale_factor_for_screen(new_screen)
        
        # If we haven't stored initial screen yet, just store it now
        if self._current_screen is None:
            self._current_screen = new_screen_name
            return
        
        # Screen didn't change, nothing to do
        if new_screen_name == self._current_screen:
            return
        
        # Screen changed - check if DPI is different from what we built with
        # Only reopen if DPI is actually different
        if abs(self._built_with_scale - new_scale) > 0.01:
            self._last_reopen_time = current_time
            self._reopen_for_new_screen(new_screen)
        else:
            # Same DPI, just update screen name
            self._current_screen = new_screen_name
    
    def _reopen_for_new_screen(self, new_screen):
        """Close and reopen the UI for the new screen's DPI."""
        self._is_reopening = True
        
        # Save current position
        pos = self.pos()
        pos_str = "{0},{1}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        
        # Reset DPI scale factor and set to new screen's DPI
        new_scale = get_scale_factor_for_screen(new_screen)
        reset_scale_factor()
        set_scale_factor(new_scale)
        
        # Close current window
        self.close()
        
        # Reopen with new DPI - use deferred to let close complete
        cmds.evalDeferred(reopen_spacify_ui)
    
    def toggle_collapse(self):
        if self.is_collapsed:
            self.expand_ui()
        else:
            self.collapse_ui()
    
    def expand_ui(self):
        if not self.is_collapsed:
            return
        self.is_collapsed = False
        self.content_widget.show()
        self.setFixedWidth(dpi(self.BASE_WIDTH))
        self.setFixedHeight(self._full_height)
        self.apply_rounded_corners()
    
    def collapse_ui(self):
        if self.is_collapsed:
            return
        self.is_collapsed = True
        self.content_widget.hide()
        self.setFixedWidth(dpi(self.BASE_WIDTH))
        self.setFixedHeight(self._collapsed_height)
        self.apply_rounded_corners()
    
    def enterEvent(self, event):
        self._collapse_timer.stop()
        if self.auto_collapse_enabled and self.is_collapsed:
            self.expand_ui()
        self.fade_to(0.87, 50, QtCore.QEasingCurve.OutQuad)
        super(SpacifyUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        if self.auto_collapse_enabled and not self.is_collapsed:
            self._collapse_timer.start(4000)
        self.fade_to(0.55, 300)
        super(SpacifyUI, self).leaveEvent(event)
    
    def _delayed_collapse(self):
        if self.auto_collapse_enabled and not self.is_collapsed:
            popup_open = False
            for combo in self.findChildren(QtWidgets.QComboBox):
                if combo.view().isVisible():
                    popup_open = True
                    break
            
            if not popup_open:
                self.collapse_ui()
            else:
                self._collapse_timer.start(4000)
    
    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                color: white;
                padding: 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #C94A47;
            }
        """)
        
        auto_collapse_action = menu.addAction("Auto Collapse")
        auto_collapse_action.setCheckable(True)
        auto_collapse_action.setChecked(self.auto_collapse_enabled)
        auto_collapse_action.triggered.connect(self.toggle_auto_collapse)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def toggle_auto_collapse(self, checked):
        self.auto_collapse_enabled = checked
        cmds.optionVar(iv=(self.option_var_auto_collapse, int(checked)))
        
        # If disabling auto-collapse while collapsed, expand the UI
        if not checked and self.is_collapsed:
            self.expand_ui()

    def _build_tabs(self, content_layout):
        tab_nav_container = QtWidgets.QWidget()
        tab_nav_layout = QtWidgets.QVBoxLayout(tab_nav_container)
        tab_nav_layout.setContentsMargins(0, 0, 0, 0)
        tab_nav_layout.setSpacing(dpi(3))
        
        tab_row1 = QtWidgets.QHBoxLayout()
        tab_row1.setSpacing(dpi(3))
        
        self.tab_buttons = []
        self.tab_names_row1 = ["Spaces", "Offset"]
        for i, name in enumerate(self.tab_names_row1):
            btn = QtWidgets.QPushButton(name)
            btn.setMinimumHeight(dpi(24))
            btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            btn.setStyleSheet(get_tab_style(False))
            btn.clicked.connect(lambda checked=False, idx=i: self.switch_tab(idx))
            tab_row1.addWidget(btn)
            self.tab_buttons.append(btn)
        
        tab_nav_layout.addLayout(tab_row1)
        content_layout.addWidget(tab_nav_container)
        
        content_layout.addSpacing(dpi(8))
        
        self.tab_stack = QtWidgets.QStackedWidget()
        self.tab_stack.addWidget(create_spaces_tab(self))
        self.tab_stack.addWidget(create_animation_tab(self))
        
        content_layout.addWidget(self.tab_stack)
        
        last_tab = 0
        if cmds.optionVar(exists=self.option_var_tab):
            last_tab = cmds.optionVar(q=self.option_var_tab)
            if last_tab < 0 or last_tab >= len(self.tab_buttons):
                last_tab = 0
        self.switch_tab(last_tab)

    def switch_tab(self, index):
        self.tab_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setStyleSheet(get_tab_style(i == index, i))
        # Save last tab
        cmds.optionVar(iv=(self.option_var_tab, index))

    def execute_world(self):
        actions.execute_world()

    def execute_new_pivot(self):
        actions.execute_new_pivot()

    def execute_relative(self):
        actions.execute_relative()

    def execute_group(self):
        actions.execute_group()

    def execute_aim(self):
        actions.execute_aim()

    def execute_fk(self):
        actions.execute_fk()

    def execute_world_orient(self):
        actions.execute_world_orient()

    def execute_temp_ik(self):
        actions.execute_temp_ik()

    def assign_camera(self):
        actions.assign_camera(self.camera_field)

    def create_camera_space(self):
        actions.create_camera_space()

    def set_offset_value(self, value):
        actions.set_offset_value(value)

    def apply_shift(self):
        actions.apply_shift()

    def execute_sequential_offset(self):
        offset_value = self.overlap_spinbox.value()
        actions.execute_sequential_offset(offset_value)

    def clean_and_bake_wrapper(self):
        actions.clean_and_bake_wrapper()

    def pick_color(self):
        actions.pick_color(self.color_button)

    def hue_changed(self, value):
        actions.hue_changed(value, self.color_button)

    def scale_changed(self, value):
        actions.scale_changed(value, self.scale_label)

    def scale_released(self):
        actions.scale_released(self.scale_slider, self.scale_label)

    def set_scale_preset(self, value):
        actions.set_scale_preset(value, self.scale_slider, self.scale_label)

    # Xform tab methods
    def execute_copy_xform(self):
        actions.execute_copy_xform()

    def execute_copy_xform_range(self):
        actions.execute_copy_xform_range()

    def execute_paste_xform(self):
        actions.execute_paste_xform()

    def execute_copy_xform_relationship(self):
        actions.execute_copy_xform_relationship()

    def execute_paste_xform_relationship(self):
        actions.execute_paste_xform_relationship()

    def execute_bake_xform_relationship(self):
        actions.execute_bake_xform_relationship()

    # Align methods
    def execute_align_translate(self):
        actions.execute_align_translate()

    def execute_align_rotate(self):
        actions.execute_align_rotate()

    def execute_align(self):
        actions.execute_align()

    def execute_align_range_translate(self):
        actions.execute_align_range_translate()

    def execute_align_range_rotate(self):
        actions.execute_align_range_rotate()

    def execute_align_range(self):
        actions.execute_align_range()

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                color: white;
                border-radius: 14px;
            }
        """)

    def apply_rounded_corners(self):
        radius = 14
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super(SpacifyUI, self).resizeEvent(event)
        self.apply_rounded_corners()

    def fade_to(self, target_opacity, duration=300, easing=None):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        if easing is None:
            self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        else:
            self.anim.setEasingCurve(easing)
        self.anim.start()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        current_index = self.tab_stack.currentIndex()
        
        if delta > 0:
            if current_index > 0:
                self.switch_tab(current_index - 1)
        elif delta < 0:
            if current_index < self.tab_stack.count() - 1:
                self.switch_tab(current_index + 1)


def reopen_spacify_ui():
    """Reopen the Spacify UI (called after screen change)."""
    # Import here to avoid circular imports
    import Spacify
    Spacify.show_ui()
