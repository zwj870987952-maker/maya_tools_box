import json
from maya import cmds

OWNER = 'maya_toolkit.copy_animation.v1'
TAG = 'mtbCAOwner'
ROLE = 'mtbCARole'
TOKEN = 'mtbCAPair'
DATA = 'mtbCAData'
GROUP = 'mtbCA_CopyAnimation_Locators_GRP'
SETS = {'source': 'mtbCA_CopyAnimation_Source_SET', 'target': 'mtbCA_CopyAnimation_Target_SET', 'locator': 'mtbCA_CopyAnimation_Locator_SET', 'constraint': 'mtbCA_CopyAnimation_Constraint_SET'}


def identity(node):
    identifiers = cmds.ls(node, uuid=True) or []
    if len(identifiers) != 1:
        raise ValueError('UUID需要唯一明确节点: ' + str(node))
    return identifiers[0]


def find(uid):
    nodes = cmds.ls(uid, long=True) or []
    return nodes[0] if nodes else None


def resolve(name):
    nodes = cmds.ls(name, long=True) or []
    if len(nodes) != 1 or not cmds.objectType(nodes[0], isAType='transform'):
        raise ValueError('对象不是唯一transform: ' + str(name))
    return nodes[0]


def owned(node, token=None):
    return bool(node and cmds.objExists(node) and cmds.attributeQuery(TAG, node=node, exists=True) and cmds.getAttr(node + '.' + TAG) == OWNER and (token is None or cmds.getAttr(node + '.' + TOKEN) == token))


def mark(node, role, token='global'):
    for attr, value in [(TAG, OWNER), (ROLE, role), (TOKEN, token)]:
        if not cmds.attributeQuery(attr, node=node, exists=True):
            cmds.addAttr(node, longName=attr, dataType='string')
        cmds.setAttr(node + '.' + attr, value, type='string')


def nodes(role=None):
    return [node for node in cmds.ls('*.' + TAG, objectsOnly=True, long=True) or [] if owned(node) and (role is None or cmds.getAttr(node + '.' + ROLE) == role)]


def group():
    groups = nodes('group')
    if len(groups) > 1:
        raise ValueError('多个owned group，需检查')
    if not groups and cmds.objExists(GROUP):
        raise ValueError('helper group固定名被外部占用')
    return groups[0] if groups else None


def ensure_group():
    root = group()
    if root:
        return root
    root = cmds.group(empty=True, world=True, name=GROUP)
    mark(root, 'group')
    return root


def records():
    result = []
    for node in nodes('record'):
        data = json.loads(cmds.getAttr(node + '.' + DATA))
        if data.get('token') != identity(node):
            raise ValueError('pair record UUID损坏')
        result.append((node, data))
    return result


def get_record(source, target):
    source_id, target_id = identity(source), identity(target)
    found = [(node, data) for node, data in records() if data['source_uuid'] == source_id and data['target_uuid'] == target_id]
    if len(found) > 1:
        raise ValueError('同pair多个记录')
    if found:
        node, data = found[0]
        for attr, uid in [('sourceMessage', source_id), ('targetMessage', target_id)]:
            connections = cmds.listConnections(node + '.' + attr, source=True, destination=False) or []
            if len(connections) != 1 or identity(connections[0]) != uid:
                raise ValueError('pair message被改接')
        return node, data
    return None, None


def save(node, data):
    cmds.setAttr(node + '.' + DATA, json.dumps(data), type='string')


def ensure_record(source, target):
    node, data = get_record(source, target)
    if node:
        return node, data
    node = cmds.createNode('network', name='mtbCA_pairRecord')
    token = identity(node)
    mark(node, 'record', token)
    cmds.addAttr(node, longName=DATA, dataType='string')
    for attr, target_node in [('sourceMessage', source), ('targetMessage', target)]:
        cmds.addAttr(node, longName=attr, attributeType='message')
        cmds.connectAttr(target_node + '.message', node + '.' + attr)
    data = {'token': token, 'source_uuid': identity(source), 'target_uuid': identity(target), 'source_locator': None, 'target_locator': None, 'follow_constraints': [], 'constraints': []}
    save(node, data)
    return node, data


def validate_record(data):
    for key in ('source_locator', 'target_locator'):
        node = find(data.get(key)) if data.get(key) else None
        if node and not owned(node, data['token']):
            raise ValueError('record helper所有权不匹配')
    for key in ('follow_constraints', 'constraints'):
        for uid in data.get(key, []):
            node = find(uid)
            if node and not owned(node, data['token']):
                raise ValueError('record约束所有权不匹配')
            if node:
                command = getattr(cmds, cmds.nodeType(node))
                targets = command(node, query=True, targetList=True) or []
                if [identity(target) for target in targets] != [data['source_uuid']]:
                    raise ValueError('约束输入被改接')
                expected = data['source_locator'] if key == 'follow_constraints' else data['target_uuid']
                for consumer in cmds.listConnections(node, source=False, destination=True) or []:
                    if identity(consumer) != expected and not owned(consumer, data['token']) and cmds.nodeType(consumer) not in ('objectSet', 'displayLayer'):
                        raise ValueError('约束有外部输出消费者')
    src = find(data.get('source_locator')) if data.get('source_locator') else None
    if src:
        safe_helper(src, data['token'])


def safe_helper(node, token):
    descendants = cmds.listRelatives(node, allDescendents=True, fullPath=True) or []
    for child in [node] + descendants:
        if not owned(child, token):
            raise ValueError('helper有外部/别pair后代')
        for consumer in cmds.listConnections(child, source=False, destination=True) or []:
            if not owned(consumer, token) and cmds.nodeType(consumer) not in ('objectSet', 'displayLayer', 'shadingEngine'):
                raise ValueError('helper有外部消费者: ' + consumer)


def delete_constraints(ids, token):
    for uid in ids:
        node = find(uid)
        if not node:
            continue
        if not owned(node, token) or not cmds.objectType(node, isAType='constraint'):
            raise ValueError('不能删除非本pair约束')
        if cmds.listRelatives(node, parent=True):
            node = cmds.parent(node, world=True)[0]
        cmds.delete(node)


def delete_locators(record_node, data):
    validate_record(data)
    delete_constraints(data['follow_constraints'], data['token'])
    for key in ('source_locator', 'target_locator'):
        helper = find(data.get(key)) if data.get(key) else None
        if helper:
            safe_helper(helper, data['token'])
            cmds.delete(helper)
    data.update(source_locator=None, target_locator=None, follow_constraints=[])
    save(record_node, data)


def create_locators(source, target, force=False):
    record_node, data = ensure_record(source, target)
    validate_record(data)
    source_locator = find(data.get('source_locator')) if data.get('source_locator') else None
    target_locator = find(data.get('target_locator')) if data.get('target_locator') else None
    if source_locator and target_locator and not force:
        return record_node, data, source_locator, target_locator
    delete_locators(record_node, data)
    root = ensure_group()
    source_locator = cmds.spaceLocator(name='mtbCA_Source_LOC')[0]
    target_locator = cmds.spaceLocator(name='mtbCA_Target_LOC')[0]
    for node in (source_locator, target_locator):
        mark(node, 'locator', data['token'])
        for shape in cmds.listRelatives(node, shapes=True, fullPath=True) or []:
            mark(shape, 'shape', data['token'])
    data.update(source_locator=identity(source_locator), target_locator=identity(target_locator))
    save(record_node, data)
    # Original hierarchy and maintainOffset preserves target's initial source-relative pose.
    cmds.matchTransform(source_locator, source, pos=True, rot=True, scl=True)
    cmds.matchTransform(target_locator, target, pos=True, rot=True, scl=True)
    source_locator = cmds.parent(source_locator, root)[0]
    target_locator = cmds.parent(target_locator, source_locator)[0]
    follows = []
    for command in (cmds.parentConstraint, cmds.scaleConstraint):
        created = command(source, source_locator, maintainOffset=True) or []
        for node in created:
            mark(node, 'constraint', data['token'])
        follows += created
        data['follow_constraints'] = [identity(n) for n in follows]
        save(record_node, data)
    data.update(source_locator=identity(source_locator), target_locator=identity(target_locator), follow_constraints=[identity(n) for n in follows])
    save(record_node, data)
    return record_node, data, resolve(source_locator), resolve(target_locator)


def channel_constraints(record_node, data, source, target, modes):
    delete_constraints(data['constraints'], data['token'])
    data['constraints'] = []
    save(record_node, data)
    result = []
    for channel, command in [('translate', cmds.pointConstraint), ('rotate', cmds.orientConstraint), ('scale', cmds.scaleConstraint)]:
        if modes[channel] != 'constraint':
            continue
        before = {identity(n) for n in cmds.ls(long=True) or []}
        created = command(source, target, maintainOffset=True) or []
        for node in cmds.ls(long=True) or []:
            if identity(node) not in before:
                mark(node, 'constraint' if cmds.objectType(node, isAType='constraint') else 'aux', data['token'])
        result += created
        data['constraints'] = [identity(n) for n in result]
        save(record_node, data)
    return result


def update_sets():
    all_records = records()
    membership = {key: [] for key in SETS}
    for _, data in all_records:
        for kind in ('source', 'target'):
            node = find(data[kind + '_uuid'])
            if node:
                membership[kind].append(node)
        for key in ('source_locator', 'target_locator'):
            node = find(data[key]) if data[key] else None
            if node:
                membership['locator'].append(node)
        membership['constraint'] += [find(uid) for uid in data['constraints'] if find(uid)]
    for role, name in SETS.items():
        if cmds.objExists(name) and (cmds.nodeType(name) != 'objectSet' or not owned(name)):
            raise ValueError('不更新外部固定名集合: ' + name)
        if not cmds.objExists(name):
            mark(cmds.sets(empty=True, name=name), 'set')
        cmds.sets(clear=name)
        if membership[role]:
            cmds.sets(list(dict.fromkeys(membership[role])), add=name)


def cleanup(record_node, data):
    validate_record(data)
    delete_constraints(data['constraints'], data['token'])
    delete_locators(record_node, data)
    # Metadata has source/target incoming messages; only delete our own network.
    cmds.delete(record_node)
    root = group()
    if root and not cmds.listRelatives(root, children=True):
        safe_helper(root, 'global')
        cmds.delete(root)
