import json
from pathlib import Path
import uuid

_ACTIVE = False
_WARNINGS = []


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部写场景算法仅允许CopyAnimationTool.run()')


def record_warning(message):
    _WARNINGS.append(message)


def execute(args):
    global _ACTIVE, _WARNINGS
    if args['action'] == 'load_config':
        return {'pairs': args['pairs'], 'file_path': args['file_path']}
    from maya import cmds
    from . import scene
    from .algorithms import ChannelAlgorithms
    time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    _WARNINGS = []
    result_rows = []
    try:
        _ACTIVE = True
        if args['action'] == 'save_config':
            path = Path(args['file_path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
            try:
                temporary.write_text(json.dumps([{'text': pair['source'] + ' , ' + pair['target'], 'modes': pair['modes']} for pair in args['pairs']], ensure_ascii=False, indent=4), encoding='utf-8')
                temporary.replace(path)
            finally:
                if temporary.exists():
                    temporary.unlink()
            return {'file_path': str(path), 'warnings': ['JSON文件/目录写入不能由Maya Undo撤回。']}
        if args['action'] == 'cleanup':
            for uid in args['record_ids']:
                node = scene.find(uid)
                if node:
                    data = json.loads(cmds.getAttr(node + '.' + scene.DATA))
                    scene.cleanup(node, data)
            scene.update_sets()
            return {'cleaned_records': args['record_ids'], 'retained_auxiliary': scene.nodes('aux')}
        worker = ChannelAlgorithms()
        for pair in args['pairs']:
            source, target, modes = pair['source'], pair['target'], pair['modes']
            node, data = scene.ensure_record(source, target)
            locator = None
            if args['action'] == 'create_locators':
                node, data, _, locator = scene.create_locators(source, target, force=True)
            else:
                constraints = scene.channel_constraints(node, data, source, target, modes)
                if any(modes[c] == 'frame' for c in ('translate', 'rotate', 'scale')):
                    node, data, _, locator = scene.create_locators(source, target, force=False)
                worker.apply_channel_modes(source, target, locator, modes, args['start'], args['end'])
            result_rows.append({'source': source, 'target': target, 'record_uuid': scene.identity(node), 'target_locator': locator, 'constraint_uuids': data['constraints']})
        scene.update_sets()
        errors = [message for message in _WARNINGS if '失败' in message]
        return {'action': args['action'], 'pairs': result_rows, 'warnings': list(_WARNINGS), 'errors': errors, 'retained_auxiliary': scene.nodes('aux')}
    finally:
        restore_errors = []
        try:
            for callback in (lambda: cmds.currentTime(time, edit=True), lambda: cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)):
                try:
                    callback()
                except Exception as error:
                    restore_errors.append(str(error))
        finally:
            _ACTIVE = False
        if restore_errors:
            raise RuntimeError('时间/选择恢复失败，请检查并Undo: ' + '; '.join(restore_errors))
