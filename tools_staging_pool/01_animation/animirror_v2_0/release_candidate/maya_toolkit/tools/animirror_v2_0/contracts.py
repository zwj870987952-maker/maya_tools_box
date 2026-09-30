"""Strict JSON arguments; expose the original axis radio choice without inferred planes."""
import math

ACTIONS = ('inventory', 'open_ui', 'mirror', 'mirror_bake', 'bake', 'clear')
DEFAULTS = {'action': 'mirror', 'objects': [], 'translations': True, 'rotations': True, 'translation_axis': 'X',
            'invert_rotation': ['Y', 'Z'], 'start': None, 'end': None}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数: ' + ', '.join(sorted(set(kwargs) - set(DEFAULTS))))
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or type(args['translations']) is not bool or type(args['rotations']) is not bool:
        raise ValueError('无效操作或通道开关')
    if args['translation_axis'] not in ('X', 'Y', 'Z'):
        raise ValueError('translation_axis 必须为 X、Y 或 Z')
    values = args['invert_rotation']
    if not isinstance(values, list) or any(value not in ('X', 'Y', 'Z') for value in values) or len(values) != len(set(values)):
        raise ValueError('invert_rotation 必须为不重复的 X/Y/Z 数组')
    objects = args['objects']
    if not isinstance(objects, list) or any(not isinstance(node, str) or not node or any(char in node for char in '*?[]\n\r') or '.' in node for node in objects):
        raise ValueError('objects 必须为明确的对象名数组')
    if args['action'] in ('mirror', 'mirror_bake') and len(objects) not in (0, 3):
        raise ValueError('objects 按中心、参考、目标顺序恰含三项；空数组使用选择')
    if args['action'] in ('mirror', 'mirror_bake') and not args['translations'] and not args['rotations']:
        raise ValueError('位移与旋转不能同时关闭')
    if (args['start'] is None) != (args['end'] is None):
        raise ValueError('start/end 必须同时提供')
    for value in (args['start'], args['end']):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            raise ValueError('帧范围必须为有限数字')
    if args['start'] is not None and args['start'] > args['end']:
        raise ValueError('start 不得大于 end')
    return args


SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': list(ACTIONS), 'default': 'mirror'},
    'objects': {'type': 'array', 'items': {'type': 'string'}, 'description': '中心、参考、目标；省略则使用三项选择', 'default': []},
    'translations': {'type': 'boolean', 'default': True}, 'rotations': {'type': 'boolean', 'default': True},
    'translation_axis': {'type': 'string', 'enum': ['X', 'Y', 'Z'], 'default': 'X', 'description': '原位移单选 X/Y/Z；UI 标签分别 XZ/YX/ZY'},
    'invert_rotation': {'type': 'array', 'items': {'type': 'string', 'enum': ['X', 'Y', 'Z']}, 'uniqueItems': True, 'default': ['Y', 'Z']},
    'start': {'type': ['number', 'null'], 'default': None}, 'end': {'type': ['number', 'null'], 'default': None}},
    'additionalProperties': False}
