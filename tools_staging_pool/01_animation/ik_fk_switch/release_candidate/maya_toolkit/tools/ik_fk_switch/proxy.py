"""Command scope for intact PyMel algorithms; metadata works without PyMel."""
from . import runtime as r

CREATORS = {'createNode', 'group', 'joint', 'spaceLocator', 'duplicate', 'ikHandle', 'parentConstraint', 'pointConstraint', 'orientConstraint', 'aimConstraint', 'poleVectorConstraint'}
WRITES = CREATORS | {'delete', 'parent', 'setAttr', 'xform', 'setKeyframe', 'cutKey', 'keyframe', 'makeIdentity', 'addAttr', 'connectAttr', 'rename', 'autoKeyframe'}


def flatten(values):
    for value in values:
        if isinstance(value, (list, tuple)):
            yield from flatten(value)
        elif value is not None:
            yield str(value)


def resolve(values):
    cmds = r.cmds_module()
    result = []
    for value in flatten(values):
        matches = cmds.ls(value.split('.', 1)[0], long=True) or []
        if len(matches) != 1:
            raise ValueError('写入节点不唯一/缺失: ' + value)
        result.append(matches[0])
    return result


def require_nodes(nodes, helpers_only=False):
    allowed = r._HELPERS if helpers_only else r._HELPERS | r._CONTROLS
    for node in nodes:
        if r.identity(node) not in allowed:
            raise ValueError('原PyMel写入超出范围: ' + node)


def remove_owned(values):
    cmds = r.cmds_module()
    nodes = []
    for value in flatten(values):
        found = cmds.ls(value, long=True) or []
        if not found:
            continue
        if len(found) != 1:
            raise ValueError('删除节点不唯一')
        node = found[0]
        require_nodes([node], helpers_only=True)
        descendants = cmds.listRelatives(node, allDescendents=True, fullPath=True) or []
        require_nodes(descendants, helpers_only=True)
        for owned in [node] + descendants:
            for consumer in cmds.listConnections(owned, source=False, destination=True) or []:
                if r.identity(consumer) not in r._HELPERS:
                    raise ValueError('临时图有外部使用者，保留并请Undo: ' + owned)
        # Removing a child constraint must not also remove its empty helper target.
        if cmds.nodeType(node).endswith('Constraint') and cmds.listRelatives(node, parent=True):
            node = cmds.parent(node, world=True)[0]
        nodes.append(node)
    if nodes:
        cmds.delete(nodes)


def cleanup_helpers():
    cmds = r.cmds_module()
    if not r._HELPERS:
        return
    found = [(key, node) for key, node in r.snapshot().items() if key in r._HELPERS]
    # Maya's shared solver infrastructure remains; only private temporary graph is removed.
    retained = {'ikRPsolver', 'ikSCsolver', 'ikSystem'}
    nodes = [node for key, node in found if cmds.nodeType(node) not in retained]
    for node in sorted(nodes, key=lambda n: n.count('|'), reverse=True):
        if cmds.objExists(node):
            remove_owned([node])


class PM:
    def __getattr__(self, name):
        import pymel.core as real
        if name == 'cmds':
            return self
        function = getattr(real, name)
        if name not in WRITES and name not in ('objExists', 'file', 'importFile', 'exportSelected'):
            return function

        def invoke(*args, **kwargs):
            query = kwargs.get('q') or kwargs.get('query')
            if name == 'objExists' and args and str(args[0]) == 'mtbIKFK_private_snapGrp' and r._ACTIVE:
                return False  # Every run has a private fresh root; never delete a foreign snapGrp.
            if name in ('file', 'importFile', 'exportSelected'):
                raise ValueError('原场景文件进出已替换为显式自有Store JSON，不执行场景代码/强制覆盖')
            if name in WRITES and not query:
                r.require_active()
                if name == 'delete':
                    return remove_owned(args)
                if name in ('setAttr', 'setKeyframe', 'cutKey', 'keyframe', 'xform', 'makeIdentity', 'rename', 'addAttr', 'connectAttr'):
                    nodes = resolve(args[:1] if name in ('setAttr', 'xform', 'rename', 'addAttr') else args)
                    require_nodes(nodes, name in ('makeIdentity', 'rename', 'addAttr', 'connectAttr'))
                    if name == 'setAttr' and any(k in kwargs for k in ('lock', 'l', 'keyable', 'k')):
                        require_nodes(nodes, helpers_only=True)
                if name == 'parent':
                    require_nodes(resolve(args[:1]), helpers_only=True)
                before = r.snapshot() if name in CREATORS else {}
                if name in CREATORS:
                    for field in ('name', 'n'):
                        if field in kwargs:
                            kwargs[field] = r._PREFIX + str(kwargs[field]).split('|')[-1].replace(':', '_')
                result = function(*args, **kwargs)
                if name in CREATORS:
                    r._HELPERS.update(set(r.snapshot()) - set(before))
                return result
            result = function(*args, **kwargs)
            return [] if name == 'keyframe' and query and result is None else result
        return invoke


pm = PM()
