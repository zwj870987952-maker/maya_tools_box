import maya.cmds as cmds
import maya.api.OpenMaya as om2


def _force_show_locators_in_viewports():
    panels = cmds.getPanel(type="modelPanel") or []
    for panel in panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            try:
                cmds.modelEditor(panel, edit=True, locators=True)
            except Exception:
                pass


def _resolve_component_shape(item):
    shape_name = item.split(".")[0]
    try:
        node_type = cmds.nodeType(shape_name)
    except Exception:
        node_type = None

    if node_type in ("mesh", "nurbsSurface", "nurbsCurve"):
        return shape_name

    try:
        shapes = cmds.listRelatives(shape_name, shapes=True, fullPath=True) or []
    except Exception:
        shapes = []

    return shapes[0] if shapes else shape_name


def _classify_component(item):
    if ".vtx[" in item:
        return "vertex"
    if ".e[" in item:
        return "edge"
    if ".f[" in item:
        return "face"
    if ".cv[" in item:
        return "cv"
    return "unknown"


def _get_component_world_position(item):
    pos = None
    try:
        pos = cmds.xform(item, query=True, worldSpace=True, translation=True)
    except Exception:
        pos = None

    if not pos or len(pos) < 3:
        try:
            pos = cmds.pointPosition(item, world=True)
        except Exception:
            pos = None

    return pos


def _get_component_uv_sample(item, component_kind):
    resolved_shape = _resolve_component_shape(item)
    face_id = None
    uv_components = []

    if component_kind == "edge":
        try:
            face_components = cmds.polyListComponentConversion(item, fromEdge=True, toFace=True)
            face_components = cmds.ls(face_components, flatten=True) if face_components else []
        except Exception:
            face_components = []

        if not face_components:
            return None

        try:
            face_id = int(face_components[0].split("[")[1].split("]")[0])
        except Exception:
            return None

        try:
            uv_components = cmds.polyListComponentConversion(item, fromEdge=True, toUV=True)
            uv_components = cmds.ls(uv_components, flatten=True) if uv_components else []
        except Exception:
            uv_components = []

    elif component_kind == "face":
        try:
            face_id = int(item.split("[")[1].split("]")[0])
        except Exception:
            return None

        try:
            uv_components = cmds.polyListComponentConversion(item, fromFace=True, toUV=True)
            uv_components = cmds.ls(uv_components, flatten=True) if uv_components else []
        except Exception:
            uv_components = []

    else:
        return None

    if not uv_components:
        return None

    u_total = 0.0
    v_total = 0.0
    count = 0
    for uv in uv_components:
        try:
            uv_val = cmds.polyEditUV(uv, query=True)
        except Exception:
            uv_val = None
        if uv_val and len(uv_val) >= 2:
            u_total += uv_val[0]
            v_total += uv_val[1]
            count += 1

    if count == 0:
        return None

    return resolved_shape, face_id, u_total / count, v_total / count


def _sample_point_at_uv(shape, face_id, u, v):
    try:
        selection_list = om2.MSelectionList()
        selection_list.add(shape)
        dag_path = selection_list.getDagPath(0)
        try:
            dag_path.extendToShape()
        except Exception:
            pass
        mesh_fn = om2.MFnMesh(dag_path)
        point = mesh_fn.getPointAtUV(face_id, u, v, space=om2.MSpace.kWorld)
        return [point.x, point.y, point.z]
    except Exception:
        return None


def _get_component_position(item, uv_sample):
    if uv_sample:
        shape, face_id, u, v = uv_sample
        pos = _sample_point_at_uv(shape, face_id, u, v)
        if pos:
            return pos

    return _get_component_world_position(item)


def _get_target_transform(shape):
    parent = cmds.listRelatives(shape, parent=True, fullPath=True)
    return parent[0] if parent else shape


def _create_locator_for_object(item):
    locator = cmds.spaceLocator(name="{0}_locator#".format(item.split("|")[-1]))[0]
    try:
        cmds.matchTransform(locator, item, position=True, rotation=True, scale=False)
    except Exception:
        try:
            cmds.delete(cmds.pointConstraint(item, locator, weight=1))
            cmds.delete(cmds.orientConstraint(item, locator, weight=1))
        except Exception:
            cmds.warning("Could not match transform for '{0}'.".format(item))
    return locator


def _create_locator_for_component(item):
    component_kind = _classify_component(item)
    uv_sample = None
    if component_kind in ("edge", "face"):
        uv_sample = _get_component_uv_sample(item, component_kind)

    pos = _get_component_position(item, uv_sample)

    if not pos or len(pos) < 3:
        cmds.warning("Could not resolve a world position for '{0}'.".format(item))
        return None

    locator = cmds.spaceLocator(name="{0}_locator#".format(item.split(".")[0].split("|")[-1]))[0]
    cmds.xform(locator, worldSpace=True, translation=pos[:3])

    shape = _resolve_component_shape(item)
    node_type = None
    try:
        node_type = cmds.nodeType(shape)
    except Exception:
        node_type = None

    constraint = None
    rotation_applied = False

    if node_type in ("mesh", "nurbsSurface"):
        target_transform = _get_target_transform(shape)
        try:
            constraint = cmds.normalConstraint(target_transform, locator)[0]
            rotation_applied = True
        except Exception:
            rotation_applied = False

    if constraint and cmds.objExists(constraint):
        cmds.delete(constraint)

    if not rotation_applied:
        cmds.warning(
            "Locator for '{0}' was positioned, but a matching rotation "
            "could not be determined (rotation left at default).".format(item)
        )

    return locator


def create_locators_at_selection():
    selection = cmds.ls(selection=True, flatten=True)

    if not selection:
        cmds.warning("Nothing is selected. Select objects or components first.")
        return []

    cmds.undoInfo(openChunk=True)
    created_locators = []

    try:
        for item in selection:
            locator = None
            try:
                if "." in item:
                    locator = _create_locator_for_component(item)
                else:
                    locator = _create_locator_for_object(item)
            except Exception:
                cmds.warning("Failed to create a locator for '{0}'.".format(item))
                locator = None

            if locator:
                created_locators.append(locator)

        if created_locators:
            _force_show_locators_in_viewports()
            cmds.select(created_locators, replace=True)
        else:
            cmds.warning("No locators were created from the current selection.")
    finally:
        cmds.undoInfo(closeChunk=True)

    return created_locators


def create_locators_at_selection_ui_command(*args):
    create_locators_at_selection()


create_locators_at_selection()