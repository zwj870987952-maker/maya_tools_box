from . import scene


def link(record, field, node):
    if node:
        scene.commands().connectAttr(node + '.message', record + '.' + field)


def tag(node):
    cmds = scene.commands()
    cmds.addAttr(node, longName='fdHelperOwner', dataType='string')
    cmds.setAttr(node + '.fdHelperOwner', scene.OWNER, type='string')
    cmds.setAttr(node + '.fdHelperOwner', lock=True)


def prepare(args):
    cmds = scene.commands()
    identity = scene.uid(args['driven'])
    parent = args['parent']
    if not parent:
        # Original local algorithm: group the control and center the group's pivot.
        parent = cmds.group(args['driven'], name=args['driven'].split('|')[-1] + '_spaceGrp')
        cmds.xform(parent, centerPivots=True)
        tag(parent)
    driven = scene.unique(identity)
    parent = scene.unique(parent)
    cmds.addAttr(driven, longName=args['attribute'], attributeType='double', minValue=0, maxValue=1, defaultValue=0, keyable=True)
    record = cmds.createNode('network', name='mtbFD_spaceRecord#')
    for name, value in (('fdOwner', scene.OWNER), ('mode', args['mode']), ('attributeName', args['attribute'])):
        cmds.addAttr(record, longName=name, dataType='string')
        cmds.setAttr(record + '.' + name, value, type='string')
        cmds.setAttr(record + '.' + name, lock=True)
    cmds.addAttr(record, longName='phase', attributeType='long', defaultValue=1)
    for field in ('driven', 'parent', 'driver', 'constraint', 'group'):
        cmds.addAttr(record, longName=field, attributeType='message')
    link(record, 'driven', driven)
    link(record, 'parent', parent)
    if args['mode'] == 'local':
        link(record, 'group', parent)
    return scene.uid(record)


def add_driver(args):
    cmds = scene.commands()
    data = args['data']
    if args['existing_constraint']:
        constraint = cmds.parentConstraint(args['driver'], args['parent'], edit=True, maintainOffset=True)[0]
        if scene.uid(constraint) != scene.uid(args['existing_constraint']):
            raise RuntimeError('Maya未返回预期自有约束；请Undo')
    else:
        constraint = cmds.parentConstraint(args['driver'], args['parent'], maintainOffset=True, name='mtbFD_parentConstraint#')[0]
        tag(constraint)
    link(data['node'], 'driver', args['driver'])
    link(data['node'], 'constraint', constraint)
    cmds.setAttr(data['node'] + '.phase', 2)
    return data['record_id']


def connect(args):
    cmds = scene.commands()
    data = args['data']
    # Weight target alias identified by target UUID; never listAttr[-1] or force.
    cmds.connectAttr(args['driven'] + '.' + args['attribute'], args['weight_plug'])
    cmds.setAttr(data['node'] + '.phase', 3)
    return data['record_id']


def execute(args):
    cmds = scene.commands()
    if args['action'] == 'records':
        return {'records': scene.records()}
    if args['action'] == 'open_ui':
        from .ui import show
        return {'window': show()}
    selection = cmds.ls(selection=True, long=True) or []
    selected_ids = [scene.uid(n) for n in selection]
    current = cmds.currentTime(query=True)
    namespace = cmds.namespaceInfo(currentNamespace=True)
    auto = cmds.autoKeyframe(query=True, state=True)
    record_id = args['record_id']
    try:
        cmds.autoKeyframe(state=False)
        if args['action'] == 'create':
            record_id = prepare(args)
            next_args = scene.plan(dict(args, action='add_driver', record_id=record_id))
            add_driver(next_args)
            next_args = scene.plan(dict(args, action='connect', record_id=record_id))
            connect(next_args)
        elif args['action'] == 'prepare':
            record_id = prepare(args)
        elif args['action'] == 'add_driver':
            record_id = add_driver(args)
        elif args['action'] == 'connect':
            record_id = connect(args)
        data = scene.record(record_id)
        data.pop('node')
        return data
    finally:
        try:
            if cmds.currentTime(query=True) != current:
                cmds.currentTime(current, edit=True)
            available = []
            for identity in selected_ids:
                try:
                    available.append(scene.unique(identity))
                except ValueError:
                    pass
            cmds.select(available, replace=True) if available else cmds.select(clear=True)
            cmds.namespace(setNamespace=namespace)
        finally:
            cmds.autoKeyframe(state=auto)
