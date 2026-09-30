"""Generate alternating bookmarks with a complete read-only effect preview."""
import math

from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .palettes import COLOR_PALETTES

DEFAULTS = dict(action='generate', objects=None, layer='auto', palette_name='dual',
                prefix='BM', clear_existing=False, max_bookmarks=10000)


def normalize(kwargs):
    unknown = set(kwargs) - set(DEFAULTS)
    if unknown:
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(unknown)))
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ('generate', 'clear', 'inspect'):
        raise ValueError('action must be generate, clear or inspect')
    if args['palette_name'] not in COLOR_PALETTES:
        raise ValueError('Unknown palette_name')
    if not isinstance(args['prefix'], str) or not args['prefix'].strip() or len(args['prefix']) > 240:
        raise ValueError('prefix must be a non-empty string of at most 240 characters')
    if not isinstance(args['layer'], str) or not args['layer'].strip():
        raise ValueError('layer must be a non-empty name, auto or All')
    if type(args['clear_existing']) is not bool:
        raise ValueError('clear_existing must be boolean')
    if type(args['max_bookmarks']) is not int or not 1 <= args['max_bookmarks'] <= 100000:
        raise ValueError('max_bookmarks must be an integer in [1,100000]')
    objects = args['objects']
    if isinstance(objects, str):
        objects = [objects]
    if objects is not None and (not isinstance(objects, list) or not objects or any(not isinstance(o, str) or not o.strip() for o in objects)):
        raise ValueError('objects must be null, one node name or a non-empty array of names')
    args['objects'] = objects
    return args


def plan_intervals(frames, palette_name, prefix):
    colors = COLOR_PALETTES[palette_name]['colors']
    if len(colors) < 2 or any(colors[i] == colors[(i+1) % len(colors)] for i in range(len(colors))):
        raise ValueError('Palette must alternate, including across cycle boundaries')
    if len(frames) < 2 or not all(math.isfinite(f) for f in frames) or any(a >= b for a, b in zip(frames, frames[1:])):
        raise ValueError('At least two finite increasing frame times are required')
    return [dict(name='{}_{}_{}'.format(prefix, int(round(start)), int(round(stop))),
                 start=start, stop=stop, color=list(colors[i % len(colors)]), priority=i)
            for i, (start, stop) in enumerate(zip(frames, frames[1:]))]


class AnimLayerKeyframeBookmarkTool(BaseMayaTool):
    tool_id = 'anim_layer_keyframe_bookmark'
    tool_name = '动画层关键帧区间书签生成器'
    category = 'Animation'
    version = '1.1.0'
    description = '按选定动画层相邻关键帧生成四色板交替区间书签；支持关键帧检查与清空。清空影响场景所有书签。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'action': {'type': 'string', 'enum': ['generate', 'clear', 'inspect'], 'default': 'generate'},
            'objects': {'anyOf': [{'type': 'null'}, {'type': 'string', 'minLength': 1}, {'type': 'array', 'minItems': 1, 'items': {'type': 'string', 'minLength': 1}}], 'default': None},
            'layer': {'type': 'string', 'minLength': 1, 'default': 'auto'},
            'palette_name': {'type': 'string', 'enum': list(COLOR_PALETTES), 'default': 'dual'},
            'prefix': {'type': 'string', 'minLength': 1, 'maxLength': 240, 'default': 'BM'},
            'clear_existing': {'type': 'boolean', 'default': False, 'description': '生成前删除场景全部 timeSliderBookmark，不按前缀/动画层筛选。'},
            'max_bookmarks': {'type': 'integer', 'minimum': 1, 'maximum': 100000, 'default': 10000},
        },
    }

    def _prepare(self, kwargs):
        args = normalize(kwargs)
        from . import layer_queries as query
        cmds = query.cmds
        if args['action'] != 'inspect':
            if not cmds.pluginInfo('timeSliderBookmark', query=True, loaded=True):
                raise ValueError('Load timeSliderBookmark explicitly or open the candidate UI first')
            if not cmds.undoInfo(query=True, state=True):
                raise ValueError('Enable Maya Undo before changing bookmarks')
        deletes = sorted(cmds.ls(type='timeSliderBookmark') or []) if args['action'] == 'clear' or (args['action'] == 'generate' and args['clear_existing']) else []
        for node in deletes:
            if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
                raise ValueError('Cannot delete referenced/locked bookmark: ' + node)
        deletion_targets = [dict(node=node, uuid=cmds.ls(node, uuid=True)[0]) for node in deletes]
        data = dict(action=args['action'], deleted_bookmarks=deletes, deletion_targets=deletion_targets,
                    intervals=[], keyframes=[], objects=[], curves=[], layer=None)
        if args['action'] == 'clear':
            return args, data
        source = args['objects'] if args['objects'] is not None else (cmds.ls(selection=True, long=True) or [])
        objects = []
        for obj in source:
            matches = cmds.ls(obj, long=True) or []
            if len(matches) != 1 or '.' in matches[0]:
                raise ValueError('Object must resolve uniquely to one node: ' + obj)
            if matches[0] not in objects:
                objects.append(matches[0])
        if not objects:
            raise ValueError('Select animated objects or provide objects')
        frames, layer, curves = query.get_keyframes_from_layer(objects, args['layer'], False)
        data.update(keyframes=frames, layer=layer, objects=objects, curves=curves)
        if args['action'] == 'generate':
            if len(frames) - 1 > args['max_bookmarks']:
                raise ValueError('Interval count exceeds max_bookmarks')
            data['intervals'] = plan_intervals(frames, args['palette_name'], args['prefix'])
        return args, data

    def validate(self, **kwargs):
        try:
            args, data = self._prepare(kwargs)
            data['count'] = len(data['intervals']) if args['action'] == 'generate' else len(data['deleted_bookmarks']) if args['action'] == 'clear' else len(data['keyframes'])
            return ToolResult.ok('预检: {} 个区间、{} 个待删除书签、{} 个键时间。'.format(len(data['intervals']), len(data['deleted_bookmarks']), len(data['keyframes'])),
                                 data=data, dry_run=True)
        except Exception as error:
            return ToolResult.fail('预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from . import layer_queries as query
        cmds = query.cmds
        args, data = self._prepare(kwargs)
        created = []
        created_ids = {}
        deleted = []
        errors = []
        try:
            if args['action'] == 'generate':
                # Global plugin save requirement matches upstream; it is not a Maya Undo effect.
                cmds.pluginInfo('timeSliderBookmark', edit=True, writeRequires=True)
            if data['deleted_bookmarks']:
                cmds.delete(data['deleted_bookmarks'])
                deleted = list(data['deleted_bookmarks'])
            for interval in data['intervals']:
                node = cmds.createNode('timeSliderBookmark', skipSelect=True)
                created.append(node)
                created_ids[node] = cmds.ls(node, uuid=True)[0]
                cmds.setAttr(node + '.timeRangeStart', interval['start'])
                cmds.setAttr(node + '.timeRangeStop', interval['stop'])
                cmds.setAttr(node + '.name', interval['name'], type='string')
                cmds.setAttr(node + '.color', *interval['color'])
                cmds.setAttr(node + '.priority', interval['priority'])
        except Exception as error:
            errors.append(str(error))
            # Maya may reuse a deleted node's name for a newly created bookmark.
            deleted = [item['node'] for item in data['deletion_targets'] if not cmds.ls(item['uuid'])]
        data.update(bookmarks=created, created_bookmark_uuids=created_ids, deleted_bookmarks=deleted,
                    count=len(created) if args['action'] == 'generate' else len(deleted) if args['action'] == 'clear' else len(data['keyframes']))
        warnings = ['异常不会自动回滚；可能留下部分书签或已删除项，请检查并 Maya Undo。'] if errors else []
        if args['action'] == 'generate':
            warnings.append('插件 writeRequires 保存要求设置不能由 Maya Undo 撤回。')
        return ToolResult(success=not errors, message='{}: 创建 {}、删除 {} 个书签。'.format(args['action'], len(created), len(deleted)),
                          data=data, errors=errors, warnings=warnings)

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(self)
