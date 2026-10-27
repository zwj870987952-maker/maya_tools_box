import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'weights', 'disconnect', 'restore', 'reverse', 'rebuild', 'delete', 'remove_target', 'rest', 'axis', 'save_list', 'export_snapshot', 'import_snapshot']


def normalize(**kwargs):
    allowed = {'action', 'objects', 'constraints', 'selected_weights', 'all_weights', 'mode', 'value', 'keyframe', 'maintain_offset', 'list_name', 'items', 'path'}
    if set(kwargs)-allowed:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    for name in ('objects', 'constraints', 'selected_weights', 'all_weights'):
        if name in p and (not isinstance(p[name], list) or len(p[name]) > 1000 or any(not isinstance(x, str) or not x for x in p[name]) or len(set(p[name])) != len(p[name])):
            raise ValueError('Unique bounded '+name+' list required')
    for name, default in (('keyframe', True), ('maintain_offset', True)):
        p.setdefault(name, default)
        if type(p[name]) is not bool:
            raise ValueError(name+' must be boolean')
    p.setdefault('mode', 'custom')
    if p['mode'] not in ('custom', 'zero', 'one', 'selected_one'):
        raise ValueError('Unknown weight mode')
    p.setdefault('value', 1.)
    if type(p['value']) not in (int, float) or not math.isfinite(p['value']) or abs(p['value']) > 1000000:
        raise ValueError('Bounded finite weight required')
    if p['action'] == 'weights' and not p.get('selected_weights'):
        raise ValueError('Explicit selected_weights required')
    if p['action'] == 'save_list':
        import re
        if not isinstance(p.get('list_name'), str) or not re.fullmatch(r'[A-Za-z_]\w*', p['list_name'], re.ASCII):
            raise ValueError('New simple scene list name required')
        if not isinstance(p.get('items'), list) or not 1 <= len(p['items']) <= 1000:
            raise ValueError('Bounded nonempty item list required')
        for item in p['items']:
            if not isinstance(item, dict) or set(item)-{'text', 'color', 'constraint_node', 'weight_attrs'} or not isinstance(item.get('text'), str) or len(item['text']) > 4096 or not re.fullmatch(r'#[0-9A-Fa-f]{6}', item.get('color', '#e0e0e0')) or not isinstance(item.get('constraint_node', ''), str) or not isinstance(item.get('weight_attrs', []), list) or any(not isinstance(x, str) for x in item.get('weight_attrs', [])):
                raise ValueError('Plain colored list item data required')
    if p['action'] in ('export_snapshot', 'import_snapshot') and (not isinstance(p.get('path'), str) or not p['path']):
        raise ValueError('Explicit snapshot JSON path required')
    return p


class ConstraintManagerTool(BaseMayaTool):
    tool_id = 'constraint_manager_v6'
    tool_name = '约束管理 v6'
    category = 'rigging'
    version = '6.0.0-candidate.1'
    description = '完整权重列表、颜色、选择、断开恢复、反向、重建及辅助界面；API 检查真实约束目标/别名，保存动画与偏移，真实 Maya GUI 待验收。'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'maxItems': 1000}, 'constraints': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'maxItems': 1000}, 'selected_weights': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'all_weights': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'mode': {'type': 'string', 'enum': ['custom', 'zero', 'one', 'selected_one']}, 'value': {'type': 'number'}, 'keyframe': {'type': 'boolean', 'default': True}, 'maintain_offset': {'type': 'boolean', 'default': True}, 'list_name': {'type': 'string'}, 'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'text': {'type': 'string'}, 'color': {'type': 'string'}, 'constraint_node': {'type': 'string'}, 'weight_attrs': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['text'], 'additionalProperties': False}}, 'path': {'type': 'string'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .engine import preflight
            return ToolResult.ok(message='Read-only constraint/target/edge preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .engine import execute
        return ToolResult.ok(message='Constraint operation completed', data=execute(normalize(**kwargs)), warnings=['GUI/production acceptance not_run', 'Python session snapshots and external files are outside scene Undo'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(parent)
