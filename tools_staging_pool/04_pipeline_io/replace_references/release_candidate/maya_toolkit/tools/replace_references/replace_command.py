import json
from maya import cmds
from maya.api import OpenMaya as om
def maya_useNewAPI(): pass
def guarded(callback):
    enabled=cmds.undoInfo(query=True,state=True); time=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True); namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
    cmds.undoInfo(stateWithoutFlush=False)
    try: cmds.namespace(set=':'); return callback()
    finally:
        cmds.namespace(set=namespace if cmds.namespace(exists=namespace) else ':')
        if cmds.currentTime(query=True)!=time: cmds.currentTime(time)
        cmds.autoKeyframe(state=auto); cmds.undoInfo(stateWithoutFlush=enabled)

class Replace(om.MPxCommand):
    def __init__(self): super().__init__(); self.rows=[]; self.selected=[]; self.after_selected=[]
    @staticmethod
    def creator(): return Replace()
    def doIt(self,args):
        from maya_toolkit.tools.replace_references.tool import current_plan,normalize
        data=current_plan(normalize(json.loads(args.asString(0)))); self.rows=data['references']; self.selected=cmds.ls(selection=True,long=True) or []
        guarded(lambda:self.apply('new')); self.after_selected=cmds.ls(selection=True,long=True) or []; self.setResult(json.dumps(data))
    def apply(self,direction):
        from maya_toolkit.tools.replace_references.tool import load_row,file_hash
        for row in self.rows:
            target=row['path'] if direction=='old' else row['new_file']; sha=row['sha256'] if direction=='old' else row['new_sha256']
            if file_hash(target)!=sha: raise RuntimeError('Undo/Redo reference source changed/unavailable')
            names=cmds.ls(row['uuid'],type='reference') or []
            if len(names)!=1: raise RuntimeError('Owned reference missing')
            from pathlib import Path
            expected_current=row['new_file'] if direction=='old' else row['path']
            if Path(cmds.referenceQuery(names[0],filename=True,withoutCopyNumber=True)).resolve()!=Path(expected_current).resolve(): raise RuntimeError('Reference was externally replaced; Undo/Redo refused')
            if cmds.referenceQuery(names[0],editStrings=True): raise RuntimeError('Reference acquired edits; Undo/Redo refused')
            target_ns=row['namespace'] if direction=='old' else row['new_namespace']; current_ns=cmds.referenceQuery(names[0],namespace=True).lstrip(':')
            if target_ns!=current_ns and cmds.namespace(exists=':'+target_ns): raise RuntimeError('Undo/Redo namespace occupied')
        done=[]
        try:
            for row in self.rows: done.append(row); load_row(row,direction)
        except Exception:
            for row in reversed(done): load_row(row,'old' if direction=='new' else 'new')
            raise
    def isUndoable(self): return True
    def undoIt(self):
        guarded(lambda:self.apply('old')); valid=[n for n in self.selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
    def redoIt(self):
        guarded(lambda:self.apply('new')); valid=[n for n in self.after_selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbReplaceReferences',Replace.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbReplaceReferences')
