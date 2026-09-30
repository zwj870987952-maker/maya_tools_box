import json
from pathlib import Path
import uuid

_ACTIVE = False
PACKAGE = Path(__file__).parent


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部DOF MEL仅允许DofControlTool.run')


def load_suite():
    from maya import mel
    path = PACKAGE / 'runtime.mel'
    name = 'mtbDOF_build'
    if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        raise RuntimeError('DOF MEL来源冲突')


def execute(args):
    global _ACTIVE
    from maya import cmds, mel
    from . import scene
    selection = cmds.ls(selection=True, long=True) or []
    time = cmds.currentTime(query=True)
    results = []
    try:
        _ACTIVE = True
        if args['action'] in ('cleanup', 'set_template'):
            records = {scene.identity(n): (n, data) for n, data in scene.records()}
            for uid in args['record_ids']:
                node, data = records[uid]
                if args['action'] == 'cleanup':
                    results.append(scene.cleanup(node, data))
                else:
                    cube = scene.find(data['cube_uuid'])
                    shapes = cmds.listRelatives(cube, shapes=True, fullPath=True) or []
                    for shape in shapes:
                        cmds.setAttr(shape + '.template', args['template'])
                    results.append({'record_uuid': uid, 'cube': cube, 'template': args['template']})
            return {'action': args['action'], 'results': results}
        load_suite()
        for camera in args['cameras']:
            token = uuid.uuid4().hex
            node = cmds.createNode('network', name='mtbDOF_' + token[:8] + '_record')
            scene.tag(node, token, 'record')
            cmds.addAttr(node, longName=scene.DATA_ATTR, dataType='string')
            cmds.addAttr(node, longName='camera', attributeType='message')
            cmds.connectAttr(camera + '.message', node + '.camera')
            data = {'token': token, 'record_uuid': scene.identity(node), 'camera_uuid': scene.identity(camera), 'old_values': {attr: cmds.getAttr(camera + '.' + attr) for attr in ('focusDistance', 'fStop')}, 'resources': [], 'cube_uuid': None, 'connections': {}, 'state': 'working'}
            scene.save(node, data)
            before = {scene.identity(n) for n in cmds.ls(long=True) or []}
            error = None
            built = None
            try:
                cameras = '{' + json.dumps(camera, ensure_ascii=False) + '}'
                built = mel.eval('mtbDOF_build(' + cameras + ',' + json.dumps('mtbDOF_' + token[:8] + '_') + ');')
            except Exception as exc:
                error = exc
            finally:
                after = {scene.identity(n) for n in cmds.ls(long=True) or []}
                for uid in after - before:
                    resource = scene.find(uid)
                    if resource:
                        scene.tag(resource, token, cmds.nodeType(resource))
                        data['resources'].append(uid)
                data['connections'] = {attr: scene.connection(camera + '.' + attr) for attr in ('focusDistance', 'fStop')}
                if built:
                    data['cube_uuid'] = scene.identity(built[0])
                data['state'] = 'failed' if error else 'ready'
                scene.save(node, data)
            if error:
                return {'errors': [str(error)], 'record_uuid': data['record_uuid'], 'results': results, 'warnings': ['部分创建可能已写场景，请Undo。']}
            if args['template']:
                cube = scene.find(data['cube_uuid'])
                for shape in cmds.listRelatives(cube, shapes=True, fullPath=True) or []:
                    cmds.setAttr(shape + '.template', True)
            results.append({'camera': camera, 'cube': scene.find(data['cube_uuid']), 'record_uuid': data['record_uuid'], 'resources': [scene.find(uid) for uid in data['resources']]})
        return {'action': 'create', 'results': results, 'warnings': ['原ScaleZ连接的是fStop，不是物理焦深范围；DepthOfField保持原值。']}
    finally:
        try:
            cmds.currentTime(time, edit=True)
            cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)
        finally:
            _ACTIVE = False
