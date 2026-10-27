from . import runtime as r


def strings(values):
    for value in values:
        if isinstance(value, (tuple, list)):
            yield from strings(value)
        elif isinstance(value, str):
            yield value


def scope(values, delete=False):
    c = r.mc()
    for value in strings(values):
        n = value.split('.', 1)[0]
        if not c.objExists(n):
            raise ValueError('写入对象缺失: ' + n)
        key = r.identity(n)
        if key not in (r._OWNED if delete else r._OWNED | r._TARGETS | r._CURVES):
            raise ValueError('超出自有图/控制器范围: ' + n)
        if delete:
            for child in c.listRelatives(n, allDescendents=True, fullPath=True) or []:
                if r.identity(child) not in r._OWNED:
                    raise ValueError('删除组有外部后代')
            for consumer in c.listConnections(n, source=False, destination=True) or []:
                if consumer != r._OWNER and r.identity(consumer) not in r._OWNED | r._TARGETS and c.nodeType(consumer) not in ('objectSet', 'shadingEngine'):
                    raise ValueError('删除自有图有外部输出')


class Commands:
    def __getattr__(self, name):
        c = r.mc()
        function = getattr(c, name)
        def call(*args, **kwargs):
            query = kwargs.get('query') or kwargs.get('q')
            if r._ACTIVE and name == 'playbackOptions' and query:
                if kwargs.get('minTime'):
                    return r._ARGS['start']
                if kwargs.get('maxTime'):
                    return r._ARGS['end']
            writes = {'spaceLocator', 'group', 'particle', 'parentConstraint', 'pointConstraint', 'orientConstraint', 'aimConstraint', 'goal', 'parent', 'xform', 'setAttr', 'connectAttr', 'delete', 'bakeResults', 'setKeyframe', 'keyframe', 'cutKey'}
            if name in writes and not query:
                r.require_active()
                r.discover()
                if name not in ('spaceLocator', 'group', 'particle'):
                    scope(args[:1] if name in ('setAttr', 'setKeyframe') else args, delete=name == 'delete')
                if name == 'connectAttr' and r.identity(args[1].split('.', 1)[0]) not in r._OWNED:
                    raise ValueError('不force覆盖控制器输入')
                if name == 'parent':
                    for child in strings(args[:1]):
                        if r.identity(child) not in r._OWNED:
                            raise ValueError('不重父级控制器')
                if name == 'xform' and any(r.identity(n.split('.', 1)[0]) in r._TARGETS for n in strings(args)):
                    raise ValueError('不xform改控制器，只经原key/constraint')
                if name == 'particle' and 'name' in kwargs and not kwargs['name'].startswith(r._PREFIX):
                    raise ValueError('粒子名非私有')
                try:
                    return function(*args, **kwargs)
                finally:
                    r.discover()
            return function(*args, **kwargs)
        return call


cmds = Commands()
