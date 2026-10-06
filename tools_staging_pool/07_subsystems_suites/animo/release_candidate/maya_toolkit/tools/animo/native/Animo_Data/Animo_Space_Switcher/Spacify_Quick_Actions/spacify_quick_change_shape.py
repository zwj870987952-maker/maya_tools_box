# Quick-menu window: "Change Shape" -- lets you pick the exact control
# shape you want for the selection, instead of Spacify's normal toggle
# behavior (which just steps to "whatever shape comes next" each click).
#
# This does NOT modify ChangeCtrlShape.py. It reuses that file's own shape
# builders (create_cube, create_plus, create_circle, ...) and the same
# bounding-box rescale math changeCtrlShape() uses, so a picked shape ends
# up the same size/orientation as the toggle would have produced -- it just
# lets you jump straight to the one you want.

import maya.OpenMayaUI as omui
import maya.cmds as cmds

try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance

import ChangeCtrlShape as CCS
from dpi_scale import dpi

WINDOW_OBJECT_NAME = "SpacifyChangeShapeUIWindow"

KNOWN_SUFFIXES = [
    "_cubeShape", "_plusShape", "_simpleCircleShape",
    "_circleShape", "_diamondShape", "_locatorShape",
]

SHAPE_OPTIONS = [
    ("Cube", CCS.create_cube, "_cubeShape"),
    ("Plus", CCS.create_plus, "_plusShape"),
    ("Simple Circle", CCS.create_simple_circle, "_simpleCircleShape"),
    ("Sphere", CCS.create_circle, "_circleShape"),
    ("Diamond", CCS.create_diamond, "_diamondShape"),
    ("Locator", CCS.create_locator, "_locatorShape"),
]


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def _apply_shape_to_object(sel, new_suffix_for_rename, creator_fn):
    """Same geometry-preserving rescale/rename logic as
    ChangeCtrlShape.changeCtrlShape(), just driven by an explicit target
    shape instead of the shape_map cycle lookup."""
    old_shapes = cmds.listRelatives(sel, shapes=True, fullPath=True)
    if not old_shapes:
        cmds.warning("No shapes found under " + str(sel))
        return sel

    old_cvs = CCS._gather_cvs_for_shapes(old_shapes)
    old_bbox_local = CCS._bbox_from_cvs_object_space(old_cvs)

    if old_bbox_local:
        old_min_local, old_max_local = old_bbox_local
        old_size = [
            old_max_local[0] - old_min_local[0],
            old_max_local[1] - old_min_local[1],
            old_max_local[2] - old_min_local[2],
        ]
    else:
        old_bb_world = cmds.exactWorldBoundingBox(old_shapes)
        ctrl_scale = CCS.get_control_scale_info(sel) or 1.0
        old_size = [
            (old_bb_world[3] - old_bb_world[0]) / ctrl_scale,
            (old_bb_world[4] - old_bb_world[1]) / ctrl_scale,
            (old_bb_world[5] - old_bb_world[2]) / ctrl_scale,
        ]

    short_name = sel.split('|')[-1]
    matched_suffix = None
    for suffix in KNOWN_SUFFIXES:
        if suffix in short_name:
            matched_suffix = suffix
            break

    if matched_suffix == "_cubeShape":
        cube_compensation_factor = 1.0 / 0.65
        old_size = [size * cube_compensation_factor for size in old_size]

    new_transform = creator_fn()

    new_shape_nodes = cmds.listRelatives(new_transform, shapes=True, fullPath=True) or []
    new_cvs = CCS._gather_cvs_for_shapes(new_shape_nodes)
    new_bbox_local = CCS._bbox_from_cvs_object_space(new_cvs)

    if new_bbox_local and new_cvs:
        new_min_local, new_max_local = new_bbox_local
        new_size = [
            new_max_local[0] - new_min_local[0],
            new_max_local[1] - new_min_local[1],
            new_max_local[2] - new_min_local[2],
        ]

        if CCS.is_symmetric_shape(new_suffix_for_rename):
            max_old_size = max(old_size)
            max_new_size = max(new_size)
            uniform_scale = max_old_size / max_new_size if max_new_size != 0 else 1.0
            scale_factors = [uniform_scale, uniform_scale, uniform_scale]
        else:
            scale_factors = [
                (old_size[0] / new_size[0]) if new_size[0] != 0 else 1.0,
                (old_size[1] / new_size[1]) if new_size[1] != 0 else 1.0,
                (old_size[2] / new_size[2]) if new_size[2] != 0 else 1.0,
            ]

        if new_suffix_for_rename == "_cubeShape":
            cube_scale_factor = 0.65
            scale_factors = [sf * cube_scale_factor for sf in scale_factors]

        pivot = [
            (new_min_local[0] + new_max_local[0]) / 2.0,
            (new_min_local[1] + new_max_local[1]) / 2.0,
            (new_min_local[2] + new_max_local[2]) / 2.0,
        ]

        for cv in new_cvs:
            pos = cmds.xform(cv, q=True, t=True, os=True)
            new_pos = [
                pivot[0] + (pos[0] - pivot[0]) * scale_factors[0],
                pivot[1] + (pos[1] - pivot[1]) * scale_factors[1],
                pivot[2] + (pos[2] - pivot[2]) * scale_factors[2],
            ]
            cmds.xform(cv, os=True, t=new_pos)

    if old_shapes:
        try:
            cmds.delete(old_shapes)
        except Exception:
            pass

    new_shapes_after_scale = cmds.listRelatives(new_transform, shapes=True, fullPath=True) or []
    if new_shapes_after_scale:
        for new_shape in new_shapes_after_scale:
            try:
                cmds.parent(new_shape, sel, r=True, s=True)
            except Exception:
                pass

    try:
        cmds.delete(new_transform)
    except Exception:
        pass

    short_name = sel.split('|')[-1]
    base_name = short_name
    if matched_suffix and matched_suffix in short_name:
        idx = short_name.rfind(matched_suffix)
        if idx != -1:
            base_name = short_name[:idx]

    new_short_name = base_name + new_suffix_for_rename

    try:
        renamed_obj = cmds.rename(sel, new_short_name)
    except Exception:
        renamed_obj = sel

    CCS.lock_and_hide_channels(renamed_obj)

    try:
        cmds.select(renamed_obj, r=True)
    except Exception:
        pass

    return renamed_obj


def apply_shape_to_selection(new_suffix_for_rename, creator_fn):
    cmds.undoInfo(openChunk=True, chunkName="Spacify Change Shape")
    try:
        try:
            CCS.cv_selected()
        except Exception:
            pass

        sel = cmds.ls(sl=True, type='transform')
        curve_loc_list = [s for s in sel if CCS.is_only_curves_and_locators_selected(s)]

        if not curve_loc_list:
            cmds.warning("No curves or locators selected.")
            return

        new_selections = []
        for obj in curve_loc_list:
            try:
                if cmds.referenceQuery(obj, isNodeReferenced=True):
                    cmds.warning("Skipping referenced object: " + str(obj))
                    new_selections.append(obj)
                    continue
            except Exception:
                pass

            new_obj = _apply_shape_to_object(obj, new_suffix_for_rename, creator_fn)
            try:
                cmds.setAttr(new_obj + ".displayHandle", 1)
            except Exception:
                pass
            new_selections.append(new_obj or obj)

        cmds.select(new_selections, r=True)
        CCS.set_always_draw_on_top_for_controls()
        CCS.make_nurbs_curve_thicker(line_width_increase=3.0)
        CCS.show_nurbs_curves_in_all_viewports()
    except Exception as e:
        cmds.warning("Error changing shape: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass


class ChangeShapeUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ChangeShapeUI, self).__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle("Change Shape")
        self.setMinimumWidth(dpi(230))
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet("background-color: #3a3a3a;")
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(12))
        layout.setSpacing(dpi(8))

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(dpi(6))

        button_style = """
            QPushButton {{
                background-color: #4A4A4A; border: none; color: white;
                border-radius: 5px; font-size: 8pt; font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{ background-color: #575757; }}
            QPushButton:pressed {{ background-color: #3A3A3A; }}
        """.format(dpi(8), dpi(6))

        for i, (label_text, creator_fn, suffix) in enumerate(SHAPE_OPTIONS):
            btn = QtWidgets.QPushButton(label_text)
            btn.setMinimumHeight(dpi(32))
            btn.setStyleSheet(button_style)
            btn.clicked.connect(
                lambda checked=False, fn=creator_fn, sfx=suffix: apply_shape_to_selection(sfx, fn)
            )
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)


def show_change_shape_ui():
    maya_main = get_maya_main_window()

    for child in maya_main.children():
        try:
            if child.objectName() == WINDOW_OBJECT_NAME:
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue

    ui = ChangeShapeUI(parent=maya_main)
    ui.show()
    return ui


show_change_shape_ui()
