import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['tween', 'keyhammer', 'tick', 'activate_tool']
MODES = ['between', 'towards', 'average', 'curve', 'default']


def normalize(**kwargs):
    if set(kwargs) - {'action', 'objects', 'curves', 'time_range', 'key_indices', 'blend', 'mode', 'special'}:
        raise ValueError('Unknown arguments')
    p = dict(action='tween', blend=0., mode='between', special=True)
    p.update(kwargs)
    if p['action'] not in ACTIONS or p['mode'] not in MODES or type(p['special']) is not bool:
        raise ValueError('Invalid action/mode/special')
    if type(p['blend']) not in (int, float) or not math.isfinite(p['blend']) or not -2 <= p['blend'] <= 2:
        raise ValueError('blend must be finite in -2..2 (overshoot included)')
    if 'objects' in p and 'curves' in p:
        raise ValueError('Supply objects or curves, not both')
    for key in ('objects', 'curves'):
        if key in p and (not isinstance(p[key], list) or not p[key] or len(p[key]) != len(set(p[key])) or any(not isinstance(n, str) or not n for n in p[key])):
            raise ValueError('Supply nonempty unique names')
    if 'time_range' in p:
        r = p['time_range']
        if not isinstance(r, list) or len(r) != 2 or any(type(t) not in (int, float) or not math.isfinite(t) for t in r) or r[0] > r[1]:
            raise ValueError('time_range requires finite inclusive [start,end]')
    if 'key_indices' in p:
        if 'time_range' in p or not isinstance(p['key_indices'], dict) or any(not isinstance(k, str) or not isinstance(v, list) or not v or any(type(i) is not int or i < 0 for i in v) or len(v) != len(set(v)) for k, v in p['key_indices'].items()):
            raise ValueError('key_indices requires curve-name -> unique nonnegative indices, without time_range')
    if p['action'] == 'activate_tool' and set(kwargs) - {'action'}:
        raise ValueError('Mouse tool reads its full original GUI preferences; action only')
    return p


def preflight(p, gui=False):
    from . import runtime
    return runtime.plan(p, gui=gui)


class TweenerTool(BaseMayaTool):
    tool_id = 'tweener_v1_0_2'
    tool_name = 'Tweener 1.0.2 完整插值'
    category = 'animation'
    version = '1.0.2-candidate.1'
    description = 'Complete five-mode original Tweener API2 algorithm, animation-layer choice, curve tangent Bézier interpolation, keyhammer, key tick styling and full dockable UI/mouse preview. Uses original MPxCommand/MAnimCurveChange for scene Undo.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'tween'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'uniqueItems': True}, 'curves': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'uniqueItems': True}, 'time_range': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 2, 'maxItems': 2}, 'key_indices': {'type': 'object', 'additionalProperties': {'type': 'array', 'items': {'type': 'integer', 'minimum': 0}, 'uniqueItems': True, 'minItems': 1}}, 'blend': {'type': 'number', 'minimum': -2, 'maximum': 2, 'default': 0}, 'mode': {'type': 'string', 'enum': MODES, 'default': 'between'}, 'special': {'type': 'boolean', 'default': True}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='Read-only complete Tweener preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from maya import cmds
        from . import runtime
        p = normalize(**kwargs)
        if runtime.PREVIEW:
            raise RuntimeError('Release or cancel the active mouse/slider preview before another API action')
        data = preflight(p)
        runtime.load_plugin()
        if p['action'] == 'activate_tool':
            cmds.stagingTweenerTool()
        elif p['action'] == 'tick':
            runtime.tick(data, p['special'])
        else:
            with runtime.scope(data):
                if p['action'] == 'tween':
                    cmds.stagingTweener(t=p['blend'], newCache=True, type=MODES.index(p['mode']))
                else:
                    result = cmds.stagingKeyHammer()
                    if not result:
                        return ToolResult.fail(message='Keyhammer cancelled and original API changes rolled back', errors=['cancelled'])
        return ToolResult.ok(message='Tweener action complete', data=data, warnings=['Private plugin registration, UI preferences, dragger contexts and tick colors are separate from scene Undo', 'Real GUI/live preview and production layer acceptance still not_run'])

    def show_ui(self, parent=None):
        from maya import cmds
        if cmds.about(batch=True):
            raise RuntimeError('Real interactive Maya required for complete Tweener UI')
        from . import runtime
        runtime.load_plugin()
        from .native.mods import ui
        return ui.TweenerUIScript()
