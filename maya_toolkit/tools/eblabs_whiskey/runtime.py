"""Preserve the native suite; own callback lifetime, scope, and preference I/O."""
import copy
from functools import wraps
import json
import os
from pathlib import Path
import tempfile
import uuid

_ACTIVE = False
_MODE = ''
_ARGS = {}
_AUTO = False
_ERRORS = []
_CALLBACKS = {}
_SESSION = None
_IDS = set()


def preferences():
    global _SESSION
    if _SESSION is None:
        path = Path(__file__).parent / 'upstream/eblabs_prefs/whiskey.prefs'
        _SESSION = json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else {}
    return copy.deepcopy(_SESSION)


def load_preferences(cls):
    cls.data = preferences()
    return cls.data


def save_preferences(cls):
    global _SESSION
    _SESSION = copy.deepcopy(cls.data)
    return copy.deepcopy(_SESSION)


def read_json(filename):
    if str(filename).startswith('session://'):
        return preferences()
    if not _ACTIVE or _ARGS.get('action') != 'import_preferences' or str(filename) != _ARGS['file_path']:
        raise ValueError('仅显式import_preferences允许读取外部偏好')
    return json.loads(Path(filename).read_text(encoding='utf-8-sig'))


def write_json(filename, dictionary):
    global _SESSION
    if str(filename).startswith('session://'):
        _SESSION = copy.deepcopy(dictionary)
        return copy.deepcopy(_SESSION)
    if not _ACTIVE or _ARGS.get('action') != 'export_preferences' or str(filename) != _ARGS['file_path']:
        raise ValueError('仅显式export_preferences允许写外部偏好')
    target = Path(filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create when overwrite is false; an intervening file is never replaced.
    if not _ARGS['overwrite_file']:
        with target.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(dictionary, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        return str(target)
    descriptor, temporary = tempfile.mkstemp(prefix='whiskey_', suffix='.json', dir=str(target.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(dictionary, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, target)
    finally:
        if Path(temporary).is_file():
            Path(temporary).unlink()
    return str(target)


def require_active():
    if not _ACTIVE:
        raise RuntimeError('场景写入须经WhiskeyTool.run标准调用')


def note_error(error):
    if _ACTIVE:
        _ERRORS.append(str(error))


def native_operation(name):
    def decorate(function):
        @wraps(function)
        def callback(target, *positional, **keyword):
            if _ACTIVE:
                return function(target, *positional, **keyword)
            from .tool import WhiskeyTool
            ticket = uuid.uuid4().hex
            _CALLBACKS[ticket] = (function, target, positional, keyword)
            try:
                result = WhiskeyTool().run(action='native_callback', callback_ticket=ticket)
                if not result.success:
                    raise RuntimeError(name + ': ' + result.message + '; ' + '; '.join(result.errors))
                return result.data.get('native_result')
            finally:
                _CALLBACKS.pop(ticket, None)
        return callback
    return decorate


def flatten(items):
    for item in items:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        elif isinstance(item, str):
            yield item


def check_write(command, positional, keyword):
    from maya import cmds
    from .tool import scope
    require_active()
    if command == 'delete':
        raise ValueError('拒绝原脚本失败后的上游节点删除；请检查并Undo')
    if command == 'keyTangent' and (keyword.get('global') or keyword.get('g')):
        return  # Explicit native tangent button changes a global preference.
    values = list(flatten(positional))
    if command == 'animLayer':
        if not keyword.get('edit') and not keyword.get('e'):
            raise ValueError('候选不创建/接管动画层')
        # Native Smash temporarily selects every layer; restore these flags finally.
        if not keyword.get('removeAttribute'):
            return
        values = [keyword['removeAttribute']]
    elif command == 'disconnectAttr':
        values = values[-1:]
    elif command == 'connectAttr':
        raise ValueError('原套件不需要新图连接')
    if not values:
        raise ValueError('拒绝隐式范围的场景写入: ' + command)
    # Refresh new keys' curves without admitting unrelated nodes or shared drivers.
    _, curves = scope(_ARGS['objects'], _ARGS['attributes'], _ARGS.get('allow_driven', False))
    allowed = _IDS | {cmds.ls(c, uuid=True)[0] for c in curves}
    for value in values:
        node = value.split('.', 1)[0]
        matches = cmds.ls(node, long=True) or []
        if len(matches) != 1 or cmds.ls(matches[0], uuid=True)[0] not in allowed:
            raise ValueError('写入超出预检对象/曲线范围: ' + value)
        if cmds.referenceQuery(matches[0], isNodeReferenced=True) or cmds.lockNode(matches[0], query=True, lock=True)[0]:
            raise ValueError('写入引用/锁定节点: ' + value)
        if '.' in value and cmds.objExists(value) and cmds.getAttr(value, lock=True):
            raise ValueError('写入锁定通道: ' + value)
        if command == 'setAttr' and '.' in value and not cmds.nodeType(matches[0]).startswith('animCurve'):
            attribute = value.split('.', 1)[1]
            if _ARGS['attributes']:
                canonical = cmds.attributeQuery(attribute, node=matches[0], longName=True)
                names = {cmds.attributeQuery(a, node=matches[0], longName=True) for a in _ARGS['attributes']}
                if canonical not in names:
                    raise ValueError('写入超出明确通道: ' + value)


def engine(native, args, kind=None):
    kind = kind or args['slider_kind']
    item = object.__new__(getattr(native, 'slider_' + kind))
    item.pinState = False
    item.bufferSelection = []
    item.data = {}
    item.getSelected = lambda: list(args['objects'])
    item.getSelectedChannels = lambda *unused, **ignored: list(args['attributes'])
    item.getSliderValue = lambda: float(args['value'])
    item.getMultiplier = lambda *unused, **ignored: 1.0
    item.getUseAllLayersState = lambda: args['use_all_layers']
    item.snapShotData = copy.deepcopy(args['snapshot_data'])
    return item


def execute(args):
    global _ACTIVE, _MODE, _ARGS, _AUTO, _ERRORS, _IDS, _SESSION
    from maya import cmds
    from . import native
    if args['action'] in ('import_preferences', 'export_preferences'):
        _ARGS, _ACTIVE = args, True
        try:
            if args['action'] == 'import_preferences':
                _SESSION = read_json(args['file_path'])
                native.Prefs.data = copy.deepcopy(_SESSION)
            else:
                write_json(args['file_path'], preferences())
            return {'action': args['action'], 'file_path': args['file_path'], 'warnings': ['偏好文件/目录写入不属于Maya Undo；导入只更改会话偏好，重新打开UI使用新配置']}
        finally:
            _ACTIVE, _ARGS = False, {}
    if args['action'] == 'open_ui':
        native.window.load()
        return {'window': 'mtbWK_whisKEY_Pro', 'warnings': ['完整原生UI待真人验收；偏好只存会话，持久化使用export_preferences']}
    current = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    namespace = cmds.namespaceInfo(currentNamespace=True)
    auto = cmds.autoKeyframe(query=True, state=True)
    layers = {n: (cmds.animLayer(n, query=True, selected=True), cmds.animLayer(n, query=True, preferred=True)) for n in cmds.ls(type='animLayer') or []}
    _ARGS, _AUTO, _ERRORS = dict(args), auto, []
    _MODE = 'gui' if args['action'] == 'native_callback' else 'api'
    if _MODE == 'gui':
        function = _CALLBACKS[args['callback_ticket']][0]
        _ARGS['allow_driven'] = function.__name__ == 'smashBaker'
    else:
        _ARGS['allow_driven'] = args['action'] == 'smash_bake'
    _IDS = {cmds.ls(n, uuid=True)[0] for n in args['objects']}
    _IDS.update(cmds.ls(s, uuid=True)[0] for n in args['objects'] for s in cmds.listRelatives(n, shapes=True, fullPath=True) or [])
    _ACTIVE = True
    result, collected = None, {}
    try:
        cmds.autoKeyframe(state=False)
        if _MODE == 'api':
            cmds.select(args['objects'], replace=True) if args['objects'] else cmds.select(clear=True)
        action = args['action']
        if action == 'native_callback':
            function, target, positional, keyword = _CALLBACKS[args['callback_ticket']]
            if function.__name__ == 'inbetween':
                collected = target.collectData()
            result = function(target, *positional, **keyword)
        elif action == 'inbetween':
            collected = native.Hotkeys.collectData()
            native.Hotkeys.inbetween(args['value'], args['use_set_value'], args['from_current_value'])
        elif action == 'capture_snapshot':
            item = engine(native, args, 'snapshot')
            item.collectSnapshotData()
            result = item.getSnapshotData()
        elif action == 'slider':
            item = engine(native, args)
            layered = not args['use_all_layers'] and args['slider_kind'] == 'tween'
            item.collectData_layers() if layered else item.collectData()
            collected = item.data
            if layered:
                item.slider_exec_layers(overrideRatio=float(args['value']), useSetValue=args['use_set_value'], fromCurrentValue=args['from_current_value'])
            else:
                item.slider_exec(overrideRatio=float(args['value']), useSetValue=args['use_set_value'], fromCurrentValue=args['from_current_value'])
        elif action == 'set_keys':
            native.Functions.setKeyframe(objects=list(args['objects']), special=args['special'], useHighlighted=True)
        elif action == 'rekey':
            native.Functions.rekeyOnKeys(objects=list(args['objects']), matchLast=args['match_last'])
        elif action == 'clean_subframes':
            native.Functions.cleanSubframeKeys(selection=list(args['objects']))
        elif action == 'remove_boring':
            native.Functions.removeBoringKeys(selection=list(args['objects']))
        elif action == 'smash_bake':
            native.Functions.smashBaker(list(args['objects']), args['start'], args['end'])
        elif action == 'set_tangent':
            native.Functions.setKeyType(args['tangent'])
        else:
            raise ValueError('未知执行action')
        if auto and collected and (action == 'inbetween' or action == 'slider' and args['use_all_layers'] or action == 'native_callback' and function.__name__ == 'inbetween'):
            from .proxy import cmds as guarded
            guarded.setKeyframe(list(collected))
        warnings = ['操作遵循原算法；失败可能已留下局部写入，请Undo后检查'] if _ERRORS else []
        if action in ('inbetween', 'slider') and not collected:
            warnings.append('原算法没有采集到可处理通道；请检查关键帧/选中通道/活动视图')
        if action == 'set_tangent':
            warnings.append('原按钮同时修改全局切线偏好；该偏好不能保证由Maya Undo恢复')
        return {'action': action, 'objects': list(args['objects']), 'native_result': result, 'collected_data': collected, 'errors': list(dict.fromkeys(_ERRORS)), 'warnings': warnings}
    finally:
        try:
            if cmds.currentTime(query=True) != current:
                cmds.currentTime(current, edit=True)
            cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)
            cmds.namespace(setNamespace=namespace)
            for node, state in layers.items():
                if cmds.objExists(node):
                    cmds.animLayer(node, edit=True, selected=state[0], preferred=state[1])
            cmds.autoKeyframe(state=auto)
            if not cmds.about(batch=True):
                cmds.waitCursor(state=False)
        finally:
            _ACTIVE, _MODE, _ARGS, _IDS = False, '', {}, set()
