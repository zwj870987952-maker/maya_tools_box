from __future__ import division
from __future__ import absolute_import

import os
import sys

try:
    _this_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    from maya import cmds as _cmds
    _this_dir = os.path.normpath(os.path.join(
        _cmds.internalVar(userScriptDir=True), "..", "..", "scripts", "Animo_Data", "Animo_Transify"
    ))

if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from maya import cmds

from transify_common import (
    QtWidgets, QtGui, QtCore, PYSIDE_VERSION,
    dpi, is_macos, get_maya_main_window, show_styled_error,
    save_window_position, load_window_position, is_position_visible,
    get_screen_at_position, get_scale_factor, set_scale_factor,
    get_scale_factor_for_screen, get_center_of_primary_screen,
    load_transify_module,
)
from transify_engine import AnimationCopyPasteJson


def _run_action(module_name, ui):
    action_module = load_transify_module(module_name)
    if action_module is not None:
        action_module.run(ui)


class TransifyUI(QtWidgets.QDialog):
    option_var_name = "TransifyUI_lastPos"
    
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(TransifyUI, self).__init__(parent)
        self.setObjectName("TransifyUIWindow")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        self.current_mode = "Insert"
        self.selected_file = None
        
        self._current_screen = None
        self._current_scale_factor = get_scale_factor()
        
        self.tool = AnimationCopyPasteJson()
        
        self.setup_ui()
        self.apply_theme()
        self.restore_position()
        self.apply_rounded_corners()
        self.update_file_info()
        
        self.fade_to(0.87)
    
    def setup_ui(self):
        window_width = dpi(280)
        window_height = dpi(560)
        self.setFixedSize(window_width, window_height)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(16), dpi(16), dpi(16), dpi(16))
        main_layout.setSpacing(dpi(8))
        
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(0)
        
        spacer_left = QtWidgets.QWidget()
        spacer_left.setFixedSize(dpi(26), dpi(26))
        title_bar.addWidget(spacer_left)
        
        title_bar.addStretch()
        
        self.title_label = QtWidgets.QLabel("Transify")
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #4A90E2; background: transparent;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_bar.addWidget(self.title_label)
        
        title_bar.addStretch()
        
        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(dpi(26), dpi(26))
        close_button.setText(u"\u00D7")
        close_button.setCursor(QtCore.Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
                color: #666666;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        main_layout.addLayout(title_bar)
        main_layout.addSpacing(dpi(14))
        
        copy_label = QtWidgets.QLabel("COPY ANIMATION")
        copy_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(copy_label)
        main_layout.addSpacing(dpi(8))
        
        self.copy_all_button = QtWidgets.QPushButton("C O P Y   A L L   A N I M A T I O N")
        self.copy_all_button.setFixedHeight(dpi(35))
        self.copy_all_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_all_button.setStyleSheet("""
            QPushButton {
                background-color: #3A7BC8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4A8BD8;
            }
            QPushButton:pressed {
                background-color: #2A6BB8;
            }
        """)
        self.copy_all_button.clicked.connect(self.copy_all_action)
        main_layout.addWidget(self.copy_all_button)
        main_layout.addSpacing(dpi(6))
        
        self.copy_selected_button = QtWidgets.QPushButton("C O P Y   S E L E C T E D   C U R V E S")
        self.copy_selected_button.setFixedHeight(dpi(35))
        self.copy_selected_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_selected_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.copy_selected_button.clicked.connect(self.copy_action)
        main_layout.addWidget(self.copy_selected_button)
        main_layout.addSpacing(dpi(14))
        
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("background-color: #3A3A3A; border: none;")
        main_layout.addWidget(separator1)
        main_layout.addSpacing(dpi(10))
        
        self.file_info_label = QtWidgets.QLabel("No files found")
        self.file_info_label.setStyleSheet("""
            QLabel {
                font-size: 7pt;
                color: #888888;
                font-style: italic;
                background: transparent;
            }
        """)
        self.file_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.file_info_label.setWordWrap(True)
        main_layout.addWidget(self.file_info_label)
        main_layout.addSpacing(dpi(10))
        
        paste_label = QtWidgets.QLabel("PASTE ANIMATION")
        paste_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(paste_label)
        main_layout.addSpacing(dpi(8))
        
        self.select_button = QtWidgets.QPushButton("S E L E C T   O B J E C T S")
        self.select_button.setFixedHeight(dpi(33))
        self.select_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9BD5;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #6BABE5;
            }
            QPushButton:pressed {
                background-color: #4B8BC5;
            }
        """)
        self.select_button.clicked.connect(self.select_objects_action)
        main_layout.addWidget(self.select_button)
        main_layout.addSpacing(dpi(8))
        
        paste_container = QtWidgets.QWidget()
        paste_layout = QtWidgets.QHBoxLayout(paste_container)
        paste_layout.setContentsMargins(0, 0, 0, 0)
        paste_layout.setSpacing(dpi(8))
        
        self.replace_button = QtWidgets.QPushButton("R E P L A C E")
        self.replace_button.setFixedHeight(dpi(38))
        self.replace_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.replace_button.setStyleSheet("""
            QPushButton {
                background-color: #2E6BA8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #3E7BB8;
            }
            QPushButton:pressed {
                background-color: #1E5B98;
            }
        """)
        self.replace_button.clicked.connect(self.replace_action)
        paste_layout.addWidget(self.replace_button)
        
        self.insert_button = QtWidgets.QPushButton("I N S E R T")
        self.insert_button.setFixedHeight(dpi(38))
        self.insert_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.insert_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.insert_button.clicked.connect(self.insert_action)
        paste_layout.addWidget(self.insert_button)
        
        main_layout.addWidget(paste_container)
        main_layout.addSpacing(dpi(8))
        
        self.browse_button = QtWidgets.QPushButton("B R O W S E   F I L E S")
        self.browse_button.setFixedHeight(dpi(30))
        self.browse_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3D4045;
                border: 1px solid #505560;
                color: #CCCCCC;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4A4E55;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2D3035;
            }
        """)
        self.browse_button.clicked.connect(self.browse_action)
        main_layout.addWidget(self.browse_button)
        main_layout.addSpacing(dpi(14))
        
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: #3A3A3A; border: none;")
        main_layout.addWidget(separator2)
        main_layout.addSpacing(dpi(10))
        
        pose_label = QtWidgets.QLabel("POSE")
        pose_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(pose_label)
        main_layout.addSpacing(dpi(8))
        
        pose_container = QtWidgets.QWidget()
        pose_layout = QtWidgets.QHBoxLayout(pose_container)
        pose_layout.setContentsMargins(0, 0, 0, 0)
        pose_layout.setSpacing(dpi(8))
        
        self.copy_pose_button = QtWidgets.QPushButton("C O P Y")
        self.copy_pose_button.setFixedHeight(dpi(35))
        self.copy_pose_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_pose_button.setStyleSheet("""
            QPushButton {
                background-color: #3A7BC8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4A8BD8;
            }
            QPushButton:pressed {
                background-color: #2A6BB8;
            }
        """)
        self.copy_pose_button.clicked.connect(self.copy_pose_action)
        pose_layout.addWidget(self.copy_pose_button)
        
        self.paste_pose_button = QtWidgets.QPushButton("P A S T E")
        self.paste_pose_button.setFixedHeight(dpi(35))
        self.paste_pose_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.paste_pose_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.paste_pose_button.clicked.connect(self.paste_pose_action)
        pose_layout.addWidget(self.paste_pose_button)
        
        main_layout.addWidget(pose_container)
        
        main_layout.addStretch()
    
    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                color: white;
                border-radius: 14px;
            }
        """)
    
    def apply_rounded_corners(self):
        try:
            radius = dpi(14)
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
            if PYSIDE_VERSION >= 2:
                polygon = path.toFillPolygon().toPolygon()
            else:
                polygon = path.toFillPolygon().toPolygon()
            region = QtGui.QRegion(polygon)
            self.setMask(region)
        except Exception:
            pass
    
    def resizeEvent(self, event):
        super(TransifyUI, self).resizeEvent(event)
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
    
    def update_file_info(self):
        if self.selected_file:
            filename = os.path.basename(self.selected_file)
            self.file_info_label.setText(filename)
        else:
            latest = self.tool.get_latest_json_file()
            if latest:
                filename = os.path.basename(latest)
                self.file_info_label.setText(filename)
            else:
                self.file_info_label.setText("No files found")
    
    def has_selection(self):
        return bool(cmds.ls(selection=True))
    
    def get_target_namespace(self):
        selected = cmds.ls(selection=True)
        if selected:
            return self.tool.detect_most_common_namespace_from_selection(selected)
        return ""
    
    def copy_all_action(self):
        _run_action("action_copy_all", self)
    
    def copy_action(self):
        _run_action("action_copy_selected", self)
    
    def insert_action(self):
        _run_action("action_paste_insert", self)
    
    def replace_action(self):
        _run_action("action_paste_replace", self)
    
    
    def copy_pose_action(self):
        _run_action("action_copy_pose", self)
    
    def paste_pose_action(self):
        _run_action("action_paste_pose", self)
    
    def select_objects_action(self):
        _run_action("action_select_objects", self)
    
    def browse_action(self):
        _run_action("action_browse_files", self)
    
    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass
    
    def restore_position(self):
        """Restore window position, checking if it's visible on any screen."""
        saved_pos = load_window_position()
        window_width = self.width()
        window_height = self.height()
        
        if saved_pos and is_position_visible(saved_pos, window_width, window_height):
            self.move(saved_pos)
        else:
            center = get_center_of_primary_screen()
            new_x = center.x() - window_width // 2
            new_y = center.y() - window_height // 2
            self.move(new_x, new_y)
        
        try:
            center = QtCore.QPoint(
                self.x() + window_width // 2,
                self.y() + window_height // 2
            )
            self._current_screen = get_screen_at_position(center)
            if self._current_screen:
                self._current_scale_factor = get_scale_factor_for_screen(self._current_screen)
        except:
            pass
    
    def closeEvent(self, event):
        save_window_position(self.pos())
        super(TransifyUI, self).closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, "globalPosition"):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            if hasattr(event, "globalPosition"):
                self.show_context_menu(event.globalPosition().toPoint())
            else:
                self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #2E2E2E;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #E0E0E0;
                font-size: 8pt;
            }}
            QMenu::item {{
                padding: {0}px {1}px;
                border-radius: 2px;
                margin: 1px;
            }}
            QMenu::item:selected {{
                background-color: #4A90E2;
                color: white;
            }}
        """.format(dpi(6), dpi(12)))
        
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_ui)
        
        if self.selected_file:
            clear_action = menu.addAction("Use Latest File")
            clear_action.triggered.connect(self.clear_selected_file)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Close")
        if PYSIDE_VERSION == 6:
            action = menu.exec(pos)
        else:
            action = menu.exec_(pos)
        if action == exit_action:
            self.close()
    
    def clear_selected_file(self):
        self.selected_file = None
        self.update_file_info()
    
    def refresh_ui(self):
        self.update_file_info()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, "globalPosition"):
                delta = event.globalPosition().toPoint() - self.old_pos
                self.old_pos = event.globalPosition().toPoint()
            else:
                delta = event.globalPos() - self.old_pos
                self.old_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.check_screen_change()
    
    def moveEvent(self, event):
        """Called when window position changes."""
        super(TransifyUI, self).moveEvent(event)
    
    def check_screen_change(self):
        """Check if window moved to a different screen and rebuild UI if DPI changed."""
        try:
            center = QtCore.QPoint(
                self.x() + self.width() // 2,
                self.y() + self.height() // 2
            )
            
            new_screen = get_screen_at_position(center)
            if new_screen is None:
                return
            
            new_scale = get_scale_factor_for_screen(new_screen)
            
            if abs(new_scale - self._current_scale_factor) > 0.01:
                self._current_screen = new_screen
                self._current_scale_factor = new_scale
                
                self.rebuild_for_new_screen(new_scale)
        except Exception:
            pass
    
    def rebuild_for_new_screen(self, new_scale):
        """Rebuild the UI for a new screen with different DPI."""
        current_pos = self.pos()
        
        set_scale_factor(new_scale)
        
        for child in self.findChildren(QtWidgets.QWidget):
            child.deleteLater()
        
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())
            
            QtWidgets.QWidget().setLayout(old_layout)
        
        QtWidgets.QApplication.processEvents()
        
        self.setup_ui()
        self.apply_theme()
        self.apply_rounded_corners()
        self.update_file_info()
        
        self.move(current_pos)
    
    def _clear_layout(self, layout):
        """Recursively clear a layout."""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def enterEvent(self, event):
        self.fade_to(0.95, 50, QtCore.QEasingCurve.OutQuad)
        super(TransifyUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.fade_to(0.75, 300)
        super(TransifyUI, self).leaveEvent(event)


transify_ui_instance = None


def create_transify_ui():
    global transify_ui_instance
    
    if transify_ui_instance is not None:
        try:
            transify_ui_instance.close()
            transify_ui_instance.deleteLater()
        except Exception:
            pass
        transify_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "TransifyUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    transify_ui_instance = TransifyUI()
    transify_ui_instance.show()
    return transify_ui_instance


def ui():
    return create_transify_ui()


def show_modern_animation_copy_paste_ui():
    return create_transify_ui()


def create_complete_animation_ui():
    return create_transify_ui()


def create_animation_paste_ui():
    return create_transify_ui()


def create_animation_copy_ui():
    return create_transify_ui()


create_transify_ui()
