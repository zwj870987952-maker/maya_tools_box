import math

DEFAULTS = {'action': 'inventory', 'direction': 'left', 'controllers': [], 'feet_number': 2, 'angle': 45, 'bake': True, 'correction_locators': True, 'counter_rotation': False, 'start': None, 'end': None, 'record_id': '', 'remove_layers': False}
ACTIONS = ['inventory', 'open_ui', 'run', 'cleanup']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or args['direction'] not in ('left', 'right', 'back'):
        raise ValueError('未知action/direction')
    if type(args['feet_number']) is not int or not 1 <= args['feet_number'] <= 999:
        raise ValueError('feet_number需要1..999整数，原0足临时约束列表无效')
    if type(args['angle']) not in (int, float) or not math.isfinite(args['angle']) or not 0 <= args['angle'] <= 90:
        raise ValueError('angle需要0..90')
    if not isinstance(args['controllers'], list) or any(not isinstance(n, str) or not n or any(c in n for c in '.*?[]\r\n') for n in args['controllers']) or len(set(args['controllers'])) != len(args['controllers']):
        raise ValueError('controllers需要明确不重复有序数组')
    for key in ('bake', 'correction_locators', 'counter_rotation', 'remove_layers'):
        if type(args[key]) is not bool:
            raise ValueError(key + '需要bool')
    for key in ('start', 'end'):
        if args[key] is not None and (type(args[key]) not in (float, int) or not math.isfinite(args[key])):
            raise ValueError('start/end需要有限数值或null')
    if not isinstance(args['record_id'], str):
        raise ValueError('record_id需要UUID字符串')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'direction': {'type': 'string', 'enum': ['left', 'right', 'back'], 'default': 'left'}, 'controllers': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': 'Master, feet_number feet, MainBody, Upperbody, Head'}, 'feet_number': {'type': 'integer', 'minimum': 1, 'maximum': 999, 'default': 2}, 'angle': {'type': 'number', 'minimum': 0, 'maximum': 90, 'default': 45}, **{key: {'type': 'boolean', 'default': DEFAULTS[key]} for key in ('bake', 'correction_locators', 'counter_rotation', 'remove_layers')}, 'start': {'type': ['number', 'null'], 'default': None}, 'end': {'type': ['number', 'null'], 'default': None}, 'record_id': {'type': 'string', 'default': ''}}, 'additionalProperties': False}
