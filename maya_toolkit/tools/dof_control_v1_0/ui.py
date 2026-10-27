_WINDOW = None


def show_window():
    global _WINDOW
    from maya import cmds
    from . import scene
    from .tool import DofControlTool
    if _WINDOW and cmds.window(_WINDOW, exists=True):
        cmds.deleteUI(_WINDOW, window=True)
    _WINDOW = cmds.window(title='DOF Control · Dirk Bialluch', widthHeight=(430, 260))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='选择camera/直接camera transform后创建；不会启用DepthOfField')
    cmds.text(label='cube -TranslateZ → focusDistance；ScaleZ → fStop')
    rows = cmds.textScrollList(height=120, allowMultiSelection=True)

    def refresh():
        cmds.textScrollList(rows, edit=True, removeAll=True)
        for node, data in scene.records():
            cmds.textScrollList(rows, edit=True, append=data['record_uuid'] + ' | ' + str(scene.find(data['camera_uuid'])))

    def action(name, template=False):
        ids = [value.split(' | ', 1)[0] for value in cmds.textScrollList(rows, query=True, selectItem=True) or []]
        result = DofControlTool().run(action=name, **({'record_ids': ids, 'template': template} if name != 'create' else {}))
        if not result.success:
            cmds.warning(result.message + str(result.errors))
        refresh()
        return result

    cmds.button(label='为当前选择创建DOF cube', command=lambda *_: action('create'))
    cmds.button(label='选中记录：模板显示', command=lambda *_: action('set_template', True))
    cmds.button(label='选中记录：正常显示', command=lambda *_: action('set_template', False))
    cmds.button(label='选中记录：清理并恢复创建前焦距/fStop', command=lambda *_: action('cleanup'))
    cmds.button(label='刷新记录', command=lambda *_: refresh())
    refresh()
    cmds.showWindow(_WINDOW)
    return _WINDOW
