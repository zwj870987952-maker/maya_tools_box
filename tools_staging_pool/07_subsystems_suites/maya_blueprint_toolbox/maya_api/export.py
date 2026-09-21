"""Export helpers for blueprint Maya operations."""

import os

from .common import MayaApiError, maya_modules
from .selection import get_current_selection, replace_selection


def export_fbx(nodes, target_path, bake_animation=False, frame_start=1.0, frame_end=120.0, overwrite_existing=False):
    """Export nodes to FBX and restore the previous Maya selection."""
    cmds, mel = maya_modules(include_mel=True)
    existing_nodes = _validate_export_nodes(cmds, nodes)
    resolved_path = _validate_fbx_target(target_path, overwrite_existing)

    _ensure_fbx_plugin(cmds)
    _configure_fbx_export(mel, bake_animation, frame_start, frame_end)

    previous_selection = get_current_selection()
    export_path = resolved_path.replace("\\", "/")
    try:
        replace_selection(existing_nodes)
        mel.eval('FBXExport -f "{0}" -s'.format(export_path))
    finally:
        replace_selection(previous_selection)

    print("Export FBX: {0} node(s) to {1}".format(len(existing_nodes), resolved_path))
    return resolved_path


def _validate_export_nodes(cmds, nodes):
    if not nodes:
        raise MayaApiError("Export FBX requires nodes.")

    existing_nodes = [node for node in nodes if cmds.objExists(node)]
    if not existing_nodes:
        raise MayaApiError("Export FBX input nodes do not exist in the scene.")

    return existing_nodes


def _validate_fbx_target(target_path, overwrite_existing):
    if not target_path:
        raise MayaApiError("FBX target path is required.")

    resolved_path = os.path.normpath(target_path)
    if os.path.splitext(resolved_path)[1].lower() != ".fbx":
        raise MayaApiError("FBX target path must end with .fbx: {0}".format(resolved_path))

    target_dir = os.path.dirname(resolved_path)
    if target_dir and not os.path.isdir(target_dir):
        raise MayaApiError("Export directory does not exist: {0}".format(target_dir))

    if os.path.exists(resolved_path) and not overwrite_existing:
        raise MayaApiError("Export target already exists. Enable Overwrite Existing: {0}".format(resolved_path))

    return resolved_path


def _ensure_fbx_plugin(cmds):
    if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
        cmds.loadPlugin("fbxmaya")


def _configure_fbx_export(mel, bake_animation, frame_start, frame_end):
    bake_enabled = bool(bake_animation)
    mel.eval("FBXExportBakeComplexAnimation -v {0}".format(str(bake_enabled).lower()))
    if bake_enabled:
        mel.eval("FBXExportBakeComplexStart -v {0}".format(float(frame_start)))
        mel.eval("FBXExportBakeComplexEnd -v {0}".format(float(frame_end)))
