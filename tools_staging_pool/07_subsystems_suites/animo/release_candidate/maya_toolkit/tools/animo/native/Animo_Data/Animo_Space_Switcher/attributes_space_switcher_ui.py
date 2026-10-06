from __future__ import print_function, division, absolute_import

import os
import sys
import platform
import maya.cmds as cmds
from functools import partial

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

# Add Spacify directory to path for dpi_scale
spacify_dir = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher")
if spacify_dir not in sys.path:
    sys.path.insert(0, spacify_dir)

from dpi_scale import (
    dpi, 
    reset_scale_factor, 
    get_screen_for_widget, 
    get_scale_factor_for_screen, 
    set_scale_factor,
    get_scale_factor
)
import AttributeSpaceSwitcher


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class AttributesSpaceSwitcherUI(QtWidgets.QDialog):
    option_var_name = "AttributesSpaceSwitcherUI_lastPos"
    
    # Base width (at 100% / 96 DPI)
    BASE_WIDTH = 282

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(AttributesSpaceSwitcherUI, self).__init__(parent)
        self.setObjectName("AttributesSpaceSwitcherUIWindow")
        
        if platform.system() == 'Darwin':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        
        # Screen change detection - store scale factor BEFORE building UI
        self._built_with_scale = get_scale_factor()
        self._current_screen = None
        self._screen_check_timer = QtCore.QTimer()
        self._screen_check_timer.setSingleShot(True)
        self._screen_check_timer.timeout.connect(self._check_screen_change)
        self._is_reopening = False
        
        self.build_ui()
        self.apply_theme()
        
        # Set fixed width, let height adjust to content
        self.setFixedWidth(dpi(self.BASE_WIDTH))
        self.adjustSize()
        
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
        
        if hasattr(self, '_script_jobs'):
            for job_id in self._script_jobs:
                try:
                    if cmds.scriptJob(exists=job_id):
                        cmds.scriptJob(kill=job_id, force=True)
                except:
                    pass
        
        super(AttributesSpaceSwitcherUI, self).closeEvent(event)

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(18))
        main_layout.setSpacing(0)

        # Title bar
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(dpi(9))
        
        title_bar.addStretch()
        
        title_label = QtWidgets.QLabel("ATTRIBUTES SPACE SWITCHER")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10pt;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        # Close button
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #C94A47;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)
        
        main_layout.addLayout(title_bar)
        
        # Content
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, dpi(18), 0, 0)
        content_layout.setSpacing(dpi(6))
        
        self._build_content(content_layout)
        
        main_layout.addWidget(content_widget)

    def _build_content(self, layout):
        # ============ GROUP 1: Rotate Order ============

        self.ro_label = QtWidgets.QLabel("Select an Object!")
        self.ro_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ro_label.setMinimumHeight(dpi(32))
        self.ro_label.setStyleSheet("""
            QLabel {{
                background-color: #2A2A2A;
                color: white;
                font-weight: 700;
                padding: {0}px;
                border-radius: 6px;
                font-size: 8pt;
            }}
        """.format(dpi(7)))
        layout.addWidget(self.ro_label)

        layout.addSpacing(dpi(6))

        self.ro_buttons = {}

        ro_container1 = QtWidgets.QWidget()
        ro_layout1 = QtWidgets.QHBoxLayout(ro_container1)
        ro_layout1.setContentsMargins(0, 0, 0, 0)
        ro_layout1.setSpacing(dpi(6))

        for label in ["XYZ", "YZX", "ZXY"]:
            btn = self._create_ro_button(label)
            self.ro_buttons[label] = btn
            ro_layout1.addWidget(btn)
        layout.addWidget(ro_container1)

        ro_container2 = QtWidgets.QWidget()
        ro_layout2 = QtWidgets.QHBoxLayout(ro_container2)
        ro_layout2.setContentsMargins(0, 0, 0, 0)
        ro_layout2.setSpacing(dpi(6))

        for label in ["XZY", "YXZ", "ZYX"]:
            btn = self._create_ro_button(label)
            self.ro_buttons[label] = btn
            ro_layout2.addWidget(btn)
        layout.addWidget(ro_container2)

        layout.addSpacing(dpi(6))

        self.set_best_btn = self._create_red_button("Set to Best", self.on_set_best_clicked)
        layout.addWidget(self.set_best_btn)

        # ============ SEPARATOR between Group 1 and 2 ============
        layout.addSpacing(dpi(14))
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background-color: #4A3A3A; max-height: 1px; margin: 0px;")
        layout.addWidget(separator)
        layout.addSpacing(dpi(14))

        # ============ GROUP 2: Attribute Space Switcher ============

        attr_container = QtWidgets.QWidget()
        attr_layout = QtWidgets.QHBoxLayout(attr_container)
        attr_layout.setContentsMargins(0, 0, 0, 0)
        attr_layout.setSpacing(dpi(6))

        attr_label = QtWidgets.QLabel("Attribute:")
        attr_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; font-weight: 700;")
        attr_layout.addWidget(attr_label)
        attr_layout.addStretch()

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setMinimumHeight(dpi(29))
        self.refresh_btn.setStyleSheet("""
            QPushButton {{
                background-color: #C94A47;
                border: none;
                color: white;
                border-radius: 6px;
                font-size: 8pt;
                padding: 0px {0}px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #D95A57; }}
            QPushButton:pressed {{ background-color: #B93A37; }}
        """.format(dpi(11)))
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        attr_layout.addWidget(self.refresh_btn)
        layout.addWidget(attr_container)

        layout.addSpacing(dpi(4))

        self.attr_combo = QtWidgets.QComboBox()
        self.attr_combo.addItem("No Attributes")
        self.attr_combo.setMinimumHeight(dpi(33))
        self.attr_combo.setStyleSheet("""
            QComboBox {{
                background-color: #3D2A2A;
                border: none;
                color: white;
                border-radius: 6px;
                padding: {0}px {1}px;
                font-size: 8pt;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox::down-arrow {{ image: none; border: none; }}
            QComboBox QAbstractItemView {{
                background-color: #3D2A2A;
                color: white;
                selection-background-color: #C94A47;
                border: none;
                font-size: 8pt;
            }}
        """.format(dpi(5), dpi(11)))
        self.attr_combo.currentTextChanged.connect(self.on_attr_changed)
        layout.addWidget(self.attr_combo)

        layout.addSpacing(dpi(8))

        value_label = QtWidgets.QLabel("New Value:")
        value_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; padding-left: 2px; font-weight: 700;")
        layout.addWidget(value_label)

        layout.addSpacing(dpi(4))

        self.value_combo = QtWidgets.QComboBox()
        self.value_combo.addItem("No Values")
        self.value_combo.setMinimumHeight(dpi(33))
        self.value_combo.setStyleSheet("""
            QComboBox {{
                background-color: #3D2A2A;
                border: none;
                color: white;
                border-radius: 6px;
                padding: {0}px {1}px;
                font-size: 8pt;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox::down-arrow {{ image: none; border: none; }}
            QComboBox QAbstractItemView {{
                background-color: #3D2A2A;
                color: white;
                selection-background-color: #C94A47;
                border: none;
                font-size: 8pt;
            }}
        """.format(dpi(5), dpi(11)))
        layout.addWidget(self.value_combo)

        layout.addSpacing(dpi(8))

        self.current_frame_check = QtWidgets.QCheckBox("Only Current Frame")
        self.current_frame_check.setStyleSheet("""
            QCheckBox {{
                color: #AAAAAA;
                font-size: 8pt;
                spacing: {0}px;
            }}
            QCheckBox::indicator {{
                width: {1}px;
                height: {1}px;
                border-radius: 4px;
                background-color: #2A2A2A;
                border: none;
            }}
            QCheckBox::indicator:checked {{
                background-color: #C94A47;
            }}
        """.format(dpi(7), dpi(18)))
        layout.addWidget(self.current_frame_check)

        layout.addSpacing(dpi(8))

        self.apply_attr_btn = self._create_red_button("A P P L Y", self.on_apply_clicked)
        layout.addWidget(self.apply_attr_btn)

        # Initialize
        AttributeSpaceSwitcher.initialize_ui_state(
            self.attr_combo,
            self.value_combo,
            self.refresh_btn,
            self.apply_attr_btn,
            self.current_frame_check,
            self.ro_label
        )

        self._setup_selection_callback()

        layout.addStretch()

    def _create_ro_button(self, label):
        btn = QtWidgets.QPushButton(label)
        btn.setMinimumHeight(dpi(28))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #3D2A2A;
                border: none;
                color: white;
                padding: {0}px {1}px;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #4D3A3A; }}
            QPushButton:pressed {{ background-color: #2D1A1A; }}
        """.format(dpi(6), dpi(12)))
        btn.clicked.connect(partial(self.on_ro_button_clicked, label))
        return btn

    def _create_red_button(self, text, callback):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(dpi(28))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #C94A47;
                border: none;
                color: white;
                padding: {0}px {1}px;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background-color: #D95A57; }}
            QPushButton:pressed {{ background-color: #B93A37; }}
        """.format(dpi(6), dpi(12)))
        if callback:
            btn.clicked.connect(callback)
        return btn

    # ==================== Action Handlers ====================

    def on_attr_changed(self, text=None):
        AttributeSpaceSwitcher.update_value_menu(self.attr_combo)

    def on_ro_button_clicked(self, label):
        cmds.undoInfo(openChunk=True)
        try:
            AttributeSpaceSwitcher.change_ro_enhanced(label.lower())
            self._update_ro_display()
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def on_set_best_clicked(self):
        cmds.undoInfo(openChunk=True)
        try:
            AttributeSpaceSwitcher.set_each_object_to_best_ro()
            self._update_ro_display()
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def on_refresh_clicked(self):
        AttributeSpaceSwitcher.refresh_ui(
            self.attr_combo,
            self.value_combo,
            self.refresh_btn,
            self.apply_attr_btn,
            self.current_frame_check,
            self.ro_label
        )
        self._update_ro_display()
        self._clear_focus()

    def on_apply_clicked(self):
        cmds.undoInfo(openChunk=True)
        try:
            AttributeSpaceSwitcher.apply_change(self.attr_combo, self.value_combo, self.current_frame_check)
        finally:
            cmds.undoInfo(closeChunk=True)
        self._clear_focus()

    def _clear_focus(self):
        self.setFocus()

    def _update_ro_display(self):
        sel = cmds.ls(sl=True)
        
        default_style = """
            QPushButton {{
                background-color: #3D2A2A;
                border: none;
                color: white;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{ background-color: #4D3A3A; }}
            QPushButton:pressed {{ background-color: #2D1A1A; }}
        """.format(dpi(6), dpi(12))
        
        green_style = """
            QPushButton {{
                background-color: #2A5A2A;
                border: none;
                color: white;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{ background-color: #3A6A3A; }}
            QPushButton:pressed {{ background-color: #1A4A1A; }}
        """.format(dpi(6), dpi(12))
        
        for btn in self.ro_buttons.values():
            btn.setStyleSheet(default_style)
        
        if not sel:
            self.ro_label.setText("Select an Object!")
            return
        
        if len(sel) > 1:
            self.ro_label.setText("Multi-selection")
            return
        
        obj = sel[0]
        
        if not cmds.objExists(obj + ".rotateOrder"):
            self.ro_label.setText("No RO on object")
            return
        
        try:
            ro_index = cmds.getAttr("{0}.rotateOrder".format(obj))
            ro_names = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
            current_ro = ro_names[ro_index]
            
            current_ro_str = AttributeSpaceSwitcher.rotate_order_dict.get(ro_index, "xyz")
            mid_axis = current_ro_str[1].upper()
            rotate_attr = obj + ".rotate" + mid_axis
            
            current_risk = 0.0
            if cmds.objExists(rotate_attr):
                try:
                    mid_value = cmds.getAttr(rotate_attr)
                    current_risk = AttributeSpaceSwitcher.gimbal_risk(mid_value)
                except Exception:
                    pass
            
            self.ro_label.setText("{0} ({1:.0f}% risk)".format(current_ro, current_risk))
        except:
            self.ro_label.setText("Select an Object!")
            return
        
        try:
            cmds.undoInfo(stateWithoutFlush=False)
            best_ro, best_risk = AttributeSpaceSwitcher.evaluate_best_ro_with_preserve(obj)
            cmds.undoInfo(stateWithoutFlush=True)
            if best_ro is not None:
                best_ro_str = AttributeSpaceSwitcher.rotate_order_dict[best_ro].upper()
                if best_ro_str in self.ro_buttons:
                    self.ro_buttons[best_ro_str].setStyleSheet(green_style)
        except:
            cmds.undoInfo(stateWithoutFlush=True)
            pass

    def _setup_selection_callback(self):
        if not hasattr(self, '_script_jobs'):
            self._script_jobs = []
        
        job_id = cmds.scriptJob(
            event=["SelectionChanged", self._on_selection_changed],
            protected=True
        )
        self._script_jobs.append(job_id)
        
        self._update_ro_display()

    def _on_selection_changed(self):
        self._update_ro_display()
        AttributeSpaceSwitcher.refresh_ui()

    # ==================== Window Dragging ====================

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

    # ==================== Screen Change Detection ====================

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
        cmds.evalDeferred(reopen_attributes_space_switcher_ui)

    # ==================== Theme & Appearance ====================

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
        """)

    def apply_rounded_corners(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #C94A47;
            }
        """)
        
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        
        menu.exec_(self.mapToGlobal(pos))

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

    def enterEvent(self, event):
        self.fade_to(0.87, 50, QtCore.QEasingCurve.OutQuad)
        super(AttributesSpaceSwitcherUI, self).enterEvent(event)

    def leaveEvent(self, event):
        self.fade_to(0.55, 300)
        super(AttributesSpaceSwitcherUI, self).leaveEvent(event)


def reopen_attributes_space_switcher_ui():
    """Reopen the UI (called after screen change)."""
    show_ui()


# Global instance
_ui_instance = None


def show_ui():
    """Show the Attributes Space Switcher UI."""
    global _ui_instance
    
    if _ui_instance is not None:
        try:
            _ui_instance.close()
            _ui_instance.deleteLater()
        except Exception:
            pass
        _ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "AttributesSpaceSwitcherUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    _ui_instance = AttributesSpaceSwitcherUI()
    _ui_instance.show()
    return _ui_instance


if __name__ == "__main__":
    show_ui()
