"""Whole native workflows, read-only scope and owned session cleanup."""
import hashlib
import json
import math
from pathlib import Path
import re
from maya import cmds, mel
from maya.api import OpenMaya as om

PKG = Path(__file__).resolve().parent
OWNER = 'stagingReParentOwner'
IDS = 'stagingReParentControlIds'
IDENTITY = 'reparent_pro_v1_5_1'
SETS = {'root': 'rppstg_reParent_sets', 'all_controls': 'rppstg_All_Sessions_reParentControls_set', 'last_controls': 'rppstg_Last_Session_reParentControls_set', 'last_locators': 'rppstg_Last_Session_reParentLocator_set', 'all_locators': 'rppstg_All_Session_reParentLocator_set'}
TR = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
OPTIONS = {}
_loaded_hash = None
PROCS = {'reparent': 'reParent', 'manual_start': 'reParentManualStarter', 'manual_go': 'manualModeGo', 'relative': 'reParentRelative', 'freeze': 'reParentStayHere', 'ik': 'IKmode', 'locator_size': 'reParentLocatorSize'}


def catalog():
    return json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))


def resources():
    for row in catalog()['files']:
        path = PKG / 'vendor' / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Original asset missing/changed: ' + row['path'])


def uid(node):
    return cmds.ls(node, uuid=True)[0]


def scene_map():
    return {uid(n): n for n in cmds.ls(long=True) or []}


def is_owned(node):
    return cmds.objExists(node + '.' + OWNER) and cmds.getAttr(node + '.' + OWNER) == IDENTITY


def owned():
    return [n for n in cmds.ls(long=True) or [] if is_owned(n)]


def stamp(node):
    if not cmds.objExists(node + '.' + OWNER):
        cmds.addAttr(node, longName=OWNER, dataType='string')
    cmds.setAttr(node + '.' + OWNER, IDENTITY, type='string')


def resolve(values):
    result = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Unique whole transform/joint required: ' + value)
        node = found[0]
        sl = om.MSelectionList()
        sl.add(node)
        if len(om.MDagPath.getAllPathsTo(sl.getDependNode(0))) != 1:
            raise ValueError('True instanced DAG input unsupported')
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Referenced/locked input: ' + node)
        leaf = node.rsplit('|', 1)[-1]
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_:]*', leaf) or leaf.startswith('rppstg_') or '_RPPStage' in leaf or len(cmds.ls(leaf, long=True) or []) != 1:
            raise ValueError('Native suffix naming requires unique nonreserved simple leaf names')
        if node in result:
            raise ValueError('Duplicate object aliases')
        result.append(node)
    return result


def cleanup_plan():
    items = owned()
    identifiers = {uid(n) for n in items}
    controls = set()
    for key in ('all_controls', 'last_controls'):
        node = SETS[key]
        if cmds.objExists(node):
            if not is_owned(node) or not cmds.objExists(node + '.' + IDS):
                raise ValueError('Unknown control set provenance')
            members = cmds.sets(node, query=True) or []
            actual = {uid(n) for n in resolve(members)}
            recorded = set(json.loads(cmds.getAttr(node + '.' + IDS)))
            if actual != recorded:
                raise ValueError('Owned control set membership changed; review scene before cleanup')
            controls.update(actual)
    for node in items:
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Owned helper locked/referenced: ' + node)
        if cmds.objectType(node, isAType='dagNode'):
            for child in cmds.listRelatives(node, allDescendents=True, fullPath=True) or []:
                if uid(child) not in identifiers:
                    raise ValueError('Foreign descendant beneath helper: ' + child)
        if cmds.nodeType(node) == 'objectSet':
            members = cmds.sets(node, query=True) or []
            if node not in (SETS['all_controls'], SETS['last_controls']):
                for member in members:
                    if '.' in member or uid(member) not in identifiers:
                        raise ValueError('Foreign member in helper set: ' + member)
        # Message links are metadata; all actual downstream scene targets must belong
        # to this session or its recorded controls. Preserve bake curves on controls.
        for plug in cmds.listConnections(node, source=False, destination=True, plugs=True) or []:
            if plug.rsplit('.', 1)[-1] == 'message' or 'message' in plug:
                continue
            target = plug.split('.', 1)[0]
            if uid(target) not in identifiers | controls and cmds.nodeType(target) not in ('time',):
                # Maya default sets/partition are bookkeeping, not manipulated targets.
                if target not in ('defaultLightSet', 'defaultObjectSet', 'renderPartition', 'initialShadingGroup', 'ikSystem'):
                    raise ValueError('Foreign downstream connection from helper: ' + plug)
    return items


def sessions(which):
    name = SETS[which]
    if not cmds.objExists(name) or not is_owned(name):
        raise ValueError('No owned ' + which + ' session')
    values = cmds.sets(name, query=True) or []
    if not values:
        raise ValueError('Owned session is empty')
    return resolve(values)


def editable(nodes, allow_owned_constraints=False):
    for node in nodes:
        for attr in TR:
            plug = node + '.' + attr
            if cmds.getAttr(plug, lock=True) or not cmds.getAttr(plug, keyable=True):
                raise ValueError('All six native TR channels must be editable: ' + plug)
            for incoming in cmds.listConnections(plug, source=True, destination=False, plugs=True) or []:
                driver = incoming.split('.', 1)[0]
                if allow_owned_constraints and is_owned(driver) and (cmds.objectType(driver, isAType='constraint') or cmds.nodeType(driver) == 'pairBlend' or cmds.nodeType(driver).startswith('animBlend')):
                    continue
                kind = cmds.nodeType(driver)
                if not kind.startswith('animCurveT') or kind not in ('animCurveTL', 'animCurveTA', 'animCurveTU'):
                    raise ValueError('Existing nonordinary animation/constraint: ' + plug)
                if len(cmds.listConnections(driver + '.output', source=False, destination=True, plugs=True) or []) != 1:
                    raise ValueError('Shared animation curve unsupported')
                upstream = cmds.listConnections(driver + '.input', source=True, destination=False) or []
                # Maya 2025 time curves can use implicit time with no input connection.
                if any(cmds.nodeType(n) != 'time' for n in upstream):
                    raise ValueError('Non-time/driven animation curve unsupported')
        for constraint in cmds.listRelatives(node, children=True, type='constraint', fullPath=True) or []:
            if not allow_owned_constraints or not is_owned(constraint):
                raise ValueError('Existing foreign constraint on control')


def preflight(p):
    resources()
    if p['action'] == 'inspect':
        return {'catalog': catalog(), 'gui_acceptance': 'not_run', 'scene_write': False, 'file_write': False}
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before calls')
    if p['action'] == 'freeze' and cmds.about(batch=True):
        raise ValueError('Native freeze progress window requires interactive Maya')
    for row in catalog()['adapted_procedures']:
        status = mel.eval('whatIs ' + row['name'])
        if status != 'Unknown' and _loaded_hash != hashlib.sha256((PKG / 'native.mel').read_bytes()).hexdigest():
            raise ValueError('Native procedure name conflict; use fresh Maya session')
    reserved = [n for n in cmds.ls(long=True) or [] if n.rsplit('|', 1)[-1].startswith('rppstg_') or '_RPPStage' in n.rsplit('|', 1)[-1]]
    if any(not is_owned(n) for n in reserved):
        raise ValueError('Foreign reserved helper name; nothing will be deleted')
    helpers = cleanup_plan()
    action = p['action']
    if action in ('manual_go', 'manual_cancel'):
        nodes = sessions('last_controls')
        locators = cmds.sets(SETS['last_locators'], query=True) or [] if cmds.objExists(SETS['last_locators']) else []
        if not locators or any(not is_owned(n) for n in locators):
            raise ValueError('No owned manual locators')
        if any(cmds.listConnections(n, source=False, destination=True, type='constraint') for n in locators):
            raise ValueError('Last session is already bound; manual Go/Cancel rejected')
    elif action == 'bake_delete':
        nodes = sessions('all_controls')
    else:
        nodes = resolve(p.get('objects', cmds.ls(selection=True, long=True) or []))
        if not nodes:
            raise ValueError('Select explicit ordered controls')
    if action in ('relative', 'freeze') and len(nodes) < 2:
        raise ValueError('This mode needs at least two controls')
    if action == 'relative' and any(nodes[-1].startswith(n + '|') for n in nodes[:-1]):
        raise ValueError('Relative reference beneath a controlled object creates feedback')
    if action == 'ik':
        if len(nodes) != 3 or not cmds.listRelatives(nodes[0], parent=True):
            raise ValueError('Original IK requires three controls and a parent above the first')
        positions = [cmds.xform(n, query=True, worldSpace=True, translation=True) for n in nodes]
        a = [positions[1][i] - positions[0][i] for i in range(3)]
        b = [positions[2][i] - positions[1][i] for i in range(3)]
        cross = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
        if sum(v*v for v in a) < 1e-12 or sum(v*v for v in b) < 1e-12 or sum(v*v for v in cross) < 1e-12:
            raise ValueError('Zero-length/collinear IK limb would divide by zero')
    if action not in ('manual_cancel', 'locator_size'):
        editable(nodes, allow_owned_constraints=action == 'bake_delete')
    if action in ('reparent', 'manual_go', 'relative', 'freeze', 'ik') and not p['allow_clear_animation']:
        raise ValueError('Original TR clear/constraint replacement requires allow_clear_animation=True on backup scene')
    if action not in ('manual_go', 'manual_cancel', 'bake_delete', 'locator_size'):
        for node in nodes:
            leaf = node.rsplit('|', 1)[-1]
            if cmds.ls(leaf + '_RPPStage*') or cmds.ls(leaf + 'rppstg_Temp*'):
                raise ValueError('Control already has helper session; bake/delete before reusing it')
    if action == 'locator_size':
        if len(nodes) != 1 or not cmds.objExists('rppstg_TempLocator') or not is_owned('rppstg_TempLocator'):
            raise ValueError('Sizing helper is only callable for one control and owned temporary locator')
    frame_range = p['frame_range'] or [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)]
    if any(not math.isfinite(v) or int(v) != v or abs(v) > 1000000 for v in frame_range) or not 0 <= frame_range[1] - frame_range[0] <= 10000 or (frame_range[1] - frame_range[0] + 1)*len(nodes) > 200000:
        raise ValueError('Bounded integer inclusive playback range required')
    return {'action': action, 'objects': nodes, 'frame_range': frame_range, 'owned_helpers': helpers, 'scene_write': True, 'file_write': False, 'clear_all_TR_keys': action in ('reparent', 'manual_go', 'relative', 'freeze'), 'gui_acceptance': 'not_run'}


def native_setting(name):
    return int(OPTIONS.get(name, False))


def load_native():
    global _loaded_hash
    data = (PKG / 'native.mel').read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if _loaded_hash == digest and mel.eval('whatIs rppstg_reParent') != 'Unknown':
        return
    if any(mel.eval('whatIs ' + row['name']) != 'Unknown' for row in catalog()['adapted_procedures']):
        raise ValueError('Conflicting prefixed MEL definitions')
    mel.eval(data.decode('utf-8'))
    _loaded_hash = digest


def snapshot():
    key_curves = cmds.keyframe(query=True, selected=True, name=True) or []
    return {'time': cmds.currentTime(query=True), 'selection': [uid(n) for n in cmds.ls(selection=True, long=True) or []], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True), 'track': cmds.selectPref(query=True, trackSelectionOrder=True), 'playback': {k: cmds.playbackOptions(query=True, **{k: True}) for k in ('minTime', 'maxTime', 'animationStartTime', 'animationEndTime')}, 'keys': {uid(n): cmds.keyframe(n, query=True, selected=True, indexValue=True) or [] for n in key_curves}, 'blend': cmds.optionVar(query='animBlendingOpt') if cmds.optionVar(exists='animBlendingOpt') else None}


def restore(state):
    cmds.namespace(setNamespace=state['namespace'])
    cmds.autoKeyframe(state=state['autokey'])
    cmds.playbackOptions(**state['playback'])
    cmds.currentTime(state['time'])
    cmds.selectKey(clear=True)
    for identifier, indices in state['keys'].items():
        nodes = cmds.ls(identifier) or []
        if nodes:
            for index in indices:
                if index < (cmds.keyframe(nodes[0], query=True, keyframeCount=True) or 0):
                    cmds.selectKey(nodes[0], add=True, index=(index, index))
    selected = [cmds.ls(identifier, long=True)[0] for identifier in state['selection'] if cmds.ls(identifier, long=True)]
    cmds.select(selected, replace=True) if selected else cmds.select(clear=True)
    cmds.selectPref(trackSelectionOrder=state['track'])
    if state['blend'] is None:
        cmds.optionVar(remove='animBlendingOpt')
    else:
        cmds.optionVar(intValue=('animBlendingOpt', int(state['blend'])))


def set_provenance():
    for key in ('all_controls', 'last_controls'):
        node = SETS[key]
        if cmds.objExists(node) and is_owned(node):
            if not cmds.objExists(node + '.' + IDS):
                cmds.addAttr(node, longName=IDS, dataType='string')
            identifiers = sorted(uid(n) for n in cmds.sets(node, query=True) or [])
            cmds.setAttr(node + '.' + IDS, json.dumps(identifiers), type='string')


def delete_owned_helpers(items):
    # Bake can retain a pairBlend network (preserveOutsideKeys); keep its complete
    # upstream animation graph and remove ownership after deleting constraints.
    def result_node(node):
        kind = cmds.nodeType(node)
        return kind.startswith('animCurve') or kind.startswith('animBlend') or kind == 'pairBlend'
    retained = {uid(n) for n in items if result_node(n) and any(not is_owned(d) for d in cmds.listConnections(n, source=False, destination=True) or [])}
    pending = list(retained)
    while pending:
        found = cmds.ls(pending.pop(), long=True) or []
        for n in cmds.listConnections(found[0], source=True, destination=False) or [] if found else []:
            identifier = uid(n)
            if is_owned(n) and result_node(n) and identifier not in retained:
                retained.add(identifier)
                pending.append(identifier)
    kept = []
    deletable = []
    for node in items:
        if uid(node) in retained:
            kept.append(node)
            cmds.deleteAttr(node + '.' + OWNER)
            continue
        deletable.append(node)
    identifiers = [uid(n) for n in deletable]
    for identifier in identifiers:
        found = cmds.ls(identifier, long=True) or []
        if found:
            cmds.delete(found[0])
    return kept


def execute(p):
    plan = preflight(p)
    if p['action'] == 'inspect':
        return plan
    load_native()
    state = snapshot()
    before = scene_map()
    old_options = dict(OPTIONS)
    try:
        OPTIONS.clear()
        OPTIONS.update({'PinCheckBox': p['pin'], 'IKCheckLocalBox': p['local'], 'DelRed': p['delete_redundant']})
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        cmds.selectPref(trackSelectionOrder=True)
        cmds.playbackOptions(minTime=plan['frame_range'][0], maxTime=plan['frame_range'][1])
        cmds.select([n.rsplit('|', 1)[-1] for n in plan['objects']], replace=True)
        if p['action'] == 'bake_delete':
            options = dict(time=tuple(plan['frame_range']), simulation=True, sampleBy=1, preserveOutsideKeys=True, sparseAnimCurveBake=False, minimizeRotation=True, controlPoints=False, shape=False, attribute=list(TR), disableImplicitControl=True)
            if p['bake_on_layer']:
                layer = cmds.animLayer('RPPStage_FinalBake', override=True)
                options['destinationLayer'] = layer
            cmds.bakeResults(plan['objects'], **options)
            # The final override layer is part of the result, not a helper to erase.
            delete_owned_helpers([n for n in plan['owned_helpers'] if cmds.objExists(n)])
        elif p['action'] == 'manual_cancel':
            values = cmds.sets(SETS['last_locators'], query=True) or []
            cmds.delete(values)
            mel.eval('rppstg_manualUI(0);')
        else:
            mel.eval('rppstg_' + PROCS[p['action']] + '();')
        selected = cmds.ls(selection=True, long=True) or []
        return dict(plan, native_selection=selected, created_node_uuids=sorted(set(scene_map()) - set(before)))
    finally:
        # Recover ownership even after partial native failure so it is reviewable.
        current = scene_map()
        if p['action'] != 'bake_delete':
            for identifier in set(current) - set(before):
                stamp(current[identifier])
        set_provenance()
        OPTIONS.clear()
        OPTIONS.update(old_options)
        restore(state)
