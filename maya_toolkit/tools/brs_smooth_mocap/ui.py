WINDOW = 'mtbBRSSmoothMocapUI'


def show():
    from maya import cmds
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    cmds.window(WINDOW, title='BRS Smooth Mocap candidate', widthHeight=(340, 240))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='Mocap: strength - 1 passes; selected keys: one pass')
    cmds.textFieldButtonGrp('mtbSMRoot', label='Root joint', buttonLabel='Selected', buttonCommand=lambda *_: fill())
    cmds.intSliderGrp('mtbSMStrength', label='Strength', field=True, minValue=1, maxValue=10, fieldMaxValue=100, value=3)
    for name, label, value in [('mtbSMAnno', 'Annotation', True), ('mtbSMBake', 'Dense locator keys', False), ('mtbSMTimeline', 'Locator range from timeline', False)]:
        cmds.checkBox(name, label=label, value=value)
    cmds.button(label='Smooth Mocap hierarchy', command=lambda *_: dispatch('smooth_mocap'))
    cmds.button(label='Smooth Selected Keys (one pass)', command=lambda *_: dispatch('smooth_keys'))
    cmds.showWindow(WINDOW)
    fill()
    return WINDOW


def fill():
    from maya import cmds
    selected = cmds.ls(selection=True, long=True, type='joint') or []
    cmds.textFieldButtonGrp('mtbSMRoot', edit=True, text=selected[0] if selected else '')


def dispatch(action):
    from maya import cmds
    from .tool import SmoothMocapTool
    args = dict(action=action)
    if action == 'smooth_mocap':
        root = cmds.textFieldButtonGrp('mtbSMRoot', query=True, text=True)
        if cmds.confirmDialog(title='BRS Smooth Mocap', message='Smooth root joint hierarchy: ' + root, button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No') != 'Yes':
            return
        args.update(root_joint=root, strength=cmds.intSliderGrp('mtbSMStrength', query=True, value=True),
                    annotation=cmds.checkBox('mtbSMAnno', query=True, value=True), bake_all=cmds.checkBox('mtbSMBake', query=True, value=True), in_timeline=cmds.checkBox('mtbSMTimeline', query=True, value=True))
    result = SmoothMocapTool().run(**args)
    if not result.success:
        cmds.warning(result.message)
