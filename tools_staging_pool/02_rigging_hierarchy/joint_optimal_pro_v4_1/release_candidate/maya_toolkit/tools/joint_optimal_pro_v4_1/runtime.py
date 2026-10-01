"""Original whole source loading, preflight and reversible caller context."""
import hashlib
import json
from pathlib import Path
import re
from maya import cmds, mel
from maya.api import OpenMaya as om
from .tool import catalog

PKG = Path(__file__).resolve().parent
VENDOR = PKG / 'vendor/barnev_Joint_Optimal_Pro_Application_code.mel'
RADIUS = 'JOPA_4_1_92de112c5c170c44ad9daf4d48b1acdd'
COLOR = 'JOPA_4_1_cc20e95399a3b6da44eb78e45451d764'
HANDLE = 'JOPA_4_1_34cdd1e4469c2d3c695448db824d2ecb'
CREATE = 'JOPA_4_1_f2d5a2798ed7cfee36eb77ee8a281ed8'
LIMIT_CREATE = 'JOPA_4_1_a724b4b2abdd9e942758573c2c47afe6'
BATCH_PROCEDURES = {RADIUS, COLOR, HANDLE, CREATE, LIMIT_CREATE}
UI_PROCEDURES = {'JOPA_skeleton_tools_menue', 'JOPA_4_1_9e849622a64e61725d0526208e8aee88'}
_loaded_hash = None


def resources():
    for row in catalog()['files']:
        path = PKG / 'vendor' / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Missing/changed original asset: ' + row['path'])


def uuids():
    return {cmds.ls(n, uuid=True)[0] for n in cmds.ls(long=True) or []}


def source_conflicts():
    expected = hashlib.sha256(VENDOR.read_bytes()).hexdigest()
    for name in catalog()['procedures']:
        existing = mel.eval('whatIs ' + name)
        if existing == 'Unknown':
            continue
        if existing == 'Mel procedure entered interactively.' and _loaded_hash == expected:
            continue
        if not existing.startswith('Mel procedure found in:'):
            raise ValueError('Conflicting native name: ' + name)
        path = Path(existing.split(':', 1)[1].strip())
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Another suite defines ' + name + '; fresh Maya session required')


def nodes(values):
    result = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Unique whole transform/joint required: ' + value)
        node = found[0]
        selection = om.MSelectionList()
        selection.add(node)
        if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0))) != 1:
            raise ValueError('Instanced DAG input is unsupported by original naming/hierarchy routines')
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Referenced/locked input: ' + node)
        if node in result:
            raise ValueError('Duplicate object aliases')
        result.append(node)
    return result


def editable_attributes(node, attrs):
    for attr in attrs:
        plug = node + '.' + attr
        if not cmds.objExists(plug) or cmds.getAttr(plug, lock=True) or cmds.listConnections(plug, source=True, destination=False):
            raise ValueError('Missing/locked/driven target channel: ' + plug)


def preflight(p):
    resources()
    c = catalog()
    if p['action'] == 'inspect':
        return {'files': c['files'], 'public': c['public'], 'declarations': c['declaration_count'], 'unique_procedures': len(c['procedures']), 'duplicates': c['duplicate_names'], 'license': c['license'], 'vendor_modified': False, 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    proc = p['procedure']
    source_conflicts()
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before calls')
    if proc not in BATCH_PROCEDURES and not p['allow_native_scope']:
        raise ValueError('Original workflow can expand scope; allow_native_scope required on backup scene')
    resolved = nodes(p.get('objects', cmds.ls(selection=True, long=True) or []))
    if not resolved and proc in BATCH_PROCEDURES:
        raise ValueError('Nonempty ordered selection required for verified native subset')
    if proc == LIMIT_CREATE and len(resolved) >= p['arguments'][0]:
        raise ValueError('Original creation uses strict less-than limit; no-op rejected')
    if proc == RADIUS:
        for node in resolved:
            if cmds.nodeType(node) != 'joint':
                raise ValueError('Radius operation requires joints')
            editable_attributes(node, ('radius',))
    if proc == COLOR:
        for node in resolved:
            editable_attributes(node, ('overrideEnabled', 'overrideColor', 'overrideRGBColors'))
            if cmds.getAttr(node + '.overrideRGBColors'):
                raise ValueError('Original indexed color does not switch off RGB mode')
    if proc == HANDLE:
        for node in resolved:
            editable_attributes(node, ('displayHandle',))
    if proc not in BATCH_PROCEDURES:
        # Guard object arrays when the declared argument actually resolves scene nodes.
        for value, parameter in zip(p['arguments'], c['public'][proc]['parameters']):
            candidates = value if parameter['type'] == 'string[]' else [value] if parameter['type'] == 'string' else []
            existing = [n for n in candidates if cmds.objExists(n)]
            if existing:
                nodes(existing)
    return {'procedure': proc, 'arguments': p['arguments'], 'objects': resolved, 'signature': c['public'][proc], 'scene_write': True, 'file_write': False, 'gui_acceptance': 'not_run', 'batch_supported': proc in BATCH_PROCEDURES, 'native_scope': 'Original hierarchy/components/selection/global/preferences/callback behavior retained; explicit inputs are not a transitive scope guarantee'}


def load_vendor():
    global _loaded_hash
    resources()
    source_conflicts()
    if mel.eval('whatIs JOPA_skeleton_tools_menue') == 'Unknown':
        # Original bytes have one CP1251 Cyrillic X in a tooltip. Windows source
        # interprets it using CP936 and consumes the quote, causing a syntax error.
        # Decode to Unicode in memory, without rewriting or filtering vendor code.
        mel.eval(VENDOR.read_bytes().decode('cp1251'))
        _loaded_hash = hashlib.sha256(VENDOR.read_bytes()).hexdigest()


def snapshot():
    selected = cmds.ls(selection=True, long=True) or []
    return {'time': cmds.currentTime(query=True), 'selected': selected, 'selection_uuids': [cmds.ls(n, uuid=True)[0] for n in selected], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True), 'track': cmds.selectPref(query=True, trackSelectionOrder=True), 'highlight': cmds.selectPref(query=True, selectionChildHighlightMode=True), 'undo': cmds.undoInfo(query=True, state=True), 'mirror': {name: cmds.optionVar(query=name) if cmds.optionVar(exists=name) else None for name in ('mirrorJointSearch', 'mirrorJointReplace', 'mirrorJointFunction', 'mirrorJointMode')}}


def restore(state):
    cmds.undoInfo(stateWithoutFlush=state['undo'])
    cmds.namespace(setNamespace=state['namespace'])
    cmds.autoKeyframe(state=state['autokey'])
    cmds.currentTime(state['time'])
    for name, value in state['mirror'].items():
        if value is None:
            cmds.optionVar(remove=name)
        elif isinstance(value, str):
            cmds.optionVar(stringValue=(name, value))
        else:
            cmds.optionVar(intValue=(name, int(value)))
    selected = []
    for identifier in state['selection_uuids']:
        found = cmds.ls(identifier, long=True) or []
        if len(found) == 1:
            selected.append(found[0])
    cmds.select(selected, replace=True) if selected else cmds.select(clear=True)
    cmds.selectPref(trackSelectionOrder=state['track'], selectionChildHighlightMode=state['highlight'])


def execute(p):
    plan = preflight(p)
    if p['action'] == 'inspect':
        return plan
    proc = p['procedure']
    if cmds.about(batch=True) and proc not in BATCH_PROCEDURES:
        raise RuntimeError('Original full workflow requires interactive Maya; GUI acceptance not_run')
    load_vendor()
    state = snapshot()
    before = uuids()
    depth = [0]
    def callback(command, *args):
        if re.match(r'\s*undoInfo\b', command):
            depth[0] += bool(re.search(r'-(?:ock|openChunk)\b', command))
            depth[0] -= bool(re.search(r'-(?:cck|closeChunk)\b', command))
    callback_id = om.MCommandMessage.addCommandCallback(callback)
    try:
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        cmds.selectPref(trackSelectionOrder=True)
        cmds.select(plan['objects'], replace=True) if plan['objects'] else cmds.select(clear=True)
        result = mel.eval(p['command'])
        selected = cmds.ls(selection=True, long=True) or []
        if depth[0] < 0:
            raise RuntimeError('Original procedure closed an outer Undo chunk')
        return dict(plan, native_result=result, native_result_selection=selected, created_node_uuids=sorted(uuids() - before), runtime_effects='MEL declarations and shared globals persist; original UI/callback effects are not scene Undo')
    finally:
        om.MMessage.removeCallback(callback_id)
        try:
            for unused in range(max(0, depth[0])):
                cmds.undoInfo(closeChunk=True)
        finally:
            restore(state)


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for original full skeleton UI')
    if cmds.window('create_skeleton_tools', exists=True) or cmds.dockControl('JointOPtimalAalign', exists=True):
        raise RuntimeError('Original UI already exists; use or close it first')
    load_vendor()
    mel.eval('JOPA_skeleton_tools_menue();')
    return 'create_skeleton_tools'
