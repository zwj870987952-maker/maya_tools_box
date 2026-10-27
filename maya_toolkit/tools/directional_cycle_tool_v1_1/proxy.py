"""Run-local names, persistent UUID ownership, and safe helper deletion."""
import json
import re
import uuid
from maya import cmds

OWNER = 'maya_toolkit.directional_cycle.v1'
OWNER_ATTR = 'mtbDCTOwner'
TOKEN_ATTR = 'mtbDCTToken'
ROLE_ATTR = 'mtbDCTRole'
DATA_ATTR = 'mtbDCTData'
KINDS = ('helper', 'constraint', 'layer', 'animation', 'aux')


def identity(node):
    values = cmds.ls(node, uuid=True) or []
    if len(values) != 1:
        raise ValueError('节点身份不唯一: ' + str(node))
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


def records():
    result = []
    for node in cmds.ls(type='network') or []:
        if owned(node) and cmds.getAttr(node + '.' + ROLE_ATTR) == 'record':
            result.append((node, json.loads(cmds.getAttr(node + '.' + DATA_ATTR))))
    return result


def flatten(values):
    for value in values:
        if isinstance(value, (list, tuple)):
            yield from flatten(value)
        else:
            yield value


def validate_resources(data, remove_layers=False):
    token = data['token']
    live = {uid: find(uid) for role in KINDS for uid in data[role]}
    known = set(live) | set(data['controllers']) | {data['record_uuid']}
    root = cmds.animLayer(query=True, root=True)
    for role in ('helper', 'constraint') + (('layer',) if remove_layers else ()):
        for uid in data[role]:
            node = live[uid]
            if not node:
                continue
            if not owned(node, token) or cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
                raise ValueError('资源已被外部接管/锁定/引用: ' + node)
            for child in cmds.listRelatives(node, allDescendents=True, fullPath=True) or []:
                if not owned(child, token):
                    raise ValueError('资源含外部子节点: ' + child)
            for destination in cmds.listConnections(node, source=False, destination=True) or []:
                if role == 'layer' and root and identity(destination) == identity(root):
                    continue
                if identity(destination) not in known:
                    raise ValueError('资源被外部节点使用: ' + destination)
            if role == 'layer':
                for plug in cmds.animLayer(node, query=True, attribute=True) or []:
                    if identity(plug.split('.', 1)[0]) not in data['controllers']:
                        raise ValueError('动画层新增了外部控制器: ' + plug)
                for child in cmds.animLayer(node, query=True, children=True) or []:
                    if not owned(child, token):
                        raise ValueError('动画层含外部子层: ' + child)


def safe_delete(nodes, data):
    nodes = list(dict.fromkeys(n for n in flatten(nodes) if n and cmds.objExists(n)))
    if not nodes:
        return
    validate_resources(data)
    token = data['token']
    expanded = list(nodes)
    for node in nodes:
        if not owned(node, token):
            raise ValueError('拒绝删除外部节点: ' + node)
        expanded.extend(cmds.listRelatives(node, allDescendents=True, fullPath=True) or [])
    # Delete owned constraint children/outputs first; empty target transforms must survive.
    constraints = [find(uid) for uid in data['constraint'] if find(uid)]
    deleting = {identity(n) for n in expanded}
    for node in constraints:
        inputs = cmds.listConnections(node, source=True, destination=False) or []
        if identity(node) in deleting or any(identity(n) in deleting for n in inputs):
            parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if parent:
                node = cmds.parent(node, world=True)[0]
            cmds.delete(node)
    survivors = [find(uid) for uid in deleting if find(uid)]
    if survivors:
        cmds.delete(survivors)


def cleanup(node, data, remove_layers=False):
    validate_resources(data, remove_layers)
    safe_delete([find(uid) for uid in data['constraint'] + data['helper']], data)
    if remove_layers:
        for uid in reversed(data['layer']):
            layer = find(uid)
            if layer:
                cmds.delete(layer)
    data['state'] = 'cleaned'
    cmds.setAttr(node + '.' + DATA_ATTR, json.dumps(data), type='string')
    return {'record_uuid': data['record_uuid'], 'layers': [find(uid) for uid in data['layer'] if find(uid)], 'retained_auxiliary': [find(uid) for uid in data['aux'] if find(uid)]}


class Commands:
    def __init__(self, args):
        self.args = args
        self.names = {}
        token = uuid.uuid4().hex
        node = cmds.createNode('network', name='mtbDCT_' + token[:8] + '_record')
        tag(node, token, 'record')
        cmds.addAttr(node, longName=DATA_ATTR, dataType='string')
        cmds.addAttr(node, longName='controllers', attributeType='message', multi=True)
        self.node = node
        self.data = {'token': token, 'record_uuid': identity(node), 'direction': args['direction'], 'bake': args['bake'], 'state': 'working', 'controllers': [identity(n) for n in args['controllers']], **{role: [] for role in KINDS}}
        self.save()
        for index, controller in enumerate(args['controllers']):
            cmds.connectAttr(controller + '.message', node + '.controllers[' + str(index) + ']')

    def save(self):
        cmds.setAttr(self.node + '.' + DATA_ATTR, json.dumps(self.data), type='string')

    def name(self, value):
        return 'mtbDCT_' + self.data['token'][:8] + '_' + re.sub(r'[^A-Za-z0-9_]', '_', value)[-90:]

    def capture(self, callback):
        before = {identity(node) for node in cmds.ls(long=True) or []}
        try:
            return callback()
        finally:
            root = cmds.animLayer(query=True, root=True)
            root_uid = identity(root) if root else None
            after = {identity(node) for node in cmds.ls(long=True) or []}
            for uid in after - before:
                node = find(uid)
                if not node or uid == root_uid or uid == self.data['record_uuid']:
                    continue
                kind = cmds.nodeType(node)
                role = 'helper' if kind in ('transform', 'locator') else 'constraint' if cmds.objectType(node, isAType='constraint') else 'layer' if kind == 'animLayer' else 'animation' if kind.startswith('animCurve') else 'aux'
                tag(node, self.data['token'], role)
                self.data[role].append(uid)
            self.save()

    def spaceLocator(self, **kwargs):
        logical = kwargs.pop('n', kwargs.pop('name', 'locator'))
        result = self.capture(lambda: cmds.spaceLocator(name=self.name(logical), **kwargs))
        self.names[logical] = identity(result[0])
        return result

    def animLayer(self, *args, **kwargs):
        values = list(args)
        if values:
            logical = values[0]
            if logical in self.names:
                values[0] = find(self.names[logical])
            elif kwargs.get('query') or kwargs.get('q'):
                if kwargs.get('exists') or kwargs.get('ex'):
                    return False
                raise ValueError('本轮动画层不存在: ' + logical)
            elif not (kwargs.get('edit') or kwargs.get('e')):
                values[0] = self.name(logical)
        result = self.capture(lambda: cmds.animLayer(*values, **kwargs))
        if args and not (kwargs.get('edit') or kwargs.get('e') or kwargs.get('query') or kwargs.get('q')):
            self.names[args[0]] = identity(result)
        return result

    def create_layer(self, name, controllers):
        cmds.select(controllers)
        return self.animLayer(name, aso=True)

    def setKeyframe(self, *args, **kwargs):
        if 'al' in kwargs:
            kwargs['al'] = find(self.names[kwargs['al']])
        return self.capture(lambda: cmds.setKeyframe(*args, **kwargs))

    def bakeResults(self, *args, **kwargs):
        for key in ('dl', 'destinationLayer'):
            if key in kwargs:
                kwargs[key] = find(self.names[kwargs[key]])
        return self.capture(lambda: cmds.bakeResults(*args, **kwargs))

    def playbackOptions(self, **kwargs):
        if kwargs.get('min') or kwargs.get('minTime'):
            return self.args['start']
        if kwargs.get('max') or kwargs.get('maxTime'):
            return self.args['end']
        raise ValueError('只支持读取本轮范围')

    def delete(self, *args):
        nodes = [find(self.names[value]) if value in self.names else value for value in flatten(args)]
        return safe_delete(nodes, self.data)

    def __getattr__(self, name):
        callback = getattr(cmds, name)
        if name in ('parentConstraint', 'pointConstraint', 'aimConstraint'):
            return lambda *args, **kwargs: self.capture(lambda: callback(*args, **kwargs))
        return callback
