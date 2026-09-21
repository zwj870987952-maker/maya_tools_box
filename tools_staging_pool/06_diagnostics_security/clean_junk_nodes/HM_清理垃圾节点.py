import pymel.core as pm
 
def delete_unknowNodes(*args):
    ls_unknownNodes = pm.ls(type='unknown')
    if pm.objExists('ls_unknownNodes'):
        pm.lockNode(ls_unknownNodes,lock=False)
        pm.delete(ls_unknownNodes)
    else:
        print(u'没有可以清理得未知节点啦~')

def delete_unknowPlugins(*args):
    plugin_list = pm.unknownPlugin(q=True,l=True)
    if plugin_list:
        for plugin in plugin_list:
            
            try:
                pm.unknownPlugin(plugin,r=True)
                print(u'{}_节点已被清理！'.format(plugin))
            except:
                pass
    else:
        print(u'没有可以清理得未知插件啦~')

def delete_callback_node(*args):
    for model_panel in cmds.getPanel(typ="modelPanel"):
        callback = cmds.modelEditor(model_panel, query=True, editorChanged=True)
        if callback == "CgAbBlastPanelOptChangeCallback":
            cmds.modelEditor(model_panel, edit=True, editorChanged="")
    for item in pm.lsUI(editors=True):
        if isinstance(item, pm.ui.ModelEditor):
            pm.modelEditor(item, edit=True, editorChanged='')

def run_delete(*args):
    delete_unknowNodes()
    delete_unknowPlugins()
    delete_callback_node()

if pm.window('cleanup_node_ui', ex=True):
    pm.deleteUI('cleanup_node_ui')
if pm.windowPref('cleanup_node_ui', ex=True):
    pm.windowPref('cleanup_node_ui', remove=True)
window = pm.window( 'cleanup_node_ui', title=u'HM_清理垃圾节点工具',widthHeight=(300,50) )
pm.columnLayout( adjustableColumn=True)
pm.button( label=u'清理场景', h=50,c=run_delete )
pm.showWindow()