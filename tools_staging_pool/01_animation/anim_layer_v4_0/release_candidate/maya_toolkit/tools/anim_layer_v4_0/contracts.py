"""Catalog-backed contracts, literal serialization and intact resource verification."""
import hashlib
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CATALOG = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
DEFAULTS = dict(action='inventory', edition='no_ui', procedure='', arguments={},
                force_reload=False, restore_runtime_state=True)
PROCEDURES = sorted({name for edition in CATALOG['editions'].values() for name in edition['procedures']})
HEADLESS_PROCEDURES = {
    'get_anim_time_range_from_anim_layer', 'get_anim_time_range_from_multiply_anim_layers',
    'get_min_max_from_selected', 'select_skip_no_exist', 'select_few_Layers', 'select_best_layer',
    'euler_filter_on_selected',
}


def resources():
    for relative, expected in CATALOG['resources'].items():
        path = PACKAGE / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Missing/changed original resource: ' + relative)


def mel_literal(value, kind):
    if kind.endswith('[]'):
        if not isinstance(value, list):
            raise ValueError(kind + ' requires a JSON array')
        return '{' + ','.join(mel_literal(item, kind[:-2]) for item in value) + '}'
    if kind == 'string':
        if not isinstance(value, str) or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
            raise ValueError('MEL string requires text without control characters')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        if type(value) is not int or not -2147483648 <= value <= 2147483647:
            raise ValueError('MEL int requires a signed 32-bit JSON integer')
        return str(value)
    if kind == 'float':
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('MEL float requires a finite number')
        return repr(float(value))
    raise ValueError('Unsupported MEL parameter type: ' + kind)


def normalize(kwargs):
    unknown = set(kwargs) - set(DEFAULTS)
    if unknown:
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(unknown)))
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('inventory', 'load', 'invoke', 'open_ui'):
        raise ValueError('Unknown action')
    if args['edition'] not in CATALOG['editions']:
        raise ValueError('edition must be no_ui or full')
    if not isinstance(args['procedure'], str) or not isinstance(args['arguments'], dict):
        raise ValueError('procedure must be a name and arguments must be an object')
    for name in ('force_reload', 'restore_runtime_state'):
        if type(args[name]) is not bool:
            raise ValueError(name + ' must be boolean')
    signatures = CATALOG['editions'][args['edition']]['procedures']
    signature = None
    command = None
    if args['procedure']:
        if args['procedure'] not in signatures:
            raise ValueError('Procedure not exported by selected edition')
        signature = signatures[args['procedure']]
    if args['action'] == 'invoke':
        if signature is None:
            raise ValueError('invoke requires a procedure')
        params = signature['parameters']
        if set(args['arguments']) != {p['name'] for p in params}:
            raise ValueError('arguments must exactly match: ' + ', '.join(p['name'] for p in params))
        encoded = [mel_literal(args['arguments'][p['name']], p['type']) for p in params]
        command = args['procedure'] + '(' + ','.join(encoded) + ');'
        for name in ('rotation_mod', 'mod', 'fidelity'):
            if name in args['arguments'] and args['arguments'][name] not in (0, 1):
                raise ValueError(name + ' must be 0 or 1')
        for name in ('tolerance', 'side_frames'):
            if name in args['arguments'] and args['arguments'][name] < 0:
                raise ValueError(name + ' cannot be negative')
        if 'timerange' in args['arguments']:
            times = args['arguments']['timerange']
            if len(times) != 2 or times[0] >= times[1]:
                raise ValueError('timerange requires exactly two increasing times')
        if args['procedure'] == 'get_anim_time_range_from_multiply_anim_layers' and not args['arguments']['anim_layers_name']:
            raise ValueError('At least one layer is required')
    elif args['arguments']:
        raise ValueError('arguments are only used by invoke')
    return args, signature, command
