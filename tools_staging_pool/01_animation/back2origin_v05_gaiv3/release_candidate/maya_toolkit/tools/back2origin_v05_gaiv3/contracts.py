"""Strict parameters matching the original frame-loop and channel semantics."""
DEFAULTS = {'action': 'convert', 'root_control': '', 'global_control': '', 'ik_controls': [],
            'pv_controls': [], 'other_controls': [], 'channels': ['Z'], 'start': None, 'end': None,
            'frame_step': 1, 'namespace': None}
ACTIONS = ['convert', 'reverse', 'discover', 'inventory', 'open_ui']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数: ' + ', '.join(sorted(set(kwargs) - set(DEFAULTS))))
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('无效 action')
    for name in ('root_control', 'global_control'):
        if not isinstance(args[name], str):
            raise ValueError(name + ' 必须为字符串')
    for name in ('ik_controls', 'pv_controls', 'other_controls'):
        if not isinstance(args[name], list) or any(not isinstance(node, str) or not node for node in args[name]):
            raise ValueError(name + ' 必须为明确的对象名数组')
    if not isinstance(args['channels'], list) or not args['channels'] or any(ch not in ('X', 'Z') for ch in args['channels']) or len(set(args['channels'])) != len(args['channels']):
        raise ValueError('channels 是不重复且非空的 X/Z 数组')
    if type(args['frame_step']) is not int or args['frame_step'] < 1:
        raise ValueError('frame_step 必须为正整数')
    if (args['start'] is None) != (args['end'] is None):
        raise ValueError('start/end 必须同时提供')
    if any(value is not None and type(value) is not int for value in (args['start'], args['end'])):
        raise ValueError('start/end 必须为整数；省略使用原播放范围整数边界')
    if args['start'] is not None and args['start'] > args['end']:
        raise ValueError('start 不得大于 end')
    ns = args['namespace']
    if ns is not None and (not isinstance(ns, str) or any(char in ns for char in '|.*?[]\n\r') or ns.startswith(':') or ns.endswith(':')):
        raise ValueError('namespace 为 None、根命名空间空字符串或明确命名空间')
    return args


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ACTIONS, 'default': 'convert'},
    'root_control': {'type': 'string', 'default': ''}, 'global_control': {'type': 'string', 'default': ''},
    'ik_controls': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
    'pv_controls': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
    'other_controls': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
    'channels': {'type': 'array', 'items': {'type': 'string', 'enum': ['X', 'Z']}, 'minItems': 1, 'uniqueItems': True, 'default': ['Z']},
    'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None},
    'frame_step': {'type': 'integer', 'minimum': 1, 'default': 1},
    'namespace': {'type': ['string', 'null'], 'default': None}}, 'additionalProperties': False}
