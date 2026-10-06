from __future__ import print_function, division, absolute_import

from spacify_core import QtWidgets, SPACIFY_STATE
from dpi_scale import dpi
import ShiftSceneKeys


def create_blue_button(text, callback):
    """Create a blue accent button for the Offset tab."""
    btn = QtWidgets.QPushButton(text)
    btn.setMinimumHeight(dpi(28))
    btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    btn.setStyleSheet("""
        QPushButton {{
            background-color: #1E88A8;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{ background-color: #2898B8; }}
        QPushButton:pressed {{ background-color: #167898; }}
    """.format(dpi(6), dpi(12)))
    if callback:
        btn.clicked.connect(callback)
    return btn


def create_animation_tab(parent):
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    layout.setContentsMargins(0, dpi(11), 0, 0)
    layout.setSpacing(dpi(6))

    # ============ GROUP 1: Frame Offset ============

    offset_label = QtWidgets.QLabel("Frame Offset:")
    offset_label.setStyleSheet("color: white; font-size: 8pt; font-weight: 700;")
    layout.addWidget(offset_label)

    layout.addSpacing(dpi(4))

    saved_offset = ShiftSceneKeys.load_offset_value()

    parent.offset_spinbox = QtWidgets.QSpinBox()
    parent.offset_spinbox.setRange(-100000, 100000)
    parent.offset_spinbox.setValue(saved_offset)
    parent.offset_spinbox.setMinimumHeight(dpi(35))
    parent.offset_spinbox.setStyleSheet("""
        QSpinBox {{
            background-color: #2A3A3D;
            border: none;
            color: white;
            border-radius: 6px;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
    """.format(dpi(5), dpi(11)))
    parent.offset_spinbox.valueChanged.connect(parent.set_offset_value)
    layout.addWidget(parent.offset_spinbox)

    layout.addSpacing(dpi(6))

    SPACIFY_STATE["offset_field"] = parent.offset_spinbox
    SPACIFY_STATE["offset_value"] = saved_offset

    parent.apply_shift_btn = create_blue_button("A P P L Y   S H I F T", parent.apply_shift)
    layout.addWidget(parent.apply_shift_btn)

    # ============ SEPARATOR between Group 1 and 2 ============
    layout.addSpacing(dpi(14))
    separator = QtWidgets.QFrame()
    separator.setFrameShape(QtWidgets.QFrame.HLine)
    separator.setStyleSheet("background-color: #3A4A4D; max-height: 1px; margin: 0px;")
    layout.addWidget(separator)
    layout.addSpacing(dpi(14))

    # ============ GROUP 2: Sequential Key Offset ============

    offset_keys_label = QtWidgets.QLabel("Sequential Key Offset:")
    offset_keys_label.setStyleSheet("color: white; font-size: 8pt; font-weight: 700;")
    layout.addWidget(offset_keys_label)

    layout.addSpacing(dpi(4))

    parent.overlap_spinbox = QtWidgets.QDoubleSpinBox()
    parent.overlap_spinbox.setRange(-1000.0, 1000.0)
    parent.overlap_spinbox.setValue(1.0)
    parent.overlap_spinbox.setDecimals(2)
    parent.overlap_spinbox.setMinimumHeight(dpi(35))
    parent.overlap_spinbox.setStyleSheet("""
        QDoubleSpinBox {{
            background-color: #2A3A3D;
            border: none;
            color: white;
            border-radius: 6px;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
    """.format(dpi(5), dpi(11)))
    layout.addWidget(parent.overlap_spinbox)

    layout.addSpacing(dpi(6))

    parent.offset_btn = create_blue_button("O F F S E T", parent.execute_sequential_offset)
    layout.addWidget(parent.offset_btn)

    layout.addStretch()
    return tab
