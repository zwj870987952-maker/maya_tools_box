"""Read-only gateway opening; original full UI is an explicit action."""
import json
from .contracts import API_FUNCTIONS,CATALOG,PACKAGE


def show(tool):
    import maya.cmds as cmds
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    name = 'toolkitAnimPolishCandidate'
    if cmds.window(name,exists=True):
        cmds.deleteUI(name)
    cmds.window(name,title='AnimPolish 完整候选入口',widthHeight=(740,650))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='在备份场景测试。缓存文件不能 Undo；已有缓存不允许覆盖。',wordWrap=True)
    function = cmds.optionMenu(label='Function')
    for item in API_FUNCTIONS:
        cmds.menuItem(label=item)
    signature = cmds.scrollField(editable=False,wordWrap=True,height=110)
    arguments = cmds.scrollField(text='{}',wordWrap=True,height=100)
    output = cmds.scrollField(editable=False,wordWrap=True,height=190)
    def update(*unused):
        selected = cmds.optionMenu(function,query=True,value=True)
        cmds.scrollField(signature,edit=True,text=json.dumps(CATALOG['functions'][selected],ensure_ascii=False,indent=2))
    def run(dry,*unused):
        try:
            result = tool.run(action='invoke',function=cmds.optionMenu(function,query=True,value=True),
                              arguments=json.loads(cmds.scrollField(arguments,query=True,text=True)),dry_run=dry).to_json()
        except Exception as error:
            result = str(error)
        cmds.scrollField(output,edit=True,text=result)
    def open_original(dock,*unused):
        cmds.scrollField(output,edit=True,text=tool.run(action='open_ui',dock=dock).to_json())
    cmds.optionMenu(function,edit=True,changeCommand=update)
    cmds.button(label='Dry-run 只读预检',command=lambda *a:run(True))
    cmds.button(label='执行',command=lambda *a:run(False))
    cmds.button(label='完整原始界面（不停靠）',command=lambda *a:open_original(0))
    cmds.button(label='完整原始界面（停靠）',command=lambda *a:open_original(1))
    cmds.button(label='原始 Word 指南',command=lambda *a:cmds.showHelp((PACKAGE/'upstream/AnimPolish Documentation.docx').as_uri(),absolute=True))
    update()
    cmds.showWindow(name)
    return name
