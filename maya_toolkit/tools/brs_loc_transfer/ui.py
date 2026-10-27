def feedback(text=''):
    from maya import cmds
    from . import legacy
    if hasattr(legacy, 'statText') and cmds.text(legacy.statText, exists=True):
        cmds.text(legacy.statText, edit=True, label=text)


def dispatch(action):
    from maya import cmds
    from . import legacy
    from .tool import LocatorTransferTool
    options = {key: cmds.checkBox(getattr(legacy, widget), query=True, value=True) for widget, key in [('AnnoChk', 'annotation'), ('BakeChk', 'bake_all'), ('ConsChk', 'constrain'), ('TimelineChk', 'in_timeline'), ('translateChk', 'translate'), ('rotateChk', 'rotate')]}
    result = LocatorTransferTool().run(action=action, **options)
    if result.success:
        if action == 'create':
            cmds.checkBox(legacy.translateChk, edit=True, value=True)
            cmds.checkBox(legacy.rotateChk, edit=True, value=True)
        feedback('')
    else:
        feedback(result.message)
        cmds.warning(result.message)
