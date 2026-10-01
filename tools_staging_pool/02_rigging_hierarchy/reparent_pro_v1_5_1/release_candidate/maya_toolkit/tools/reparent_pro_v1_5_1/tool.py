import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'reparent', 'manual_start', 'manual_go', 'manual_cancel', 'relative', 'freeze', 'ik', 'bake_delete', 'locator_size']


def normalize(**kwargs):
    if set(kwargs) - {'action', 'objects', 'frame_range', 'pin', 'local', 'delete_redundant', 'bake_on_layer', 'allow_clear_animation'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    if p['action'] == 'inspect' and set(p) != {'action'}:
        raise ValueError('inspect accepts no mutation arguments')
    for key, default in (('pin', False), ('local', False), ('delete_redundant', True), ('bake_on_layer', False), ('allow_clear_animation', False)):
        p.setdefault(key, default)
        if type(p[key]) is not bool:
            raise ValueError(key + ' must be boolean')
    if p['pin'] and p['action'] not in ('reparent', 'manual_go'):
        raise ValueError('Pin supports default and manual Go only')
    if p['local'] and p['action'] != 'ik':
        raise ValueError('Local applies to IK only')
    if p['bake_on_layer'] and p['action'] != 'bake_delete':
        raise ValueError('Original layer menu is inert; candidate layer applies to final bake only')
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(n, str) or not n.strip() or len(n) > 1024 for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Unique ordered whole objects required')
    if p['action'] in ('manual_go', 'manual_cancel', 'bake_delete') and 'objects' in p:
        raise ValueError('This action uses validated owned session membership')
    p.setdefault('frame_range', None)
    if p['frame_range'] is not None:
        v = p['frame_range']
        if not isinstance(v, list) or len(v) != 2 or any(type(n) is not int or abs(n) > 1000000 for n in v) or not 0 <= v[1] - v[0] <= 10000:
            raise ValueError('Integer inclusive [start,end] range, at most 10001 frames')
    return p


class ReParentProTool(BaseMayaTool):
    tool_id = 'reparent_pro_v1_5_1'
    tool_name = 'ReParent Pro 1.5.1'
    category = 'rigging'
    version = '1.5.1-candidate.1'
    description = 'Complete original locator/relative/manual pivot/freeze/FK to IK workflows, scoped ownership and explicit clear-animation protection; Maya GUI acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True, 'description': 'Ordered controls; relative last is reference, freeze first is main, IK exactly three'}, 'frame_range': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2, 'description': 'Inclusive bounded integer range; defaults to current playback bounds'}, 'pin': {'type': 'boolean', 'default': False}, 'local': {'type': 'boolean', 'default': False}, 'delete_redundant': {'type': 'boolean', 'default': True}, 'bake_on_layer': {'type': 'boolean', 'default': False, 'description': 'Final bake_delete override layer only'}, 'allow_clear_animation': {'type': 'boolean', 'default': False, 'description': 'Acknowledge original modes clear all six TR keys, including keys outside bake range; use backup scene'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only scope/ownership/animation plan', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='ReParent operation finished', data=execute(normalize(**kwargs)), warnings=['Real Maya GUI/production rigs not_run', 'Original TR key clearing includes outside range; MEL/UI state not scene Undo'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui()
