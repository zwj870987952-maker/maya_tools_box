import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

CATALOG = json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8'))
DEFAULTS = dict(action='inspect', procedure=None, targets=None, frame_range=None,
                allow_reference_edits=False, overlap=2.0, weight=0.5, softness=0.1,
                damping=0.4, jiggle_weight=0.7, attributes=None, cache_directory=None)
NUMBER_LIMITS = dict(overlap=(0, 10), weight=(0, 1), softness=(0, 1), damping=(0, 1), jiggle_weight=(0, 0.9))


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(set(kwargs) - set(DEFAULTS))))
    options = dict(DEFAULTS)
    options.update(kwargs)
    if options['action'] not in ('inspect', 'invoke', 'open_ui', 'close_ui', 'cleanup_session'):
        raise ValueError('Invalid action')
    if options['action'] == 'invoke' and options['procedure'] not in CATALOG['procedures']:
        raise ValueError('Select one original procedure from Schema')
    if options['procedure'] is not None and options['procedure'] not in CATALOG['procedures']:
        raise ValueError('Invalid procedure')
    if type(options['allow_reference_edits']) is not bool:
        raise ValueError('allow_reference_edits must be boolean')
    for key, limits in NUMBER_LIMITS.items():
        v = options[key]
        if type(v) not in (int, float) or not math.isfinite(v) or not limits[0] <= v <= limits[1]:
            raise ValueError('Invalid finite range: ' + key)
    for key in ('targets', 'attributes'):
        v = options[key]
        if v is not None and (not isinstance(v, list) or not 1 <= len(v) <= 100 or any(not isinstance(n, str) or not n or '\0' in n or len(n) > 2048 for n in v) or len(v) != len(set(v))):
            raise ValueError(key + ' must contain unique bounded strings')
    r = options['frame_range']
    if r is not None and (not isinstance(r, list) or len(r) != 2 or any(type(n) is not int or abs(n) > 1000000 for n in r) or r[1] < r[0] or r[1] - r[0] > 10000):
        raise ValueError('frame_range must be ordered bounded integer range')
    if options['cache_directory'] is not None and (not isinstance(options['cache_directory'], str) or '\0' in options['cache_directory']):
        raise ValueError('Invalid cache_directory')
    return options


class PhysicsToolsTool(BaseMayaTool):
    tool_id = 'physics_tools'
    tool_name = 'Physics Tools 动态与动画流程'
    category = 'animation'
    description = '完整109过程MEL套件：粒子、Jiggle、先进主轴、局部空间、代理、跟踪、时序、循环与噪声；真实Maya待验。'
    version = '1.8-candidate.1'
    parameters_schema = {'type': 'object', 'properties': {
        'action': {'type': 'string', 'enum': ['inspect', 'invoke', 'open_ui', 'close_ui', 'cleanup_session'], 'default': 'inspect'},
        'procedure': {'type': 'string', 'enum': CATALOG['procedures']},
        'targets': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 100, 'uniqueItems': True},
        'attributes': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 100, 'uniqueItems': True},
        'frame_range': {'type': 'array', 'items': {'type': 'integer', 'minimum': -1000000, 'maximum': 1000000}, 'minItems': 2, 'maxItems': 2},
        'allow_reference_edits': {'type': 'boolean', 'default': False, 'description': '明确允许原流程在引用控制器上写键/约束等引用编辑'},
        'cache_directory': {'type': 'string', 'description': '明确已有缓存父目录；只创建自有子目录，不删全场景缓存'},
        **{k: {'type': 'number', 'minimum': bounds[0], 'maximum': bounds[1], 'default': DEFAULTS[k]} for k, bounds in NUMBER_LIMITS.items()}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过', data=prepare(normalize(**kwargs)), dry_run=True)
        except Exception as error:
            return ToolResult.fail('Physics Tools 预检失败', errors=str(error), dry_run=True)

    def execute(self, **kwargs):
        try:
            from .runtime import execute, prepare
            options = normalize(**kwargs)
            return execute(options, prepare(options))
        except Exception as error:
            from . import runtime
            return ToolResult.fail('Physics Tools 执行失败；已写场景可一次Undo，外部缓存不归Undo', errors=str(error), data={'cache_files': runtime._LAST_FILES[:], 'external_undo': False})

    def show_ui(self, parent=None):
        return self.run(action='open_ui')
