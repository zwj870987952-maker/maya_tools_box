"""Snapshot local node lifetime and restore eligible whole-file references."""
import json
from maya import cmds
from maya.api import OpenMaya as om
def maya_useNewAPI(): pass

def guarded(callback):
    enabled=cmds.undoInfo(query=True,state=True); namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
    time=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
    cmds.undoInfo(stateWithoutFlush=False)
    try: cmds.namespace(set=':'); return callback()
    finally:
        cmds.namespace(set=namespace if cmds.namespace(exists=namespace) else ':')
        if cmds.currentTime(query=True)!=time: cmds.currentTime(time)
        if cmds.autoKeyframe(query=True,state=True)!=auto: cmds.autoKeyframe(state=auto)
        cmds.undoInfo(stateWithoutFlush=enabled)

class Cleanup(om.MPxCommand):
    def __init__(self): super().__init__(); self.modifier=None; self.rows=[]; self.selection=[]; self.data={}
    @staticmethod
    def creator(): return Cleanup()
    def doIt(self,args):
        from maya_toolkit.tools.clean_invalid_paths.tool import normalize,plan
        self.data=plan(normalize(json.loads(args.asString(0)))); self.rows=self.data['references']; self.selection=cmds.ls(selection=True,long=True) or []
        self.modifier=om.MDagModifier()
        for row in self.data['delete_nodes']:
            names=cmds.ls(row['uuid'],long=True) or []
            if len(names)!=1: raise RuntimeError('Path owner identity changed')
            select=om.MSelectionList(); select.add(names[0]); self.modifier.deleteNode(select.getDependNode(0),False)
        def remove():
            for row in self.rows: cmds.file(referenceNode=row['reference_node'],removeReference=True)
            self.modifier.doIt()
        guarded(remove); self.setResult(json.dumps(self.data))
    def isUndoable(self): return True
    def undoIt(self):
        from maya_toolkit.tools.clean_invalid_paths.reference_ops import create_reference,file_hash
        for row in self.rows:
            if file_hash(row['path'])!=row['sha256']: raise RuntimeError('Reference source changed; Undo restoration refused')
            if cmds.objExists(row['reference_node']): raise RuntimeError('Reference node name occupied')
        def restore():
            self.modifier.undoIt()
            self.rows=[create_reference(row,restore=True) for row in self.rows]
            valid=[n for n in self.selection if cmds.objExists(n)]
            cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        guarded(restore)
    def redoIt(self):
        from maya_toolkit.tools.clean_invalid_paths.reference_ops import file_hash,references
        for row in self.rows:
            names=cmds.ls(row['uuid']) or []
            if len(names)!=1 or file_hash(row['path'])!=row['sha256']: raise RuntimeError('Reference changed; Redo refused')
            current=references({'reference_nodes':names})[0]
            if current['path']!=row['path'] or current['namespace']!=row['namespace']: raise RuntimeError('Reference scope changed; Redo refused')
        def remove():
            for row in self.rows: cmds.file(referenceNode=(cmds.ls(row['uuid']) or [None])[0],removeReference=True)
            self.modifier.doIt()
        guarded(remove); self.setResult(json.dumps(self.data))

def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbCleanPathNodes',Cleanup.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbCleanPathNodes')
