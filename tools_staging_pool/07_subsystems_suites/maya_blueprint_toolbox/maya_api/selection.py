"""Selection helpers for blueprint Maya operations."""

from .common import maya_modules


def get_current_selection(include_shapes=False):
    """Return the current Maya selection as long names."""
    cmds = maya_modules()
    selection = cmds.ls(selection=True, long=True) or []
    if include_shapes and selection:
        shapes = cmds.listRelatives(selection, shapes=True, fullPath=True) or []
        selection = selection + shapes
    return selection


def replace_selection(nodes):
    """Replace Maya selection with existing nodes and return the selected nodes."""
    cmds = maya_modules()
    existing_nodes = [node for node in (nodes or []) if cmds.objExists(node)]
    if existing_nodes:
        cmds.select(existing_nodes, replace=True)
    else:
        cmds.select(clear=True)
    return existing_nodes
