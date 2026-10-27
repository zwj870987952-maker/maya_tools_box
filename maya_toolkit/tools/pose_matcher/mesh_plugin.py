"""Private API2 command: construct geometry in data, attach through undoable modifier."""
import json
import uuid
import maya.api.OpenMaya as om

COMMAND = 'mtkPoseCandidateMesh'


def maya_useNewAPI():
    pass


class MeshCommand(om.MPxCommand):
    def __init__(self):
        super().__init__()
        self.modifier = None
        self.transform = None

    @staticmethod
    def creator():
        return MeshCommand()

    def doIt(self, args):
        from maya_toolkit.tools.pose_matcher.runtime import require_scope, check_arrays
        require_scope()
        if len(args) != 1:
            raise ValueError('One JSON mesh payload required')
        d = json.loads(args.asString(0))
        v, uv, vt, vn = check_arrays(d['v'], d['uv'], d['vt'], d['vn'])
        self.data_fn = om.MFnMeshData()
        data = self.data_fn.create()
        self.geometry = data
        counts = []
        for f in vt[:, 0]:
            if not counts or int(f) != last:
                counts.append(1)
                last = int(f)
            else:
                counts[-1] += 1
        fn = om.MFnMesh()
        self.mesh_fn = fn
        fn.create(om.MPointArray([om.MPoint(*p) for p in v]), om.MIntArray(counts), om.MIntArray(vt[:, 1].tolist()), parent=data)
        fn.setUVs(om.MFloatArray(uv[:, 0].tolist()), om.MFloatArray(uv[:, 1].tolist()))
        fn.assignUVs(om.MIntArray(counts), om.MIntArray(vt[:, 2].tolist()))
        fn.setFaceVertexNormals(om.MVectorArray([om.MVector(*vn[i]) for i in vt[:, 3]]), om.MIntArray(vt[:, 0].tolist()), om.MIntArray(vt[:, 1].tolist()), om.MSpace.kObject)
        self.modifier = om.MDagModifier()
        self.transform = self.modifier.createNode('transform')
        shape = self.modifier.createNode('mesh', self.transform)
        # UUID suffix ensures none of the requested names can rename an existing node.
        name = d['name'] + '_' + uuid.uuid4().hex[:10]
        self.modifier.renameNode(self.transform, name)
        self.modifier.renameNode(shape, name + 'Shape')
        self.modifier.newPlugValue(om.MFnDependencyNode(shape).findPlug('cachedInMesh', False), data)
        self.redoIt()
        self.setResult(om.MDagPath.getAPathTo(self.transform).fullPathName())

    def redoIt(self):
        self.modifier.doIt()
        from maya import cmds
        path = om.MDagPath.getAPathTo(self.transform).fullPathName()
        shapes = cmds.listRelatives(path, shapes=True, fullPath=True) or []
        for shape in shapes:
            cmds.dgdirty(shape)
            cmds.dgeval(shape + '.outMesh')

    def undoIt(self):
        self.modifier.undoIt()

    def isUndoable(self):
        return True


def initializePlugin(obj):
    om.MFnPlugin(obj, 'Maya Toolkit private candidate', '1.0', 'Any').registerCommand(COMMAND, MeshCommand.creator)


def uninitializePlugin(obj):
    om.MFnPlugin(obj).deregisterCommand(COMMAND)
