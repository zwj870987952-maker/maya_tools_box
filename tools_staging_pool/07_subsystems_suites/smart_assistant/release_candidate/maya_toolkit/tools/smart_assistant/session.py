"""Explicit typed optionVar changes and reversible Python fileDialog2 patch."""
from pathlib import Path
from . import config_io
patch=None;original=None;preference_snapshot=None
def capture_prefs():
    from maya import cmds
    result={}
    for key in config_io.KEYS:
        if cmds.optionVar(exists=key):result[key]=cmds.optionVar(query=key)
    return config_io.prefs(result)
def apply_prefs(values):
    global preference_snapshot
    from maya import cmds
    values=config_io.prefs(values)
    before={k:{'exists':cmds.optionVar(exists=k),'value':cmds.optionVar(query=k) if cmds.optionVar(exists=k) else None} for k in values}
    # Keep the first pre-session value for every changed key, including keys
    # added by later apply calls. Failure rolls back this call's own full set.
    saved=preference_snapshot or {}
    for key,row in before.items():saved.setdefault(key,row)
    try:
        for key,value in values.items():
            flag='stringValue' if type(value) is str else 'intValue' if type(value) is int else 'floatValue'
            cmds.optionVar(**{flag:(key,value)})
    except Exception:
        _restore(before);raise
    preference_snapshot=saved
    return {'applied':values,'undo':'optionVars require restore_prefs; no scene Undo'}
def _restore(values):
    from maya import cmds
    for key,row in values.items():
        if not row['exists']:
            if cmds.optionVar(exists=key):cmds.optionVar(remove=key)
        else:
            v=row['value'];flag='stringValue' if type(v) is str else 'intValue' if type(v) is int else 'floatValue'
            cmds.optionVar(**{flag:(key,v)})
def restore_prefs():
    global preference_snapshot
    if preference_snapshot:_restore(preference_snapshot)
    preference_snapshot=None
def patch_dialog():
    global patch,original
    from maya import cmds
    if patch is not None:
        if cmds.fileDialog2 is not patch:raise RuntimeError('Another tool changed fileDialog2; refusing to stack hooks')
        return
    original=cmds.fileDialog2
    def wrapper(*args,**kwargs):
        current=cmds.file(query=True,sceneName=True)
        if 'startingDirectory' not in kwargs and 'dir' not in kwargs and current and Path(current).parent.is_dir():kwargs['startingDirectory']=str(Path(current).parent)
        return original(*args,**kwargs)
    patch=wrapper;cmds.fileDialog2=patch
def restore_dialog():
    global patch,original
    from maya import cmds
    if patch is not None:
        if cmds.fileDialog2 is not patch:raise RuntimeError('Foreign fileDialog2 wrapper installed later; restore that wrapper first')
        cmds.fileDialog2=original
    patch=None;original=None
def state():
    from .native.dragdrop import dragdrop_handler
    return {'dialog_patch_owned':patch is not None,'dragdrop_enabled':dragdrop_handler._filter is not None,
            'prefs_restore_available':bool(preference_snapshot)}
