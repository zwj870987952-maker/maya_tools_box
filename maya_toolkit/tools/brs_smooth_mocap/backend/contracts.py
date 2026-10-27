DEFAULTS = {'action': 'inventory', 'objects': [], 'annotation': True, 'constrain': True, 'bake_all': False, 'in_timeline': False, 'translate': True, 'rotate': True}
ACTIONS = ['inventory', 'open_ui', 'create', 'apply', 'create_guide', 'redirect']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('未知action')
    if not isinstance(args['objects'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['objects']) or len(set(args['objects'])) != len(args['objects']):
        raise ValueError('objects需要明确不重复transform数组')
    for key in set(DEFAULTS) - {'action', 'objects'}:
        if type(args[key]) is not bool:
            raise ValueError(key + '需要bool')
    if args['action'] in ('apply', 'redirect') or (args['action'] == 'create' and args['constrain']):
        if not args['translate'] and not args['rotate']:
            raise ValueError('需要至少Position或Rotation')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'default': []}, **{key: {'type': 'boolean', 'default': value} for key, value in DEFAULTS.items() if type(value) is bool}}, 'additionalProperties': False}
