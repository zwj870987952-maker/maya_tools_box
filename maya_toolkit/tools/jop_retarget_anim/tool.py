import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = {'action': 'capture', 'objects': [], 'bake': False, 'start': None, 'end': None, 'snapshot_data': {}, 'allow_reference_edits': False}
SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['capture', 'retarget', 'open_ui'], 'default': 'capture'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'bake': {'type': 'boolean', 'default': False}, 'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None}, 'snapshot_data': {'type': 'object', 'description': 'capture返回的完整records结构，可JSON序列化；retarget按UUID/reference上下文恢复默认对象'}, 'allow_reference_edits': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('capture', 'retarget', 'open_ui') or type(args['bake']) is not bool or type(args['allow_reference_edits']) is not bool:
        raise ValueError('action/bake/allow_reference_edits无效')
    if not isinstance(args['objects'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['objects']) or len(set(args['objects'])) != len(args['objects']):
        raise ValueError('objects须唯一明确transform名数组')
    for name in ('start', 'end'):
        if args[name] is not None and type(args[name]) is not int:
            raise ValueError(name + '须整数/null')
    if args['start'] is not None and args['end'] is not None and args['start'] > args['end']:
        raise ValueError('范围反转')
    if not isinstance(args['snapshot_data'], dict):
        raise ValueError('snapshot_data须object')
    return args


def snapshot_rows(data):
    if data.get('format') != 'maya_toolkit.jop_retarget_anim.v1' or not isinstance(data.get('records'), list) or not data['records'] or len(data['records']) > 1000:
        raise ValueError('非候选capture快照')
    rows = data['records']
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('node_uuid'), str) or not isinstance(row.get('reference_uuid'), str) or not isinstance(row.get('samples'), list) or not row['samples']:
            raise ValueError('快照来源/samples无效')
        seen = set()
        for sample in row['samples']:
            if not isinstance(sample, dict) or type(sample.get('time')) not in (int, float) or not math.isfinite(sample['time']) or sample['time'] in seen:
                raise ValueError('快照time无效/重复')
            seen.add(sample['time'])
            matrix = sample.get('matrix')
            if not isinstance(matrix, list) or len(matrix) != 16 or any(type(n) not in (int, float) or not math.isfinite(n) for n in matrix):
                raise ValueError('快照matrix须16有限数值')
    if sum(len(r['samples']) for r in rows) > 200000:
        raise ValueError('总样本过大')
    return rows


def plan(**kwargs):
    args = normalize(**kwargs)
    from maya import cmds
    from . import runtime
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原生GUI需要真实Maya')
        return args
    if runtime._ACTIVE:
        raise ValueError('已有Retarget运行中')
    if cmds.currentUnit(query=True, angle=True) != 'deg' or cmds.currentUnit(query=True, linear=True) != 'cm':
        raise ValueError('当前候选只验证degree/cm，先备份在此单位下验收')
    if args['action'] == 'retarget':
        rows = snapshot_rows(args['snapshot_data'])
        objects = args['objects'] or [runtime.resolve_row(r) for r in rows]
        if len(objects) != len(rows):
            raise ValueError('目标数量须与快照一一对应')
    else:
        rows = None
        objects = args['objects'] or cmds.ls(selection=True, long=True) or []
        if not objects:
            raise ValueError('需要控制器')
    nodes = []
    for name in objects:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1 or cmds.nodeType(found[0]) != 'transform' or len(cmds.ls(found[0], allPaths=True, long=True) or []) != 1:
            raise ValueError('需要唯一非实例transform控制器: ' + name)
        node = found[0]
        if node in nodes:
            raise ValueError('控制器重复')
        nodes.append(node)
        for pivot in ('rotatePivot', 'rotatePivotTranslate'):
            if any(cmds.listConnections(node + '.' + attr, source=True, destination=False) for attr in [pivot] + [pivot + axis for axis in 'XYZ']):
                raise ValueError('不支持动画/驱动pivot')
        if args['action'] == 'retarget':
            # Original six-channel decomposition does not solve these extra transforms.
            if any(cmds.listConnections(node + '.' + attr, source=True, destination=False) for attr in ('rotateAxis', 'rotateAxisX', 'rotateAxisY', 'rotateAxisZ', 'offsetParentMatrix')):
                raise ValueError('不支持目标rotateAxis/offsetParentMatrix驱动')
            if any(abs(v) > 1e-9 for attr in ('rotateAxis', 'rotatePivotTranslate') for v in cmds.getAttr(node + '.' + attr)[0]):
                raise ValueError('目标rotateAxis/rotatePivotTranslate须零')
            identity_matrix = [1.0 if i % 5 == 0 else 0.0 for i in range(16)]
            if any(abs(a - b) > 1e-9 for a, b in zip(cmds.getAttr(node + '.offsetParentMatrix'), identity_matrix)):
                raise ValueError('目标offsetParentMatrix须identity')
            if not cmds.undoInfo(query=True, state=True) or cmds.lockNode(node, query=True, lock=True)[0] or cmds.referenceQuery(node, isNodeReferenced=True) and not args['allow_reference_edits']:
                raise ValueError('Undo关闭/对象锁/引用编辑未允许')
            for compound in ('translate', 'rotate'):
                if any(not cmds.nodeType(driver).startswith('animCurve') for driver in cmds.listConnections(node + '.' + compound, source=True, destination=False) or []):
                    raise ValueError('复合通道有外部驱动')
            for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                plug = node + '.' + attr
                if cmds.getAttr(plug, lock=True):
                    raise ValueError('通道锁定: ' + plug)
                for source in cmds.listConnections(plug, source=True, destination=False) or []:
                    if not cmds.nodeType(source).startswith('animCurve'):
                        raise ValueError('目标通道有外部驱动: ' + plug)
            curves = set(cmds.listConnections(node, source=True, destination=False, type='animCurve') or [])
            curves.update(cmds.ls(cmds.listHistory(node, pruneDagObjects=True) or [], type='animCurve') or [])
            for curve in curves:
                if cmds.lockNode(curve, query=True, lock=True)[0] or cmds.referenceQuery(curve, isNodeReferenced=True):
                    raise ValueError('目标动画曲线引用/锁定')
                if any((cmds.ls(n, long=True) or [''])[0] != node for n in cmds.listConnections(curve + '.output', source=False, destination=True) or []):
                    raise ValueError('目标曲线被共享')
    if rows:
        from maya.api import OpenMaya as om
        for node, row in zip(nodes, rows):
            for sample in row['samples']:
                if abs(om.MMatrix(sample['matrix']).det4x4()) < 1e-12 or abs(om.MMatrix(cmds.getAttr(node + '.parentInverseMatrix[0]', time=sample['time'])).det4x4()) < 1e-12:
                    raise ValueError('快照/父逆矩阵奇异')
    else:
        args['start'] = int(cmds.playbackOptions(query=True, minTime=True)) if args['start'] is None else args['start']
        args['end'] = int(cmds.playbackOptions(query=True, maxTime=True)) if args['end'] is None else args['end']
        if args['start'] > args['end'] or args['end'] - args['start'] > 100000:
            raise ValueError('范围反转/过大')
        count = 0
        for node in nodes:
            times = list(range(args['start'], args['end'] + 1)) if args['bake'] else sorted(set(cmds.keyframe(node, time=(args['start'], args['end']), query=True, timeChange=True) or []))
            if not times:
                raise ValueError('当前范围控制器无key: ' + node)
            count += len(times)
        if count > 200000:
            raise ValueError('总样本过大')
    args.update(objects=nodes)
    return args


class JopRetargetTool(BaseMayaTool):
    tool_id = 'jop_retarget_anim'
    tool_name = 'JOP世界矩阵动画Retarget v09'
    category = 'animation'
    version = 'v09-candidate.1'
    description = '完整原multMatrix/quatToEuler/pivot修正与Bake/稀疏capture/UI，结构化UUID快照与保护、只读采样、Undo。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读采样范围/身份/通道/共享/矩阵预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['Retarget写六轴key并对目标执行原Euler过滤；插件状态不归普通Maya Undo；真人视窗验收待完成'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
