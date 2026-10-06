from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
from functools import partial
from spacify_core import QtWidgets, QtCore
from spacify_buttons import create_small_button, create_red_button
from dpi_scale import dpi
import spacify_actions
import AttributeSpaceSwitcher

_active_chunk_depth = 0


def create_rotation_tab(parent):
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    layout.setContentsMargins(0, dpi(11), 0, 0)
    layout.setSpacing(dpi(6))

    # ============ GROUP 1: Rotate Order ============

    parent.ro_label = QtWidgets.QLabel("Select an Object!")
    parent.ro_label.setAlignment(QtCore.Qt.AlignCenter)
    parent.ro_label.setMinimumHeight(dpi(32))
    parent.ro_label.setStyleSheet("""
        QLabel {{
            background-color: #2A2A2A;
            color: white;
            font-weight: 700;
            padding: {0}px;
            border-radius: 6px;
            font-size: 8pt;
        }}
    """.format(dpi(7)))
    layout.addWidget(parent.ro_label)

    layout.addSpacing(dpi(6))

    parent.ro_buttons = {}

    ro_container1 = QtWidgets.QWidget()
    ro_layout1 = QtWidgets.QHBoxLayout(ro_container1)
    ro_layout1.setContentsMargins(0, 0, 0, 0)
    ro_layout1.setSpacing(dpi(6))

    for label in ["XYZ", "YZX", "ZXY"]:
        btn = create_small_button(label, partial(on_ro_button_clicked, parent, label))
        parent.ro_buttons[label] = btn
        ro_layout1.addWidget(btn)
    layout.addWidget(ro_container1)

    ro_container2 = QtWidgets.QWidget()
    ro_layout2 = QtWidgets.QHBoxLayout(ro_container2)
    ro_layout2.setContentsMargins(0, 0, 0, 0)
    ro_layout2.setSpacing(dpi(6))

    for label in ["XZY", "YXZ", "ZYX"]:
        btn = create_small_button(label, partial(on_ro_button_clicked, parent, label))
        parent.ro_buttons[label] = btn
        ro_layout2.addWidget(btn)
    layout.addWidget(ro_container2)

    layout.addSpacing(dpi(6))

    parent.set_best_btn = create_red_button("Set to Best", partial(on_set_best_clicked, parent))
    layout.addWidget(parent.set_best_btn)

    # ============ SEPARATOR between Group 1 and 2 ============
    layout.addSpacing(dpi(14))
    separator = QtWidgets.QFrame()
    separator.setFrameShape(QtWidgets.QFrame.HLine)
    separator.setStyleSheet("background-color: #4A3A3A; max-height: 1px; margin: 0px;")
    layout.addWidget(separator)
    layout.addSpacing(dpi(14))

    # ============ GROUP 2: Attribute Space Switcher ============

    attr_container = QtWidgets.QWidget()
    attr_layout = QtWidgets.QHBoxLayout(attr_container)
    attr_layout.setContentsMargins(0, 0, 0, 0)
    attr_layout.setSpacing(dpi(6))

    attr_label = QtWidgets.QLabel("Attribute:")
    attr_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; font-weight: 700;")
    attr_layout.addWidget(attr_label)
    attr_layout.addStretch()

    parent.refresh_btn = QtWidgets.QPushButton("Refresh")
    parent.refresh_btn.setMinimumHeight(dpi(29))
    parent.refresh_btn.setStyleSheet("""
        QPushButton {{
            background-color: #C94A47;
            border: none;
            color: white;
            border-radius: 6px;
            font-size: 8pt;
            padding: 0px {0}px;
            font-weight: 700;
        }}
        QPushButton:hover {{ background-color: #D95A57; }}
        QPushButton:pressed {{ background-color: #B93A37; }}
    """.format(dpi(11)))
    parent.refresh_btn.clicked.connect(partial(on_refresh_clicked, parent))
    attr_layout.addWidget(parent.refresh_btn)
    layout.addWidget(attr_container)

    layout.addSpacing(dpi(4))

    parent.attr_combo = QtWidgets.QComboBox()
    parent.attr_combo.addItem("No Attributes")
    parent.attr_combo.setMinimumHeight(dpi(33))
    parent.attr_combo.setStyleSheet("""
        QComboBox {{
            background-color: #3D2A2A;
            border: none;
            color: white;
            border-radius: 6px;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox::down-arrow {{ image: none; border: none; }}
        QComboBox QAbstractItemView {{
            background-color: #3D2A2A;
            color: white;
            selection-background-color: #C94A47;
            border: none;
            font-size: 8pt;
        }}
    """.format(dpi(5), dpi(11)))
    parent.attr_combo.currentTextChanged.connect(partial(on_attr_changed, parent))
    layout.addWidget(parent.attr_combo)

    layout.addSpacing(dpi(8))

    value_label = QtWidgets.QLabel("New Value:")
    value_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; padding-left: 2px; font-weight: 700;")
    layout.addWidget(value_label)

    layout.addSpacing(dpi(4))

    parent.value_combo = QtWidgets.QComboBox()
    parent.value_combo.addItem("No Values")
    parent.value_combo.setMinimumHeight(dpi(33))
    parent.value_combo.setStyleSheet("""
        QComboBox {{
            background-color: #3D2A2A;
            border: none;
            color: white;
            border-radius: 6px;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox::down-arrow {{ image: none; border: none; }}
        QComboBox QAbstractItemView {{
            background-color: #3D2A2A;
            color: white;
            selection-background-color: #C94A47;
            border: none;
            font-size: 8pt;
        }}
    """.format(dpi(5), dpi(11)))
    layout.addWidget(parent.value_combo)

    layout.addSpacing(dpi(8))

    parent.current_frame_check = QtWidgets.QCheckBox("Only Current Frame")
    parent.current_frame_check.setStyleSheet("""
        QCheckBox {{
            color: #AAAAAA;
            font-size: 8pt;
            spacing: {0}px;
        }}
        QCheckBox::indicator {{
            width: {1}px;
            height: {1}px;
            border-radius: 4px;
            background-color: #2A2A2A;
            border: none;
        }}
        QCheckBox::indicator:checked {{
            background-color: #1565C0;
        }}
    """.format(dpi(7), dpi(18)))
    layout.addWidget(parent.current_frame_check)

    layout.addSpacing(dpi(8))

    parent.apply_attr_btn = create_red_button("A P P L Y", partial(on_apply_clicked, parent))
    layout.addWidget(parent.apply_attr_btn)

    AttributeSpaceSwitcher.initialize_ui_state(
        parent.attr_combo,
        parent.value_combo,
        parent.refresh_btn,
        parent.apply_attr_btn,
        parent.current_frame_check,
        parent.ro_label
    )

    setup_selection_callback(parent)

    layout.addStretch()
    return tab


def on_attr_changed(parent, text=None):
    AttributeSpaceSwitcher.update_value_menu(parent.attr_combo)


def on_ro_button_clicked(parent, label):
    global _active_chunk_depth
    cmds.undoInfo(openChunk=True)
    _active_chunk_depth += 1
    try:
        AttributeSpaceSwitcher.change_ro_enhanced(label.lower())
        update_ro_display(parent)
    finally:
        _active_chunk_depth -= 1
        cmds.undoInfo(closeChunk=True)
        spacify_actions.clear_focus()


def on_set_best_clicked(parent):
    global _active_chunk_depth
    cmds.undoInfo(openChunk=True)
    _active_chunk_depth += 1
    try:
        AttributeSpaceSwitcher.set_each_object_to_best_ro()
        update_ro_display(parent)
    finally:
        _active_chunk_depth -= 1
        cmds.undoInfo(closeChunk=True)
        spacify_actions.clear_focus()


def on_refresh_clicked(parent):
    AttributeSpaceSwitcher.refresh_ui(
        parent.attr_combo,
        parent.value_combo,
        parent.refresh_btn,
        parent.apply_attr_btn,
        parent.current_frame_check,
        parent.ro_label
    )
    update_ro_display(parent)
    spacify_actions.clear_focus()


def on_apply_clicked(parent):
    global _active_chunk_depth
    cmds.undoInfo(openChunk=True)
    _active_chunk_depth += 1
    try:
        AttributeSpaceSwitcher.apply_change(parent.attr_combo, parent.value_combo, parent.current_frame_check)
    finally:
        _active_chunk_depth -= 1
        cmds.undoInfo(closeChunk=True)
    spacify_actions.clear_focus()


def update_ro_display(parent):
    sel = cmds.ls(sl=True)
    
    default_style = """
        QPushButton {
            background-color: #3D2A2A;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #4D3A3A; }
        QPushButton:pressed { background-color: #2D1A1A; }
    """
    
    green_style = """
        QPushButton {
            background-color: #2A5A2A;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #3A6A3A; }
        QPushButton:pressed { background-color: #1A4A1A; }
    """
    
    for btn in parent.ro_buttons.values():
        btn.setStyleSheet(default_style)
    
    if not sel:
        parent.ro_label.setText("Select an Object!")
        return
    
    if len(sel) > 1:
        parent.ro_label.setText("Multi-selection")
        return
    
    obj = sel[0]
    
    if not cmds.objExists(obj + ".rotateOrder"):
        parent.ro_label.setText("No RO on object")
        return
    
    try:
        ro_index = cmds.getAttr("{0}.rotateOrder".format(obj))
        ro_names = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
        current_ro = ro_names[ro_index]
        
        current_ro_str = AttributeSpaceSwitcher.rotate_order_dict.get(ro_index, "xyz")
        mid_axis = current_ro_str[1].upper()
        rotate_attr = obj + ".rotate" + mid_axis
        
        current_risk = 0.0
        if cmds.objExists(rotate_attr):
            try:
                mid_value = cmds.getAttr(rotate_attr)
                current_risk = AttributeSpaceSwitcher.gimbal_risk(mid_value)
            except Exception:
                pass
        
        parent.ro_label.setText("{0} ({1:.0f}% risk)".format(current_ro, current_risk))
    except:
        parent.ro_label.setText("Select an Object!")
        return
    
    try:
        if _active_chunk_depth <= 0:
            cmds.undoInfo(stateWithoutFlush=False)
        best_ro, best_risk = AttributeSpaceSwitcher.evaluate_best_ro_with_preserve(obj)
        if _active_chunk_depth <= 0:
            cmds.undoInfo(stateWithoutFlush=True)
        if best_ro is not None:
            best_ro_str = AttributeSpaceSwitcher.rotate_order_dict[best_ro].upper()
            if best_ro_str in parent.ro_buttons:
                parent.ro_buttons[best_ro_str].setStyleSheet(green_style)
    except:
        if _active_chunk_depth <= 0:
            cmds.undoInfo(stateWithoutFlush=True)
        pass


def setup_selection_callback(parent):
    if not hasattr(parent, '_script_jobs'):
        parent._script_jobs = []
    
    job_id = cmds.scriptJob(
        event=["SelectionChanged", partial(on_selection_changed, parent)],
        protected=True
    )
    parent._script_jobs.append(job_id)
    
    update_ro_display(parent)


def on_selection_changed(parent):
    update_ro_display(parent)
    AttributeSpaceSwitcher.refresh_ui()