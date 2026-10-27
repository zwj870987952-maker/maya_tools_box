def dispatch(action):
    import maya.cmds as cmds
    from .tool import SpeedLinesTool
    from . import scene
    if action == 'toggle_draw':
        action = 'stop_draw' if scene.plane() else 'start_draw'
    args = {'action': action, 'camera': cmds.textField('mtbSL_bh_SL_cameraField', query=True, text=True)}
    for name, control in (('high_detail', 'bhsl_detailSwitch'), ('on_layer', 'bhsl_layerSwitch'), ('hold_two', 'bhsl_vis2s'), ('ep_tool', 'bhsl_toolMode')):
        args[name] = bool(cmds.menuItem('mtbSL_' + control, query=True, checkBox=True))
    if action == 'start_draw':
        args['depth'] = cmds.floatField('mtbSL_bhSL_depthField', query=True, value=True)
    elif action == 'draw_depth':
        args['depth'] = cmds.floatSliderGrp('mtbSL_bhSL_drawDepthSlider', query=True, value=True)
    result = SpeedLinesTool().run(**args)
    if not result.success:
        cmds.warning(result.message + '；执行失败可能已有部分修改，请检查并Undo。')
    for warning in result.warnings:
        cmds.warning(warning)
    return result.to_dict()


def on_close():
    from .tool import SpeedLinesTool
    result = SpeedLinesTool().run(action='stop_draw')
    if not result.success:
        import maya.cmds as cmds
        cmds.warning('关闭前清理失败: ' + result.message)


def tool_changed(*unused):
    # The runOnce job belongs to this window; the standard action owns cleanup.
    on_close()


def undo_changed(*unused):
    import maya.cmds as cmds
    from . import runtime, scene
    record = runtime._DRAW
    if record and not scene.find(record['uuid']):
        expected = record['uuid']
        def cleanup():
            # Defer past Maya's Undo event and ignore an already replaced session.
            if runtime._DRAW and runtime._DRAW['uuid'] == expected and not scene.find(expected):
                on_close()
        cmds.evalDeferred(cleanup, lowestPriority=True)
