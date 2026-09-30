import math

CHANNELS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
ACTIONS = ['inventory', 'open_ui', 'apply', 'cache', 'restore', 'clear', 'save_preset', 'load_preset']
DEFAULTS = {'action': 'inventory', 'object': '', 'start': None, 'end': None, 'step': 1, 'amounts': {c: 5.0 for c in CHANNELS}, 'falloff_samples': [], 'seed': None, 'overwrite': False, 'use_cache': False, 'file_path': '', 'overwrite_file': False, 'preset': {}}


def finite(value):
    return type(value) in (float, int) and math.isfinite(value)


def preset_data(value):
    required = ['Frame', 'TX', 'TY', 'TZ', 'RX', 'RY', 'RZ', 'Points']
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError('preset需要原Frame/TX..RZ/Points完整字段')
    if type(value['Frame']) is not int or not 1 <= value['Frame'] <= 99:
        raise ValueError('preset Frame需要1..99')
    if any(not finite(value[key]) or not 0 <= value[key] <= 99.99 for key in required[1:7]):
        raise ValueError('preset amount需要0..99.99')
    if not isinstance(value['Points'], str):
        raise ValueError('Points需要原Maya渐变字符串')
    numbers = [float(item) for item in value['Points'].split(',')]
    if len(numbers) < 6 or len(numbers) % 3 or any(not math.isfinite(n) for n in numbers):
        raise ValueError('Points需要有限value,position,interpolation三元组')
    if any(not 0 <= numbers[i] <= 1 or numbers[i + 1] not in (0, 1, 2, 3) for i in range(1, len(numbers), 3)):
        raise ValueError('Points position/interpolation越界')
    return dict(value)


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('未知action')
    if not isinstance(args['object'], str) or any(c in args['object'] for c in '.*?[]\r\n'):
        raise ValueError('object需要明确transform名')
    if not isinstance(args['amounts'], dict) or set(args['amounts']) != set(CHANNELS) or any(not finite(v) or not 0 <= v <= 99.99 for v in args['amounts'].values()):
        raise ValueError('amounts需要六TR各0..99.99')
    if type(args['step']) is not int or not 1 <= args['step'] <= 99:
        raise ValueError('step需要1..99整数')
    if any(args[key] is not None and not finite(args[key]) for key in ('start', 'end')):
        raise ValueError('start/end需要有限数值或null')
    if args['seed'] is not None and type(args['seed']) is not int:
        raise ValueError('seed需要整数或null')
    if not isinstance(args['falloff_samples'], list) or any(not finite(v) for v in args['falloff_samples']):
        raise ValueError('falloff_samples需要有限数值数组')
    for key in ('overwrite', 'use_cache', 'overwrite_file'):
        if type(args[key]) is not bool:
            raise ValueError(key + '需要bool')
    if not isinstance(args['file_path'], str) or any(c in args['file_path'] for c in '\r\n\x00'):
        raise ValueError('file_path需要路径字符串')
    if args['action'] == 'save_preset':
        args['preset'] = preset_data(args['preset'])
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'object': {'type': 'string', 'default': ''},
    'start': {'type': ['number', 'null'], 'default': None}, 'end': {'type': ['number', 'null'], 'default': None}, 'step': {'type': 'integer', 'minimum': 1, 'maximum': 99, 'default': 1},
    'amounts': {'type': 'object', 'properties': {c: {'type': 'number', 'minimum': 0, 'maximum': 99.99} for c in CHANNELS}, 'required': CHANNELS, 'additionalProperties': False, 'default': DEFAULTS['amounts']},
    'falloff_samples': {'type': 'array', 'items': {'type': 'number'}, 'description': 'Apply requires one weight for each integer sampled frame; GUI evaluates its native gradient.'},
    'seed': {'type': ['integer', 'null'], 'default': None}, **{key: {'type': 'boolean', 'default': False} for key in ('overwrite', 'use_cache', 'overwrite_file')}, 'file_path': {'type': 'string', 'default': ''}, 'preset': {'type': 'object', 'description': 'Original Frame/TX/TY/TZ/RX/RY/RZ/Points .cgsk data'}}, 'additionalProperties': False}
