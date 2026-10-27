from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'info', 'select_weighted', 'select_influences', 'export', 'import', 'lock_weights', 'unlock_weights', 'transfer', 'copy', 'connect']
CHANNELS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']


def normalize(**kwargs):
    allowed = {'action', 'objects', 'sources', 'destinations', 'source_prefix', 'destination_prefix', 'mode', 'channels', 'maintain_offset', 'directory', 'basename', 'formats', 'convention', 'create_skin', 'post_normalize', 'delete_history', 'allow_delete_history', 'allow_replace_connections', 'allow_unchecked_topology'}
    if set(kwargs) - allowed:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'inspect')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    for key in ('objects', 'sources', 'destinations'):
        if key in p and (not isinstance(p[key], list) or not 1 <= len(p[key]) <= 1000 or any(not isinstance(n, str) or not n.strip() for n in p[key]) or len(set(p[key])) != len(p[key])):
            raise ValueError('Unique nonempty ' + key + ' required')
    for key, default in (('maintain_offset', True), ('create_skin', True), ('post_normalize', False), ('delete_history', False), ('allow_delete_history', False), ('allow_replace_connections', False), ('allow_unchecked_topology', False)):
        p.setdefault(key, default)
        if type(p[key]) is not bool:
            raise ValueError(key + ' must be boolean')
    for key, default in (('source_prefix', ''), ('destination_prefix', ''), ('mode', 'direct'), ('convention', 'skininfo')):
        p.setdefault(key, default)
        if not isinstance(p[key], str) or len(p[key]) > 256:
            raise ValueError('Bounded string ' + key + ' required')
    if p['mode'] not in ('direct', 'parent', 'point', 'orient', 'point_orient') or p['convention'] not in ('skininfo', 'timal'):
        raise ValueError('Unknown mode/convention')
    p.setdefault('channels', CHANNELS[:])
    if not isinstance(p['channels'], list) or not p['channels'] or len(set(p['channels'])) != len(p['channels']) or any(c not in CHANNELS for c in p['channels']):
        raise ValueError('Unique TRS channels required')
    p.setdefault('formats', ['xml'])
    if not isinstance(p['formats'], list) or not p['formats'] or len(set(p['formats'])) != len(p['formats']) or any(f not in ('xml', 'json') for f in p['formats']):
        raise ValueError('Formats xml/json required')
    if p['action'] == 'import' and len(p['formats']) != 1:
        raise ValueError('Choose one import format')
    if p['convention'] == 'timal' and p['formats'] != ['xml']:
        raise ValueError('Timal original convention uses XML only')
    if p['delete_history'] and not p['allow_delete_history']:
        raise ValueError('Explicit allow_delete_history required')
    return p


class SkinInfoSuperConnectTool(BaseMayaTool):
    tool_id = 'skin_info_and_super_connect'
    tool_name = 'Skin Info / Super Connect / Timal Weights'
    category = 'rigging'
    version = '1.92-candidate.1'
    description = 'Full skin information/weight interchange, transfer, joint locks and prefix matched direct/constraints, with original full layouts and safe files.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, **{k: {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000, 'uniqueItems': True} for k in ('objects', 'sources', 'destinations')}, **{k: {'type': 'string'} for k in ('directory', 'basename', 'source_prefix', 'destination_prefix')}, 'mode': {'type': 'string', 'enum': ['direct', 'parent', 'point', 'orient', 'point_orient']}, 'convention': {'type': 'string', 'enum': ['skininfo', 'timal']}, 'channels': {'type': 'array', 'items': {'type': 'string', 'enum': CHANNELS}, 'minItems': 1, 'uniqueItems': True}, 'formats': {'type': 'array', 'items': {'type': 'string', 'enum': ['xml', 'json']}, 'minItems': 1, 'uniqueItems': True}, **{k: {'type': 'boolean'} for k in ('maintain_offset', 'create_skin', 'post_normalize', 'delete_history', 'allow_delete_history', 'allow_replace_connections', 'allow_unchecked_topology')}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .operations import plan
            return ToolResult.ok(message='Read-only full scope/file/connection plan', data=plan(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .operations import execute
        return ToolResult.ok(message='Suite operation finished', data=execute(normalize(**kwargs)), warnings=['Files are outside Maya Undo; real GUI/production skin acceptance not_run'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui()
