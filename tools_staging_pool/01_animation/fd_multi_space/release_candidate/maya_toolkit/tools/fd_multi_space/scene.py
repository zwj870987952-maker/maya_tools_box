"""Private provenance and conservative preflight; never adopt same-name nodes."""
OWNER = 'maya_toolkit.fd_multi_space.v1'
TRS = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')


def commands():
    from maya import cmds
    return cmds


def uid(node):
    cmds = commands()
    identity = cmds.ls(node, uuid=True)[0]
    if cmds.referenceQuery(node, isNodeReferenced=True):
        reference = cmds.referenceQuery(node, referenceNode=True)
        identity += '@@' + cmds.ls(reference, uuid=True)[0]
    return identity


def unique(value):
    cmds = commands()
    if '@@' in value:
        identity, reference_id = value.split('@@', 1)
        matches = [n for n in cmds.ls(identity, long=True) or [] if cmds.referenceQuery(n, isNodeReferenced=True) and cmds.ls(cmds.referenceQuery(n, referenceNode=True), uuid=True)[0] == reference_id]
    else:
        matches = cmds.ls(value, long=True) or []
    if len(matches) != 1:
        raise ValueError('节点缺失/不唯一: ' + value)
    return matches[0]


def writable(node, allow_reference=False):
    cmds = commands()
    if cmds.lockNode(node, query=True, lock=True)[0] or cmds.referenceQuery(node, isNodeReferenced=True) and not allow_reference:
        raise ValueError('节点锁定/未允许引用编辑: ' + node)


def transform(value):
    cmds = commands()
    node = unique(value)
    if not cmds.objectType(node, isAType='transform'):
        raise ValueError('须transform/joint: ' + node)
    if len(cmds.ls(node, long=True, allPaths=True) or []) != 1:
        raise ValueError('不处理实例transform')
    return node


def attached(record, field, required=True):
    cmds = commands()
    items = cmds.listConnections(record + '.' + field, source=True, destination=False) or []
    if len(items) != 1:
        if not items and not required:
            return None
        raise ValueError('来源message缺失/重复: ' + field)
    return unique(items[0])


def records():
    cmds = commands()
    output = []
    for node in cmds.ls(type='network') or []:
        if cmds.objExists(node + '.fdOwner') and cmds.getAttr(node + '.fdOwner') == OWNER:
            output.append({'record_id': uid(node), 'record_node': node, 'phase': cmds.getAttr(node + '.phase'), 'mode': cmds.getAttr(node + '.mode'), 'attribute': cmds.getAttr(node + '.attributeName')})
    return output


def record(value):
    cmds = commands()
    node = unique(value)
    if cmds.nodeType(node) != 'network' or not cmds.objExists(node + '.fdOwner') or cmds.getAttr(node + '.fdOwner') != OWNER:
        raise ValueError('非本工具来源记录')
    writable(node)
    result = {'node': node, 'record_id': uid(node), 'phase': cmds.getAttr(node + '.phase'), 'mode': cmds.getAttr(node + '.mode'), 'attribute': cmds.getAttr(node + '.attributeName')}
    for field in ('driven', 'parent', 'driver', 'constraint', 'group'):
        result[field] = attached(node, field, field in ('driven', 'parent'))
        if field in ('constraint', 'group') and result[field] and (not cmds.objExists(result[field] + '.fdHelperOwner') or cmds.getAttr(result[field] + '.fdHelperOwner') != OWNER):
            raise ValueError('辅助节点不属于本工具: ' + field)
    if result['phase'] >= 2 and not (result['driver'] and result['constraint']):
        raise ValueError('约束阶段来源缺失')
    return result


def relatives(driven):
    cmds = commands()
    result = []
    for item in records():
        data = record(item['record_id'])
        if uid(data['driven']) == uid(driven):
            result.append(data)
    return result


def owned_constraint(parent):
    cmds = commands()
    peers = [record(row['record_id']) for row in records() if attached(row['record_node'], 'parent', False) and uid(attached(row['record_node'], 'parent')) == uid(parent)]
    constraints = {uid(p['constraint']): p['constraint'] for p in peers if p['constraint']}
    if len(constraints) > 1:
        raise ValueError('父级具有多条来源约束')
    constraint = next(iter(constraints.values()), None)
    if constraint:
        writable(constraint)
        drivers = {uid(p['driver']) for p in peers if p['driver']}
        targets = cmds.parentConstraint(constraint, query=True, targetList=True) or []
        if {uid(unique(t)) for t in targets} != drivers:
            raise ValueError('约束target被外部改动')
        allowed_destinations = {uid(parent), uid(constraint)} | {uid(p['node']) for p in peers}
        for node in cmds.listConnections(constraint, source=False, destination=True) or []:
            if uid(unique(node)) not in allowed_destinations:
                raise ValueError('约束有外部使用者: ' + node)
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        for target, alias in zip(targets, aliases):
            row = next(p for p in peers if p['driver'] and uid(p['driver']) == uid(unique(target)))
            plug = constraint + '.' + alias
            if cmds.getAttr(plug, lock=True):
                raise ValueError('权重锁定')
            incoming = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
            expected = row['driven'] + '.' + row['attribute']
            if incoming and (len(incoming) != 1 or uid(incoming[0].split('.')[0]) != uid(row['driven']) or incoming[0].split('.', 1)[1] != row['attribute']):
                raise ValueError('权重被外部连接: ' + plug)
            if row['phase'] == 3 and not incoming:
                raise ValueError('已完成权重连接被移除: ' + expected)
    for attr in TRS:
        plug = parent + '.' + attr
        if cmds.getAttr(plug, lock=True):
            raise ValueError('父级通道锁定: ' + plug)
        for source in cmds.listConnections(plug, source=True, destination=False) or []:
            if not constraint or uid(source) != uid(constraint):
                raise ValueError('父级有既存外部驱动: ' + plug)
    return constraint


def driver_plan(driver, parent):
    cmds = commands()
    node = transform(driver)
    if uid(node) == uid(parent) or node.startswith(parent + '|'):
        raise ValueError('driver在受约束父级下，形成循环')
    constraint = owned_constraint(parent)
    if constraint and uid(node) in {uid(unique(t)) for t in cmds.parentConstraint(constraint, query=True, targetList=True) or []}:
        raise ValueError('相同driver已经属于该空间约束')
    return node, constraint


def plan(args):
    cmds = commands()
    action = args['action']
    if action == 'records':
        return args
    if action == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('界面需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Undo')
    if action in ('add_driver', 'connect'):
        data = record(args['record_id'])
        driven, parent = data['driven'], data['parent']
        current_parent = cmds.listRelatives(driven, parent=True, fullPath=True) or []
        if len(current_parent) != 1 or uid(current_parent[0]) != uid(parent):
            raise ValueError('来源driven父级已被改变')
        allow_ref = data['mode'] == 'reference' and args['allow_reference_edits']
        writable(driven, allow_ref)
        writable(parent, allow_ref)
        plug = driven + '.' + data['attribute']
        if not cmds.objExists(plug) or cmds.getAttr(plug, lock=True) or cmds.getAttr(plug, type=True) != 'double':
            raise ValueError('来源自定义属性缺失/锁定/类型不符')
        if action == 'add_driver':
            if data['phase'] != 1:
                raise ValueError('须先prepare，不能重复添加driver')
            driver, constraint = driver_plan(args['driver'], parent)
            args.update(driver=driver, existing_constraint=constraint)
        else:
            if data['phase'] != 2:
                raise ValueError('须先add_driver，不能重复connect')
            owned_constraint(parent)
            targets = cmds.parentConstraint(data['constraint'], query=True, targetList=True)
            aliases = cmds.parentConstraint(data['constraint'], query=True, weightAliasList=True)
            index = [uid(unique(t)) for t in targets].index(uid(data['driver']))
            weight = data['constraint'] + '.' + aliases[index]
            if cmds.listConnections(weight, source=True, destination=False):
                raise ValueError('目标权重已经连接，禁止force覆盖')
            args.update(weight_plug=weight)
        args.update(data=data, driven=driven, parent=parent, mode=data['mode'], attribute=data['attribute'])
        return args
    driven = transform(args['driven'])
    writable(driven, args['mode'] == 'reference' and args['allow_reference_edits'])
    if cmds.objExists(driven + '.' + args['attribute']):
        raise ValueError('自定义属性已存在，拒绝接管/覆盖')
    peers = relatives(driven)
    if peers and any(p['mode'] != args['mode'] for p in peers):
        raise ValueError('同一对象不能混合两种候选模式')
    if args['mode'] == 'reference':
        parents = cmds.listRelatives(driven, parent=True, fullPath=True) or []
        if len(parents) != 1:
            raise ValueError('reference模式需要既有父级')
        parent = parents[0]
    elif peers:
        parent = peers[0]['group']
        if not parent or uid((cmds.listRelatives(driven, parent=True, fullPath=True) or [''])[0]) != uid(parent):
            raise ValueError('自有空间组父级被改动')
    else:
        parent = None
        for attr in TRS:
            if cmds.getAttr(driven + '.' + attr, lock=True):
                raise ValueError('local分组需要解锁TR通道')
    if parent:
        writable(parent, args['mode'] == 'reference' and args['allow_reference_edits'])
        owned_constraint(parent)
    if action == 'create':
        driver = transform(args['driver'])
        if uid(driver) == uid(driven) or driver.startswith(driven + '|'):
            raise ValueError('driver是driven或其后代，形成循环')
        if parent:
            driver, constraint = driver_plan(driver, parent)
        args['driver'] = driver
    args.update(driven=driven, parent=parent)
    return args
