"""Independent wrapper, never modifies or installs the licensed MEL source."""
import hashlib
import json
from pathlib import Path
import re
from maya import cmds, mel
from maya.api import OpenMaya as om
from .tool import catalog

PKG = Path(__file__).resolve().parent
VENDOR = PKG / 'vendor/base_OverRig_scripts.mel'
BATCH_PROCEDURES = {'create_normalised_locators_on_selected', 'scale_selected_lock_or_joint', 'return_constrained_object', 'delete_constraint_attributes_on_objects', 'barn_sel_set_member'}
UI_PROCEDURES = {'base_OverRig_scripts', 'bar_tail_overlap_window', 'overRig_noise_window', 'create_recalc_spine_rig_menue', 'overRig_tween_window', 'BP_arc_tool_menue'}


def resources():
    for row in catalog()['files']:
        path = PKG / 'vendor' / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Missing/changed vendor asset: ' + row['path'])


def quote(text):
    return json.dumps(text, ensure_ascii=False)


def uuids():
    return {cmds.ls(n, uuid=True)[0] for n in cmds.ls(long=True) or []}


def nodes(values):
    out = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Unique whole transform/joint required: ' + value)
        node = found[0]
        selection = om.MSelectionList()
        selection.add(node)
        if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0))) != 1:
            raise ValueError('Instanced nodes unsupported by original routines')
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Referenced/locked API input: ' + node)
        for child in [node] + (cmds.listRelatives(node, shapes=True, fullPath=True) or []):
            if cmds.referenceQuery(child, isNodeReferenced=True) or any(cmds.lockNode(child, query=True, lock=True)):
                raise ValueError('Referenced/locked input shape')
            for attribute in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'radius', 'localScaleX', 'localScaleY', 'localScaleZ'):
                if cmds.attributeQuery(attribute, node=child, exists=True) and cmds.getAttr(child + '.' + attribute, lock=True):
                    raise ValueError('Locked input channel: ' + child + '.' + attribute)
        if node in out:
            raise ValueError('Duplicate object aliases')
        out.append(node)
    return out


def source_conflicts():
    expected = hashlib.sha256(VENDOR.read_bytes()).hexdigest()
    for name in catalog()['procedures']:
        existing = mel.eval('whatIs ' + name)
        if existing == 'Unknown':
            continue
        if not existing.startswith('Mel procedure found in:'):
            raise ValueError('Conflicting native command/procedure: ' + name)
        path = Path(existing.split(':', 1)[1].strip())
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Another suite defines ' + name + '; start a fresh Maya session')


def preflight(p):
    resources()
    c = catalog()
    if p['action'] == 'inspect':
        return {'action': 'inspect', 'files': c['files'], 'public': c['public'], 'declarations': c['declaration_count'], 'unique_procedures': len(c['procedures']), 'duplicates': c['duplicate_names'], 'vendor_modified': False, 'license': c['license'], 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    source_conflicts()
    proc = p['procedure']
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before native calls')
    selection = p.get('objects', cmds.ls(selection=True, long=True) or [])
    resolved = nodes(selection)
    if not resolved and proc not in UI_PROCEDURES and proc != 'barn_sel_set_member':
        raise ValueError('Explicit objects or ordered whole selection required')
    arguments = p['arguments']
    if proc in ('delete_constraint_attributes_on_objects', 'execute_overlap_command'):
        index = 0 if proc.startswith('delete_') else 1
        explicit = nodes(arguments[index])
        if not explicit:
            raise ValueError('Nonempty explicit object array required')
        if set(explicit) - set(resolved):
            raise ValueError('Argument objects must be included in the explicit call scope')
    if proc == 'barn_sel_set_member':
        name = arguments[0]
        if not cmds.objExists(name) or cmds.nodeType(name) != 'objectSet':
            raise ValueError('Existing objectSet required')
        nodes(cmds.sets(name, query=True) or [])
    if proc in ('barn_fast_bake_source_obj_and_delete_knots', 'barn_fast_bake_min_max_or_range_source_obj_and_delete_knots'):
        for name in ('OverRig_rig_objects', 'OverRig_knots'):
            if not cmds.objExists(name) or cmds.nodeType(name) != 'objectSet' or cmds.referenceQuery(name, isNodeReferenced=True) or any(cmds.lockNode(name, query=True, lock=True)):
                raise ValueError('Native bake/delete requires an editable ' + name + ' objectSet')
            members = nodes(cmds.sets(name, query=True) or [])
            if not members or set(members) - set(resolved):
                raise ValueError('Explicit objects must include all source/knots set members')
    if proc == 'scale_selected_lock_or_joint':
        for node in resolved:
            shape = cmds.listRelatives(node, shapes=True, fullPath=True) or []
            if cmds.nodeType(node) != 'joint' and not any(cmds.nodeType(x) == 'locator' for x in shape):
                raise ValueError('Native size utility requires locators/joints')
            for target in [node] + shape:
                for attribute in ('radius', 'localScaleX', 'localScaleY', 'localScaleZ'):
                    if cmds.attributeQuery(attribute, node=target, exists=True) and cmds.listConnections(target + '.' + attribute, source=True, destination=False):
                        raise ValueError('Driven locator/joint display size rejected')
    if proc == 'set_infinity_graphEditor' and arguments[0] not in ('cycle', 'oscillate', 'linear', 'constant', 'cycleRelative'):
        raise ValueError('Unsupported infinity type')
    if proc == 'set_key_time_range' and arguments[0] not in ('all', 'translate', 'rotate', 'channelbox'):
        raise ValueError('Unsupported key mode')
    if proc == 'base_OverRig_scripts' and arguments[0] not in (0, 1):
        raise ValueError('Color scheme must be 0 or 1')
    if proc in ('apply_objects_spline_IK', 'apply_Smart_Bake', 'return_constrained_object') and arguments[0] not in (0, 1):
        raise ValueError('Boolean-like native flag requires 0 or 1')
    if proc == 'move_and_rotate_total_pivot' and arguments[0] not in range(4):
        raise ValueError('Pivot mode must be 0..3')
    if proc == 'bar_create_multiply_fast_motion_trail' and not 0 < arguments[1] - arguments[0] <= 10000:
        raise ValueError('Bounded positive motion-trail interval required')
    if proc in ('apply_Parent_in', 'apply_Swap_parent', 'apply_ForwHierarhy', 'apply_ReverseHierarhy', 'make_aim_from_selected') and len(resolved) < 2:
        raise ValueError('At least two ordered objects required')
    if proc == 'apply_rebike_3_or_more_object_to_IK' and len(resolved) < 3:
        raise ValueError('At least three objects required for IK conversion')
    if proc == 'apply_objects_spline_IK' and len(resolved) < 2:
        raise ValueError('At least two objects required for spline IK')
    return {'action': 'call', 'procedure': proc, 'arguments': arguments, 'objects': resolved, 'command': p['command'], 'signature': c['public'][proc], 'scene_write': True, 'file_write': False, 'gui_acceptance': 'not_run', 'batch_supported': proc in BATCH_PROCEDURES, 'native_effects': 'Original scope may expand to parents, children, rig sets, connected nodes and callbacks; check backup scene'}


def load_vendor():
    resources()
    source_conflicts()
    if mel.eval('whatIs base_OverRig_scripts') == 'Unknown':
        mel.eval('source ' + quote(VENDOR.as_posix()) + ';')


def initialize_globals(p):
    mel.eval('global string $path_to_JGLBN; $path_to_JGLBN=' + quote((PKG / 'vendor/misc').as_posix() + '/') + ';')
    mel.eval('global int $barnev_OverRig_RotateOrder; $barnev_OverRig_RotateOrder=' + str(p.get('rotate_order', 0)) + ';')
    mel.eval('global string $my_eval_mode[]; $my_eval_mode={' + ','.join(quote(x) for x in cmds.evaluationManager(query=True, mode=True)) + '}; global float $startTime; $startTime=`timerX`;')


def snapshot():
    options = ['animBlendingOpt', 'animBlendBrokenInputOpt', 'animLayerSelectionKey', 'bar_mt_START_val', 'bar_mt_END_val', 'bar_trailThickness', 'bar_trailDotsize', 'bar_mt_DOT_colors']
    data = {'time': cmds.currentTime(query=True), 'selection': cmds.ls(selection=True, long=True) or [], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True), 'undo': cmds.undoInfo(query=True, state=True), 'linear': cmds.currentUnit(query=True, linear=True), 'evaluation': cmds.evaluationManager(query=True, mode=True), 'track': cmds.selectPref(query=True, trackSelectionOrder=True), 'suspend': bool(cmds.refresh(query=True, suspend=True)), 'options': {k: cmds.optionVar(query=k) if cmds.optionVar(exists=k) else None for k in options}, 'plugins': {x: cmds.pluginInfo(x, query=True, autoload=True) for x in cmds.pluginInfo(query=True, listPlugins=True) or []}}
    if not cmds.about(batch=True):
        from maya.plugin.evaluator.cache_preferences import CachePreferenceEnabled
        data['cache'] = CachePreferenceEnabled().get_value()
        data['slider'] = bool(mel.eval('isTimeSliderVisible()'))
    return data


def restore(data, procedure):
    errors = []
    def attempt(function):
        try:
            function()
        except Exception as exc:
            errors.append(str(exc))
    attempt(lambda: cmds.undoInfo(stateWithoutFlush=data['undo']))
    attempt(lambda: cmds.namespace(setNamespace=data['namespace']))
    attempt(lambda: cmds.autoKeyframe(state=data['autokey']))
    attempt(lambda: cmds.currentUnit(linear=data['linear']))
    attempt(lambda: cmds.evaluationManager(mode=data['evaluation'][0]))
    attempt(lambda: cmds.selectPref(trackSelectionOrder=data['track']))
    attempt(lambda: cmds.refresh(suspend=data['suspend']))
    for key, value in data['options'].items():
        def option(key=key, value=value):
            if value is None:
                cmds.optionVar(remove=key)
            elif isinstance(value, str):
                cmds.optionVar(stringValue=(key, value))
            elif isinstance(value, float):
                cmds.optionVar(floatValue=(key, value))
            else:
                cmds.optionVar(intValue=(key, int(value)))
        attempt(option)
    for plugin in cmds.pluginInfo(query=True, listPlugins=True) or []:
        attempt(lambda plugin=plugin: cmds.pluginInfo(plugin, edit=True, autoload=data['plugins'].get(plugin, False)))
    if 'cache' in data:
        from maya.plugin.evaluator.cache_preferences import CachePreferenceEnabled
        attempt(lambda: CachePreferenceEnabled().set_value(data['cache']))
        attempt(lambda: mel.eval('setTimeSliderVisible(' + str(int(data['slider'])) + ');'))
    if procedure not in ('set_currenttime_to_mid_selection',):
        attempt(lambda: cmds.currentTime(data['time']))
    if procedure != 'barn_sel_set_member' and not (procedure == 'return_constrained_object'):
        def selection():
            surviving = [n for n in data['selection'] if cmds.objExists(n)]
            cmds.select(surviving, replace=True) if surviving else cmds.select(clear=True)
        attempt(selection)
    if errors:
        raise RuntimeError('Native caller environment restoration failed: ' + '; '.join(errors))


def execute(p):
    plan = preflight(p)
    if p['action'] == 'inspect':
        return plan
    procedure = p['procedure']
    if cmds.about(batch=True) and procedure not in BATCH_PROCEDURES:
        raise RuntimeError('Complete original workflow needs real Maya timeline/GraphEditor/UI; no batch simulation')
    if procedure in UI_PROCEDURES:
        load_vendor()
        initialize_globals(p)
        mel.eval(p['command'])
        return dict(plan, native_ui=True, runtime_effects='Native preferences/layer selection and callbacks intentionally follow vendor UI')
    load_vendor()
    initialize_globals(p)
    state = snapshot()
    before = uuids()
    depth = [0]
    def command_callback(command, *args):
        if re.match(r'\s*undoInfo\b', command):
            if re.search(r'-(?:ock|openChunk)\b', command):
                depth[0] += 1
            if re.search(r'-(?:cck|closeChunk)\b', command):
                depth[0] -= 1
    callback = om.MCommandMessage.addCommandCallback(command_callback)
    try:
        cmds.namespace(setNamespace=':')
        cmds.selectPref(trackSelectionOrder=True)
        cmds.autoKeyframe(state=False)
        if plan['objects']:
            cmds.select(plan['objects'], replace=True)
        result = mel.eval(p['command'])
        selected = cmds.ls(selection=True, long=True) or []
        created = sorted(uuids() - before)
        if depth[0] < 0:
            raise RuntimeError('Native procedure closed an outer Undo chunk; inspect scene and native warning')
        return dict(plan, native_result=result, created_node_uuids=created, native_result_selection=selected, scene_undo_limitations='Native callbacks/motion-trail disable-Undo and preference/plugin effects are not guaranteed by Undo')
    finally:
        om.MMessage.removeCallback(callback)
        try:
            for unused in range(max(0, depth[0])):
                cmds.undoInfo(closeChunk=True)
        finally:
            restore(state, procedure)


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for full original OverRig UI')
    if cmds.window('basic_anim_scripts_ui', exists=True) or cmds.dockControl('basicOverRigScripts', exists=True):
        raise RuntimeError('Original OverRig UI already exists; use or close it')
    load_vendor()
    initialize_globals({'rotate_order': 0})
    mel.eval('base_OverRig_scripts(1);')
    return 'basic_anim_scripts_ui'
