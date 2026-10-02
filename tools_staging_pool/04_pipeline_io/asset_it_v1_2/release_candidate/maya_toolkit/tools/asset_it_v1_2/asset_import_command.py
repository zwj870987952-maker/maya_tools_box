"""Own file-import node lifetime; preserve native suite and existing Undo queue."""
import json
from maya import cmds
from maya.api import OpenMaya as om


def maya_useNewAPI(): pass


class ImportCommand(om.MPxCommand):
    def __init__(self):
        super().__init__(); self.result={}; self.modifier=None

    @staticmethod
    def creator(): return ImportCommand()

    def doIt(self,args):
        from maya_toolkit.tools.asset_it_v1_2.tool import normalize,AssetItTool,import_native
        p=normalize(json.loads(args.asString(0)))
        if p['action']!='import_asset': raise ValueError('Import command only handles import_asset')
        checked=AssetItTool().validate(**p)
        if not checked.success: raise ValueError(checked.message)
        enabled=cmds.undoInfo(query=True,state=True); cmds.undoInfo(stateWithoutFlush=False)
        try: self.result=import_native(p)
        finally: cmds.undoInfo(stateWithoutFlush=enabled)
        self.setResult(json.dumps(self.result))

    def isUndoable(self): return True

    def undoIt(self):
        created=set(self.result['created_uuids']); self.modifier=om.MDagModifier()
        for identity in created:
            names=cmds.ls(identity,long=True) or []
            if not names: continue
            selected=om.MSelectionList(); selected.add(names[0]); node=selected.getDependNode(0)
            if node.hasFn(om.MFn.kDagNode):
                parent=cmds.listRelatives(names[0],parent=True,fullPath=True) or []
                if parent and cmds.ls(parent[0],uuid=True)[0] in created: continue
            self.modifier.deleteNode(node)
        current=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
        try:
            cmds.namespace(setNamespace=':'); self.modifier.doIt()
            # Keep the empty namespace: removing/recreating it makes API-restored
            # nodes appear in ls but fail Maya name lookup in Maya2025.
        finally: cmds.namespace(setNamespace=current if cmds.namespace(exists=current) else ':')

    def redoIt(self):
        if self.modifier is None: raise RuntimeError('No import snapshot available')
        current=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
        try:
            cmds.namespace(setNamespace=':')
            if not cmds.namespace(exists=self.result['namespace']): raise RuntimeError('Reserved import namespace removed after Undo; Redo cannot safely restore named nodes')
            self.modifier.undoIt(); self.setResult(json.dumps(self.result))
        finally: cmds.namespace(setNamespace=current)


def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbAssetItImport',ImportCommand.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbAssetItImport')
