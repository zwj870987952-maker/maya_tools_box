"""Own lifetime deletion and explicit callback restoration as one undoable command."""
import json
from maya import cmds
from maya.api import OpenMaya as om
def maya_useNewAPI(): pass
class Cleanup(om.MPxCommand):
    def __init__(self): super().__init__(); self.modifier=om.MDagModifier(); self.rows=[]; self.callbacks=[]; self.selection=[]; self.data={}
    @staticmethod
    def creator(): return Cleanup()
    def doIt(self,args):
        from maya_toolkit.tools.clean_junk_nodes import normalize,plan
        self.data=plan(normalize(json.loads(args.asString(0)))); self.rows=self.data['nodes']; self.callbacks=self.data['callbacks']
        self.selection=cmds.ls(selection=True,long=True) or []
        for row in self.rows:
            names=cmds.ls(row['uuid'],long=True) or []
            if len(names)!=1: raise RuntimeError('Node identity changed')
            selection=om.MSelectionList(); selection.add(names[0]); obj=selection.getDependNode(0)
            if row['locked']: om.MFnDependencyNode(obj).isLocked=False
            self.modifier.deleteNode(obj,False)
        self.redoIt(); self.setResult(json.dumps(self.data))
    def isUndoable(self): return True
    def _guard(self,callback):
        enabled=cmds.undoInfo(query=True,state=True); cmds.undoInfo(stateWithoutFlush=False)
        try: callback()
        finally: cmds.undoInfo(stateWithoutFlush=enabled)
    def redoIt(self):
        def remove():
            unlocked=[]; cleared=[]
            try:
                for row in self.rows:
                    node=(cmds.ls(row['uuid'],long=True) or [None])[0]
                    if node is None: raise RuntimeError('Unknown node no longer exists')
                    if row['locked']: cmds.lockNode(node,lock=False); unlocked.append(row)
                for row in self.callbacks:
                    if cmds.modelEditor(row['editor'],exists=True):
                        if cmds.modelEditor(row['editor'],query=True,editorChanged=True)!=row['callback']: raise RuntimeError('ModelEditor callback changed; redo refused')
                        cmds.modelEditor(row['editor'],edit=True,editorChanged=''); cleared.append(row)
                self.modifier.doIt()
            except Exception:
                for row in cleared: cmds.modelEditor(row['editor'],edit=True,editorChanged=row['callback'])
                for row in unlocked:
                    names=cmds.ls(row['uuid'],long=True) or []
                    if names: cmds.lockNode(names[0],lock=True)
                raise
        self._guard(remove)
    def undoIt(self):
        def restore():
            self.modifier.undoIt()
            for row in self.rows:
                if row['locked']: cmds.lockNode((cmds.ls(row['uuid'],long=True) or [None])[0],lock=True)
            for row in self.callbacks:
                if cmds.modelEditor(row['editor'],exists=True): cmds.modelEditor(row['editor'],edit=True,editorChanged=row['callback'])
            valid=[n for n in self.selection if cmds.objExists(n)]
            cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        self._guard(restore)
def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbCleanJunkNodes',Cleanup.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbCleanJunkNodes')
