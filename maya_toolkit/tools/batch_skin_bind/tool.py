import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs) - {'action', 'pairs', 'objects', 'proxy_type', 'skinning', 'allow_source_key_removal', 'start_frame', 'end_frame'}:
        raise ValueError('Unknown arguments')
    p = dict(action='proxies', proxy_type='joint', skinning=False, allow_source_key_removal=False)
    p.update(kwargs)
    if p['action'] not in ('proxies', 'bind') or p['proxy_type'] not in ('joint', 'locator', 'cube') or any(type(p[k]) is not bool for k in ('skinning', 'allow_source_key_removal')):
        raise ValueError('Invalid action/proxy/skinning options')
    if p['action'] == 'bind':
        if set(kwargs) - {'action', 'pairs'} or not isinstance(p.get('pairs'), list) or not 1 <= len(p['pairs']) <= 1000 or any(not isinstance(x, dict) or set(x) != {'joint', 'mesh'} or any(not isinstance(v, str) or not v for v in x.values()) for x in p['pairs']):
            raise ValueError('bind requires explicit bounded joint/mesh pairs only')
    elif 'pairs' in p:
        raise ValueError('pairs applies only to bind')
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(n, str) or not n for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('objects must be unique whole transform names')
    if p['skinning'] and (p['proxy_type'] != 'joint' or not p['allow_source_key_removal']):
        raise ValueError('Joint skinning requires explicit allow_source_key_removal=True for all source animation keys')
    if not p['skinning'] and (p['allow_source_key_removal'] or 'start_frame' in p or 'end_frame' in p):
        raise ValueError('Source removal and bake interval apply only to skinned joints')
    if ('start_frame' in p) != ('end_frame' in p):
        raise ValueError('Supply both bake endpoints')
    for key in ('start_frame', 'end_frame'):
        if key in p and (type(p[key]) not in (int, float) or not math.isfinite(p[key]) or abs(p[key]) > 1000000):
            raise ValueError('Bounded finite bake frame required')
    if 'start_frame' in p and not 0 <= p['end_frame'] - p['start_frame'] <= 10000:
        raise ValueError('Inclusive interval must be ordered and at most 10000 frames')
    return p


class BatchSkinBindTool(BaseMayaTool):
    tool_id = 'batch_skin_bind'
    tool_name = '批量绑骨头 / 生成代理'
    category = 'rigging'
    version = '1.0.0-candidate.1'
    description = 'Explicit joint/mesh batch binding and full joint/locator/cube constrained proxies. Optional joint bake/skin transfer uses actual created names and explicit removal of all source animation keys.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['proxies', 'bind'], 'default': 'proxies'}, 'pairs': {'type': 'array', 'minItems': 1, 'maxItems': 1000, 'items': {'type': 'object', 'properties': {'joint': {'type': 'string'}, 'mesh': {'type': 'string'}}, 'required': ['joint', 'mesh'], 'additionalProperties': False}}, 'objects': {'type': 'array', 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True, 'items': {'type': 'string'}, 'description': 'Whole explicit source transforms; defaults to selection without expanding children'}, 'proxy_type': {'type': 'string', 'enum': ['joint', 'locator', 'cube'], 'default': 'joint'}, 'skinning': {'type': 'boolean', 'default': False}, 'allow_source_key_removal': {'type': 'boolean', 'default': False, 'description': 'Skinned joint transfer removes ALL source transform animation, including outside bake range/custom channel keys'}, 'start_frame': {'type': 'number', 'description': 'Inclusive bake start, default playback minimum'}, 'end_frame': {'type': 'number', 'description': 'Inclusive bake end, default playback maximum'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only whole-batch proxy/binding preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Batch binding/proxy creation complete', data=execute(normalize(**kwargs)), warnings=['GUI and production animation acceptance not_run', 'Skinned proxies remove all source animation only when explicitly requested; partial failures require Undo'])

    def show_ui(self, parent=None):
        from maya import cmds
        if cmds.about(batch=True):
            raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui(self)
