"""Original HM one-button workflow plus explicit scopes and full preflight display."""
def show_ui():
    from maya import cmds
    from . import CleanJunkNodesTool
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    name='mtb_clean_junk_ui'
    if cmds.window(name,exists=True): cmds.deleteUI(name)
    window=cmds.window(name,title='HM 清理垃圾节点（候选）',widthHeight=(440,320)); cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='未知节点可能是缺插件的生产数据；先检查列表')
    dag=cmds.checkBox(label='同时处理 unknownDag/unknownTransform',value=False)
    unlock=cmds.checkBox(label='允许解锁并删除局部未知节点',value=False)
    plugins=cmds.checkBox(label='删除未知插件 requires 信息（须先备份，不能依赖Undo）',value=False)
    all_cb=cmds.checkBox(label='清空所有 ModelEditor 回调（含非已知回调）',value=False)
    results=cmds.scrollField(editable=False,wordWrap=True,height=160)
    def params():
        broad=cmds.checkBox(all_cb,query=True,value=True)
        return dict(action='clean',include_unknown_dag=cmds.checkBox(dag,query=True,value=True),unlock_nodes=cmds.checkBox(unlock,query=True,value=True),
            remove_unknown_plugins=cmds.checkBox(plugins,query=True,value=True),confirm_plugin_metadata_loss=cmds.checkBox(plugins,query=True,value=True),callback_policy='all' if broad else 'known',confirm_all_callbacks=broad)
        # Plugin checkbox is explicit acknowledgement that this metadata may not Undo.
    def check(*unused):
        result=CleanJunkNodesTool().run(dry_run=True,**params()); cmds.scrollField(results,edit=True,text=result.to_json())
        return result
    def clean(*unused):
        preview=check()
        if not preview.success: return
        if cmds.confirmDialog(title='确认清理范围',message='删除预检列出的局部未知节点/插件信息并清回调？请先保存备份。',button=['清理','取消'],defaultButton='取消',cancelButton='取消')!='清理': return
        result=CleanJunkNodesTool().run(**params()); cmds.scrollField(results,edit=True,text=result.to_json())
    cmds.button(label='预检完整列表',command=check)
    cmds.button(label='一键清理',height=50,command=clean); cmds.showWindow(window); return window
