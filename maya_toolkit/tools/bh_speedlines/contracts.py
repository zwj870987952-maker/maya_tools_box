import math

ACTIONS = ['inventory', 'open_ui', 'geometry', 'flip', 'simplify', 'smooth', 'key_visibility', 'start_draw', 'stop_draw', 'draw_depth', 'reset_depth']
DEFAULTS = {'action': 'inventory', 'objects': [], 'camera': 'persp', 'high_detail': False, 'on_layer': False, 'hold_two': False,
            'consume_curves': True, 'ep_tool': False, 'depth': 0.0}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('无效 action')
    for name in ('high_detail', 'on_layer', 'hold_two', 'consume_curves', 'ep_tool'):
        if type(args[name]) is not bool:
            raise ValueError(name + ' 必须为布尔')
    if not isinstance(args['objects'], list) or any(not isinstance(node, str) or not node or any(char in node for char in '.*?[]\n\r') for node in args['objects']):
        raise ValueError('objects 必须为明确对象名数组')
    if not isinstance(args['camera'], str) or not args['camera'] or any(char in args['camera'] for char in '.*?[]\n\r'):
        raise ValueError('camera 必须为明确相机transform')
    if type(args['depth']) not in (int, float) or not math.isfinite(args['depth']):
        raise ValueError('depth 必须为有限数字')
    return args


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'},
    'objects': {'type': 'array', 'items': {'type': 'string'}, 'default': []}, 'camera': {'type': 'string', 'default': 'persp'},
    'high_detail': {'type': 'boolean', 'default': False}, 'on_layer': {'type': 'boolean', 'default': False}, 'hold_two': {'type': 'boolean', 'default': False},
    'consume_curves': {'type': 'boolean', 'default': True, 'description': 'geometry默认删除两输入曲线；false保留'},
    'ep_tool': {'type': 'boolean', 'default': False}, 'depth': {'type': 'number', 'default': 0}}, 'additionalProperties': False}
