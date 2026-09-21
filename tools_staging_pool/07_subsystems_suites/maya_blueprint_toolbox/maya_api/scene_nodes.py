"""Scene node helpers for blueprint Maya operations."""

from .common import MayaApiError, UndoChunk, maya_modules
from .selection import replace_selection


DEFORMER_TYPES = set([
    "skinCluster",
    "blendShape",
    "cluster",
    "ffd",
    "lattice",
    "wire",
    "wrap",
    "nonLinear",
    "sculpt",
    "tweak",
])

CONSTRAINT_TYPES = set([
    "parentConstraint",
    "pointConstraint",
    "orientConstraint",
    "scaleConstraint",
    "aimConstraint",
    "geometryConstraint",
    "normalConstraint",
    "poleVectorConstraint",
    "tangentConstraint",
])

ANIM_CURVE_TYPES = [
    "animCurveTA",
    "animCurveTL",
    "animCurveTT",
    "animCurveTU",
    "animCurveUA",
    "animCurveUL",
    "animCurveUT",
    "animCurveUU",
]


def parse_node_names(names_text):
    """Parse comma/newline separated Maya node names."""
    if not names_text:
        return []
    if isinstance(names_text, (list, tuple)):
        return unique_nodes([str(name).strip() for name in names_text if str(name).strip()])

    normalized = names_text.replace("\n", ",").replace(";", ",")
    names = []
    for raw_name in normalized.split(","):
        name = raw_name.strip()
        if name:
            names.append(name)
    return names


def unique_nodes(nodes):
    """Return nodes without duplicates while preserving order."""
    result = []
    seen = set()
    for node in nodes or []:
        if node and node not in seen:
            result.append(node)
            seen.add(node)
    return result


def existing_nodes(nodes, label="nodes"):
    """Return existing nodes, raising when no input nodes exist."""
    cmds = maya_modules()
    found_nodes = [node for node in (nodes or []) if cmds.objExists(node)]
    if not found_nodes:
        raise MayaApiError("No existing {0} found.".format(label))
    return found_nodes


def nodes_by_type(maya_type, shape_result="original", long_name=True):
    """Return scene nodes by Maya node type."""
    cmds = maya_modules()
    if not maya_type:
        raise MayaApiError("Maya type is required.")

    if maya_type == "animCurve":
        found_nodes = []
        for curve_type in ANIM_CURVE_TYPES:
            found_nodes.extend(cmds.ls(type=curve_type, long=long_name) or [])
    else:
        found_nodes = cmds.ls(type=maya_type, long=long_name) or []

    if shape_result == "parent_transform":
        found_nodes = parent_transforms(found_nodes, keep_non_shapes=True)

    found_nodes = unique_nodes(found_nodes)
    print("Nodes By Type: {0} node(s) of type {1}.".format(len(found_nodes), maya_type))
    return found_nodes


def parent_transforms(nodes, keep_non_shapes=False):
    """Return parent transforms for shape nodes."""
    cmds = maya_modules()
    result = []
    for node in nodes or []:
        if not cmds.objExists(node):
            continue
        if _is_shape_node(node):
            parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
            result.extend(parents)
        elif keep_non_shapes:
            result.append(node)
    return unique_nodes(result)


def shape_nodes(nodes):
    """Return non-intermediate shapes for input transforms or shape nodes."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    result = []
    for node in source_nodes:
        if _is_shape_node(node):
            result.append(node)
            continue
        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
        result.extend(shapes)
    return unique_nodes(result)


def related_skin_clusters(nodes):
    """Return skinCluster nodes affecting the input objects."""
    return related_deformers(nodes, allowed_types=set(["skinCluster"]), label="SkinCluster")


def related_blend_shapes(nodes):
    """Return blendShape nodes affecting the input objects."""
    return related_deformers(nodes, allowed_types=set(["blendShape"]), label="BlendShape")


def related_deformers(nodes, allowed_types=None, label="Deformers"):
    """Return deformer nodes related to input transforms or shapes."""
    cmds = maya_modules()
    shapes = shape_nodes(nodes)
    allowed_types = allowed_types or DEFORMER_TYPES
    result = []
    for shape in shapes:
        history_nodes = cmds.listHistory(shape, pruneDagObjects=True) or []
        for history_node in history_nodes:
            if cmds.nodeType(history_node) in allowed_types:
                result.append(history_node)
    result = unique_nodes(result)
    print("{0}: {1} node(s).".format(label, len(result)))
    return result


def related_materials(nodes):
    """Return material nodes assigned to input transforms or shapes."""
    cmds = maya_modules()
    shapes = shape_nodes(nodes)
    result = []
    for shape in shapes:
        shading_engines = cmds.listConnections(shape, type="shadingEngine") or []
        for shading_engine in shading_engines:
            materials = cmds.listConnections(
                "{0}.surfaceShader".format(shading_engine),
                source=True,
                destination=False,
            ) or []
            result.extend(materials)
    result = unique_nodes(result)
    print("Materials: {0} node(s).".format(len(result)))
    return result


def related_constraints(nodes):
    """Return constraint nodes connected to input objects."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    result = []
    for node in source_nodes:
        connected_nodes = cmds.listConnections(node, source=True, destination=True) or []
        for connected_node in connected_nodes:
            if cmds.nodeType(connected_node) in CONSTRAINT_TYPES:
                result.append(connected_node)
    result = unique_nodes(result)
    print("Constraints: {0} node(s).".format(len(result)))
    return result


def select_nodes(nodes):
    """Select nodes and return the nodes that were selected."""
    selected_nodes = replace_selection(existing_nodes(nodes))
    print("Select Nodes: {0} node(s).".format(len(selected_nodes)))
    return selected_nodes


def rename_nodes(nodes, base_name, start_index=1, padding=2):
    """Rename nodes using base_name plus an incrementing index."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not base_name:
        raise MayaApiError("Rename base name is required.")

    renamed_nodes = []
    start_index = int(start_index)
    padding = max(0, int(padding))

    with UndoChunk("Blueprint Rename Nodes"):
        for offset, node in enumerate(source_nodes):
            index_text = str(start_index + offset).zfill(padding)
            new_name = "{0}_{1}".format(base_name, index_text)
            renamed_name = cmds.rename(node, new_name)
            long_names = cmds.ls(renamed_name, long=True) or [renamed_name]
            renamed_nodes.append(long_names[0])

    print("Rename Nodes: {0} node(s).".format(len(renamed_nodes)))
    return renamed_nodes


def group_nodes(nodes, group_name):
    """Group nodes under a new transform and return the group node."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not group_name:
        raise MayaApiError("Group name is required.")

    with UndoChunk("Blueprint Group Nodes"):
        group_node = cmds.group(source_nodes, name=group_name)

    long_names = cmds.ls(group_node, long=True) or [group_node]
    print("Group Nodes: {0} node(s) into {1}.".format(len(source_nodes), group_node))
    return [long_names[0]]


def delete_nodes(nodes):
    """Delete nodes from the Maya scene."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    with UndoChunk("Blueprint Delete Nodes"):
        cmds.delete(source_nodes)
    print("Delete Nodes: {0} node(s).".format(len(source_nodes)))
    return True


def _is_shape_node(node):
    cmds = maya_modules()
    inherited_types = cmds.nodeType(node, inherited=True) or []
    return "shape" in inherited_types
