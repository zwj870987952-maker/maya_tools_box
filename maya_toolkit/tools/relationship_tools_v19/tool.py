import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'mark', 'mark_foot', 'mark_animation', 'copy_world', 'one_step', 'more_step', 'align', 'delete_marks', 'export_pose', 'import_pose']


def normalize(**kwargs):
    if set(kwargs) - {'action', 'objects', 'translate', 'rotate', 'bake', 'step', 'world_coords', 'layer', 'advance', 'frame_range', 'file_path'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ACTIONS:
        raise ValueError('Choose known action')
    if p['action'] == 'inspect' and set(p) != {'action'}:
        raise ValueError('inspect takes no mutation arguments')
    for key, default in (('translate', True), ('rotate', True), ('bake', True), ('world_coords', False), ('layer', False), ('advance', False)):
        p.setdefault(key, default)
        if type(p[key]) is not bool:
            raise ValueError(key + ' must be boolean')
    if not p['translate'] and not p['rotate']:
        raise ValueError('Choose at least one TR channel group')
    p.setdefault('step', 1)
    if type(p['step']) is not int or not 1 <= p['step'] <= 1000:
        raise ValueError('step must be integer 1..1000')
    p.setdefault('frame_range', None)
    if p['frame_range'] is not None:
        value = p['frame_range']
        if not isinstance(value, list) or len(value) != 2 or any(type(n) is not int or abs(n) > 1000000 for n in value) or not 0 < value[1] - value[0] <= 10000:
            raise ValueError('Bounded [start inclusive, end exclusive] integer frame_range required')
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(n, str) or not n.strip() or len(n) > 4096 for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Unique ordered whole nodes required')
    if p['action'] in ('export_pose', 'import_pose'):
        if not isinstance(p.get('file_path'), str):
            raise ValueError('Explicit absolute JSON file required')
    elif 'file_path' in p:
        raise ValueError('file_path only for explicit pose import/export')
    return p


class RelationshipToolsTool(BaseMayaTool):
    tool_id = 'relationship_tools_v19'
    tool_name = 'Relationship Tools v19'
    category = 'rigging'
    version = '19-candidate.1'
    description = 'Complete mark/foot/animated locator, world pose, one/more step, align and animation-layer workflows with owned marks and explicit options. Real GUI acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True, 'description': 'Ordered whole objects; last is parent/align target; empty step selection uses only owned marks/copied UUIDs'}, 'translate': {'type': 'boolean', 'default': True}, 'rotate': {'type': 'boolean', 'default': True}, 'bake': {'type': 'boolean', 'default': True}, 'step': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 1}, 'world_coords': {'type': 'boolean', 'default': False}, 'layer': {'type': 'boolean', 'default': False}, 'advance': {'type': 'boolean', 'default': False, 'description': 'One/more step optionally advance exactly one frame after operation; GUI preserves original advance'}, 'frame_range': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2, 'description': '[start inclusive,end exclusive]; multi defaults playback range; align omitted is single-frame'}, 'file_path': {'type': 'string', 'description': 'Absolute JSON pose import or new exclusive export file'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only scope, ownership, channels and frames', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Relationship operation finished', data=execute(normalize(**kwargs)), warnings=['Real Maya GUI/complex production rigs not_run', 'In-memory copied pose and exported files are outside scene Undo'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui()
