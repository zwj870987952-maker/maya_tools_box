# -*- coding: utf-8 -*-
"""Main entry point for the Maya Blueprint Toolbox."""

from .qt_compat import QtCore, QtWidgets, maya_main_window, qt_enum
from .ui.canvas import BlueprintCanvasWidget


WINDOW_OBJECT_NAME = "MayaBlueprintToolboxWindow"

_window_instance = None


class BlueprintToolboxWindow(QtWidgets.QDialog):
    """Top-level toolbox window that hosts the node canvas."""

    def __init__(self, parent=None):
        super(BlueprintToolboxWindow, self).__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle("Maya 蓝图工具盒")
        self.resize(1180, 760)

        window_flag = qt_enum(
            (QtCore.Qt, "WindowType.Window"),
            (QtCore.Qt, "Window"),
        )
        self.setWindowFlags(self.windowFlags() | window_flag)

        self.canvas_widget = BlueprintCanvasWidget(self)
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas_widget)


def show():
    """Show the toolbox window inside Maya."""
    global _window_instance

    if _window_instance is not None:
        try:
            _window_instance.close()
            _window_instance.deleteLater()
        except RuntimeError:
            pass

    _window_instance = BlueprintToolboxWindow(parent=maya_main_window())
    _window_instance.show()
    _window_instance.raise_()
    _window_instance.activateWindow()
    return _window_instance
