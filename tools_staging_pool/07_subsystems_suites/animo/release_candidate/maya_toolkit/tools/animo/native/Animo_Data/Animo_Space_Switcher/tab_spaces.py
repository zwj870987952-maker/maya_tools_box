from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
from spacify_core import QtWidgets, QtCore, SPACIFY_STATE
from spacify_buttons import create_compact_gradient_button
from dpi_scale import dpi
import CameraSpace
import ChangeCtrlShape


def create_spaces_tab(parent):
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    layout.setContentsMargins(0, dpi(6), 0, 0)
    layout.setSpacing(dpi(6))

    only_keys_container = QtWidgets.QWidget()
    only_keys_layout = QtWidgets.QHBoxLayout(only_keys_container)
    only_keys_layout.setContentsMargins(0, 0, 0, dpi(4))
    only_keys_layout.setSpacing(dpi(6))

    parent.only_keys_checkbox = QtWidgets.QCheckBox("Only Keys")
    parent.only_keys_checkbox.setChecked(SPACIFY_STATE.get("only_keys", False))
    parent.only_keys_checkbox.setStyleSheet("""
        QCheckBox {{
            color: #AAAAAA;
            font-size: 9pt;
            font-weight: 700;
            spacing: {0}px;
        }}
        QCheckBox::indicator {{
            width: {1}px;
            height: {1}px;
            border-radius: 3px;
            border: 1px solid #555555;
            background-color: #2A2A2A;
        }}
        QCheckBox::indicator:checked {{
            background-color: #1565C0;
            border: 1px solid #1976D2;
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid #1976D2;
        }}
    """.format(dpi(5), dpi(14)))
    parent.only_keys_checkbox.setToolTip("When checked, bakes only at existing keyframe times instead of every frame")
    parent.only_keys_checkbox.toggled.connect(lambda checked: SPACIFY_STATE.update({"only_keys": checked}))
    only_keys_layout.addWidget(parent.only_keys_checkbox)
    only_keys_layout.addStretch()
    layout.addWidget(only_keys_container)

    button_colors = [
        ("#1976D2", "#42A5F5", "#1565C0"),
        ("#1870C8", "#3D9EEE", "#145BB6"),
        ("#166ABE", "#3897E7", "#1351AC"),
        ("#1564B4", "#3390E0", "#1247A2"),
        ("#145EAA", "#2E89D9", "#113D98"),
        ("#1358A0", "#2982D2", "#10338E"),
        ("#125296", "#247BD0", "#0F2984"),
        ("#114C8C", "#1F74C9", "#0E1F7A"),
    ]

    button_data = [
        ("W O R L D", parent.execute_world, 0),
        ("N E W   P I V O T", parent.execute_new_pivot, 1),
        ("R E L A T I V E", parent.execute_relative, 2),
        ("W O R L D   O R I E N T", parent.execute_world_orient, 3),
        ("G R O U P", parent.execute_group, 4),
        ("A I M", parent.execute_aim, 5),
        ("T E M P   I K", parent.execute_temp_ik, 6),
        ("F K   C H A I N", parent.execute_fk, 7),
    ]

    for i in range(0, len(button_data), 2):
        row_container = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(dpi(6))

        label1, callback1, color_idx1 = button_data[i]
        btn1 = create_compact_gradient_button(label1, button_colors[color_idx1], callback1)
        row_layout.addWidget(btn1)

        if i + 1 < len(button_data):
            label2, callback2, color_idx2 = button_data[i + 1]
            btn2 = create_compact_gradient_button(label2, button_colors[color_idx2], callback2)
            row_layout.addWidget(btn2)

        layout.addWidget(row_container)

    layout.addSpacing(dpi(10))

    assign_label = QtWidgets.QLabel("Assign Camera")
    assign_label.setStyleSheet("color: #AAAAAA; font-size: 9pt; font-weight: 700;")
    layout.addWidget(assign_label)

    layout.addSpacing(dpi(4))

    camera_container = QtWidgets.QWidget()
    camera_layout = QtWidgets.QHBoxLayout(camera_container)
    camera_layout.setContentsMargins(0, 0, 0, 0)
    camera_layout.setSpacing(dpi(6))

    parent.assign_camera_btn = QtWidgets.QPushButton("Assign")
    parent.assign_camera_btn.setMinimumHeight(dpi(28))
    parent.assign_camera_btn.setStyleSheet("""
        QPushButton {{
            background-color: #2A2A2A;
            border: none;
            color: white;
            border-radius: 4px;
            font-size: 8pt;
            font-weight: 700;
            padding: {0}px {1}px;
        }}
        QPushButton:hover {{ background-color: #353535; }}
        QPushButton:pressed {{ background-color: #1F1F1F; }}
    """.format(dpi(4), dpi(8)))
    parent.assign_camera_btn.clicked.connect(parent.assign_camera)
    camera_layout.addWidget(parent.assign_camera_btn, 1)

    parent.camera_field = QtWidgets.QLineEdit()
    parent.camera_field.setPlaceholderText("persp")
    parent.camera_field.setReadOnly(True)
    parent.camera_field.setMinimumHeight(dpi(28))
    parent.camera_field.setStyleSheet("""
        QLineEdit {{
            background-color: #2A2A2A;
            border: none;
            color: #DDDDDD;
            border-radius: 4px;
            padding-left: {0}px;
            font-size: 9pt;
            font-weight: 700;
        }}
    """.format(dpi(7)))
    camera_layout.addWidget(parent.camera_field, 2)
    layout.addWidget(camera_container)

    SPACIFY_STATE["camera_field"] = parent.camera_field

    saved_camera = CameraSpace.load_camera_from_network()
    if saved_camera and cmds.objExists(saved_camera):
        SPACIFY_STATE["camera"] = saved_camera
        short_name = saved_camera.split('|')[-1]
        parent.camera_field.setText(short_name)

    layout.addSpacing(dpi(8))

    parent.camera_space_btn = QtWidgets.QPushButton("C A M E R A   S P A C E")
    parent.camera_space_btn.setMinimumHeight(dpi(32))
    parent.camera_space_btn.setStyleSheet("""
        QPushButton {{
            background-color: #1565C0;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #1976D2; }}
        QPushButton:pressed {{ background-color: #0D47A1; }}
    """.format(dpi(6), dpi(10)))
    parent.camera_space_btn.clicked.connect(parent.create_camera_space)
    layout.addWidget(parent.camera_space_btn)

    layout.addSpacing(dpi(10))

    color_label = QtWidgets.QLabel("Color")
    color_label.setStyleSheet("color: white; font-size: 9pt; font-weight: 700;")
    layout.addWidget(color_label)

    layout.addSpacing(dpi(4))

    color_container = QtWidgets.QWidget()
    color_layout = QtWidgets.QHBoxLayout(color_container)
    color_layout.setContentsMargins(0, 0, 0, 0)
    color_layout.setSpacing(dpi(6))

    parent.color_button = QtWidgets.QPushButton()
    parent.color_button.setFixedSize(dpi(40), dpi(24))
    parent.color_button.setStyleSheet("background-color: rgb(255, 102, 204); border-radius: 4px;")
    parent.color_button.clicked.connect(parent.pick_color)
    color_layout.addWidget(parent.color_button)

    parent.hue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    parent.hue_slider.setRange(0, 360)
    parent.hue_slider.setValue(0)
    parent.hue_slider.setMinimumHeight(dpi(24))
    parent.hue_slider.setStyleSheet("""
        QSlider::groove:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF0000, stop:0.17 #FFFF00, stop:0.33 #00FF00,
                stop:0.5 #00FFFF, stop:0.67 #0000FF, stop:0.83 #FF00FF, stop:1 #FF0000);
            height: {0}px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: white;
            width: {1}px;
            margin: -{2}px 0;
            border-radius: 6px;
        }}
    """.format(dpi(6), dpi(12), dpi(3)))
    parent.hue_slider.valueChanged.connect(parent.hue_changed)
    color_layout.addWidget(parent.hue_slider)
    layout.addWidget(color_container)

    layout.addSpacing(dpi(8))

    size_header = QtWidgets.QWidget()
    size_header_layout = QtWidgets.QHBoxLayout(size_header)
    size_header_layout.setContentsMargins(0, 0, 0, 0)
    size_header_layout.setSpacing(0)

    size_label = QtWidgets.QLabel("Size")
    size_label.setStyleSheet("color: white; font-size: 9pt; font-weight: 700;")
    size_header_layout.addWidget(size_label)

    size_header_layout.addStretch()

    parent.scale_label = QtWidgets.QLabel("100%")
    parent.scale_label.setStyleSheet("color: #1565C0; font-size: 8pt; font-weight: 700;")
    size_header_layout.addWidget(parent.scale_label)
    layout.addWidget(size_header)

    layout.addSpacing(dpi(4))

    parent.scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    parent.scale_slider.setRange(0, 200)
    parent.scale_slider.setValue(100)
    parent.scale_slider.setMinimumHeight(dpi(24))
    parent.scale_slider.setStyleSheet("""
        QSlider::groove:horizontal {{
            background: #2A2A2A;
            height: {0}px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #1565C0;
            width: {1}px;
            margin: -{2}px 0;
            border-radius: 6px;
        }}
    """.format(dpi(6), dpi(12), dpi(3)))
    parent.scale_slider.valueChanged.connect(parent.scale_changed)
    parent.scale_slider.sliderReleased.connect(parent.scale_released)
    layout.addWidget(parent.scale_slider)

    layout.addSpacing(dpi(6))

    preset_container = QtWidgets.QWidget()
    preset_layout = QtWidgets.QHBoxLayout(preset_container)
    preset_layout.setContentsMargins(0, 0, 0, 0)
    preset_layout.setSpacing(dpi(4))

    for preset in [50, 100, 150, 200]:
        btn = QtWidgets.QPushButton("{0}%".format(preset))
        btn.setMinimumHeight(dpi(26))
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #2A2A2A;
                border: none;
                color: white;
                border-radius: 4px;
                font-size: 7pt;
                font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{ background-color: #353535; }}
            QPushButton:pressed {{ background-color: #1F1F1F; }}
        """.format(dpi(4), dpi(8)))
        btn.clicked.connect(lambda checked, p=preset: parent.set_scale_preset(p))
        preset_layout.addWidget(btn)
    layout.addWidget(preset_container)

    layout.addSpacing(dpi(10))

    parent.change_shape_btn = QtWidgets.QPushButton("C H A N G E   S H A P E")
    parent.change_shape_btn.setMinimumHeight(dpi(32))
    parent.change_shape_btn.setStyleSheet("""
        QPushButton {{
            background-color: #1565C0;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #1976D2; }}
        QPushButton:pressed {{ background-color: #0D47A1; }}
    """.format(dpi(6), dpi(10)))
    parent.change_shape_btn.clicked.connect(lambda: ChangeCtrlShape.change_selected_shape())
    layout.addWidget(parent.change_shape_btn)

    layout.addSpacing(dpi(6))

    parent.clean_bake_btn = QtWidgets.QPushButton("C L E A N   A N D   B A K E")
    parent.clean_bake_btn.setMinimumHeight(dpi(38))
    parent.clean_bake_btn.setStyleSheet("""
        QPushButton {{
            background-color: #0D47A1;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #1565C0; }}
        QPushButton:pressed {{ background-color: #01579B; }}
    """.format(dpi(5), dpi(10)))
    parent.clean_bake_btn.clicked.connect(parent.clean_and_bake_wrapper)
    layout.addWidget(parent.clean_bake_btn)

    layout.addStretch()
    return tab
