from maya import cmds


def choose(panel=None):
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya modelPanel required')
    panels=cmds.getPanel(type='modelPanel') or []
    if panel:
        if panel not in panels: raise ValueError('Missing explicit modelPanel')
        return panel
    focus=cmds.getPanel(withFocus=True)
    if focus in panels: return focus
    for candidate in panels:
        if cmds.modelEditor(candidate,query=True,activeView=True): return candidate
    if not panels: raise RuntimeError('No modelPanel')
    return panels[0]


def state(panel): return bool(cmds.modelEditor(panel,query=True,sel=True))
def apply(panel,value): cmds.modelEditor(panel,edit=True,sel=value)
def exists(panel): return panel in (cmds.getPanel(type='modelPanel') or [])


def selection_state():
    return {'object':bool(cmds.selectMode(query=True,object=True)),'component':bool(cmds.selectMode(query=True,component=True)),'facet':bool(cmds.selectType(query=True,facet=True))}


def selection_apply(object_mode,facet):
    cmds.selectMode(object=True) if object_mode else cmds.selectMode(component=True)
    cmds.selectType(facet=facet)
