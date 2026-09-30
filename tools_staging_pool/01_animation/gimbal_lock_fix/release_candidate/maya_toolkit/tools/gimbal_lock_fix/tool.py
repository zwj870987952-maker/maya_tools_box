import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = {'action': 'detect', 'objects': [], 'threshold': 45.0, 'start': None, 'end': None, 'samples_per_frame': 1}
SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['detect', 'fix', 'open_ui'], 'default': 'detect'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'threshold': {'type': 'number', 'exclusiveMinimum': 0, 'default': 45.0}, 'start': {'type': ['number', 'null'], 'default': None}, 'end': {'type': ['number', 'null'], 'default': None}, 'samples_per_frame': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 1}}, 'additionalProperties': False}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('detect', 'fix', 'open_ui'):
        raise ValueError('action无效')
    if not isinstance(args['objects'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['objects']) or len(set(args['objects'])) != len(args['objects']):
        raise ValueError('objects须明确不重复节点名数组')
    for name in ('threshold', 'start', 'end'):
        value = args[name]
        if value is None and name != 'threshold':
            continue
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(name + '须有限数值')
    if args['threshold'] <= 0 or type(args['samples_per_frame']) is not int or not 1 <= args['samples_per_frame'] <= 100:
        raise ValueError('阈值/采样密度无效')
    if args['start'] is not None and args['end'] is not None and args['start'] > args['end']:
        raise ValueError('时间范围反转')
    return args


def plan(**kwargs):
    args = normalize(**kwargs)
    from maya import cmds
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原生界面需要真实Maya GUI')
        return args
    if cmds.currentUnit(query=True, angle=True) != 'deg':
        raise ValueError('原算法只支持degree旋转单位')
    if args['action'] == 'fix' and not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Undo')
    objects = args['objects'] or cmds.ls(selection=True, long=True) or []
    if not objects:
        raise ValueError('需要对象或当前选择')
    plans, identities = [], set()
    for value in objects:
        matches = cmds.ls(value, long=True) or []
        if len(matches) != 1 or not cmds.objectType(matches[0], isAType='transform'):
            raise ValueError('对象缺失/不唯一transform: ' + value)
        node = matches[0]
        identity = cmds.ls(node, uuid=True)[0]
        if identity in identities:
            raise ValueError('重复对象UUID')
        identities.add(identity)
        if args['action'] == 'fix' and (cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]):
            raise ValueError('修复对象引用/锁定')
        if cmds.listConnections(node + '.rotateOrder', source=True, destination=False):
            raise ValueError('不支持动画/驱动rotateOrder')
        curves, times = [], set()
        for attr in ('rotateX', 'rotateY', 'rotateZ'):
            plug = node + '.' + attr
            drivers = cmds.listConnections(plug, source=True, destination=False) or []
            if len(drivers) != 1 or cmds.nodeType(drivers[0]) != 'animCurveTA':
                raise ValueError('需要三轴各自直接angular animCurveTA；不支持约束/层或缺轴: ' + plug)
            curve = drivers[0]
            keys = cmds.keyframe(curve, query=True, timeChange=True) or []
            if not keys or any(not math.isfinite(t) for t in keys):
                raise ValueError('旋转曲线无有效key')
            times.update(keys)
            if args['action'] == 'fix':
                if cmds.getAttr(plug, lock=True) or cmds.referenceQuery(curve, isNodeReferenced=True) or cmds.lockNode(curve, query=True, lock=True)[0]:
                    raise ValueError('旋转通道/曲线引用锁定')
                outputs = cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
                if len(outputs) != 1 or outputs[0].split('.', 1)[1] != attr or cmds.ls(outputs[0].split('.')[0], uuid=True)[0] != identity:
                    raise ValueError('旋转曲线有共享/外部输出')
            curves.append(curve)
        times = sorted(times)
        start = times[0] if args['start'] is None else args['start']
        end = times[-1] if args['end'] is None else args['end']
        if start > end:
            raise ValueError('时间范围反转')
        chosen = [t for t in times if start <= t <= end]
        if args['action'] == 'fix' and not chosen:
            raise ValueError('范围内无原始关键帧；不创建边界样本')
        count = len(chosen)
        if args['samples_per_frame'] > 1:
            count += sum(max(0, int((b - a) * args['samples_per_frame']) - 1) for a, b in zip(chosen, chosen[1:]) if b - a > 1)
        if count > 200000:
            raise ValueError('采样数量过大')
        plans.append({'object': node, 'curves': curves, 'times': times, 'start': start, 'end': end, 'sample_count': count, 'rotation_order': cmds.getAttr(node + '.rotateOrder')})
    args.update(objects=[p['object'] for p in plans], plans=plans)
    return args


class GimbalFixTool(BaseMayaTool):
    tool_id = 'gimbal_lock_fix'
    tool_name = '四元数动画旋转修复候选'
    category = 'animation'
    version = '1.0-candidate.1'
    description = '完整原四元数角速度检测/SLERP/原生UI；六种rotationOrder正确重排、只读检测、曲线保护和Undo。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读曲线/关键帧/单位/共享与范围检查')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['原算法改写欧拉表示/采样与整条曲线spline切线，不保证消除所有万向锁或保留长转圈动画；先备份复验'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
