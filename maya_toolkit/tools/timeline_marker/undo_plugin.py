"""Undoable fileInfo command. GPL-3.0-or-later adaptation; private command, no node types."""
import json
import maya.api.OpenMaya as om
from maya import cmds
from maya_toolkit.tools.timeline_marker import model

COMMAND = 'mtkTimelineMarkerData'
KEY = 'timelineMarkers'


def maya_useNewAPI():
    pass


class MarkerDataCommand(om.MPxCommand):
    def __init__(self):
        super().__init__()
        self.before = None
        self.after = None

    @staticmethod
    def creator():
        return MarkerDataCommand()

    def doIt(self, args):
        if len(args) != 1:
            raise ValueError('一个JSON参数需要')
        self.after = json.dumps(model.dataset(json.loads(args.asString(0))), ensure_ascii=True)
        stored = cmds.fileInfo(KEY, query=True) or []
        if len(stored) > 1:
            raise ValueError('多值metadata不能覆盖')
        if stored:
            model.decode(stored[0])
            try:
                json.loads(stored[0])
                self.before = stored[0]
            except json.JSONDecodeError:
                self.before = json.loads('"' + stored[0] + '"')
        self.redoIt()

    def redoIt(self):
        cmds.fileInfo(KEY, self.after)
        try:
            cmds.file(modified=True)
        except Exception:
            # A failed MPxCommand is not added to Undo. Restore this sole header write.
            self.restore_before()
            raise

    def undoIt(self):
        self.restore_before()
        cmds.file(modified=True)

    def restore_before(self):
        if self.before is None:
            cmds.fileInfo(remove=KEY)
        else:
            cmds.fileInfo(KEY, self.before)

    def isUndoable(self):
        return True


def initializePlugin(obj):
    om.MFnPlugin(obj, 'Maya Toolkit / Robert Joosten GPL adaptation', '2.0.2-candidate.1', 'Any').registerCommand(COMMAND, MarkerDataCommand.creator)


def uninitializePlugin(obj):
    om.MFnPlugin(obj).deregisterCommand(COMMAND)
