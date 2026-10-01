from maya import cmds
from .tool import SkeletonGeneratorTool


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    name = 'stagingSkeletonGenerator'
    if cmds.window(name,exists=True):
        cmds.showWindow(name)
        return name
    cmds.window(name,title='选区生成骨骼链',widthHeight=(390,180))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='仅所选 joint/locator；直接选中父子关系保留，不复制缩放/动画。')
    cmds.textFieldGrp('stagingSkeletonSuffix',label='新骨架后缀',text='_copy')
    cmds.checkBox('stagingSkeletonSelect',label='选择新创建骨架',value=True)
    def call(dry):
        result = SkeletonGeneratorTool().run(dry_run=dry,suffix=cmds.textFieldGrp('stagingSkeletonSuffix',query=True,text=True),select_result=cmds.checkBox('stagingSkeletonSelect',query=True,value=True))
        if result.success:
            cmds.text('stagingSkeletonStatus',edit=True,label='{} 个对象 / {} 个根'.format(len(result.data['rows']),len(result.data['roots'])))
        else:
            cmds.warning(result.message)
    cmds.button(label='只读预检',command=lambda unused=False:call(True))
    cmds.button(label='生成骨架',command=lambda unused=False:call(False))
    cmds.text('stagingSkeletonStatus',label='请选择骨骼或定位器')
    cmds.showWindow(name)
    return name
