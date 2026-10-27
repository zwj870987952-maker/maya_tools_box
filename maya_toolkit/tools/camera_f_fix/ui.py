_window=None


def show_ui():
    global _window
    from maya import cmds
    from .tool import CameraFFixTool
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    if _window and cmds.window(_window,exists=True):
        cmds.deleteUI(_window)
    _window=cmds.window(title='按 F 相机重置 — 待验收',widthHeight=(440,170))
    cmds.columnLayout(adjustableColumn=True,rowSpacing=8)
    cmds.text(label='重置相机局部变换并设平移为 (1,1,1)。\n旋转/缩放默认沿用 Maya Reset Transformations 偏好。',align='left')
    field=cmds.textField(text='persp')
    keep=cmds.checkBox(label='保留当前选择（原脚本会选中相机）',value=False)
    def run(dry,*unused):
        result=CameraFFixTool().run(camera=cmds.textField(field,query=True,text=True),preserve_selection=cmds.checkBox(keep,query=True,value=True),dry_run=dry)
        print(result.to_json())
        if not result.success:
            cmds.warning(result.message)
    cmds.button(label='只读预检',command=lambda *a:run(True))
    cmds.button(label='执行相机重置',command=lambda *a:run(False))
    cmds.showWindow(_window)
    return _window
