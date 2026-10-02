from maya import cmds
from .tool import VesselFbxExporterTool
def show_ui():
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    if cmds.window('vesselFbxCandidate',exists=True): cmds.deleteUI('vesselFbxCandidate')
    window=cmds.window('vesselFbxCandidate',title='舰船选择集FBX（当前场景私有副本）',widthHeight=(460,320)); cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='整个流程在隔离Maya副本运行；Reset_Trans会清空其所有keys。')
    keyword=cmds.textFieldGrp(label='AAA替换关键词',text='vessel'); directory=cmds.textFieldButtonGrp(label='结果目录',buttonLabel='浏览')
    def browse(*args):
        chosen=cmds.fileDialog2(fileMode=3,caption='选择FBX结果目录')
        if chosen: cmds.textFieldButtonGrp(directory,edit=True,text=chosen[0])
    cmds.textFieldButtonGrp(directory,edit=True,buttonCommand=browse)
    checks={key:cmds.checkBox(label=label,value=default) for key,label,default in [('bake_joints','All_joints烘焙',True),('bake_export_sets','烘焙_FBXExport成员（原默认关闭）',False),('reset_transforms','Reset_Trans重置并删除其全部keys',True),('import_references','副本导入全部reference',True),('remove_namespaces','副本移除导出集合/成员namespace',True),('rename_root','副本导出后rename root',True),('reference_results','副本引用FBX结果',False),('save_prepared_scene','另存副本准备场景MA',False)]}
    def run(action,*args):
        result=VesselFbxExporterTool().run(action=action,keyword=cmds.textFieldGrp(keyword,query=True,text=True),output_dir=cmds.textFieldButtonGrp(directory,query=True,text=True) or None,**{k:cmds.checkBox(v,query=True,value=True) for k,v in checks.items()}); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
    cmds.button(label='只读预检：集合/成员/输出',command=lambda *a:run('inspect')); cmds.button(label='私有副本执行原完整流程并导出',command=lambda *a:run('process'))
    cmds.showWindow(window); return window
