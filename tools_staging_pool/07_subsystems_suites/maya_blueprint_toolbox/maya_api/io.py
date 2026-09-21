"""File import and reference helpers for blueprint Maya operations."""

import os

from .common import MayaApiError, UndoChunk, maya_modules


def import_file(file_path, mode="import", namespace="", preserve_references=True):
    """Import or reference a file and return newly created Maya nodes."""
    cmds = maya_modules()
    resolved_path = _validate_source_path(file_path)
    mode = mode or "import"

    if mode not in ("import", "reference"):
        raise MayaApiError("Unsupported import mode: {0}".format(mode))

    kwargs = {"returnNewNodes": True}
    if namespace:
        kwargs["namespace"] = namespace

    with UndoChunk("Blueprint Import File"):
        if mode == "reference":
            new_nodes = cmds.file(resolved_path, reference=True, **kwargs) or []
        else:
            kwargs["preserveReferences"] = bool(preserve_references)
            new_nodes = cmds.file(resolved_path, i=True, **kwargs) or []

    print("Import File: {0} node(s) from {1}".format(len(new_nodes), resolved_path))
    return new_nodes


def _validate_source_path(file_path):
    if not file_path:
        raise MayaApiError("File path is required.")

    resolved_path = os.path.normpath(file_path)
    if not os.path.exists(resolved_path):
        raise MayaApiError("File path does not exist: {0}".format(resolved_path))

    return resolved_path
