from __future__ import division
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

_tracify_module = None


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


def scale_size(size):
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
        version_script_dir = cmds.internalVar(userScriptDir=True)
        base_path = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(base_path, 'Animo_Data', 'Animo_Launcher')
    except Exception:
        username = os.getenv('USERNAME', '')
        return os.path.join('C:', os.sep, 'Users', username, 'Documents', 'maya', 'scripts', 'Animo_Data', 'Animo_Launcher')


def find_versioned_script(scripts_path, script_name):
    import re
    
    base_name = os.path.splitext(script_name)[0]
    maya_version = get_maya_version()
    
    py_path = os.path.join(scripts_path, script_name)
    if os.path.exists(py_path):
        return py_path, "py"
    
    versioned_pyc = os.path.join(scripts_path, "{0}_py{1}.pyc".format(base_name, maya_version))
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    
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
        for file_version, filename in available_versions:
            if file_version <= maya_version:
                return os.path.join(scripts_path, filename), "pyc"
        return os.path.join(scripts_path, available_versions[-1][1]), "pyc"
    
    generic_pyc = os.path.join(scripts_path, base_name + ".pyc")
    if os.path.exists(generic_pyc):
        return generic_pyc, "pyc"
    
    return None, None


def load_tracify_module():
    global _tracify_module
    import marshal
    
    scripts_path = get_scripts_path()
    
    script_path, file_type = find_versioned_script(scripts_path, "tracify.py")
    
    if script_path is None:
        return None
    
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    existing_tracify = sys.modules.get('tracify')
    if existing_tracify is not None:
        _tracify_module = existing_tracify
        return _tracify_module
    
    try:
        if file_type == "py":
            import tracify
            _tracify_module = tracify
        else:
            import types
            with open(script_path, 'rb') as f:
                f.read(16)
                code = marshal.load(f)
            
            module = types.ModuleType('tracify')
            module.__file__ = script_path
            exec(code, module.__dict__)
            sys.modules['tracify'] = module
            _tracify_module = module
        
        node_path, node_type = find_versioned_script(scripts_path, "tracify_node.py")
        
        return _tracify_module
        
    except Exception:
        return None


def get_tracify():
    global _tracify_module
    if _tracify_module is None:
        load_tracify_module()
    return _tracify_module


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=('TracifyUI_WindowPos', pos_str))


def load_window_position():
    if cmds.optionVar(exists='TracifyUI_WindowPos'):
        try:
            pos_str = cmds.optionVar(q='TracifyUI_WindowPos')
            x, y = pos_str.split(',')
            return QtCore.QPoint(int(x), int(y))
        except Exception:
            pass
    return None


def save_custom_colors(trail_color, keys_color):
    cmds.optionVar(stringValue=('TracifyUI_TrailColor', '{0},{1},{2}'.format(*trail_color)))
    cmds.optionVar(stringValue=('TracifyUI_KeysColor', '{0},{1},{2}'.format(*keys_color)))


def save_color_mode(mode):
    cmds.optionVar(intValue=('TracifyUI_ColorMode', mode))


def load_color_mode():
    if cmds.optionVar(exists='TracifyUI_ColorMode'):
        try:
            return cmds.optionVar(q='TracifyUI_ColorMode')
        except Exception:
            pass
    return 1  # Default: rainbow


def load_custom_colors():
    trail_color = (0.85, 0.12, 0.11)
    keys_color = (0.95, 0.45, 0.45)
    
    if cmds.optionVar(exists='TracifyUI_TrailColor'):
        try:
            parts = cmds.optionVar(q='TracifyUI_TrailColor').split(',')
            trail_color = (float(parts[0]), float(parts[1]), float(parts[2]))
        except Exception:
            pass
    
    if cmds.optionVar(exists='TracifyUI_KeysColor'):
        try:
            parts = cmds.optionVar(q='TracifyUI_KeysColor').split(',')
            keys_color = (float(parts[0]), float(parts[1]), float(parts[2]))
        except Exception:
            pass
    
    return trail_color, keys_color


def save_dot_size(value):
    cmds.optionVar(intValue=('TracifyUI_DotSize', value))


def load_dot_size():
    if cmds.optionVar(exists='TracifyUI_DotSize'):
        try:
            return cmds.optionVar(q='TracifyUI_DotSize')
        except Exception:
            pass
    return 5  # Default


def save_line_width(value):
    cmds.optionVar(intValue=('TracifyUI_LineWidth', value))


def load_line_width():
    if cmds.optionVar(exists='TracifyUI_LineWidth'):
        try:
            return cmds.optionVar(q='TracifyUI_LineWidth')
        except Exception:
            pass
    return 4  # Default


def save_camera_space(enabled):
    cmds.optionVar(intValue=('TracifyUI_CameraSpace', 1 if enabled else 0))


def load_camera_space():
    if cmds.optionVar(exists='TracifyUI_CameraSpace'):
        try:
            return bool(cmds.optionVar(q='TracifyUI_CameraSpace'))
        except Exception:
            pass
    return False  # Default


FRAME_RANGE_OPTIONS = [4, 8, 16, 32, 64]
FRAME_RANGE_ALL_VALUE = 999999
FRAME_RANGE_DEFAULT = 16


def save_frame_range(value):
    cmds.optionVar(intValue=('TracifyUI_FrameRange', value))


def load_frame_range():
    if cmds.optionVar(exists='TracifyUI_FrameRange'):
        try:
            return cmds.optionVar(q='TracifyUI_FrameRange')
        except Exception:
            pass
    return FRAME_RANGE_DEFAULT


class ColorButton(QtWidgets.QPushButton):
    color_changed = QtCore.Signal(tuple)
    
    def __init__(self, color=(1.0, 1.0, 1.0), parent=None):
        super(ColorButton, self).__init__(parent)
        self._color = color
        self.setFixedSize(scale_size(50), scale_size(24))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_style()
        self.clicked.connect(self.pick_color)
    
    def update_style(self):
        r = int(self._color[0] * 255)
        g = int(self._color[1] * 255)
        b = int(self._color[2] * 255)
        self.setStyleSheet("""
            QPushButton {{
                background-color: rgb({0}, {1}, {2});
                border: 2px solid #444444;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #666666;
            }}
        """.format(r, g, b))
    
    def pick_color(self):
        initial = QtGui.QColor(int(self._color[0] * 255), int(self._color[1] * 255), int(self._color[2] * 255))
        color = QtWidgets.QColorDialog.getColor(initial, self, "Pick Color")
        if color.isValid():
            self._color = (color.redF(), color.greenF(), color.blueF())
            self.update_style()
            self.color_changed.emit(self._color)
    
    def set_color(self, color):
        self._color = color
        self.update_style()
    
    def get_color(self):
        return self._color


class PresetButton(QtWidgets.QPushButton):
    preset_clicked = QtCore.Signal(tuple, tuple)
    
    def __init__(self, trail_color, keys_color, parent=None):
        super(PresetButton, self).__init__(parent)
        self._trail_color = trail_color
        self._keys_color = keys_color
        self.setFixedSize(scale_size(50), scale_size(40))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_style()
        self.clicked.connect(self.on_click)
    
    def update_style(self):
        r = int(self._trail_color[0] * 255)
        g = int(self._trail_color[1] * 255)
        b = int(self._trail_color[2] * 255)
        # Slightly lighter at top, slightly darker at bottom
        r_light = min(255, int(r * 1.1))
        g_light = min(255, int(g * 1.1))
        b_light = min(255, int(b * 1.1))
        r_dark = int(r * 0.85)
        g_dark = int(g * 0.85)
        b_dark = int(b * 0.85)
        self.setStyleSheet("""
            QPushButton {{
                background: qlineargradient(y1:0, y2:1, stop:0 rgb({0}, {1}, {2}), stop:1 rgb({3}, {4}, {5}));
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #FFFFFF;
            }}
        """.format(r_light, g_light, b_light, r_dark, g_dark, b_dark))
    
    def on_click(self):
        self.preset_clicked.emit(self._trail_color, self._keys_color)


class TracifyUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(TracifyUI, self).__init__(parent)
        self.setObjectName("TracifyUIWindow")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        
        self.trail_color, self.keys_color = load_custom_colors()
        
        self.setup_ui()
        self.apply_theme()
        self.restore_position()
        self.apply_rounded_corners()
        
        self.fade_to(0.87)
    
    def setup_ui(self):
        window_width = scale_size(240)
        window_height = scale_size(440)
        self.setFixedSize(window_width, window_height)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(scale_size(18), scale_size(18), scale_size(18), scale_size(18))
        main_layout.setSpacing(0)
        
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(0)
        
        spacer_left = QtWidgets.QWidget()
        spacer_left.setFixedSize(scale_size(26), scale_size(26))
        title_bar.addWidget(spacer_left)
        
        title_bar.addStretch()
        
        self.title_label = QtWidgets.QLabel("Tracify")
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
        main_layout.addSpacing(scale_size(20))
        
        presets_label = QtWidgets.QLabel("Solid:")
        presets_label.setStyleSheet("""
            QLabel {
                font-size: 8pt;
                color: #888888;
                background: transparent;
            }
        """)
        main_layout.addWidget(presets_label)
        main_layout.addSpacing(scale_size(10))
        
        # Row 1: Solid color presets
        presets_layout = QtWidgets.QHBoxLayout()
        presets_layout.setSpacing(scale_size(10))
        
        presets = [
            ((0.85, 0.12, 0.11), (0.95, 0.45, 0.45)),   # Red trail -> Light red dots
            ((0.23, 0.48, 0.84), (0.55, 0.72, 0.95)),   # Blue trail -> Light blue dots
            ((0.7, 0.3, 0.9), (0.85, 0.6, 0.95)),       # Purple trail -> Light purple dots
            ((0.1, 0.8, 0.5), (0.5, 0.92, 0.7)),        # Green trail -> Light green dots
        ]
        
        for trail_c, keys_c in presets:
            btn = PresetButton(trail_c, keys_c)
            btn.preset_clicked.connect(self.apply_preset)
            presets_layout.addWidget(btn)
        
        presets_layout.addStretch()
        main_layout.addLayout(presets_layout)
        main_layout.addSpacing(scale_size(28))
        
        # Row 2: Gradient presets label
        gradient_label = QtWidgets.QLabel("Gradients:")
        gradient_label.setStyleSheet("""
            QLabel {
                font-size: 8pt;
                color: #888888;
                background: transparent;
            }
        """)
        main_layout.addWidget(gradient_label)
        main_layout.addSpacing(scale_size(10))
        
        # Row 2: Gradient presets
        gradient_layout = QtWidgets.QHBoxLayout()
        gradient_layout.setSpacing(scale_size(10))
        
        self.gradient_buttons = []
        
        # Rainbow button (mode 1)
        self.rainbow_btn = QtWidgets.QPushButton()
        self.rainbow_btn.setFixedSize(scale_size(50), scale_size(40))
        self.rainbow_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.rainbow_btn.setCheckable(True)
        self.rainbow_btn.setProperty("colorMode", 1)
        self.rainbow_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff0000, stop:0.17 #ffff00, stop:0.33 #00ff00,
                    stop:0.5 #00ffff, stop:0.67 #0000ff, stop:0.83 #ff00ff, stop:1 #ff0000);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { border: 2px solid #4D4D4D; }
            QPushButton:checked { border: 2px solid #FFFFFF; }
        """)
        self.rainbow_btn.clicked.connect(lambda: self.set_gradient_mode(1))
        gradient_layout.addWidget(self.rainbow_btn)
        self.gradient_buttons.append(self.rainbow_btn)
        
        # Fire button (mode 2) - red/orange/gold
        self.fire_btn = QtWidgets.QPushButton()
        self.fire_btn.setFixedSize(scale_size(50), scale_size(40))
        self.fire_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.fire_btn.setCheckable(True)
        self.fire_btn.setProperty("colorMode", 2)
        self.fire_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e61a1a, stop:0.25 #ff4d00, stop:0.5 #ff8000,
                    stop:0.75 #ffb31a, stop:1 #ffd933);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { border: 2px solid #4D4D4D; }
            QPushButton:checked { border: 2px solid #FFFFFF; }
        """)
        self.fire_btn.clicked.connect(lambda: self.set_gradient_mode(2))
        gradient_layout.addWidget(self.fire_btn)
        self.gradient_buttons.append(self.fire_btn)
        
        # Ocean button (mode 3) - blue/cyan/teal
        self.ocean_btn = QtWidgets.QPushButton()
        self.ocean_btn.setFixedSize(scale_size(50), scale_size(40))
        self.ocean_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.ocean_btn.setCheckable(True)
        self.ocean_btn.setProperty("colorMode", 3)
        self.ocean_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0033cc, stop:0.25 #0066cc, stop:0.5 #0099e6,
                    stop:0.75 #00ccd9, stop:1 #33e6cc);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { border: 2px solid #4D4D4D; }
            QPushButton:checked { border: 2px solid #FFFFFF; }
        """)
        self.ocean_btn.clicked.connect(lambda: self.set_gradient_mode(3))
        gradient_layout.addWidget(self.ocean_btn)
        self.gradient_buttons.append(self.ocean_btn)
        
        # Candy button (mode 4) - light pink/pink/purple
        self.candy_btn = QtWidgets.QPushButton()
        self.candy_btn.setFixedSize(scale_size(50), scale_size(40))
        self.candy_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.candy_btn.setCheckable(True)
        self.candy_btn.setProperty("colorMode", 4)
        self.candy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffd9eb, stop:0.25 #ff99cc, stop:0.5 #ff66b2,
                    stop:0.75 #e64dbf, stop:1 #bf59e6);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { border: 2px solid #4D4D4D; }
            QPushButton:checked { border: 2px solid #FFFFFF; }
        """)
        self.candy_btn.clicked.connect(lambda: self.set_gradient_mode(4))
        gradient_layout.addWidget(self.candy_btn)
        self.gradient_buttons.append(self.candy_btn)
        
        gradient_layout.addStretch()
        main_layout.addLayout(gradient_layout)
        main_layout.addSpacing(scale_size(24))
        
        # Line width slider (moved to top)
        line_row = QtWidgets.QHBoxLayout()
        line_row.setSpacing(scale_size(8))
        line_label = QtWidgets.QLabel("Line")
        line_label.setFixedWidth(scale_size(40))
        line_label.setStyleSheet("QLabel { color: #FFFFFF; font-size: 8pt; background: transparent; }")
        line_row.addWidget(line_label)
        
        self.line_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.line_slider.setMinimum(1)
        self.line_slider.setMaximum(10)
        saved_line_width = load_line_width()
        self.line_slider.setValue(saved_line_width)
        self.line_slider.setFixedHeight(scale_size(20))
        self.line_slider.setStyleSheet("""
            QSlider::groove:horizontal {{
                background: #3D3D3D;
                height: {groove}px;
                border-radius: {grooveRadius}px;
            }}
            QSlider::handle:horizontal {{
                background: #3A7BD5;
                width: {handle}px;
                height: {handle}px;
                margin: {margin}px 0;
                border-radius: {handleRadius}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #4A8BE5;
            }}
        """.format(
            groove=scale_size(4),
            grooveRadius=scale_size(2),
            handle=scale_size(14),
            handleRadius=scale_size(7),
            margin=-(scale_size(14) - scale_size(4)) // 2
        ))
        self.line_slider.valueChanged.connect(self.on_line_width_changed)
        line_row.addWidget(self.line_slider)
        
        self.line_value_label = QtWidgets.QLabel(str(saved_line_width))
        self.line_value_label.setFixedWidth(scale_size(20))
        self.line_value_label.setStyleSheet("QLabel { color: #888888; font-size: 8pt; background: transparent; }")
        line_row.addWidget(self.line_value_label)
        
        main_layout.addLayout(line_row)
        main_layout.addSpacing(scale_size(8))
        
        # Dot size slider
        size_row = QtWidgets.QHBoxLayout()
        size_row.setSpacing(scale_size(8))
        size_label = QtWidgets.QLabel("Dots")
        size_label.setFixedWidth(scale_size(40))
        size_label.setStyleSheet("QLabel { color: #FFFFFF; font-size: 8pt; background: transparent; }")
        size_row.addWidget(size_label)
        
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setMinimum(2)
        self.size_slider.setMaximum(20)
        saved_dot_size = load_dot_size()
        self.size_slider.setValue(saved_dot_size)
        self.size_slider.setFixedHeight(scale_size(20))
        self.size_slider.setStyleSheet("""
            QSlider::groove:horizontal {{
                background: #3D3D3D;
                height: {groove}px;
                border-radius: {grooveRadius}px;
            }}
            QSlider::handle:horizontal {{
                background: #3A7BD5;
                width: {handle}px;
                height: {handle}px;
                margin: {margin}px 0;
                border-radius: {handleRadius}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #4A8BE5;
            }}
        """.format(
            groove=scale_size(4),
            grooveRadius=scale_size(2),
            handle=scale_size(14),
            handleRadius=scale_size(7),
            margin=-(scale_size(14) - scale_size(4)) // 2
        ))
        self.size_slider.valueChanged.connect(self.on_dot_size_changed)
        size_row.addWidget(self.size_slider)
        
        self.size_value_label = QtWidgets.QLabel(str(saved_dot_size))
        self.size_value_label.setFixedWidth(scale_size(20))
        self.size_value_label.setStyleSheet("QLabel { color: #888888; font-size: 8pt; background: transparent; }")
        size_row.addWidget(self.size_value_label)
        
        main_layout.addLayout(size_row)
        main_layout.addSpacing(scale_size(16))
        
        camera_row = QtWidgets.QHBoxLayout()
        camera_row.setSpacing(scale_size(8))
        
        self.camera_space_checkbox = QtWidgets.QCheckBox("Camera Space")
        self.camera_space_checkbox.setCursor(QtCore.Qt.PointingHandCursor)
        self.camera_space_checkbox.setStyleSheet("""
            QCheckBox {{
                color: #FFFFFF;
                font-size: 8pt;
                background: transparent;
                spacing: {spacing}px;
            }}
            QCheckBox::indicator {{
                width: {indicator}px;
                height: {indicator}px;
                border-radius: {radius}px;
                border: {border}px solid #3D3D3D;
                background-color: #2D2D2D;
            }}
            QCheckBox::indicator:hover {{
                border: {border}px solid #666666;
            }}
            QCheckBox::indicator:checked {{
                background-color: #3A7BD5;
                border: {border}px solid #3A7BD5;
            }}
        """.format(
            spacing=scale_size(8),
            indicator=scale_size(14),
            radius=scale_size(3),
            border=max(1, scale_size(1))
        ))
        saved_camera_space = load_camera_space()
        self.camera_space_checkbox.setChecked(saved_camera_space)
        self.camera_space_checkbox.stateChanged.connect(self.on_camera_space_changed)
        camera_row.addWidget(self.camera_space_checkbox)
        camera_row.addStretch()
        
        main_layout.addLayout(camera_row)
        main_layout.addSpacing(scale_size(16))
        
        frame_range_row = QtWidgets.QHBoxLayout()
        frame_range_row.setSpacing(scale_size(8))
        
        frame_range_label = QtWidgets.QLabel("Frames Before and After")
        frame_range_label.setStyleSheet("QLabel { color: #FFFFFF; font-size: 8pt; background: transparent; }")
        frame_range_row.addWidget(frame_range_label)
        
        frame_range_row.addStretch()
        
        self.frame_range_combo = QtWidgets.QComboBox()
        self.frame_range_combo.setFixedWidth(scale_size(60))
        self.frame_range_combo.setCursor(QtCore.Qt.PointingHandCursor)
        self.frame_range_combo.setStyleSheet("""
            QComboBox {{
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-size: 8pt;
                border: {border}px solid #3D3D3D;
                border-radius: {radius}px;
                padding: {padding}px;
            }}
            QComboBox:hover {{
                border: {border}px solid #666666;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2D2D2D;
                color: #FFFFFF;
                selection-background-color: #3A7BD5;
            }}
        """.format(
            border=max(1, scale_size(1)),
            radius=scale_size(3),
            padding=scale_size(3)
        ))
        
        for option in FRAME_RANGE_OPTIONS:
            self.frame_range_combo.addItem(str(option), option)
        self.frame_range_combo.addItem("All", FRAME_RANGE_ALL_VALUE)
        
        saved_frame_range = load_frame_range()
        matched_index = self.frame_range_combo.findData(saved_frame_range)
        if matched_index < 0:
            matched_index = self.frame_range_combo.findData(FRAME_RANGE_DEFAULT)
        matched_index = matched_index if matched_index >= 0 else 0
        self.frame_range_combo.setCurrentIndex(matched_index)
        
        self.frame_range_combo.currentIndexChanged.connect(self.on_frame_range_changed)
        self.on_frame_range_changed(matched_index)
        frame_range_row.addWidget(self.frame_range_combo)
        
        main_layout.addLayout(frame_range_row)
        main_layout.addSpacing(scale_size(20))
        
        self.reset_button = QtWidgets.QPushButton("R E S E T   T O   D E F A U L T")
        self.reset_button.setFixedHeight(scale_size(28))
        self.reset_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #3D3D3D;
                color: #888888;
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 7pt;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
                color: #AAAAAA;
            }
            QPushButton:pressed {
                background-color: #1D1D1D;
            }
        """)
        self.reset_button.clicked.connect(self.reset_to_default)
        main_layout.addWidget(self.reset_button)
        
        main_layout.addSpacing(scale_size(20))
        main_layout.addStretch()
        
        # Restore saved color mode
        saved_mode = load_color_mode()
        if saved_mode > 0:
            for btn in self.gradient_buttons:
                if btn.property("colorMode") == saved_mode:
                    btn.setChecked(True)
                    break
    
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
        super(TracifyUI, self).resizeEvent(event)
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
    
    def apply_preset(self, trail_color, keys_color):
        self.trail_color = trail_color
        self.keys_color = keys_color
        save_custom_colors(trail_color, keys_color)
        # Turn off gradient mode when selecting a solid color preset
        self.clear_gradient_buttons()
        self.set_color_mode(0)
        self.update_tracify_colors()
        self.clear_focus()
    
    def set_gradient_mode(self, mode):
        """Set gradient mode and update button states"""
        # Uncheck other gradient buttons
        for btn in self.gradient_buttons:
            if btn.property("colorMode") != mode:
                btn.setChecked(False)
        
        # Find the clicked button
        clicked_btn = None
        for btn in self.gradient_buttons:
            if btn.property("colorMode") == mode:
                clicked_btn = btn
                break
        
        # Toggle behavior - if already checked, turn off
        if clicked_btn and clicked_btn.isChecked():
            self.set_color_mode(mode)
        else:
            self.set_color_mode(0)
        
        self.clear_focus()
    
    def clear_gradient_buttons(self):
        """Uncheck all gradient buttons"""
        for btn in self.gradient_buttons:
            btn.setChecked(False)
    
    def set_color_mode(self, mode):
        save_color_mode(mode)
        tracify = get_tracify()
        if tracify:
            try:
                tracify.setColorMode(mode)
            except Exception:
                pass
    
    def reset_to_default(self):
        """Reset all settings to default values"""
        # Reset colors to red preset (used if switching to solid)
        self.trail_color = (0.85, 0.12, 0.11)
        self.keys_color = (0.95, 0.45, 0.45)
        save_custom_colors(self.trail_color, self.keys_color)
        
        # Reset gradient buttons and set to rainbow
        self.clear_gradient_buttons()
        self.set_color_mode(1)  # Rainbow as default
        
        # Reset sliders and save defaults
        self.size_slider.setValue(5)
        self.line_slider.setValue(4)
        save_dot_size(5)
        save_line_width(4)
        
        # Reset camera space
        self.camera_space_checkbox.setChecked(False)
        save_camera_space(False)
        
        default_frame_range_index = self.frame_range_combo.findData(FRAME_RANGE_DEFAULT)
        if default_frame_range_index >= 0:
            self.frame_range_combo.setCurrentIndex(default_frame_range_index)
        save_frame_range(FRAME_RANGE_DEFAULT)
        
        # Apply to existing tracify nodes
        self.update_tracify_colors()
        
        tracify = get_tracify()
        if tracify:
            try:
                tracify.setPointSize(5.0)
                tracify.setLineWidth(4.0)
                tracify.setCameraSpace(False)
                tracify.setRange(FRAME_RANGE_DEFAULT)
            except Exception:
                pass
        
        self.clear_focus()
    
    def on_dot_size_changed(self, value):
        self.size_value_label.setText(str(value))
        save_dot_size(value)
        tracify = get_tracify()
        if tracify:
            try:
                tracify.POINT_SIZE = float(value)
                if tracify._isPluginLoaded():
                    nodes = cmds.ls(type="tracifyNode") or []
                    for node in nodes:
                        cmds.setAttr(node + ".pointSize", float(value))
                        cmds.dgdirty(node)
                    cmds.refresh(force=True)
            except Exception:
                pass
    
    def on_line_width_changed(self, value):
        self.line_value_label.setText(str(value))
        save_line_width(value)
        tracify = get_tracify()
        if tracify:
            try:
                tracify.LINE_WIDTH = float(value)
                if tracify._isPluginLoaded():
                    nodes = cmds.ls(type="tracifyNode") or []
                    for node in nodes:
                        cmds.setAttr(node + ".lineWidth", float(value))
                        cmds.dgdirty(node)
                    cmds.refresh(force=True)
            except Exception:
                pass
    
    def on_frame_range_changed(self, index):
        value = self.frame_range_combo.itemData(index)
        if value is None:
            return
        save_frame_range(value)
        tracify = get_tracify()
        if tracify:
            try:
                tracify.setRange(value)
            except Exception:
                pass
        self.clear_focus()
    
    def on_camera_space_changed(self, state):
        enabled = self.camera_space_checkbox.isChecked()
        save_camera_space(enabled)
        tracify = get_tracify()
        if tracify:
            try:
                tracify.setCameraSpace(enabled)
            except Exception:
                pass
        self.clear_focus()
    
    def update_tracify_colors(self):
        tracify = get_tracify()
        if tracify:
            try:
                tracify.COLORS[0] = self.trail_color
                tracify.KEY_COLOR = self.keys_color
                if hasattr(tracify, '_colorIndex'):
                    tracify._colorIndex = 0
                
                if tracify._isPluginLoaded():
                    nodes = cmds.ls(type="tracifyNode") or []
                    for node in nodes:
                        cmds.setAttr(node + ".lineColorR", self.trail_color[0])
                        cmds.setAttr(node + ".lineColorG", self.trail_color[1])
                        cmds.setAttr(node + ".lineColorB", self.trail_color[2])
                        cmds.setAttr(node + ".keyColorR", self.keys_color[0])
                        cmds.setAttr(node + ".keyColorG", self.keys_color[1])
                        cmds.setAttr(node + ".keyColorB", self.keys_color[2])
                    cmds.refresh()
            except Exception:
                pass
    
    def toggle_action(self):
        tracify = get_tracify()
        if tracify:
            cmds.undoInfo(openChunk=True, chunkName="Tracify Toggle")
            try:
                tracify.COLORS[0] = self.trail_color
                tracify.KEY_COLOR = self.keys_color
                point_size = float(self.size_slider.value())
                line_width = float(self.line_slider.value())
                frame_range_value = self.frame_range_combo.itemData(self.frame_range_combo.currentIndex())
                tracify.POINT_SIZE = point_size
                tracify.LINE_WIDTH = line_width
                tracify.CAMERA_SPACE = load_camera_space()
                if frame_range_value is not None:
                    tracify.FRAME_RANGE = frame_range_value
                tracify._colorIndex = 0
                tracify.t()
                
                # Apply saved color mode after creating
                saved_mode = load_color_mode()
                if saved_mode > 0:
                    tracify.setColorMode(saved_mode)
            except Exception:
                pass
            finally:
                cmds.undoInfo(closeChunk=True)
                self.clear_focus()
    
    def refresh_action(self):
        tracify = get_tracify()
        if tracify:
            try:
                tracify.r()
            except Exception:
                pass
            finally:
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
        super(TracifyUI, self).closeEvent(event)
    
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
        super(TracifyUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.fade_to(0.67, 300)
        super(TracifyUI, self).leaveEvent(event)


_tracify_ui_instance = None


def create_tracify_ui():
    global _tracify_ui_instance
    
    if _tracify_ui_instance is not None:
        try:
            _tracify_ui_instance.close()
            _tracify_ui_instance.deleteLater()
        except Exception:
            pass
        _tracify_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "TracifyUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    load_tracify_module()
    
    _tracify_ui_instance = TracifyUI()
    _tracify_ui_instance.show()
    return _tracify_ui_instance


def ui():
    return create_tracify_ui()


def track_arcs():
    tracify = get_tracify()
    if tracify:
        is_tracking = False
        try:
            is_tracking = bool(cmds.objExists(tracify.GROUP_NAME)) or (bool(cmds.ls(type="tracifyNode")) if tracify._isPluginLoaded() else False)
        except Exception:
            pass
        if not is_tracking and not cmds.ls(selection=True):
            cmds.inViewMessage(amg='<span style="font-size:12pt;">Please select something!</span>', pos='midCenter', fade=True)
            return
        cmds.undoInfo(openChunk=True, chunkName="Tracify Toggle")
        try:
            trail_color, keys_color = load_custom_colors()
            tracify.COLORS[0] = trail_color
            tracify.KEY_COLOR = keys_color
            tracify.POINT_SIZE = float(load_dot_size())
            tracify.LINE_WIDTH = float(load_line_width())
            tracify.CAMERA_SPACE = load_camera_space()
            tracify.FRAME_RANGE = load_frame_range()
            tracify._colorIndex = 0
            tracify.t()

            saved_mode = load_color_mode()
            if saved_mode > 0:
                tracify.setColorMode(saved_mode)
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)


def toggle_camera_space():
    enabled = not load_camera_space()
    save_camera_space(enabled)
    tracify = get_tracify()
    if tracify:
        try:
            tracify.setCameraSpace(enabled)
        except Exception:
            pass