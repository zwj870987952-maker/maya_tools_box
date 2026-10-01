import hashlib
import json
import math
import os
from pathlib import Path
import uuid
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .model import document, transform, integer, STYLES, load_bytes

ACTIONS = ['inspect', 'configure', 'add', 'edit', 'move', 'select', 'copy', 'paste', 'delete', 'clear', 'load', 'save', 'sync', 'set_current_frame', 'play', 'stop']
FIELDS = {'state', 'action', 'frame', 'source_frame', 'frames', 'block', 'block_type', 'start_frame', 'frame_count', 'path', 'overwrite'}
USES = {'inspect': set(), 'configure': {'start_frame', 'frame_count'}, 'add': {'frame', 'block', 'block_type', 'overwrite'}, 'edit': {'frame', 'block'}, 'move': {'source_frame', 'frame', 'overwrite'}, 'select': {'frames'}, 'copy': set(), 'paste': {'frame', 'overwrite'}, 'delete': {'frames'}, 'clear': set(), 'load': {'path'}, 'save': {'path', 'overwrite'}, 'sync': set(), 'set_current_frame': {'frame'}, 'play': set(), 'stop': set()}
REQUIRED = {'add': {'frame'}, 'edit': {'frame', 'block'}, 'move': {'source_frame', 'frame'}, 'select': {'frames'}, 'paste': {'frame'}, 'load': {'path'}, 'save': {'path'}, 'set_current_frame': {'frame'}}
BLOCK_SCHEMA = {'type': 'object', 'properties': {'color': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': {'type': 'number', 'minimum': 0, 'maximum': 1}}, 'label': {'type': 'string', 'maxLength': 256}, 'name': {'type': 'string', 'maxLength': 256}}, 'additionalProperties': False}
FRAME_SCHEMA = {'type': 'integer', 'minimum': -10000000, 'maximum': 10000000}
DOCUMENT_SCHEMA = {'type': 'object', 'properties': {'start_frame': FRAME_SCHEMA, 'frame_count': {'type': 'integer', 'minimum': 10, 'maximum': 1000}, 'blocks': {'type': 'object', 'maxProperties': 10000, 'propertyNames': {'pattern': '^(0|-[1-9][0-9]*|[1-9][0-9]*)$'}, 'additionalProperties': BLOCK_SCHEMA}, 'selected': {'type': 'array', 'items': FRAME_SCHEMA, 'uniqueItems': True}, 'clipboard': {'type': 'object', 'maxProperties': 10000, 'additionalProperties': BLOCK_SCHEMA}}, 'additionalProperties': False}


def file_path(value):
    if not isinstance(value, str) or not value or any(c in value for c in ('\n', '\r', '"')):
        raise ValueError('Explicit absolute JSON path is required')
    path = Path(value)
    if not path.is_absolute() or path.suffix.lower() != '.json' or any(p in ('.', '..') for p in value.replace('\\', '/').split('/')):
        raise ValueError('Absolute .json path without dot segments required')
    for node in [path] + list(path.parents):
        if (node.exists() or node.is_symlink()) and (node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Symlink/junction paths are unsupported')
    if not path.parent.is_dir():
        raise ValueError('Parent directory must already exist')
    return path.resolve()


def normalize(**kwargs):
    if set(kwargs) - FIELDS:
        raise ValueError('Unknown arguments')
    p = dict(action='inspect', state=None)
    p.update(kwargs)
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    specific = set(kwargs) - {'action', 'state'}
    if specific - USES[p['action']] or not REQUIRED.get(p['action'], set()) <= specific:
        raise ValueError('Missing or irrelevant action arguments')
    if 'overwrite' in p and type(p['overwrite']) is not bool:
        raise ValueError('overwrite must be boolean')
    if p.get('block_type', 'keyframe') not in STYLES:
        raise ValueError('Unknown block type')
    for key in ('frame', 'source_frame', 'start_frame'):
        if key in p:
            integer(p[key])
    if 'frames' in p and (not isinstance(p['frames'], list) or any(type(f) is not int for f in p['frames']) or len(set(p['frames'])) != len(p['frames'])):
        raise ValueError('frames must be unique integer values')
    p['state'] = document(p['state'])
    return p


def preflight(p):
    from maya import cmds
    action = p['action']
    plan = {'action': action, 'gui_acceptance': 'not_run', 'scene_keys_changed': False}
    if action in ('load', 'save'):
        path = file_path(p['path'])
        plan['path'] = str(path)
        if path.exists() and not path.is_file():
            raise ValueError('Config is not a regular file')
        if action == 'load':
            plan['state'] = load_bytes(path.read_bytes())
        else:
            if path.exists() and not p.get('overwrite', False):
                raise ValueError('Existing JSON requires overwrite=True; a separate backup will be retained')
            plan['existing_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
            plan['state'] = p['state']
            if len((json.dumps(p['state'], ensure_ascii=False, indent=2) + '\n').encode('utf-8')) > 4 * 1024 * 1024:
                raise ValueError('Saved config would exceed the 4 MiB load limit')
    elif action == 'sync':
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        if not start.is_integer() or not end.is_integer():
            raise ValueError('Marker frames require an integer Maya playback range')
        plan['state'] = transform(p['state'], 'configure', start_frame=int(start), frame_count=int(end - start + 1))
    elif action in ('set_current_frame', 'play', 'stop'):
        if action == 'play' and cmds.about(batch=True):
            raise ValueError('Interactive Maya is required for playback')
        plan['state'] = p['state']
        if action == 'set_current_frame':
            plan['frame'] = p['frame']
    else:
        plan['state'] = transform(p['state'], action, **{k: v for k, v in p.items() if k not in ('state', 'action')})
    return plan


class TimelineEnhancedTool(BaseMayaTool):
    tool_id = 'timeline_enhanced'
    tool_name = '时间轴方块规划（基础/增强）'
    category = 'animation'
    version = '1.0.0-candidate.1'
    description = 'Manage colored timeline planning blocks independently of scene animation keys. Complete basic/enhanced UI, pure document operations, safe JSON persistence, explicit Maya playback/time controls.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'state': DOCUMENT_SCHEMA, 'frame': FRAME_SCHEMA, 'source_frame': FRAME_SCHEMA, 'frames': {'type': 'array', 'items': FRAME_SCHEMA, 'uniqueItems': True}, 'start_frame': FRAME_SCHEMA, 'frame_count': {'type': 'integer', 'minimum': 10, 'maximum': 1000}, 'block': BLOCK_SCHEMA, 'block_type': {'type': 'string', 'enum': list(STYLES)}, 'path': {'type': 'string', 'minLength': 1}, 'overwrite': {'type': 'boolean', 'default': False}}, 'additionalProperties': False, 'allOf': [{'if': {'properties': {'action': {'const': action}}, 'required': ['action']}, 'then': {'required': sorted(fields)}} for action, fields in REQUIRED.items()]}

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='Read-only planning document preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from maya import cmds
        p = normalize(**kwargs)
        plan = preflight(p)
        if p['action'] == 'save':
            path = Path(plan['path'])
            data = (json.dumps(plan['state'], ensure_ascii=False, indent=2) + '\n').encode('utf-8')
            if plan['existing_sha256'] is None:
                with path.open('xb') as stream:
                    stream.write(data)
            else:
                # Preserve exact previous bytes before explicit replacement.
                old = path.read_bytes()
                if hashlib.sha256(old).hexdigest() != plan['existing_sha256']:
                    raise RuntimeError('Config changed after preflight')
                backup = path.with_name(path.name + '.backup-' + uuid.uuid4().hex)
                with backup.open('xb') as stream:
                    stream.write(old)
                temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
                try:
                    with temporary.open('xb') as stream:
                        stream.write(data)
                    file_path(str(path))
                    if hashlib.sha256(path.read_bytes()).hexdigest() != plan['existing_sha256']:
                        raise RuntimeError('Config changed during save; backup retained')
                    os.replace(str(temporary), str(path))
                finally:
                    if temporary.exists():
                        temporary.unlink()
                plan['backup'] = str(backup)
        elif p['action'] == 'set_current_frame':
            cmds.currentTime(p['frame'])
        elif p['action'] == 'play':
            cmds.play(forward=True)
        elif p['action'] == 'stop':
            cmds.play(state=False)
        return ToolResult.ok(message='Timeline action complete: ' + p['action'], data=plan, warnings=['JSON writes, playback/time and UI memory have separate effects; markers never move animation keys'])

    def show_ui(self, parent=None, variant='enhanced'):
        from .ui import show_ui
        return show_ui(self, variant)
