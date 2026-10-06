import maya.cmds as cmds


def _get_locator_shapes(transform):
    try:
        return cmds.listRelatives(transform, shapes=True, type='locator', fullPath=True) or []
    except Exception:
        return []


def _get_curve_shapes(transform):
    try:
        return cmds.listRelatives(transform, shapes=True, type='nurbsCurve', fullPath=True) or []
    except Exception:
        return []


def _scale_locator_shape(shape, factor):
    try:
        current_scale = cmds.getAttr(shape + '.localScaleX')
    except Exception:
        return

    new_scale = current_scale * factor
    try:
        cmds.setAttr(shape + '.localScaleX', new_scale)
        cmds.setAttr(shape + '.localScaleY', new_scale)
        cmds.setAttr(shape + '.localScaleZ', new_scale)
    except Exception:
        pass


def _scale_curve_shape(transform, shape, factor):
    try:
        cvs = cmds.ls(shape + '.cv[*]', flatten=True)
    except Exception:
        cvs = []

    if not cvs:
        return

    try:
        pivot = cmds.xform(transform, query=True, worldSpace=True, rotatePivot=True)
    except Exception:
        pivot = (0, 0, 0)

    try:
        cmds.scale(factor, factor, factor, cvs, relative=True, pivot=pivot)
    except Exception:
        pass


def resize_controls(factor):
    selected = cmds.ls(selection=True, type='transform')

    if not selected:
        cmds.warning("Nothing is selected. Select locators or NURBS curves first.")
        return

    found_valid = False

    cmds.undoInfo(openChunk=True)
    try:
        for obj in selected:
            for shape in _get_locator_shapes(obj):
                _scale_locator_shape(shape, factor)
                found_valid = True

            for shape in _get_curve_shapes(obj):
                _scale_curve_shape(obj, shape, factor)
                found_valid = True

        if not found_valid:
            cmds.warning("No locators or NURBS curves found in the current selection.")
    finally:
        cmds.undoInfo(closeChunk=True)


def make_controls_bigger():
    resize_controls(1.35)


def make_controls_bigger_ui(*args):
    make_controls_bigger()


make_controls_bigger()