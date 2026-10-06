import maya.OpenMayaUI as omui
import maya.cmds as cmds
import sys
import os
import platform
import time
import importlib
import json
import math

try:
    import __builtin__ as builtins
except ImportError:
    import builtins
try:
    max = builtins.max 
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass

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

IS_MACOS = platform.system() == "Darwin"

try:
    MAYA_VERSION = int(cmds.about(version=True))
except:
    MAYA_VERSION = 2020


def _resolve_animo_data_path():
    user_script_dir = cmds.internalVar(userScriptDir=True)
    direct_path = os.path.normpath(os.path.join(user_script_dir, "Animo_Data"))
    if os.path.isdir(direct_path):
        return direct_path
    fallback_dir = os.path.normpath(os.path.join(user_script_dir, "..", "..", "scripts"))
    return os.path.join(fallback_dir, "Animo_Data")


ANIMO_DATA_PATH = _resolve_animo_data_path()
if ANIMO_DATA_PATH not in sys.path:
    sys.path.insert(0, ANIMO_DATA_PATH)


for _mod_name in list(sys.modules.keys()):
    if 'Animo_Sliders' in _mod_name:
        del sys.modules[_mod_name]

from Animo_Sliders import slider_utils

SLIDER_MODULES = {}

BASE_DPI = 96.0
_scale_factor = None
_cursor_position = None

def get_scale_factor():
    global _scale_factor, _cursor_position
    
    try:
        current_cursor = QtGui.QCursor.pos()
        if _cursor_position is not None and _scale_factor is not None:
            if abs(current_cursor.x() - _cursor_position.x()) < 100 and \
               abs(current_cursor.y() - _cursor_position.y()) < 100:
                return _scale_factor
        _cursor_position = current_cursor
    except:
        if _scale_factor is not None:
            return _scale_factor
        current_cursor = None
    
    try:
        app = QtWidgets.QApplication.instance()
        raw_scale = 1.0
        
        if app:
            screen = None
            
            if PYSIDE_VERSION == 6:
                if current_cursor:
                    screen = app.screenAt(current_cursor)
                if not screen:
                    screen = QGuiApplication.primaryScreen()
            else:
                if current_cursor and hasattr(app, 'screenAt'):
                    screen = app.screenAt(current_cursor)
                if not screen and hasattr(app, 'primaryScreen'):
                    screen = app.primaryScreen()
            
            if screen:
                raw_scale = screen.logicalDotsPerInch() / BASE_DPI
            else:
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    raw_scale = desktop.logicalDpiX() / BASE_DPI
        
        _scale_factor = max(1.0, min(raw_scale, 3.0))
            
    except:
        _scale_factor = 1.0
    
    return _scale_factor

def reset_scale_factor():
    global _scale_factor, _cursor_position
    _scale_factor = None
    _cursor_position = None

def dpi(value):
    return int(value * get_scale_factor())

def scale_size(size):
    return dpi(size)

def copy_current_keyframe():
    current_time = cmds.currentTime(q=True)

    selection = cmds.ls(sl=True)
    if not selection:
        cmds.warning("No object selected.")
        return

    copy_data = []

    for obj in selection:
        anim_curves = cmds.listConnections(obj, type='animCurve', d=False, s=True) or []
        for curve in anim_curves:
            try:
                connections = cmds.listConnections(curve + ".output", plugs=True)
                if connections:
                    attr = connections[0]
                    value = cmds.getAttr(attr, time=current_time)
                    copy_data.append("{0}|{1}|{2}".format(attr, value, current_time))
            except:
                continue

    if copy_data:
        cmds.optionVar(stringArray=('tweenMachine_copyData', copy_data))
    else:
        cmds.warning("No animation data found to copy.")

try:
    long
except NameError:
    long = int

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is None:
        return None
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class CustomSlider(QtWidgets.QSlider):
    def __init__(self, label="EA", handle_color=(80, 200, 120), icon_color=(80, 200, 120), parent=None):
        super(CustomSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        
        self.label_text = label
        self.handle_color = QtGui.QColor(*handle_color)
        self.icon_color = QtGui.QColor(*icon_color)
        
        self.setMinimumHeight(dpi(21))
        self.setMaximumHeight(dpi(21))
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
    def setLabel(self, label):
        self.label_text = label
        self.update()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        icon_size = dpi(6)
        num_dots = 7
        total_items = num_dots + 2
        
        margin = dpi(8)
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
        dot_color.setAlpha(180)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        
        dot_spacing = (track_end - track_start) / (num_dots - 1)
        dot_radius = dpi(1.5)
        
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
        
        handle_size = dpi(22)
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
            
            icon_size = dpi(6)
            margin = dpi(8)
            icon_y = rect.height() // 2 - icon_size // 2
            
            left_icon_rect = QtCore.QRect(margin, icon_y, icon_size, icon_size)
            
            icon_right = rect.width() - margin - icon_size
            right_icon_rect = QtCore.QRect(icon_right, icon_y, icon_size, icon_size)
            
            if left_icon_rect.contains(click_pos):
                self.setValue(self.minimum())
                self.sliderReleased.emit()
                return
            
            if right_icon_rect.contains(click_pos):
                self.setValue(self.maximum())
                self.sliderReleased.emit()
                return
        
        QtWidgets.QSlider.mousePressEvent(self, event)



SLIDER_DEFS = [
    {"key": "tween", "name": "Tween", "tag": "TW", "color": (225, 175, 45), "module": "tween_slider", "min": -100, "max": 100, "start": 0},
    {"key": "blend", "name": "Blend to Neighbors", "tag": "BN", "color": (220, 140, 60), "module": "blend_slider", "min": -100, "max": 100, "start": 0},
    {"key": "scale_left", "name": "Scale Left", "tag": "SL", "color": (100, 180, 220), "module": "scale_slider", "mode": "left", "min": -100, "max": 100, "start": 0},
    {"key": "scale_right", "name": "Scale Right", "tag": "SR", "color": (70, 140, 220), "module": "scale_slider", "mode": "right", "min": -100, "max": 100, "start": 0},
    {"key": "scale_avg", "name": "Scale Average", "tag": "SA", "color": (120, 200, 200), "module": "scale_slider", "mode": "avg", "min": -100, "max": 100, "start": 0},
    {"key": "cascade", "name": "Connect to Neighbor", "tag": "CN", "color": (180, 120, 200), "module": "cascade_slider", "min": 0, "max": 200, "start": 100},
    {"key": "ease", "name": "Ease", "tag": "EA", "color": (80, 200, 120), "module": "ease_slider", "mode": "ease", "min": -100, "max": 100, "start": 0},
    {"key": "blend_default", "name": "Blend to Default", "tag": "BD", "color": (200, 100, 100), "module": "bd_slider", "min": -100, "max": 100, "start": 0},
    {"key": "blend_ease", "name": "Blend to Ease", "tag": "BE", "color": (235, 130, 170), "module": "be_slider", "min": -100, "max": 100, "start": 0},
    {"key": "blend_infinity", "name": "Blend to Infinity", "tag": "BI", "color": (150, 150, 235), "module": "bi_slider", "min": -100, "max": 100, "start": 0},
    {"key": "blend_mirror", "name": "Blend to Mirror", "tag": "BM", "color": (100, 210, 180), "module": "bm_slider", "min": -100, "max": 100, "start": 0},
    {"key": "blend_world", "name": "Blend to World", "tag": "BW", "color": (170, 205, 80), "module": "bw_slider", "min": -100, "max": 100, "start": 0},
    {"key": "wave_noise", "name": "Wave / Noise", "tag": "NW", "color": (240, 215, 120), "module": "nw_slider", "min": -100, "max": 100, "start": 0},
    {"key": "push_pull", "name": "Push / Pull", "tag": "PP", "color": (240, 100, 60), "module": "pp_slider", "min": -100, "max": 100, "start": 0},
    {"key": "simplify_bake", "name": "Simplify | Bake", "tag": "SB", "color": (170, 170, 170), "module": "sb_slider", "min": -100, "max": 100, "start": 0},
    {"key": "scale_default", "name": "Scale From Default", "tag": "SD", "color": (150, 190, 240), "module": "sd_slider", "min": -100, "max": 100, "start": 0},
    {"key": "smooth_harsh", "name": "Smooth | Harsh", "tag": "SH", "color": (210, 160, 235), "module": "sh_slider", "min": -100, "max": 100, "start": 0},
    {"key": "time_offset", "name": "Time Offset", "tag": "TO", "color": (230, 160, 110), "module": "to_slider", "min": -100, "max": 100, "start": 0},
    {"key": "time_stagger", "name": "Time Offset Stagger", "tag": "TS", "color": (190, 130, 90), "module": "ts_slider", "min": -100, "max": 100, "start": 0},
]

SLIDER_KEYS = [definition["key"] for definition in SLIDER_DEFS]
SLIDER_BY_KEY = dict((definition["key"], definition) for definition in SLIDER_DEFS)

DEFAULT_ENABLED = ["tween", "blend", "scale_left", "cascade"]
SETTINGS_FILE = os.path.join(ANIMO_DATA_PATH, "tweenify_settings.json")
SETTINGS_OPTION_VAR = "SimplifiedTweenUI_enabledSliders"
SETTINGS_MARKER = "__saved__"


def normalize_keys(keys):
    wanted = set(keys)
    return [key for key in SLIDER_KEYS if key in wanted]


def load_enabled_keys():
    try:
        with open(SETTINGS_FILE, "r") as handle:
            data = json.load(handle)
        return normalize_keys(data["enabled"])
    except Exception:
        pass
    try:
        if cmds.optionVar(exists=SETTINGS_OPTION_VAR):
            stored = cmds.optionVar(query=SETTINGS_OPTION_VAR)
            if not isinstance(stored, (list, tuple)):
                stored = [stored]
            if SETTINGS_MARKER in stored:
                return normalize_keys(stored)
    except Exception:
        pass
    return normalize_keys(DEFAULT_ENABLED)


def save_enabled_keys(keys):
    keys = normalize_keys(keys)
    try:
        folder = os.path.dirname(SETTINGS_FILE)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(SETTINGS_FILE, "w") as handle:
            json.dump({"enabled": keys}, handle, indent=2)
    except Exception:
        pass
    try:
        if cmds.optionVar(exists=SETTINGS_OPTION_VAR):
            cmds.optionVar(remove=SETTINGS_OPTION_VAR)
        cmds.optionVar(stringValueAppend=(SETTINGS_OPTION_VAR, SETTINGS_MARKER))
        for key in keys:
            cmds.optionVar(stringValueAppend=(SETTINGS_OPTION_VAR, key))
    except Exception:
        pass


def module_for(definition):
    name = definition["module"]
    if name not in SLIDER_MODULES:
        try:
            SLIDER_MODULES[name] = importlib.import_module("Animo_Sliders." + name)
        except Exception:
            SLIDER_MODULES[name] = None
    return SLIDER_MODULES[name]


def slider_logic_for(definition):
    module = module_for(definition)
    mode = definition.get("mode")
    if mode == "left":
        return lambda value, pressed, last, throttle: module.scale_left_logic(value, last, throttle)
    if mode == "right":
        return lambda value, pressed, last, throttle: module.scale_right_logic(value, last, throttle)
    if mode == "avg":
        return lambda value, pressed, last, throttle: module.scale_avg_logic(value, last, throttle)
    if mode == "ease":
        def ease_logic(value, pressed, last, throttle):
            module.update_ease(value)
            return last, "Ease: {0}".format(value)
        return ease_logic
    return module.slider_logic


def slider_reset_for(definition):
    module = module_for(definition)
    if definition.get("mode") == "ease":
        def ease_reset(widget):
            module.finish_ease()
            widget.blockSignals(True)
            widget.setValue(definition["start"])
            widget.blockSignals(False)
        return ease_reset
    return module.reset_slider


def slider_style(color):
    red, green, blue = color
    base = "#{0:02X}{1:02X}{2:02X}".format(red, green, blue)
    edge = "#{0:02X}{1:02X}{2:02X}".format(int(red * 0.78), int(green * 0.78), int(blue * 0.78))
    hover = "#{0:02X}{1:02X}{2:02X}".format(min(255, int(red * 1.15)), min(255, int(green * 1.15)), min(255, int(blue * 1.15)))
    style = """
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 6px;
            background: #3C3C3C;
            margin: 0px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: @BASE@;
            border: 1px solid @EDGE@;
            width: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }
        QSlider::handle:horizontal:hover {
            background: @HOVER@;
        }
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 @BASE@, stop: 1 #3C3C3C);
            border-radius: 3px;
        }
        QSlider::add-page:horizontal {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #3C3C3C, stop: 1 @BASE@);
            border-radius: 3px;
        }
    """
    return style.replace("@BASE@", base).replace("@EDGE@", edge).replace("@HOVER@", hover)


class StayOpenMenu(QtWidgets.QMenu):
    def mouseReleaseEvent(self, event):
        if hasattr(event, 'position'):
            point = event.position().toPoint()
        else:
            point = event.pos()
        action = self.actionAt(point)
        if action is not None and action.isCheckable() and action.isEnabled():
            action.trigger()
            self.update()
            return
        QtWidgets.QMenu.mouseReleaseEvent(self, event)


class SimplifiedTweenUI(QtWidgets.QDialog):
    option_var_name = "SimplifiedTweenUI_lastPos"

    def __init__(self, parent=get_maya_main_window()):
        QtWidgets.QDialog.__init__(self, parent)

        if IS_MACOS:
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.Window |
                QtCore.Qt.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.Window
            )

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.69)

        self.pad = dpi(5)
        self.top_inset = dpi(14)
        self.cell_w = dpi(161)
        self.col_gap = dpi(10)
        self.row_gap = dpi(3)
        self.label_h = dpi(14)
        self.slider_h = dpi(20)
        self.inner_gap = dpi(2)
        self.status_h = dpi(12)
        self.block_h = self.label_h + self.inner_gap + self.slider_h

        self.pressed = dict((key, False) for key in SLIDER_KEYS)
        self.cursor_restore = dict((key, False) for key in SLIDER_KEYS)
        self.widgets = {}
        self.enabled_keys = load_enabled_keys()
        self._menu_open = False
        self.old_pos = None
        self.last_update_time = 0
        self.update_throttle_ms = 1

        self.maya_main_window = get_maya_main_window()

        self.build_ui()
        self.apply_dark_theme()
        self.layout_sliders()

        self._outside_count = 0
        self._background_check_timer = QtCore.QTimer()
        self._background_check_timer.timeout.connect(self._background_mouse_check)
        self._background_check_timer.start(100)

    def closeEvent(self, event):
        if hasattr(self, '_background_check_timer') and self._background_check_timer.isActive():
            self._background_check_timer.stop()
        QtWidgets.QDialog.closeEvent(self, event)

    def check_mouse_position(self):
        return

    def any_pressed(self):
        return any(self.pressed.values())

    def _background_mouse_check(self):
        if self._menu_open or self.any_pressed():
            self._outside_count = 0
            return

        cursor_pos = QtGui.QCursor.pos()
        widget_rect = self.geometry()

        tolerance = scale_size(20)
        expanded_rect = widget_rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)

        if not expanded_rect.contains(cursor_pos):
            self._outside_count += 1

            if self._outside_count >= 2:
                self._background_check_timer.stop()
                self.close()
        else:
            self._outside_count = 0

    def force_deactivate_window(self):
        if self._menu_open or self.any_pressed():
            return
        self.close()

    def build_ui(self):
        self.frame = QtWidgets.QFrame(self)
        self.frame.setStyleSheet("background-color: rgba(46, 46, 46, 253); border-radius: 15px;")
        self.frame.setMouseTracking(True)

        self.status_label = QtWidgets.QLabel("", self.frame)
        self.status_label.setStyleSheet("font-size: 7pt; color: #BBBBBB; background-color: transparent;")
        self.status_label.setMouseTracking(True)

        self.setMouseTracking(True)

    def widgets_for(self, key):
        pair = self.widgets.get(key)
        if pair is not None:
            return pair

        definition = SLIDER_BY_KEY[key]
        color = definition["color"]

        label = QtWidgets.QLabel("{0}:".format(definition["name"]), self.frame)
        label.setStyleSheet("font-size: 8pt; background-color: transparent;")
        label.setFixedSize(self.cell_w, self.label_h)
        label.setMouseTracking(True)

        slider = CustomSlider(definition["tag"], color, color, self.frame)
        slider.setMinimum(definition["min"])
        slider.setMaximum(definition["max"])
        slider.setValue(definition["start"])
        slider.setFixedSize(self.cell_w, self.slider_h)
        slider.setStyleSheet(slider_style(color))
        slider.setProperty("slider_key", key)
        slider.setMouseTracking(True)
        slider.valueChanged.connect(lambda value, k=key: self.slider_changed(k, value))
        slider.installEventFilter(self)

        self.widgets[key] = (label, slider)
        return label, slider

    def active_keys(self):
        return [key for key in self.enabled_keys if module_for(SLIDER_BY_KEY[key]) is not None]

    def column_count(self, count):
        if count <= 1:
            return 1
        cell = self.cell_w + self.col_gap
        row = self.block_h + self.row_gap
        columns = int(round(math.sqrt(count * row / float(cell) * 2.0)))
        geometry = self.available_geometry(QtGui.QCursor.pos())
        if geometry is not None:
            max_columns = max(1, int((geometry.width() - self.pad * 2 + self.col_gap) // cell))
            max_rows = max(1, int((geometry.height() - dpi(80) + self.row_gap) // row))
            columns = max(columns, int(math.ceil(count / float(max_rows))))
            columns = min(columns, max_columns)
        columns = max(1, min(columns, count))
        rows = int(math.ceil(count / float(columns)))
        return int(math.ceil(count / float(rows)))

    def layout_sliders(self):
        active = self.active_keys()
        count = len(active)
        columns = self.column_count(count)
        rows = int(math.ceil(count / float(columns))) if count else 0

        full_w = columns * self.cell_w + (columns - 1) * self.col_gap
        width = self.pad * 2 + full_w
        if rows:
            rows_h = rows * self.block_h + (rows - 1) * self.row_gap
            status_y = self.top_inset + rows_h + self.row_gap * 2
        else:
            status_y = self.top_inset
        height = max(status_y + self.status_h + self.pad, dpi(40))

        shown = set(active)
        for key, pair in self.widgets.items():
            if key not in shown:
                pair[0].hide()
                pair[1].hide()

        for index, key in enumerate(active):
            row = index // columns
            column = index % columns
            in_row = min(columns, count - row * columns)
            row_w = in_row * self.cell_w + (in_row - 1) * self.col_gap
            x = self.pad + (full_w - row_w) // 2 + column * (self.cell_w + self.col_gap)
            y = self.top_inset + row * (self.block_h + self.row_gap)
            label, slider = self.widgets_for(key)
            label.move(x, y)
            slider.move(x, y + self.label_h + self.inner_gap)
            label.show()
            slider.show()

        self.status_label.setGeometry(self.pad, status_y, width - self.pad * 2, self.status_h)
        self.apply_size(width, height)

    def apply_size(self, width, height):
        center = self.geometry().center() if self.isVisible() else None
        self.setFixedSize(width, height)
        self.frame.setGeometry(0, 0, width, height)
        if center is not None:
            self.move(center.x() - width // 2, center.y() - height // 2)
            self.keep_on_screen()
        self.update()

    def available_geometry(self, point):
        try:
            screen = QGuiApplication.screenAt(point)
            if screen:
                return screen.availableGeometry()
        except Exception:
            pass
        try:
            return QtWidgets.QApplication.desktop().availableGeometry(point)
        except Exception:
            return None

    def keep_on_screen(self):
        geometry = self.available_geometry(self.geometry().center())
        if geometry is None:
            return
        x = max(min(self.x(), geometry.right() - self.width() + 1), geometry.left())
        y = max(min(self.y(), geometry.bottom() - self.height() + 1), geometry.top())
        self.move(x, y)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog { 
                background-color: transparent;
            }
        """)

    def enterEvent(self, event):
        if hasattr(self, '_outside_count'):
            self._outside_count = 0
        QtWidgets.QDialog.enterEvent(self, event)

    def leaveEvent(self, event):
        if self._menu_open or self.any_pressed():
            QtWidgets.QDialog.leaveEvent(self, event)
            return

        delay = 10 if IS_MACOS else 1
        QtCore.QTimer.singleShot(delay, self.force_deactivate_window)
        QtWidgets.QDialog.leaveEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'globalPosition'):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            if hasattr(event, 'globalPosition'):
                self.show_context_menu(event.globalPosition().toPoint())
            else:
                self.show_context_menu(event.globalPos())

    def show_context_menu(self, pos):
        menu = StayOpenMenu(self)

        menu_style = """
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                padding: @PAD@px;
            }
            QMenu::item {
                background-color: transparent;
                color: #cccccc;
                padding: @ITEM_V@px @ITEM_R@px @ITEM_V@px @ITEM_L@px;
                border-radius: @ITEM_RAD@px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #6a6a6a;
            }
            QMenu::indicator {
                width: @BOX@px;
                height: @BOX@px;
                left: @BOX_LEFT@px;
            }
            QMenu::indicator:non-exclusive:unchecked {
                border: 1px solid #666666;
                border-radius: @BOX_RAD@px;
                background-color: transparent;
            }
            QMenu::indicator:non-exclusive:checked {
                border: 1px solid #B08A24;
                border-radius: @BOX_RAD@px;
                background-color: #E1AF2D;
            }
        """
        for token, value in (("@PAD@", dpi(4)), ("@ITEM_V@", dpi(5)), ("@ITEM_R@", dpi(22)),
                             ("@ITEM_L@", dpi(30)), ("@ITEM_RAD@", dpi(3)), ("@BOX@", dpi(12)),
                             ("@BOX_LEFT@", dpi(8)), ("@BOX_RAD@", dpi(2))):
            menu_style = menu_style.replace(token, str(value))
        menu.setStyleSheet(menu_style)

        for definition in SLIDER_DEFS:
            action = menu.addAction(definition["name"])
            action.setCheckable(True)
            action.setChecked(definition["key"] in self.enabled_keys)
            action.setEnabled(module_for(definition) is not None)
            action.toggled.connect(lambda checked, k=definition["key"]: self.set_slider_enabled(k, checked))

        self._menu_open = True
        try:
            if PYSIDE_VERSION >= 6:
                getattr(menu, 'exec')(pos)
            else:
                menu.exec_(pos)
        finally:
            self._menu_open = False
            self._outside_count = 0

    def set_slider_enabled(self, key, enabled):
        wanted = set(self.enabled_keys)
        if enabled:
            wanted.add(key)
        else:
            wanted.discard(key)
        self.enabled_keys = normalize_keys(wanted)
        save_enabled_keys(self.enabled_keys)
        self.layout_sliders()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, 'globalPosition'):
                current_pos = event.globalPosition().toPoint()
            else:
                current_pos = event.globalPos()

            delta = current_pos - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = current_pos

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ControlModifier:
            self.execute_copy_with_undo()
        elif event.key() == QtCore.Qt.Key_V and event.modifiers() == QtCore.Qt.ControlModifier:
            self.execute_paste_with_undo()
        QtWidgets.QDialog.keyPressEvent(self, event)

    def eventFilter(self, obj, event):
        key = obj.property("slider_key")
        if not key:
            return False

        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() != QtCore.Qt.LeftButton:
                return False

            self.pressed[key] = True

            getCurves = slider_utils.get_anim_curves()
            anim_curves = getCurves[0]
            if anim_curves and len(anim_curves) > 400:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                self.cursor_restore[key] = True
            else:
                self.cursor_restore[key] = False

            return False
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() != QtCore.Qt.LeftButton:
                return False

            self.pressed[key] = False
            release_delay = 100 if IS_MACOS else 50
            QtCore.QTimer.singleShot(release_delay, lambda k=key: self.slider_released(k))
            return False
        return False

    def slider_changed(self, key, value):
        if not self.pressed.get(key):
            return
        logic = slider_logic_for(SLIDER_BY_KEY[key])
        self.last_update_time, status = logic(
            value, True, self.last_update_time, self.update_throttle_ms)
        if status:
            self.status_label.setText(status)

    def slider_released(self, key):
        if self.pressed.get(key):
            return
        pair = self.widgets.get(key)
        if pair is not None:
            slider_reset_for(SLIDER_BY_KEY[key])(pair[1])
        if self.cursor_restore.get(key):
            QtWidgets.QApplication.restoreOverrideCursor()
            self.cursor_restore[key] = False

def toggle_simplified_tween_ui():
    global simplified_tween_ui
    
    try:
        if simplified_tween_ui.isVisible():
            return
    except:
        pass
    
    try:
        simplified_tween_ui.close()
        simplified_tween_ui.deleteLater()
    except:
        pass
    
    reset_scale_factor()
    
    cursor_pos = QtGui.QCursor.pos()
    
    simplified_tween_ui = SimplifiedTweenUI()
    
    ui_x = cursor_pos.x() - simplified_tween_ui.width() // 2
    ui_y = cursor_pos.y() - simplified_tween_ui.height() // 2 + dpi(6)
    
    simplified_tween_ui.move(ui_x, ui_y)
    simplified_tween_ui.keep_on_screen()
    simplified_tween_ui.show()

toggle_simplified_tween_ui()