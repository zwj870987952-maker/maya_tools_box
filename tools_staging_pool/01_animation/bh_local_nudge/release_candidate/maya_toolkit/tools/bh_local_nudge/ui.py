def dispatch(channel, axis, direction):
    import maya.cmds as cmds
    from .tool import LocalNudgeTool
    amount = cmds.floatSliderGrp('mtbLN_NudgeVal' if channel == 'translate' else 'mtbLN_RotVal', query=True, value=True)
    mods = cmds.getModifiers()
    result = LocalNudgeTool().run(channel=channel, axis=axis, direction=direction, amount=amount, ctrl=bool(mods & 4), alt=bool(mods & 8))
    if not result.success:
        cmds.warning(result.message + '；执行失败可能已部分写入，请检查并 Undo。')
    for warning in result.warnings:
        cmds.warning(warning)
    return result.to_dict()
