"""Native-window discovery and scene callbacks use the candidate adapter."""


def identify(namespace=None):
    from .engine import discover
    data = discover(namespace)
    result = {role: (values[0] if len(values) == 1 else '') if role in ('root_control', 'global_control') else values
              for role, values in data['matches'].items()}
    return result, data['namespaces']


def fill(namespace=None):
    import maya.cmds as cmds
    from .engine import discover
    data = discover(namespace)
    fields = {'root_control': 'rootControlField', 'global_control': 'globalControlField', 'ik_controls': 'ikControlsField',
              'pv_controls': 'pvControlsField', 'other_controls': 'otherControlsField'}
    for role, field in fields.items():
        values = data['matches'][role]
        text = (values[0] if len(values) == 1 else '') if role in ('root_control', 'global_control') else ', '.join(values)
        cmds.textFieldButtonGrp('mtbB2O_' + field, edit=True, text=text)
    if data['ambiguous']:
        cmds.warning('根/全局控制器不唯一，请在 Object 菜单选择命名空间或手动选择。')
    return data


def dispatch(action):
    import maya.cmds as cmds
    from .tool import Back2OriginTool
    def text(field):
        return cmds.textFieldButtonGrp('mtbB2O_' + field, query=True, text=True).strip()
    args = {'action': action, 'root_control': text('rootControlField'), 'global_control': text('globalControlField')}
    for key, field in (('ik_controls', 'ikControlsField'), ('pv_controls', 'pvControlsField'), ('other_controls', 'otherControlsField')):
        args[key] = [node.strip() for node in text(field).split(',') if node.strip()]
    args['channels'] = [axis for index, axis in enumerate(('X', 'Z'), 1) if cmds.checkBoxGrp('mtbB2O_channelCheckBoxGrp', query=True, **{'value' + str(index): True})]
    args['frame_step'] = cmds.intFieldGrp('mtbB2O_frameStepField', query=True, value1=True)
    if not cmds.checkBox('mtbB2O_bakeFromTimesliderCheckBox', query=True, value=True):
        args['start'], args['end'] = (cmds.intFieldGrp('mtbB2O_' + field, query=True, value1=True) for field in ('startFrameField', 'endFrameField'))
    result = Back2OriginTool().run(**args)
    if not result.success:
        cmds.warning(result.message + '；执行失败时可能已有部分修改，请检查后 Maya Undo。')
    for warning in result.warnings:
        cmds.warning(warning)
    return result.to_dict()
