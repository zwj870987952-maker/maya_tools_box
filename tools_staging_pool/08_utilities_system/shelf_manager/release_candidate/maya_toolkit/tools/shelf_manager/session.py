from pathlib import Path
import importlib,json
from . import backend
window=None;source_roots=None;own_ui={};loaded={}
def close():
    global window
    if window is None:return
    from maya import cmds,OpenMayaUI
    name=window.window_name
    if cmds.window(name,exists=True):
        if not own_ui.get(name) or int(OpenMayaUI.MQtUtil.findWindow(name) or 0)!=own_ui[name]:raise RuntimeError('Foreign window replacement preserved')
        cmds.deleteUI(name,window=True)
    own_ui.pop(name,None);window=None
def show(values=None):
    global window,source_roots
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    source_roots=[str(p) for p in backend.roots(values or backend.detect())];close();module=importlib.import_module('maya_toolkit.tools.shelf_manager.native');window=module.ShelfManager();return window
class Commands:
    def __getattr__(self,name):
        from maya import cmds,OpenMayaUI
        fn=getattr(cmds,name)
        def call(*args,**kw):
            if name=='deleteUI':
                if not args or args[0] not in own_ui:raise ValueError('Foreign UI deletion refused')
                if int(OpenMayaUI.MQtUtil.findWindow(args[0]) or 0)!=own_ui[args[0]]:raise ValueError('Foreign UI replacement preserved')
            if name=='window' and args and not any(kw.get(k) for k in ('exists','ex','query','q','edit','e')) and cmds.window(args[0],exists=True):raise ValueError('Existing manager window preserved')
            result=fn(*args,**kw)
            if name=='window' and not any(kw.get(k) for k in ('exists','ex','query','q','edit','e')):own_ui[result]=int(OpenMayaUI.MQtUtil.findWindow(result) or 0)
            if name=='deleteUI':own_ui.pop(args[0],None)
            return result
        return call
cmds=Commands()
def load_shelf(value):
    from maya import cmds,mel,OpenMayaUI
    path=backend.path(value)
    name=path.stem[6:]
    top=mel.eval('$tmp=$gShelfTopLevel');before=cmds.tabLayout(top,q=True,childArray=True) or []
    for child in before:
        if child.rsplit('|',1)[-1]==name or cmds.shelfLayout(child,q=True,annotation=True)==name:raise ValueError('Existing shelf UI preserved; rename incoming shelf first')
    mel.eval('loadNewShelf '+json.dumps(str(path).replace('\\','/'))+';')
    after=cmds.tabLayout(top,q=True,childArray=True) or []
    for child in set(after)-set(before):loaded[child]=int(OpenMayaUI.MQtUtil.findLayout(child) or 0)
    return {'source':str(path),'added_layouts':sorted(set(after)-set(before)),'executes_mel':True}
def gui_load(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    files=[r[1] for r in selected];backend.selected(manager.user_paths,files,False)
    if cmds.confirmDialog(title='加载工具架',message='加载会执行所选MEL文件代码，仅继续信任的工具架。',button=['Load','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')!='Load':return
    results=[load_shelf(value) for value in files];cmds.text(manager.status_text,e=True,label='已加载 {} 个工具架'.format(len(results)))
def gui_delete(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    rows=backend.selected(manager.user_paths,[r[1] for r in selected],True)
    if cmds.confirmDialog(title='移入可恢复目录',message='将所选工具架及同名PNG移入源root下独立隔离目录；保留receipt，不删除已存在的外来shelf UI。',button=['Quarantine','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')!='Quarantine':return
    result=backend.quarantine(rows);manager._initial_scan();cmds.text(manager.status_text,e=True,label='已隔离 {} 个文件；源root的.mtb_shelf_trash_*中可恢复'.format(len(result)))
def gui_migrate(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    targets=cmds.fileDialog2(fileMode=3,caption='选择复制目标目录（源文件保留，已有同名拒绝）')
    if not targets:return
    rows=backend.migration(manager.user_paths,[r[1] for r in selected],targets[0],True,False);result=backend.migrate(rows);cmds.text(manager.status_text,e=True,label='已复制 {} 个文件，源文件保留'.format(len(result)))
