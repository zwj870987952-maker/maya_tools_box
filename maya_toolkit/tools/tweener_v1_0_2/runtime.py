from contextlib import contextmanager
from pathlib import Path
from maya import cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

ACTIVE = None
LAST = None
PREVIEW = False
PROGRESS = set()
PLUGIN = Path(__file__).resolve().parent / 'native/staging_tweener_plugin.py'


def libraries():
    from .native.mods import utils, animdata, tween, options, animlayers
    return utils, animdata, tween, options, animlayers


def node(name):
    selection = om.MSelectionList()
    selection.add(name)
    return om.MFnDependencyNode(selection.getDependNode(0))


def identity(name):
    return cmds.ls(name, uuid=True)[0]


def editable(name):
    if cmds.referenceQuery(name, isNodeReferenced=True) or any(cmds.lockNode(name, query=True, lock=True)):
        raise ValueError('Referenced/locked node: ' + name)


def targets(curve):
    pending = cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
    found, seen = [], set()
    while pending:
        plug = pending.pop()
        if plug in seen:
            continue
        seen.add(plug)
        name = plug.split('.')[0]
        editable(name)
        if cmds.getAttr(plug, lock=True):
            raise ValueError('Locked target plug: ' + plug)
        kind = cmds.nodeType(name)
        if cmds.objectType(name, isAType='dagNode'):
            found.append(plug)
        elif kind.startswith('animBlend'):
            for layer in cmds.listConnections(name, type='animLayer') or []:
                if cmds.getAttr(layer + '.lock'):
                    raise ValueError('Locked animation layer in output graph')
            pending.extend(cmds.listConnections(name + '.output', source=False, destination=True, plugs=True) or [])
        elif kind == 'unitConversion':
            pending.extend(cmds.listConnections(name + '.output', source=False, destination=True, plugs=True) or [])
        else:
            raise ValueError('Unsupported downstream graph: ' + kind)
    if not found or len(set(found)) != 1:
        raise ValueError('Curve must affect one uniquely scoped editable DAG attribute')
    return sorted(set(found))


def plan(p, gui=False):
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before editing keys')
    if p['action'] == 'activate_tool':
        if cmds.about(batch=True):
            raise ValueError('Interactive Maya required for mouse tool')
        return {'action': 'activate_tool', 'parameters': p, 'gui_acceptance': 'not_run'}
    utils, _, _, _, _ = libraries()
    graph = gui and not cmds.about(batch=True) and utils.is_graph_editor()
    allowed = None
    if 'curves' in p:
        names = p['curves']
    elif graph:
        names = [str(n.name()) for n in utils.get_selected_anim_curves()]
    else:
        objects = p.get('objects', cmds.ls(selection=True, long=True) or [])
        resolved = []
        for value in objects:
            match = cmds.ls(value, long=True) or []
            if len(match) != 1 or '.' in value or not cmds.objectType(match[0], isAType='dagNode'):
                raise ValueError('Select/supply unique whole DAG objects')
            editable(match[0])
            resolved.append(match[0])
        if not resolved or len(set(resolved)) != len(resolved):
            raise ValueError('No unique animation objects')
        allowed = {identity(n) for n in resolved}
        curve_nodes, _ = utils.get_anim_curves_from_objects([node(n) for n in resolved])
        names = [str(n.name()) for n in curve_nodes]
    if not names:
        raise ValueError('No supported time animation curves in scope')
    if gui and 'time_range' not in p:
        time_range = list(utils.get_time_slider_range())
    else:
        time_range = p.get('time_range', [cmds.currentTime(query=True)] * 2)
    rows = []
    for value in dict.fromkeys(names):
        match = cmds.ls(value, long=True) or []
        if len(match) != 1 or cmds.nodeType(match[0]) not in ('animCurveTA', 'animCurveTL', 'animCurveTU', 'animCurveTT'):
            raise ValueError('Supply unique supported time curves')
        curve = match[0]
        editable(curve)
        outgoing = targets(curve)
        if allowed is not None and any(identity(x.split('.')[0]) not in allowed for x in outgoing):
            raise ValueError('Curve affects an object outside the explicit selection')
        incoming = cmds.listConnections(curve + '.input', source=True, destination=False, plugs=True) or []
        if incoming and (len(incoming) != 1 or cmds.nodeType(incoming[0].split('.')[0]) != 'time' or incoming[0].split('.')[-1] not in ('outTime', 'unwarpedTime')):
            raise ValueError('Unsupported time warp/driver')
        times = cmds.keyframe(curve, query=True, timeChange=True) or []
        if not times:
            raise ValueError('Empty curve is unsupported')
        selected = p.get('key_indices', {}).get(value)
        if gui and 'key_indices' not in p:
            selected = cmds.keyframe(curve, query=True, selected=True, indexValue=True)
        if selected and any(i >= len(times) for i in selected):
            raise ValueError('Key index exceeds curve key count')
        if 'key_indices' in p and selected is None:
            raise ValueError('Supply key_indices for every scoped curve')
        if p['action'] == 'tween' and time_range[0] == time_range[1] and not selected and not times[0] <= time_range[0] <= times[-1]:
            raise ValueError('Current frame outside keyed range; original endpoint insertion is unsafe')
        rows.append({'curve': curve, 'uuid': identity(curve), 'targets': outgoing, 'selected_indices': sorted(selected) if selected else None, 'key_count': len(times), 'insert_at_current': p['action'] == 'tween' and time_range[0] == time_range[1] and not selected and time_range[0] not in times})
    indices = p.get('key_indices', {})
    if set(indices) - set(names):
        raise ValueError('key_indices contains a curve outside scope')
    return {'action': p['action'], 'curves': rows, 'time_range': time_range, 'parameters': p, 'gui_acceptance': 'not_run', 'engine': 'full original five-mode API2 algorithms/animation-layer choice', 'undo': 'private original MPxCommand + MAnimCurveChange; Base UndoChunk alone cannot undo API edits'}


@contextmanager
def scope(data):
    global ACTIVE
    previous = ACTIVE
    ACTIVE = data
    try:
        yield
    finally:
        ACTIVE = previous


@contextmanager
def native_context(action='tween'):
    global LAST
    from .tool import normalize
    data = ACTIVE or plan(normalize(action=action), gui=True)
    LAST = data
    with scope(data):
        yield


def scoped_curves():
    return [node(row['curve']) for row in ACTIVE['curves']]


def scoped_plugs():
    result = []
    for row in ACTIVE['curves']:
        sl = om.MSelectionList()
        sl.add(row['targets'][0])
        result.append(sl.getPlug(0))
    return result


def selected_indices(curve):
    if ACTIVE is not None:
        return next(row['selected_indices'] for row in ACTIVE['curves'] if row['uuid'] == identity(curve))
    return cmds.keyframe(curve, query=True, selected=True, indexValue=True)


def guard_cached():
    if not LAST:
        raise RuntimeError('No prepared tween cache')
    _, animdata, _, _, _ = libraries()
    expected = {row['uuid'] for row in LAST['curves']}
    actual = set()
    for fn in animdata.curve_key_values:
        name = str(fn.name())
        editable(name)
        actual.add(identity(name))
        old = next((r for r in LAST['curves'] if r['uuid'] == identity(name)), None)
        if old is None or targets(name) != old['targets']:
            raise RuntimeError('Cached curve ownership/output changed during drag')
    if actual - expected:
        raise RuntimeError('Stale curve cache; cancel preview')


def load_plugin():
    name = PLUGIN.name
    if cmds.pluginInfo(name, query=True, registered=True):
        loaded_path = Path(cmds.pluginInfo(name, query=True, path=True)).resolve()
        if loaded_path != PLUGIN.resolve():
            raise RuntimeError('Foreign private Tweener plugin; restart Maya')
        if not cmds.pluginInfo(name, query=True, loaded=True):
            cmds.loadPlugin(str(PLUGIN), quiet=True)
    else:
        if hasattr(cmds, 'stagingTweener'):
            raise RuntimeError('Conflicting private command registered elsewhere')
        cmds.loadPlugin(str(PLUGIN), quiet=True)


def begin_preview(blend, mode):
    global PREVIEW, LAST
    from .tool import normalize, MODES
    cancel_preview()
    data = plan(normalize(mode=MODES[mode], blend=blend), gui=True)
    utils, animdata, tween, options, _ = libraries()
    LAST = data
    animdata.anim_cache = oma.MAnimCurveChange()
    PREVIEW = True
    try:
        with scope(data):
            animdata.prepare(options.BlendingMode.get_mode_from_id(mode))
            tween.interpolate(blend, options.BlendingMode.get_mode_from_id(mode))
    except Exception:
        cancel_preview()
        raise


def finish_preview():
    global PREVIEW
    PREVIEW = False


def cancel_preview():
    global PREVIEW
    if PREVIEW:
        _, animdata, _, _, _ = libraries()
        try:
            if animdata.anim_cache is not None:
                animdata.anim_cache.undoIt()
        finally:
            PREVIEW = False
            animdata.curve_key_values = {}
            animdata.anim_cache = None


def tick(data, special):
    for row in data['curves']:
        if row['selected_indices'] is not None:
            for i in row['selected_indices']:
                cmds.keyframe(row['curve'], edit=True, index=(i, i), tickDrawSpecial=special)
        else:
            cmds.keyframe(row['curve'], edit=True, time=tuple(data['time_range']), tickDrawSpecial=special)


def progress(control, **kwargs):
    if control is None:
        return False
    if kwargs.get('beginProgress'):
        PROGRESS.add(control)
    if kwargs.get('endProgress'):
        PROGRESS.discard(control)
    return cmds.progressBar(control, **kwargs)


def selected_times():
    if ACTIVE is None:
        return cmds.keyframe(query=True, selected=True, timeChange=True)
    result = []
    selected = False
    for row in ACTIVE['curves']:
        if row['selected_indices'] is not None:
            selected = True
            for i in row['selected_indices']:
                result.extend(cmds.keyframe(row['curve'], query=True, index=(i, i), timeChange=True) or [])
    return result if selected else None


def native_command(action):
    def decorate(function):
        def invoke(command, args):
            global PREVIEW
            if action == 'tween':
                parsed = om.MArgParser(command.syntax(), args)
                if parsed.numberOfFlagsUsed == 0:
                    return function(command, args)
                new_cache = not parsed.isFlagSet('-nc') or parsed.flagArgumentBool('-nc', 0)
                if not new_cache and not PREVIEW:
                    raise RuntimeError('A cached command requires an active uncommitted preview')
                if new_cache and PREVIEW:
                    cancel_preview()
            with native_context(action):
                try:
                    result = function(command, args)
                    if action == 'keyhammer' and not getattr(command, '_operation_success', True):
                        raise RuntimeError('Keyhammer cancelled')
                except Exception:
                    if getattr(command, 'anim_cache', None) is not None:
                        command.anim_cache.undoIt()
                    PREVIEW = False
                    raise
                finally:
                    if action == 'keyhammer':
                        for control in list(PROGRESS):
                            progress(control, edit=True, endProgress=True)
                finish_preview()
                return result
        return invoke
    return decorate
