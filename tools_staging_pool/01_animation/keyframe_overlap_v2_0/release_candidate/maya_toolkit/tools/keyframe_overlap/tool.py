import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = {'action': 'inventory', 'objects': [], 'record_id': '', 'mode_name': 'aim_xb', 'distance': 3.0, 'dynamic': 3.0, 'offset': 0.0, 'smoothness': True, 'aim_invert': False, 'start': None, 'end': None}
MODES = ['aim_xb', 'aim_yb', 'aim_zb', 'pos_xzb', 'pos_yb', 'pos_xyzb']
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {'action': {'type': 'string', 'enum': ['inventory', 'create', 'bake', 'open_ui'], 'default': 'inventory'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'record_id': {'type': 'string', 'default': ''}, 'mode_name': {'type': 'string', 'enum': MODES}, 'distance': {'type': 'number', 'minimum': 0.001, 'maximum': 500}, 'dynamic': {'type': 'number', 'minimum': 0, 'maximum': 6}, 'offset': {'type': 'number', 'minimum': -10, 'maximum': 10}, 'smoothness': {'type': 'boolean', 'default': True}, 'aim_invert': {'type': 'boolean', 'default': False}, 'start': {'type': ['integer', 'null']}, 'end': {'type': ['integer', 'null']}}}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('inventory', 'create', 'bake', 'open_ui') or args['mode_name'] not in MODES:
        raise ValueError('无效action/mode')
    if not isinstance(args['objects'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['objects']) or len(set(args['objects'])) != len(args['objects']):
        raise ValueError('objects须唯一transform数组')
    if not isinstance(args['record_id'], str) or any(type(args[k]) is not bool for k in ('smoothness', 'aim_invert')):
        raise ValueError('record_id/bool参数错误')
    for name, minimum, maximum in (('distance', .001, 500), ('dynamic', 0, 6), ('offset', -10, 10)):
        if type(args[name]) not in (int, float) or not math.isfinite(args[name]) or not minimum <= args[name] <= maximum:
            raise ValueError(name + '超范围/非有限数')
    for name in ('start', 'end'):
        if args[name] is not None and type(args[name]) is not int:
            raise ValueError(name + '须整数/null')
    if args['start'] is not None and args['end'] is not None and args['end'] <= args['start']:
        raise ValueError('至少两帧递增范围')
    return args


def plan(**kwargs):
    args = normalize(**kwargs)
    from maya import cmds
    from . import runtime as r
    if r._ACTIVE:
        raise ValueError('已有Overlap运行')
    r.machine_check()
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('真实Maya GUI需要')
        return args
    if args['action'] == 'inventory':
        return args
    if not cmds.undoInfo(query=True, state=True) or cmds.play(query=True, state=True):
        raise ValueError('需要Undo开启并停止播放')
    if cmds.currentUnit(query=True, angle=True) != 'deg' or cmds.currentUnit(query=True, linear=True) != 'cm':
        raise ValueError('只验证degree/cm')
    start = int(round(cmds.playbackOptions(query=True, minTime=True))) if args['start'] is None else args['start']
    end = int(round(cmds.playbackOptions(query=True, maxTime=True))) if args['end'] is None else args['end']
    if not 0 < end - start <= 10000:
        raise ValueError('范围须2..10001帧')
    args.update(start=start, end=end)
    row = r.get_record(args['record_id']) if args['action'] == 'bake' else None
    if row and row.get('state') != 'editable':
        raise ValueError('创建失败的半成品请先Undo，不自动烘焙/清理')
    names = r.controls(row) if row else args['objects'] or cmds.ls(selection=True, long=True) or []
    if not names or len(names) > 100 or len(names) * (end - start + 21) > 100000:
        raise ValueError('需要控制器/总模拟量过大')
    if row and args['objects']:
        supplied = [cmds.ls(n, long=True)[0] for n in args['objects']]
        if supplied != names:
            raise ValueError('bake必须覆盖完整record')
    owned = r.validate_graph(row) if row else set()
    nodes = []
    for name in names:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1 or cmds.nodeType(found[0]) != 'transform' or len(cmds.ls(found[0], allPaths=True, long=True) or []) != 1:
            raise ValueError('需要唯一非实例transform')
        n = found[0]
        if cmds.referenceQuery(n, isNodeReferenced=True) or cmds.lockNode(n, query=True, lock=True)[0]:
            raise ValueError('引用/对象锁拒绝')
        if n in nodes:
            raise ValueError('重复控制器')
        nodes.append(n)
        if not row and any(n in r.controls(x) for x in r.records()):
            raise ValueError('已有自有Overlap，请先bake或Undo')
        if not cmds.listRelatives(n, shapes=True, fullPath=True):
            raise ValueError('控制器需要shape供原尺寸计算')
        for attr in ('translate', 'rotate'):
            for driver in cmds.listConnections(n + '.' + attr, source=True, destination=False) or []:
                if not cmds.nodeType(driver).startswith('animCurve') and r.identity(driver) not in owned:
                    raise ValueError('复合通道外部驱动拒绝')
        for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
            if cmds.getAttr(n + '.' + attr, lock=True):
                raise ValueError('六轴须可写')
            for driver in cmds.listConnections(n + '.' + attr, source=True, destination=False) or []:
                if not cmds.nodeType(driver).startswith('animCurve') and r.identity(driver) not in owned:
                    raise ValueError('外部驱动/约束/动画层拒绝')
        for constraint in cmds.listRelatives(n, type='constraint', fullPath=True) or []:
            if r.identity(constraint) not in owned:
                raise ValueError('不删除外部约束')
        curves = set(cmds.listConnections(n, source=True, destination=False, type='animCurve') or [])
        curves.update(cmds.ls(cmds.listHistory(n, pruneDagObjects=True) or [], type='animCurve') or [])
        for curve in curves:
            if cmds.referenceQuery(curve, isNodeReferenced=True) or cmds.lockNode(curve, query=True, lock=True)[0]:
                raise ValueError('曲线引用/锁')
            if any((cmds.ls(out, long=True) or [''])[0] != n and r.identity(out) not in owned for out in cmds.listConnections(curve + '.output', source=False, destination=True) or []):
                raise ValueError('曲线共享外部对象')
    args.update(objects=nodes, _row=row)
    return args


class KeyframeOverlapTool(BaseMayaTool):
    tool_id = 'keyframe_overlap'
    tool_name = 'KF Overlap粒子延迟 v2.0'
    category = 'animation'
    version = '2.0-candidate.1'
    description = '完整粒子延迟、六模式locator/约束、编辑定位器和回烘焙优化；自有图身份、Undo、原用户机器限制。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            data = plan(**kwargs)
            data.pop('_row', None)
            return ToolResult.ok(data=data, dry_run=True, message='只读参数/自有图/曲线/范围预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['创建留下自有定位器/约束供编辑；Bake会删自有图和范围外键、优化不保证误差；粒子缓存求值需备份环境'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
