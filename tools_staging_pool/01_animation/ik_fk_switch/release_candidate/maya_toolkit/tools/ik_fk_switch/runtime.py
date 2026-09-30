import ast
from functools import wraps
import json
import os
from pathlib import Path
import tempfile
import uuid

OWNER = 'maya_toolkit.ik_fk_switch.v1'
_ACTIVE = False
_ARGS = {}
_CALLBACKS = {}
_HELPERS = set()
_CONTROLS = set()
_PREFIX = ''


def cmds_module():
    from maya import cmds
    return cmds


def identity(node):
    cmds = cmds_module()
    return (cmds.ls(node, uuid=True)[0], cmds.referenceQuery(node, referenceNode=True) if cmds.referenceQuery(node, isNodeReferenced=True) else '')


def snapshot():
    return {identity(node): node for node in cmds_module().ls(long=True) or []}


def require_active():
    if not _ACTIVE:
        raise RuntimeError('场景写入须标准IKFKTool.run')


def literal_data(value):
    result = ast.literal_eval(value)
    if not isinstance(result, (list, tuple)) or len(result) != 3 or any(type(n) not in (int, float) for n in result):
        raise ValueError('rotation offset须三数值，不执行Store代码')
    return result


def records():
    cmds = cmds_module()
    return [{'record_id': cmds.ls(node, uuid=True)[0], 'node': node} for node in cmds.ls(type='transform') or [] if cmds.objExists(node + '.mtbIKFKOwner') and cmds.getAttr(node + '.mtbIKFKOwner') == OWNER]


def ensure_store(node):
    cmds = cmds_module()
    if not cmds.objExists(node + '.mtbIKFKOwner') or cmds.getAttr(node + '.mtbIKFKOwner') != OWNER:
        raise ValueError('不是本候选自有Store')
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0] or cmds.listRelatives(node, children=True):
        raise ValueError('Store引用/锁定/有外部子节点')
    # Store owns only metadata; scene-driving outgoing connections are not allowed.
    if cmds.listConnections(node, source=False, destination=True):
        raise ValueError('Store有外部使用者')
    for name in cmds.listAttr(node, userDefined=True) or []:
        if name != 'mtbIKFKOwner' and cmds.getAttr(node + '.' + name, lock=True):
            raise ValueError('Store字段锁定: ' + name)


def load_record(identifier):
    from .tool import CONTROLS, DEFAULTS
    cmds = cmds_module()
    matches = cmds.ls(identifier, long=True) or []
    if len(matches) != 1:
        raise ValueError('Store缺失/UUID不唯一')
    node = matches[0]
    ensure_store(node)
    fields = json.loads(cmds.getAttr(node + '.mtbIKFKData'))
    for field in CONTROLS:
        values = cmds.listConnections(node + '.' + field + 'Message', source=True, destination=False) or []
        if len(values) != 1:
            raise ValueError('Store控制器来源缺失: ' + field)
        resolved = cmds.ls(values[0], long=True) or []
        if len(resolved) != 1:
            raise ValueError('Store控制器不唯一: ' + field)
        fields[field] = resolved[0]
    return {'node': node, 'fields': fields}


def matching_store(fields):
    for row in records():
        data = load_record(row['record_id'])
        value = data['fields']
        if identity(value['fkwrist']) == identity(fields['fkwrist']) and value['side'] == fields['side'] and value['limb'] == fields['limb']:
            return row['node']
    return None


def store_fields(args):
    from .tool import CONTROLS
    return {n: args[n] for n in CONTROLS + ('switchAttr', 'switch0isfk', 'switchAttrRange', 'rotOffset', 'side', 'limb', 'bendKneeAxis')}


def store_namespace(control):
    return control.split('|')[-1].rsplit(':', 1)[0].replace(':', '__') if ':' in control.split('|')[-1] else 'local'


def save_store(args):
    from .tool import CONTROLS
    cmds = cmds_module()
    fields = store_fields(args)
    node = args.get('existing_store')
    if node:
        ensure_store(node)
        for name in CONTROLS:
            inputs = cmds.listConnections(node + '.' + name + 'Message', source=True, destination=False, plugs=True) or []
            for plug in inputs:
                cmds.disconnectAttr(plug, node + '.' + name + 'Message')
    else:
        node = cmds.createNode('transform', name=store_namespace(fields['fkwrist']) + '__' + fields['side'] + '_' + fields['limb'] + '_IKFKSTORE')
        cmds.addAttr(node, longName='mtbIKFKOwner', dataType='string')
        cmds.setAttr(node + '.mtbIKFKOwner', OWNER, type='string', lock=True)
        cmds.addAttr(node, longName='mtbIKFKData', dataType='string')
        for name in CONTROLS:
            cmds.addAttr(node, longName=name + 'Message', attributeType='message')
        for name in fields:
            cmds.addAttr(node, longName='attrRange' if name == 'switchAttrRange' else name, dataType='string')
    cmds.setAttr(node + '.mtbIKFKData', json.dumps(fields, ensure_ascii=False), type='string')
    for name, value in fields.items():
        cmds.setAttr(node + '.' + ('attrRange' if name == 'switchAttrRange' else name), str(int(value)) if type(value) is bool else str(value), type='string')
    for name in CONTROLS:
        cmds.connectAttr(fields[name] + '.message', node + '.' + name + 'Message')
    return {'node': node, 'record_id': cmds.ls(node, uuid=True)[0], 'fields': fields}


def save_from_native(limb, side, fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis):
    from .tool import plan
    require_active()
    args = dict(action='store', limb=limb, side=side, fkwrist=str(fkwrist), fkellbow=str(fkellbow), fkshldr=str(fkshldr), ikwrist=str(ikwrist), ikpv=str(ikpv), switchCtrl=str(switchCtrl), switchAttr=str(switchAttr), switch0isfk=bool(switch0isfk), switchAttrRange=int(switchAttrRange), rotOffset=list(rotOffset), bendKneeAxis=bendKneeAxis, overwrite_store=_ARGS['overwrite_store'], allow_reference_edits=_ARGS['allow_reference_edits'])
    # Standard parent callback has already checked fields; allow this metadata suboperation.
    old = _ACTIVE
    globals()['_ACTIVE'] = False
    try:
        checked = plan(**args)
    finally:
        globals()['_ACTIVE'] = old
    row = save_store(checked)
    import pymel.core as pm
    return pm.PyNode(row['node'])


def find_store_from_selection():
    import pymel.core as pm
    selected = pm.selected()
    if not selected:
        return []
    for row in records():
        data = load_record(row['record_id'])
        if identity(str(selected[0])) in {identity(data['fields'][name]) for name in ('fkshldr', 'fkellbow', 'fkwrist', 'ikwrist', 'ikpv', 'switchCtrl')}:
            return pm.PyNode(row['node'])
    return []


def load_store(ns, limb, side):
    node = find_store_from_selection()
    if not node:
        return {}
    data = load_record(str(node))['fields']
    if data['limb'] != limb or data['side'] != side:
        for row in records():
            other = load_record(row['record_id'])['fields']
            if store_namespace(other['fkwrist']) == store_namespace(data['fkwrist']) and other['limb'] == limb and other['side'] == side:
                data = other
                break
        else:
            return {}
    return {('attrRange' if key == 'switchAttrRange' else key): str(int(value)) if type(value) is bool else str(value) for key, value in data.items() if key != 'limb'}


def export_data():
    return [load_record(row['record_id'])['fields'] for row in records()]


def export_json(args):
    path = Path(args['file_path'])
    payload = {'format': OWNER, 'stores': args['stores']}
    path.parent.mkdir(parents=True, exist_ok=True)
    if not args['overwrite_file']:
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    else:
        descriptor, temporary = tempfile.mkstemp(prefix='ikfk_store_', suffix='.json', dir=str(path.parent))
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
            os.replace(temporary, path)
        finally:
            if Path(temporary).is_file():
                Path(temporary).unlink()
    return {'file_path': str(path), 'store_count': len(args['stores'])}


def ui_operation(name):
    def decorate(function):
        @wraps(function)
        def callback(target, *positional, **keyword):
            if _ACTIVE:
                return function(target, *positional, **keyword)
            from maya import cmds
            from .tool import IKFKTool, CONTROLS
            values = target.getAndCheckInputWin()
            fields = {n: str(v) for n, v in zip(CONTROLS, values[:6])}
            fields.update(switchAttr=str(values[6]), switch0isfk=bool(values[7]), switchAttrRange=int(values[8]), rotOffset=list(values[9]), bendKneeAxis=str(values[10]))
            from . import native
            choice = str(cmds.radioCollection(native.win + 'limbRadioCollt', query=True, select=True)).split('_')
            fields.update(side=choice[1], limb=choice[2])
            referenced = any(cmds.referenceQuery(fields[n], isNodeReferenced=True) for n in CONTROLS)
            if referenced:
                if cmds.confirmDialog(title='Reference edits', message='Run matching/key/Store edits on selected referenced controls in this backup scene?', button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No') != 'Yes':
                    return None
                fields['allow_reference_edits'] = True
            existing = matching_store(fields) if name == 'saveIkFkCtrlsWin' else None
            if existing:
                if cmds.confirmDialog(title='Update owned Store', message='Replace this candidate-owned Store metadata?', button=['Yes', 'No'], defaultButton='No') != 'Yes':
                    return None
                fields['overwrite_store'] = True
            ticket = uuid.uuid4().hex
            _CALLBACKS[ticket] = {'function': function, 'target': target, 'positional': positional, 'keyword': keyword, 'fields': fields}
            try:
                result = IKFKTool().run(action='native_callback', callback_ticket=ticket)
                if not result.success:
                    raise RuntimeError(result.message)
                return result.data.get('native_result')
            finally:
                _CALLBACKS.pop(ticket, None)
        return callback
    return decorate


def file_ui(action):
    from maya import cmds
    from .tool import IKFKTool
    names = cmds.fileDialog2(fileFilter='Candidate Store JSON (*.json)', fileMode=0 if action == 'export_store' else 1) or []
    if not names:
        return None
    args = dict(action=action, file_path=names[0])
    if action == 'export_store' and Path(names[0]).exists():
        if cmds.confirmDialog(title='Overwrite JSON', message='Overwrite this JSON file? Maya Undo cannot restore it.', button=['Yes', 'No'], defaultButton='No') != 'Yes':
            return None
        args['overwrite_file'] = True
    if action == 'import_store':
        policy = cmds.confirmDialog(title='Import policy', message='Update only candidate-owned colliding Store metadata?', button=['Update owned', 'Keep existing', 'Cancel'], defaultButton='Keep existing')
        if policy == 'Cancel':
            return None
        args['overwrite_store'] = policy == 'Update owned'
        args['allow_reference_edits'] = cmds.confirmDialog(title='Reference edits', message='Allow metadata message connections to referenced controls?', button=['Yes', 'No'], defaultButton='No') == 'Yes'
    result = IKFKTool().run(**args)
    if not result.success:
        raise RuntimeError(result.message)
    return result.data


def execute(args):
    global _ACTIVE, _ARGS, _HELPERS, _CONTROLS, _PREFIX
    from .tool import CONTROLS
    cmds = cmds_module()
    action = args['action']
    if action == 'records':
        return {'records': records()}
    if action == 'load':
        return load_record(args['record_id'])
    if action == 'export_store':
        return export_json(args)
    if action == 'open_ui':
        from . import native
        native.FkIk_UI()
        return {'window': 'mtbIKFK_UI'}
    current = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    auto = cmds.autoKeyframe(query=True, state=True)
    namespace = cmds.namespaceInfo(currentNamespace=True)
    _ACTIVE, _ARGS, _HELPERS, _PREFIX = True, args, set(), 'mtbIKFK_' + uuid.uuid4().hex + '_'
    _CONTROLS = {identity(args[n]) for n in CONTROLS} if all(args.get(n) for n in CONTROLS) else set()
    try:
        if action == 'store':
            return save_store(args)
        if action == 'import_store':
            return {'records': [save_store(row) for row in args['stores']]}
        if action == 'switch':
            value = args['switchAttrRange'] if (args['direction'] == 'to_ik') == args['switch0isfk'] else 0
            cmds.setAttr(args['switchCtrl'] + '.' + args['switchAttr'], value)
            return {'switch_value': value}
        if action == 'key':
            for n in CONTROLS[:3] if args['direction'] == 'to_fk' else CONTROLS[3:5]:
                cmds.setKeyframe(args[n], shape=False, respectKeyable=True, minimizeRotation=True)
            cmds.setKeyframe(args['switchCtrl'], attribute=args['switchAttr'])
            return {'keyed': args['direction']}
        from . import native
        if action == 'native_callback':
            item = _CALLBACKS[args['callback_ticket']]
            value = item['function'](item['target'], *item['positional'], **item['keyword'])
            return {'native_result': value}
        controls = [args[n] for n in ('fkwrist', 'fkellbow', 'fkshldr', 'ikwrist', 'ikpv', 'switchCtrl', 'switchAttr')]
        options = {n: args[n] for n in ('switch0isfk', 'switchAttrRange', 'rotOffset', 'side', 'limb')}
        options['switch0isfk'] = int(options['switch0isfk'])
        function = native.ikfkMatch if args['direction'] == 'to_fk' else native.fkikMatch
        if args['direction'] == 'to_fk':
            options['bendKneeAxis'] = args['bendKneeAxis']
        if action == 'match':
            function(*controls, **options)
            return {'matched': args['direction']}
        cmds.autoKeyframe(state=False)
        target = [args[n] for n in CONTROLS[:3] if args['direction'] == 'to_fk'] if args['direction'] == 'to_fk' else [args[n] for n in CONTROLS[3:5]]
        if args['keys_only']:
            cmds.cutKey(target, time=(min(args['frames']), max(args['frames'])))
        for frame in args['frames']:
            cmds.currentTime(frame)
            cmds.cutKey(target, time=(frame, frame))
            function(*controls, **options)
            cmds.setKeyframe(target, shape=False)
        return {'baked_frames': args['frames'], 'direction': args['direction']}
    finally:
        try:
            from .proxy import cleanup_helpers
            cleanup_helpers()
        finally:
            try:
                if cmds.currentTime(query=True) != current:
                    cmds.currentTime(current)
                cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)
                cmds.namespace(setNamespace=namespace)
                cmds.autoKeyframe(state=auto)
            finally:
                _ACTIVE, _ARGS, _HELPERS, _CONTROLS = False, {}, set(), set()
