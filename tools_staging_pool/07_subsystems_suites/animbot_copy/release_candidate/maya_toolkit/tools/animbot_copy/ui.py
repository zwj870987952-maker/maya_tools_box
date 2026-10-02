"""Lazy native UI lifecycle; uses Maya's QApplication exclusively."""
import sys

def notify(toolbar):
    mod=sys.modules.get(__package__+'.native.core.workspace_manager')
    if mod:
        mod.WORKSPACE_MGR.workspaceChanged.emit(toolbar)
        mod.WORKSPACE_MGR.layoutConfigChanged.emit(toolbar)

def require_gui():
    import maya.cmds as cmds
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    from .native.qt import QtCore,QtWidgets
    app=QtWidgets.QApplication.instance()
    if not isinstance(app,QtWidgets.QApplication) or QtCore.QThread.currentThread()!=app.thread(): raise RuntimeError('Maya QApplication and UI main thread required')

def launch(floating=False):
    require_gui()
    from .native.ui import workspace_control as wc
    if floating: return wc.create_floating_window()
    from .workspace import CONFIGS
    return wc.dock_to_location(CONFIGS['main']['location'])

def attach_graph_editor():
    require_gui()
    from .native.ui.graph_editor_toolbar import attach_to_graph_editor
    result=attach_to_graph_editor()
    if result is None: raise RuntimeError('Graph Editor controls not found')
    return result

def open_workspace():
    require_gui()
    from .native.widgets.workspace_window import show_workspace_window
    return show_workspace_window()

def close():
    require_gui()
    mod=sys.modules.get(__package__+'.native.ui.workspace_control')
    if mod: mod.close_workspace_control()
    for module, attr in [('native.ui.graph_editor_toolbar','GRAPH_EDITOR_TOOLBAR_INSTANCE'),
                         ('native.widgets.workspace_window','_WORKSPACE_WINDOW_INSTANCE')]:
        mod=sys.modules.get(__package__+'.'+module)
        obj=getattr(mod,attr,None) if mod else None
        if obj is not None:
            from .native.qt import shiboken
            if shiboken.isValid(obj): obj.close();obj.deleteLater()
            setattr(mod,attr,None)
    # Session configuration persists across close/reopen; no module reload or preference save.

def reposition(toolbar):
    from .workspace import CONFIGS
    if toolbar=='main':
        mod=sys.modules.get(__package__+'.native.ui.workspace_control')
        if mod and mod._TOOLBAR_INSTANCE is not None: mod.dock_to_location(CONFIGS[toolbar]['location'])
    else:
        mod=sys.modules.get(__package__+'.native.ui.graph_editor_toolbar')
        if mod and mod.GRAPH_EDITOR_TOOLBAR_INSTANCE is not None: mod.dock_graph_editor_toolbar(CONFIGS[toolbar]['location'])
