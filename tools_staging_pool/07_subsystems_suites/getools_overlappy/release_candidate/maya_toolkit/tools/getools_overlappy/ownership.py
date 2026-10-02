import functools
import maya.cmds as cmds
from maya_toolkit.core.context import UndoChunkContext

def assert_group_owned(instance,name):
    if not cmds.objExists(name):return
    actual=cmds.ls(name,uuid=True)
    if len(actual)!=1 or actual[0]!=getattr(instance,'_owned_group_uuid',None):raise RuntimeError('Existing setup group is not owned by this instance; rename or inspect it first')
def assert_com_owned(instance):
    node=getattr(instance,'COMObject',None)
    if node and cmds.objExists(node) and cmds.ls(node,uuid=True)!=[getattr(instance,'_owned_com_uuid',None)]:raise RuntimeError('Borrowed COM object cannot be deleted by this candidate')

def scene_operation(function):
    @functools.wraps(function)
    def wrapped(*args,**kwargs):
        if not cmds.undoInfo(q=True,state=True):raise RuntimeError('Enable Maya Undo before native scene operations')
        selected=cmds.ls(selection=True,long=True) or [];time=cmds.currentTime(q=True)
        suspend=cmds.refresh(q=True,suspend=True)
        bounds={flag:cmds.playbackOptions(q=True,**{flag:True}) for flag in ('minTime','maxTime','animationStartTime','animationEndTime')}
        cached=cmds.optionVar(q='cachedPlaybackEnable') if cmds.optionVar(exists='cachedPlaybackEnable') else None
        with UndoChunkContext('GETools_'+function.__name__):
            try:return function(*args,**kwargs)
            finally:
                cmds.playbackOptions(**bounds);cmds.currentTime(time)
                cmds.refresh(suspend=suspend)
                if cached is not None:cmds.optionVar(intValue=('cachedPlaybackEnable',cached))
                cmds.select([n for n in selected if cmds.objExists(n)],replace=True) if selected else cmds.select(clear=True)
    return wrapped
