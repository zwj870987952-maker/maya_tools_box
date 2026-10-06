# Quick-menu window: "Ctrls Size" -- a small floating tool with a slider
# that behaves exactly like the "Size" slider on the full Spacify UI
# (same live drag-to-scale behavior via spacify_actions.scale_changed /
# scale_released, same 50/100/150/200% presets via
# spacify_actions.set_scale_preset), without needing the whole Spacify
# panel open. Stays open as its own window until you close it.

import maya.OpenMayaUI as omui

try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance

import spacify_actions
from dpi_scale import dpi

WINDOW_OBJECT_NAME = "SpacifyCtrlsSizeUIWindow"


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class CtrlsSizeUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CtrlsSizeUI, self).__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle("Ctrls Size")
        self.setMinimumWidth(dpi(230))
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet("background-color: #3a3a3a;")
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(12))
        layout.setSpacing(dpi(8))

        header = QtWidgets.QHBoxLayout()
        size_label = QtWidgets.QLabel("Size")
        size_label.setStyleSheet("color: white; font-size: 9pt; font-weight: 700;")
        header.addWidget(size_label)
        header.addStretch()

        self.scale_label = QtWidgets.QLabel("100%")
        self.scale_label.setStyleSheet("color: #1565C0; font-size: 8pt; font-weight: 700;")
        header.addWidget(self.scale_label)
        layout.addLayout(header)

        self.scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.scale_slider.setRange(0, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.setMinimumHeight(dpi(24))
        self.scale_slider.setStyleSheet("""
            QSlider::groove:horizontal {{ background: #2A2A2A; height: {0}px; border-radius: 3px; }}
            QSlider::handle:horizontal {{ background: #1565C0; width: {1}px; margin: -{2}px 0; border-radius: 6px; }}
        """.format(dpi(6), dpi(12), dpi(3)))
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        self.scale_slider.sliderReleased.connect(self.on_scale_released)
        layout.addWidget(self.scale_slider)

        preset_row = QtWidgets.QHBoxLayout()
        preset_row.setSpacing(dpi(4))
        for preset in (50, 75, 150, 200):
            btn = QtWidgets.QPushButton("{0}%".format(preset))
            btn.setMinimumHeight(dpi(26))
            btn.setStyleSheet("""
                QPushButton {{
                    background-color: #2A2A2A; border: none; color: white;
                    border-radius: 4px; font-size: 7pt; font-weight: 700;
                    padding: {0}px {1}px;
                }}
                QPushButton:hover {{ background-color: #353535; }}
                QPushButton:pressed {{ background-color: #1F1F1F; }}
            """.format(dpi(4), dpi(8)))
            btn.clicked.connect(lambda checked=False, p=preset: self.on_preset(p))
            preset_row.addWidget(btn)
        layout.addLayout(preset_row)

    def on_scale_changed(self, value):
        spacify_actions.scale_changed(value, self.scale_label)

    def on_scale_released(self):
        spacify_actions.scale_released(self.scale_slider, self.scale_label)

    def on_preset(self, value):
        spacify_actions.set_scale_preset(value, self.scale_slider, self.scale_label)


def show_ctrls_size_ui():
    maya_main = get_maya_main_window()

    for child in maya_main.children():
        try:
            if child.objectName() == WINDOW_OBJECT_NAME:
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue

    ui = CtrlsSizeUI(parent=maya_main)
    ui.show()
    return ui


show_ctrls_size_ui()
