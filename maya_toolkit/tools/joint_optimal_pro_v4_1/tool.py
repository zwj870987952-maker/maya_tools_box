"""Typed independent adapter; licensed algorithms remain byte-for-byte intact."""
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
            raise ValueError('Bounded typed array required')
        return '{' + ','.join(literal(v, kind[:-2]) for v in value) + '}'
    if kind == 'string':
        if not isinstance(value, str) or len(value) > 4096 or any(c in value for c in ('\x00', '\n', '\r', '`', ';', '"', '\\')):
            raise ValueError('Plain string required; MEL commands/escapes rejected')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        if type(value) is not int or abs(value) > 1000000:
            raise ValueError('Bounded integer required')
        return str(value)
    if kind == 'float':
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1000000:
            raise ValueError('Bounded finite number required')
        return str(float(value))
    if kind == 'vector':
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('Vector requires three finite coordinates')
        return '<<' + ','.join(literal(v, 'float') for v in value) + '>>'
    if kind == 'matrix':
        if not isinstance(value, list) or len(value) != 4 or any(not isinstance(row, list) or len(row) != 4 for row in value):
            raise ValueError('Matrix requires four rows of four finite values')
        return '<<' + ';'.join(','.join(literal(v, 'float') for v in row) for row in value) + '>>'
    raise ValueError('Unsupported type: ' + kind)


def normalize(**kwargs):
    if set(kwargs) - {'action', 'procedure', 'arguments', 'objects', 'allow_native_scope'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ('inspect', 'call'):
        raise ValueError('Choose inspect or call')
    if p['action'] == 'inspect':
        if set(p) != {'action'}:
            raise ValueError('inspect takes no call arguments')
        return p
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(n, str) or not n.strip() or len(n) > 4096 for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Unique ordered whole objects required')
    p.setdefault('allow_native_scope', False)
    if type(p['allow_native_scope']) is not bool:
        raise ValueError('allow_native_scope must be boolean')
    public = catalog()['public']
    if not isinstance(p.get('procedure'), str) or p['procedure'] not in public:
        raise ValueError('Choose catalog procedure; installer/system find are not callable')
    p.setdefault('arguments', [])
    signature = public[p['procedure']]['parameters']
    if not isinstance(p['arguments'], list) or len(p['arguments']) != len(signature):
        raise ValueError('Argument count must match original signature')
    p['command'] = p['procedure'] + '(' + ','.join(literal(v, s['type']) for v, s in zip(p['arguments'], signature)) + ');'
    for value, definition in zip(p['arguments'], signature):
        if definition['name'] in ('rad', 'local_scale', 'scale_on', 'subScale', 'lenght_coeff') and not value > 0:
            raise ValueError('Positive display size/coefficient required')
        if definition['name'] == 'color' and (type(value) is not int or value not in range(32)):
            raise ValueError('Indexed color must be 0..31')
        if definition['name'] == 'limit' and not 1 <= value <= 1000:
            raise ValueError('Joint creation limit must be 1..1000')
        if definition['name'] in ('on', 'on_off', 'show', 'lock', 'vis') and value not in (0, 1):
            raise ValueError('Native boolean flag must be 0 or 1')
        if definition['name'] == 'poisk' and not value:
            raise ValueError('Empty native delimiter divides by zero')
    return p


class JointOptimalProTool(BaseMayaTool):
    tool_id = 'joint_optimal_pro_v4_1'
    tool_name = 'Joint Optimal Pro 4.1'
    category = 'rigging'
    version = '4.1-candidate.1'
    description = 'Complete unmodified skeleton creation/parenting/orientation/alignment/selection/color/naming suite. Independent typed API and full native GUI; production acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'call'], 'default': 'inspect'}, 'procedure': {'type': 'string', 'enum': sorted(catalog()['public'])}, 'arguments': {'type': 'array', 'maxItems': 10, 'description': 'Positional values matching inspect signature; vector=[x,y,z], matrix=four rows'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True, 'description': 'Ordered whole nodes, defaults to current selection; component workflows use complete native UI'}, 'allow_native_scope': {'type': 'boolean', 'default': False, 'description': 'Acknowledge original broader hierarchy/global/UI scope for native workflows beyond the isolated verified subset'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only resources/signature/scene preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Original procedure returned; inspect native output and warnings', data=execute(normalize(**kwargs)), warnings=['Real Maya GUI acceptance not_run', 'Original catchQuiet, callbacks, shared globals and preference effects retained; return does not prove complete success'])

    def show_ui(self, parent=None):
        from .runtime import show_ui
        return show_ui()
