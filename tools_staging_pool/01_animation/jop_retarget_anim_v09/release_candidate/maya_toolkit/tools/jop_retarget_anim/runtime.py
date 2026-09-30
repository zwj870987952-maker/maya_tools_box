import copy
from functools import wraps
import json
import uuid

FORMAT = 'maya_toolkit.jop_retarget_anim.v1'
_ACTIVE = False
_ARGS = {}
_HELPERS = set()
_TARGETS = set()
_PREFIX = ''
_CACHE = {}


def cmds_module():
    from maya import cmds
    return cmds


def require_active():
    if not _ACTIVE:
        raise RuntimeError('写入须经JopRetargetTool.run')


def identity(node):
    cmds = cmds_module()
    reference = cmds.referenceQuery(node, referenceNode=True) if cmds.referenceQuery(node, isNodeReferenced=True) else None
    return cmds.ls(node, uuid=True)[0], cmds.ls(reference, uuid=True)[0] if reference else ''


def resolve_row(row):
    cmds = cmds_module()
    found = [n for n in cmds.ls(row['node_uuid'], long=True) or [] if identity(n)[1] == row['reference_uuid']]
    if len(found) != 1:
        raise ValueError('快照UUID/reference对象缺失或不唯一')
    return found[0]


def world_matrix(node, time):
    from maya.api import OpenMaya as om
    cmds = cmds_module()
    raw = cmds.getAttr(node + '.worldMatrix[0]', time=time)
    if cmds.getAttr(node + '.rotatePivot')[0] == (0, 0, 0):
        return list(raw)
    # Exact original frozen branch: world pivot point + decompose/compose rotation, unit scale.
    pivot = cmds.getAttr(node + '.rotatePivot', time=time)[0]
    matrix = om.MMatrix(raw)
    point = om.MPoint(*pivot) * matrix
    result = om.MTransformationMatrix()
    result.setRotation(om.MTransformationMatrix(matrix).rotation(asQuaternion=True))
    result.setTranslation(om.MVector(point.x, point.y, point.z), om.MSpace.kTransform)
    return list(result.asMatrix())


def cache_key(objects, dictionaries):
    return json.dumps([objects, dictionaries], sort_keys=True, separators=(',', ':'))


def capture_bridge(function):
    @wraps(function)
    def call(bake):
        if _ACTIVE:
            return function(bake)
        cmds = cmds_module()
        from .tool import JopRetargetTool
        result = JopRetargetTool().run(action='capture', bake=bool(cmds.checkBox(bake, query=True, value=True)))
        if not result.success:
            raise RuntimeError(result.message)
        data = result.data
        objects = [resolve_row(row) for row in data['records']]
        dictionaries = [{s['time']: s['matrix'] for s in row['samples']} for row in data['records']]
        _CACHE[cache_key(objects, dictionaries)] = copy.deepcopy(data)
        return objects, dictionaries
    return call


def restore_bridge(function):
    @wraps(function)
    def call(objects, dictionaries):
        if _ACTIVE:
            return function(objects, dictionaries)
        data = _CACHE.get(cache_key(objects, dictionaries))
        if not data:
            raise ValueError('请先在本候选保存动画或使用标准snapshot_data')
        cmds = cmds_module()
        referenced = any(cmds.referenceQuery(resolve_row(row), isNodeReferenced=True) for row in data['records'])
        if referenced and cmds.confirmDialog(title='Reference edits', message='Retarget writes referenced control keys. Continue in backup scene?', button=['Yes', 'No'], defaultButton='No') != 'Yes':
            return None
        from .tool import JopRetargetTool
        result = JopRetargetTool().run(action='retarget', snapshot_data=copy.deepcopy(data), allow_reference_edits=referenced)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
    return call


def ensure_nodes():
    cmds = cmds_module()
    loaded = []
    try:
        types = set(cmds.allNodeTypes())
        for required, plugin in (('multMatrix', 'matrixNodes'), ('quatToEuler', 'quatNodes')):
            if required not in types:
                already = cmds.pluginInfo(plugin, query=True, loaded=True)
                cmds.loadPlugin(plugin, quiet=True)
                if not already:
                    loaded.append(plugin)
        return loaded
    except Exception:
        for plugin in reversed(loaded):
            if cmds.pluginInfo(plugin, query=True, unloadOk=True):
                cmds.unloadPlugin(plugin)
        raise


def execute(args):
    global _ACTIVE, _ARGS, _HELPERS, _TARGETS, _PREFIX
    cmds = cmds_module()
    from . import native
    if args['action'] == 'open_ui':
        native.main()
        return {'window': 'mtbJopRetargetAnimation_v09'}
    current = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    auto = cmds.autoKeyframe(query=True, state=True)
    namespace = cmds.namespaceInfo(currentNamespace=True)
    _ACTIVE, _ARGS, _HELPERS, _PREFIX = True, args, set(), 'mtbJop_' + uuid.uuid4().hex + '_'
    _TARGETS = {identity(n) for n in args['objects']}
    plugins = []
    try:
        if args['action'] == 'capture':
            objects, dictionaries = native.saveAnimToList('apiCapture')
            rows = []
            for node, data in zip(objects, dictionaries):
                node_id, reference_id = identity(node)
                rows.append({'object_name': node, 'node_uuid': node_id, 'reference_uuid': reference_id, 'samples': [{'time': time, 'matrix': list(matrix)} for time, matrix in sorted(data.items())]})
            return {'format': FORMAT, 'records': rows}
        cmds.autoKeyframe(state=False)
        plugins = ensure_nodes()
        dictionaries = [{s['time']: s['matrix'] for s in row['samples']} for row in args['snapshot_data']['records']]
        native.snapCtlFromMatrixDic(args['objects'], dictionaries)
        return {'retargeted': args['objects'], 'sample_counts': [len(d) for d in dictionaries]}
    finally:
        try:
            from .proxy import cleanup
            cleanup()
            for timer in ('saveAnimToListTimer', 'snapCtlFromMatrixDicTimer'):
                try:
                    cmds.timer(endTimer=True, name=_PREFIX + timer)
                except RuntimeError:
                    pass
            for plugin in reversed(plugins):
                if cmds.pluginInfo(plugin, query=True, unloadOk=True):
                    cmds.unloadPlugin(plugin)
        finally:
            try:
                if args['action'] == 'retarget':
                    if cmds.currentTime(query=True) != current:
                        cmds.currentTime(current)
                    if (cmds.ls(selection=True, long=True) or []) != selection:
                        cmds.select(selection, replace=True) if selection else cmds.select(clear=True)
                    cmds.namespace(setNamespace=namespace)
                    cmds.autoKeyframe(state=auto)
            finally:
                _ACTIVE, _ARGS, _HELPERS, _TARGETS = False, {}, set(), set()
