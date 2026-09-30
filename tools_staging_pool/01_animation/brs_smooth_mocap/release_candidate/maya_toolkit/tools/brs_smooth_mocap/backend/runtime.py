_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部写场景函数仅允许LocatorTransferTool.run()')


def execute(args):
    global _ACTIVE
    from maya import cmds
    from . import legacy, scene
    if args['action'] == 'open_ui':
        return {'window': legacy.build_ui()}
    time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    refresh = cmds.refresh(query=True, suspend=True)
    paused = None if cmds.about(batch=True) else cmds.ogs(query=True, pause=True)
    root = scene.group()
    root_id = scene.identity(root) if root else None
    root_locks = {attr: cmds.getAttr(root + '.' + attr, lock=True) for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']} if root else {}
    before = {scene.identity(n) for n in cmds.ls(long=True) or []}
    try:
        _ACTIVE = True
        legacy._options = args
        legacy.BRSAnimLocGrp = root or scene.GROUP
        legacy.redirectGuide = scene.guide() or scene.GUIDE
        if args['action'] in ('create', 'apply'):
            cmds.select(args['objects'], replace=True)
            if args['action'] == 'create':
                if any(e['eligible'] for e in args['eligibility']):
                    legacy.objectToLocatorSnap(toGroup=True, forceConstraint=False)
            else:
                legacy.locatorToObjectSnap()
        elif args['action'] == 'create_guide':
            legacy.createRedirectGuide()
        else:
            legacy.applyRedirectGuide()
        new_nodes = [n for n in cmds.ls(long=True) or [] if scene.identity(n) not in before]
        warnings = ['原bake/round/keep/snapKey可能改变六TR的键密度、breakdown和小数时间；辅助blend节点可能携带旧曲线而保留。']
        if args['action'] == 'redirect':
            warnings.append('保留原重定向流程：先缓存世界动画再移动组，隔离平移测试中世界轨迹保持原位；需人工确认，不代表整体动画平移已通过。')
        return {'action': args['action'], 'created_nodes': new_nodes, 'locators': scene.by_role('locator'), 'group': scene.group(), 'guide': scene.guide(), 'skipped': [e['object'] for e in args.get('eligibility', []) if not e['eligible']], 'retained_blend_nodes': scene.by_role('aux'), 'warnings': warnings}
    finally:
        errors = []
        callbacks = [lambda: cmds.refresh(suspend=refresh), lambda: cmds.currentTime(time), lambda: cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)]
        if paused is not None:
            def restore_pause():
                if cmds.ogs(query=True, pause=True) != paused:
                    cmds.ogs(pause=True)
            callbacks.append(restore_pause)
        def restore_locks():
            found = cmds.ls(root_id, long=True) if root_id else []
            if found:
                for attr, state in root_locks.items():
                    cmds.setAttr(found[0] + '.' + attr, lock=state)
        callbacks.append(restore_locks)
        try:
            for callback in callbacks:
                try:
                    callback()
                except Exception as error:
                    errors.append(str(error))
        finally:
            _ACTIVE = False
        if errors:
            raise RuntimeError('状态恢复失败，请检查/Undo: ' + '; '.join(errors))
