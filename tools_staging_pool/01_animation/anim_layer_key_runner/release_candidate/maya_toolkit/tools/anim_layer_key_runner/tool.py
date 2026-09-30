"""Framework adapter; preflight discovers times but never evaluates custom code."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = dict(objects=None, command='asAutoSwitchFKIK', layer='auto', language='mel',
                only_in_playback=True, continue_on_error=True, max_frames=10000)
COMMAND_EFFECTS = '命令以 Maya 进程权限执行；文件写入、导出、网络、禁用 Undo 等影响无法由本工具预检或撤回。'


def normalize(kwargs):
    unknown = set(kwargs) - set(DEFAULTS)
    if unknown:
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(unknown)))
    args = dict(DEFAULTS, **kwargs)
    objects = args['objects']
    if isinstance(objects, str):
        objects = [objects]
    if objects is not None and (not isinstance(objects, list) or not objects or
                               any(not isinstance(o, str) or not o.strip() for o in objects)):
        raise ValueError('objects must be null, a name or a non-empty array of names')
    args['objects'] = objects
    if not isinstance(args['command'], str) or not args['command'].strip():
        raise ValueError('command must be a non-empty string')
    if args['language'] not in ('mel', 'python'):
        raise ValueError('language must be mel or python')
    if not isinstance(args['layer'], str) or not args['layer'].strip():
        raise ValueError('layer must be a non-empty name, auto or All')
    for name in ('only_in_playback', 'continue_on_error'):
        if type(args[name]) is not bool:
            raise ValueError(name + ' must be boolean')
    if type(args['max_frames']) is not int or not 1 <= args['max_frames'] <= 100000:
        raise ValueError('max_frames must be an integer in [1, 100000]')
    if args['language'] == 'python':
        compile(args['command'], '<anim_layer_key_runner preflight>', 'exec')
    return args


class AnimLayerKeyRunnerTool(BaseMayaTool):
    tool_id = 'anim_layer_key_runner'
    tool_name = '动画层逐关键帧命令执行器'
    category = 'Animation'
    version = '1.1.0'
    description = '查询选定动画层的关键帧，在每帧执行显式 MEL/Python 命令；dry_run 仅列帧，不执行命令。命令副作用取决于输入脚本。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'objects': {'anyOf': [{'type': 'null'}, {'type': 'string', 'minLength': 1}, {'type': 'array', 'minItems': 1, 'items': {'type': 'string', 'minLength': 1}}], 'default': None},
            'command': {'type': 'string', 'minLength': 1, 'default': 'asAutoSwitchFKIK', 'description': COMMAND_EFFECTS},
            'layer': {'type': 'string', 'minLength': 1, 'default': 'auto', 'description': '仅用层筛选调度帧，不改变命令写入的动画层。'},
            'language': {'type': 'string', 'enum': ['mel', 'python'], 'default': 'mel'},
            'only_in_playback': {'type': 'boolean', 'default': True},
            'continue_on_error': {'type': 'boolean', 'default': True},
            'max_frames': {'type': 'integer', 'minimum': 1, 'maximum': 100000, 'default': 10000},
        },
    }

    def _prepare(self, kwargs):
        args = normalize(kwargs)
        from . import operations as op
        if not op.cmds.undoInfo(query=True, state=True):
            raise ValueError('Enable Maya Undo before running')
        source = args['objects'] if args['objects'] is not None else (op.cmds.ls(selection=True, long=True) or [])
        objects = []
        for obj in source:
            matches = op.cmds.ls(obj, long=True) or []
            if len(matches) != 1 or '.' in matches[0]:
                raise ValueError('Object must resolve uniquely to a node: ' + obj)
            node = matches[0]
            if node not in objects:
                objects.append(node)
        if not objects:
            raise ValueError('Select target objects or provide objects')
        frames, layer, curves = op.get_keyframes_from_layer(objects, args['layer'], args['only_in_playback'])
        if len(frames) > args['max_frames']:
            raise ValueError('Scheduled frame count exceeds max_frames')
        args.update(objects=objects, layer=layer)
        return args, frames, curves

    def validate(self, **kwargs):
        try:
            args, frames, curves = self._prepare(kwargs)
            return ToolResult.ok('动画层 [{}] 共 {} 个调度帧。命令未执行。'.format(args['layer'], len(frames)),
                                 data=dict(layer=args['layer'], objects=args['objects'], frames=frames, count=len(frames), curves=curves),
                                 warnings=[COMMAND_EFFECTS, 'MEL 语法/过程存在性与 Python 命令依赖尚未运行验证。'], dry_run=True)
        except Exception as error:
            return ToolResult.fail('预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from . import operations as op
        args, frames, curves = self._prepare(kwargs)
        if frames:
            report = op.run_frames(args['objects'], frames, args['layer'], args['command'], args['language'], args['continue_on_error'])
        else:
            report = dict(layer=args['layer'], frames=[], completed_frames=[], count=0, total=0, errors=[])
        report.update(curves=curves, objects=args['objects'])
        return ToolResult(success=not report['errors'],
                          message='动画层 [{}] 已完成 {}/{} 个调度帧。'.format(args['layer'], report['count'], report['total']),
                          data=report, errors=[str(e) for e in report['errors']],
                          warnings=[COMMAND_EFFECTS, '失败不会自动回滚；已完成帧可能留下部分修改。'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(self)
