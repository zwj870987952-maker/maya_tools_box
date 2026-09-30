def dispatch(action):
    from maya import cmds
    from .tool import WaveItTool
    if action == 'interactive':
        if not cmds.checkBox('mtbWI_intBox', query=True, value=True):
            return
        action = 'wave'
    args = dict(action=action,
                amplitude=cmds.floatSliderGrp('mtbWI_Size', query=True, value=True),
                frequency=cmds.floatSliderGrp('mtbWI_Freq', query=True, value=True),
                phase=cmds.floatSliderGrp('mtbWI_WaveIt', query=True, value=True),
                base_offset=cmds.floatSliderGrp('mtbWI_RotOffset', query=True, value=True),
                rotate_axes=[axis for axis in 'XYZ' if cmds.checkBox('mtbWI_rot' + axis + 'Box', query=True, value=True)],
                translate_axes=[axis for axis in 'XYZ' if cmds.checkBox('mtbWI_tra' + axis + 'Box', query=True, value=True)],
                custom_attributes=(cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True) or []) if cmds.checkBox('mtbWI_chBox', query=True, value=True) else [])
    result = WaveItTool().run(**args)
    if result.success:
        cmds.floatSliderGrp('mtbWI_Freq', edit=True, value=result.data['effective_frequency'])
        cmds.floatSliderGrp('mtbWI_WaveIt', edit=True, value=result.data['effective_phase'])
    else:
        cmds.warning(result.message)
