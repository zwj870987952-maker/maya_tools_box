"""Original native MEL layout with its scene actions routed to the standard API."""


def options():
    import maya.cmds as cmds
    values = {'translations': bool(cmds.checkBox('mtbAV2_TranslationsCheckbox', query=True, value=True)),
              'rotations': bool(cmds.checkBox('mtbAV2_RotationsCheckbox', query=True, value=True))}
    values['translation_axis'] = next(axis for axis in 'XYZ' if cmds.radioButton('mtbAV2_' + axis + 'AxisTransRadio', query=True, select=True))
    values['invert_rotation'] = [axis for axis in 'XYZ' if cmds.checkBox('mtbAV2_' + axis + 'AxisRotCheckbox', query=True, value=True)]
    return values


def dispatch(action):
    import maya.cmds as cmds
    from .tool import AnimirrorV2Tool
    result = AnimirrorV2Tool().run(action=action, **options())
    if not result.success:
        cmds.warning(result.message + '；可能已部分改场景，请检查后用 Maya Undo 撤回。')
    else:
        for warning in result.warnings:
            cmds.warning(warning)
    return result.to_dict()


def show_ui():
    from .tool import AnimirrorV2Tool
    result = AnimirrorV2Tool().run(action='open_ui')
    if not result.success:
        raise RuntimeError(result.message)
    return result.data['window']
