MODES = {'translate': 'frame', 'rotate': 'frame', 'scale': 'frame', 'other': 'none'}
ACTIONS = ['inventory', 'open_ui', 'create_locators', 'execute', 'cleanup', 'save_config', 'load_config']
DEFAULTS = {'action': 'inventory', 'pairs': [], 'start': None, 'end': None, 'file_path': '', 'overwrite_file': False}


def pair_data(value):
    if not isinstance(value, dict) or set(value) - {'source', 'target', 'modes'} or not {'source', 'target'}.issubset(value):
        raise ValueError('pair需要source/target，可选modes')
    result = dict(value)
    for key in ('source', 'target'):
        if not isinstance(result[key], str) or not result[key] or any(c in result[key] for c in '.*?[]\r\n'):
            raise ValueError('pair需要明确transform名')
    modes = result.get('modes', {})
    if not isinstance(modes, dict) or set(modes) - set(MODES):
        raise ValueError('未知channel模式')
    result['modes'] = dict(MODES, **modes)
    for channel, mode in result['modes'].items():
        if mode not in (('numeric', 'none') if channel == 'other' else ('frame', 'constraint', 'numeric', 'none')):
            raise ValueError('无效模式: ' + channel)
    return result


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS:
        raise ValueError('未知action')
    if not isinstance(args['pairs'], list):
        raise ValueError('pairs需要数组')
    args['pairs'] = [pair_data(value) for value in args['pairs']]
    for key in ('start', 'end'):
        if args[key] is not None and type(args[key]) is not int:
            raise ValueError('start/end需要整数或null，原UI截断playback值')
    if not isinstance(args['file_path'], str) or any(c in args['file_path'] for c in '\r\n\x00'):
        raise ValueError('file_path需要路径')
    if type(args['overwrite_file']) is not bool:
        raise ValueError('overwrite_file需要bool')
    return args


SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inventory'}, 'pairs': {'type': 'array', 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}, 'modes': {'type': 'object', 'properties': {c: {'type': 'string', 'enum': ['numeric', 'none'] if c == 'other' else ['frame', 'constraint', 'numeric', 'none']} for c in MODES}, 'additionalProperties': False}}, 'required': ['source', 'target'], 'additionalProperties': False}}, 'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None}, 'file_path': {'type': 'string', 'default': ''}, 'overwrite_file': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}
