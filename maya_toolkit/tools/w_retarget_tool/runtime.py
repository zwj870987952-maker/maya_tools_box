from types import SimpleNamespace
import uuid
from maya import cmds


def uid(name):
    return cmds.ls(name, uuid=True)[0]


class OwnedCommands:
    def __init__(self):
        self.owned = set()
        self.token = uuid.uuid4().hex
        self.prefix = 'wRetarget_' + self.token + '_'

    def __getattr__(self, name):
        function = getattr(cmds, name)
        if name not in ('group', 'shadingNode', 'parentConstraint', 'pointConstraint'):
            return function
        def invoke(*args, **kwargs):
            result = function(*args, **kwargs)
            nodes = result if isinstance(result, list) else [result]
            for node in nodes:
                self.owned.add(uid(node))
                cmds.addAttr(node, longName='wRetargetTemporaryOwner', dataType='string')
                cmds.setAttr(node + '.wRetargetTemporaryOwner', self.token, type='string')
            return result
        return invoke

    def delete(self, *args):
        nodes = []
        for arg in args:
            nodes.extend(arg if isinstance(arg, list) else [arg])
        for name in nodes:
            if not cmds.objExists(name):
                continue
            if uid(name) not in self.owned:
                raise RuntimeError('Refusing to delete a non-owned helper')
            for child in cmds.listRelatives(name, allDescendents=True, fullPath=True) or []:
                if uid(child) not in self.owned:
                    raise RuntimeError('Foreign child attached to helper; cleanup blocked')
            cmds.delete(name)

    def progressBar(self, *args, **kwargs):
        # Native progress only runs when an explicit UI callback is supplied.
        if args and args[0] is not None:
            return cmds.progressBar(*args, **kwargs)

    def cleanup(self):
        nodes = [n for n in cmds.ls(long=True) or [] if uid(n) in self.owned]
        for name in sorted(nodes, key=lambda n: n.count('|'), reverse=True):
            if cmds.objExists(name):
                self.delete(name)


def retarget(plan, progress_control=None):
    from . import engine
    original = engine.cmds
    tracker = OwnedCommands()
    state = {'time': cmds.currentTime(query=True), 'selection': cmds.ls(selection=True, long=True) or [], 'autokey': cmds.autoKeyframe(query=True, state=True)}
    completed = []
    try:
        engine.cmds = tracker
        cmds.autoKeyframe(state=False)
        adapter = SimpleNamespace(ProgressControl=progress_control)
        for pair in plan['pairs']:
            engine.copy_anim(adapter, source=pair['source'], target=pair['target'], start_frame=plan['start_frame'], end_frame=plan['end_frame_exclusive'], prefix=tracker.prefix, ValidObj=len(plan['pairs']))
            completed.append(pair)
        return dict(plan, completed_pairs=completed, temporary_nodes='all owned helpers/matrix nodes removed')
    finally:
        try:
            tracker.cleanup()
        finally:
            engine.cmds = original
            cmds.currentTime(state['time'])
            cmds.autoKeyframe(state=state['autokey'])
            if state['selection']:
                cmds.select(state['selection'], replace=True)
            else:
                cmds.select(clear=True)
