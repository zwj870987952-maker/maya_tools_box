DEFAULTS = {'action': 'inventory', 'root_joint': '', 'strength': 3, 'curves': [], 'selected_only': True, 'annotation': True, 'bake_all': False, 'in_timeline': False}
ACTIONS = ['inventory', 'open_ui', 'smooth_mocap', 'smooth_keys']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('未知action')
    if not isinstance(args['root_joint'], str) or any(c in args['root_joint'] for c in '.*?[]\r\n'):
        raise ValueError('root_joint需要明确joint名')
    if type(args['strength']) is not int or not 1 <= args['strength'] <= 100:
        raise ValueError('strength需要1..100整数，实际次数strength-1')
    if not isinstance(args['curves'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['curves']) or len(set(args['curves'])) != len(args['curves']):
        raise ValueError('curves需要明确不重复animCurve名')
    for key in ('selected_only', 'annotation', 'bake_all', 'in_timeline'):
        if type(args[key]) is not bool:
            raise ValueError(key + '需要bool')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'root_joint': {'type': 'string', 'default': ''}, 'strength': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 3}, 'curves': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'default': []}, **{key: {'type': 'boolean', 'default': value} for key, value in DEFAULTS.items() if type(value) is bool}}, 'additionalProperties': False}
