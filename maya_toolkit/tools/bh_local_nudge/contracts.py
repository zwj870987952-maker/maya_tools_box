import math

DEFAULTS = {'action': 'nudge', 'objects': [], 'channel': 'translate', 'axis': 'Y', 'direction': 'positive', 'amount': None, 'ctrl': False, 'alt': False}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('inventory', 'open_ui', 'nudge') or args['channel'] not in ('translate', 'rotate') or args['axis'] not in ('X', 'Y', 'Z') or args['direction'] not in ('positive', 'negative'):
        raise ValueError('无效动作/通道/轴/方向')
    if type(args['ctrl']) is not bool or type(args['alt']) is not bool:
        raise ValueError('ctrl/alt 必须为布尔')
    if not isinstance(args['objects'], list) or any(not isinstance(node, str) or not node or any(ch in node for ch in '.*?[]\n\r') for node in args['objects']):
        raise ValueError('objects 必须为明确对象名数组')
    if args['amount'] is None:
        args['amount'] = 0.01 if args['channel'] == 'translate' else 1.0
    if type(args['amount']) not in (int, float) or not math.isfinite(args['amount']) or args['amount'] <= 0:
        raise ValueError('amount 必须为有限正数')
    args['delta'] = args['amount'] * (0.5 if args['ctrl'] else 1) * (0.25 if args['alt'] else 1) * (1 if args['direction'] == 'positive' else -1)
    return args


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ['inventory', 'open_ui', 'nudge'], 'default': 'nudge'},
    'objects': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
    'channel': {'type': 'string', 'enum': ['translate', 'rotate'], 'default': 'translate'},
    'axis': {'type': 'string', 'enum': ['X', 'Y', 'Z'], 'default': 'Y'},
    'direction': {'type': 'string', 'enum': ['positive', 'negative'], 'default': 'positive'},
    'amount': {'type': ['number', 'null'], 'exclusiveMinimum': 0, 'default': None, 'description': '省略：translate=.01，rotate=1，当前Maya单位'},
    'ctrl': {'type': 'boolean', 'default': False}, 'alt': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}
