"""Full native MEL execution with single-session helpers and explicit destination scope."""
from contextlib import contextmanager
import ast
import hashlib
import json
import os
from pathlib import Path
import random
import re
import tempfile
import uuid
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
from maya_toolkit.framework.models import ToolResult
from .tool import CATALOG, DEFAULTS

PREFIX = 'mtkPTC_'
_ACTIVE = None
_LOADED = None
_LAST_FILES = []
_UI_VALUES = False
WARNINGS = ['完整原套件尚待真人Maya验收；离线定义编译不是运动/GUI实测。', '原资源未附独立许可，仅本地整理，不发布。', '预览助手与metadata会保留到明确cleanup_session；缓存文件不受Undo恢复。']
NO_TARGET = {'PhysicsToolsWin', 'Delete_tracking', 'GhostOptions', 'engagemode', 'ParticleOptions', 'ParticleOptionsTwo', 'Youtube', 'gumroad', 'Vimeo', 'ReportBug', 'RefeshParticleSettings', 'RefeshParticleSettingsThree', 'RefeshParticleSettings5', 'RefeshParticleSettingsTwo', 'RefeshParticleSettings4', 'RefeshParticleSettingsRotations', 'Bakeinfo', 'BakeinfoController', 'TheOptionsareBelow', 'PhysicsSettingUp', 'PointC', 'Aimcontrolerselect', 'AimDelete', 'RotationsBake', 'FinalRotationsBake', 'BakeEverything', 'cleanMAHshit', 'footPlacerDeleter', 'OffsetKeysLessSL', 'OffsetKeysMoreSL', 'LocalspaceLoccontrolerselect', 'BakeLocalspaceLoc', 'LocalspaceLocDelete', 'keyframeDy', 'keyframeDyy', 'PlayEveryframe', 'PlayNormalframe', 'CacheMe', 'BakePhysics', 'RedoMe', 'RotWorkflowSelect', 'BakeRotWork', 'SProxies', 'SProxiesSpheres', 'SProxiesCubes', 'CL', 'RedoDRW', 'Redoweapons'}
GUI_ONLY = {'PhysicsToolsWin', 'GhostSelectedtrack', 'UnghostSelectedtrack', 'UnghostAlltrack', 'GhostOptions', 'engagemode', 'Youtube', 'gumroad', 'Vimeo', 'ReportBug', 'Aim', 'Iframe', 'Rframe'}
ONE_TARGET = {'PhysicsMagicButton', 'SetupPhysics', 'SetupRotationsPhysics', 'CreateLocatorRotationsAim', 'CreateLocatorRotations', 'CreateLocatorUpVectorRotations', 'SetupRotationsXmais', 'SetupRotationsXmenos', 'SetupRotationsYmais', 'SetupRotationsYmenos', 'SetupRotationsZmais', 'SetupRotationsZmenos'}
MAX_TARGETS = {'BakeVariosControladores': 10, 'LocalspaceLoc': 11, 'SetupRotationsPhysicssmoothA': 30, 'SetupRotationsPhysicssmoothB': 20}


def object_path(obj):
    """Resolve API absolute namespace names even when MEL relativeNames is enabled."""
    if not obj.hasFn(om.MFn.kDagNode):
        return om.MFnDependencyNode(obj).absoluteName()
    path = om.MDagPath.getAPathTo(obj)
    parts = []
    while path.length():
        parts.append(om.MFnDependencyNode(path.node()).absoluteName())
        path.pop()
    return '|' + '|'.join(reversed(parts))


def idmap():
    result = {}
    it = om.MItDependencyNodes()
    while not it.isDone():
        fn = om.MFnDependencyNode(it.thisNode())
        identity = fn.uuid().asString()
        name = object_path(it.thisNode())
        result.setdefault(identity, []).append(name)
        it.next()
    return result


def identity(node):
    return cmds.ls(node.split('.', 1)[0], uuid=True)[0]


def existing_session():
    results = []
    for n in cmds.ls(type='network') or []:
        if not cmds.attributeQuery('mayaToolkitPhysicsSession', node=n, exists=True):
            continue
        if cmds.referenceQuery(n, isNodeReferenced=True):
            continue
        value = cmds.getAttr(n + '.mayaToolkitPhysicsSession')
        if not isinstance(value, str) or len(value) > 4000000:
            raise ValueError('Malformed candidate session metadata')
        data = json.loads(value)
        sid = data.get('id', '')
        if not re.fullmatch('[a-f0-9]{32}', sid) or data.get('namespace') != 'mtkPhysics_' + sid:
            raise ValueError('Session identity/namespace mismatch')
        absolute = om.MFnDependencyNode(_object(n)).absoluteName()
        if absolute != ':' + data['namespace'] + ':session':
            raise ValueError('Session marker name/provenance mismatch')
        data['marker'] = absolute
        results.append(data)
    if len(results) > 1:
        raise ValueError('More than one local candidate session; use separate scene copies')
    return results[0] if results else None


def _object(n):
    sel = om.MSelectionList()
    sel.add(n)
    return sel.getDependNode(0)


def whole(n):
    found = cmds.ls(n, long=True) or []
    if len(found) != 1:
        raise ValueError('Require unambiguous object/component: ' + n)
    base, dot, suffix = found[0].partition('.')
    return object_path(_object(base)) + (dot + suffix if dot else '')


def mutable(n, allow_reference=False):
    base = n.split('.', 1)[0]
    if any(cmds.lockNode(base, q=True, lock=True) or []) or (cmds.referenceQuery(base, isNodeReferenced=True) and not allow_reference):
        raise ValueError('Locked/referenced destination refused: ' + n)


def prepare(o):
    session = existing_session()
    proc = 'PhysicsToolsWin' if o['action'] == 'open_ui' else o['procedure']
    data = dict(action=o['action'], procedure=proc, warnings=WARNINGS[:], session=session['namespace'] if session else None)
    if o['action'] in ('inspect', 'close_ui', 'cleanup_session'):
        data.update(selection=cmds.ls(sl=True, long=True) or [], procedures=CATALOG['procedures'], owned_count=len(session.get('owned', [])) if session else 0)
        if o['action'] == 'cleanup_session' and not cmds.undoInfo(q=True, state=True):
            raise ValueError('Enable Undo before cleanup')
        return data
    if (o['action'] == 'open_ui' or proc in GUI_ONLY) and cmds.about(batch=True):
        raise ValueError('This procedure needs interactive native Maya UI')
    if o['action'] == 'open_ui':
        return data
    if not cmds.undoInfo(q=True, state=True):
        raise ValueError('Enable Undo before native execution')
    targets = [whole(n) for n in (o['targets'] if o['targets'] is not None else cmds.ls(sl=True, long=True) or [])]
    if session and proc in NO_TARGET and o['targets'] is None:
        targets = [whole(n) for n in session.get('targets', []) if cmds.objExists(n)]
    if len(targets) != len(set(targets)):
        raise ValueError('Duplicate target identities')
    if proc not in NO_TARGET and not targets:
        raise ValueError('This procedure requires a nonempty selection')
    if proc in ONE_TARGET and len(targets) != 1:
        raise ValueError('This preview setup requires one target')
    if len(targets) > MAX_TARGETS.get(proc, 100):
        raise ValueError('Original unrolled selection limit exceeded')
    if proc in ('MatchTransforms', 'MatchTranslations', 'MatchRotations', 'PCT', 'PCToff', 'PCR', 'ParentConstraintNormal', 'OrientC', 'AlignCommand', 'Tempivot') and len(targets) < 2:
        raise ValueError('Need source(s) then destination selection')
    r = o['frame_range'] or [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
    if o['frame_range'] is None and _UI_VALUES and proc in ('ruidoA', 'ruidoB', 'ruidoC'):
        slider = mel.eval('$tmpVar=$gPlayBackSlider')
        selected = cmds.timeControl(slider, q=True, rangeArray=True)
        if selected[1] - selected[0] > 1:
            r = [selected[0], selected[1] - 1]
    if any(type(v) not in (int, float) or v != int(v) or abs(v) > 1000000 for v in r) or r[1] < r[0] or r[1] - r[0] > 10000 or (r[1] - r[0] + 1) * max(1, len(targets)) > 100000:
        raise ValueError('Frame range/total sample budget exceeded')
    allowed_existing_constraints = []
    read_only = proc.startswith('tracking_') or proc in ('GhostSelectedtrack', 'UnghostSelectedtrack', 'UnghostAlltrack')
    for n in targets:
        base = n.split('.', 1)[0]
        if not read_only:
            if cmds.nodeType(base) != 'transform' and (session is None or identity(base) not in session.get('owned', [])):
                raise ValueError('Choose transform controls or own session helper nodes')
            mutable(n, o['allow_reference_edits'])
            if cmds.nodeType(base) == 'transform':
                if len(cmds.ls(base, long=True, allPaths=True) or []) != 1:
                    raise ValueError('Instanced controls unsupported')
                for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                    if cmds.getAttr(base + '.' + attr, lock=True):
                        raise ValueError('Locked transform channel: ' + base + '.' + attr)
                    inputs = cmds.listConnections(base + '.' + attr, s=True, d=False) or []
                    inputs += cmds.listConnections(base + ('.translate' if attr.startswith('t') else '.rotate'), s=True, d=False) or []
                    for upstream in set(inputs):
                        t = cmds.nodeType(upstream)
                        own = bool(session and identity(upstream) in session.get('owned', []))
                        if cmds.objectType(upstream, isAType='constraint') and proc == 'RemoveConstraints':
                            mutable(upstream, False)
                            allowed_existing_constraints.append(upstream)
                        elif t.startswith('animCurve'):
                            mutable(upstream, o['allow_reference_edits'])
                            outputs = cmds.listConnections(upstream + '.output', s=False, d=True) or []
                            if any(whole(out) != whole(base) for out in outputs):
                                raise ValueError('Shared time curve refused')
                            if t not in ('animCurveTA', 'animCurveTL', 'animCurveTU') or any(cmds.nodeType(driver) != 'time' for driver in cmds.listConnections(upstream + '.input', s=True, d=False) or []):
                                raise ValueError('Driven-key/external time driver refused')
                        elif not own:
                            raise ValueError('Existing external layer/driver/constraint refused: ' + upstream)
    if proc == 'CacheMe':
        path = Path(o['cache_directory']).resolve() if o['cache_directory'] else None
        if path is None or not path.is_dir():
            raise ValueError('CacheMe requires an explicit existing cache_directory')
        data['cache_directory'] = str(path)
    if o['allow_reference_edits']:
        data['warnings'].append('显式允许原流程产生引用编辑，保存场景时这些编辑会保留。')
    data.update(targets=targets, target_uuids={n.split('.', 1)[0]: identity(n) for n in targets}, frame_range=[int(v) for v in r], allowed_existing_constraints=list(set(allowed_existing_constraints)))
    if o['attributes']:
        for n in targets:
            for attr in o['attributes']:
                if not cmds.attributeQuery(attr, node=n.split('.', 1)[0], exists=True) or cmds.getAttr(n.split('.', 1)[0] + '.' + attr, lock=True):
                    raise ValueError('Missing/locked requested channel: ' + attr)
    return data


def active():
    return _ACTIVE is not None


def require_scope():
    if _ACTIVE is None:
        raise ValueError('Use PhysicsToolsTool.run; private native body requires API scope')
    if _ACTIVE.get('namespace') and cmds.namespaceInfo(currentNamespace=True).lstrip(':') != _ACTIVE['namespace']:
        raise ValueError('Native operation escaped private helper namespace')


def alive_owned():
    require_scope()
    current = idmap()
    owned = set(_ACTIVE.get('owned', [])) | (set(current) - _ACTIVE['baseline'])
    return {i: names[0] for i, names in current.items() if i in owned and len(names) == 1}


def _delete_check(names, owned, targets):
    for n in names:
        if identity(n) not in owned:
            raise ValueError('Refuse deleting a node not created by this candidate: ' + n)
        mutable(n)
        for child in cmds.listRelatives(n, allDescendents=True, fullPath=True) or []:
            if identity(child) not in owned:
                raise ValueError('Own helper has external child; cleanup refused: ' + child)
        for source in [n] + (cmds.listRelatives(n, allDescendents=True, fullPath=True) or []):
            for out in cmds.listConnections(source, s=False, d=True) or []:
                if cmds.nodeType(out) == 'shadingEngine' and whole(out) in (':initialParticleSE', ':initialShadingGroup'):
                    continue  # Maya's default shading membership, not a driven user destination.
                if identity(out) not in owned and whole(out) not in targets:
                    raise ValueError('Helper feeds an external user; cleanup refused: ' + out)


def scene_delete(names, owned):
    """Maya legacy particle deletion can cascade through goal connections."""
    relative = cmds.namespace(q=True, relativeNames=True)
    targets = list(dict.fromkeys(_ACTIVE.get('targets', []) + (_ACTIVE.get('metadata') or {}).get('targets', [])))
    protected = [n for n in targets if cmds.objExists(n) and identity(n) not in owned]
    locks = {n: bool(cmds.lockNode(n, q=True, lock=True)[0]) for n in protected}
    names = [n for n in names if not n.startswith('|') or not any(n.startswith(parent + '|') for parent in names if parent.startswith('|') and parent != n)]
    try:
        cmds.namespace(relativeNames=False)
        # Remove own constraints under controls before temporarily locking those controls.
        for n in names[:]:
            if cmds.objExists(n) and cmds.objectType(n, isAType='constraint'):
                cmds.delete(n)
                names.remove(n)
        for n in protected:
            cmds.lockNode(n, lock=True)
        # Avoid a legacy Maya bulk-delete dependency cycle across particles/sets/curves.
        for n in sorted(names, key=lambda n: (not n.startswith('|'), n)):
            if cmds.objExists(n):
                cmds.delete(n)
    finally:
        for n, locked in locks.items():
            if cmds.objExists(n):
                cmds.lockNode(n, lock=locked)
        cmds.namespace(relativeNames=relative)


def delete_owned(patterns, constraints=0):
    require_scope()
    owned = alive_owned()
    selection = cmds.ls(sl=True, long=True) or []
    matches = list(dict.fromkeys(whole(n) for p in (patterns or selection) for n in cmds.ls(p, long=True) or []))
    if constraints:
        controls = matches
        matches = list(set(c for n in controls for c in cmds.listConnections(n, s=True, d=False, type='constraint') or []))
        allowed = _ACTIVE.get('allowed_existing_constraints', [])
        foreign = [n for n in matches if identity(n) not in owned and n not in allowed]
        if foreign:
            raise ValueError('Refuse deleting preexisting constraints: ' + ', '.join(foreign))
        for n in matches:
            mutable(n)
            for out in cmds.listConnections(n, s=False, d=True) or []:
                if identity(out) not in owned and whole(out) not in _ACTIVE.get('targets', []):
                    raise ValueError('Constraint also serves an unselected node: ' + out)
    else:
        _delete_check(matches, owned, set(_ACTIVE.get('targets', [])))
    if matches:
        scene_delete(matches, owned)


def value(control):
    require_scope()
    original = control.removeprefix(PREFIX)
    if _UI_VALUES and cmds.floatSliderGrp(PREFIX + original, exists=True):
        return cmds.floatSliderGrp(PREFIX + original, q=True, value=True)
    key = 'overlap' if original.startswith('Goalsmooth') else 'softness' if original.startswith('Goalstiffness') else 'damping' if original.startswith('Goaldamping') else 'jiggle_weight' if original in ('GoalWeightRotations', 'GoalWeightt') else 'weight'
    return _ACTIVE['options'][key]


def helper_name(prefix, n):
    require_scope()
    leaf = n.rsplit('|', 1)[-1].split(':')[-1]
    return prefix + re.sub('[^A-Za-z0-9_]', '_', leaf) + '_' + identity(n).replace('-', '')[:8]


def load():
    global _LOADED
    path = Path(__file__).parent / 'native.mel'
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if _LOADED is not None:
        if _LOADED != digest:
            raise ValueError('MEL candidate changed after load; restart Maya before using it')
        return
    # Do not replace another candidate copy's already compiled procedures.
    if mel.eval('exists "' + PREFIX + 'Native_PhysicsToolsWin"'):
        raise ValueError('Private candidate MEL procedures already exist from another loader')
    mel.eval(path.read_text(encoding='utf-8'))
    _LOADED = digest


@contextmanager
def scope(options, plan, create_session=True):
    global _ACTIVE
    if _ACTIVE is not None:
        raise ValueError('Reentrant API mutation refused')
    session = existing_session() if create_session else None
    original = dict(time=cmds.currentTime(q=True), selection=[whole(n) for n in cmds.ls(sl=True, long=True) or []], namespace=':' + cmds.namespaceInfo(currentNamespace=True).lstrip(':'), relative=cmds.namespace(q=True, relativeNames=True), auto=cmds.autoKeyframe(q=True, state=True), playback=[cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)], speeds=[cmds.playbackOptions(q=True, playbackSpeed=True), cmds.playbackOptions(q=True, maxPlaybackSpeed=True)], refresh=cmds.refresh(q=True, suspend=True), layers={whole(l): [cmds.animLayer(l, q=True, selected=True), cmds.animLayer(l, q=True, preferred=True)] for l in cmds.ls(type='animLayer') or []})
    if create_session and session is None:
        sid = uuid.uuid4().hex
        ns = 'mtkPhysics_' + sid
        cmds.namespace(add=':' + ns)
        marker = cmds.createNode('network', name=':' + ns + ':session')
        cmds.addAttr(marker, ln='mayaToolkitPhysicsSession', dt='string')
        session = dict(id=sid, namespace=ns, marker=':' + ns + ':session', owned=[identity(marker)], targets=[], cache_files=[], cache_roots=[])
    baseline = set(idmap())
    _ACTIVE = dict(plan, options=options, baseline=baseline, owned=session.get('owned', []) if session else [], namespace=session['namespace'] if session else None, metadata=session)
    if session and not _ACTIVE.get('targets'):
        _ACTIVE['targets'] = [n for n in session.get('targets', []) if cmds.objExists(n)]
    try:
        if session:
            cmds.namespace(set=':' + session['namespace'])
            cmds.namespace(relativeNames=True)
        cmds.autoKeyframe(state=False)
        if 'frame_range' in plan:
            cmds.playbackOptions(min=plan['frame_range'][0], max=plan['frame_range'][1])
        if plan.get('targets'):
            cmds.select(plan['targets'], r=True)
        yield _ACTIVE
    finally:
        errors = []
        if session and cmds.objExists(session['marker']):
            try:
                session['owned'] = sorted(alive_owned())
                session['targets'] = list(dict.fromkeys(session.get('targets', []) + plan.get('targets', [])))
                cmds.setAttr(session['marker'] + '.mayaToolkitPhysicsSession', json.dumps({k: v for k, v in session.items() if k != 'marker'}), type='string')
            except Exception as error:
                errors.append(str(error))
        _ACTIVE = None
        restore = [lambda: cmds.namespace(relativeNames=False), lambda: cmds.namespace(set=original['namespace']), lambda: cmds.namespace(relativeNames=original['relative']), lambda: cmds.autoKeyframe(state=original['auto']), lambda: cmds.currentTime(original['time']), lambda: cmds.playbackOptions(min=original['playback'][0], max=original['playback'][1]), lambda: cmds.refresh(suspend=original['refresh'])]
        for l in {whole(l) for l in cmds.ls(type='animLayer') or []} - set(original['layers']):
            restore.append(lambda l=l: cmds.animLayer(l, e=True, selected=False, preferred=False))
        for l, flags in original['layers'].items():
            restore.append(lambda l=l, flags=flags: cmds.animLayer(l, e=True, selected=flags[0], preferred=flags[1]) if cmds.objExists(l) else None)
        if plan.get('procedure') not in ('PlayEveryframe', 'PlayNormalframe'):
            restore.append(lambda: cmds.playbackOptions(playbackSpeed=original['speeds'][0], maxPlaybackSpeed=original['speeds'][1]))
        if plan.get('procedure') not in ('ParticleOptions', 'ParticleOptionsTwo', 'LocalspaceLoccontrolerselect', 'SProxies', 'SProxiesSpheres', 'SProxiesCubes', 'RotWorkflowSelect'):
            restore.append(lambda: cmds.select([n for n in original['selection'] if cmds.objExists(n)], r=True) if original['selection'] else cmds.select(clear=True))
        for fn in restore:
            try:
                fn()
            except Exception as error:
                errors.append(str(error))
        if errors:
            raise RuntimeError('Session/context finalization failed: ' + '; '.join(errors))


def execute(o, plan):
    global _LAST_FILES
    _LAST_FILES = []
    data = dict(plan)
    if o['action'] == 'inspect':
        return ToolResult.ok(data=data, warnings=plan['warnings'])
    if o['action'] == 'close_ui':
        if cmds.window(PREFIX + 'PhysicsToolsWin', exists=True):
            cmds.deleteUI(PREFIX + 'PhysicsToolsWin', window=True)
        return ToolResult.ok('候选窗口已关闭', data=data, warnings=plan['warnings'])
    if o['action'] == 'cleanup_session' and existing_session() is None:
        return ToolResult.ok('没有候选会话需要清理', data=data, warnings=plan['warnings'])
    load()
    with scope(o, plan, create_session=o['action'] != 'open_ui') as state:
        if o['action'] == 'cleanup_session':
            owned = alive_owned()
            marker = state['metadata']['marker'] if state['metadata'] else None
            names = [n for n in owned.values() if n != marker]
            _delete_check(names, owned, set(state.get('targets', [])))
            cache(False)
            if names:
                scene_delete(names, owned)
            if marker and cmds.objExists(marker):
                cmds.delete(marker)
            data['deleted_nodes'] = names
        else:
            proc = plan['procedure']
            mel.eval(PREFIX + 'Native_' + proc + '();')
            data['owned_nodes'] = list(alive_owned().values()) if state['namespace'] else []
            data['session'] = state['namespace']
            data['cache_files'] = _LAST_FILES[:]
    return ToolResult.ok('Physics Tools 操作完成', data=data, warnings=plan['warnings'])


def ui_call(procedure):
    global _UI_VALUES
    from .tool import PhysicsToolsTool
    options = dict(action='open_ui' if procedure == 'PhysicsToolsWin' else 'invoke', procedure=procedure)
    if cmds.checkBox(PREFIX + 'AllowReferences', exists=True):
        options['allow_reference_edits'] = cmds.checkBox(PREFIX + 'AllowReferences', q=True, value=True)
    if procedure == 'CacheMe':
        chosen = cmds.fileDialog2(fileMode=3, caption='Physics Tools: owned cache parent directory')
        if not chosen:
            return {'success': False, 'message': 'Cache directory selection cancelled'}
        options['cache_directory'] = chosen[0]
    _UI_VALUES = True
    try:
        result = PhysicsToolsTool().run(**options)
        if not result.success:
            cmds.warning(result.message + ': ' + '; '.join(result.errors))
        return result.to_dict()
    finally:
        _UI_VALUES = False


def create_jiggle():
    require_scope()
    selected = cmds.ls(sl=True, long=True) or []
    own = alive_owned()
    if len(selected) != 1 or identity(selected[0]) not in own:
        raise ValueError('Jiggle may only deform the newly created candidate plane')
    # Same doJiggle 1 {...} business: actual Maya jiggle deformer plus connected diskCache.
    # Avoid doJiggle's automatic project file-rule/cache-name mutation.
    jiggle = cmds.deformer(selected[0], type='jiggle', name='jiggle1')[0]
    cmds.connectAttr(':time1.outTime', jiggle + '.currentTime')
    cache_node = cmds.createNode('diskCache', name='jiggle1Cache')
    cmds.setAttr(cache_node + '.cacheType', 'mcj', type='string')
    cmds.setAttr(cache_node + '.copyLocally', False)
    cmds.connectAttr(cache_node + '.diskCache', jiggle + '.diskCache')
    for key, value in dict(ignoreTransform=0, enable=0, stiffness=0.1, damping=0.5, jiggleWeight=0.9).items():
        cmds.setAttr(jiggle + '.' + key, value)
    return jiggle


def cache(create):
    require_scope()
    metadata = _ACTIVE['metadata']
    if metadata is None:
        return
    roots = metadata.setdefault('cache_roots', [])
    files = metadata.setdefault('cache_files', [])
    if not create:
        for name in files[:]:
            p = Path(name).resolve()
            matched = [Path(r).resolve() for r in roots if p.parent == Path(r).resolve()]
            if not matched or not p.name.endswith('.mcj'):
                raise ValueError('Cache file provenance mismatch')
            owner = p.parent / 'owner.json'
            if not owner.is_file() or json.loads(owner.read_text(encoding='utf-8')).get('session_id') != metadata['id']:
                raise ValueError('Cache directory ownership mismatch')
            if p.exists():
                cmds.diskCache(close=str(p))
                p.unlink()
            files.remove(name)
        return
    directory = _ACTIVE['options'].get('cache_directory')
    if directory is None:
        raise ValueError('CacheMe needs explicit cache_directory')
    owned = alive_owned()
    nodes = [n for n in owned.values() if cmds.nodeType(n) == 'diskCache']
    if not nodes:
        raise ValueError('No own Jiggle diskCache node; setup first')
    foreign = [n for n in cmds.ls(type='diskCache') or [] if identity(n) not in owned and cmds.getAttr(n + '.enable')]
    for n in foreign:
        mutable(n)
        if cmds.getAttr(n + '.enable', lock=True) or cmds.listConnections(n + '.enable', s=True, d=False):
            raise ValueError('Cannot isolate a locked/connected foreign cache')
    root = Path(tempfile.mkdtemp(prefix='mtk_physics_' + metadata['id'] + '_', dir=directory)).resolve()
    if root.parent != Path(directory).resolve():
        raise ValueError('Cache output escaped parent directory')
    (root / 'owner.json').write_text(json.dumps({'session_id': metadata['id']}), encoding='utf-8')
    roots.append(str(root))
    created = []
    for n in nodes:
        p = root / (identity(n).replace('-', '') + '.mcj')
        for a in ('cacheName', 'hiddenCacheName'):
            cmds.setAttr(n + '.' + a, str(p), type='string')
        cmds.setAttr(n + '.copyLocally', False)
        cmds.setAttr(n + '.enable', True)
        files.append(str(p))
        _LAST_FILES.append(str(p))
        created.append(str(p))
    try:
        # diskCache is a global command; only our cache nodes remain enabled during it.
        for n in foreign:
            cmds.setAttr(n + '.enable', False)
        cmds.diskCache(cacheType='mcj', samplingRate=1, overSample=True, enabledCachesOnly=True,
                       startTime=_ACTIVE['frame_range'][0], endTime=_ACTIVE['frame_range'][1])
    finally:
        for n in foreign:
            cmds.setAttr(n + '.enable', True)
    if any(not Path(p).is_file() or Path(p).stat().st_size == 0 for p in created):
        raise ValueError('Maya cache command did not create all requested owned mcj files')


class EmbeddedCommands:
    def timeControl(self, *args, **kwargs):
        if args and args[0] == 'candidateRange':
            r = _ACTIVE['frame_range']
            return [r[0], r[1] + 1]
        return cmds.timeControl(*args, **kwargs)

    def channelBox(self, *args, **kwargs):
        return _ACTIVE['options'].get('attributes') or [a for a in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz') if all(cmds.getAttr(n + '.' + a, keyable=True) for n in _ACTIVE.get('targets', []))]

    def _write_targets(self, values):
        require_scope()
        if isinstance(values, str):
            values = [values]
        owned = alive_owned()
        targets = {whole(n).split('.', 1)[0] for n in _ACTIVE.get('targets', [])}
        for n in values:
            base = whole(n).split('.', 1)[0]
            if identity(base) not in owned and base not in targets:
                raise ValueError('Embedded Python write escaped scope: ' + n)
        return values

    def delete(self, values, **kwargs):
        self._write_targets(values)
        if kwargs.get('constraints') and kwargs.get('staticChannels'):
            for n in ([values] if isinstance(values, str) else values):
                if identity(n) not in alive_owned():
                    raise ValueError('Temporary pivot cleanup requires own locator')
            return cmds.delete(values, **kwargs)
        return delete_owned([values] if isinstance(values, str) else values, int(kwargs.get('constraints', False)))

    def animLayer(self, name=None, **kwargs):
        if kwargs.get('edit') and kwargs.get('addSelectedObjects'):
            if identity(name) not in alive_owned():
                raise ValueError('Noise may only add channels to its own newly created layer')
        return cmds.animLayer(name, **kwargs) if name else cmds.animLayer(**kwargs)

    def group(self, **kwargs):
        kwargs['name'] = 'pivot_' + uuid.uuid4().hex[:12]
        return cmds.group(**kwargs)

    def spaceLocator(self, **kwargs):
        kwargs['name'] = 'pivotLoc_' + uuid.uuid4().hex[:12]
        return cmds.spaceLocator(**kwargs)

    def parent(self, child, parent):
        for n in [child, parent]:
            if identity(n) not in alive_owned():
                raise ValueError('Temporary pivot may only parent its own helper locators')
        return cmds.parent(child, parent)

    def parentConstraint(self, *args, **kwargs):
        self._write_targets([args[-1]])
        return cmds.parentConstraint(*args, **kwargs)

    def bakeResults(self, values, **kwargs):
        self._write_targets(values)
        return cmds.bakeResults(values, **kwargs)

    def keyframe(self, values, **kwargs):
        if not (kwargs.get('q') or kwargs.get('query')):
            self._write_targets(values)
        return cmds.keyframe(values, **kwargs)

    def setKeyframe(self, values, **kwargs):
        self._write_targets(values)
        if _ACTIVE['procedure'] in ('ruidoA', 'ruidoB', 'ruidoC') and 'attribute' not in kwargs:
            kwargs['attribute'] = self.channelBox()
        return cmds.setKeyframe(values, **kwargs)

    def keyTangent(self, values, **kwargs):
        if not (kwargs.get('q') or kwargs.get('query')):
            self._write_targets(values)
        return cmds.keyTangent(values, **kwargs)

    def __getattr__(self, name):
        if name in ('ls', 'getAttr', 'playbackOptions', 'listAttr', 'confirmDialog', 'timeControl'):
            return getattr(cmds, name)
        raise ValueError('Unreviewed embedded Maya command: ' + name)


class EmbeddedMel:
    def eval(self, code):
        if 'treeView' in code:
            # Scope noise to a new own layer, never implicit foreign layer membership.
            return []
        if '$gPlayBackSlider' in code:
            return 'candidateRange'
        raise ValueError('Unreviewed embedded MEL: ' + code)


def embedded(source):
    require_scope()
    tree = ast.parse(source)
    # Retain full embedded Python functions, avoid polluting Maya __main__ globals.
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Import) and any(a.name in ('maya.cmds', 'maya.mel') for a in n.names))]
    proxy = EmbeddedCommands()
    namespace = {'cmds': proxy, 'mel': EmbeddedMel()}
    state = random.getstate()
    try:
        exec(compile(ast.fix_missing_locations(tree), '<PhysicsTools original embedded business>', 'exec'), namespace, namespace)
    finally:
        random.setstate(state)
