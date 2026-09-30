from . import runtime as r


def targets(args):
    for value in args:
        if isinstance(value, (list, tuple)):
            yield from targets(value)
        elif isinstance(value, str):
            yield value


def cleanup():
    cmds = r.cmds_module()
    nodes = [n for n in cmds.ls(long=True) or [] if r.identity(n) in r._HELPERS]
    for node in nodes:
        for consumer in cmds.listConnections(node, source=False, destination=True) or []:
            if r.identity(consumer) not in r._HELPERS:
                raise ValueError('临时矩阵节点有外部输出，保留并请Undo')
    if nodes:
        cmds.delete(nodes)


class Commands:
    def __getattr__(self, name):
        cmds = r.cmds_module()
        function = getattr(cmds, name)

        def invoke(*args, **kwargs):
            query = kwargs.get('q') or kwargs.get('query')
            if r._ACTIVE:
                if name == 'ls' and (kwargs.get('sl') or kwargs.get('selection')):
                    return list(r._ARGS['objects'])
                if name == 'channelBox' and query:
                    return list(r._ARGS['attributes'])
                if name == 'playbackOptions' and query:
                    if kwargs.get('min') or kwargs.get('minTime'):
                        return r._ARGS['start']
                    if kwargs.get('max') or kwargs.get('maxTime'):
                        return r._ARGS['end']
                if name == 'timer' and 'name' in kwargs:
                    kwargs['name'] = r._PREFIX + kwargs['name']
            if name == 'createNode':
                r.require_active()
                kwargs['name'] = r._PREFIX + kwargs.get('name', args[0])
                result = function(*args, **kwargs)
                r._HELPERS.add(r.identity(result))
                return result
            if name in ('setAttr', 'connectAttr', 'disconnectAttr', 'setKeyframe', 'filterCurve', 'delete') and not query:
                r.require_active()
                values = list(targets(args[:1] if name in ('setAttr', 'setKeyframe') else args))
                for value in values:
                    node = value.split('.', 1)[0]
                    identity = r.identity(node)
                    allowed = r._HELPERS | r._TARGETS if name in ('setKeyframe', 'filterCurve', 'connectAttr', 'disconnectAttr') else r._HELPERS
                    if identity not in allowed:
                        raise ValueError('写入/删除超出控制器/自有图范围')
                if name == 'connectAttr' and r.identity(values[-1].split('.', 1)[0]) not in r._HELPERS:
                    raise ValueError('不连接目标驱动，不force覆盖')
                if name == 'delete':
                    for value in values:
                        for consumer in cmds.listConnections(value, source=False, destination=True) or []:
                            if r.identity(consumer) not in r._HELPERS:
                                raise ValueError('自有图有外部使用者')
            return function(*args, **kwargs)
        return invoke


mc = Commands()
