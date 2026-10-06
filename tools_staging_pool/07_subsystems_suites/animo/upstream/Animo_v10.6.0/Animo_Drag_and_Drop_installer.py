from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import shutil

THIS_FILE_PATH = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE_PATH)

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtGui import QGuiApplication
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        from PySide2.QtGui import QGuiApplication
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1
        QGuiApplication = QtGui.QApplication

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import platform

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    int = builtins.int
except Exception:
    pass


def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
            if '.' in part:
                major = part.split('.')[0]
                if major.isdigit() and len(major) == 4:
                    return int(major)
        return 2022
    except Exception:
        return 2022


def get_reference_screen():
    app = QtWidgets.QApplication.instance()
    if not app:
        return None

    screen = None
    try:
        maya_widget = get_maya_main_window()
        if maya_widget:
            handle = maya_widget.windowHandle()
            if handle:
                screen = handle.screen()
            if screen is None:
                pos = maya_widget.pos()
                size = maya_widget.size()
                center = QtCore.QPoint(pos.x() + size.width() // 2, pos.y() + size.height() // 2)
                screen = app.screenAt(center)
    except Exception:
        screen = None

    if screen:
        return screen

    try:
        if PYSIDE_VERSION == 6:
            return QGuiApplication.primaryScreen()
        return app.primaryScreen()
    except Exception:
        return None


def get_dpi_scale():
    base_scale = 1.0

    try:
        if PYSIDE_VERSION == 6:
            screen = get_reference_screen()
            if screen:
                base_scale = screen.logicalDotsPerInch() / 96.0
        else:
            app = QtWidgets.QApplication.instance()
            if app:
                desktop = app.desktop()
                if desktop:
                    screen = desktop.screen()
                    if screen:
                        base_scale = screen.logicalDpiX() / 96.0
    except Exception:
        base_scale = 1.0

    return max(1.0, min(base_scale, 3.0))


def get_manual_scale_override():
    if cmds.optionVar(exists="AnimoUIScale"):
        scale = cmds.optionVar(q="AnimoUIScale")
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


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def get_maya_scripts_dir():
    try:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        maya_scripts_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        if maya_scripts_dir:
            return maya_scripts_dir
    except Exception:
        pass
    
    if platform.system() == "Windows":
        user_profile = os.environ.get('USERPROFILE', '')
        if not user_profile:
            home_drive = os.environ.get('HOMEDRIVE', 'C:')
            home_path = os.environ.get('HOMEPATH', '\\Users\\Default')
            user_profile = home_drive + home_path
        scripts_dir = user_profile + "\\Documents\\maya\\scripts"
    elif platform.system() == "Darwin":
        home = os.environ.get('HOME', os.path.expanduser("~"))
        scripts_dir = os.path.join(home, "Library", "Preferences", "Autodesk", "maya", "scripts")
        if not os.path.exists(os.path.dirname(os.path.dirname(scripts_dir))):
            scripts_dir = os.path.join(home, "Documents", "maya", "scripts")
    else:
        home = os.environ.get('HOME', os.path.expanduser("~"))
        scripts_dir = os.path.join(home, "maya", "scripts")
    return scripts_dir


def close_existing_animo_ui():
    try:
        if cmds.workspaceControl('animo', exists=True):
            cmds.workspaceControl('animo', edit=True, visible=False)
            cmds.deleteUI('animo', control=True)
    except Exception:
        pass
    
    try:
        maya_main_ptr = omui.MQtUtil.mainWindow()
        if maya_main_ptr:
            maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
            for existing in maya_main.findChildren(QtWidgets.QWidget, "animo_qt_toolbar"):
                try:
                    existing.hide()
                    existing.setParent(None)
                    existing.deleteLater()
                except Exception:
                    pass
    except Exception:
        pass
    
    QtWidgets.QApplication.processEvents()



def launch_animo_after_install(target_data_folder):
    import sys
    
    scripts_dir = os.path.dirname(target_data_folder)
    launcher = os.path.join(target_data_folder, "Animo_Launcher")
    
    for p in [scripts_dir, target_data_folder, launcher]:
        if p not in sys.path:
            sys.path.insert(0, p)
    
    for m in [k for k in sys.modules if 'Animo' in k]:
        del sys.modules[m]
    
    import Animo_Launcher
    
    cmds.inViewMessage(
        amg='<span style="color: #4A90D9; font-size:14pt;">Animo</span> installed successfully!',
        pos='midCenter',
        fade=True
    )

class AnimoInstallerUI(QtWidgets.QDialog):

    def __init__(self, installer_dir, parent=get_maya_main_window()):
        super(AnimoInstallerUI, self).__init__(parent)
        self.setObjectName("AnimoInstallerWindow")
        
        self.installer_dir = installer_dir
        self.target_data_folder = None
        
        self.dpi_scale = get_final_dpi_scale()
        
        if platform.system() == "Darwin":
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        
        self.setFixedSize(scale_size(368), scale_size(280))
        self.old_pos = None
        
        self.build_ui()
        self.apply_theme()
        self.center_on_screen()
        self.apply_rounded_corners()

    def center_on_screen(self):
        try:
            parent = self.parent()
            if parent:
                parent_geo = parent.geometry()
                x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
                y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
                self.move(x, y)
                return
        except Exception:
            pass
        
        try:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen()
                if screen:
                    screen_geo = screen.geometry()
                    x = (screen_geo.width() - self.width()) // 2
                    y = (screen_geo.height() - self.height()) // 2
                    self.move(x, y)
                    return
            else:
                app = QtWidgets.QApplication.instance()
                if app:
                    desktop = app.desktop()
                    if desktop:
                        screen_geo = desktop.screenGeometry()
                        x = (screen_geo.width() - self.width()) // 2
                        y = (screen_geo.height() - self.height()) // 2
                        self.move(x, y)
                        return
        except Exception:
            pass

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(scale_size(18), scale_size(12), scale_size(18), scale_size(18))
        main_layout.setSpacing(0)

        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(scale_size(9))
        title_bar.addStretch()

        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(scale_size(28), scale_size(28))
        close_button.setText(u"\u00D7")
        close_button.setStyleSheet("""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: {radius}px;
                color: #666666;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: #3A3A3A;
                color: #AAAAAA;
            }}
            QPushButton:pressed {{ 
                background-color: #2A2A2A;
            }}
        """.format(radius=scale_size(14), font_size=scale_font_size(28)))
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        main_layout.addLayout(title_bar)

        logo_layout = QtWidgets.QHBoxLayout()
        logo_layout.setSpacing(0)
        logo_layout.addStretch()

        an_label = QtWidgets.QLabel("An")
        an_label.setStyleSheet("""
            QLabel {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {font_size}px;
                font-weight: bold;
                color: #4A90D9;
                letter-spacing: 2px;
            }}
        """.format(font_size=scale_font_size(43)))
        logo_layout.addWidget(an_label)

        imo_label = QtWidgets.QLabel("imo")
        imo_label.setStyleSheet("""
            QLabel {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {font_size}px;
                font-weight: bold;
                color: #E0E0E0;
                letter-spacing: 2px;
            }}
        """.format(font_size=scale_font_size(43)))
        logo_layout.addWidget(imo_label)
        
        logo_layout.addStretch()
        main_layout.addLayout(logo_layout)

        main_layout.addSpacing(scale_size(7))

        version_layout = QtWidgets.QHBoxLayout()
        version_layout.addStretch()
        
        version_label = QtWidgets.QLabel("v10.6.0 BETA")
        version_label.setStyleSheet("""
            QLabel {{
                font-size: {font_size}px;
                font-weight: bold;
                color: #4A90D9;
                background-color: rgba(74, 144, 217, 0.15);
                padding: {pad_v}px {pad_h}px;
                border-radius: {radius}px;
            }}
        """.format(font_size=scale_font_size(13), pad_v=scale_size(3), pad_h=scale_size(12), radius=scale_size(12)))
        version_layout.addWidget(version_label)
        
        version_layout.addStretch()
        main_layout.addLayout(version_layout)

        main_layout.addSpacing(scale_size(25))

        install_layout = QtWidgets.QHBoxLayout()
        install_layout.addStretch()
        
        self.install_button = QtWidgets.QPushButton("Install")
        self.install_button.setFixedSize(scale_size(140), scale_size(40))
        self.install_button.setStyleSheet("""
            QPushButton {{
                background-color: #4A90D9;
                border: none;
                border-radius: {radius}px;
                color: #FFFFFF;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: #5AA0E9;
            }}
            QPushButton:pressed {{ 
                background-color: #3A80C9;
            }}
            QPushButton:disabled {{
                background-color: #2A5A89;
                color: #888888;
            }}
        """.format(radius=scale_size(8), font_size=scale_font_size(16)))
        self.install_button.clicked.connect(self.run_installation)
        install_layout.addWidget(self.install_button)
        
        install_layout.addStretch()
        main_layout.addLayout(install_layout)

        main_layout.addSpacing(scale_size(18))
        main_layout.addStretch()

        footer_layout = QtWidgets.QVBoxLayout()
        footer_layout.setSpacing(scale_size(5))

        copyright_label = QtWidgets.QLabel(u"\u00A9 2026 by Ehsan Bayat")
        copyright_label.setAlignment(QtCore.Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {{
                font-size: {font_size}px;
                color: #888888;
            }}
        """.format(font_size=scale_font_size(12)))
        footer_layout.addWidget(copyright_label)

        thanks_label = QtWidgets.QLabel("Accessible to all, made with heart.")
        thanks_label.setAlignment(QtCore.Qt.AlignCenter)
        thanks_label.setStyleSheet("""
            QLabel {{
                font-size: {font_size}px;
                color: #666666;
            }}
        """.format(font_size=scale_font_size(12)))
        footer_layout.addWidget(thanks_label)

        main_layout.addLayout(footer_layout)
        main_layout.addSpacing(scale_size(9))

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {{
                background-color: #1A1A1A;
                color: #E0E0E0;
                border-radius: {radius}px;
            }}
        """.format(radius=scale_size(16)))

    def apply_rounded_corners(self):
        radius = scale_size(16)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super(AnimoInstallerUI, self).resizeEvent(event)
        self.apply_rounded_corners()

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

    def delayed_launch(self):
        if self.target_data_folder:
            launch_animo_after_install(self.target_data_folder)

    def add_shelf_button(self, source_data_folder):
        shelf_command = '''import os
import maya.cmds as cmds
import maya.mel as mel
import runpy

cmds.optionVar(intValue=("SafeModeExecUserSetupScript", 1))

version_script_dir = cmds.internalVar(userScriptDir=True)
script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
animo_data = os.path.join(script_dir, "Animo_Data")

toggle_py = os.path.join(animo_data, "Animo_Launcher", "toggle.py")
if os.path.exists(toggle_py):
    runpy.run_path(toggle_py, run_name="__main__")
'''

        source_icon_path = os.path.join(source_data_folder, "Animo_Launcher", "animo_icon.png")

        default_icon = "commandButton.png"
        shelf_icon = default_icon

        try:
            maya_prefs_dir = cmds.internalVar(userPrefDir=True)
            maya_icons_dir = os.path.join(maya_prefs_dir, "icons")

            if os.path.exists(source_icon_path):
                if not os.path.exists(maya_icons_dir):
                    os.makedirs(maya_icons_dir)

                target_icon_path = os.path.join(maya_icons_dir, "animo_icon.png")
                shutil.copy(source_icon_path, target_icon_path)

                if os.path.exists(target_icon_path):
                    shelf_icon = target_icon_path
        except Exception:
            shelf_icon = default_icon

        shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
        current_shelf = cmds.tabLayout(shelf, q=True, st=True)

        base_label = "Animo"
        button_label = base_label
        counter = 1

        try:
            existing_buttons = cmds.shelfLayout(current_shelf, q=True, ca=True) or []
            existing_labels = []
            for btn in existing_buttons:
                try:
                    label = cmds.shelfButton(btn, q=True, label=True)
                    if label and label.startswith(base_label):
                        existing_labels.append(label)
                except Exception:
                    pass

            while button_label in existing_labels:
                counter += 1
                button_label = "{0}_{1}".format(base_label, counter)
        except Exception:
            pass

        cmds.shelfButton(
            label=button_label,
            parent=current_shelf,
            annotation="Launch Animo",
            image=shelf_icon,
            command=shelf_command,
            sourceType="python"
        )

    def install_data_folder(self, source_data_folder):
        scripts_dir = get_maya_scripts_dir()

        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)

        self.target_data_folder = os.path.join(scripts_dir, "Animo_Data")

        saved_tooltip_pref = None
        saved_startup_configured = False
        saved_overshoot_data = None
        saved_row_order_data = None
        saved_graph_sliders_data = None
        saved_toolbar_enabled_data = None
        saved_graph_tools_data = None

        if os.path.exists(self.target_data_folder):
            prefs_folder = os.path.join(self.target_data_folder, "Animo_Prefs")

            tooltip_prefs_file = os.path.join(prefs_folder, "tooltip_prefs.json")
            if os.path.exists(tooltip_prefs_file):
                try:
                    import json
                    with open(tooltip_prefs_file, 'r') as f:
                        tooltip_data = json.load(f)
                        saved_tooltip_pref = tooltip_data.get("enabled", True)
                except Exception:
                    pass

            overshoot_prefs_file = os.path.join(prefs_folder, "sliders_overshoot.json")
            if os.path.exists(overshoot_prefs_file):
                try:
                    import json
                    with open(overshoot_prefs_file, 'r') as f:
                        saved_overshoot_data = json.load(f)
                except Exception:
                    pass

            row_order_prefs_file = os.path.join(prefs_folder, "graph_editor_row_order.json")
            if os.path.exists(row_order_prefs_file):
                try:
                    import json
                    with open(row_order_prefs_file, 'r') as f:
                        saved_row_order_data = json.load(f)
                except Exception:
                    pass

            graph_sliders_prefs_file = os.path.join(prefs_folder, "graph_editor_sliders.json")
            if os.path.exists(graph_sliders_prefs_file):
                try:
                    import json
                    with open(graph_sliders_prefs_file, 'r') as f:
                        saved_graph_sliders_data = json.load(f)
                except Exception:
                    pass

            toolbar_enabled_prefs_file = os.path.join(prefs_folder, "graph_editor_toolbar_enabled.json")
            if os.path.exists(toolbar_enabled_prefs_file):
                try:
                    import json
                    with open(toolbar_enabled_prefs_file, 'r') as f:
                        saved_toolbar_enabled_data = json.load(f)
                except Exception:
                    pass

            graph_tools_prefs_file = os.path.join(prefs_folder, "graph_editor_tools.json")
            if os.path.exists(graph_tools_prefs_file):
                try:
                    import json
                    with open(graph_tools_prefs_file, 'r') as f:
                        saved_graph_tools_data = json.load(f)
                except Exception:
                    pass

            startup_file = os.path.join(prefs_folder, "startup_configured.txt")
            if os.path.exists(startup_file):
                saved_startup_configured = True

            shutil.rmtree(self.target_data_folder)

        shutil.copytree(source_data_folder, self.target_data_folder)

        prefs_folder = os.path.join(self.target_data_folder, "Animo_Prefs")
        if not os.path.exists(prefs_folder):
            try:
                os.makedirs(prefs_folder)
            except Exception:
                pass

        size_prefs_file = os.path.join(prefs_folder, "size_prefs.json")
        if os.path.exists(size_prefs_file):
            try:
                os.remove(size_prefs_file)
            except Exception:
                pass

        if saved_tooltip_pref is not None:
            try:
                import json
                tooltip_prefs_file = os.path.join(prefs_folder, "tooltip_prefs.json")
                with open(tooltip_prefs_file, 'w') as f:
                    json.dump({"enabled": saved_tooltip_pref}, f)
            except Exception:
                pass

        if saved_overshoot_data is not None:
            try:
                import json
                overshoot_prefs_file = os.path.join(prefs_folder, "sliders_overshoot.json")
                with open(overshoot_prefs_file, 'w') as f:
                    json.dump(saved_overshoot_data, f)
            except Exception:
                pass

        if saved_row_order_data is not None:
            try:
                import json
                row_order_prefs_file = os.path.join(prefs_folder, "graph_editor_row_order.json")
                with open(row_order_prefs_file, 'w') as f:
                    json.dump(saved_row_order_data, f)
            except Exception:
                pass

        if saved_graph_sliders_data is not None:
            try:
                import json
                graph_sliders_prefs_file = os.path.join(prefs_folder, "graph_editor_sliders.json")
                with open(graph_sliders_prefs_file, 'w') as f:
                    json.dump(saved_graph_sliders_data, f)
            except Exception:
                pass

        if saved_toolbar_enabled_data is not None:
            try:
                import json
                toolbar_enabled_prefs_file = os.path.join(prefs_folder, "graph_editor_toolbar_enabled.json")
                with open(toolbar_enabled_prefs_file, 'w') as f:
                    json.dump(saved_toolbar_enabled_data, f)
            except Exception:
                pass

        if saved_graph_tools_data is not None:
            try:
                import json
                graph_tools_prefs_file = os.path.join(prefs_folder, "graph_editor_tools.json")
                with open(graph_tools_prefs_file, 'w') as f:
                    json.dump(saved_graph_tools_data, f)
            except Exception:
                pass

        if saved_startup_configured:
            try:
                startup_file = os.path.join(prefs_folder, "startup_configured.txt")
                with open(startup_file, 'w') as f:
                    f.write("configured")
            except Exception:
                pass

    def run_installation(self):
        self.install_button.setEnabled(False)
        self.install_button.setText("Installing...")
        QtWidgets.QApplication.processEvents()

        cmds.waitCursor(state=True)

        try:
            close_existing_animo_ui()
        except Exception:
            pass

        source_data_folder = os.path.join(self.installer_dir, "Animo_Data")
        data_found = os.path.exists(source_data_folder)

        shelf_error = None
        try:
            self.add_shelf_button(source_data_folder)
            shelf_added = True
        except Exception as e:
            shelf_added = False
            shelf_error = e

        data_error = None
        if data_found:
            try:
                self.install_data_folder(source_data_folder)
            except Exception as e:
                data_error = e

        cmds.waitCursor(state=False)

        if not shelf_added:
            cmds.inViewMessage(
                amg='<span style="color: #FF6B6B; font-size:14pt;">Shelf button could not be added: {0}</span>'.format(str(shelf_error)),
                pos='midCenter',
                fade=True
            )
            self.install_button.setEnabled(True)
            self.install_button.setText("Install")
            return

        if not data_found or data_error is not None:
            cmds.inViewMessage(
                amg='<span style="color: #FFD166; font-size:14pt;">Shelf button added. Please place the Animo_Data folder inside your Maya scripts folder manually.</span>',
                pos='midCenter',
                fade=True
            )

        self.close()

        if data_found and data_error is None:
            QtCore.QTimer.singleShot(1000, self.delayed_launch)


animo_installer_instance = None


def onMayaDroppedPythonFile(*args, **kwargs):
    installer_dir = os.path.dirname(__file__)
    create_installer_ui(installer_dir)


def create_installer_ui(installer_dir=None):
    global animo_installer_instance
    
    if installer_dir is None:
        installer_dir = THIS_DIR
    
    if animo_installer_instance is not None:
        try:
            animo_installer_instance.close()
            animo_installer_instance.deleteLater()
        except Exception:
            pass
        animo_installer_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        if child.objectName() == "AnimoInstallerWindow":
            try:
                child.close()
                child.deleteLater()
            except Exception:
                pass
    
    animo_installer_instance = AnimoInstallerUI(installer_dir)
    animo_installer_instance.show()
    return animo_installer_instance