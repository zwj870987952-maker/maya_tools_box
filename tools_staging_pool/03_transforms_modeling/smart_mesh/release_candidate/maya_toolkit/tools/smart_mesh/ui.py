import webbrowser
from maya import cmds
from .tool import OPTIONS

TITLES=['Smart Combine','Smart Separate','Smart Extract','Smart Duplicate Face']
ICONS=['polyUnite.png','polySeparate.png','polyChipOff.png','polyDuplicateFacet.png']


def show(tool):
    win='mtbSmartMeshToolsWindow'
    if cmds.window(win,exists=True): cmds.deleteUI(win)
    cmds.window(win,title='SmartMesh Tools v1.1.0 Candidate',widthHeight=(480,260)); cmds.columnLayout(adjustableColumn=True)
    def invoke(action,dry=False,**kwargs):
        result=tool.run(action=action,dry_run=dry,**kwargs); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        return result
    def install(option):
        if cmds.confirmDialog(title='创建工具架按钮',message='验收转正后才可创建。此UI配置写入不受Maya Undo恢复。',button=['创建','取消'],defaultButton='取消',cancelButton='取消')=='创建': invoke('shelf',option=option)
    def hotkey(option):
        name='mtbSmartHotkeyWindow'
        if cmds.window(name,exists=True): cmds.deleteUI(name)
        cmds.window(name,title='Bind '+TITLES[option]); cmds.columnLayout(adjustableColumn=True)
        field=cmds.textField(text='CSED'[option]); alt=cmds.checkBox(label='Alt',value=True); ctrl=cmds.checkBox(label='Ctrl',value=True)
        def assign(*args):
            if cmds.confirmDialog(title='确认快捷键',message='仅绑定空闲键；配置写入不能Undo，请转正后使用。',button=['绑定','取消'],defaultButton='取消',cancelButton='取消')=='绑定':
                invoke('hotkey',option=option,key=cmds.textField(field,query=True,text=True),alt=cmds.checkBox(alt,query=True,value=True),ctrl=cmds.checkBox(ctrl,query=True,value=True))
        cmds.button(label='ASSIGN',command=assign); cmds.showWindow(name)
    for i,action in enumerate(OPTIONS[:4]):
        cmds.rowLayout(numberOfColumns=5,adjustableColumn=1)
        choice=cmds.checkBox(label='自定义名',value=True)
        kwargs={'image':ICONS[i]} if cmds.resourceManager(nameFilter=ICONS[i]) else {}
        cmds.iconTextButton(style='iconAndTextHorizontal' if kwargs else 'textOnly',label=TITLES[i],command=lambda *_,action=action,choice=choice:invoke(action,custom_names=cmds.checkBox(choice,query=True,value=True)),**kwargs)
        cmds.button(label='预检',command=lambda _,action=action,choice=choice:invoke(action,True,custom_names=cmds.checkBox(choice,query=True,value=True)))
        cmds.button(label='Shelf',command=lambda _,i=i:install(i)); cmds.button(label='Hotkey',command=lambda _,i=i:hotkey(i)); cmds.setParent('..')
    cmds.button(label='Make shelf button for this window',command=lambda *_:install(4))
    def about(*args):
        name='mtbSmartMeshAbout'
        if cmds.window(name,exists=True): cmds.deleteUI(name)
        cmds.window(name,title='About SmartMesh'); cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Dennis Bartalon Porter — SmartMesh 1.1.0 / 27 January 2015\n原支持Maya2012–2015；候选其它版本待实测',align='left')
        cmds.button(label='Author Website',command=lambda *_:webbrowser.open('http://dennisporter3d.com/mel.htm'))
        cmds.button(label='SmartMesh on CreativeCrash',command=lambda *_:webbrowser.open('http://www.creativecrash.com/maya/script/smartmesh-tools'))
        cmds.showWindow(name)
    cmds.button(label='About SmartMesh Tools',command=about); cmds.showWindow(win); return win
