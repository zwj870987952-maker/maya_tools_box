"""Robert Joosten Timeline Marker adaptation, GPL-3.0-or-later; see upstream/LICENSE."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import model

ACTIONS = ['inspect', 'add', 'remove', 'clear', 'set', 'remap', 'open_ui', 'close_ui', 'hotkey']
DEFAULTS = {'action': 'inspect', 'frames': [], 'colors': [], 'comments': [], 'color': [0, 255, 0], 'comment': '', 'old_range': [], 'new_range': [], 'hotkey_action': 'add'}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'},
    'frames': {'type': 'array', 'maxItems': 20000, 'uniqueItems': True, 'items': {'type': 'integer', 'minimum': -1000000, 'maximum': 1000000}},
    'colors': {'type': 'array', 'maxItems': 20000, 'items': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': {'type': 'integer', 'minimum': 0, 'maximum': 255}}},
    'comments': {'type': 'array', 'maxItems': 20000, 'items': {'type': 'string', 'maxLength': 4096}},
    'color': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': {'type': 'integer', 'minimum': 0, 'maximum': 255}, 'default': [0, 255, 0]},
    'comment': {'type': 'string', 'maxLength': 4096, 'default': ''},
    'old_range': {'type': 'array', 'minItems': 2, 'maxItems': 2, 'items': {'type': 'integer'}},
    'new_range': {'type': 'array', 'minItems': 2, 'maxItems': 2, 'items': {'type': 'integer'}},
    'hotkey_action': {'type': 'string', 'enum': ['add', 'remove', 'clear'], 'default': 'add'}
}}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    a = dict(DEFAULTS, **kwargs)
    if not isinstance(a['action'], str) or a['action'] not in ACTIONS or a['hotkey_action'] not in ('add', 'remove', 'clear'):
        raise ValueError('action无效')
    for key in ('frames', 'colors', 'comments', 'old_range', 'new_range'):
        if not isinstance(a[key], list):
            raise ValueError(key + '须列表')
    a['frames'] = [model.frame(v) for v in a['frames']]
    if len(set(a['frames'])) != len(a['frames']) or len(a['frames']) > model.MAX_MARKERS:
        raise ValueError('frames须唯一且≤20000')
    a['color'] = model.color(a['color'])
    a['comment'] = model.comment(a['comment'])
    a['colors'] = [model.color(v) for v in a['colors']]
    a['comments'] = [model.comment(v) for v in a['comments']]
    for k in ('old_range', 'new_range'):
        a[k] = [model.frame(v) for v in a[k]]
    relevant = {'add': {'frames', 'color', 'comment'}, 'remove': {'frames'}, 'set': {'frames', 'colors', 'comments'}, 'remap': {'old_range', 'new_range'}, 'hotkey': {'hotkey_action'}}.get(a['action'], set()) | {'action'}
    if set(kwargs) - relevant:
        raise ValueError('此action不接受提供的其他参数')
    if a['action'] in ('add', 'remove') and not a['frames']:
        raise ValueError('需要明确frames')
    if a['action'] == 'set':
        model.dataset({k: a[k] for k in ('frames', 'colors', 'comments')})
    if a['action'] == 'remap':
        model.remap(model.empty(), a['old_range'], a['new_range'])
    return a


def plan(**kwargs):
    a = normalize(**kwargs)
    from maya import cmds
    from . import runtime
    if runtime.ACTIVE:
        raise ValueError('已有标记写入正在运行')
    if a['action'] in ('open_ui', 'close_ui', 'hotkey'):
        if cmds.about(batch=True):
            raise ValueError('需要真实Maya时间轴GUI')
        if a['action'] in ('close_ui', 'hotkey') and runtime.widget() is None:
            raise ValueError('候选Timeline Marker未打开')
        if a['action'] == 'hotkey' and not cmds.undoInfo(query=True, state=True):
            raise ValueError('Undo必须开启')
        return a
    current = runtime.read_scene()
    a['before'] = current
    if a['action'] == 'inspect':
        return a
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Undo必须开启')
    if a['action'] == 'clear':
        after = model.empty()
    elif a['action'] == 'set':
        after = model.dataset({k: a[k] for k in ('frames', 'colors', 'comments')})
    elif a['action'] == 'remap':
        after = model.remap(current, a['old_range'], a['new_range'])
    else:
        records = dict(zip(current['frames'], zip(current['colors'], current['comments'])))
        for f in a['frames']:
            if a['action'] == 'add':
                records[f] = (a['color'], a['comment'])
            else:
                records.pop(f, None)
        after = model.dataset({'frames': list(records), 'colors': [v[0] for v in records.values()], 'comments': [v[1] for v in records.values()]})
    a['after'] = after
    return a


class TimelineMarkerTool(BaseMayaTool):
    tool_id = 'timeline_marker'
    tool_name = '原生时间轴颜色标记与注释'
    category = 'animation'
    version = '2.0.2-candidate.1'
    description = '完整原时间轴覆层/右键菜单/颜色注释/范围移动，保留fileInfo格式并通过自有命令支持Undo；不改动画键。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读参数/标记格式/Undo和GUI前提检查')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['仅场景标记数据由Undo恢复；GUI/插件/回调为会话状态，不写用户hotkeys或文件'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
