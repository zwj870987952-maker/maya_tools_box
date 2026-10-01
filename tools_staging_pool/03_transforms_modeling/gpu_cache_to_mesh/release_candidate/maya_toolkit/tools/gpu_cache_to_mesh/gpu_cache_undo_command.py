"""Own native import lifetime, so Maya2025 native orphan nodes also undo."""
import json
from maya import cmds
from maya.api import OpenMaya as om


def maya_useNewAPI(): pass


class ConvertCommand(om.MPxCommand):
    def __init__(self):
        super().__init__(); self.modifier=None; self.original=[]; self.result={}

    @staticmethod
    def creator(): return ConvertCommand()

    def doIt(self,args):
        from maya_toolkit.tools.gpu_cache_to_mesh.tool import execute_native,plan,normalize
        p=normalize(json.loads(args.asString(0))); scope=plan(p)
        self.original=[(t['shape_uuid'],t['original_visibility']) for t in scope['tasks']] if p['hide_original'] else []
        enabled=cmds.undoInfo(query=True,state=True)
        # Preserve the existing queue: only this synchronous native operation
        # omits child command records; this MPxCommand owns its whole lifetime.
        cmds.undoInfo(stateWithoutFlush=False)
        try: self.result=execute_native(p,scope)
        finally: cmds.undoInfo(stateWithoutFlush=enabled)
        self.setResult(json.dumps(self.result))

    def isUndoable(self): return True

    def undoIt(self):
        created=set(self.result['created_uuids'])
        self.modifier=om.MDagModifier()
        for uid in created:
            values=cmds.ls(uid,long=True) or []
            if not values: continue
            sel=om.MSelectionList(); sel.add(values[0]); obj=sel.getDependNode(0)
            if obj.hasFn(om.MFn.kDagNode):
                parent=cmds.listRelatives(values[0],parent=True,fullPath=True) or []
                if parent and cmds.ls(parent[0],uuid=True)[0] in created: continue
            self.modifier.deleteNode(obj)
        for uid,value in self.original:
            values=cmds.ls(uid,long=True) or []
            if not values: raise RuntimeError('Original GPU cache missing during Undo')
            sel=om.MSelectionList(); sel.add(values[0]+'.visibility')
            self.modifier.newPlugValueBool(sel.getPlug(0),bool(value))
        self.modifier.doIt()

    def redoIt(self):
        if self.modifier is None: raise RuntimeError('No import snapshot available for Redo')
        self.modifier.undoIt()
        self.setResult(json.dumps(self.result))


def initializePlugin(obj):
    om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbGpuCacheConvert',ConvertCommand.creator)


def uninitializePlugin(obj):
    om.MFnPlugin(obj).deregisterCommand('mtbGpuCacheConvert')
