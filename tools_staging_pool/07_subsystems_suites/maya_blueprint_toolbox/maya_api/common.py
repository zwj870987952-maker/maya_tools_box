"""Shared helpers for Maya API wrapper modules."""


class MayaApiError(RuntimeError):
    """Raised when a wrapped Maya API operation fails or is invalid."""


def maya_modules(include_mel=False):
    """Return Maya Python modules, or raise a clear error outside Maya."""
    try:
        import maya.cmds as cmds
    except ImportError:
        raise MayaApiError("This operation must run inside Maya.")

    if not include_mel:
        return cmds

    try:
        import maya.mel as mel
    except ImportError:
        raise MayaApiError("Maya MEL module is not available.")

    return cmds, mel


class UndoChunk(object):
    """Context manager for grouping scene-changing Maya operations."""

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        cmds = maya_modules()
        if self.name:
            cmds.undoInfo(openChunk=True, chunkName=self.name)
        else:
            cmds.undoInfo(openChunk=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        cmds = maya_modules()
        cmds.undoInfo(closeChunk=True)
        return False
