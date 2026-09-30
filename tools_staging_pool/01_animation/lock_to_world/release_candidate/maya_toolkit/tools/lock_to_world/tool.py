from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

AXES = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
DEFAULTS = {'action': 'lock', 'objects': [], 'start': None, 'end': None, 'attributes': [], 'use_channel_box': False, 'allow_reference_edits': False}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {'action': {'type': 'string', 'enum': ['lock', 'open_ui'], 'default': 'lock'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'start': {'type': ['integer', 'null']}, 'end': {'type': ['integer', 'null']}, 'attributes': {'type': 'array', 'items': {'type': 'string', 'enum': AXES}, 'uniqueItems': True}, 'use_channel_box': {'type': 'boolean', 'default': False}, 'allow_reference_edits': {'type': 'boolean', 'default': False}}}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    a = dict(DEFAULTS, **kwargs)
    if a['action'] not in ('lock', 'open_ui') or any(type(a[k]) is not bool for k in ('use_channel_box', 'allow_reference_edits')):
        raise ValueError('action/bool无效')
    if not isinstance(a['objects'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in a['objects']) or len(set(a['objects'])) != len(a['objects']):
        raise ValueError('objects须明确唯一transform数组')
    if not isinstance(a['attributes'], list) or any(n not in AXES for n in a['attributes']) or len(set(a['attributes'])) != len(a['attributes']):
        raise ValueError('attributes须唯一TR六轴短名')
    if a['use_channel_box'] and a['attributes']:
        raise ValueError('显式attributes和channelBox不能同时指定')
    for key in ('start', 'end'):
        if a[key] is not None and type(a[key]) is not int:
            raise ValueError(key + '须整数/null')
    if a['start'] is not None and a['end'] is not None and a['start'] > a['end']:
        raise ValueError('范围反转')
    return a


def plan(**kwargs):
    a = normalize(**kwargs)
    from maya import cmds as c
    from maya.api import OpenMaya as om
    from . import runtime as r
    if r._ACTIVE:
        raise ValueError('已有Lock运行')
    if a['action'] == 'open_ui':
        if c.about(batch=True):
            raise ValueError('真实Maya GUI需要')
        return a
    if c.currentUnit(query=True, angle=True) != 'deg' or c.currentUnit(query=True, linear=True) != 'cm' or not c.undoInfo(query=True, state=True):
        raise ValueError('需要degree/cm和Undo开启')
    start = int(c.playbackOptions(query=True, minTime=True)) if a['start'] is None else a['start']
    end = int(c.playbackOptions(query=True, maxTime=True)) if a['end'] is None else a['end']
    if start > end or end - start > 10000:
        raise ValueError('范围反转/大于10001帧')
    attrs = list(a['attributes'])
    if a['use_channel_box']:
        if c.about(batch=True) or not c.channelBox('mainChannelBox', exists=True):
            raise ValueError('读取channelBox需要真实Maya')
        aliases = {'translate' + axis.upper(): 't' + axis for axis in 'xyz'}
        aliases.update({'rotate' + axis.upper(): 'r' + axis for axis in 'xyz'})
        attrs = [aliases.get(x, x) for x in c.channelBox('mainChannelBox', query=True, selectedMainAttributes=True) or []]
        if any(x not in AXES for x in attrs):
            raise ValueError('channelBox只接受TR六轴')
    attrs = attrs or list(AXES)
    objects = a['objects'] or c.ls(selection=True, long=True) or []
    if not objects or len(objects) * (end - start + 1) > 200000:
        raise ValueError('无对象/总采样过大')
    result = []
    unit = [1.0 if i % 5 == 0 else 0.0 for i in range(16)]
    for name in objects:
        found = c.ls(name, long=True) or []
        if len(found) != 1 or c.nodeType(found[0]) != 'transform' or len(c.ls(found[0], allPaths=True, long=True) or []) != 1:
            raise ValueError('唯一非实例transform需要')
        n = found[0]
        if n in result or c.lockNode(n, query=True, lock=True)[0] or c.referenceQuery(n, isNodeReferenced=True) and not a['allow_reference_edits']:
            raise ValueError('重复/对象锁/引用编辑未允许')
        result.append(n)
        for compound in ('rotatePivot', 'rotatePivotTranslate', 'rotateAxis'):
            if any(c.listConnections(n + '.' + attr, source=True, destination=False) for attr in [compound] + [compound + x for x in 'XYZ']):
                raise ValueError('pivot/rotateAxis动画驱动拒绝')
        if any(abs(v) > 1e-9 for attr in ('rotatePivotTranslate', 'rotateAxis') for v in c.getAttr(n + '.' + attr)[0]) or any(abs(x-y) > 1e-9 for x,y in zip(c.getAttr(n + '.offsetParentMatrix'), unit)) or c.listConnections(n + '.offsetParentMatrix', source=True, destination=False):
            raise ValueError('目标额外变换不支持')
        for compound in ('translate', 'rotate'):
            if any(not c.nodeType(d).startswith('animCurve') for d in c.listConnections(n + '.' + compound, source=True, destination=False) or []):
                raise ValueError('复合通道外部驱动')
        for attr in attrs:
            plug = n + '.' + attr
            if c.getAttr(plug, lock=True):
                raise ValueError('写入通道锁: ' + plug)
            for driver in c.listConnections(plug, source=True, destination=False) or []:
                if not c.nodeType(driver).startswith('animCurve') or c.referenceQuery(driver, isNodeReferenced=True) or c.lockNode(driver, query=True, lock=True)[0]:
                    raise ValueError('写入曲线/驱动不支持')
                if any((c.ls(out, long=True) or [''])[0] != n for out in c.listConnections(driver + '.output', source=False, destination=True) or []):
                    raise ValueError('写入曲线共享')
        if abs(om.MMatrix(r.world_matrix(n, start)).det4x4()) < 1e-12:
            raise ValueError('起始矩阵奇异')
        if any(abs(om.MMatrix(c.getAttr(n + '.parentInverseMatrix[0]', time=frame)).det4x4()) < 1e-12 for frame in range(start, end + 1)):
            raise ValueError('父逆矩阵奇异')
    a.update(objects=result, attributes=attrs, start=start, end=end)
    return a


class LockToWorldTool(BaseMayaTool):
    tool_id = 'lock_to_world'
    tool_name = 'JOP世界锁定 v09'
    category = 'animation'
    version = 'v09-candidate.1'
    description = '完整起始世界矩阵/冻结pivot/逐帧父逆补偿/通道掩码/原UI，安全预检、Undo与助手清理。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读范围/矩阵/枢轴/写入通道预检')
        except Exception as e:
            return ToolResult.fail(message=str(e), errors=[str(e)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['只键所选局部轴，部分轴不保证完整世界锁；不键scale；插件状态不由场景Undo恢复'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
