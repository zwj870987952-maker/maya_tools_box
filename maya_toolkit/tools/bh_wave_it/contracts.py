import math
import re

ACTIONS = ['inventory', 'open_ui', 'wave', 'basic_s', 'inverse_s', 'basic_c', 'inverse_c', 'invert', 'base_offset']
DEFAULTS = {'action': 'inventory', 'objects': [], 'rotate_axes': ['X'], 'translate_axes': [], 'custom_attributes': [], 'amplitude': .15, 'frequency': 1.0, 'phase': 0.0, 'base_offset': 0.0}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('未知action')
    for key in ('objects', 'rotate_axes', 'translate_axes', 'custom_attributes'):
        value = args[key]
        if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value) or len(set(value)) != len(value):
            raise ValueError(key + ' 必须是不重复字符串数组')
    if any(any(char in name for char in '.*?[]\r\n') for name in args['objects']):
        raise ValueError('objects需要明确transform名')
    if any(axis not in 'XYZ' or len(axis) != 1 for key in ('rotate_axes', 'translate_axes') for axis in args[key]):
        raise ValueError('axis需要X/Y/Z')
    if any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', attr) for attr in args['custom_attributes']):
        raise ValueError('custom_attributes需要标量属性名')
    for key, limit in [('amplitude', (0, 1)), ('frequency', (-1, 1)), ('phase', (-10, 10)), ('base_offset', (-180, 180))]:
        value = args[key]
        if type(value) not in (float, int) or not math.isfinite(value) or not limit[0] <= value <= limit[1]:
            raise ValueError(key + '超出原UI范围')
    if args['action'] in ('basic_s', 'inverse_s', 'basic_c', 'inverse_c'):
        args['frequency'] = {'basic_s': 1, 'inverse_s': -1, 'basic_c': .5, 'inverse_c': -.5}[args['action']]
        args['phase'] = 0.0
    elif args['action'] == 'invert':
        args['frequency'] *= -1
    return args


def values(args, count):
    return [math.degrees(math.sin(((i + 1 + args['phase']) * (6.28 / count)) * args['frequency']) * args['amplitude']) - (args['base_offset'] if i == 0 else 0) for i in range(count)]


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'},
    'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'default': []},
    'rotate_axes': {'type': 'array', 'items': {'type': 'string', 'enum': ['X', 'Y', 'Z']}, 'uniqueItems': True, 'default': ['X']},
    'translate_axes': {'type': 'array', 'items': {'type': 'string', 'enum': ['X', 'Y', 'Z']}, 'uniqueItems': True, 'default': []},
    'custom_attributes': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'default': []},
    **{key: {'type': 'number', 'minimum': bounds[0], 'maximum': bounds[1], 'default': DEFAULTS[key]} for key, bounds in [('amplitude', (0, 1)), ('frequency', (-1, 1)), ('phase', (-10, 10)), ('base_offset', (-180, 180))]}
}, 'additionalProperties': False}
