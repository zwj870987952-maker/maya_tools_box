import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = {'action': 'reduce', 'curves': [], 'error': 0.1, 'step': 1.0, 'weightedTangents': True, 'tangentSplitAuto': False, 'tangentSplitExisting': False, 'tangentSplitAngleThreshold': False, 'tangentSplitAngleThresholdValue': 15.0}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'reduce', 'open_ui'], 'default': 'reduce'}, 'curves': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'error': {'type': 'number', 'exclusiveMinimum': 0, 'maximum': 1000, 'default': .1}, 'step': {'type': 'number', 'minimum': .1, 'maximum': 100, 'default': 1}, 'tangentSplitAngleThresholdValue': {'type': 'number', 'minimum': .01, 'maximum': 180, 'default': 15}}}
SCHEMA['properties'].update({k: {'type': 'boolean', 'default': v} for k, v in DEFAULTS.items() if type(v) is bool})


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    a = dict(DEFAULTS, **kwargs)
    if a['action'] not in ('inspect', 'reduce', 'open_ui') or any(type(a[k]) is not bool for k, v in DEFAULTS.items() if type(v) is bool):
        raise ValueError('action/bool无效')
    if not isinstance(a['curves'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in a['curves']) or len(set(a['curves'])) != len(a['curves']):
        raise ValueError('curves须明确唯一curve名')
    for k, minimum, maximum in (('error', 0, 1000), ('step', .1, 100), ('tangentSplitAngleThresholdValue', .01, 180)):
        if type(a[k]) not in (int, float) or not math.isfinite(a[k]) or a[k] < minimum or a[k] > maximum or k == 'error' and a[k] == 0:
            raise ValueError(k + '超范围/非有限数')
    return a


def plan(**kwargs):
    a = normalize(**kwargs)
    from maya import cmds as c
    from . import runtime as r
    if r._ACTIVE:
        raise ValueError('已有Reduction运行')
    if a['action'] == 'open_ui':
        if c.about(batch=True):
            raise ValueError('真实Maya Qt GUI需要')
        return a
    curves = a['curves'] or r.selection_curves()
    if not curves or len(curves) > 1000:
        raise ValueError('需要1..1000条曲线')
    if a['action'] == 'reduce' and not c.undoInfo(query=True, state=True):
        raise ValueError('Undo必须开启')
    result, count = [], 0
    for name in curves:
        found = c.ls(name) or []
        if len(found) != 1 or not r.suitable(found[0]):
            raise ValueError('需要本地不共享可写TL/TA/TU、≥2键、非step无时间重映射: ' + name)
        n = found[0]
        if n in result:
            raise ValueError('重复曲线')
        result.append(n)
        frames = c.keyframe(n, query=True, timeChange=True)
        samples = int(math.ceil((math.ceil(frames[-1]) + 1 - math.floor(frames[0])) / a['step']))
        if samples > 20000 or samples < 2:
            raise ValueError('单曲线采样须2..20000')
        count += samples
        if count > 100000:
            raise ValueError('总采样超过100000')
        values = c.keyframe(n, query=True, valueChange=True) or []
        if any(not math.isfinite(v) for v in frames + values):
            raise ValueError('曲线非有限数据')
    a['curves'] = result
    return a


class KeyframeReductionTool(BaseMayaTool):
    tool_id = 'keyframe_reduction'
    tool_name = 'Bezier最小二乘关键帧精简'
    category = 'animation'
    version = '0.0.1-candidate.1'
    description = '完整原Bezier递归拟合/加权切线/三种拆分与Qt过滤UI，Python3、自有curve范围/Undo，只读预检。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读curve/连接/键/采样预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['全曲线重采样可移动子帧端点/改变切线和Infinity；原拟合误差不保证最终Maya间帧最大值误差'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
