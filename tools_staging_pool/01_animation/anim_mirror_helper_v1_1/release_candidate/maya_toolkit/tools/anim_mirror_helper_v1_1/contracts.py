"""Read-only catalog and JSON-to-MEL contracts, including vector arrays."""
import hashlib
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CATALOG = json.loads((PACKAGE/'catalog.json').read_text(encoding='utf-8'))
DEFAULTS = dict(action='inventory', procedure='', arguments={}, force_reload=False)
ALIASES = {
    'create_system': 'MIRR_b7cfd62c53832d19b9248a27c80a6f44',
    'add_items': 'MIRR_9147e5087e953411782b272b89b1ddb6',
    'auto_connect': 'MIRR_0d9dbbe39a5758068cdf30cf9c7cb924',
    'attach_pairs': 'MIRR_18a1bcd5e135a60ba68f5eb3c465884e',
    'select_pairs': 'MIRR_af16024bff0824c73ab6c4082569d9ed',
    'connect_attributes': 'MIRR_ebdde21f7478f2e87c8125a749c52f7a',
    'copy_rotation': 'MIRR_66c56c7553b8c48c1c480f58c19084ce',
    'paste_rotation': 'MIRR_f0a28d7c6e1c7cd0114c5b790b5810db',
    'calculate': 'MT_calcul_single',
    'delete_system': 'MIRR_4e55dd5ee0a5a72502e97cf0ed202fa7',
}
HEADLESS = {'MIRR_e3bea614176fbceebe7c7aae67e953b0', 'MIRR_f71c299bf7b53f7243b078a9990e581c'}
ACTIONS = ['inventory', 'load', 'invoke', 'open_ui', 'bake_selected', 'mirror_rotation', 'zero_rotation'] + list(ALIASES)


def resources():
    for relative, expected in CATALOG['resources'].items():
        p = PACKAGE/relative
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError('Missing/changed original resource: '+relative)


def mel_literal(value, kind):
    if kind.endswith('[]'):
        if not isinstance(value, list):
            raise ValueError(kind+' requires a JSON array')
        return '{'+','.join(mel_literal(v, kind[:-2]) for v in value)+'}'
    if kind == 'string':
        if not isinstance(value, str) or any(ord(c)<32 or ord(c)==127 for c in value):
            raise ValueError('string requires text without control characters')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        if type(value) is not int or not -2147483648 <= value <= 2147483647:
            raise ValueError('int requires a signed 32-bit JSON integer')
        return str(value)
    if kind == 'float':
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('float requires a finite number')
        return repr(float(value))
    if kind == 'vector':
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('vector requires three finite coordinates')
        return '<<'+','.join(mel_literal(v, 'float') for v in value)+'>>'
    raise ValueError('Unsupported MEL type: '+kind)


def normalize(kwargs):
    if set(kwargs)-set(DEFAULTS):
        raise ValueError('Unknown top-level parameters')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or type(args['force_reload']) is not bool:
        raise ValueError('Unknown action or invalid force_reload')
    if not isinstance(args['procedure'], str) or not isinstance(args['arguments'], dict):
        raise ValueError('procedure requires text; arguments requires object')
    action = args['action']
    name = ALIASES.get(action, args['procedure'] if action=='invoke' else '')
    if action != 'invoke' and args['procedure']:
        raise ValueError('procedure is only used by invoke')
    signature = CATALOG['procedures'].get(name)
    if action=='invoke' and not signature:
        raise ValueError('invoke requires an exported procedure')
    command = None
    if signature:
        params = signature['parameters']
        if set(args['arguments']) != {p['name'] for p in params}:
            raise ValueError('arguments must exactly match: '+', '.join(p['name'] for p in params))
        values = args['arguments']
        command = name+'('+','.join(mel_literal(values[p['name']], p['type']) for p in params)+');'
        if name == ALIASES['create_system']:
            if values['mirror_axis'].lower() not in ('x','y','z') or values['cycled'] not in (0,1):
                raise ValueError('mirror_axis must be x/y/z; cycled must be 0/1')
        if name in (ALIASES['auto_connect'],ALIASES['select_pairs']):
            if not values['side_from'] or not values['side_to'] or values['side_from']==values['side_to']:
                raise ValueError('Side names must be nonempty and different')
        if name == ALIASES['auto_connect']:
            if values['rig_type'] not in ('Symmetric','SymmetricRotate','AdvSkel'):
                raise ValueError('rig_type must be Symmetric/SymmetricRotate/AdvSkel')
        if name == ALIASES['attach_pairs'] and (values['type'] not in ('parent','orient','point') or values['offset'] != 0):
            raise ValueError('type must be parent/orient/point; original across helper only supports offset=0')
        if name == 'MIRR_e3bea614176fbceebe7c7aae67e953b0' and not values['coords']:
            raise ValueError('coords cannot be empty (original divides by count)')
    elif args['arguments']:
        raise ValueError('This action takes no arguments')
    if action == 'open_ui':
        name, command = 'Mirror_tool_menue', 'Mirror_tool_menue();'
    elif action == 'bake_selected':
        command = ('MIRR_692e2fda85cadfdf0f28e93323f58c08();'
                   'MIRR_de88efca2929f0080ae1d45ff5db42d4();'
                   'MIRR_09f1edc0a69a4931b08e1bcc40e94a55();'
                   'MIRR_f4b1a2b52ab1771321003f86cde63160();')
    elif action in ('mirror_rotation','zero_rotation'):
        command = 'rotate -os {} 0 0;'.format(180 if action=='mirror_rotation' else 0)
    return args, name, signature, command
