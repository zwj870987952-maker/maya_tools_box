"""Static no-scene-mutation Undo marker; no generated temp plugin or MEL interpolation."""
import json
from maya.api import OpenMaya as om
def maya_useNewAPI():pass
class Marker(om.MPxCommand):
    def __init__(self):super().__init__();self.identifier=''
    @staticmethod
    def creator():return Marker()
    def doIt(self,args):
        data=json.loads(args.asString(0));self.identifier=data['id'];self.redoIt()
    def isUndoable(self):return True
    def redoIt(self):
        from maya_toolkit.tools.undo_checkpoint import manager as state
        if any(item.id==self.identifier for item in state.items):state.applied[self.identifier]=True
    def undoIt(self):
        from maya_toolkit.tools.undo_checkpoint import manager as state
        if any(item.id==self.identifier for item in state.items):state.applied[self.identifier]=False
        state.last_undone=self.identifier
def initializePlugin(obj):om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbUndoCheckpointMarker',Marker.creator)
def uninitializePlugin(obj):om.MFnPlugin(obj).deregisterCommand('mtbUndoCheckpointMarker')
