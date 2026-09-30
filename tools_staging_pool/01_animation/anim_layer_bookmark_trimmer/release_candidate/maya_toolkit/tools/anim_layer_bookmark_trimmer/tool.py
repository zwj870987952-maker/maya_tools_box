"""Framework adapter for bookmark trimming and six curve optimization modes."""
import math

from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


DEFAULTS = dict(action='trim', objects=None, layer='auto', scope='all', mode='smooth',
                strength=0.5, bias=0.5, include_translate=True, include_rotate=True,
                include_scale=False, include_others=False, channel_box_priority=True,
                ensure_keys_at_bounds=False, ease_bounds=True)
BOOLS = ('include_translate', 'include_rotate', 'include_scale', 'include_others',
         'channel_box_priority', 'ensure_keys_at_bounds', 'ease_bounds')
CHANNELS = BOOLS[:5]
MODES = ('smooth', 'simplify', 'multikey_ease', 'ease', 'tangents', 'smart')


def normalize(arguments):
    unknown = set(arguments) - set(DEFAULTS)
    if unknown:
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(unknown)))
    result = dict(DEFAULTS, **arguments)
    for name, choices in [('action', ('trim', 'optimize')), ('scope', ('all', 'playback', 'selected')), ('mode', MODES)]:
        if result[name] not in choices:
            raise ValueError('Invalid ' + name)
    if not isinstance(result['layer'], str) or not result['layer'].strip():
        raise ValueError('layer must be a non-empty name or auto')
    objects = result['objects']
    if isinstance(objects, str):
        objects = [objects]
    if objects is not None and (not isinstance(objects, list) or not objects or
                               any(not isinstance(o, str) or not o.strip() for o in objects)):
        raise ValueError('objects must be null, a node name, or a non-empty array of names')
    result['objects'] = objects
    for name in BOOLS:
        if type(result[name]) is not bool:
            raise ValueError(name + ' must be boolean')
    for name in ('strength', 'bias'):
        value = result[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(name + ' must be finite and in [0, 1]')
    return result


class AnimLayerBookmarkTrimmerTool(BaseMayaTool):
    tool_id = 'anim_layer_bookmark_trimmer'
    tool_name = '动画层书签修剪与曲线优化器'
    category = 'Animation'
    version = '1.1.0'
    description = '按时间滑块书签修剪一个动画层的关键帧，或在书签区间内进行六种曲线优化。范围外插值可能因切线变化而改变。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'action': {'type': 'string', 'enum': ['trim', 'optimize'], 'default': 'trim'},
            'objects': {'anyOf': [{'type': 'null'}, {'type': 'string', 'minLength': 1},
                                   {'type': 'array', 'minItems': 1, 'items': {'type': 'string', 'minLength': 1}}], 'default': None},
            'layer': {'type': 'string', 'minLength': 1, 'default': 'auto'},
            'scope': {'type': 'string', 'enum': ['all', 'playback', 'selected'], 'default': 'all',
                      'description': 'playback/selected选择相交书签，不裁切书签；selected光标不在书签时沿用最近书签。'},
            'mode': {'type': 'string', 'enum': list(MODES), 'default': 'smooth'},
            'strength': {'type': 'number', 'minimum': 0, 'maximum': 1, 'default': 0.5},
            'bias': {'type': 'number', 'minimum': 0, 'maximum': 1, 'default': 0.5},
            **{name: {'type': 'boolean', 'default': DEFAULTS[name]} for name in BOOLS},
        },
    }

    def _prepare(self, kwargs):
        from . import operations as op
        cmds = op.cmds
        args = normalize(kwargs)
        op.ensure_bookmark_plugin()
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('Enable Maya Undo before running this tool')
        source_objects = args['objects'] if args['objects'] is not None else (cmds.ls(selection=True, long=True) or [])
        objects = []
        for obj in source_objects:
            matches = cmds.ls(obj, long=True) or []
            if len(matches) != 1 or '.' in matches[0]:
                raise ValueError('Object must resolve to one node: ' + obj)
            node = matches[0]
            if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
                raise ValueError('Referenced or locked object: ' + node)
            if node not in objects:
                objects.append(node)
        if not objects:
            raise ValueError('Select animated objects or provide objects')
        args['objects'] = objects
        args['layer'] = op.get_active_anim_layer() if args['layer'] == 'auto' else args['layer']
        layers = cmds.ls(type='animLayer') or []
        if args['layer'] not in layers and not (args['layer'] == 'BaseAnimation' and not layers):
            raise ValueError('Unknown animation layer: ' + args['layer'])
        if args['layer'] in layers:
            if cmds.animLayer(args['layer'], query=True, lock=True) or cmds.referenceQuery(args['layer'], isNodeReferenced=True):
                raise ValueError('Animation layer is locked or referenced')
        bookmarks, description = op.get_filtered_bookmarks(args['scope'])
        if not bookmarks:
            raise ValueError('No bookmarks in scope: ' + description)
        for bm in bookmarks:
            if not all(math.isfinite(bm[k]) for k in ('start', 'stop')):
                raise ValueError('Non-finite bookmark range')
        if args['action'] == 'optimize':
            prior_stop = None
            for bm in bookmarks:
                if bm['stop'] - bm['start'] <= 0.002:
                    raise ValueError('Optimization requires bookmark duration > 0.002 frames')
                if prior_stop is not None and bm['start'] < prior_stop - 0.001:
                    raise ValueError('Overlapping bookmarks must be separated before optimization')
                prior_stop = bm['stop']
        curves = op.get_layer_curves_for_objects(objects, args['layer'], **{k: args[k] for k in CHANNELS})
        if not curves:
            raise ValueError('No matching continuous animation curves on the selected layer')
        for curve in curves:
            if cmds.referenceQuery(curve, isNodeReferenced=True) or any(cmds.lockNode(curve, query=True, lock=True)) or cmds.getAttr(curve + '.ktv', lock=True):
                raise ValueError('Animation curve is locked or referenced: ' + curve)
            if len(cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []) != 1:
                raise ValueError('Curve must have exactly one driven connection: ' + curve)
            values = cmds.keyframe(curve, query=True, valueChange=True) or []
            times = cmds.keyframe(curve, query=True, timeChange=True) or []
            if not all(math.isfinite(x) for x in times + values):
                raise ValueError('Non-finite key data: ' + curve)
        return args, curves, bookmarks

    @staticmethod
    def _invoke(args, dry_run):
        from . import operations as op
        args = dict(args)
        action = args.pop('action')
        if action == 'trim':
            for name in ('mode', 'strength', 'bias', 'ease_bounds'):
                args.pop(name)
            return op.trim_layer_keyframes_by_bookmarks(dry_run=dry_run, **args)
        args.pop('ensure_keys_at_bounds')
        return op.optimize_layer_curves_by_bookmarks(dry_run=dry_run, **args)

    def validate(self, **kwargs):
        try:
            args, curves, bookmarks = self._prepare(kwargs)
            report = self._invoke(args, True)
            return ToolResult(success=report['success'], message=report['message'],
                              data=dict(report, curves=curves, bookmarks=bookmarks), dry_run=True,
                              warnings=['优化可修改端点切线和整曲线 weightedTangents；范围外插值不保证不变。'] if args['action'] == 'optimize' else [])
        except Exception as error:
            return ToolResult.fail('预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args, curves, bookmarks = self._prepare(kwargs)
        report = self._invoke(args, False)
        return ToolResult(success=report['success'], message=report['message'],
                          data=dict(report, curves=curves, bookmarks=bookmarks),
                          warnings=['失败不会自动回滚；如遇异常，检查结果并使用 Maya Undo。'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(self)
