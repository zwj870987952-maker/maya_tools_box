import copy
from functools import wraps
import getpass
import json
import uuid

_ACTIVE = False
_ARGS = {}
_PREFIX = ''
_GROUPS = {}
_TARGETS = set()
_OWNED = set()
_CURVES = set()
_BASE = set()
_OWNER = None
_UI = None
TAG = 'mtbKeyframeOverlapRecord'


def mc():
    from maya import cmds
    return cmds


def machine_check():
    # Preserve the supplied source's placeholder handling; do not fake another user.
    original = '$usr_orig$'
    if 'usr_orig' in original:
        original = getpass.getuser()
    if original != getpass.getuser():
        raise ValueError('原作者仅允许原用户机器运行')


def require_active():
    if not _ACTIVE:
        raise RuntimeError('场景写入须经KeyframeOverlapTool.run')


def identity(node):
    c = mc()
    ref = c.referenceQuery(node, referenceNode=True) if c.referenceQuery(node, isNodeReferenced=True) else None
    return c.ls(node, uuid=True)[0], c.ls(ref, uuid=True)[0] if ref else ''


def scene_nodes():
    return {identity(n): n for n in mc().ls(long=True) or []}


def records():
    c = mc()
    output = []
    for plug in c.ls('*.' + TAG, recursive=True) or []:
        n = plug.rsplit('.', 1)[0]
        if c.nodeType(n) == 'network':
            data = json.loads(c.getAttr(plug))
            data['record_id'] = c.ls(n, uuid=True)[0]
            data['_owner'] = n
            output.append(data)
    return output


def get_record(record_id):
    rows = [x for x in records() if x['record_id'] == record_id]
    if len(rows) != 1:
        raise ValueError('需要唯一有效record_id')
    return rows[0]


def controls(row):
    c = mc()
    nodes = []
    for i in range(row['control_count']):
        targets = c.listConnections(row['_owner'] + '.controls[%d]' % i, source=True, destination=False) or []
        if len(targets) != 1:
            raise ValueError('record控制器消息缺失')
        nodes.append(c.ls(targets[0], long=True)[0])
    return nodes


def validate_graph(row):
    c = mc()
    owner = row['_owner']
    if c.referenceQuery(owner, isNodeReferenced=True) or c.lockNode(owner, query=True, lock=True)[0]:
        raise ValueError('record引用/锁')
    nodes = c.listConnections(owner + '.members', source=True, destination=False, shapes=True) or []
    owned = {identity(n) for n in nodes}
    targets = {identity(n) for n in controls(row)}
    for n in nodes:
        if c.referenceQuery(n, isNodeReferenced=True) or c.lockNode(n, query=True, lock=True)[0]:
            raise ValueError('自有图引用/锁')
        if c.listConnections(n + '.mtbKfoOwner', source=True, destination=False) != [owner]:
            raise ValueError('成员owner不匹配')
        for child in c.listRelatives(n, allDescendents=True, fullPath=True) or []:
            if identity(child) not in owned:
                raise ValueError('Foreign descendant: ' + n + ' -> ' + child)
        for consumer in c.listConnections(n, source=False, destination=True) or []:
            if consumer != owner and identity(consumer) not in owned | targets and c.nodeType(consumer) not in ('objectSet', 'shadingEngine'):
                raise ValueError('自有图有外部输出')
        for driver in c.listConnections(n, source=True, destination=False) or []:
            if driver == owner or identity(driver) in owned | targets or c.nodeType(driver) == 'time':
                continue
            # User may key the red editable locator after creation. Accept only
            # local unshared direct curves feeding the same owned graph.
            if not c.nodeType(driver).startswith('animCurve') or c.referenceQuery(driver, isNodeReferenced=True) or c.lockNode(driver, query=True, lock=True)[0]:
                raise ValueError('自有图有外部驱动')
            if any(identity(out) not in owned | targets for out in c.listConnections(driver + '.output', source=False, destination=True) or []):
                raise ValueError('Unshared curve check: ' + n + ' <- ' + driver + ' -> ' + repr(c.listConnections(driver + '.output', source=False, destination=True)))
            owned.add(identity(driver))
    return owned


def helper_name(node, suffix):
    require_active()
    return _PREFIX + identity(node)[0].replace('-', '') + suffix


def clear_transients():
    require_active()
    # New run prefix cannot refer to existing foreign scene content. Native
    # particle cleanup itself uses scope-checked explicit ls/delete below.
    return None


def discover():
    require_active()
    _OWNED.update(set(scene_nodes()) - _BASE - _TARGETS - _CURVES)


def mark(owner, nodes):
    c = mc()
    current = c.getAttr(owner + '.members', multiIndices=True) or []
    index = max(current, default=-1) + 1
    for n in nodes:
        if n == owner:
            continue
        if not c.attributeQuery('mtbKfoOwner', node=n, exists=True):
            c.addAttr(n, longName='mtbKfoOwner', attributeType='message')
            c.connectAttr(owner + '.message', n + '.mtbKfoOwner')
            c.connectAttr(n + '.message', owner + '.members[%d]' % index)
            index += 1


def business_bridge(action):
    def decorate(function):
        @wraps(function)
        def call(self, param):
            if _ACTIVE:
                return function(self, param)
            return UIBridge().invoke(action, param)
        return call
    return decorate


class UIBridge:
    def invoke(self, action, param):
        from .tool import KeyframeOverlapTool, DEFAULTS
        args = {key: value for key, value in param.items() if key in DEFAULTS}
        args.update(action=action, objects=param.get('select_ls', []))
        if action == 'bake':
            selected = {identity(n) for n in args['objects']}
            found = [x for x in records() if {identity(n) for n in controls(x)} == selected]
            if len(found) != 1:
                raise ValueError('选中完整一组自有Overlap控制器后Bake')
            args['record_id'] = found[0]['record_id']
        result = KeyframeOverlapTool().run(**args)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data

    def kf_overlap(self, param):
        return self.invoke('create', param)

    def kf_bake_animation(self, param):
        return self.invoke('bake', param)


def preset(ui, action):
    c = mc()
    current = c.optionMenu(ui.element['preset_om'], query=True, value=True)
    if action == 'load_preset':
        data = ui.cfg_data if current == 'Defualt' else ui._presets[current]
        ui.mode_current, ui.is_smoothness, ui.is_aim_invert = data['mode_name'], data['smoothness'], data['aim_invert']
        c.optionMenu(ui.element['mode_om'], edit=True, value=data['mode_transform'])
        for key in ('distance', 'dynamic', 'offset'):
            c.floatSlider(ui.element[key + '_fs'], edit=True, value=data[key])
        ui.update_ui()
        ui.update_ui(slider=True)
        return
    if action == 'delete_preset':
        if current != 'Defualt' and c.confirmDialog(title='Delete session preset', message=current, button=['Confirm', 'Cancel'], defaultButton='Cancel') == 'Confirm':
            ui._presets.pop(current, None)
            ui.update_ui()
        return
    decision = c.promptDialog(title='Session preset', message='Preset name', text=current, button=['Save', 'Cancel'], defaultButton='Save', cancelButton='Cancel')
    if decision != 'Save':
        return
    name = c.promptDialog(query=True, text=True)
    if not name or name == 'Defualt' or name in ui._presets:
        raise ValueError('需要新session preset名，不隐式覆盖')
    if action == 'rename_preset':
        if current == 'Defualt':
            return
        ui._presets[name] = ui._presets.pop(current)
    else:
        ui._presets[name] = copy.deepcopy(ui.get_captured_param())
    ui.update_ui()
    c.optionMenu(ui.element['preset_om'], edit=True, value=name)


def execute(args):
    global _ACTIVE, _ARGS, _PREFIX, _GROUPS, _TARGETS, _OWNED, _CURVES, _BASE, _OWNER, _UI
    c = mc()
    if args['action'] == 'inventory':
        return {'records': [{k: v for k, v in x.items() if not k.startswith('_')} for x in records()]}
    from . import native
    if args['action'] == 'open_ui':
        _UI = native.kf_overlap()
        _UI.show_ui()
        return {'window': _UI.win_id}
    current, selection, auto, namespace = c.currentTime(query=True), c.ls(selection=True, long=True) or [], c.autoKeyframe(query=True, state=True), c.namespaceInfo(currentNamespace=True)
    evaluation, suspended = c.evaluationManager(query=True, mode=True)[0], c.refresh(query=True, suspend=True)
    row = args['_row']
    _PREFIX = row['prefix'] if row else 'mtbKfo_' + uuid.uuid4().hex + '_'
    _GROUPS = {key: _PREFIX + value for key, value in {'main': 'overlap_grp', 'editable': 'editable_loc_grp', 'origin': 'origin_loc_grp', 'result': 'result_loc_grp'}.items()}
    _BASE = set(scene_nodes())
    _TARGETS = {identity(n) for n in args['objects']}
    _OWNED = validate_graph(row) if row else set()
    _CURVES = {identity(curve) for n in args['objects'] for curve in c.ls(c.listHistory(n, pruneDagObjects=True) or [], type='animCurve') or []} - _OWNED
    _OWNER = row['_owner'] if row else None
    _ACTIVE, _ARGS = True, args
    try:
        c.autoKeyframe(state=False)
        c.namespace(setNamespace=':')
        c.evaluationManager(mode='off')
        system = native.loc_delay_system()
        param = dict(args, select_ls=args['objects'])
        if args['action'] == 'create':
            _OWNER = c.createNode('network', name=_PREFIX + 'record')
            c.addAttr(_OWNER, longName=TAG, dataType='string')
            c.addAttr(_OWNER, longName='controls', attributeType='message', multi=True)
            c.addAttr(_OWNER, longName='members', attributeType='message', multi=True)
            data = {'prefix': _PREFIX, 'control_count': len(args['objects']), 'mode_name': args['mode_name'], 'start': args['start'], 'end': args['end'], 'state': 'working'}
            c.setAttr(_OWNER + '.' + TAG, json.dumps(data), type='string')
            for index, n in enumerate(args['objects']):
                c.connectAttr(n + '.message', _OWNER + '.controls[%d]' % index)
            system.kf_overlap(param)
            data['state'] = 'editable'
            c.setAttr(_OWNER + '.' + TAG, json.dumps(data), type='string')
            discover()
            mark(_OWNER, [n for key, n in scene_nodes().items() if key in _OWNED])
            return {'record_id': c.ls(_OWNER, uuid=True)[0], 'controls': args['objects'], 'editable_group': _GROUPS['editable'], 'mode_name': args['mode_name']}
        # Link any direct unshared curve the user added to the editable helper.
        mark(_OWNER, [n for key, n in scene_nodes().items() if key in _OWNED])
        system.kf_bake_animation(param)
        remaining = [n for key, n in scene_nodes().items() if key in _OWNED and c.nodeType(n) in ('pairBlend', 'pointConstraint', 'orientConstraint', 'aimConstraint')]
        from .proxy import cmds as guarded
        if remaining:
            guarded.delete(remaining)
        c.delete(_OWNER)
        _OWNER = None
        return {'baked': args['objects'], 'range': [args['start'], args['end']], 'removed_record_id': row['record_id']}
    finally:
        try:
            discover()
            if _OWNER and c.objExists(_OWNER):
                mark(_OWNER, [n for key, n in scene_nodes().items() if key in _OWNED])
        finally:
            try:
                c.refresh(suspend=suspended)
                c.evaluationManager(mode=evaluation)
                c.currentTime(current)
                if (c.ls(selection=True, long=True) or []) != selection:
                    c.select(selection, replace=True) if selection else c.select(clear=True)
                c.namespace(setNamespace=namespace)
                c.autoKeyframe(state=auto)
            finally:
                _ACTIVE, _ARGS, _OWNED, _TARGETS, _CURVES, _BASE, _OWNER = False, {}, set(), set(), set(), set(), None
