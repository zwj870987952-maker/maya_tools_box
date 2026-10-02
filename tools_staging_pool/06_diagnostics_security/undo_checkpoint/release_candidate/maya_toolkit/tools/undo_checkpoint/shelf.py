"""Four idempotent session Shelf shortcuts, package imports and real newlines."""
BUTTONS=[('panel','CP面板','history.png',"UndoCheckpointTool().show_ui()"),
         ('create','设记录','setKeyframe.png',"UndoCheckpointTool().run(action='create',overwrite=True,name='唯一记录点')"),
         ('restore','回记录','undo.png',"UndoCheckpointTool().run(action='restore')"),
         ('clear','清记录','delete.png',"UndoCheckpointTool().run(action='clear')")]
def command(expression):return 'from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool\n'+expression+'\n'
def shelf_plan(shelf_name=None):
    from maya import cmds,mel
    if cmds.about(batch=True):raise ValueError('Shelf requires interactive Maya')
    shelf=shelf_name or mel.eval('tabLayout -q -st $gShelfTopLevel;')
    if not shelf or not cmds.shelfLayout(shelf,exists=True):raise ValueError('Active Shelf missing')
    return {'shelf':shelf,'buttons':[{'id':identifier,'label':label,'image':image,'command':command(expression)} for identifier,label,image,expression in BUTTONS],
            'impact':'Changes 4 owned session Shelf buttons; preferences not automatically saved; not scene Undo'}
def install_to_shelf(shelf_name=None):
    from maya import cmds
    plan=shelf_plan(shelf_name);children=cmds.shelfLayout(plan['shelf'],query=True,childArray=True) or [];owned={}
    for child in children:
        if cmds.shelfButton(child,exists=True):
            tag=cmds.shelfButton(child,query=True,docTag=True)
            if tag.startswith('maya_toolkit.undo_checkpoint.'):owned[tag.rsplit('.',1)[1]]=child
    for button in plan['buttons']:
        options=dict(label=button['label'],annotation=button['label'],image1=button['image'],command=button['command'],sourceType='python',imageOverlayLabel=button['label'],docTag='maya_toolkit.undo_checkpoint.'+button['id'])
        if button['id'] in owned:cmds.shelfButton(owned[button['id']],edit=True,**options)
        else:cmds.shelfButton(parent=plan['shelf'],**options)
    return plan
