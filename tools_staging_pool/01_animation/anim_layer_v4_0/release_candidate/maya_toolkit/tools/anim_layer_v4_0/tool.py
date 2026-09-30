"""Meaningful suite bridge: typed procedures, inventory, readonly preflight and Undo."""
from pathlib import Path

from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import CATALOG, DEFAULTS, HEADLESS_PROCEDURES, PACKAGE, PROCEDURES, normalize, resources

LOAD_WARNING = 'source 会覆盖进程 MEL 定义；完整版还重建编辑器/设置 UI、optionVar、scriptJobs。这些不能由 Maya 场景 Undo 撤回。'
CALL_WARNING = '原始 MEL 回调/过程未重写；参数预检不等于原算法已成功、参考节点可写或合并/烘焙正确。异常不自动回滚。'


class AnimLayerSuiteTool(BaseMayaTool):
    tool_id = 'anim_layer_v4_0'
    tool_name = 'Anim Layer v4.0 第三方层编辑器套件'
    category = 'Animation'
    version = '4.0.1-adapter'
    description = '保留完整版/NoUI 原始 MEL 与全部 global 过程。先 inventory 查签名，再通过 invoke 调用；dry_run 不 source、不运行过程。遵循包内原许可。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'action': {'type': 'string', 'enum': ['inventory', 'load', 'invoke', 'open_ui'], 'default': 'inventory'},
            'edition': {'type': 'string', 'enum': ['no_ui', 'full'], 'default': 'no_ui'},
            'procedure': {'type': 'string', 'enum': [''] + PROCEDURES, 'default': ''},
            'arguments': {'type': 'object', 'default': {}, 'description': '先 inventory 查所选过程 parameters；键与签名完全一致。值为 string/int/float 或对应数组，运行时精确验证。',
                          'additionalProperties': {'anyOf': [{'type': 'string'}, {'type': 'number'}, {'type': 'array', 'items': {'anyOf': [{'type': 'string'}, {'type': 'number'}]}}]}},
            'force_reload': {'type': 'boolean', 'default': False, 'description': '明确重新 source 原文件；不会卸载其他文件定义的 MEL。'},
            'restore_runtime_state': {'type': 'boolean', 'default': True, 'description': '过程后尽力恢复 evaluation mode/refresh suspension；显式 viewport 开关过程保留其作用。'},
        },
        'allOf': [{'if': {'properties': {'action': {'const': 'invoke'}}, 'required': ['action']},
                   'then': {'required': ['procedure'], 'properties': {'procedure': {'minLength': 1}}}}],
    }

    def _prepare(self, kwargs):
        args, signature, command = normalize(kwargs)
        resources()
        data = dict(action=args['action'], edition=args['edition'], procedure=args['procedure'],
                    arguments=args['arguments'], signature=signature, mel_command=command,
                    resource_count=len(CATALOG['resources']), source_executed=False)
        if args['action'] == 'inventory':
            data['procedures'] = ({args['procedure']: signature} if signature else CATALOG['editions'][args['edition']]['procedures'])
            data['top_level_lines'] = CATALOG['editions'][args['edition']]['top_level_lines']
            return args, data
        import maya.cmds as cmds
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('Enable Maya Undo before loading/running this suite')
        if cmds.about(batch=True) and (args['edition'] == 'full' or args['action'] == 'open_ui' or
                                       (args['action'] == 'invoke' and args['procedure'] not in HEADLESS_PROCEDURES)):
            raise ValueError('This edition/procedure requires interactive Maya with the stock layer/Channel Box/time slider UI')
        # Some suite arguments represent MEL/UI labels rather than nodes; only the
        # clearly declared object/layer lists and known layer names are checked here.
        for name, value in args['arguments'].items():
            if name in ('objects', 'layers', 'anim_layers_name', 'anim_layer_name'):
                names = value if isinstance(value, list) else [value]
                for node in names:
                    if name in ('anim_layer_name', 'anim_layers_name') and node == 'BaseAnimation':
                        # Upstream treats this as a direct-curve query sentinel even
                        # before Maya creates a real BaseAnimation node.
                        continue
                    if node and not cmds.objExists(node):
                        raise ValueError('Named target does not exist: ' + node)
        if args['procedure'] == 'animLayersSaveExportClbc':
            target = Path(args['arguments']['file']).expanduser()
            if not target.is_absolute() or not target.parent.is_dir() or target.exists():
                raise ValueError('Export requires an absolute, new file in an existing directory; overwriting is refused')
            data['external_file'] = str(target)
        data['selection'] = cmds.ls(selection=True, long=True) or []
        return args, data

    def validate(self, **kwargs):
        try:
            args, data = self._prepare(kwargs)
            return ToolResult.ok('套件资源/参数预检通过；MEL 未 source 或执行。', data=data,
                                 warnings=[LOAD_WARNING, CALL_WARNING], dry_run=True)
        except Exception as error:
            return ToolResult.fail('预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args, data = self._prepare(kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok('套件过程目录。', data=data)
        from .runtime import invoke, load_suite
        warnings = [LOAD_WARNING, CALL_WARNING]
        try:
            data['load'] = load_suite(args['edition'], args['force_reload'], args['procedure'] or None)
            data['source_executed'] = data['load']['source_executed']
            if args['action'] == 'load':
                return ToolResult.ok('原始套件已加载。', data=data, warnings=warnings)
            command = 'anim_layer_util_menue();' if args['action'] == 'open_ui' else data['mel_command']
            restore = args['restore_runtime_state'] and args['procedure'] not in ('disable_viewport', 'enable_viewport')
            report = invoke(command, restore)
            data.update(report)
            errors = ([report['error']] if report['error'] else []) + report['restoration_errors']
            return ToolResult(success=not errors, message='MEL 调用结束。' if not errors else 'MEL 调用或状态恢复失败。',
                              data=data, errors=errors, warnings=warnings)
        except Exception as error:
            data['source_may_be_partially_loaded'] = True
            return ToolResult.fail('套件加载/调用失败: ' + str(error), errors=[str(error)], data=data)

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(self)
