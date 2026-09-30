import json

OWNER = 'maya_toolkit.bh_speedlines.v1'
PLANE = 'mtbSL_SL_Draw_Plane'
LAYER = 'mtbSL_bh_DrawnGeoL'
TAG = 'mtbSLOwner'
DATA = 'mtbSLDrawData'


def maya():
    import maya.cmds as cmds
    return cmds


def identity(node):
    return maya().ls(node, uuid=True)[0]


def find(value):
    found = maya().ls(value, long=True) or []
    return found[0] if len(found) == 1 else None


def resolve(node):
    cmds = maya()
    nodes = cmds.ls(node, long=True) or []
    if len(nodes) != 1 or not cmds.objectType(nodes[0], isAType='transform'):
        raise ValueError('对象缺失、重名或非 transform: ' + node)
    return nodes[0]


def shape(node):
    shapes = maya().listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
    if len(shapes) != 1:
        raise ValueError('需要一个明确的非中间shape: ' + node)
    return shapes[0]


def mark(node):
    cmds = maya()
    if not cmds.attributeQuery(TAG, node=node, exists=True):
        cmds.addAttr(node, longName=TAG, dataType='string')
    cmds.setAttr(node + '.' + TAG, OWNER, type='string')


def owned(node):
    cmds = maya()
    return cmds.attributeQuery(TAG, node=node, exists=True) and cmds.getAttr(node + '.' + TAG) == OWNER


def plane():
    cmds = maya()
    recorded = [node for node in (cmds.ls('*.' + DATA, objectsOnly=True, long=True) or []) if owned(node)]
    if len(recorded) > 1:
        raise ValueError('有多个绘画平面记录，请在副本逐一检查')
    if recorded:
        return safe_plane(recorded[0])
    matches = cmds.ls(PLANE, long=True) or []
    if not matches:
        return None
    raise ValueError('固定helper名被外部或不完整记录占用；不删除')


def safe_plane(node):
    cmds = maya()
    if not owned(node):
        raise ValueError('绘画平面所有权丢失')
    data = read_draw(node)
    children = cmds.listRelatives(node, children=True, fullPath=True) or []
    if any(identity(child) not in data.get('shapes', []) for child in children):
        raise ValueError('绘画平面下有外部子对象；请先分离')
    ids = {identity(item) for item in [node] + children}
    for item in [node] + children:
        for consumer in cmds.listConnections(item, source=False, destination=True) or []:
            if cmds.nodeType(consumer) not in ('shadingEngine', 'objectSet', 'displayLayer') and identity(consumer) not in ids:
                raise ValueError('绘画平面有外部输出消费连接: ' + consumer)
    return node


def read_draw(node):
    cmds = maya()
    if not cmds.attributeQuery(DATA, node=node, exists=True):
        return {'context': 'moveSuperContext', 'live': []}
    return json.loads(cmds.getAttr(node + '.' + DATA))


def write_draw(node, data):
    cmds = maya()
    mark(node)
    if not cmds.attributeQuery(DATA, node=node, exists=True):
        cmds.addAttr(node, longName=DATA, dataType='string')
    data = dict(data, shapes=[identity(shape) for shape in (cmds.listRelatives(node, shapes=True, fullPath=True) or [])])
    cmds.setAttr(node + '.' + DATA, json.dumps(data), type='string')
