"""Typed interface to the complete retained BB suite, with explicit native entry points."""
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
            raise ValueError('Bounded typed argument array required')
        return '{'+','.join(literal(v, kind[:-2]) for v in value)+'}'
    if kind == 'string':
        if not isinstance(value, str) or len(value) > 4096 or any(c in value for c in ('\x00', '\n', '\r', '`', ';', '"', '\\')):
            raise ValueError('Plain MEL string required; command/escape text rejected')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        if type(value) is not int or abs(value) > 1000000:
            raise ValueError('Bounded integer required')
        return str(value)
    if kind == 'float':
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1000000:
            raise ValueError('Finite bounded number required')
        return str(float(value))
    raise ValueError('Unsupported parameter kind '+kind)


def normalize(**kwargs):
    if set(kwargs)-{'action', 'procedure', 'arguments', 'objects', 'allow_scene_scope'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ('inspect', 'call'):
        raise ValueError('Expected inspect/call')
    if p['action'] == 'inspect':
        if set(p)-{'action'}:
            raise ValueError('inspect takes no call or scene arguments')
        return p
    c = catalog()['procedures']
    name = p.get('procedure')
    if not isinstance(name, str) or name not in c or not c[name]['global_scope']:
        raise ValueError('Choose an original declared global procedure from inspect')
    p.setdefault('arguments', [])
    params = c[name]['parameters']
    if not isinstance(p['arguments'], list) or len(p['arguments']) != len(params):
        raise ValueError('Arguments must match original positional signature')
    p['command'] = c[name]['native_name']+'('+','.join(literal(v, d['type']) for v, d in zip(p['arguments'], params))+');'
    p.setdefault('objects', [])
    if not isinstance(p['objects'], list) or len(p['objects']) > 1000 or any(not isinstance(x, str) or not x for x in p['objects']) or len(set(p['objects'])) != len(p['objects']):
        raise ValueError('Unique ordered whole-node objects required')
    if type(p.get('allow_scene_scope', False)) is not bool:
        raise ValueError('allow_scene_scope must be boolean')
    if name == 'bb_CtrlTool_createShape':
        if p['arguments'][0] not in SHAPES or not valid_name(p['arguments'][1]):
            raise ValueError('Original shape enum and unused simple node name required')
    if name == 'bb_CtrlTool_changeColorApply' and not 0 <= p['arguments'][1] <= 31:
        raise ValueError('Maya overrideColor must be 0..31')
    if name == 'wpRename_js_replaceHash' and p['arguments'][1] < 0:
        raise ValueError('Nonnegative name index required')
    if name == 'bb_attr_addAttr':
        info = p['arguments'][1]
        if len(info) != 6 or not valid_name(info[0]) or info[1] not in ('Int', 'Float', 'Boolean', 'Enum') or info[4] not in ('0', '1') or info[5] not in ('0', '1'):
            raise ValueError('attrInfo: name,type,minOrEnum,max,minEnabled,maxEnabled')
        if info[1] in ('Int', 'Float'):
            values = [float(info[2]), float(info[3])]
            if any(not math.isfinite(x) or abs(x) > 1000000 for x in values) or info[4] == info[5] == '1' and values[0] > values[1]:
                raise ValueError('Bounded ordered attribute limits required')
            if info[1] == 'Int' and any(x != int(x) for x in values):
                raise ValueError('Integer attribute limits required')
        if info[1] == 'Enum' and (not info[2] or any(not valid_name(x) for x in info[2].rstrip(',').split(','))):
            raise ValueError('Comma-separated plain enum labels required')
    return p


def valid_name(value):
    import re
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z_]\w*', value, re.ASCII) is not None


SHAPES = ['CtrlShape_'+s for s in ('sphere', 'cube', 'pyramid', 'rhombus', 'cylinder', 'circle', 'square', 'triangle', 'arrowhead1', 'arrowhead2', 'arrowCircle1', 'arrowCircle2', 'cross', 'arc1', 'arc2', 'loc')]


class BBToolsTool(BaseMayaTool):
    tool_id = 'bb_tools'
    tool_name = 'BB Tools 完整套件'
    category = 'rigging'
    version = '1.0.0-candidate.1'
    description = '完整 BB MEL 套件与素材；显式原界面、类型化过程调用及只读清单。候选版保护文件并隔离全局过程名，真实 Maya 验收待完成。'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'call'], 'default': 'inspect'}, 'procedure': {'type': 'string', 'enum': sorted(n for n, d in catalog()['procedures'].items() if d['global_scope'])}, 'arguments': {'type': 'array', 'description': 'Original positional signature; inspect lists typed parameters and direct effects'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'maxItems': 1000}, 'allow_scene_scope': {'type': 'boolean', 'default': False, 'description': 'Required for native interactive procedures whose original scope may include connected nodes or the whole scene'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only BB resources/signature/scene preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='BB original procedure returned; review native output', data=execute(normalize(**kwargs)), warnings=['GUI/production workflows not_run', 'Native callbacks/UI/settings and external files cannot be reverted with scene Undo; partial failures may require Undo and file recovery'])

    def show_ui(self, parent=None):
        from .runtime import show_ui
        return show_ui()
