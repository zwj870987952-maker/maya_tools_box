"""Complete multiline task-list UI, exact full-path selection and preflight."""
_window=None


def show_ui():
    global _window
    from maya import cmds
    from .tool import SkinWeightTransferTool
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for task-list UI')
    if _window and cmds.window(_window,exists=True):
        cmds.deleteUI(_window)
    _window=cmds.window(title='骨骼权重批量转移 — 待验收',widthHeight=(1020,560),sizeable=True)
    form=cmds.formLayout()
    label=cmds.text(label='源骨骼 => 目标骨骼 => 模型1,模型2 => DelSkin\n模型省略：从源骨骼连接自动查找。DelSkin：移除源影响，保留骨骼。完整预检后执行，单次Undo。',align='left')
    field=cmds.scrollField(editable=True,wordWrap=False,text='',height=380)
    column=cmds.columnLayout(adjustableColumn=True,rowSpacing=6)

    def load(*unused):
        selected=cmds.ls(selection=True,long=True) or []
        if len(selected)<2:
            cmds.warning('请先按顺序选择源关节、目标关节、可选网格')
            return
        line=selected[0]+' => '+selected[1]+' => '+','.join(selected[2:])
        old=cmds.scrollField(field,query=True,text=True).rstrip()
        cmds.scrollField(field,edit=True,text=(old+'\n' if old else '')+line)

    def run(dry,*unused):
        result=SkinWeightTransferTool().run(task_text=cmds.scrollField(field,query=True,text=True),dry_run=dry)
        print(result.to_json())
        if not result.success:
            cmds.warning(result.message+'；检查并Undo失败的本次操作，再继续')

    cmds.button(label='载入选择（完整路径）',height=36,command=load)
    cmds.button(label='只读预检',height=36,command=lambda *a:run(True))
    cmds.button(label='执行全部任务',height=36,bgc=(0.3,0.6,0.3),command=lambda *a:run(False))
    cmds.formLayout(form,edit=True,attachForm=[(label,'top',10),(label,'left',10),(label,'right',10),(field,'left',10),(field,'right',10),(column,'left',10),(column,'right',10),(column,'bottom',10)],attachControl=[(field,'top',10,label),(column,'top',10,field)],attachPosition=[(field,'bottom',0,72)])
    cmds.showWindow(_window)
    return _window
