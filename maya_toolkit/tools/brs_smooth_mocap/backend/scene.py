from maya import cmds

OWNER = 'maya_toolkit.brs_smooth_mocap.v1'
TAG = 'mtbBRSTOwner'
ROLE = 'mtbBRSTRole'
TARGET = 'mtbBRSTTarget'
UUID = 'mtbBRSTTargetUUID'
GROUP = 'mtbBRSSmoothAnimLoc_Grp'
GUIDE = 'mtbBRSSmoothRedirectGuide'


def identity(node):
    return cmds.ls(node, uuid=True)[0]


def resolve(node):
    found = cmds.ls(node, long=True) or []
    if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('对象不是唯一transform: ' + str(node))
    return found[0]


def mark(node, role):
    for attr, value in [(TAG, OWNER), (ROLE, role)]:
        if not cmds.attributeQuery(attr, node=node, exists=True):
            cmds.addAttr(node, longName=attr, dataType='string')
        cmds.setAttr(node + '.' + attr, value, type='string')


def owned(node, role=None):
    return cmds.objExists(node) and cmds.attributeQuery(TAG, node=node, exists=True) and cmds.getAttr(node + '.' + TAG) == OWNER and (role is None or cmds.getAttr(node + '.' + ROLE) == role)


def by_role(role):
    return [node for node in cmds.ls('*.' + TAG, objectsOnly=True, long=True) or [] if owned(node, role)]


def unique(role, fixed):
    nodes = by_role(role)
    if len(nodes) > 1:
        raise ValueError('多个owned ' + role + '，需人工检查')
    if not nodes and cmds.objExists(fixed):
        raise ValueError('固定辅助名被外部对象占用: ' + fixed)
    return nodes[0] if nodes else None


def group():
    return unique('group', GROUP)


def guide():
    return unique('guide', GUIDE)


def locators():
    root = group()
    if not root:
        return []
    children = cmds.listRelatives(root, children=True, fullPath=True) or []
    if any(not owned(child, 'locator') for child in children):
        raise ValueError('组中有外部子对象，拒绝重定向')
    return children


def locator_for(target, required=False):
    target_id = identity(target)
    found = []
    for node in by_role('locator'):
        if cmds.getAttr(node + '.' + UUID) == target_id:
            connected = cmds.listConnections(node + '.' + TARGET, source=True, destination=False) or []
            if len(connected) != 1 or identity(connected[0]) != target_id:
                raise ValueError('定位器目标message被改接: ' + node)
            found.append(node)
    if len(found) > 1:
        raise ValueError('同目标多个定位器')
    if required and not found:
        raise ValueError('目标没有本候选定位器: ' + target)
    return found[0] if found else None


def constraints(object, target, translate=True, rotate=True):
    result = []
    for command, enabled in [(cmds.pointConstraint, translate), (cmds.orientConstraint, rotate)]:
        if not enabled:
            continue
        before = {identity(node) for node in cmds.ls(long=True) or []}
        nodes = command(target, object, weight=1, maintainOffset=False)
        for node in cmds.ls(long=True) or []:
            if identity(node) not in before:
                mark(node, 'constraint' if cmds.objectType(node, isAType='constraint') else 'aux')
        result.append(nodes)
    return result


def delete_constraints(object):
    nodes = cmds.listRelatives(object, type='constraint', fullPath=True) or []
    if any(not owned(node, 'constraint') for node in nodes):
        raise ValueError('拒绝删除外部约束: ' + object)
    # Detach before delete to protect otherwise empty constrained transform.
    for node in nodes:
        detached = cmds.parent(node, world=True)[0]
        cmds.delete(detached)


def safe_hierarchy(node):
    if not owned(node):
        raise ValueError('非owned helper')
    descendants = cmds.listRelatives(node, allDescendents=True, fullPath=True) or []
    if any(not owned(child) for child in descendants):
        raise ValueError('helper有外部后代: ' + node)
    for item in [node] + descendants:
        for consumer in cmds.listConnections(item, source=False, destination=True) or []:
            if not owned(consumer) and cmds.nodeType(consumer) not in ('objectSet', 'shadingEngine', 'displayLayer'):
                raise ValueError('helper有外部输出消费者: ' + consumer)
    return node


def delete_locator(node):
    safe_hierarchy(node)
    # Disconnect only our output constraints; never blanket-delete target constraints.
    constraints_to_remove = set()
    for item in [node] + (cmds.listRelatives(node, allDescendents=True, fullPath=True) or []):
        for dest in cmds.listConnections(item, source=False, destination=True) or []:
            if cmds.objectType(dest, isAType='constraint') and owned(dest):
                constraints_to_remove.add(identity(dest))
    for uid in constraints_to_remove:
        found = cmds.ls(uid, long=True) or []
        if found:
            node_con = found[0]
            if cmds.listRelatives(node_con, parent=True):
                node_con = cmds.parent(node_con, world=True)[0]
            cmds.delete(node_con)
    cmds.delete(node)


def delete_group_if_empty():
    node = group()
    if node and not cmds.listRelatives(node, children=True):
        safe_hierarchy(node)
        cmds.delete(node)


def delete_guide():
    node = guide()
    if node:
        safe_hierarchy(node)
        cmds.delete(node)


def ensure_group(objects):
    root = group()
    if root:
        return root
    root = cmds.group(name=GROUP, empty=True)
    mark(root, 'group')
    cmds.setAttr(root + '.rotateOrder', 3)
    cmds.setAttr(root + '.useOutlinerColor', 1)
    cmds.setAttr(root + '.outlinerColor', .7067, 1, 0)
    con = cmds.pointConstraint(objects, root, weight=1, maintainOffset=False)
    cmds.delete(con)
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
        cmds.setAttr(root + '.' + attr, lock=True)
    return root


def make_locator(target, annotation):
    old = locator_for(target)
    if old:
        delete_locator(old)
    leaf = target.rsplit('|', 1)[-1].replace(':', '_')
    loc = cmds.spaceLocator(name=leaf + '_mtbBRSSmoothSnapLoc')[0]
    mark(loc, 'locator')
    cmds.addAttr(loc, longName=UUID, dataType='string')
    cmds.setAttr(loc + '.' + UUID, identity(target), type='string')
    cmds.addAttr(loc, longName=TARGET, attributeType='message')
    cmds.connectAttr(target + '.message', loc + '.' + TARGET)
    for shape in cmds.listRelatives(loc, shapes=True, fullPath=True) or []:
        mark(shape, 'shape')
    cmds.setAttr(loc + '.overrideEnabled', 1)
    cmds.setAttr(loc + '.overrideRGBColors', 1)
    cmds.setAttr(loc + '.overrideColorRGB', .465, 1, 0)
    cmds.setAttr(loc + '.useOutlinerColor', 1)
    cmds.setAttr(loc + '.outlinerColor', .7067, 1, 0)
    constraints(loc, target)
    if annotation:
        anno_shape = cmds.annotate(loc, text=target.rsplit(':', 1)[-1].rsplit('|', 1)[-1])
        anno = cmds.listRelatives(anno_shape, parent=True, fullPath=True)[0]
        anno = cmds.parent(anno, loc)[0]
        mark(anno, 'annotation')
        for shape in cmds.listRelatives(anno, shapes=True, fullPath=True) or []:
            mark(shape, 'shape')
            cmds.setAttr(shape + '.displayArrow', 0)
        cmds.setAttr(anno + '.overrideEnabled', 1)
        cmds.setAttr(anno + '.overrideDisplayType', 2)
        for axis in 'XYZ':
            cmds.setAttr(anno + '.translate' + axis, 0)
        cmds.setAttr(anno + '.hiddenInOutliner', True)
        cmds.rename(anno, leaf + '_mtbBRSSmoothAnnotate')
    return cmds.ls(loc, long=True)[0]


def create_guide():
    root = group()
    if not root:
        raise ValueError('没有本候选locator group')
    delete_guide()
    node = cmds.spaceLocator(name=GUIDE)[0]
    mark(node, 'guide')
    for shape in cmds.listRelatives(node, shapes=True, fullPath=True) or []:
        mark(shape, 'shape')
    for attr, value in [('overrideEnabled', 1), ('overrideRGBColors', 1), ('useOutlinerColor', 1), ('localScaleZ', 2)]:
        cmds.setAttr(node + '.' + attr, value)
    cmds.setAttr(node + '.overrideColorRGB', 0, .701, 1)
    cmds.setAttr(node + '.outlinerColor', 0, .7, 1)
    con = cmds.pointConstraint(root, node, maintainOffset=False, weight=1)
    cmds.delete(con)
    return node
