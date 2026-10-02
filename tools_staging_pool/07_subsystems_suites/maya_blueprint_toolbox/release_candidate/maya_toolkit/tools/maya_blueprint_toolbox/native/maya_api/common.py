"""Native wrapper compatibility using existing toolkit Undo context."""
from maya_toolkit.core.context import UndoChunkContext
class MayaApiError(RuntimeError):pass
def maya_modules(include_mel=False):
    try:
        from maya import cmds
        if include_mel:
            from maya import mel
            return cmds,mel
        return cmds
    except ImportError:raise MayaApiError('This operation requires Maya')
class UndoChunk(UndoChunkContext):
    def __init__(self,name=None):super().__init__(name or 'Blueprint Operation')
    def __enter__(self):
        if not maya_modules().undoInfo(query=True,state=True):raise MayaApiError('Enable Undo before scene operations')
        return super().__enter__()
