from maya import cmds
from . import proxy

_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部写场景函数仅允许DirectionalCycleTool.run')


def execute(args):
    global _ACTIVE
    from . import algorithms
    time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    layer_flags = {proxy.identity(n): (cmds.animLayer(n, query=True, selected=True), cmds.animLayer(n, query=True, preferred=True)) for n in cmds.ls(type='animLayer') or []}
    old = algorithms.cmds
    worker = None
    try:
        _ACTIVE = True
        if args['action'] == 'cleanup':
            node = proxy.find(args['record_id'])
            data = next(data for n, data in proxy.records() if proxy.identity(n) == args['record_id'])
            return proxy.cleanup(node, data, args['remove_layers'])
        worker = proxy.Commands(args)
        algorithms.cmds = worker
        if args['direction'] == 'back':
            algorithms.run_back(args['controllers'], args['bake'], args['feet_number'], args['correction_locators'])
        else:
            algorithms.run_side(args['direction'] == 'right', args['angle'], args['controllers'], args['bake'], args['feet_number'], args['correction_locators'], args['counter_rotation'])
        if args['bake']:
            proxy.cleanup(worker.node, worker.data)
        worker.data['state'] = 'baked' if args['bake'] else 'live'
        worker.save()
        return {'record_uuid': worker.data['record_uuid'], 'direction': args['direction'], 'state': worker.data['state'], **{role: [proxy.find(uid) for uid in worker.data[role] if proxy.find(uid)] for role in proxy.KINDS}, 'warnings': ['原脚本固定世界头部瞄准点与骨盆/脚部启发式算法；真实角色仍需人工验收。', '生成方向层不会自动静音其他已有动画层；请检查层混合。']}
    except Exception as error:
        if worker:
            worker.data['state'] = 'failed'
            worker.save()
            return {'errors': [str(error)], 'record_uuid': worker.data['record_uuid'], 'state': 'failed', 'warnings': ['可能已有部分场景写入，请Undo或按record_id清理。']}
        raise
    finally:
        try:
            cmds.currentTime(time, edit=True)
            cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)
            for uid, flags in layer_flags.items():
                node = proxy.find(uid)
                if node:
                    cmds.animLayer(node, edit=True, selected=flags[0], preferred=flags[1])
        finally:
            algorithms.cmds = old
            _ACTIVE = False
