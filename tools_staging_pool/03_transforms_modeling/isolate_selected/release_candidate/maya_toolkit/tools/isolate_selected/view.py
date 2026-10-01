"""Native panel operations are exercised only in interactive Maya acceptance."""
from maya import cmds


def choose(panel=None):
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya modelPanel required')
    if panel:
        if cmds.getPanel(typeOf=panel)!='modelPanel': raise ValueError('Explicit modelPanel not found')
        return panel
    current=cmds.getPanel(withFocus=True)
    if current and cmds.getPanel(typeOf=current)=='modelPanel': return current
    panels=cmds.getPanel(type='modelPanel') or []
    if not panels: raise RuntimeError('No modelPanel found')
    return panels[0]


def state(panel):
    enabled=bool(cmds.isolateSelect(panel,query=True,state=True))
    group=cmds.isolateSelect(panel,query=True,viewObjects=True) if enabled else None
    return {'enabled':enabled,'members':cmds.sets(group,query=True) or [] if group else []}


def apply(panel,objects):
    cmds.isolateSelect(panel,state=False)
    cmds.select(objects,replace=True)
    cmds.isolateSelect(panel,state=True)
    cmds.isolateSelect(panel,loadSelected=True)
    cmds.isolateSelect(panel,update=True)


def restore(panel,snapshot,members):
    cmds.isolateSelect(panel,state=False)
    if snapshot['enabled']:
        cmds.select(members,replace=True) if members else cmds.select(clear=True)
        cmds.isolateSelect(panel,state=True)
        cmds.isolateSelect(panel,loadSelected=True)
        cmds.isolateSelect(panel,update=True)
