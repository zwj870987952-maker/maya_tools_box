"""Owned staging dispatch; all Maya/native interactions occur on explicit actions."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import uuid

PACKAGE = Path(__file__).resolve().parent
ACTION_NAMES = ('inspect', 'catalog', 'show_ui', 'install_runtime', 'invoke', 'launch_toolbar')
DEFAULTS = {'action': 'inspect', 'operation_id': None, 'objects': None,
            'query': '', 'operation_category': '', 'offset': 0, 'limit': 50}
SHORT_MODULES = ('compat', 'barMod', 'styleMod', 'graphSliderMod', 'slider_utils',
                 'spacify_core', 'spacify_actions', 'tooltip_manager', 'tooltip_widget', 'tooltip_data')
MARKER = '_maya_toolkit_animo_candidate.json'


def read_json(name):
    return json.loads((PACKAGE / name).read_text(encoding='utf-8'))


def operations():
    return read_json('operations.json')['operations']


def find_operation(operation_id):
    matches = [row for row in operations() if row['id'] == operation_id]
    if len(matches) != 1:
        raise ValueError('UNKNOWN_OPERATION: operation_id 不在候选白名单中')
    return matches[0]


def contained(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def source_path(relative, root=None):
    root = Path(root) if root is not None else PACKAGE / 'native'
    if not isinstance(relative, str) or not relative:
        raise ValueError('INVALID_SOURCE_PATH: 脚本路径必须位于包内')
    candidate = root / relative
    if not contained(candidate, root):
        raise ValueError('INVALID_SOURCE_PATH: 脚本路径必须位于包内')
    if not candidate.is_file():
        raise ValueError('SOURCE_MISSING: ' + relative)
    return candidate


def sha256(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def normalize(kwargs):
    extra = set(kwargs) - set(DEFAULTS)
    if extra:
        raise ValueError('UNKNOWN_PARAMETER: ' + ', '.join(sorted(extra)))
    args = dict(DEFAULTS, **kwargs)
    if not isinstance(args['action'], str) or args['action'] not in ACTION_NAMES:
        raise ValueError('INVALID_ACTION')
    for key in ('query', 'operation_category'):
        if not isinstance(args[key], str):
            raise ValueError('INVALID_TYPE: ' + key + ' 必须为字符串')
    if type(args['offset']) is not int or args['offset'] < 0:
        raise ValueError('INVALID_OFFSET: offset 必须为非负整数')
    if type(args['limit']) is not int or not 1 <= args['limit'] <= 200:
        raise ValueError('INVALID_LIMIT: limit 必须为 1–200 的整数')
    if args['operation_id'] is not None and not isinstance(args['operation_id'], str):
        raise ValueError('INVALID_OPERATION_ID')
    if args['action'] != 'invoke' and args['operation_id'] is not None:
        raise ValueError('UNUSED_PARAMETER: operation_id 只适用于 invoke')
    if args['objects'] is not None:
        objects = args['objects']
        if args['action'] != 'invoke':
            raise ValueError('UNUSED_PARAMETER: objects 只适用于 invoke')
        if (not isinstance(objects, list) or not 1 <= len(objects) <= 4096 or
                any(not isinstance(obj, str) or not obj.strip() or '.' in obj for obj in objects)):
            raise ValueError('INVALID_OBJECTS: 提供非空节点名称数组，不支持组件/属性')
        if len(set(objects)) != len(objects):
            raise ValueError('DUPLICATE_OBJECTS')
    return args


def catalog(args):
    rows = operations()
    query = args['query'].casefold()
    if query:
        rows = [row for row in rows if query in (' '.join(str(row[k]) for k in
                ('id', 'name', 'category', 'category_zh', 'description'))).casefold()]
    if args['operation_category']:
        rows = [row for row in rows if row['category'] == args['operation_category']]
    start = args['offset']
    return {'total': len(rows), 'offset': start, 'operations': rows[start:start + args['limit']],
            'categories': sorted(set(row['category'] for row in operations())), 'maya_verified': False}


def maya_cmds():
    try:
        from maya import cmds
        if cmds.about(batch=True):
            raise ValueError('GUI_REQUIRED: 请在真实 Maya GUI 中人工检验')
        version = int(str(cmds.about(version=True))[:4])
        if version < 2022 or version > 2026:
            raise ValueError('MAYA_VERSION_UNVERIFIED: 官方包标注 2022–2026；其他版本尚未纳入候选范围')
        return cmds
    except ImportError:
        raise ValueError('MAYA_REQUIRED: 当前进程不是 Maya')


def runtime_destination(cmds):
    script_dir = Path(cmds.internalVar(userScriptDir=True)).resolve()
    result = script_dir.parent.parent / 'scripts' / 'Animo_Data'
    if contained(result, PACKAGE) or result.name != 'Animo_Data':
        raise ValueError('INVALID_RUNTIME_DESTINATION')
    return result


def verify_code(root, check_marker=False):
    """Read-only integrity check. Runtime preferences and saved user data may change."""
    root = Path(root)
    hashes = read_json('runtime_files.json')
    if check_marker:
        marker = root / 'Animo_Data' / MARKER
        if not marker.is_file():
            raise ValueError('RUNTIME_NOT_CANDIDATE: 目标已有普通 Animo，候选不会覆盖；先手动备份并移开旧目录')
        try:
            identity = json.loads(marker.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            raise ValueError('RUNTIME_MARKER_INVALID')
        expected = sha256(PACKAGE / 'runtime_files.json')
        if identity.get('manifest_sha256') != expected:
            raise ValueError('RUNTIME_VERSION_MISMATCH: 运行目录来自另一候选版本')
    missing = []
    changed = []
    for relative, expected in hashes.items():
        if not relative.endswith('.py'):
            continue
        path = root / relative
        if not contained(path, root) or not path.is_file():
            missing.append(relative)
        elif sha256(path) != expected:
            changed.append(relative)
    if missing or changed:
        raise ValueError('RUNTIME_CODE_MISMATCH: missing={} changed={}'.format(missing[:5], changed[:5]))
    return len([key for key in hashes if key.endswith('.py')])


def check_module_collisions(runtime):
    for name, module in list(sys.modules.items()):
        if not (name.startswith(('Animo_', 'animo_')) or name in SHORT_MODULES):
            continue
        filename = getattr(module, '__file__', None)
        if filename and not contained(Path(filename), runtime):
            raise ValueError('MODULE_COLLISION: {} 已从其他目录加载，候选不会卸载其他工具；请重启 Maya 后再验'.format(name))


def preflight(kwargs):
    args = normalize(kwargs)
    report = {'action': args['action'], 'state': 'prepared_unverified', 'maya_verified': False,
              'native_imported': False, 'preflight_only': True}
    if args['action'] in ('inspect', 'catalog'):
        report.update(catalog(args) if args['action'] == 'catalog' else {
            'source_version': '10.6.0', 'operation_count': len(operations()),
            'runtime_install_required': True, 'formal_registration': False})
        return args, report
    if args['action'] == 'invoke':
        report['operation'] = find_operation(args['operation_id'])
        source_path(report['operation']['entrypoint'])
    cmds = maya_cmds()
    runtime = runtime_destination(cmds)
    report['runtime_directory'] = str(runtime)
    if args['action'] == 'show_ui':
        return args, report
    if args['action'] == 'install_runtime':
        if runtime.exists():
            raise ValueError('RUNTIME_EXISTS: 候选只允许全新安装，不能覆盖已有 Animo_Data')
        report['checked_python_files'] = verify_code(PACKAGE / 'native')
        report['file_write_on_execute'] = True
        report['undoable_file_write'] = False
        return args, report
    if not runtime.is_dir():
        raise ValueError('RUNTIME_MISSING: 先在候选面板执行安装运行副本')
    report['checked_python_files'] = verify_code(runtime.parent, check_marker=True)
    check_module_collisions(runtime)
    if args['action'] == 'invoke':
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('UNDO_DISABLED: 启用 Maya Undo 后再调用')
        explicit = args['objects']
        if explicit is not None:
            resolved = []
            for obj in explicit:
                matches = cmds.ls(obj, long=True) or []
                if len(matches) != 1:
                    raise ValueError('AMBIGUOUS_OR_MISSING_OBJECT: ' + obj)
                if matches[0] in resolved:
                    raise ValueError('DUPLICATE_RESOLVED_OBJECT')
                resolved.append(matches[0])
            args['objects'] = resolved
        report['target_objects'] = args['objects']
        report['current_selection'] = cmds.ls(selection=True, long=True) or []
        report['native_context_validation'] = '原生对象数、关键帧/层/摄像机等前提在执行时检查；本预检不导入原工具'
    return args, report


def install_runtime(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('RUNTIME_EXISTS: 拒绝覆盖已有目录')
    source = PACKAGE / 'native/Animo_Data'
    verify_code(PACKAGE / 'native')
    # Verify resources as well before copying executable programs or assets.
    for relative, expected in read_json('runtime_files.json').items():
        if sha256(source_path(relative)) != expected:
            raise ValueError('SOURCE_RESOURCE_CHANGED: ' + relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / ('.Animo_candidate_' + uuid.uuid4().hex)
    try:
        shutil.copytree(str(source), str(temporary))
        identity = {'tool_id': 'animo', 'source_version': '10.6.0', 'maya_verified': False,
                    'manifest_sha256': sha256(PACKAGE / 'runtime_files.json')}
        (temporary / MARKER).write_text(json.dumps(identity, indent=2), encoding='utf-8')
        if destination.exists():
            raise ValueError('RUNTIME_EXISTS: 安装时目标目录出现，拒绝覆盖')
        os.rename(str(temporary), str(destination))
    finally:
        if temporary.is_dir() and contained(temporary, destination.parent) and temporary.name.startswith('.Animo_candidate_'):
            shutil.rmtree(str(temporary))
    return {'runtime_directory': str(destination), 'state': 'installed_unverified',
            'file_write': True, 'file_write_undoable': False, 'startup_file_written': False}


def invoke(operation, runtime, objects=None):
    runtime = Path(runtime)
    cmds = maya_cmds()
    check_module_collisions(runtime)
    script = source_path(operation['entrypoint'], runtime.parent)
    before = cmds.ls(selection=True, long=True) or []
    for directory in (runtime, script.parent, runtime / 'Animo_Launcher', runtime / 'Animo_Sliders',
                      runtime / 'Animo_Space_Switcher', runtime / 'Animo_UI', runtime / 'Animo_Tools_Tip'):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    if objects is not None:
        cmds.select(objects, replace=True)
    try:
        runpy.run_path(str(script), run_name='__main__')
    except SystemExit as exc:
        # Native scripts use sys.exit() on unmet selection conditions. Never
        # let this terminate the host, and never report it as a successful edit.
        raise ValueError('NATIVE_ABORTED: 原入口提前退出 ({})；检查选择和 Script Editor'.format(exc.code))
    return {'operation_id': operation['id'], 'entrypoint': operation['entrypoint'],
            'state': 'dispatched_unverified', 'selection_before': before,
            'selection_after': cmds.ls(selection=True, long=True) or [],
            'native_business_success': None, 'maya_verified': False,
            'external_files_undoable': False}
