import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def catalog():
    return json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8'))


def literal(value, kind):
    if kind.endswith('[]'):
        if not isinstance(value, list) or len(value) > 1000:
            raise ValueError('Bounded argument array required')
        return '{' + ','.join(literal(v, kind[:-2]) for v in value) + '}'
    if kind == 'string':
        if not isinstance(value, str) or len(value) > 4096 or any(c in value for c in ('\x00', '\n', '\r', '`', ';', '"', '\\')):
            raise ValueError('Plain MEL string argument required; commands/escapes rejected')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        if type(value) is not int or abs(value) > 1000000:
            raise ValueError('Bounded integer required')
        return str(value)
    if kind == 'float':
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1000000:
            raise ValueError('Bounded finite number required')
        return str(float(value))
    raise ValueError('Unsupported public parameter type: ' + kind)


def normalize(**kwargs):
    allowed = {'action', 'procedure', 'arguments', 'objects', 'rotate_order'}
    if set(kwargs) - allowed:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ('inspect', 'call'):
        raise ValueError('Expected inspect or call')
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(x, str) or not x.strip() for x in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('objects must contain unique whole node names in order')
    for key, allowed_values in (('rotate_order', range(6)),):
        if key in p and (type(p[key]) is not int or p[key] not in allowed_values):
            raise ValueError('Invalid ' + key)
    if p['action'] == 'inspect':
        if set(p) - {'action'}:
            raise ValueError('inspect takes no scene/call arguments')
        return p
    public = catalog()['public']
    if not isinstance(p.get('procedure'), str) or p['procedure'] not in public:
        raise ValueError('Choose a declared public procedure; no arbitrary MEL/internal entry')
    p.setdefault('arguments', [])
    definition = public[p['procedure']]
    if not isinstance(p['arguments'], list) or len(p['arguments']) != len(definition['parameters']):
        raise ValueError('Argument count must match public declaration')
    p['command'] = p['procedure'] + '(' + ','.join(literal(v, d['type']) for v, d in zip(p['arguments'], definition['parameters'])) + ');'
    for v, d in zip(p['arguments'], definition['parameters']):
        if d['name'] in ('locksize', 'loc_size', 'size_j', 'size_lock', 'scale_on', 'period') and (not v > 0):
            raise ValueError('Positive size/scale/period required')
    return p


class BaseOverRigTool(BaseMayaTool):
    tool_id = 'base_overrig_v9_0'
    tool_name = 'Base OverRig 9.0'
    category = 'rigging'
    version = '9.0-candidate.1'
    description = 'Complete original OverRig suite; separate typed public-procedure wrapper with read-only resource/selection preflight. Original MEL/resources/license/UI unchanged; interactive production acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'call'], 'default': 'inspect'}, 'procedure': {'type': 'string', 'enum': sorted(catalog()['public'])}, 'arguments': {'type': 'array', 'description': 'Positional typed values in the declared public signature; inspect returns all signatures'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True, 'description': 'Ordered whole nodes; defaults to current ordered selection'}, 'rotate_order': {'type': 'integer', 'minimum': 0, 'maximum': 5, 'default': 0}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only vendor/resources and declared call preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Original OverRig procedure returned; inspect output and native warnings', data=execute(normalize(**kwargs)), warnings=['GUI and production workflows not_run', 'Original callbacks, optionVars, plugins and some Undo-disabled motion trails have effects outside ordinary Undo', 'Native silent catch behavior retained unchanged'])

    def show_ui(self, parent=None):
        from .runtime import show_ui
        return show_ui()
