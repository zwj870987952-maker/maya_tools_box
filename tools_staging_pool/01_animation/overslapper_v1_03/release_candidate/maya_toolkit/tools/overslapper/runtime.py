"""Exact scene scopes for full native algorithms, explicit layers and restored context."""
from contextlib import contextmanager
import json
import math
from pathlib import Path
import os
import re
import tempfile
import uuid
import maya.cmds as cmds
from maya_toolkit.framework.models import ToolResult
from .settings import validate_preset

_ACTIVE = None
_WIDGET = None
_PROGRESS = None
WARNINGS = ['未经真实 Maya GUI 验收；视觉结果及版本兼容待用户确认。', '上游 EULA 限制修改与再分发；本地候选不构成授权，禁止发布。']


def native():
    from .native.packages import overlap_package
    return overlap_package


def node(name, transform=True):
    found = cmds.ls(name, long=True) or []
    if len(found) != 1 or '.' in name:
        raise ValueError('Node must identify one whole object: ' + name)
    name = found[0]
    if transform and cmds.nodeType(name) != 'transform':
        raise ValueError('Only transform controls supported: ' + name)
    if transform and len(cmds.ls(name, allPaths=True, long=True) or []) != 1:
        raise ValueError('Instanced controls not supported: ' + name)
    return name


def mutable(name):
    if cmds.referenceQuery(name, isNodeReferenced=True) or any(cmds.lockNode(name, q=True, lock=True) or []):
        raise ValueError('Referenced/locked destination refused: ' + name)


def winds():
    found = []
    for n in cmds.ls(type='transform', long=True) or []:
        if cmds.attributeQuery('overslapper_tag', node=n, exists=True) and cmds.getAttr(n + '.overslapper_tag') == 'wind':
            if not all(cmds.attributeQuery(a, node=n, exists=True) for a in ('wind', 'wind_strength')):
                raise ValueError('Incomplete wind control: ' + n)
            strength = cmds.getAttr(n + '.wind_strength')
            if type(strength) not in (int, float) or not math.isfinite(strength):
                raise ValueError('Invalid wind strength: ' + n)
            found.append(n)
    return sorted(set(found))


def ordered(targets, order):
    # Resolve long paths for identity; original natural-name sorting acts on leaf names.
    def natural(text):
        return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', text)]
    if order == 'selection':
        return [targets[:]]
    if order == 'name':
        return [sorted(targets, key=lambda x: natural(x.rsplit('|', 1)[-1]))]
    groups = {}
    for n in targets:
        leaf = n.rsplit('|', 1)[-1]
        ns, _, bare = leaf.rpartition(':')
        key = n.rsplit('|', 1)[0] + '|' + ns + ':' + re.split(r'\d', bare, maxsplit=1)[0]
        groups.setdefault(key, []).append(n)
    return [sorted(groups[k], key=lambda x: natural(x.rsplit('|', 1)[-1])) for k in sorted(groups, key=natural)]


def source_nodes(plug):
    todo = list(cmds.listConnections(plug, s=True, d=False, p=True) or [])
    seen, result = set(), set()
    while todo:
        p = todo.pop()
        n = p.split('.', 1)[0]
        if n in seen:
            continue
        seen.add(n)
        t = cmds.nodeType(n)
        if t.startswith('animCurve'):
            if t not in ('animCurveTA', 'animCurveTL', 'animCurveTU'):
                raise ValueError('Driven-key curve refused: ' + p)
            result.add(n)
            drivers = cmds.listConnections(n + '.input', s=True, d=False) or []
            if any(cmds.nodeType(d) != 'time' for d in drivers):
                raise ValueError('Curve input is not Maya time: ' + p)
        elif t.startswith('animBlendNode') or t == 'unitConversion':
            result.add(n)
            todo.extend(cmds.listConnections(n, s=True, d=False, p=True) or [])
        elif t in ('animLayer', 'time'):
            continue
        else:
            raise ValueError('Connected driver/constraint refused: ' + p)
    return result


def layer_curve(layer, plug):
    value = cmds.animLayer(layer, q=True, findCurveForPlug=plug)
    if isinstance(value, (list, tuple)):
        if len(value) > 1:
            raise ValueError('Multiple destination curves for ' + plug)
        return value[0] if value else None
    return value or None


def prepare(o):
    action = o['action']
    if action in ('overlap', 'create_wind', 'set_winds') and not cmds.undoInfo(q=True, state=True):
        raise ValueError('Enable Maya Undo before scene writes')
    plan = {'action': action, 'warnings': WARNINGS[:], 'scene_write': action in ('overlap', 'create_wind', 'set_winds'), 'external_file_write': action == 'write_preset'}
    if action in ('open_ui', 'close_ui'):
        if cmds.about(batch=True):
            raise ValueError('Native GUI requires interactive Maya; standalone is not GUI acceptance')
        return plan
    if action in ('read_preset', 'write_preset'):
        path = Path(o['preset_path']).expanduser().resolve()
        if path.suffix.lower() != '.json' or not path.parent.is_dir() or path.is_dir():
            raise ValueError('Preset path must be JSON in existing directory')
        if action == 'read_preset':
            plan['preset_data'] = read_preset(path)
        elif path.exists() and not o['overwrite']:
            raise ValueError('Preset already exists; overwrite=True required')
        plan['preset_path'] = str(path)
        plan['file_signature'] = file_signature(path)
        return plan
    all_winds = winds()
    chosen = all_winds if o['winds'] is None else [node(n) for n in o['winds']]
    if len(chosen) != len(set(chosen)) or set(chosen) - set(all_winds):
        raise ValueError('winds must resolve to unique tagged wind controls')
    plan['winds'] = chosen
    if action == 'inspect':
        plan.update({'layers': cmds.ls(type='animLayer') or [], 'selection': cmds.ls(sl=True, long=True) or [], 'playback_range': [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]})
        return plan
    if action == 'create_wind':
        return plan
    if action in ('set_winds', 'select_winds'):
        if not chosen:
            raise ValueError('No wind controls')
        if action == 'set_winds':
            for n in chosen:
                mutable(n)
                if cmds.getAttr(n + '.wind', lock=True) or cmds.listConnections(n + '.wind', s=True, d=False):
                    raise ValueError('Wind enable plug is locked/connected: ' + n)
        return plan
    targets = [node(n) for n in (o['targets'] if o['targets'] is not None else (cmds.ls(sl=True, long=True) or []))]
    if not targets or len(targets) != len(set(targets)) or len(targets) > 500:
        raise ValueError('Require 1..500 unique transform controls')
    r = o['frame_range']
    if r is None:
        r = [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
        if any(v != int(v) for v in r):
            raise ValueError('Fractional playback boundaries require explicit integer frame_range')
        r = [int(v) for v in r]
    if r[1] <= r[0] or r[1] - r[0] > 20000 or max(abs(v) for v in r) > 1000000 or (r[1] - r[0] + 1) * len(targets) > 200000:
        raise ValueError('Frame/target sample budget exceeded')
    groups = ordered(targets, o['order'])
    s = o['stiffness_values']
    if s is not None and ([len(g) for g in s] != [len(g) for g in groups]):
        raise ValueError('stiffness_values must match resolved sorted groups')
    attrs = [('r' if o['mode'] == 'rotation' else 't') + a for a in o['axes']]
    layer = o['target_layer']
    if layer:
        layer = node(layer, transform=False)
        if cmds.nodeType(layer) != 'animLayer' or layer == cmds.animLayer(q=True, root=True):
            raise ValueError('target_layer must be a non-base animLayer')
        mutable(layer)
        if cmds.animLayer(layer, q=True, lock=True) or cmds.animLayer(layer, q=True, mute=True):
            raise ValueError('Locked/muted target layer refused')
    all_sources, graph_by_plug = set(), {}
    for n in targets:
        mutable(n)
        if o['mode'] == 'rotation':
            # Parent-axis/joint orientation business is not silently approximated.
            if any(abs(v) > 1e-8 for v in cmds.getAttr(n + '.rotateAxis')[0]):
                raise ValueError('Nonzero rotateAxis unsupported: ' + n)
        for attr in attrs:
            plug = n + '.' + attr
            if cmds.getAttr(plug, lock=True) or cmds.getAttr(n + ('.rotate' if attr[0] == 'r' else '.translate'), lock=True):
                raise ValueError('Locked chosen channel: ' + plug)
            connected = source_nodes(plug) | source_nodes(n + ('.rotate' if attr[0] == 'r' else '.translate'))
            if not layer and not o['new_layer'] and any(cmds.nodeType(c).startswith('animBlendNode') for c in connected):
                raise ValueError('Layered channel requires explicit target_layer/new_layer: ' + plug)
            graph_by_plug[plug] = sorted(connected)
            all_sources.update(connected)
    # Refuse shared curves feeding another object/driver graph: deleting their keys would change it.
    for c in all_sources:
        if cmds.nodeType(c).startswith('animCurve'):
            mutable(c)
            for out in cmds.listConnections(c + '.output', s=False, d=True, p=True) or []:
                dest = out.split('.', 1)[0]
                canonical = (cmds.ls(dest, long=True) or [dest])[0]
                if canonical in targets:
                    long_attr = out.split('.', 1)[1]
                    short_attr = cmds.attributeQuery(long_attr, node=canonical, shortName=True)
                    if short_attr not in attrs:
                        raise ValueError('Curve also drives unchosen channel: ' + out)
                elif dest not in all_sources:
                    raise ValueError('Shared animation curve destination refused: ' + out)
    parent = node(o['remove_parent']) if o['remove_parent'] else None
    active_winds = [n for n in chosen if cmds.getAttr(n + '.wind')]
    if o['wind'] and not active_winds:
        raise ValueError('Wind requested but no enabled scoped wind control')
    if not cmds.undoInfo(q=True, state=True):
        raise ValueError('Enable Maya Undo before scene writes')
    plan.update(targets=targets, uuids={n: cmds.ls(n, uuid=True)[0] for n in targets}, groups=groups, frame_range=r, attrs=attrs, target_layer=layer, new_layer=o['new_layer'], remove_parent=parent, source_graph=graph_by_plug, sample_count=len(targets) * (r[1] - r[0] + 1))
    if o['overshoot']:
        plan['warnings'].append('原过冲算法可在结束帧后生成衰减关键帧；仅写入所选通道。')
    if o['animation_type'] == 'deleteall':
        plan['warnings'].append('deleteall 删除目标通道/目标层全部时间的键。')
    return plan


def file_signature(path):
    if not path.exists():
        return None
    s = path.stat()
    return [s.st_size, s.st_mtime_ns, s.st_ino]


def read_preset(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 1000000:
        raise ValueError('Preset must be a JSON file <=1MB')
    return validate_preset(json.loads(path.read_text(encoding='utf-8-sig')))


@contextmanager
def context(plan):
    global _ACTIVE
    if _ACTIVE is not None:
        raise ValueError('Reentrant native execution refused')
    state = dict(time=cmds.currentTime(q=True), selection=cmds.ls(sl=True, long=True) or [], auto=cmds.autoKeyframe(q=True, state=True), namespace=cmds.namespaceInfo(currentNamespace=True), layers={l: [cmds.animLayer(l, q=True, selected=True), cmds.animLayer(l, q=True, preferred=True)] for l in cmds.ls(type='animLayer') or []})
    _ACTIVE = dict(plan, owned=set(), layer=plan.get('target_layer'))
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        yield _ACTIVE
    finally:
        _ACTIVE = None
        errors = []
        calls = [lambda: cmds.currentTime(state['time']), lambda: cmds.select(state['selection'], r=True) if state['selection'] else cmds.select(clear=True), lambda: cmds.autoKeyframe(state=state['auto']), lambda: cmds.namespace(setNamespace=state['namespace'])]
        for l in set(cmds.ls(type='animLayer') or []) - set(state['layers']):
            calls.append(lambda l=l: cmds.animLayer(l, e=True, selected=False, preferred=False))
        for l, flags in state['layers'].items():
            calls.append(lambda l=l, flags=flags: cmds.animLayer(l, e=True, selected=flags[0], preferred=flags[1]) if cmds.objExists(l) else None)
        for f in calls:
            try:
                f()
            except Exception as error:
                errors.append(str(error))
        if errors:
            raise RuntimeError('Context restoration failed: ' + '; '.join(errors))


class NativeCommands:
    """Keep native query/UI behavior; writes only in API-created exact scene scopes."""
    def require_scope(self):
        if _ACTIVE is None:
            raise ValueError('Use OverslapperTool.run(); direct native scene writes are refused')

    def ls(self, *args, **kwargs):
        if _ACTIVE is not None:
            if kwargs.get('sl') or kwargs.get('selection'):
                return _ACTIVE.get('targets', [])[:]
            if args and isinstance(args[0], str) and args[0].endswith('.overslapper_tag'):
                return [n + '.overslapper_tag' for n in _ACTIVE['winds']] if args[0] == '*.overslapper_tag' else []
        return cmds.ls(*args, **kwargs)

    def _channels(self, targets, attr):
        self.require_scope()
        if isinstance(targets, str):
            targets = [targets]
        flat = []
        for n in targets:
            flat.extend(n if isinstance(n, list) else [n])
        if attr not in _ACTIVE.get('attrs', []):
            raise ValueError('Native write to unchosen channel refused: ' + str(attr))
        for n in flat:
            if n not in _ACTIVE.get('targets', []) or (cmds.ls(n, uuid=True) or [None])[0] != _ACTIVE['uuids'][n]:
                raise ValueError('Native write escaped exact target identity: ' + n)
        return flat

    def setKeyframe(self, targets, **kwargs):
        attr = kwargs.pop('at', kwargs.pop('attribute', None))
        flat = self._channels(targets, attr)
        if not math.isfinite(kwargs.get('v', 0)) or not math.isfinite(kwargs.get('t', 0)) or abs(kwargs.get('t', 0)) > 2000000:
            raise ValueError('Nonfinite/out-of-budget generated key')
        if _ACTIVE['layer']:
            kwargs.update(animLayer=_ACTIVE['layer'], noResolve=True)
        return cmds.setKeyframe(flat, at=attr, **kwargs)

    def _curve_edit(self, command, targets, kwargs):
        attr = kwargs.pop('at', kwargs.pop('attribute', None))
        flat = self._channels(targets, attr)
        if command == 'cutKey':
            kwargs['clear'] = True
        if not _ACTIVE['layer']:
            return getattr(cmds, command)(flat, at=attr, **kwargs)
        curves = [layer_curve(_ACTIVE['layer'], n + '.' + attr) for n in flat]
        curves = [c for c in curves if c]
        if not curves:
            return 0
        return getattr(cmds, command)(curves, **kwargs)

    def cutKey(self, targets, **kwargs):
        return self._curve_edit('cutKey', targets, kwargs)

    def scaleKey(self, targets, **kwargs):
        return self._curve_edit('scaleKey', targets, kwargs)

    def curve(self, **kwargs):
        self.require_scope()
        if _ACTIVE['action'] != 'create_wind':
            raise ValueError('Curve creation only allowed for create_wind')
        kwargs['n'] = 'mtkOverslapperWind_' + uuid.uuid4().hex[:12]
        n = cmds.curve(**kwargs)
        full = node(n)
        _ACTIVE['owned'].update([full] + (cmds.listRelatives(full, shapes=True, fullPath=True) or []))
        return full

    def _owned(self, n):
        self.require_scope()
        full = (cmds.ls(n.split('.', 1)[0], long=True) or [None])[0]
        if full not in _ACTIVE['owned']:
            raise ValueError('Write outside fresh wind nodes refused: ' + n)

    def addAttr(self, n, **kwargs):
        self._owned(n)
        return cmds.addAttr(n, **kwargs)

    def setAttr(self, p, *args, **kwargs):
        self._owned(p)
        return cmds.setAttr(p, *args, **kwargs)

    def connectAttr(self, src, dst, **kwargs):
        self._owned(src)
        self._owned(dst)
        if cmds.connectionInfo(dst, isDestination=True):
            raise ValueError('Fresh wind destination unexpectedly connected: ' + dst)
        kwargs.pop('f', None)
        kwargs.pop('force', None)
        return cmds.connectAttr(src, dst, **kwargs)

    def __getattr__(self, name):
        if name in ('delete', 'move', 'undoInfo', 'rename', 'select', 'animLayer'):
            raise ValueError('Native mutation must go through standard API: ' + name)
        return getattr(cmds, name)


mc = NativeCommands()


def dictionary(o, plan):
    return dict(selections=plan['groups'], frame_range=plan['frame_range'], main_axis=o['main_axis'], up_axis=o['up_axis'], axes=o['axes'], stiffness=[[1 - v for v in g] for g in o['stiffness_values']] if o['stiffness_values'] is not None else [[1 - o['stiffness']] * len(g) for g in plan['groups']], strength=o['strength'], translation_strength=o['frame_lag'], parent_validator=bool(plan['remove_parent']), parent_object=plan['remove_parent'] or '', distance_validator=o['distance'] is not None, distance=o['distance'] or 1, distance_only=o['distance_only'], r_overlap_ignore_t_check=o['ignore_translation'], cycle=o['cycle'], animation_type=o['animation_type'], overshoot_check=o['overshoot'], overshoot_first_validator=o['overshoot_first'], overshoot_between_validator=o['overshoot_between'], overshoot_end_validator=o['overshoot_end'], overshoot_strength=o['overshoot_strength'], overshoot_frequency=o['overshoot_frequency'], wind_check=o['wind'], wind_strength=o['wind_strength'], wind_absolute_translation=o['wind_absolute'])


def execute(o, plan):
    action = o['action']
    data = dict(plan)
    if action in ('inspect', 'read_preset'):
        return ToolResult.ok(data=data, warnings=plan['warnings'])
    if action == 'write_preset':
        path = Path(plan['preset_path'])
        if file_signature(path) != plan['file_signature']:
            raise ValueError('Preset changed after preflight')
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=str(path.parent), prefix='.overslapper_', suffix='.json', delete=False) as f:
                temp = Path(f.name)
                json.dump(o['preset_data'], f, ensure_ascii=False, indent=4)
                f.write('\n')
            if o['overwrite']:
                if file_signature(path) != plan['file_signature']:
                    raise ValueError('Preset changed while preparing export')
                os.replace(str(temp), str(path))
            else:
                os.link(str(temp), str(path))
            data['written_file'] = str(path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()
        return ToolResult.ok('预设已写入；文件不受 Maya Undo 撤回', data=data, warnings=plan['warnings'])
    if action in ('open_ui', 'close_ui'):
        from . import ui_bridge
        return ui_bridge.open_close(action, plan)
    if action == 'select_winds':
        cmds.select(plan['winds'], r=True)
        return ToolResult.ok(data=data, warnings=plan['warnings'])
    with context(plan) as scope:
        if action == 'create_wind':
            n = native().create_wind_control()
            cmds.addAttr(n, ln='mayaToolkitOverslapper', dt='string')
            cmds.setAttr(n + '.mayaToolkitOverslapper', 'candidate.1', type='string')
            data['created_wind'] = n
        elif action == 'set_winds':
            for n in plan['winds']:
                cmds.setAttr(n + '.wind', o['enabled'])
            data['enabled'] = o['enabled']
        else:
            layer = plan['target_layer']
            if o['new_layer']:
                layer = cmds.animLayer('mtkOverslapperLayer_' + uuid.uuid4().hex[:12], override=o['override'])
                data['created_layer'] = layer
                scope['layer'] = layer
            if layer:
                for l in cmds.ls(type='animLayer') or []:
                    cmds.animLayer(l, e=True, selected=l == layer, preferred=l == layer)
                for n in plan['targets']:
                    for attr in plan['attrs']:
                        cmds.animLayer(layer, e=True, attribute=n + '.' + attr)
                data['written_layer'] = layer
            business = native()
            worker = business.overlap_worker() if o['mode'] == 'rotation' else business.overlap_translation_worker()
            if _PROGRESS is not None:
                worker.progress_signal.connect(_PROGRESS)
            d = dictionary(o, plan)
            elapsed = worker.overlap(d) if o['mode'] == 'rotation' else worker.overlap_translation(d)
            data['native_elapsed_seconds'] = elapsed
    return ToolResult.ok('Overslapper 操作完成；场景写入可用一次 Undo 撤回', data=data, warnings=plan['warnings'])


def run_api(**kwargs):
    from .tool import OverslapperTool
    return OverslapperTool().run(**kwargs)
