import math

ACTIONS = ['inventory', 'open_ui', 'inbetween', 'slider', 'capture_snapshot', 'set_keys', 'rekey', 'clean_subframes', 'remove_boring', 'smash_bake', 'set_tangent', 'import_preferences', 'export_preferences', 'native_callback']
SLIDERS = ['tween', 'snapshot', 'worldSpace', 'inOut', 'PosePusher', 'multiply']
DEFAULTS = {'action': 'inventory', 'objects': [], 'attributes': [], 'value': 0.0, 'use_set_value': False, 'from_current_value': False, 'slider_kind': 'tween', 'snapshot_data': {}, 'use_all_layers': True, 'match_last': False, 'special': False, 'leave_first': True, 'start': None, 'end': None, 'tangent': 'auto', 'file_path': '', 'overwrite_file': False, 'callback_ticket': '', 'camera': ''}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or args['slider_kind'] not in SLIDERS or args['tangent'] not in ['auto', 'spline', 'clamped', 'step', 'linear', 'flat', 'plateau', 'free']:
        raise ValueError('action/slider_kind/tangent无效')
    for key in ('objects', 'attributes'):
        values = args[key]
        invalid = '.*?[]\r\n' if key == 'objects' else '.|:*?[]\r\n'
        if not isinstance(values, list) or any(not isinstance(n, str) or not n or any(c in n for c in invalid) for n in values) or len(set(values)) != len(values):
            raise ValueError(key + '需要明确不重复字符串数组')
    for key in ('use_set_value', 'from_current_value', 'use_all_layers', 'match_last', 'special', 'leave_first', 'overwrite_file'):
        if type(args[key]) is not bool:
            raise ValueError(key + '需要bool')
    if type(args['value']) not in (int, float) or not math.isfinite(args['value']) or not -1 <= args['value'] <= 1:
        raise ValueError('value需要-1..1有限数值')
    for key in ('start', 'end'):
        if args[key] is not None and type(args[key]) is not int:
            raise ValueError('Smash start/end需要整数或null')
    if not isinstance(args['snapshot_data'], dict) or not isinstance(args['file_path'], str) or not isinstance(args['callback_ticket'], str) or not isinstance(args['camera'], str):
        raise ValueError('snapshot_data/file_path/ticket类型无效')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}, 'attributes': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'description': '空数组使用全部原可用通道，API代替ChannelBox'}, 'value': {'type': 'number', 'minimum': -1, 'maximum': 1, 'default': 0.0}, 'slider_kind': {'type': 'string', 'enum': SLIDERS, 'default': 'tween'}, 'snapshot_data': {'type': 'object', 'description': 'capture_snapshot结果原结构，用于snapshot slider'}, 'tangent': {'type': 'string', 'enum': ['auto', 'spline', 'clamped', 'step', 'linear', 'flat', 'plateau', 'free'], 'default': 'auto'}, 'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None}, 'file_path': {'type': 'string', 'default': ''}, 'callback_ticket': {'type': 'string', 'default': '', 'description': '仅原UI临时已注册回调，外部不能指定任意代码'}, **{key: {'type': 'boolean', 'default': DEFAULTS[key]} for key in ('use_set_value', 'from_current_value', 'use_all_layers', 'match_last', 'special', 'leave_first', 'overwrite_file')}}, 'additionalProperties': False}
SCHEMA['properties']['camera'] = {'type': 'string', 'default': '', 'description': 'API inOut必须明确camera，GUI使用原活动视图相机；只读'}
