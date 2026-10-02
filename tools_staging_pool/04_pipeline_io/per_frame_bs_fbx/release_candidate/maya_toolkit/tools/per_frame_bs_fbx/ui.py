"""Original script had no UI; direct build remains available, add a small panel."""
from maya import cmds
from .tool import PerFrameBsFbxTool
def show_ui():
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    if cmds.window('perFrameBsFbxCandidate',exists=True): cmds.deleteUI('perFrameBsFbxCandidate')
    window=cmds.window('perFrameBsFbxCandidate',title='模型逐帧转BS / FBX候选',widthHeight=(420,250)); cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='选择一个模型组；每采样帧和mesh生成一个BS target。')
    start=cmds.floatFieldGrp(label='开始',value1=cmds.playbackOptions(query=True,minTime=True)); end=cmds.floatFieldGrp(label='结束',value1=cmds.playbackOptions(query=True,maxTime=True)); step=cmds.floatFieldGrp(label='采样间隔',value1=1)
    name=cmds.textFieldGrp(label='输出组（空=自动）'); ascii=cmds.checkBox(label='FBX ASCII',value=False); materials=cmds.checkBox(label='复制原材质分配',value=True)
    def run(action,*args):
        p=dict(action=action,start=cmds.floatFieldGrp(start,query=True,value1=True),end=cmds.floatFieldGrp(end,query=True,value1=True),step=cmds.floatFieldGrp(step,query=True,value1=True),output_group=cmds.textFieldGrp(name,query=True,text=True) or None,ascii=cmds.checkBox(ascii,query=True,value=True),copy_materials=cmds.checkBox(materials,query=True,value=True))
        if action=='build_export':
            path=cmds.fileDialog2(fileMode=0,fileFilter='FBX (*.fbx)',caption='导出全新FBX（不覆盖）')
            if not path: return
            p['output']=path[0]
        result=PerFrameBsFbxTool().run(**p); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
    cmds.button(label='只读预检',command=lambda *a:run('inspect')); cmds.button(label='生成BS组（手动导出）',command=lambda *a:run('build')); cmds.button(label='生成并导出FBX',command=lambda *a:run('build_export'))
    cmds.showWindow(window); return window
