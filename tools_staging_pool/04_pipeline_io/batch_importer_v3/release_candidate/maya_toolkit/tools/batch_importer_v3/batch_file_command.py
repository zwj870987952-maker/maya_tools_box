"""Maya file commands are not Undoable; own their import/reference lifetime."""
import json
from maya import cmds
from maya.api import OpenMaya as om


def maya_useNewAPI(): pass


def guarded(callback):
    enabled=cmds.undoInfo(query=True,state=True)
    current=cmds.currentTime(query=True); selected=cmds.ls(selection=True,long=True) or []
    namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True); auto=cmds.autoKeyframe(query=True,state=True)
    cmds.undoInfo(stateWithoutFlush=False)
    try:
        cmds.namespace(setNamespace=':')
        if auto: cmds.autoKeyframe(state=False)
        return callback()
    finally:
        cmds.namespace(setNamespace=namespace if cmds.namespace(exists=namespace) else ':')
        if cmds.currentTime(query=True)!=current: cmds.currentTime(current)
        valid=[n for n in selected if cmds.objExists(n)]
        if (cmds.ls(selection=True,long=True) or [])!=valid: cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        if cmds.autoKeyframe(query=True,state=True)!=auto: cmds.autoKeyframe(state=auto)
        cmds.undoInfo(stateWithoutFlush=enabled)


def remove(rows):
    from pathlib import Path
    targets=[]
    for row in rows:
        nodes=cmds.ls(row['uuid']) or []
        if len(nodes)!=1 or cmds.nodeType(nodes[0])!='reference': raise RuntimeError('Owned reference missing/replaced')
        if Path(cmds.referenceQuery(nodes[0],filename=True,withoutCopyNumber=True)).resolve()!=Path(row['path']).resolve(): raise RuntimeError('Owned reference source replaced')
        targets.append(nodes[0])
    for node in targets: cmds.file(referenceNode=node,removeReference=True)


def restore(rows):
    from maya_toolkit.tools.batch_importer_v3.tool import create_reference,file_hash
    from pathlib import Path
    for row in rows:
        if not Path(row['path']).is_file() or file_hash(row['path'])!=row['sha256']: raise RuntimeError('Reference source changed/unavailable for Undo')
        if cmds.objExists(row['reference_node']): raise RuntimeError('Reference node name occupied')
        namespace=':'+row['namespace']
        if cmds.namespace(exists=namespace) and cmds.namespaceInfo(namespace,listOnlyDependencyNodes=True): raise RuntimeError('Reference namespace contains foreign nodes')
    return [create_reference(row,restore=True) for row in rows]


class FileOperation(om.MPxCommand):
    def __init__(self):
        super().__init__(); self.p={}; self.scope={}; self.result={}; self.modifier=None; self.restored=[]; self.selection=[]

    @staticmethod
    def creator(): return FileOperation()

    def doIt(self,args):
        from maya_toolkit.tools.batch_importer_v3.tool import normalize,plan,native_operation
        self.p=normalize(json.loads(args.asString(0)))
        if self.p['action']=='inspect': raise ValueError('Inspect does not invoke native command')
        self.scope=plan(self.p); self.selection=cmds.ls(selection=True,long=True) or []
        self.result=guarded(lambda:native_operation(self.p,self.scope)); self.setResult(json.dumps(self.result))

    def isUndoable(self): return True

    def undoIt(self):
        if self.p['action']=='import':
            created=set(self.result['created_uuids']); self.modifier=om.MDagModifier()
            for identity in created:
                nodes=cmds.ls(identity,long=True) or []
                if not nodes: continue
                selected=om.MSelectionList(); selected.add(nodes[0]); node=selected.getDependNode(0)
                if node.hasFn(om.MFn.kDagNode):
                    parents=cmds.listRelatives(nodes[0],parent=True,fullPath=True) or []
                    if parents and cmds.ls(parents[0],uuid=True)[0] in created: continue
                self.modifier.deleteNode(node)
            self.modifier.doIt()  # Keep empty namespaces for valid MDagModifier Redo lookup.
        elif self.p['action']=='reference': guarded(lambda:remove(self.result['imports']))
        else:
            self.restored=guarded(lambda:restore(self.scope['references']))
            selected=[n for n in self.selection if cmds.objExists(n)]
            if selected: cmds.select(selected,replace=True)

    def redoIt(self):
        from maya_toolkit.tools.batch_importer_v3.tool import native_operation
        if self.p['action']=='import':
            if self.modifier is None: raise RuntimeError('No import snapshot')
            for namespace in self.result['namespaces']:
                if not cmds.namespace(exists=':'+namespace): raise RuntimeError('Reserved import namespace removed; cannot safely Redo')
            self.modifier.undoIt()
        elif self.p['action']=='reference': self.result=guarded(lambda:native_operation(self.p,self.scope))
        else: guarded(lambda:remove(self.restored))
        self.setResult(json.dumps(self.result))


def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbBatchFileOperation',FileOperation.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbBatchFileOperation')
