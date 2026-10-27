def dispatch(action):
    import maya.cmds as cmds
    from .tool import BhAimTool
    args = {'action': action}
    if action in ('attach', 'bake'):
        control = 'mtbAim_keysOnlyAttachSwitch' if action == 'attach' else 'mtbAim_keysOnlyBakeSwitch'
        args['keys_only'] = bool(cmds.checkBox(control, query=True, value=True))
    if action == 'bake' and args['keys_only']:
        args['delete_rotation_keys'] = cmds.confirmDialog(title='Confirm', message='Delete ALL existing rotation keys on the control first?', button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No') == 'Yes'
    result = BhAimTool().run(**args)
    if not result.success:
        cmds.warning(result.message + '；执行失败可能已有部分修改，请检查并 Maya Undo。')
    for warning in result.warnings:
        cmds.warning(warning)
    return result.to_dict()
