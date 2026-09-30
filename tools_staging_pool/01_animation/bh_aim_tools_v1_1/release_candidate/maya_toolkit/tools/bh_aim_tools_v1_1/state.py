"""UUID ownership is carried by each locator, including its helper connections."""
import json
import uuid

OWNER = 'maya_toolkit.bh_aim_tools_v1_1.v1'
DATA = 'mtbAimData'
TAG = 'mtbAimOwner'
TOKEN = 'mtbAimToken'


def maya():
    import maya.cmds as cmds
    return cmds


def identity(node):
    return maya().ls(node, uuid=True)[0]


def find(value):
    found = maya().ls(value, long=True) or []
    return found[0] if len(found) == 1 else None


def text(node, attr, value):
    cmds = maya()
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType='string')
    cmds.setAttr(node + '.' + attr, value, type='string')


def tagged(node, token):
    cmds = maya()
    text(node, TAG, OWNER)
    text(node, TOKEN, token)


def create(locator, controller):
    data = {'version': 1, 'token': str(uuid.uuid4()), 'locator': identity(locator), 'controller': identity(controller), 'owned': [], 'stage': 'created', 'failed': False}
    tagged(locator, data['token'])
    save(data)
    return data


def save(data):
    node = find(data['locator'])
    if node:
        text(node, DATA, json.dumps(data, ensure_ascii=False))


def load(locator):
    cmds = maya()
    if not cmds.attributeQuery(DATA, node=locator, exists=True) or not cmds.attributeQuery(TAG, node=locator, exists=True) or cmds.getAttr(locator + '.' + TAG) != OWNER:
        raise ValueError('只接受本候选创建的 Aim Locator，不接管原工具或其他节点')
    data = json.loads(cmds.getAttr(locator + '.' + DATA))
    if data.get('version') != 1 or data.get('locator') != identity(locator) or cmds.getAttr(locator + '.' + TOKEN) != data['token']:
        raise ValueError('所有权记录损坏')
    control = find(data['controller'])
    connected = cmds.listConnections(locator + '.ctrl', source=True, destination=False) or []
    if not control or len(connected) != 1 or identity(connected[0]) != data['controller']:
        raise ValueError('ctrl message 已断开或改接；拒绝操作')
    owned(data)
    return data


def capture(data, before):
    cmds = maya()
    known = {row['uuid'] for row in data['owned']}
    for node in cmds.ls(long=True) or []:
        value = identity(node)
        if value not in before and value not in known:
            tagged(node, data['token'])
            data['owned'].append({'uuid': value, 'type': cmds.nodeType(node)})
            known.add(value)
    save(data)


def owned(data):
    cmds = maya()
    nodes = []
    for row in data['owned']:
        node = find(row['uuid'])
        if node:
            if cmds.nodeType(node) != row['type'] or not cmds.attributeQuery(TAG, node=node, exists=True) or cmds.getAttr(node + '.' + TAG) != OWNER or cmds.getAttr(node + '.' + TOKEN) != data['token']:
                raise ValueError('辅助节点所有权/类型不匹配')
            nodes.append(node)
    return nodes


def safe(data):
    cmds = maya()
    nodes = owned(data)
    ids = {identity(node) for node in nodes} | {data['locator']}
    locator = find(data['locator'])
    descendants = cmds.listRelatives(locator, allDescendents=True, fullPath=True) or []
    if any(identity(node) not in ids for node in descendants):
        raise ValueError('定位器下新增了外部节点，请先在副本分离')
    for node in nodes:
        pairs = cmds.listConnections(node, source=False, destination=True, connections=True, plugs=True) or []
        for source, target in zip(pairs[::2], pairs[1::2]):
            destination = target.split('.', 1)[0]
            if identity(destination) not in ids | {data['controller']}:
                raise ValueError('辅助节点有外部输出消费连接: ' + source + ' -> ' + target)
    return nodes
