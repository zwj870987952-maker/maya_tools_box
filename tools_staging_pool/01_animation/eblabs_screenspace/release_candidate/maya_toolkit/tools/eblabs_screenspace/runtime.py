import json
from pathlib import Path
import uuid

_ACTIVE = False
_RECORD = None
PACKAGE = Path(__file__).parent


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部ScreenSpace写场景函数仅允许ScreenSpaceTool.run')


def current_target():
    require_active()
    from . import scene
    return scene.find(_RECORD[1]['target_uuid'])


def current_rig():
    require_active()
    from . import scene
    return scene.find(_RECORD[1]['rig_uuid'])


def clean_active():
    require_active()
    from . import scene
    return scene.clean_helpers(*_RECORD)


def load_suite():
    from maya import mel
    path = PACKAGE / 'runtime.mel'
    names = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))['runtime_procedures']
    if not str(mel.eval('whatIs ' + names[0] + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    for name in names:
        if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
            raise RuntimeError('MEL来源冲突: ' + name)


def execute(args):
    global _ACTIVE, _RECORD
    from maya import cmds, mel
    from . import scene
    load_suite()
    if args['action'] == 'open_ui':
        mel.eval('mtbSS_ebLabs_screenSpace();')
        return {'window': 'mtbSS_ebLabs_screenSpace'}
    time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    namespace = cmds.namespaceInfo(currentNamespace=True, absoluteName=True)
    rows = []
    try:
        _ACTIVE = True
        cmds.namespace(setNamespace=':')
        if args['action'] != 'create':
            record_map = {scene.identity(n): (n, data) for n, data in scene.records()}
            for uid in args['record_ids']:
                node, data = record_map[uid]
                _RECORD = (node, data)
                if args['action'] == 'cleanup':
                    rows.append(scene.clean_helpers(node, data))
                    continue
                control = scene.find(data['control_uuid'])
                before = scene.snapshot()
                try:
                    if args['action'] == 'full_bake':
                        keys = cmds.keyframe(control, query=True, timeChange=True) or []
                        frame = min(keys)
                        while frame < max(keys) + 1:
                            cmds.currentTime(frame)
                            cmds.setKeyframe(control)
                            frame += 1
                    mel.eval('mtbSS_ebLabs_animTools_screenSpaceSmartBake(' + json.dumps(control, ensure_ascii=False) + ');')
                    data['state'] = 'baked'
                finally:
                    scene.capture(before, node, data)
                    scene.save(node, data)
                rows.append({'record_uuid': uid, 'target': scene.find(data['target_uuid']), 'state': data['state']})
            return {'action': args['action'], 'results': rows, 'warnings': ['原Smart/Full Bake覆盖目标TR键时序/切线并使用Maya动画剪贴板；buffer/部分blend载体保留。']}
        for target in args['objects']:
            old_flags = {attr: (cmds.getAttr(target + '.' + attr, keyable=True), cmds.getAttr(target + '.' + attr, channelBox=True)) for attr in set((cmds.listAttr(target, keyable=True) or []) + (cmds.listAttr(target, channelBox=True) or [])) if cmds.objExists(target + '.' + attr)}
            token = uuid.uuid4().hex
            prefix = 'mtbSS_' + token[:10]
            node = cmds.createNode('network', name=prefix + '_record')
            scene.tag(node, token, 'record')
            cmds.addAttr(node, longName=scene.DATA_ATTR, dataType='string')
            for attr, source in (('target', target), ('camera', args['camera'])):
                cmds.addAttr(node, longName=attr, attributeType='message')
                cmds.connectAttr(source + '.message', node + '.' + attr)
            data = {'token': token, 'record_uuid': scene.identity(node), 'target_uuid': scene.identity(target), 'camera_uuid': scene.identity(args['camera']), 'rig_uuid': None, 'control_uuid': None, 'resources': {}, 'state': 'working', 'old_flags': old_flags}
            scene.save(node, data)
            _RECORD = (node, data)
            before = scene.snapshot()
            error = None
            try:
                mel.eval('mtbSS_ebLabs_animTools_screenSpaceRig(' + ','.join([json.dumps(args['camera'], ensure_ascii=False), json.dumps(target, ensure_ascii=False), json.dumps(prefix), str(int(args['include_orientation']))]) + ');')
            except Exception as exc:
                error = exc
            finally:
                scene.capture(before, node, data)
                for field, suffix in (('rig_uuid', '_screenSpaceRig'), ('control_uuid', '_screenSpaceControl')):
                    found = cmds.ls(prefix + suffix, long=True) or []
                    if len(found) == 1:
                        data[field] = scene.identity(found[0])
                data['state'] = 'failed' if error else 'live'
                scene.save(node, data)
            if error:
                return {'errors': [str(error)], 'record_uuid': data['record_uuid'], 'results': rows, 'warnings': ['部分创建可能已写场景，请Undo或明确record清理。']}
            rows.append({'target': target, 'record_uuid': data['record_uuid'], 'rig': scene.find(data['rig_uuid']), 'control': scene.find(data['control_uuid']), 'orientation': cmds.objExists(scene.find(data['control_uuid']) + '.useOrientation')})
        return {'action': 'create', 'results': rows, 'warnings': ['保留原屏幕投影/深度/朝向采样，只在原TR键时间采样，bufferCurve和动画剪贴板可能改变。']}
    finally:
        try:
            cmds.currentTime(time, edit=True)
            cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)
            cmds.namespace(setNamespace=namespace)
        finally:
            _ACTIVE, _RECORD = False, None
