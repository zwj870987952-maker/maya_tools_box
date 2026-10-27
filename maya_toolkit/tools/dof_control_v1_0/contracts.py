DEFAULTS = {'action': 'inventory', 'cameras': [], 'record_ids': [], 'template': False}
ACTIONS = ['inventory', 'open_ui', 'create', 'cleanup', 'set_template']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or type(args['template']) is not bool:
        raise ValueError('未知action或template非bool')
    for key in ('cameras', 'record_ids'):
        if not isinstance(args[key], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args[key]) or len(set(args[key])) != len(args[key]):
            raise ValueError(key + '需要明确不重复字符串数组')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'cameras': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': '明确camera shape或其transform，create空数组使用当前选择'}, 'record_ids': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': 'cleanup/set_template需要明确owned record UUID'}, 'template': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}
