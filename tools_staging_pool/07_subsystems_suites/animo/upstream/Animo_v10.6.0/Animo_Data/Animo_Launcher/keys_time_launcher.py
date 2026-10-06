from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import sys
import os
import platform

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtGui import QGuiApplication
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtGui, QtCore
        from PySide2.QtGui import QGuiApplication
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1
        QGuiApplication = QtGui.QApplication

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    int = builtins.int
    str = builtins.str
    range = builtins.range
except Exception:
    pass


def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except Exception:
        return 2022


def get_dpi_scale():
    maya_version = get_maya_version()
    
    dpi = 96.0
    base_scale = 1.0
    got_screen_info = False
    
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                try:
                    dpi = screen.logicalDotsPerInch()
                    got_screen_info = True
                except (RuntimeError, AttributeError):
                    pass
        
        if got_screen_info:
            base_scale = dpi / 96.0
            
    except (RuntimeError, AttributeError):
        pass
    except Exception:
        pass
    
    if maya_version >= 2025:
        if base_scale > 2.0:
            return max(1.0, min(base_scale * 1.15, 3.0))
        return max(1.0, min(base_scale, 3.0))
    
    if maya_version >= 2022 and maya_version <= 2024:
        return max(1.0, min(base_scale, 3.0))
    
    return max(1.0, min(base_scale, 3.0))


def get_manual_scale_override():
    if cmds.optionVar(exists="esnKeysTimeScale"):
        scale = cmds.optionVar(q="esnKeysTimeScale")
        return max(0.5, min(scale, 3.0))
    return None


def get_final_dpi_scale():
    manual_override = get_manual_scale_override()
    if manual_override:
        return manual_override
    return get_dpi_scale()


def scale_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())


def scale_font_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())


def is_macos():
    return platform.system() == 'Darwin'


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def get_scripts_path():
    try:
        if os.name == 'nt':
            base_path = os.path.join(os.path.expanduser('~'), 'Documents', 'maya', 'scripts')
        else:
            base_path = os.path.join(os.path.expanduser('~'), 'Library', 'Preferences', 'Autodesk', 'maya', 'scripts')
            if not os.path.exists(base_path):
                base_path = os.path.join(os.path.expanduser('~'), 'maya', 'scripts')
        
        keys_time_path = os.path.join(base_path, 'Animo_Data', 'Animo_Keys_Time')
        
        if os.path.exists(keys_time_path):
            return keys_time_path
        
        possible_paths = [
            os.path.join(os.path.expanduser('~'), 'Documents', 'maya', 'scripts', 'Animo_Data', 'Animo_Keys_Time'),
            os.path.join(os.path.expanduser('~'), 'maya', 'scripts', 'Animo_Data', 'Animo_Keys_Time'),
            os.path.join(os.path.expanduser('~'), 'Library', 'Preferences', 'Autodesk', 'maya', 'scripts', 'Animo_Data', 'Animo_Keys_Time'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return keys_time_path
        
    except Exception:
        return os.path.join(os.path.expanduser('~'), 'Documents', 'maya', 'scripts', 'Animo_Data', 'Animo_Keys_Time')


def find_versioned_script(scripts_path, script_name):
    """Find script file - checks .py first, then versioned .pyc, then generic .pyc"""
    import re
    
    base_name = os.path.splitext(script_name)[0]
    maya_version = get_maya_version()
    
    # Check for .py first
    py_path = os.path.join(scripts_path, script_name)
    if os.path.exists(py_path):
        return py_path, "py"
    
    # Check for exact version .pyc
    versioned_pyc = os.path.join(scripts_path, "{0}_py{1}.pyc".format(base_name, maya_version))
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    
    # Scan for other versioned .pyc files
    pattern = re.compile(r'^' + re.escape(base_name) + r'_py(\d{4})\.pyc$', re.IGNORECASE)
    available_versions = []
    
    if os.path.exists(scripts_path):
        for filename in os.listdir(scripts_path):
            match = pattern.match(filename)
            if match:
                file_version = int(match.group(1))
                available_versions.append((file_version, filename))
    
    if available_versions:
        available_versions.sort(key=lambda x: x[0], reverse=True)
        
        # Find closest version <= current Maya version
        for file_version, filename in available_versions:
            if file_version <= maya_version:
                return os.path.join(scripts_path, filename), "pyc"
        
        # Fall back to oldest available
        return os.path.join(scripts_path, available_versions[-1][1]), "pyc"
    
    # Check for generic .pyc
    generic_pyc = os.path.join(scripts_path, base_name + ".pyc")
    if os.path.exists(generic_pyc):
        return generic_pyc, "pyc"
    
    return None, None


def execute_external_script(script_name):
    import marshal
    
    scripts_path = get_scripts_path()
    script_path, file_type = find_versioned_script(scripts_path, script_name)
    
    if script_path is None:
        cmds.warning("Script not found: {0}".format(os.path.join(scripts_path, script_name)))
        return False
    
    try:
        exec_globals = {'__name__': '__main__', '__file__': script_path}
        
        if file_type == "py":
            if sys.version_info[0] >= 3:
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
            else:
                with open(script_path, 'r') as f:
                    script_content = f.read()
            
            exec(compile(script_content, script_path, 'exec'), exec_globals)
        else:
            # Load .pyc file
            with open(script_path, 'rb') as f:
                f.read(16)  # Skip pyc header
                code = marshal.load(f)
            
            exec(code, exec_globals)
        
        return True
        
    except Exception as e:
        cmds.warning("Error executing script {0}: {1}".format(script_name, str(e)))
        return False


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=('KeysTimeUI_WindowPos', pos_str))


def load_window_position():
    if cmds.optionVar(exists='KeysTimeUI_WindowPos'):
        try:
            pos_str = cmds.optionVar(q='KeysTimeUI_WindowPos')
            x, y = pos_str.split(',')
            return QtCore.QPoint(int(x), int(y))
        except Exception:
            pass
    return None


class KeysTimeUI(QtWidgets.QDialog):
    option_var_name = "KeysTimeUI_lastPos"
    
    def __init__(self, parent=get_maya_main_window()):
        super(KeysTimeUI, self).__init__(parent)
        self.setObjectName("KeysTimeUIWindow")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        self.current_mode = "Pose to Pose"
        
        self.setup_ui()
        self.apply_theme()
        self.restore_position()
        self.apply_rounded_corners()
        
        self.fade_to(0.87)
    
    def setup_ui(self):
        window_width = scale_size(240)
        window_height = scale_size(220)
        self.setFixedSize(window_width, window_height)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(scale_size(14), scale_size(14), scale_size(14), scale_size(14))
        main_layout.setSpacing(0)
        
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(0)
        
        spacer_left = QtWidgets.QWidget()
        spacer_left.setFixedSize(scale_size(26), scale_size(26))
        title_bar.addWidget(spacer_left)
        
        title_bar.addStretch()
        
        self.title_label = QtWidgets.QLabel("Keys Time")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11pt;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_bar.addWidget(self.title_label)
        
        title_bar.addStretch()
        
        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(scale_size(26), scale_size(26))
        close_button.setText("×")
        close_button.setCursor(QtCore.Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
                color: #666666;
                font-size: 16pt;
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
        
        main_layout.addSpacing(scale_size(14))
        
        self.mode_label = QtWidgets.QLabel("Pose to Pose")
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(self.mode_label)
        
        main_layout.addSpacing(scale_size(6))
        
        self.mode_dropdown = QtWidgets.QComboBox()
        self.mode_dropdown.addItems(["Pose to Pose", "Channels"])
        self.mode_dropdown.setFixedHeight(scale_size(33))
        self.mode_dropdown.setCursor(QtCore.Qt.PointingHandCursor)
        self.mode_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #3D2A2A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 5px 11px;
                font-size: 8pt;
            }
            QComboBox:hover {
                background-color: #4D3A3A;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3D2A2A;
                color: #FFFFFF;
                selection-background-color: #C94A47;
                border: none;
                font-size: 8pt;
            }
        """)
        self.mode_dropdown.currentTextChanged.connect(self.on_mode_changed)
        main_layout.addWidget(self.mode_dropdown)
        
        main_layout.addSpacing(scale_size(10))
        
        self.clean_button = QtWidgets.QPushButton("C L E A N   K E Y S")
        self.clean_button.setFixedHeight(scale_size(33))
        self.clean_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.clean_button.setStyleSheet("""
            QPushButton {
                background-color: #C94A47;
                border: none;
                color: #FFFFFF;
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #D95A57;
            }
            QPushButton:pressed {
                background-color: #B93A37;
            }
        """)
        self.clean_button.clicked.connect(self.clean_keys_action)
        main_layout.addWidget(self.clean_button)
        
        main_layout.addSpacing(scale_size(12))
        
        copy_paste_container = QtWidgets.QWidget()
        copy_paste_layout = QtWidgets.QHBoxLayout(copy_paste_container)
        copy_paste_layout.setContentsMargins(0, 0, 0, 0)
        copy_paste_layout.setSpacing(scale_size(7))
        
        self.copy_button = QtWidgets.QPushButton("C O P Y")
        self.copy_button.setFixedHeight(scale_size(35))
        self.copy_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #3D2A2A;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #4D3A3A;
            }
            QPushButton:pressed {
                background-color: #2D1A1A;
            }
        """)
        self.copy_button.clicked.connect(self.copy_action)
        copy_paste_layout.addWidget(self.copy_button)
        
        self.paste_button = QtWidgets.QPushButton("P A S T E")
        self.paste_button.setFixedHeight(scale_size(35))
        self.paste_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.paste_button.setStyleSheet("""
            QPushButton {
                background-color: #3D2A2A;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #4D3A3A;
            }
            QPushButton:pressed {
                background-color: #2D1A1A;
            }
        """)
        self.paste_button.clicked.connect(self.paste_action)
        copy_paste_layout.addWidget(self.paste_button)
        
        main_layout.addWidget(copy_paste_container)
        
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
        radius = 14
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    
    def resizeEvent(self, event):
        super(KeysTimeUI, self).resizeEvent(event)
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
    
    def on_mode_changed(self, text):
        self.current_mode = text
        self.mode_label.setText(text)
    
    def clean_keys_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            execute_external_script("clean_keys_interactive.py")
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def copy_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            if self.current_mode == "Pose to Pose":
                execute_external_script("copy_key_times_pose_to_pose.py")
            else:
                execute_external_script("copy_key_times_channels.py")
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def paste_action(self):
        cmds.undoInfo(openChunk=True)
        try:
            if self.current_mode == "Pose to Pose":
                execute_external_script("paste_key_times_pose_to_pose.py")
            else:
                execute_external_script("paste_key_times_channels.py")
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass
    
    def restore_position(self):
        saved_pos = load_window_position()
        if saved_pos:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen().geometry()
            else:
                screen = QtWidgets.QApplication.desktop().screenGeometry()
            
            window_width = self.width()
            window_height = self.height()
            
            if (saved_pos.x() >= 0 and saved_pos.y() >= 0 and
                saved_pos.x() < screen.width() - window_width and
                saved_pos.y() < screen.height() - window_height):
                self.move(saved_pos)
    
    def closeEvent(self, event):
        save_window_position(self.pos())
        super(KeysTimeUI, self).closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'globalPosition'):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, 'globalPosition'):
                delta = event.globalPosition().toPoint() - self.old_pos
                self.old_pos = event.globalPosition().toPoint()
            else:
                delta = event.globalPos() - self.old_pos
                self.old_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
    def enterEvent(self, event):
        self.fade_to(0.87, 50, QtCore.QEasingCurve.OutQuad)
        super(KeysTimeUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.fade_to(0.67, 300)
        super(KeysTimeUI, self).leaveEvent(event)


keys_time_ui_instance = None


def create_keys_time_ui():
    global keys_time_ui_instance
    
    if keys_time_ui_instance is not None:
        try:
            keys_time_ui_instance.close()
            keys_time_ui_instance.deleteLater()
        except Exception:
            pass
        keys_time_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "KeysTimeUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    keys_time_ui_instance = KeysTimeUI()
    keys_time_ui_instance.show()
    return keys_time_ui_instance


def ui():
    return create_keys_time_ui()


create_keys_time_ui()