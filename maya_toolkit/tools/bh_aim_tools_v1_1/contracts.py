DEFAULTS = {'action': 'inventory', 'objects': [], 'keys_only': True, 'delete_rotation_keys': False, 'start': None, 'end': None}
ACTIONS = ['inventory', 'open_ui', 'create', 'attach', 'aim', 'bake', 'clear']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or type(args['keys_only']) is not bool or type(args['delete_rotation_keys']) is not bool:
        raise ValueError('无效 action 或开关类型')
    if not isinstance(args['objects'], list) or any(not isinstance(node, str) or not node or any(ch in node for ch in '.*?[]\n\r') for node in args['objects']):
        raise ValueError('objects 必须为明确对象名数组，空数组使用选择')
    if (args['start'] is None) != (args['end'] is None) or any(value is not None and type(value) is not int for value in (args['start'], args['end'])):
        raise ValueError('start/end 必须同时提供整数')
    if args['start'] is not None and args['start'] > args['end']:
        raise ValueError('start 不得大于 end')
    if args['delete_rotation_keys'] and (args['action'] != 'bake' or not args['keys_only']):
        raise ValueError('delete_rotation_keys 仅用于 keys_only 的 bake，会删除全部旧旋转键')
    return args


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'},
    'objects': {'type': 'array', 'items': {'type': 'string'}, 'default': []},
    'keys_only': {'type': 'boolean', 'default': True},
    'delete_rotation_keys': {'type': 'boolean', 'default': False, 'description': '仅keys_only bake；true删除控制器所有时段旧旋转键'},
    'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None}}, 'additionalProperties': False}
