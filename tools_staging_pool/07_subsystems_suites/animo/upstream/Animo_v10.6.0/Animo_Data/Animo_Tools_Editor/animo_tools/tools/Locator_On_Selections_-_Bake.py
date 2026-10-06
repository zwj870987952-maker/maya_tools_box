import maya.cmds as cmds
import maya.mel as mel
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


def _sample_component_rotation(shape, node_type, pos):
    if node_type not in ("mesh", "nurbsSurface") or not pos:
        return None

    target_transform = _get_target_transform(shape)
    temp_locator = cmds.spaceLocator(name="tempRotationSample#")[0]
    cmds.xform(temp_locator, worldSpace=True, translation=pos[:3])

    rotation = None
    constraint = None
    try:
        constraint = cmds.normalConstraint(target_transform, temp_locator)[0]
        rotation = cmds.getAttr(temp_locator + ".rotate")[0]
    except Exception:
        rotation = None
    finally:
        if constraint and cmds.objExists(constraint):
            cmds.delete(constraint)
        if cmds.objExists(temp_locator):
            cmds.delete(temp_locator)

    return rotation


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
    uv_sample = None
    component_kind = _classify_component(item)
    if component_kind in ("edge", "face"):
        uv_sample = _get_component_uv_sample(item, component_kind)

    pos = _get_component_position(item, uv_sample)

    if not pos or len(pos) < 3:
        cmds.warning("Could not resolve a world position for '{0}'.".format(item))
        return None, None

    locator = cmds.spaceLocator(name="{0}_locator#".format(item.split(".")[0].split("|")[-1]))[0]
    cmds.xform(locator, worldSpace=True, translation=pos[:3])

    shape = _resolve_component_shape(item)
    node_type = None
    try:
        node_type = cmds.nodeType(shape)
    except Exception:
        node_type = None

    rotation = _sample_component_rotation(shape, node_type, pos)
    if rotation:
        cmds.xform(locator, worldSpace=True, rotation=rotation)

    return locator, uv_sample


def _get_bake_time_range():
    try:
        playback_slider = mel.eval('global string $gPlayBackSlider; $temp=$gPlayBackSlider')
        time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        if time_range and (time_range[1] - time_range[0]) > 1:
            return time_range[0], time_range[1] - 1
    except Exception:
        pass

    try:
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        return start, end
    except Exception:
        current = cmds.currentTime(query=True)
        return current, current


def _bake_component_locators(component_entries, start_frame, end_frame):
    frame = start_frame
    while frame <= end_frame:
        cmds.currentTime(frame)

        for locator, item, shape, node_type, uv_sample in component_entries:
            pos = _get_component_position(item, uv_sample)
            if pos and len(pos) >= 3:
                cmds.setAttr(locator + ".translateX", pos[0])
                cmds.setAttr(locator + ".translateY", pos[1])
                cmds.setAttr(locator + ".translateZ", pos[2])
                cmds.setKeyframe(
                    locator,
                    attribute=["translateX", "translateY", "translateZ"],
                    time=frame
                )

            rotation = _sample_component_rotation(shape, node_type, pos)
            if rotation:
                cmds.setAttr(locator + ".rotateX", rotation[0])
                cmds.setAttr(locator + ".rotateY", rotation[1])
                cmds.setAttr(locator + ".rotateZ", rotation[2])
                cmds.setKeyframe(
                    locator,
                    attribute=["rotateX", "rotateY", "rotateZ"],
                    time=frame
                )

        frame += 1


def bake_locators():
    selection = cmds.ls(selection=True, flatten=True)

    if not selection:
        cmds.warning("Nothing is selected. Select objects or components first.")
        return []

    cmds.undoInfo(openChunk=True)
    created_locators = []
    object_locators = []
    object_constraints = []
    component_entries = []
    original_time = cmds.currentTime(query=True)

    try:
        for item in selection:
            if "." in item:
                locator = None
                uv_sample = None
                try:
                    locator, uv_sample = _create_locator_for_component(item)
                except Exception:
                    cmds.warning("Failed to create a locator for '{0}'.".format(item))
                    locator = None

                if locator:
                    shape = _resolve_component_shape(item)
                    node_type = None
                    try:
                        node_type = cmds.nodeType(shape)
                    except Exception:
                        node_type = None

                    component_entries.append((locator, item, shape, node_type, uv_sample))
                    created_locators.append(locator)
            else:
                locator = None
                try:
                    locator = _create_locator_for_object(item)
                except Exception:
                    cmds.warning("Failed to create a locator for '{0}'.".format(item))
                    locator = None

                if locator:
                    constraint = None
                    try:
                        constraint = cmds.parentConstraint(item, locator, maintainOffset=True)[0]
                    except Exception:
                        cmds.warning("Could not constrain locator to '{0}'.".format(item))
                        constraint = None

                    if constraint:
                        object_constraints.append(constraint)

                    object_locators.append(locator)
                    created_locators.append(locator)

        if not created_locators:
            cmds.warning("No locators were created from the current selection.")
            return []

        start_time, end_time = _get_bake_time_range()
        start_frame = int(round(start_time))
        end_frame = int(round(end_time))

        original_mode = None
        try:
            mode_query = cmds.evaluationManager(query=True, mode=True)
            if mode_query:
                original_mode = mode_query[0]
        except Exception:
            original_mode = None

        cmds.refresh(suspend=True)
        cmds.evaluationManager(mode="off")
        try:
            if object_constraints:
                cmds.bakeResults(
                    object_locators,
                    simulation=True,
                    time=(start_time, end_time),
                    sampleBy=1,
                    oversamplingRate=1,
                    disableImplicitControl=True,
                    preserveOutsideKeys=True,
                    sparseAnimCurveBake=False,
                    removeBakedAttributeFromLayer=False,
                    removeBakedAnimFromLayer=False,
                    bakeOnOverrideLayer=False,
                    minimizeRotation=True,
                    controlPoints=False,
                    shape=True
                )

                for constraint in object_constraints:
                    if constraint and cmds.objExists(constraint):
                        cmds.delete(constraint)

            if component_entries:
                _bake_component_locators(component_entries, start_frame, end_frame)
        except Exception:
            cmds.warning("Baking failed partway through.")
        finally:
            cmds.currentTime(original_time)
            cmds.refresh(suspend=False)
            if original_mode:
                cmds.evaluationManager(mode=original_mode)

        cmds.select(created_locators, replace=True)
    finally:
        cmds.undoInfo(closeChunk=True)

    _force_show_locators_in_viewports()

    return created_locators


def bake_locators_ui(*args):
    bake_locators()


bake_locators()