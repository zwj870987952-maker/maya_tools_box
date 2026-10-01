from .tool import OPTIONS


def command(option):
    if option==4: return 'from maya_toolkit.tools.smart_mesh import SmartMeshTool; SmartMeshTool().show_ui()'
    return "from maya_toolkit.tools.smart_mesh import SmartMeshTool; SmartMeshTool().run(action=%r)"%OPTIONS[option]


def preflight(p):
    from maya import cmds,mel
    from maya_toolkit.framework import ToolRegistry
    if cmds.about(batch=True): raise RuntimeError('Interactive promoted Maya required for installation')
    if ToolRegistry.get('smart_mesh') is None: raise ValueError('Accept/promote/register candidate before persistent shelf/hotkey installation')
    if p['action']=='shelf':
        shelf=p.get('shelf')
        if not shelf:
            top=mel.eval('$mtbSmartShelf=$gShelfTopLevel;')
            if not top or not cmds.tabLayout(top,exists=True): raise ValueError('Existing shelf tab UI required')
            tab=cmds.tabLayout(top,query=True,selectTab=True); shelf=top+'|'+tab
        if not cmds.shelfLayout(shelf,exists=True): raise ValueError('Existing shelf layout required')
        return {'shelf':shelf,'command':command(p['option']),'persistent_ui_write':True,'undoable':False}
    if cmds.hotkey(keyShortcut=p['key'],altModifier=p['alt'],ctrlModifier=p['ctrl'],query=True,name=True) or cmds.hotkey(keyShortcut=p['key'],altModifier=p['alt'],ctrlModifier=p['ctrl'],query=True,releaseName=True): raise ValueError('Hotkey press/release already bound; choose unused key/modifiers')
    runtime='mtbSmartMesh_'+OPTIONS[p['option']]
    if cmds.runTimeCommand(runtime,exists=True) and (cmds.runTimeCommand(runtime,query=True,command=True)!=command(p['option']) or cmds.runTimeCommand(runtime,query=True,commandLanguage=True)!='python'): raise ValueError('Runtime command name owned by another definition')
    named=runtime+'Named'
    # Read named commands through the assignment table; avoid unsupported
    # nameCommand query flags and never overwrite a foreign definition.
    count=cmds.assignCommand(query=True,numElements=True)
    for i in range(1,count+1):
        if cmds.assignCommand(i,query=True,name=True)==named and cmds.assignCommand(i,query=True,command=True)!=runtime: raise ValueError('Named command collision')
    return {'runtime':runtime,'named':named,'command':command(p['option']),'persistent_preferences_write':True,'undoable':False}


def execute(p,scope):
    from maya import cmds
    if p['action']=='shelf':
        button=cmds.shelfButton(parent=scope['shelf'],label='SmartMesh '+OPTIONS[p['option']],annotation='SmartMesh '+OPTIONS[p['option']],sourceType='python',command=scope['command'])
        return dict(scope,button=button)
    runtime=scope['runtime']
    if not cmds.runTimeCommand(runtime,exists=True):
        cmds.runTimeCommand(runtime,annotation='SmartMesh '+OPTIONS[p['option']],category='User',commandLanguage='python',command=scope['command'])
    cmds.nameCommand(scope['named'],annotation='SmartMesh '+OPTIONS[p['option']],command=runtime,sourceType='mel')
    cmds.hotkey(keyShortcut=p['key'],altModifier=p['alt'],ctrlModifier=p['ctrl'],name=scope['named'])
    return scope
