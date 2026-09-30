"""Undo-aware ownership is stored in Maya nodes, never in Python/MEL name caches."""
import json
import uuid

OWNER = 'maya_toolkit.animirror_v2_0.v1'
TAG = 'mtbAV2Owner'
RECORD = 'mtbAV2Record'
DATA = 'mtbAV2Data'


def maya():
    import maya.cmds as cmds
    return cmds


def identity(node):
    return maya().ls(node, uuid=True)[0]


def find(value, required=False):
    nodes = maya().ls(value, long=True) or []
    if len(nodes) != 1:
        if required:
            raise ValueError('记录对象已删除或 UUID 无效: ' + value)
        return None
    return nodes[0]


def put_string(node, attr, value):
    cmds = maya()
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType='string')
    cmds.setAttr(node + '.' + attr, value, type='string')


def records():
    cmds = maya()
    found = []
    for node in cmds.ls(type='network') or []:
        if not cmds.attributeQuery(TAG, node=node, exists=True) or cmds.getAttr(node + '.' + TAG) != OWNER:
            continue
        data = json.loads(cmds.getAttr(node + '.' + DATA))
        if data.get('version') != 1 or not isinstance(data.get('owned'), list) or not isinstance(data.get('inputs'), list) or len(data['inputs']) != 3:
            raise ValueError('AniMirror 信息节点损坏: ' + node)
        found.append({'node': node, 'data': data})
    return found


def owned_nodes(record):
    cmds = maya()
    nodes = []
    for entry in record['data']['owned']:
        node = find(entry['uuid'])
        if node is None:
            continue  # Deletion followed by a same-name foreign node is not a match.
        if cmds.nodeType(node) != entry['type'] or not cmds.attributeQuery(TAG, node=node, exists=True) or cmds.getAttr(node + '.' + TAG) != OWNER:
            raise ValueError('辅助节点的所有权或类型已改变: ' + node)
        if not cmds.attributeQuery(RECORD, node=node, exists=True) or cmds.getAttr(node + '.' + RECORD) != record['data']['id']:
            raise ValueError('辅助节点记录身份已改变: ' + node)
        if entry['type'] not in ('joint', 'floatMath', 'unitConversion') and not cmds.objectType(node, isAType='constraint'):
            raise ValueError('不允许清理的节点类型: ' + entry['type'])
        nodes.append(node)
    return nodes


def safe_to_clear(all_records):
    cmds = maya()
    helpers = [node for record in all_records for node in owned_nodes(record)]
    helper_ids = {identity(node) for node in helpers}
    target_ids = {record['data']['inputs'][2] for record in all_records}
    for node in helpers:
        if cmds.objectType(node, isAType='joint'):
            descendants = cmds.listRelatives(node, allDescendents=True, fullPath=True) or []
            if any(identity(child) not in helper_ids for child in descendants):
                raise ValueError('辅助层级包含外部子节点，拒绝清理: ' + node)
        # New connections from an owned node to an unrelated object must not be cut.
        destinations = cmds.listConnections(node, source=False, destination=True, plugs=True) or []
        messages = set(cmds.listConnections(node + '.message', source=False, destination=True, plugs=True) or [])
        for plug in destinations:
            other = plug.split('.', 1)[0]
            if plug in messages and cmds.nodeType(other) == 'defaultRenderUtilityList' and plug.split('.', 1)[1].startswith('utilities['):
                continue  # Maya's utility registration, not a foreign scene consumer.
            if identity(other) not in helper_ids | target_ids:
                raise ValueError('辅助节点已连接外部对象，拒绝清理: ' + node + ' -> ' + plug + ' (type=' + cmds.nodeType(other) + ', message=' + str(plug in messages) + ')')
    return helpers


def create_record(objects, arguments):
    cmds = maya()
    node = cmds.createNode('network', name='aniMirrorCandidateInfo')
    data = {'version': 1, 'id': uuid.uuid4().hex, 'inputs': [identity(obj) for obj in objects], 'arguments': arguments, 'owned': [], 'failed': False}
    put_string(node, TAG, OWNER)
    put_string(node, DATA, json.dumps(data, ensure_ascii=False))
    return {'node': node, 'data': data}


def capture(record, before_ids, error=None):
    cmds = maya()
    entries = []
    import maya.mel as mel
    roles = {}
    for role, variable in (('root', 'centerJoint'), ('translate_operator', 'operatorTrans'), ('rotate_operator', 'operatorRotate')):
        for node in mel.eval('mtbAV2_read_cache(' + json.dumps(variable) + ');') or []:
            if node and cmds.objExists(node):
                roles[identity(node)] = role
    for node in cmds.ls(long=True) or []:
        value = identity(node)
        if value in before_ids:
            continue
        kind = cmds.nodeType(node)
        if kind not in ('joint', 'floatMath', 'unitConversion') and not cmds.objectType(node, isAType='constraint'):
            continue
        put_string(node, TAG, OWNER)
        put_string(node, RECORD, record['data']['id'])
        entries.append({'uuid': value, 'type': kind, 'role': roles.get(value, 'helper')})
    record['data'].update(owned=entries, failed=error is not None, error=str(error) if error is not None else None)
    put_string(record['node'], DATA, json.dumps(record['data'], ensure_ascii=False))
    return entries


def clear():
    cmds = maya()
    all_records = records()
    helpers = safe_to_clear(all_records)
    identities = [identity(node) for node in helpers]
    target_ids = {record['data']['inputs'][2] for record in all_records}
    # Maya may remove an otherwise empty target transform when a source joint
    # deletion cascades into its child constraints. Detach only owned constraints
    # from recorded targets before deleting the helper hierarchy.
    for node in helpers:
        if cmds.objectType(node, isAType='constraint'):
            parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if parents and identity(parents[0]) in target_ids:
                cmds.parent(node, world=True)
    # Delete explicit UUID-resolved owned nodes, not names in stale MEL arrays.
    # A joint deletion may already remove its owned descendants/constraints.
    deleted = []
    for value in identities:
        node = find(value)
        if node:
            deleted.append(node)
            cmds.delete(node)
    metadata = [record['node'] for record in all_records]
    if metadata:
        cmds.delete(metadata)
    return {'deleted': deleted, 'deleted_metadata': metadata}


def rebuild_globals():
    import maya.mel as mel
    groups = {'centerJoint': [], 'operatorTrans': [], 'operatorRotate': [], 'mirrorObject': []}
    roles = {'root': 'centerJoint', 'translate_operator': 'operatorTrans', 'rotate_operator': 'operatorRotate'}
    for record in records():
        for entry in record['data']['owned']:
            node = find(entry['uuid'])
            if node and entry['role'] in roles:
                groups[roles[entry['role']]].append(node)
        target = find(record['data']['inputs'][2])
        if target:
            groups['mirrorObject'].append(target)
    for key, values in groups.items():
        mel.eval('global string $mtbAV2_' + key + '[]; $mtbAV2_' + key + ' = {' + ','.join(json.dumps(node, ensure_ascii=False) for node in values) + '};')
    for variable, count in (('ind', len(groups['mirrorObject'])), ('iTo', len(groups['operatorTrans'])), ('iRo', len(groups['operatorRotate']))):
        mel.eval('global int $mtbAV2_' + variable + '; $mtbAV2_' + variable + ' = ' + str(count) + ';')
    return groups
