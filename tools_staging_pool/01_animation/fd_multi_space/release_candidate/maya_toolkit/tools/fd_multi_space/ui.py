"""Both original three-step workflows; every scene button uses standard API."""
from functools import partial


def show():
    from maya import cmds
    name = 'mtbFD_multiSpaceMain'
    if cmds.window(name, exists=True):
        cmds.deleteUI(name, window=True)
    cmds.window(name, title='FD Multi Space version', widthHeight=(270, 120))
    cmds.columnLayout(adjustableColumn=True)
    cmds.separator(height=15, style='none')
    cmds.button(label='Multi Space (reference / existing parent)', backgroundColor=[0.8, 0.5, 0], command=partial(show_mode, 'reference'))
    cmds.separator(height=20)
    cmds.button(label='Multi Space (local / new space group)', command=partial(show_mode, 'local'))
    cmds.showWindow(name)
    return name


def show_mode(mode, *unused):
    from maya import cmds
    from .tool import MultiSpaceTool
    from . import scene
    name = 'mtbFD_multiSpace_' + mode
    if cmds.window(name, exists=True):
        cmds.deleteUI(name, window=True)
    cmds.window(name, title='Multi Space - ' + mode, widthHeight=(480, 280))
    cmds.columnLayout(adjustableColumn=True)
    attribute = cmds.textFieldGrp(label='New Attribute name:', text='space', adjustableColumn=2)
    reference = cmds.checkBox(label='Allow intended Maya reference edits', value=False, enable=mode == 'reference')
    identifier = cmds.textFieldGrp(label='Record UUID (resume):', adjustableColumn=2)
    status = cmds.text(label='First select driven control; then driver control.', align='left')

    def selection():
        selected = cmds.ls(selection=True, long=True) or []
        if len(selected) != 1:
            raise ValueError('Exactly one transform must be selected')
        return selected[0]

    def invoke(action, *unused):
        try:
            args = {'action': action, 'mode': mode, 'allow_reference_edits': cmds.checkBox(reference, query=True, value=True)}
            if action == 'prepare':
                args.update(driven=selection(), attribute=cmds.textFieldGrp(attribute, query=True, text=True))
            else:
                args['record_id'] = cmds.textFieldGrp(identifier, query=True, text=True)
                if action == 'add_driver':
                    args['driver'] = selection()
            result = MultiSpaceTool().run(**args)
            if not result.success:
                raise RuntimeError(result.message)
            cmds.textFieldGrp(identifier, edit=True, text=result.data['record_id'])
            cmds.text(status, edit=True, label='Phase ' + str(result.data['phase']) + ': ' + result.data['record_id'])
        except Exception as error:
            cmds.warning(str(error))
            cmds.text(status, edit=True, label=str(error) + ' / partial failure: Undo and inspect')

    cmds.separator(height=15)
    cmds.button(label='1 - Select driven, type name and prepare', command=partial(invoke, 'prepare'))
    cmds.separator(height=10)
    cmds.button(label='2 - Select driver and create constraint', command=partial(invoke, 'add_driver'))
    cmds.separator(height=10)
    cmds.button(label='3 - Connect explicit weight', backgroundColor=[0.8, 0.5, 0], command=partial(invoke, 'connect'))
    cmds.text(label='Existing record UUIDs:')
    box = cmds.textScrollList(height=60)
    for row in scene.records():
        if row['mode'] == mode:
            cmds.textScrollList(box, edit=True, append=row['record_id'])
    cmds.textScrollList(box, edit=True, selectCommand=lambda: cmds.textFieldGrp(identifier, edit=True, text=(cmds.textScrollList(box, query=True, selectItem=True) or [''])[0]))
    cmds.showWindow(name)
    return name
