import json
from maya import cmds

OWNER = 'maya_toolkit.dof_control.v1'
OWNER_ATTR = 'mtbDOFOwner'
TOKEN_ATTR = 'mtbDOFToken'
ROLE_ATTR = 'mtbDOFRole'
DATA_ATTR = 'mtbDOFData'


def identity(node):
    result = cmds.ls(node, uuid=True) or []
    if len(result) != 1:
        raise ValueError('节点UUID不唯一: ' + str(node))
    return result[0]


def find(uid):
    result = cmds.ls(uid, long=True) or []
    return result[0] if len(result) == 1 else None


def owned(node, token=None):
    return bool(node and cmds.objExists(node + '.' + OWNER_ATTR) and cmds.getAttr(node + '.' + OWNER_ATTR) == OWNER and (token is None or cmds.getAttr(node + '.' + TOKEN_ATTR) == token))


def tag(node, token, role):
    for attr, value in ((OWNER_ATTR, OWNER), (TOKEN_ATTR, token), (ROLE_ATTR, role)):
        cmds.addAttr(node, longName=attr, dataType='string')
        cmds.setAttr(node + '.' + attr, value, type='string')


def records():
    return [(n, json.loads(cmds.getAttr(n + '.' + DATA_ATTR))) for n in cmds.ls(type='network') or [] if owned(n) and cmds.getAttr(n + '.' + ROLE_ATTR) == 'record']


def connection(plug):
    sources = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
    return [{'uuid': identity(n.split('.', 1)[0]), 'attr': n.split('.', 1)[1]} for n in sources]


def save(node, data):
    cmds.setAttr(node + '.' + DATA_ATTR, json.dumps(data), type='string')


def writable(node):
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
        raise ValueError('节点引用/锁定: ' + node)


def validate(data, camera_required=True):
    token = data['token']
    camera = find(data['camera_uuid'])
    record = find(data['record_uuid'])
    if not record or not owned(record, token):
        raise ValueError('记录所有权不符')
    writable(record)
    if camera_required and not camera:
        raise ValueError('相机已缺失，先Undo/恢复备份')
    if camera:
        writable(camera)
        for attr in ('focusDistance', 'fStop'):
            if cmds.getAttr(camera + '.' + attr, lock=True) or connection(camera + '.' + attr) != data['connections'].get(attr, []):
                raise ValueError('相机通道锁定/接线已变: ' + attr)
    resources = set(data['resources'])
    allowed = resources | {data['record_uuid']}
    if camera:
        allowed.add(identity(camera))
    for uid in resources:
        node = find(uid)
        if not node:
            raise ValueError('辅助缺失，请Undo/恢复备份: ' + uid)
        if not owned(node, token):
            raise ValueError('辅助已被外部接管: ' + node)
        writable(node)
        for child in cmds.listRelatives(node, allDescendents=True, fullPath=True) or []:
            if identity(child) not in resources:
                raise ValueError('辅助有外部后代: ' + child)
        pairs = cmds.listConnections(node, source=False, destination=True, plugs=True, connections=True) or []
        for source, destination in zip(pairs[::2], pairs[1::2]):
            target = destination.split('.', 1)[0]
            if identity(target) in allowed:
                if camera and identity(target) == identity(camera) and destination.split('.', 1)[1] not in ('focusDistance', 'fStop'):
                    raise ValueError('辅助额外驱动相机属性: ' + destination)
                continue
            # Maya cube material/set membership is removed automatically, never delete the set.
            if cmds.nodeType(node) == 'mesh' and cmds.objectType(target, isAType='objectSet') and ('.instObjGroups' in source or '.objectGroups' in source):
                continue
            raise ValueError('辅助被外部节点使用: ' + destination)
        for source in cmds.listConnections(node, source=True, destination=False) or []:
            if identity(source) in allowed or cmds.nodeType(source) == 'time':
                continue
            # Built-in material/set message links are not animation drivers.
            if cmds.objectType(source, isAType='objectSet'):
                continue
            raise ValueError('辅助有外部输入，先解除: ' + source)


def cleanup(node, data):
    validate(data)
    camera = find(data['camera_uuid'])
    for attr in ('focusDistance', 'fStop'):
        plug = camera + '.' + attr
        source = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
        for value in source:
            cmds.disconnectAttr(value, plug)
        cmds.setAttr(plug, data['old_values'][attr])
    cubes = [find(uid) for uid in data['resources'] if find(uid) and cmds.nodeType(find(uid)) == 'transform']
    for cube in cubes:
        cmds.delete(cube)
    live = [find(uid) for uid in data['resources'] if find(uid)]
    if live:
        cmds.delete(live)
    cmds.delete(node)
    return {'camera': camera, 'restored': data['old_values'], 'removed_record': data['record_uuid']}
