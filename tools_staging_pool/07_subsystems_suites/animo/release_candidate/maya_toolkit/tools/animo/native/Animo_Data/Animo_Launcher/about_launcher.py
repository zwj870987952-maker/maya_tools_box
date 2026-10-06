from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

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


class AnimoUI(QtWidgets.QDialog):
    option_var_name = "AnimoUI_lastPos"

    def __init__(self, parent=get_maya_main_window()):
        super(AnimoUI, self).__init__(parent)
        self.setObjectName("AnimoUIWindow")
        
        self.dpi_scale = get_final_dpi_scale()
        
        if platform.system() == "Darwin":
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setFixedSize(scale_size(368), scale_size(230))
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
        super(AnimoUI, self).resizeEvent(event)
        self.apply_rounded_corners()

    def closeEvent(self, event):
        super(AnimoUI, self).closeEvent(event)

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


animo_ui_instance = None


def create_animo_ui():
    global animo_ui_instance
    
    if animo_ui_instance is not None:
        try:
            animo_ui_instance.close()
            animo_ui_instance.deleteLater()
        except Exception:
            pass
        animo_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "AnimoUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    animo_ui_instance = AnimoUI()
    animo_ui_instance.show()
    return animo_ui_instance


create_animo_ui()