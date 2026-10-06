from __future__ import division
from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import platform
import os
import sys

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
    _max = builtins.max
    _min = builtins.min
    _int = builtins.int
except Exception:
    _max = max
    _min = min
    _int = int


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
    
    try:
        app = QtWidgets.QApplication.instance()
        raw_scale = 1.0
        
        if app:
            screen = None
            
            if PYSIDE_VERSION == 6:
                screen = app.screenAt(current_cursor)
                if not screen:
                    screen = QGuiApplication.primaryScreen()
            else:
                if hasattr(app, 'screenAt'):
                    screen = app.screenAt(current_cursor)
                if not screen and hasattr(app, 'primaryScreen'):
                    screen = app.primaryScreen()
            
            if screen:
                raw_scale = screen.logicalDotsPerInch() / BASE_DPI
            else:
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    raw_scale = desktop.logicalDpiX() / BASE_DPI
        
        _scale_factor = _max(1.0, _min(raw_scale, 3.0))
            
    except:
        _scale_factor = 1.0
    
    return _scale_factor


def reset_scale_factor():
    global _scale_factor, _cursor_position
    _scale_factor = None
    _cursor_position = None


def dpi(value):
    return _int(value * get_scale_factor())


def get_manual_scale_override():
    if cmds.optionVar(exists="AnimLayerMergerScale"):
        scale = cmds.optionVar(q="AnimLayerMergerScale")
        return _max(0.5, _min(scale, 3.0))
    return None


def get_final_scale():
    manual_override = get_manual_scale_override()
    if manual_override:
        global _scale_factor
        _scale_factor = manual_override
    return get_scale_factor()


SCRIPTS_SUBFOLDER = os.path.join("Animo_Data", "Animo_Animation_Layers")


def get_scripts_path():
    possible_paths = [
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2026", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2025", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2024", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2023", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "Documents", "maya", "2022", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "2026", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "2025", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "2024", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "2023", "scripts", SCRIPTS_SUBFOLDER),
        os.path.join(os.path.expanduser("~"), "maya", "2022", "scripts", SCRIPTS_SUBFOLDER),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return _int(part)
        return 2022
    except Exception:
        return 2022


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(_int(main_window_ptr), QtWidgets.QWidget)


def run_script(script_name):
    scripts_path = get_scripts_path()
    if not scripts_path:
        cmds.warning("Could not find Animo_Animation_Layers folder")
        return

    script_file = os.path.join(scripts_path, script_name)
    
    use_pyc = False
    script_to_run = None
    
    if os.path.exists(script_file):
        script_to_run = script_file
    else:
        maya_version = get_maya_version()
        base_name = script_name.replace('.py', '')
        pyc_name = "{0}_py{1}.pyc".format(base_name, maya_version)
        script_pyc = os.path.join(scripts_path, pyc_name)
        
        if os.path.exists(script_pyc):
            script_to_run = script_pyc
            use_pyc = True
        else:
            cmds.warning("Script not found: " + script_file + " or " + script_pyc)
            return

    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)

    if use_pyc:
        import importlib
        maya_version = get_maya_version()
        base_name = script_name.replace('.py', '')
        module_name = "{0}_py{1}".format(base_name, maya_version)
        if module_name in sys.modules:
            del sys.modules[module_name]
        module = importlib.import_module(module_name)
    else:
        with open(script_to_run, 'r') as f:
            script_content = f.read()

        script_globals = {
            '__name__': '__main__',
            '__file__': script_to_run,
            '__builtins__': __builtins__,
        }
        exec(compile(script_content, script_to_run, 'exec'), script_globals, script_globals)


class AnimLayerMergerUI(QtWidgets.QDialog):
    option_var_name = "AnimLayerMergerUI_lastPos"
    option_var_auto_collapse = "AnimLayerMergerUI_autoCollapse"

    def __init__(self, parent=get_maya_main_window()):
        super(AnimLayerMergerUI, self).__init__(parent)
        self.setObjectName("AnimLayerMergerUIWindow")

        if platform.system() == 'Darwin':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)

        self.setWindowOpacity(0.0)
        self.expanded_width = dpi(200)
        self.expanded_height = dpi(175)
        self.collapsed_height = dpi(36)
        self.is_collapsed = False
        self.old_pos = None
        self.size_anim = None

        if cmds.optionVar(exists=self.option_var_auto_collapse):
            self.auto_collapse_enabled = cmds.optionVar(q=self.option_var_auto_collapse)
        else:
            self.auto_collapse_enabled = False
            cmds.optionVar(iv=(self.option_var_auto_collapse, 0))

        self.build_ui()
        self.apply_theme()
        self.setFixedSize(self.expanded_width, self.expanded_height)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        positioned = False
        if cmds.optionVar(exists=self.option_var_name):
            pos_str = cmds.optionVar(q=self.option_var_name)
            try:
                x, y = _int(pos_str.split(",")[0]), _int(pos_str.split(",")[1])
                if self.is_position_on_screen(x, y):
                    self.move(x, y)
                    positioned = True
            except Exception:
                pass
        
        if not positioned:
            self.center_on_screen()

        self.fade_to(0.92)
        self.apply_rounded_corners()

    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass

    def is_position_on_screen(self, x, y):
        try:
            app = QtWidgets.QApplication.instance()
            if not app:
                return False
            
            window_rect = QtCore.QRect(x, y, self.expanded_width, self.expanded_height)
            
            if PYSIDE_VERSION == 6:
                screens = app.screens()
            else:
                screens = []
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    for i in range(desktop.screenCount()):
                        screens.append(desktop.screenGeometry(i))
                elif hasattr(app, 'screens'):
                    screens = app.screens()
            
            for screen in screens:
                if PYSIDE_VERSION == 6:
                    screen_rect = screen.availableGeometry()
                elif hasattr(screen, 'availableGeometry'):
                    screen_rect = screen.availableGeometry()
                else:
                    screen_rect = screen
                
                intersection = window_rect.intersected(screen_rect)
                min_visible = 50
                if intersection.width() >= min_visible and intersection.height() >= min_visible:
                    return True
            
            return False
        except Exception:
            return False

    def center_on_screen(self):
        try:
            app = QtWidgets.QApplication.instance()
            if not app:
                return
            
            cursor_pos = QtGui.QCursor.pos()
            screen = None
            
            if PYSIDE_VERSION == 6:
                screen = app.screenAt(cursor_pos)
                if not screen:
                    screen = QGuiApplication.primaryScreen()
            else:
                if hasattr(app, 'screenAt'):
                    screen = app.screenAt(cursor_pos)
                if not screen and hasattr(app, 'primaryScreen'):
                    screen = app.primaryScreen()
            
            if screen:
                screen_rect = screen.availableGeometry()
            else:
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    screen_rect = desktop.availableGeometry(cursor_pos)
                else:
                    screen_rect = QtCore.QRect(0, 0, 1920, 1080)
            
            x = screen_rect.x() + (screen_rect.width() - self.expanded_width) // 2
            y = screen_rect.y() + (screen_rect.height() - self.expanded_height) // 2
            self.move(x, y)
        except Exception:
            pass

    def closeEvent(self, event):
        pos = self.pos()
        pos_str = "{0},{1}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        super(AnimLayerMergerUI, self).closeEvent(event)

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(10), dpi(10), dpi(10), dpi(10))
        main_layout.setSpacing(0)

        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(dpi(6))

        title_bar.addStretch()

        title_label = QtWidgets.QLabel("Fast animLayer Merger")
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: white;")
        title_bar.addWidget(title_label)

        title_bar.addStretch()

        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(dpi(22), dpi(22))
        close_button.setText(u"\u00D7")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 11px;
                color: #888888;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(231, 76, 60, 0.8); color: white; }
            QPushButton:pressed { background-color: rgba(192, 57, 43, 1.0); }
        """)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)

        main_layout.addLayout(title_bar)

        self.content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, dpi(12), 0, 0)
        content_layout.setSpacing(0)

        all_label = QtWidgets.QLabel("All Layers")
        all_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; font-weight: 700;")
        content_layout.addWidget(all_label)

        content_layout.addSpacing(dpi(4))

        all_row = QtWidgets.QHBoxLayout()
        all_row.setSpacing(dpi(4))

        merge_all_btn = self.create_button("M E R G E", "#C94A47", "#D95A57", "#B93A37", self.execute_merge_all)
        all_row.addWidget(merge_all_btn)

        smart_all_btn = self.create_button("S M A R T", "#8B3A38", "#9B4A48", "#7B2A28", self.execute_smart_merge_all)
        all_row.addWidget(smart_all_btn)

        content_layout.addLayout(all_row)

        content_layout.addSpacing(dpi(10))

        selected_label = QtWidgets.QLabel("Selected Layers")
        selected_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; font-weight: 700;")
        content_layout.addWidget(selected_label)

        content_layout.addSpacing(dpi(4))

        selected_row = QtWidgets.QHBoxLayout()
        selected_row.setSpacing(dpi(4))

        merge_sel_btn = self.create_button("M E R G E", "#1565C0", "#1976D2", "#0D47A1", self.execute_merge_selected)
        selected_row.addWidget(merge_sel_btn)

        smart_sel_btn = self.create_button("S M A R T", "#0D47A1", "#1565C0", "#0A3A7A", self.execute_smart_merge_selected)
        selected_row.addWidget(smart_sel_btn)

        content_layout.addLayout(selected_row)
        content_layout.addStretch()

        main_layout.addWidget(self.content_widget)

    def create_button(self, text, main_color, hover_color, pressed_color, callback):
        button = QtWidgets.QPushButton(text)
        button.setFixedHeight(dpi(28))
        button.setStyleSheet("""
            QPushButton {{
                background-color: {0};
                border: none;
                color: white;
                padding: {1}px {2}px;
                border-radius: 4px;
                font-size: 7pt;
                font-weight: 700;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{ background-color: {3}; }}
            QPushButton:pressed {{ background-color: {4}; }}
        """.format(main_color, dpi(4), dpi(8), hover_color, pressed_color))
        if callback:
            button.clicked.connect(callback)
        return button

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                color: white;
                border-radius: 12px;
            }
        """)

    def apply_rounded_corners(self):
        radius = 12
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super(AnimLayerMergerUI, self).resizeEvent(event)
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

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: {0}px;
            }}
            QMenu::item {{
                padding: {1}px {2}px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: #3A3A3A;
            }}
            QMenu::separator {{
                height: 1px;
                background: #3A3A3A;
                margin: {3}px 0px;
            }}
        """.format(dpi(4), dpi(6), dpi(12), dpi(4)))

        auto_collapse_action = menu.addAction("Auto Collapse")
        auto_collapse_action.setCheckable(True)
        auto_collapse_action.setChecked(self.auto_collapse_enabled)
        auto_collapse_action.triggered.connect(self.toggle_auto_collapse)

        if PYSIDE_VERSION == 6:
            menu.exec(self.mapToGlobal(pos))
        else:
            menu.exec_(self.mapToGlobal(pos))

    def toggle_auto_collapse(self, checked):
        self.auto_collapse_enabled = checked
        cmds.optionVar(iv=(self.option_var_auto_collapse, 1 if checked else 0))

        if not checked and self.is_collapsed:
            self.expand_ui()

    def enterEvent(self, event):
        self.fade_to(0.92, 50, QtCore.QEasingCurve.OutQuad)
        if self.auto_collapse_enabled:
            self.expand_ui()
        super(AnimLayerMergerUI, self).enterEvent(event)

    def leaveEvent(self, event):
        self.fade_to(0.65, 300)
        if self.auto_collapse_enabled:
            self.collapse_ui()
        super(AnimLayerMergerUI, self).leaveEvent(event)

    def expand_ui(self):
        if not self.is_collapsed:
            return
        self.is_collapsed = False
        self.content_widget.show()
        self.animate_size(self.expanded_height)

    def collapse_ui(self):
        if self.is_collapsed:
            return
        self.is_collapsed = True
        self.content_widget.hide()
        self.animate_size(self.collapsed_height)

    def animate_size(self, target_height):
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)

        self.size_anim = QtCore.QPropertyAnimation(self, b"size")
        self.size_anim.setDuration(150)
        self.size_anim.setStartValue(self.size())
        self.size_anim.setEndValue(QtCore.QSize(self.expanded_width, target_height))
        self.size_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.size_anim.finished.connect(lambda: self.on_animation_finished(target_height))
        self.size_anim.start()

    def on_animation_finished(self, target_height):
        self.setFixedSize(self.expanded_width, target_height)
        self.apply_rounded_corners()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if PYSIDE_VERSION == 6:
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            if PYSIDE_VERSION == 6:
                delta = event.globalPosition().toPoint() - self.old_pos
                self.old_pos = event.globalPosition().toPoint()
            else:
                delta = event.globalPos() - self.old_pos
                self.old_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def execute_merge_selected(self):
        cmds.undoInfo(openChunk=True)
        try:
            run_script("merge_selected_anim_layers.py")
        except Exception as e:
            cmds.warning("Error: " + str(e))
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()

    def execute_smart_merge_selected(self):
        cmds.undoInfo(openChunk=True)
        try:
            run_script("smart_merge_selected_anim_layers.py")
        except Exception as e:
            cmds.warning("Error: " + str(e))
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()

    def execute_merge_all(self):
        cmds.undoInfo(openChunk=True)
        try:
            run_script("merge_all_anim_layers.py")
        except Exception as e:
            cmds.warning("Error: " + str(e))
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()

    def execute_smart_merge_all(self):
        cmds.undoInfo(openChunk=True)
        try:
            run_script("smart_merge_all_anim_layers.py")
        except Exception as e:
            cmds.warning("Error: " + str(e))
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()


anim_layer_merger_instance = None


def create_anim_layer_merger_ui():
    global anim_layer_merger_instance

    if anim_layer_merger_instance is not None:
        try:
            anim_layer_merger_instance.close()
            anim_layer_merger_instance.deleteLater()
        except Exception:
            pass
        anim_layer_merger_instance = None

    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "AnimLayerMergerUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue

    reset_scale_factor()
    get_final_scale()
    
    anim_layer_merger_instance = AnimLayerMergerUI()
    anim_layer_merger_instance.show()
    return anim_layer_merger_instance


def ui():
    return create_anim_layer_merger_ui()


create_anim_layer_merger_ui()