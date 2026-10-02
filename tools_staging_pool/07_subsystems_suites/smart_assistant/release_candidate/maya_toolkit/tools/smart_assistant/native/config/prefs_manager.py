from ... import session,config_io
def export_prefs(path=None):
    from maya import cmds
    if path is None:
        chosen=cmds.fileDialog2(fileMode=0,fileFilter='JSON (*.json)',caption='Export to new config file')
        if not chosen:return None
        path=chosen[0]
    return config_io.write_prefs(path,session.capture_prefs())
def apply_prefs(path=None):
    from maya import cmds
    if path is None:
        chosen=cmds.fileDialog2(fileMode=1,fileFilter='JSON (*.json)',caption='Apply saved preference optionVars')
        if not chosen:return None
        path=chosen[0]
    return session.apply_prefs(config_io.read_prefs(path))
