import os
import sys
import json
import time
import types

ANIMO_ENABLE_GRAPH_EDITOR_IDLE_JOB = True

ANIMO_ENABLE_GE_TOOL_RESET_POSE = True
ANIMO_ENABLE_GE_TOOL_FAST_BAKE = True
ANIMO_ENABLE_GE_TOOL_SMOOTH_KEYS = True
ANIMO_ENABLE_GE_TOOL_DELETE_REDUNDANT_KEYS = True
ANIMO_ENABLE_GE_TOOL_SNAP_KEYS = True

ANIMO_ENABLE_GE_SLIDER_TW = True
ANIMO_ENABLE_GE_SLIDER_BN = True
ANIMO_ENABLE_GE_SLIDER_BD = True
ANIMO_ENABLE_GE_SLIDER_CN = True
ANIMO_ENABLE_GE_SLIDER_SL = True
ANIMO_ENABLE_GE_SLIDER_SR = True
ANIMO_ENABLE_GE_SLIDER_SA = True
ANIMO_ENABLE_GE_SLIDER_SD = True
ANIMO_ENABLE_GE_SLIDER_BW = True
ANIMO_ENABLE_GE_SLIDER_EA = True
ANIMO_ENABLE_GE_SLIDER_BE = True
ANIMO_ENABLE_GE_SLIDER_TO = True
ANIMO_ENABLE_GE_SLIDER_TS = True
ANIMO_ENABLE_GE_SLIDER_NW = True
ANIMO_ENABLE_GE_SLIDER_PP = True
ANIMO_ENABLE_GE_SLIDER_SH = True
ANIMO_ENABLE_GE_SLIDER_SB = True
ANIMO_ENABLE_GE_SLIDER_BI = True
ANIMO_ENABLE_GE_SLIDER_BM = True

_GE_SLIDER_FLAGS = {
    "TW": "ANIMO_ENABLE_GE_SLIDER_TW", "BN": "ANIMO_ENABLE_GE_SLIDER_BN",
    "BD": "ANIMO_ENABLE_GE_SLIDER_BD", "CN": "ANIMO_ENABLE_GE_SLIDER_CN",
    "SL": "ANIMO_ENABLE_GE_SLIDER_SL", "SR": "ANIMO_ENABLE_GE_SLIDER_SR",
    "SA": "ANIMO_ENABLE_GE_SLIDER_SA", "SD": "ANIMO_ENABLE_GE_SLIDER_SD",
    "BW": "ANIMO_ENABLE_GE_SLIDER_BW", "EA": "ANIMO_ENABLE_GE_SLIDER_EA",
    "BE": "ANIMO_ENABLE_GE_SLIDER_BE", "TO": "ANIMO_ENABLE_GE_SLIDER_TO",
    "TS": "ANIMO_ENABLE_GE_SLIDER_TS", "NW": "ANIMO_ENABLE_GE_SLIDER_NW",
    "PP": "ANIMO_ENABLE_GE_SLIDER_PP", "SH": "ANIMO_ENABLE_GE_SLIDER_SH",
    "SB": "ANIMO_ENABLE_GE_SLIDER_SB", "BI": "ANIMO_ENABLE_GE_SLIDER_BI",
    "BM": "ANIMO_ENABLE_GE_SLIDER_BM",
}


def _ge_slider_enabled(label):
    flag_name = _GE_SLIDER_FLAGS.get(label)
    if flag_name is None:
        return False
    return globals().get(flag_name, False)


import maya.cmds as cmds
import maya.OpenMayaUI as mui

try:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance, isValid
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance, isValid

try:
    QAction = QtWidgets.QAction
except AttributeError:
    QAction = QtGui.QAction


OUTER_LAYOUT_NAME = "animoGraph_columnLayout"
PREFS_FILE_NAME = "graph_editor_sliders.json"
TOOLBAR_PREFS_FILE_NAME = "graph_editor_toolbar_enabled.json"
TOOLS_PREFS_FILE_NAME = "graph_editor_tools.json"
ROW_ORDER_PREFS_FILE_NAME = "graph_editor_row_order.json"
DEFAULT_ENABLED = ["TW", "TO", "BD"]
DEFAULT_TOOLS_ENABLED = []
ROW_BOTTOM_MARGIN = 4
OVERSHOOT_RANGE_RATIO = 0.3
PLACEHOLDER_WIDTH = 156
PLACEHOLDER_HEIGHT = 27

SLIDER_CATALOG = [
    ("TW", (225, 175, 45), "tween_slider"),
    ("BN", (220, 140, 60), "blend_slider"),
    ("BD", (157, 164, 231), "bd_slider"),
    ("CN", (205, 147, 230), "cn_cascade_adapter"),
    ("SL", (100, 180, 220), "scale_left_adapter"),
    ("SR", (113, 167, 214), "scale_right_adapter"),
    ("SA", (131, 158, 216), "scale_avg_adapter"),
    ("SD", (145, 161, 224), "sd_slider"),
    ("BW", (180, 120, 200), "bw_slider"),
    ("EA", (92, 184, 214), "ease_adapter"),
    ("BE", (100, 192, 218), "be_slider"),
    ("TO", (150, 135, 222), "to_slider"),
    ("TS", (163, 133, 226), "ts_slider"),
    ("NW", (178, 140, 227), "nw_slider"),
    ("PP", (84, 206, 212), "pp_slider"),
    ("SH", (212, 144, 228), "sh_slider"),
    ("SB", (218, 142, 226), "sb_slider"),
    ("BI", (224, 140, 224), "bi_slider"),
    ("BM", (230, 138, 205), "bm_slider"),
]

SLIDER_TOOLTIP_KEYS = {
    "TW": "tween_slider",
    "BN": "blend_slider",
    "SL": "scale_slider",
    "BW": "blend_world_slider",
    "EA": "ease_slider",
    "BE": "blend_ease_slider",
    "SR": "scale_right_slider",
    "SA": "scale_avg_slider",
    "SD": "scale_default_slider",
    "BD": "blend_default_slider",
    "TO": "time_offset_slider",
    "NW": "noise_wave_slider",
    "CN": "cascade_slider",
    "PP": "push_pull_slider",
    "TS": "time_offset_stagger_slider",
    "SH": "smooth_harsh_slider",
    "SB": "simplify_bake_slider",
    "BI": "blend_infinity_slider",
    "BM": "blend_mirror_slider",
}

SLIDER_DISPLAY_NAMES = {
    "TW": "Tween Machine",
    "BN": "Blend to Neighbour",
    "SL": "Scale from Left",
    "BW": "Blend to World",
    "EA": "Ease",
    "BE": "Blend to Ease",
    "SR": "Scale from Right",
    "SA": "Scale from Average",
    "SD": "Scale from Default",
    "BD": "Blend to Default",
    "TO": "Time Offset",
    "TS": "Time Offset Stagger",
    "NW": "Noise / Wave",
    "CN": "Connect to Neighbour",
    "PP": "Push / Pull",
    "SH": "Smooth | Harsh",
    "SB": "Simplify | Bake",
    "BI": "Blend to Infinity",
    "BM": "Blend to Mirror",
}

TOOL_CATALOG = [
    {
        "key": "ResetPose",
        "label": "Reset Pose",
        "icon_file": "reset_icon.png",
        "icon_root": "icons",
        "size": (23, 23),
        "launcher_name": "reset_pose_launcher",
        "tool_folder": None,
        "bake_menu": None,
        "special": None,
        "tooltip_key": "reset_pose_launcher",
    },
    {
        "key": "FastBake",
        "label": "Fast Bake",
        "icon_file": "bake_icon.png",
        "icon_root": "icons",
        "size": (23, 23),
        "launcher_name": None,
        "tool_folder": None,
        "special": None,
        "tooltip_key": "fast_bake_launcher",
        "bake_menu": [
            ("Bake - 7s", "fast_bake_7s", "Animo_Fast_Bake"),
            ("Bake - 6s", "fast_bake_6s", "Animo_Fast_Bake"),
            ("Bake - 5s", "fast_bake_5s", "Animo_Fast_Bake"),
            ("Bake - 4s", "fast_bake_4s", "Animo_Fast_Bake"),
            ("Bake - 3s", "fast_bake_3s", "Animo_Fast_Bake"),
            ("Bake - 2s", "fast_bake_2s", "Animo_Fast_Bake"),
            ("Bake - 1s", "fast_bake_1s", "Animo_Fast_Bake"),
        ],
    },
    {
        "key": "SmoothSelectedKeys",
        "label": "Smooth Selected Keys",
        "icon_file": "SmoothSelectedKeys.png",
        "icon_root": "tool",
        "tool_folder": "Animo_Tools_Editor/animo_tools/tools",
        "size": (20, 20),
        "launcher_name": None,
        "bake_menu": None,
        "special": "smooth_keys",
        "tooltip_key": "SmoothSelectedKeys",
    },
    {
        "key": "DeleteRedundantKeys",
        "label": "Delete Redundant Keys",
        "icon_file": "DeleteRedundantKeys.png",
        "icon_root": "tool",
        "tool_folder": "Animo_Tools_Editor/animo_tools/tools",
        "size": (20, 20),
        "launcher_name": "DeleteRedundantKeys",
        "bake_menu": None,
        "special": None,
        "tooltip_key": "DeleteRedundantKeys",
    },
    {
        "key": "SnapKeys",
        "label": "Snap Keys",
        "icon_file": "SmartSnapKeys.png",
        "icon_root": "tool",
        "tool_folder": "Animo_Tools_Editor/animo_tools/tools",
        "size": (20, 20),
        "launcher_name": "SmartSnapKeys",
        "bake_menu": None,
        "special": None,
        "tooltip_key": "SmartSnapKeys",
    },
]

_slider_modules = {}
_bar_module = None
_style_module = None
_tooltip_manager = None


                                                                             
                               
 
                                                                        
                                                                            
                                                                          
                                                                         
                                                                          
                                                                            
                                                                        
 
                                                                         
                                                                            
                                                                          
                                                                       
                                             
                                                                             

_SHARED_STATE_PROPERTY = "_animoGraphSliderMod_sharedState"
_fallback_shared_state = None


class _SharedRowState(object):

    def __init__(self):
        self.qt_poll_timer = None
        self.outer_widget = None
        self.flow_widget = None
        self.flow_layout = None
        self.current_panel_name = None
        self.ensure_row_lock = False
        self.row_order = []
        self.active_widgets = {}
        self.active_wrappers = {}
        self.active_tools = {}
        self.last_idle_check_time = 0.0
        self.last_rebuild_time = 0.0
        self.rebuild_backoff = REBUILD_MIN_INTERVAL
        self.rebuild_scheduled = False
        self.healthy_since = 0.0
        self.unhealthy_strikes = 0


def _get_shared_state():
    global _fallback_shared_state
    try:
        app = QtWidgets.QApplication.instance()
    except Exception:
        app = None
    if app is None:
                                                                           
                                                                         
                                                                   
                              
        if _fallback_shared_state is None:
            _fallback_shared_state = _SharedRowState()
        return _fallback_shared_state
    state = getattr(app, _SHARED_STATE_PROPERTY, None)
    if state is None:
        state = _SharedRowState()
        try:
            setattr(app, _SHARED_STATE_PROPERTY, state)
        except Exception:
                                                                       
                                                                       
            _fallback_shared_state = state
    return state


class _SharedRowStateProxy(object):

    def __getattr__(self, name):
        return getattr(_get_shared_state(), name)

    def __setattr__(self, name, value):
        setattr(_get_shared_state(), name, value)


_S = _SharedRowStateProxy()


class FlowLayout(QtWidgets.QLayout):

    def __init__(self, parent=None, margin=0, hspacing=6, vspacing=4):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return False

    def heightForWidth(self, width):
        return self._do_layout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        available_width = effective_rect.width()

        lines = []
        current_line = []
        current_width = 0

        for item in self._items:
            item_size = item.sizeHint()
            added_width = item_size.width() if not current_line else item_size.width() + self._hspacing
            if current_line and current_width + added_width > available_width:
                lines.append(current_line)
                current_line = []
                current_width = 0
                added_width = item_size.width()
            current_line.append((item, item_size))
            current_width += added_width

        if current_line:
            lines.append(current_line)

        y = effective_rect.y()
        for line in lines:
            line_width = 0
            line_height = 0
            for index, (item, item_size) in enumerate(line):
                line_width += item_size.width()
                if index > 0:
                    line_width += self._hspacing
                line_height = max(line_height, item_size.height())

            offset_x = effective_rect.x() + max(0.0, (available_width - line_width) / 2.0)
            x = offset_x
            for item, item_size in line:
                if not test_only:
                    item.setGeometry(QtCore.QRect(QtCore.QPoint(int(round(x)), int(round(y))), item_size))
                x += item_size.width() + self._hspacing
            y += line_height + self._vspacing

        if lines:
            y -= self._vspacing

        return y - effective_rect.y() + top + bottom


class _FlowContainer(QtWidgets.QWidget):

    def resizeEvent(self, event):
        super(_FlowContainer, self).resizeEvent(event)
        layout = self.layout()
        if layout is None:
            return
        target_height = layout.heightForWidth(self.width())
        if target_height > 0 and self.height() != target_height:
            self.setFixedHeight(target_height)


def get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


def get_prefs_path():
    animo_data = get_animo_data_path()
    prefs_dir = os.path.join(animo_data, "Animo_Prefs")
    if not os.path.exists(prefs_dir):
        try:
            os.makedirs(prefs_dir)
        except:
            pass
    return prefs_dir


def get_prefs_file():
    return os.path.join(get_prefs_path(), PREFS_FILE_NAME)


def load_enabled_labels():
    prefs_file = get_prefs_file()
    try:
        with open(prefs_file, "r") as f:
            data = json.load(f)
        return list(data.get("enabled", DEFAULT_ENABLED))
    except:
        return list(DEFAULT_ENABLED)


def save_enabled_labels(labels):
    prefs_file = get_prefs_file()
    try:
        with open(prefs_file, "w") as f:
            json.dump({"enabled": labels}, f)
    except:
        pass


def get_toolbar_prefs_file():
    return os.path.join(get_prefs_path(), TOOLBAR_PREFS_FILE_NAME)


_toolbar_enabled_cache = None


def is_toolbar_enabled():
    global _toolbar_enabled_cache
    if _toolbar_enabled_cache is not None:
        return _toolbar_enabled_cache
    prefs_file = get_toolbar_prefs_file()
    try:
        with open(prefs_file, "r") as f:
            data = json.load(f)
        _toolbar_enabled_cache = bool(data.get("enabled", False))
    except:
        _toolbar_enabled_cache = False
    return _toolbar_enabled_cache


def set_toolbar_enabled(enabled):
    global _toolbar_enabled_cache
    prefs_file = get_toolbar_prefs_file()
    _toolbar_enabled_cache = bool(enabled)
    try:
        with open(prefs_file, "w") as f:
            json.dump({"enabled": bool(enabled)}, f)
    except:
        pass


def get_tools_prefs_file():
    return os.path.join(get_prefs_path(), TOOLS_PREFS_FILE_NAME)


def load_enabled_tools():
    prefs_file = get_tools_prefs_file()
    try:
        with open(prefs_file, "r") as f:
            data = json.load(f)
        return list(data.get("enabled", DEFAULT_TOOLS_ENABLED))
    except:
        return list(DEFAULT_TOOLS_ENABLED)


def save_enabled_tools(keys):
    prefs_file = get_tools_prefs_file()
    try:
        with open(prefs_file, "w") as f:
            json.dump({"enabled": keys}, f)
    except:
        pass


def get_row_order_prefs_file():
    return os.path.join(get_prefs_path(), ROW_ORDER_PREFS_FILE_NAME)


def load_row_order():
    prefs_file = get_row_order_prefs_file()
    try:
        with open(prefs_file, "r") as f:
            data = json.load(f)
        order = data.get("order", [])
        result = []
        for entry in order:
            item_type = entry.get("type")
            item_key = entry.get("key")
            if item_type in ("slider", "tool") and item_key:
                result.append((item_type, item_key))
        return result
    except:
        return None


def save_row_order(order):
    prefs_file = get_row_order_prefs_file()
    try:
        with open(prefs_file, "w") as f:
            json.dump({"order": [{"type": t, "key": k} for (t, k) in order]}, f)
    except:
        pass


def get_icons_path():
    return os.path.join(get_animo_data_path(), "Animo_Launcher")


def get_maya_version():
    try:
        return int(cmds.about(version=True)[:4])
    except:
        return 0


def register_bar_module(bar_module):
    global _bar_module
    _bar_module = bar_module


def register_style_module(style_module):
    global _style_module
    _style_module = style_module


def register_tooltip_manager(manager):
    global _tooltip_manager
    _tooltip_manager = manager


def _register_tooltip(widget, tooltip_key, icon_path=None, hover_delay=None):
    if _tooltip_manager is None or tooltip_key is None:
        return
    try:
        if hover_delay is not None:
            _tooltip_manager.register_button(widget, tooltip_key, icon_path, hover_delay=hover_delay)
        else:
            _tooltip_manager.register_button(widget, tooltip_key, icon_path)
    except:
        pass


def _unregister_tooltip(widget):
    if _tooltip_manager is None:
        return
    try:
        _tooltip_manager.unregister_button(widget)
    except:
        pass


def _scaled(px):
    if _style_module is not None and hasattr(_style_module, "scaled"):
        try:
            return _style_module.scaled(px)
        except:
            return px
    return px


MENU_SIZE_BOOST = 1.1


def _menu_scaled(px):
    return int(round(_scaled(px) * MENU_SIZE_BOOST))


def _animo_menu_qss(with_indicator=True):
    pad_v = _menu_scaled(6)
    pad_h = _menu_scaled(25)
    ind = _menu_scaled(13)
    lines = []
    lines.append("QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }")
    lines.append("QMenu::item { padding: " + str(pad_v) + "px " + str(pad_h) + "px; color: #ccc; }")
    lines.append("QMenu::item:selected { background-color: #555; color: #fff; }")
    if with_indicator:
        lines.append("QMenu::indicator { width: " + str(ind) + "px; height: " + str(ind) + "px; }")
        lines.append("QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }")
        lines.append("QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }")
    return "\n".join(lines)


def is_tool_enabled(key):
    return key in _S.active_tools


def _tool_catalog_entry(key):
    for entry in TOOL_CATALOG:
        if entry["key"] == key:
            return entry
    return None


def _tool_icon_path(entry):
    if entry["icon_root"] == "tool":
        return os.path.join(get_animo_data_path(), entry["tool_folder"], entry["icon_file"])
    return os.path.join(get_icons_path(), entry["icon_file"])


def _run_tool_action(launcher_name, tool_folder):
    if launcher_name == "reset_pose_launcher":
        if not ANIMO_ENABLE_GE_TOOL_RESET_POSE:
            return
    elif launcher_name and launcher_name.startswith("fast_bake_"):
        if not ANIMO_ENABLE_GE_TOOL_FAST_BAKE:
            return
    elif launcher_name == "DeleteRedundantKeys":
        if not ANIMO_ENABLE_GE_TOOL_DELETE_REDUNDANT_KEYS:
            return
    elif launcher_name == "SmartSnapKeys":
        if not ANIMO_ENABLE_GE_TOOL_SNAP_KEYS:
            return
    else:
        return
    if _bar_module is None:
        cmds.warning("Animo bar module is not registered with graphSliderMod.")
        return
    _bar_module.run_launcher(
        get_animo_data_path(), get_icons_path(), get_maya_version(), launcher_name, tool_folder, None
    )


def _run_smooth_selected_keys():
    if not ANIMO_ENABLE_GE_TOOL_SMOOTH_KEYS:
        return
    plugin_name = "AnimoSmoothKeysPlugin"
    plugin_folder = os.path.join(get_animo_data_path(), "Animo_Tools_Editor", "animo_tools", "tools")
    is_loaded = False
    try:
        is_loaded = cmds.pluginInfo(plugin_name, query=True, loaded=True)
    except:
        pass
    if not is_loaded:
        plugin_path = None
        for ext in [".py", ".pyc"]:
            potential_path = os.path.join(plugin_folder, plugin_name + ext)
            if os.path.exists(potential_path):
                plugin_path = potential_path
                break
        if plugin_path:
            try:
                cmds.loadPlugin(plugin_path)
            except Exception as e:
                cmds.warning("Failed to load AnimoSmoothKeysPlugin: {0}".format(e))
                return
        else:
            cmds.warning("AnimoSmoothKeysPlugin not found in: {0}".format(plugin_folder))
            return
    try:
        cmds.smoothKeysAPI(strength=0.5, iterations=1)
    except Exception as e:
        cmds.warning("Failed to run smoothKeysAPI: {0}".format(e))


def _make_tool_button(entry, parent):
    icon_path = _tool_icon_path(entry)
    icon_w = _scaled(entry["size"][0])
    icon_h = _scaled(entry["size"][1])

    btn = QtWidgets.QPushButton(parent)
    btn.setFixedSize(icon_w + 3, icon_h + 3)
    btn.setIcon(QtGui.QIcon(icon_path))
    btn.setIconSize(QtCore.QSize(icon_w, icon_h))
    btn.setToolTip(entry["label"])
    btn.setFlat(True)
    btn.setStyleSheet('''
        QPushButton { border: none; background: transparent; }
        QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 5px; }
        QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 5px; }
        QPushButton::menu-indicator { width: 0; height: 0; }
    ''')

    if entry.get("bake_menu"):
        menu = QtWidgets.QMenu(btn)
        menu.setStyleSheet(_animo_menu_qss(with_indicator=False))
        for bake_label, launcher_name, tool_folder in entry["bake_menu"]:
            action = menu.addAction(bake_label)
            action.triggered.connect(
                lambda checked=False, ln=launcher_name, tf=tool_folder: _run_tool_action(ln, tf)
            )
        btn.setMenu(menu)
    elif entry.get("special") == "smooth_keys":
        btn.clicked.connect(_run_smooth_selected_keys)
    else:
        launcher_name = entry.get("launcher_name")
        tool_folder = entry.get("tool_folder")
        btn.clicked.connect(
            lambda checked=False, ln=launcher_name, tf=tool_folder: _run_tool_action(ln, tf)
        )

    _install_context_menu(btn)
    _register_tooltip(btn, entry.get("tooltip_key"), icon_path)
    return btn


def _make_scale_adapter(scale_module, mode_fn_name):
    mode_fn = getattr(scale_module, mode_fn_name)

    def logic(value, mouse_pressed, last_update_time, update_throttle_ms):
        if not mouse_pressed:
            return last_update_time, ""
        return mode_fn(value, last_update_time, update_throttle_ms)

    return types.SimpleNamespace(slider_logic=logic, reset_slider=scale_module.reset_slider)


def _make_ease_adapter(ease_module):
    def logic(value, mouse_pressed, last_update_time, update_throttle_ms):
        if mouse_pressed and ease_module is not None:
            ease_module.update_ease(value)
        return last_update_time, "Ease: {0}".format(value)

    def reset(widget):
        if ease_module is not None:
            ease_module.finish_ease()
        widget.blockSignals(True)
        widget.setValue(0)
        widget.blockSignals(False)

    return types.SimpleNamespace(slider_logic=logic, reset_slider=reset)


def _make_cascade_remapped_adapter(cascade_module):
    def logic(value, mouse_pressed, last_update_time, update_throttle_ms):
        remapped_value = value + 100
        return cascade_module.slider_logic(remapped_value, mouse_pressed, last_update_time, update_throttle_ms)

    def reset(widget):
        raw_value = widget.value()
        remapped_value = raw_value + 100
        widget.blockSignals(True)
        widget.setValue(remapped_value)
        widget.blockSignals(False)
        cascade_module.reset_slider(widget)
        widget.blockSignals(True)
        widget.setValue(0)
        widget.blockSignals(False)

    return types.SimpleNamespace(slider_logic=logic, reset_slider=reset)


def register_modules(modules_by_name):
    global _slider_modules
    _slider_modules = dict(modules_by_name)

    scale_module = _slider_modules.get("scale_slider")
    if scale_module is not None:
        _slider_modules["scale_left_adapter"] = _make_scale_adapter(scale_module, "scale_left_logic")
        _slider_modules["scale_right_adapter"] = _make_scale_adapter(scale_module, "scale_right_logic")
        _slider_modules["scale_avg_adapter"] = _make_scale_adapter(scale_module, "scale_avg_logic")

    ease_module = _slider_modules.get("ease_slider")
    _slider_modules["ease_adapter"] = _make_ease_adapter(ease_module)

    cascade_module = _slider_modules.get("cascade_slider")
    if cascade_module is not None:
        _slider_modules["cn_cascade_adapter"] = _make_cascade_remapped_adapter(cascade_module)


def is_slider_enabled(label):
    return label in _S.active_widgets


MODIFIER_SLIDER_MAP = {
    "TW": {"ctrl": "EA"},
    "SL": {"ctrl": "SA", "shift": "SR"},
}


class GraphEditorSlider(QtWidgets.QSlider):

    def __init__(self, label, color, module, parent=None):
        super(GraphEditorSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        self.label_text = label
        self.original_label = label
        self.handle_color = QtGui.QColor(*color)
        self.icon_color = QtGui.QColor(*color)
        self.module = module
        self.original_module = module
        self.mouse_pressed = False
        self.last_update_time = 0
        self.update_throttle_ms = 1
        self.overshoot_enabled = False
        self.shift_pressed = False
        self.ctrl_pressed = False
        self._normal_min = None
        self._normal_max = None
        self.setMinimum(-100)
        self.setMaximum(100)
        self.setValue(0)
        self.setMinimumHeight(_scaled(21))
        self.setMaximumHeight(_scaled(21))
        self.setMinimumWidth(_scaled(150))

    def _modifier_target_label(self):
        variants = MODIFIER_SLIDER_MAP.get(self.original_label)
        if variants is None:
            return self.original_label
        if self.ctrl_pressed and "ctrl" in variants:
            return variants["ctrl"]
        if self.shift_pressed and "shift" in variants:
            return variants["shift"]
        return self.original_label

    def _modifier_target_module(self, target_label):
        if target_label == self.original_label:
            return self.original_module
        for catalog_label, catalog_color, module_name in SLIDER_CATALOG:
            if catalog_label == target_label:
                return _slider_modules.get(module_name, self.original_module)
        return self.original_module

    def _refresh_modifier_state(self):
        if self.original_label not in MODIFIER_SLIDER_MAP:
            return
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
        self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
        target_label = self._modifier_target_label()
        if target_label != self.label_text:
            self.label_text = target_label
            self.module = self._modifier_target_module(target_label)
            self.update()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift):
                self._refresh_modifier_state()
        elif event.type() == QtCore.QEvent.KeyRelease:
            if event.key() in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift):
                self._refresh_modifier_state()
        return False

    def set_overshoot(self, enabled):
        enabled = bool(enabled)
        if enabled == self.overshoot_enabled:
            return
        if enabled:
            self._normal_min = self.minimum()
            self._normal_max = self.maximum()
            span = self._normal_max - self._normal_min
            extra = int(round(span * OVERSHOOT_RANGE_RATIO))
            self.blockSignals(True)
            self.setMinimum(self._normal_min - extra)
            self.setMaximum(self._normal_max + extra)
            self.blockSignals(False)
        else:
            if self._normal_min is not None and self._normal_max is not None:
                clamped = max(self._normal_min, min(self._normal_max, self.value()))
                self.blockSignals(True)
                self.setMinimum(self._normal_min)
                self.setMaximum(self._normal_max)
                self.setValue(clamped)
                self.blockSignals(False)
        self.overshoot_enabled = enabled
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()

        icon_size = _scaled(6)
        num_dots = 7
        total_items = num_dots + 2
        margin = _scaled(8)
        available_width = rect.width() - margin * 2
        item_spacing = available_width / (total_items - 1)
        icon_y = rect.height() // 2 - icon_size // 2

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(margin, icon_y, icon_size, icon_size, 1, 1)

        full_track_start = margin + item_spacing
        full_track_end = rect.width() - margin - item_spacing
        track_y = rect.height() // 2

        min_val = self.minimum()
        max_val = self.maximum()
        curr_val = self.value()

        dot_track_start = full_track_start
        dot_track_end = full_track_end

        if self.overshoot_enabled and self._normal_min is not None and self._normal_max is not None and max_val != min_val:
            normal_fraction = float(self._normal_max - self._normal_min) / float(max_val - min_val)
            normal_fraction = max(0.05, min(1.0, normal_fraction))
            overshoot_zone_each_side = (full_track_end - full_track_start) * (1.0 - normal_fraction) / 2.0
            dot_track_start = full_track_start + overshoot_zone_each_side
            dot_track_end = full_track_end - overshoot_zone_each_side

            overshoot_pen = QtGui.QPen(QtGui.QColor(230, 70, 70, 220), _scaled(2), QtCore.Qt.DashLine)
            painter.setPen(overshoot_pen)
            painter.drawLine(QtCore.QPointF(full_track_start, track_y), QtCore.QPointF(dot_track_start, track_y))
            painter.drawLine(QtCore.QPointF(dot_track_end, track_y), QtCore.QPointF(full_track_end, track_y))
            painter.setPen(QtCore.Qt.NoPen)

        dot_color = QtGui.QColor(self.handle_color)
        dot_color.setAlpha(220)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        dot_spacing = (dot_track_end - dot_track_start) / (num_dots - 1)
        dot_radius = _scaled(2.15)
        for i in range(num_dots):
            dot_x = dot_track_start + i * dot_spacing
            painter.drawEllipse(QtCore.QPointF(dot_x, track_y), dot_radius, dot_radius)

        if max_val != min_val:
            normalized = float(curr_val - min_val) / float(max_val - min_val)
        else:
            normalized = 0.5
        handle_x = full_track_start + normalized * (full_track_end - full_track_start)
        handle_size = _scaled(22)
        handle_rect = QtCore.QRectF(handle_x - handle_size / 2, track_y - handle_size / 2,
                                     handle_size, handle_size)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.handle_color)
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
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        if self.original_label in MODIFIER_SLIDER_MAP:
            QtWidgets.QApplication.instance().installEventFilter(self)
        self.mouse_pressed = True
        self._refresh_modifier_state()
        self._moveToClick(event)
        self._runLogic()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self._refresh_modifier_state()
            self._moveToClick(event)
            self._runLogic()

    def mouseReleaseEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        if self.original_label in MODIFIER_SLIDER_MAP:
            QtWidgets.QApplication.instance().removeEventFilter(self)
        self.mouse_pressed = False
        if _ge_slider_enabled(self.label_text):
            self.module.reset_slider(self)
        if self.label_text != self.original_label:
            self.label_text = self.original_label
            self.module = self.original_module
            self.update()

    def _moveToClick(self, event):
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        margin = _scaled(8)
        num_dots = 7
        item_spacing = (self.rect().width() - margin * 2) / (num_dots + 1)
        track_start = margin + item_spacing
        track_end = self.rect().width() - margin - item_spacing
        normalized = max(0.0, min(1.0, (pos.x() - track_start) / (track_end - track_start)))
        self.blockSignals(True)
        self.setValue(int(self.minimum() + normalized * (self.maximum() - self.minimum())))
        self.blockSignals(False)
        self.update()

    def _runLogic(self):
        if not _ge_slider_enabled(self.label_text):
            return
        self.last_update_time, status = self.module.slider_logic(
            self.value(), self.mouse_pressed, self.last_update_time, self.update_throttle_ms
        )


class _StaysOpenSliderMenu(QtWidgets.QMenu):
    def mousePressEvent(self, event):
        pos = event.pos() if hasattr(event, 'pos') else event.position().toPoint()
        action = self.actionAt(pos)
        if action is not None and action.isEnabled() and not action.menu():
            event.accept()
            return
        super(_StaysOpenSliderMenu, self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        pos = event.pos() if hasattr(event, 'pos') else event.position().toPoint()
        action = self.actionAt(pos)
        if action is not None and action.isEnabled() and not action.menu():
            callback = action.property("stays_open_callback")
            if callback is not None:
                if action.isCheckable():
                    action.setChecked(not action.isChecked())
                callback()
            event.accept()
            return
        super(_StaysOpenSliderMenu, self).mouseReleaseEvent(event)


def _find_loaded_module(name):
    for mod_name, mod in list(sys.modules.items()):
        if mod is not None and mod_name.split('.')[-1] == name:
            return mod
    return None


def _toggle_overshoot_from_menu(checked):
    try:
        from Animo_Sliders import slider_utils
        slider_utils.set_overshoot_enabled(checked)
    except Exception:
        pass
    launcher_mod = _find_loaded_module("Animo_Launcher")
    if launcher_mod is not None and hasattr(launcher_mod, "_apply_overshoot_to_all_sliders"):
        try:
            launcher_mod._apply_overshoot_to_all_sliders(checked)
            return
        except Exception:
            pass
    apply_overshoot_to_all(checked)


def _show_context_menu(global_pos):
    menu = QtWidgets.QMenu(_S.outer_widget)
    menu.setStyleSheet(_animo_menu_qss())

    sliders_submenu = _StaysOpenSliderMenu("Graph Editor Sliders", menu)
    sliders_submenu.setStyleSheet(menu.styleSheet())
    for label, color, module_name in SLIDER_CATALOG:
        display_name = SLIDER_DISPLAY_NAMES.get(label, label)
        slider_action = QAction(display_name, sliders_submenu)
        slider_action.setCheckable(True)
        slider_action.setChecked(is_slider_enabled(label))
        slider_action.setProperty(
            "stays_open_callback", lambda l=label: _toggle_slider_from_menu(l))
        sliders_submenu.addAction(slider_action)
    menu.addMenu(sliders_submenu)

    tools_submenu = _StaysOpenSliderMenu("Graph Editor Tools", menu)
    tools_submenu.setStyleSheet(menu.styleSheet())
    for entry in TOOL_CATALOG:
        tool_action = QAction(entry["label"], tools_submenu)
        tool_action.setCheckable(True)
        tool_action.setChecked(is_tool_enabled(entry["key"]))
        tool_action.setProperty(
            "stays_open_callback", lambda k=entry["key"]: _toggle_tool_from_menu(k))
        tools_submenu.addAction(tool_action)
    menu.addMenu(tools_submenu)

    toolbar_action = QAction("Graph Editor Toolbar", menu)
    toolbar_action.setCheckable(True)
    toolbar_action.setChecked(is_toolbar_enabled())
    toolbar_action.triggered.connect(_toggle_toolbar_from_menu)
    menu.addAction(toolbar_action)

    menu.addSeparator()

    overshoot_action = QAction("Sliders Overshoot Mode", menu)
    overshoot_action.setCheckable(True)
    overshoot_action.setChecked(_current_overshoot_state())
    overshoot_action.triggered.connect(_toggle_overshoot_from_menu)
    menu.addAction(overshoot_action)

    menu.exec_(global_pos)


def _install_context_menu(widget):
    widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    widget.customContextMenuRequested.connect(
        lambda pos, w=widget: _show_context_menu(w.mapToGlobal(pos))
    )


def _build_row_context_menu(outer_widget):
    _install_context_menu(outer_widget)


def _toggle_toolbar_from_menu(checked):
    if checked:
        enable_toolbar()
    else:
        disable_toolbar()


def _toggle_slider_from_menu(label):
    if not is_slider_enabled(label) and not is_toolbar_enabled():
        set_toolbar_enabled(True)
    toggle_slider(label, overshoot=_current_overshoot_state())


def _toggle_tool_from_menu(key):
    if not is_tool_enabled(key) and not is_toolbar_enabled():
        set_toolbar_enabled(True)
    toggle_tool(key)


def _sync_flow_height():
    if _S.flow_widget is None or _S.flow_layout is None:
        return
    target_height = _S.flow_layout.heightForWidth(_S.flow_widget.width())
    if target_height > 0 and _S.flow_widget.height() != target_height:
        _S.flow_widget.setFixedHeight(target_height)


def _find_open_graph_editor_panel():
    try:
        panels = cmds.getPanel(scriptType="graphEditor") or []
    except:
        panels = []
    existing = []
    for p in panels:
        try:
            if cmds.control(p, exists=True):
                existing.append(p)
        except:
            pass
    if not existing:
        return None
    visible = cmds.getPanel(vis=True) or []
    for p in existing:
        if p in visible:
            return p
    return existing[0]


def _widget_is_alive(widget):
    if widget is None:
        return False
    try:
        return isValid(widget)
    except:
        return False


def _row_full_path(panel_name):
    if not panel_name:
        return None
    return panel_name + "|" + OUTER_LAYOUT_NAME


def _row_is_healthy():
    if _S.outer_widget is None or _S.flow_widget is None:
        return False
    full_path = _row_full_path(_S.current_panel_name)
    if full_path is None or not cmds.control(full_path, exists=True):
        return False
    return _widget_is_alive(_S.outer_widget) and _widget_is_alive(_S.flow_widget)


def _try_wrap_existing_row(panel_name):
    full_path = _row_full_path(panel_name)
    if full_path is None or not cmds.control(full_path, exists=True):
        return None, None
    try:
        outer_ptr = mui.MQtUtil.findControl(full_path)
    except:
        outer_ptr = None
    if not outer_ptr:
        return None, None
    try:
        candidate_outer = wrapInstance(int(outer_ptr), QtWidgets.QWidget)
    except:
        candidate_outer = None
    if not _widget_is_alive(candidate_outer):
        return None, None
    candidate_flow = None
    for child in candidate_outer.findChildren(_FlowContainer):
        if _widget_is_alive(child):
            candidate_flow = child
            break
    if candidate_flow is None:
        return None, None
    return candidate_outer, candidate_flow


def _cleanup_stray_rows(keep_panel_name):
    keep_path = _row_full_path(keep_panel_name)
    keep_ptr = None
    if keep_path:
        try:
            found_ptr = mui.MQtUtil.findControl(keep_path)
            if found_ptr:
                keep_ptr = int(found_ptr)
        except:
            keep_ptr = None

    try:
        panels = cmds.getPanel(scriptType="graphEditor") or []
    except:
        panels = []
    for p in panels:
        if p == keep_panel_name:
            continue
        try:
            if not cmds.control(p, exists=True):
                continue
        except:
            continue
        stray_path = _row_full_path(p)
        try:
            if stray_path and cmds.control(stray_path, exists=True):
                cmds.deleteUI(stray_path)
        except:
            pass

    try:
        all_layouts = cmds.lsUI(long=True, controlLayouts=True) or []
    except:
        all_layouts = []
    for full_name in all_layouts:
        base_name = full_name.split("|")[-1]
        if base_name != OUTER_LAYOUT_NAME:
            continue
        try:
            candidate_ptr_raw = mui.MQtUtil.findControl(full_name)
            candidate_ptr = int(candidate_ptr_raw) if candidate_ptr_raw else None
        except:
            candidate_ptr = None
        if keep_ptr is not None and candidate_ptr == keep_ptr:
            continue
        try:
            if cmds.control(full_name, exists=True):
                cmds.deleteUI(full_name)
        except:
            pass


def _count_existing_rows():
    try:
        all_layouts = cmds.lsUI(long=True, controlLayouts=True) or []
    except:
        return 0
    return sum(1 for full_name in all_layouts if full_name.split("|")[-1] == OUTER_LAYOUT_NAME)


def _ensure_row(allow_open=True):
    if _S.ensure_row_lock:
        return _S.flow_widget
    _S.ensure_row_lock = True
    try:
        panel_name = _find_open_graph_editor_panel()
        if panel_name is None:
            if not allow_open:
                return None
            cmds.GraphEditor()
            panel_name = _find_open_graph_editor_panel()
            if panel_name is None:
                return None

        panel_changed = _S.current_panel_name is not None and _S.current_panel_name != panel_name
        stale_widgets = _S.outer_widget is not None and not _row_is_healthy()
        if panel_changed or stale_widgets:
            _S.outer_widget = None
            _S.flow_widget = None
            _S.flow_layout = None
            _S.active_widgets.clear()
            _S.active_wrappers.clear()
            _S.active_tools.clear()
        _S.current_panel_name = panel_name

        _cleanup_stray_rows(panel_name)

        full_path = _row_full_path(panel_name)
        if _S.outer_widget is None:
            reattached_outer, reattached_flow = _try_wrap_existing_row(panel_name)
            if reattached_outer is not None:
                _S.outer_widget = reattached_outer
                _S.flow_widget = reattached_flow
                _S.flow_layout = _S.flow_widget.layout()
            else:
                if cmds.control(full_path, exists=True):
                    try:
                        cmds.deleteUI(full_path)
                    except:
                        pass
                try:
                    cmds.columnLayout(OUTER_LAYOUT_NAME, adjustableColumn=True, p=panel_name)
                except RuntimeError:
                    _S.current_panel_name = None
                    return None
                _S.outer_widget = wrapInstance(int(mui.MQtUtil.findControl(full_path)), QtWidgets.QWidget)
                _build_row_context_menu(_S.outer_widget)
                outer_setup_layout = _S.outer_widget.layout()
                if outer_setup_layout is not None:
                    outer_setup_layout.setContentsMargins(0, 0, 0, _scaled(ROW_BOTTOM_MARGIN))
        if _S.flow_widget is None:
            for stray_flow in _S.outer_widget.findChildren(_FlowContainer):
                try:
                    stray_flow.hide()
                    stray_flow.setParent(None)
                    stray_flow.deleteLater()
                except:
                    pass
            _S.flow_widget = _FlowContainer(_S.outer_widget)
            _S.flow_layout = FlowLayout(_S.flow_widget, margin=0, hspacing=_scaled(6), vspacing=_scaled(4))
            _S.flow_widget.setLayout(_S.flow_layout)
            outer_qlayout = _S.outer_widget.layout()
            if outer_qlayout is not None:
                outer_qlayout.addWidget(_S.flow_widget)
            _S.flow_widget.show()
            _install_context_menu(_S.flow_widget)

        if _count_existing_rows() > 1:
            _cleanup_stray_rows(panel_name)

        return _S.flow_widget
    finally:
        _S.ensure_row_lock = False


def set_slider_enabled(label, enabled, overshoot=False, allow_open=True):
    flow_name = _ensure_row(allow_open=allow_open)
    if flow_name is None:
        return
    if enabled:
        if label in _S.active_widgets:
            return
        entry = None
        for catalog_item in SLIDER_CATALOG:
            if catalog_item[0] == label:
                entry = catalog_item
                break
        if entry is None:
            return
        _, color, module_name = entry
        module = _slider_modules.get(module_name)
        if module is None:
            return

        placeholder_widget = QtWidgets.QWidget(_S.flow_widget)
        placeholder_widget.setFixedSize(_scaled(PLACEHOLDER_WIDTH), _scaled(PLACEHOLDER_HEIGHT))
        placeholder_layout = QtWidgets.QVBoxLayout(placeholder_widget)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)

        slider = GraphEditorSlider(label, color, module, parent=placeholder_widget)
        slider.set_overshoot(overshoot)
        placeholder_layout.addWidget(slider)

        _install_context_menu(placeholder_widget)
        _install_context_menu(slider)
        _register_tooltip(slider, SLIDER_TOOLTIP_KEYS.get(label), None, hover_delay=1000)

        _S.flow_layout.addWidget(placeholder_widget)
        placeholder_widget.show()

        _S.active_widgets[label] = slider
        _S.active_wrappers[label] = placeholder_widget
        _sync_flow_height()
    else:
        widget = _S.active_widgets.pop(label, None)
        wrapper = _S.active_wrappers.pop(label, None)
        if widget is not None:
            _unregister_tooltip(widget)
        if wrapper is not None:
            try:
                _S.flow_layout.removeWidget(wrapper)
                wrapper.hide()
                wrapper.setParent(None)
                wrapper.deleteLater()
            except:
                pass
        elif widget is not None:
            try:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
            except:
                pass
        if _S.flow_widget is not None:
            _S.flow_widget.updateGeometry()
            _sync_flow_height()


def _row_order_labels(item_type):
    return [key for (t, key) in _S.row_order if t == item_type]


def _row_order_add(item_type, key):
    entry = (item_type, key)
    if entry not in _S.row_order:
        _S.row_order.append(entry)


def _row_order_remove(item_type, key):
    entry = (item_type, key)
    if entry in _S.row_order:
        _S.row_order.remove(entry)


def _persist_row_order():
    save_row_order(_S.row_order)
    save_enabled_labels(_row_order_labels("slider"))
    save_enabled_tools(_row_order_labels("tool"))


def toggle_slider(label, overshoot=False):
    enabled = label not in _S.active_widgets
    set_slider_enabled(label, enabled, overshoot=overshoot, allow_open=True)
    if enabled:
        _row_order_add("slider", label)
    else:
        _row_order_remove("slider", label)
    _persist_row_order()
    return enabled


def toggle_tool(key):
    enabled = key not in _S.active_tools
    set_tool_enabled(key, enabled, allow_open=True)
    if enabled:
        _row_order_add("tool", key)
    else:
        _row_order_remove("tool", key)
    _persist_row_order()
    return enabled


def set_tool_enabled(key, enabled, allow_open=True):
    flow_name = _ensure_row(allow_open=allow_open)
    if flow_name is None:
        return
    if enabled:
        if key in _S.active_tools:
            return
        entry = _tool_catalog_entry(key)
        if entry is None:
            return

        button = _make_tool_button(entry, _S.flow_widget)
        _S.flow_layout.addWidget(button)
        button.show()

        _S.active_tools[key] = button
        _sync_flow_height()
    else:
        button = _S.active_tools.pop(key, None)
        if button is not None:
            _unregister_tooltip(button)
            try:
                _S.flow_layout.removeWidget(button)
                button.hide()
                button.setParent(None)
                button.deleteLater()
            except:
                pass
        if _S.flow_widget is not None:
            _S.flow_widget.updateGeometry()
            _sync_flow_height()


def restore_row_from_prefs(overshoot=False):
    order = load_row_order()
    if order is None:
        slider_labels = load_enabled_labels()
        tool_keys = load_enabled_tools()
        order = [("slider", label) for label in slider_labels] + [("tool", key) for key in tool_keys]
        _S.row_order = list(order)
        _persist_row_order()
    else:
        _S.row_order = list(order)

    for item_type, item_key in _S.row_order:
        if item_type == "slider":
            set_slider_enabled(item_key, True, overshoot=overshoot, allow_open=False)
        elif item_type == "tool":
            set_tool_enabled(item_key, True, allow_open=False)


def apply_overshoot_to_all(enabled):
    stale_labels = []
    for label, widget in list(_S.active_widgets.items()):
        try:
            widget.set_overshoot(enabled)
        except Exception:
            stale_labels.append(label)
    for label in stale_labels:
        _S.active_widgets.pop(label, None)
        _S.active_wrappers.pop(label, None)


def _current_overshoot_state():
    try:
        from Animo_Sliders import slider_utils
        return slider_utils.is_overshoot_enabled()
    except:
        return False


IDLE_CHECK_MIN_INTERVAL = 0.35
REBUILD_MIN_INTERVAL = 1.5
REBUILD_MAX_INTERVAL = 30.0
HEALTHY_RESET_THRESHOLD = 4.0
UNHEALTHY_STRIKES_REQUIRED = 2


def _deferred_rebuild_row():
    _S.rebuild_scheduled = False
    _S.last_rebuild_time = time.time()
    if _S.outer_widget is None:
        try:
            restore_row_from_prefs(overshoot=_current_overshoot_state())
        except:
            pass


def _on_idle_check_graph_editor():

    if not is_toolbar_enabled():
        return

    now = time.time()
    if now - _S.last_idle_check_time < IDLE_CHECK_MIN_INTERVAL:
        return
    _S.last_idle_check_time = now

    row_healthy = _row_is_healthy()

    if not row_healthy:
        panel_still_exists = _S.current_panel_name is not None and cmds.panel(_S.current_panel_name, exists=True)
        candidate_panel = _S.current_panel_name if panel_still_exists else _find_open_graph_editor_panel()
        if candidate_panel is not None:
            reattached_outer, reattached_flow = _try_wrap_existing_row(candidate_panel)
            if reattached_outer is not None:
                _S.outer_widget = reattached_outer
                _S.flow_widget = reattached_flow
                _S.flow_layout = _S.flow_widget.layout()
                _S.current_panel_name = candidate_panel
                row_healthy = True

    if row_healthy:
        _S.unhealthy_strikes = 0
        if _S.healthy_since == 0.0:
            _S.healthy_since = now
        elif now - _S.healthy_since > HEALTHY_RESET_THRESHOLD:
            _S.rebuild_backoff = REBUILD_MIN_INTERVAL
        return

    _S.healthy_since = 0.0

    if _S.outer_widget is not None:
        _S.unhealthy_strikes += 1
        if _S.unhealthy_strikes < UNHEALTHY_STRIKES_REQUIRED:
            return
    _S.unhealthy_strikes = 0

    if _S.outer_widget is not None or _S.current_panel_name is not None:
        _S.active_widgets.clear()
        _S.active_wrappers.clear()
        _S.active_tools.clear()
        _S.outer_widget = None
        _S.flow_widget = None
        _S.flow_layout = None
        _S.current_panel_name = None
    if _find_open_graph_editor_panel() is None:
        return

    if _S.outer_widget is None and not _S.rebuild_scheduled:
        if now - _S.last_rebuild_time < _S.rebuild_backoff:
            return
        _S.rebuild_scheduled = True
        _S.rebuild_backoff = min(_S.rebuild_backoff * 2.0, REBUILD_MAX_INTERVAL)
        try:
            QtCore.QTimer.singleShot(150, _deferred_rebuild_row)
        except:
            _S.rebuild_scheduled = False


def is_auto_attach_script_job_running():
    try:
        return _S.qt_poll_timer is not None and _S.qt_poll_timer.isActive()
    except:
        return False


def start_auto_attach_script_job():
    if not ANIMO_ENABLE_GRAPH_EDITOR_IDLE_JOB:
        return None
    if _S.qt_poll_timer is not None:
        try:
            if _S.qt_poll_timer.isActive():
                return _S.qt_poll_timer
        except:
            _S.qt_poll_timer = None

    stop_auto_attach_script_job()
    _S.qt_poll_timer = QtCore.QTimer()
    _S.qt_poll_timer.setInterval(500)
    _S.qt_poll_timer.timeout.connect(_on_idle_check_graph_editor)
    _S.qt_poll_timer.start()
    return _S.qt_poll_timer


def stop_auto_attach_script_job():
    if _S.qt_poll_timer is not None:
        try:
            _S.qt_poll_timer.stop()
            _S.qt_poll_timer.deleteLater()
        except:
            pass
        _S.qt_poll_timer = None


def _clear_all_sliders():
    for label in list(_S.active_widgets.keys()):
        widget = _S.active_widgets.pop(label, None)
        if widget is not None:
            _unregister_tooltip(widget)
        wrapper = _S.active_wrappers.pop(label, None)
        if wrapper is not None:
            try:
                if _S.flow_layout is not None:
                    _S.flow_layout.removeWidget(wrapper)
                wrapper.hide()
                wrapper.setParent(None)
                wrapper.deleteLater()
            except:
                pass


def _clear_all_tools():
    for key in list(_S.active_tools.keys()):
        button = _S.active_tools.pop(key, None)
        if button is not None:
            _unregister_tooltip(button)
            try:
                if _S.flow_layout is not None:
                    _S.flow_layout.removeWidget(button)
                button.hide()
                button.setParent(None)
                button.deleteLater()
            except:
                pass


def remove_row():
    _clear_all_sliders()
    _clear_all_tools()
    full_path = _row_full_path(_S.current_panel_name)
    if full_path and cmds.control(full_path, exists=True):
        try:
            cmds.deleteUI(full_path)
        except:
            pass
    _cleanup_stray_rows(None)
    if _count_existing_rows() > 0:
        _cleanup_stray_rows(None)
    _S.outer_widget = None
    _S.flow_widget = None
    _S.flow_layout = None
    _S.current_panel_name = None


def enable_toolbar():
    set_toolbar_enabled(True)
    restore_row_from_prefs(overshoot=_current_overshoot_state())


def disable_toolbar():
    set_toolbar_enabled(False)
    remove_row()


try:
    if ANIMO_ENABLE_GRAPH_EDITOR_IDLE_JOB:
        start_auto_attach_script_job()
except:
    pass