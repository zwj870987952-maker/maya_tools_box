import hashlib
import importlib
import importlib.util
from pathlib import Path
import re
from maya import cmds
from maya.api import OpenMaya as om
from .tool import catalog
from .support import export_context, export_path

PKG = Path(__file__).resolve().parent
PREFIX = 'maya_toolkit.tools.rdm_tools_v2.native.'
FUNCTIONS = {('RdMToolsV2.RiggingTools.Curves.CurveColors', 'colorShape'), ('RdMToolsV2.RiggingTools.Curves.RootAuto', 'rootAuto'), ('RdMToolsV2.RiggingTools.Curves.RootAuto', 'offsetGrp'), ('RdMToolsV2.RiggingTools.Curves.curveOnSelection', 'curveOnSelectionFunc'), ('RdMToolsV2.RiggingTools.ShowHide.RdMToggleAxis', 'setAxisDisplay')}
SCRIPTS = {'RdMToolsV2.RiggingTools.Curves.BoxCurve', 'RdMToolsV2.RiggingTools.Curves.CurveToJson'}
_window = None


def resources():
    for row in catalog()['files']:
        path = PKG / row['vendor']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Original resource missing/changed: ' + row['path'])


def uuids():
    return {cmds.ls(n, uuid=True)[0] for n in cmds.ls(long=True) or []}


def nodes(values):
    result = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Unique whole transform/joint required')
        node = found[0]
        sel = om.MSelectionList()
        sel.add(node)
        if len(om.MDagPath.getAllPathsTo(sel.getDependNode(0))) != 1:
            raise ValueError('Instanced DAG inputs unsupported by original naming')
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Locked/referenced input rejected')
        if node in result:
            raise ValueError('Duplicate input aliases')
        result.append(node)
    return result


def editable(node, attrs):
    for attr in attrs:
        plug = node + '.' + attr
        if not cmds.objExists(plug) or cmds.getAttr(plug, lock=True) or cmds.listConnections(plug, source=True, destination=False):
            raise ValueError('Missing/locked/driven attribute: ' + plug)


def preflight(p):
    resources()
    c = catalog()
    if p['action'] == 'inspect':
        return dict(c, scene_write=False, file_write=False, gui_acceptance='not_run')
    module = p['module']
    function = p.get('function')
    bounded = (module, function) in FUNCTIONS or p['action'] == 'script' and module in SCRIPTS
    if not bounded and not p['allow_native_scope']:
        raise ValueError('Original broad scope requires allow_native_scope on backup scene')
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo')
    resolved = nodes(p.get('objects', cmds.ls(selection=True, long=True) or []))
    if (module, function) in FUNCTIONS and not resolved:
        raise ValueError('Explicit nonempty scope required; original empty selection may target entire scene')
    if c['modules'][module]['pymel_required'] and importlib.util.find_spec('pymel') is None:
        raise ValueError('Original module requires PyMel, absent in current Maya; no fabricated substitute')
    arguments = p['arguments']
    if function == 'colorShape':
        color = arguments.get('Color', 16)
        if type(color) is not int or color not in range(32):
            raise ValueError('Color must be integer 0..31')
        for node in resolved:
            editable(node, ('overrideEnabled', 'overrideColor', 'overrideRGBColors'))
            if cmds.getAttr(node + '.overrideRGBColors'):
                raise ValueError('Indexed native color does not switch RGB mode')
    if function == 'setAxisDisplay':
        if type(arguments.get('display', False)) is not bool:
            raise ValueError('display must be boolean')
        for node in resolved:
            if cmds.nodeType(node) != 'joint':
                raise ValueError('Joint scope required to prevent original all-scene fallback')
            editable(node, ('displayLocalAxis',))
    if function in ('rootAuto', 'offsetGrp'):
        suffixes = ('_Auto', '_Root') if function == 'rootAuto' else ('_Offset_Grp',)
        for node in resolved:
            if len(cmds.ls(node.rsplit('|', 1)[-1], long=True) or []) != 1:
                raise ValueError('Original group naming requires unique short names')
            if any(cmds.objExists(node.rsplit('|', 1)[-1] + suffix) for suffix in suffixes):
                raise ValueError('Original generated group name already exists')
            for ancestor in cmds.listRelatives(node, parent=True, fullPath=True) or []:
                if cmds.referenceQuery(ancestor, isNodeReferenced=True) or any(cmds.lockNode(ancestor, query=True, lock=True)):
                    raise ValueError('Original reparent affects locked/referenced parent')
            editable(node, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'))
    if function == 'curveOnSelectionFunc':
        mode = arguments.get('mode', 'Cube')
        if mode not in ('Joint', 'Locator', 'CircleX', 'CircleY', 'CircleZ', 'Sphere', 'Cube', 'Hand', 'Foot', 'EyeVisor', 'Pringle'):
            raise ValueError('Choose original supported curve mode')
        if cmds.objExists(mode):
            raise ValueError('Original routine deletes node named mode; existing scene node protected')
        for key in ('Constraint', 'offset'):
            if type(arguments.get(key, False)) is not bool:
                raise ValueError('Curve flags must be boolean')
        for node in resolved:
            leaf = node.rsplit('|', 1)[-1]
            if len(cmds.ls(leaf, long=True) or []) != 1:
                raise ValueError('Original curve naming requires unique short names')
            if arguments.get('Constraint'):
                editable(node, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
    if module == 'RdMToolsV2.RiggingTools.Curves.BoxCurve' and cmds.objExists('BoxCurve'):
        raise ValueError('Original BoxCurve name already exists')
    file_write = 'output_path' in p
    if file_write:
        path = export_path(p['output_path'])
        expected = '.json' if module.endswith('CurveToJson') else '.py'
        if path.suffix.lower() != expected:
            raise ValueError('Export extension must match original action')
        if expected == '.py':
            ui = Path(p.get('input_ui', ''))
            if not ui.is_absolute() or not ui.is_file() or ui.suffix.lower() != '.ui':
                raise ValueError('Existing explicit absolute .ui required')
    return {'action': p['action'], 'module': module, 'function': function, 'arguments': arguments, 'objects': resolved, 'scene_write': not file_write, 'file_write': file_write, 'output_path': p.get('output_path'), 'signature': c['modules'][module], 'batch_supported': bounded, 'gui_acceptance': 'not_run'}


def snapshot():
    return {'time': cmds.currentTime(query=True), 'selection_uuids': [cmds.ls(n, uuid=True)[0] for n in cmds.ls(selection=True, long=True) or []], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True), 'track': cmds.selectPref(query=True, trackSelectionOrder=True), 'symmetry': cmds.symmetricModelling(query=True, symmetry=True), 'soft': cmds.softSelect(query=True, softSelectEnabled=True)}


def restore(state):
    cmds.namespace(setNamespace=state['namespace'])
    cmds.autoKeyframe(state=state['autokey'])
    cmds.currentTime(state['time'])
    selection = [found[0] for identifier in state['selection_uuids'] for found in [cmds.ls(identifier, long=True) or []] if len(found) == 1]
    cmds.select(selection, replace=True) if selection else cmds.select(clear=True)
    cmds.selectPref(trackSelectionOrder=state['track'])
    cmds.symmetricModelling(symmetry=state['symmetry'])
    cmds.softSelect(softSelectEnabled=state['soft'])


def execute(p):
    plan = preflight(p)
    if p['action'] == 'inspect':
        return plan
    if cmds.about(batch=True) and not plan['batch_supported']:
        raise RuntimeError('Complete original workflow requires interactive Maya; not batch simulated')
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
        native = importlib.import_module(PREFIX + p['module'])
        with export_context(p):
            result = native.run_script() if p['action'] == 'script' else getattr(native, p['function'])(**p['arguments'])
        if depth[0] < 0:
            raise RuntimeError('Original operation closed an outer Undo chunk')
        return dict(plan, native_result=result, created_node_uuids=sorted(uuids() - before), native_result_selection=cmds.ls(selection=True, long=True) or [])
    finally:
        om.MMessage.removeCallback(callback_id)
        try:
            for unused in range(max(0, depth[0])):
                cmds.undoInfo(closeChunk=True)
        finally:
            restore(state)


def show_ui():
    global _window
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for complete RdM Qt interface')
    resources()
    from .native.RdMToolsV2.ShowUI import RdMV2UI
    if _window is not None:
        try:
            _window.close()
            _window.deleteLater()
        except RuntimeError:
            pass
    _window = RdMV2UI()
    _window.show()
    return _window
