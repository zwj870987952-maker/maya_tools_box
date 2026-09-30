DEFAULTS = {'action': 'inventory', 'camera': '', 'objects': [], 'record_ids': [], 'include_orientation': False}
ACTIONS = ['inventory', 'open_ui', 'create', 'smart_bake', 'full_bake', 'cleanup']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or type(args['include_orientation']) is not bool:
        raise ValueError('action/orientation无效')
    if not isinstance(args['camera'], str) or any(c in args['camera'] for c in '.*?[]\r\n'):
        raise ValueError('camera需要明确名字')
    for key in ('objects', 'record_ids'):
        values = args[key]
        if not isinstance(values, list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in values) or len(set(values)) != len(values):
            raise ValueError(key + '需要不重复明确字符串数组')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'camera': {'type': 'string', 'default': '', 'description': '明确唯一perspective camera transform/shape'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': 'create明确对象，空数组当前选择'}, 'record_ids': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': '回烘/清理明确owned record UUID'}, 'include_orientation': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}
