import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def catalog():
    return json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8'))


def safe_json(value, depth=0):
    if depth > 8:
        raise ValueError('Nested arguments too deep')
    if value is None or type(value) is bool:
        return
    if type(value) in (int, float):
        if not math.isfinite(value) or abs(value) > 1000000:
            raise ValueError('Bounded finite numeric arguments required')
    elif isinstance(value, str):
        if len(value) > 4096 or any(c in value for c in ('\x00', '\r', '\n', '`', ';', '"', '\\')):
            raise ValueError('Plain string arguments required')
    elif isinstance(value, list):
        if len(value) > 1000:
            raise ValueError('Argument array too large')
        for element in value:
            safe_json(element, depth + 1)
    else:
        raise ValueError('Arguments must be ordinary JSON scalars/lists')


def normalize(**kwargs):
    if set(kwargs) - {'action', 'module', 'function', 'arguments', 'objects', 'allow_native_scope', 'output_path', 'input_ui'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ('inspect', 'call', 'script'):
        raise ValueError('Expected inspect, call or script')
    if p['action'] == 'inspect':
        if set(p) != {'action'}:
            raise ValueError('inspect takes no call arguments')
        return p
    c = catalog()['modules']
    if not isinstance(p.get('module'), str) or p['module'] not in c or p['module'] == 'RdMToolsV2.run_RdMTools':
        raise ValueError('Known original module required; installer cannot be called')
    p.setdefault('allow_native_scope', False)
    if type(p['allow_native_scope']) is not bool:
        raise ValueError('allow_native_scope must be boolean')
    p.setdefault('arguments', {})
    if not isinstance(p['arguments'], dict) or len(p['arguments']) > 50:
        raise ValueError('Bounded named argument map required')
    if p['action'] == 'script':
        if p['arguments'] or 'function' in p:
            raise ValueError('Script entry takes no function arguments')
    else:
        definitions = {row['name']: row for row in c[p['module']]['functions']}
        if not isinstance(p.get('function'), str) or p['function'] not in definitions:
            raise ValueError('Choose exact catalog function')
        signature = definitions[p['function']]
        if set(p['arguments']) - set(signature['parameters']) or set(signature['parameters'][:signature['required']]) - set(p['arguments']):
            raise ValueError('Named parameters must match original signature')
        for value in p['arguments'].values():
            safe_json(value)
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(n, str) or not n.strip() or len(n) > 4096 for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Unique ordered whole object inputs required')
    is_export = p['module'] in ('RdMToolsV2.RiggingTools.Curves.CurveToJson', 'RdMToolsV2.RiggingTools.QT.UItoPY')
    if is_export and (p['action'] != 'script' or not isinstance(p.get('output_path'), str)):
        raise ValueError('Original exports require script action and explicit output_path')
    if not is_export and ('output_path' in p or 'input_ui' in p):
        raise ValueError('File arguments only supported by original export scripts')
    return p


class RdmToolsTool(BaseMayaTool):
    tool_id = 'rdm_tools_v2'
    tool_name = 'RdM Tools v2'
    category = 'rigging'
    version = '2.0-candidate.1'
    description = 'Complete original AutoRig, facial, skin, curve, picker and rigging toolbox with Python3/Qt compatibility and explicit legacy actions. Full resources retained; PyMel and real GUI acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'call', 'script'], 'default': 'inspect'}, 'module': {'type': 'string', 'enum': sorted(n for n in catalog()['modules'] if n != 'RdMToolsV2.run_RdMTools')}, 'function': {'type': 'string', 'description': 'Exact original function name from inspect'}, 'arguments': {'type': 'object', 'description': 'Named original parameters with JSON scalar/list values'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True}, 'allow_native_scope': {'type': 'boolean', 'default': False, 'description': 'Acknowledge broad original naming/hierarchy/whole-scene effects on backup scene'}, 'output_path': {'type': 'string', 'description': 'Absolute new .json/.py file only for original export script'}, 'input_ui': {'type': 'string', 'description': 'Existing absolute .ui for optional UItoPY'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only original files and explicit action preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Full original native action returned; verify actual outputs', data=execute(normalize(**kwargs)), warnings=['Real Maya GUI/production/PyMel workflows not_run', 'Original hardcoded rig names, broader hierarchy/selection and silent catches retained'])

    def show_ui(self, parent=None):
        from .runtime import show_ui
        return show_ui()
