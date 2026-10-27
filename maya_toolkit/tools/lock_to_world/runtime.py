from functools import wraps
import uuid
from . import matrix_support as support

_ACTIVE = False
_ARGS = {}
_HELPERS = set()
_TARGETS = set()
_PREFIX = ''
cmds_module, identity, world_matrix, ensure_nodes = support.cmds_module, support.identity, support.world_matrix, support.ensure_nodes


def require_active():
    if not _ACTIVE:
        raise RuntimeError('写入须经LockToWorldTool.run')


def lock_bridge(function):
    @wraps(function)
    def call(min, max):
        if _ACTIVE:
            return function(min, max)
        for value in (min, max):
            if type(value) not in (int, float) or int(value) != value:
                raise ValueError('候选需要整数帧，不截断子帧')
        from .tool import LockToWorldTool
        c = cmds_module()
        referenced = any(c.referenceQuery(n, isNodeReferenced=True) for n in c.ls(selection=True) or [])
        if referenced and c.confirmDialog(title='Reference edits', message='Lock writes referenced controls. Continue in backup scene?', button=['Yes', 'No'], defaultButton='No') != 'Yes':
            return None
        result = LockToWorldTool().run(start=int(min), end=int(max), use_channel_box=True, allow_reference_edits=referenced)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
    return call


def execute(args):
    global _ACTIVE, _ARGS, _HELPERS, _TARGETS, _PREFIX
    c = cmds_module()
    from . import native
    if args['action'] == 'open_ui':
        native.main()
        return {'window': 'mtbLockToWorld_v09'}
    current, selection, auto, ns = c.currentTime(query=True), c.ls(selection=True, long=True) or [], c.autoKeyframe(query=True, state=True), c.namespaceInfo(currentNamespace=True)
    plugins = []
    _ACTIVE, _ARGS, _HELPERS, _TARGETS, _PREFIX = True, args, set(), {identity(n) for n in args['objects']}, 'mtbLock_' + uuid.uuid4().hex + '_'
    try:
        c.autoKeyframe(state=False)
        plugins = ensure_nodes()
        native.lockToWorld(args['start'], args['end'])
        return {'locked': args['objects'], 'range': [args['start'], args['end']], 'attributes': args['attributes'], 'frames': args['end'] - args['start'] + 1}
    finally:
        try:
            from .proxy import cleanup
            cleanup()
            for plugin in reversed(plugins):
                if c.pluginInfo(plugin, query=True, unloadOk=True):
                    c.unloadPlugin(plugin)
        finally:
            try:
                if c.currentTime(query=True) != current:
                    c.currentTime(current)
                if (c.ls(selection=True, long=True) or []) != selection:
                    c.select(selection, replace=True) if selection else c.select(clear=True)
                c.namespace(setNamespace=ns)
                c.autoKeyframe(state=auto)
            finally:
                _ACTIVE, _ARGS, _HELPERS, _TARGETS = False, {}, set(), set()
