"""Checked schema; all Maya/NumPy imports stay behind validate/execute."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'align', 'detect', 'load_map', 'save_map', 'overlaps', 'merge', 'split', 'open_ui', 'close_ui']
DEFAULTS = dict(action='inspect', source_root=None, target_root=None, joint_map=None,
                meshes=None, decimals=3, output_path=None, map_path=None, overwrite=False)


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('Unknown parameters')
    o = dict(DEFAULTS)
    o.update(kwargs)
    if o['action'] not in ACTIONS or type(o['overwrite']) is not bool:
        raise ValueError('Invalid action/overwrite')
    if type(o['decimals']) is not int or not 0 <= o['decimals'] <= 8:
        raise ValueError('decimals requires integer 0..8')
    for k in ('source_root', 'target_root', 'output_path', 'map_path'):
        if o[k] is not None and (not isinstance(o[k], str) or not o[k] or len(o[k]) > 4096 or '\0' in o[k]):
            raise ValueError('Invalid ' + k)
    if o['joint_map'] is not None:
        validate_map(o['joint_map'])
    if o['meshes'] is not None and (not isinstance(o['meshes'], list) or not 1 <= len(o['meshes']) <= 2 or any(not isinstance(v, str) or not v or '\0' in v or len(v) > 2048 for v in o['meshes']) or len(set(o['meshes'])) != len(o['meshes'])):
        raise ValueError('Choose one or two distinct mesh transforms')
    return o


def validate_map(data):
    if not isinstance(data, dict) or not 1 <= len(data) <= 5000 or any(not isinstance(k, str) or not isinstance(v, str) or not k or not v or any(c in k + v for c in '\0|:') or len(k) > 256 or len(v) > 256 for k, v in data.items()):
        raise ValueError('Mapping requires nonempty bounded joint leaf names without namespace/path')
    return dict(data)


class PoseMatcherTool(BaseMayaTool):
    tool_id = 'pose_matcher'
    tool_name = 'Pose Matcher 骨架对齐与网格往返'
    category = 'animation'
    version = '1.0-candidate.1'
    description = '完整原骨架方向对齐/映射UI及NumPy焊接、OBJ+JSON、网格拆分；真实Maya待验。'
    parameters_schema = {'type': 'object', 'properties': {
        'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'},
        'source_root': {'type': 'string'}, 'target_root': {'type': 'string'},
        'joint_map': {'type': 'object', 'additionalProperties': {'type': 'string'}, 'maxProperties': 5000},
        'meshes': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 2, 'uniqueItems': True},
        'decimals': {'type': 'integer', 'minimum': 0, 'maximum': 8, 'default': 3},
        'output_path': {'type': 'string'}, 'map_path': {'type': 'string'},
        'overwrite': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过', data=prepare(normalize(**kwargs)), dry_run=True)
        except Exception as e:
            return ToolResult.fail('Pose Matcher 预检失败', errors=str(e), dry_run=True)

    def execute(self, **kwargs):
        from . import runtime
        try:
            o = normalize(**kwargs)
            return runtime.execute(o, runtime.prepare(o))
        except Exception as e:
            return ToolResult.fail('Pose Matcher 执行失败；场景一次Undo，文件不归Undo', errors=str(e), data={'written_files': runtime.WRITTEN[:], 'external_undo': False})

    def show_ui(self, parent=None):
        return self.run(action='open_ui')
