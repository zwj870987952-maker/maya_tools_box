def show_ui():
    from maya import cmds
    from .tool import StaggerOffsetTool
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for offset UI')
    name='mayaToolkitStaggerOffset'
    if cmds.window(name,exists=True):
        cmds.deleteUI(name)
    window=cmds.window(name,title='减选关键帧偏移',widthHeight=(250,120))
    cmds.columnLayout(adjustableColumn=True)
    field=cmds.floatField(value=5.0,minValue=-1000,maxValue=1000,precision=2,step=0.1)
    cmds.text(label='按明确选择顺序：首个不动；不自动展开子节点。')
    def apply(mode):
        result=StaggerOffsetTool().run(mode=mode,offset=cmds.floatField(field,query=True,value=True),update_selection=True)
        if not result.success:
            cmds.warning(result.message)
        return result
    cmds.button(label='单次减选（其余偏移一次）',command=lambda _:apply('once'))
    cmds.button(label='批量减选（逐个累计偏移）',command=lambda _:apply('batch'))
    cmds.showWindow(window)
    return window
