import re

DEFAULTS = {'action': 'records', 'mode': 'local', 'driven': '', 'driver': '', 'attribute': 'space', 'record_id': '', 'allow_reference_edits': False}
SCHEMA = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['records', 'open_ui', 'create', 'prepare', 'add_driver', 'connect'], 'default': 'records'}, 'mode': {'type': 'string', 'enum': ['local', 'reference'], 'default': 'local'}, 'driven': {'type': 'string', 'default': ''}, 'driver': {'type': 'string', 'default': ''}, 'attribute': {'type': 'string', 'pattern': '^[A-Za-z_][A-Za-z0-9_]*$', 'default': 'space'}, 'record_id': {'type': 'string', 'default': ''}, 'allow_reference_edits': {'type': 'boolean', 'default': False, 'description': 'reference模式明确允许创建属性/约束连接对应的Maya reference edits，local始终拒绝引用重父级'}}, 'additionalProperties': False}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in SCHEMA['properties']['action']['enum'] or args['mode'] not in ('local', 'reference'):
        raise ValueError('action/mode无效')
    if type(args['allow_reference_edits']) is not bool:
        raise ValueError('allow_reference_edits需要bool')
    for field in ('driven', 'driver', 'record_id'):
        value = args[field]
        if not isinstance(value, str) or any(c in value for c in '.*?[]\r\n'):
            raise ValueError(field + '须明确节点/UUID')
    if not isinstance(args['attribute'], str) or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', args['attribute']):
        raise ValueError('自定义属性名称非法')
    return args
