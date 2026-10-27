import json
from maya import cmds

OWNER = 'maya_toolkit.eblabs_screenspace.v1'
OWNER_ATTR = 'mtbSSOwner'
TOKEN_ATTR = 'mtbSSToken'
ROLE_ATTR = 'mtbSSRole'
DATA_ATTR = 'mtbSSData'


def identity(node):
    values = cmds.ls(node, uuid=True) or []
    if len(values) != 1:
        raise ValueError('UUID身份不唯一: ' + str(node))
    return values[0]


def find(uid):
    values = cmds.ls(uid, long=True) or []
    return values[0] if len(values) == 1 else None


def owned(node, token=None):
    return bool(node and cmds.objExists(node + '.' + OWNER_ATTR) and cmds.getAttr(node + '.' + OWNER_ATTR) == OWNER and (token is None or cmds.getAttr(node + '.' + TOKEN_ATTR) == token))


def tag(node, token, role):
    for attr, value in ((OWNER_ATTR, OWNER), (TOKEN_ATTR, token), (ROLE_ATTR, role)):
        cmds.addAttr(node, longName=attr, dataType='string')
        cmds.setAttr(node + '.' + attr, value, type='string')


def writable(node):
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
        raise ValueError('节点引用/锁定: ' + node)


def save(node, data):
    cmds.setAttr(node + '.' + DATA_ATTR, json.dumps(data), type='string')


def records():
    return [(n, json.loads(cmds.getAttr(n + '.' + DATA_ATTR))) for n in cmds.ls(type='network') or [] if owned(n) and cmds.getAttr(n + '.' + ROLE_ATTR) == 'record']


def snapshot():
    return {identity(n) for n in cmds.ls(long=True) or []}


def capture(before, node, data):
    for uid in snapshot() - before:
        resource = find(uid)
        kind = cmds.nodeType(resource)
        role = 'constraint' if cmds.objectType(resource, isAType='constraint') else 'helper' if kind in ('transform', 'locator', 'nurbsCurve') else 'animation' if kind.startswith('animCurve') else 'aux'
        tag(resource, data['token'], role)
        data['resources'][uid] = role
    save(node, data)


def validate(data, target_required=True):
    node = find(data['record_uuid'])
    if not node or not owned(node, data['token']):
        raise ValueError('记录已变更')
    writable(node)
    target = find(data['target_uuid'])
    if target_required and not target:
        raise ValueError('源控制器缺失')
    if target:
        writable(target)
    known = set(data['resources']) | {data['target_uuid'], data['camera_uuid'], data['record_uuid']}
    for uid, role in data['resources'].items():
        resource = find(uid)
        if not resource or role not in ('helper', 'constraint'):
            continue
        if not owned(resource, data['token']):
            raise ValueError('资源所有权被修改: ' + resource)
        writable(resource)
        for child in cmds.listRelatives(resource, allDescendents=True, fullPath=True) or []:
            if identity(child) not in data['resources'] or not owned(child, data['token']):
                raise ValueError('rig包含外部后代: ' + child)
        for destination in cmds.listConnections(resource, source=False, destination=True) or []:
            if identity(destination) not in known:
                raise ValueError('rig被外部节点使用: ' + destination)
        for source in cmds.listConnections(resource, source=True, destination=False) or []:
            if identity(source) not in known and cmds.nodeType(source) != 'time':
                raise ValueError('rig有外部输入，清理前需明确解除: ' + source)


def clean_helpers(node, data):
    validate(data)
    # All constraints are owned; detach before delete to protect empty target controls.
    for uid, role in list(data['resources'].items()):
        resource = find(uid)
        if resource and role == 'constraint':
            if cmds.listRelatives(resource, parent=True):
                resource = cmds.parent(resource, world=True)[0]
            cmds.delete(resource)
    for uid, role in list(data['resources'].items()):
        resource = find(uid)
        if resource and role == 'helper' and cmds.nodeType(resource) == 'transform':
            cmds.delete(resource)
    target = find(data['target_uuid'])
    # Restore only pre-existing keyable/channelBox flags; created blend attributes may remain.
    if target:
        for attr, values in data['old_flags'].items():
            if cmds.objExists(target + '.' + attr):
                cmds.setAttr(target + '.' + attr, keyable=values[0], channelBox=values[1])
    data['state'] = 'cleaned'
    save(node, data)
    return {'record_uuid': data['record_uuid'], 'target': target, 'retained_auxiliary': [find(uid) for uid, role in data['resources'].items() if role in ('aux', 'animation') and find(uid)]}
