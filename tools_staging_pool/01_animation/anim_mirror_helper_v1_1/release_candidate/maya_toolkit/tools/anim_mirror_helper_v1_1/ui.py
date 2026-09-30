"""Candidate control panel; opening this panel never sources original MEL."""
import json
from .contracts import ACTIONS, ALIASES, CATALOG, PACKAGE


def show(tool):
    import maya.cmds as cmds
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    name = 'toolkitAnimMirrorHelperCandidate'
    if cmds.window(name,exists=True):
        cmds.deleteUI(name)
    cmds.window(name,title='Anim Mirror Helper 候选入口',widthHeight=(720,600))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='在备份场景测试。开启原始界面后，其按钮使用原始 MEL 回调。',wordWrap=True)
    action = cmds.optionMenu(label='Action')
    for item in ACTIONS:
        cmds.menuItem(label=item)
    proc = cmds.optionMenu(label='Original procedure (invoke)')
    for item in sorted(CATALOG['procedures']):
        cmds.menuItem(label=item)
    help_text = cmds.scrollField(editable=False,height=100,wordWrap=True)
    arguments = cmds.scrollField(text='{}',height=110,wordWrap=True)
    reload_flag = cmds.checkBox(label='Force reload original MEL',value=False)
    output = cmds.scrollField(editable=False,height=170,wordWrap=True)
    def update(*unused):
        a = cmds.optionMenu(action,query=True,value=True)
        p = ALIASES.get(a,cmds.optionMenu(proc,query=True,value=True) if a=='invoke' else '')
        signature = CATALOG['procedures'].get(p,{})
        cmds.scrollField(help_text,edit=True,text=json.dumps(signature,ensure_ascii=False,indent=2))
    def run(dry,*unused):
        try:
            a = cmds.optionMenu(action,query=True,value=True)
            kwargs = dict(action=a,arguments=json.loads(cmds.scrollField(arguments,query=True,text=True)),
                          force_reload=cmds.checkBox(reload_flag,query=True,value=True))
            if a=='invoke':
                kwargs['procedure'] = cmds.optionMenu(proc,query=True,value=True)
            result = tool.run(dry_run=dry,**kwargs).to_json()
        except Exception as error:
            result = str(error)
        cmds.scrollField(output,edit=True,text=result)
    cmds.optionMenu(action,edit=True,changeCommand=update)
    cmds.optionMenu(proc,edit=True,changeCommand=update)
    cmds.button(label='Dry-run 只读预检',command=lambda *a:run(True))
    cmds.button(label='执行选择的 Action',command=lambda *a:run(False))
    cmds.button(label='打开完整原始界面',command=lambda *a:cmds.scrollField(output,edit=True,text=tool.run(action='open_ui').to_json()))
    cmds.button(label='原始英文指南',command=lambda *a:cmds.showHelp((PACKAGE/'upstream/Anim Mirror Helper guide ENG.pdf').as_uri(),absolute=True))
    update()
    cmds.showWindow(name)
    return name
