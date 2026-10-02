from pathlib import Path
import re
from maya_toolkit.framework import BaseMayaTool,ToolResult
from maya_toolkit.core.context import UndoChunkContext as UndoChunk
_filters=[];_dialogs=[]
def source(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Valid file path required')
    p=Path(value)
    if not p.is_absolute() or not p.is_file() or p.suffix.lower() not in ('.ma','.mb') or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Existing absolute Maya ma/mb file required')
    return str(p)
def namespace(value,path):
    if value is None:value=re.sub('[^A-Za-z0-9_]','_',Path(path).stem)
    if value and value[0].isdigit():value='file_'+value
    if not isinstance(value,str) or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]{0,127}',value):raise ValueError('Simple root namespace required')
    return value
def perform(path,action,ns=None,confirm_discard=False):
    from maya import cmds
    path=source(path)
    if action=='open':
        if cmds.file(q=True,modified=True) and not confirm_discard:raise ValueError('Modified scene requires explicit discard confirmation or save first')
        return cmds.file(path,open=True,force=True,executeScriptNodes=False)
    ns=namespace(ns,path)
    if cmds.namespace(exists=ns):raise ValueError('Existing namespace preserved; choose another')
    if action not in ('import','reference'):raise ValueError('Unknown file action')
    with UndoChunk('MTB_FileDrop_'+action):
        return cmds.file(path,namespace=ns,mergeNamespacesOnClash=False,returnNewNodes=True,executeScriptNodes=False,**({'i':True} if action=='import' else {'reference':True}))
def interactive(value,parent=None):
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    path=source(value)
    choice=cmds.confirmDialog(title='文件拖拽',message='选择导入、打开或引用：\n'+path,button=['Import','Open','Reference','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')
    if choice=='Cancel':return {'cancelled':True}
    discard=False
    if choice=='Open' and cmds.file(q=True,modified=True):
        answer=cmds.confirmDialog(title='打开场景',message='当前场景有未保存修改。',button=['Save','Discard','Cancel'],defaultButton='Save',cancelButton='Cancel',dismissString='Cancel')
        if answer=='Cancel':return {'cancelled':True}
        if answer=='Save':
            name=cmds.file(q=True,sn=True)
            if not name:
                names=cmds.fileDialog2(fileMode=0,fileFilter='Maya (*.ma *.mb)')
                if not names:return {'cancelled':True}
                name=names[0]
            from . import backups
            backups.save_scene(name)
        else:discard=True
    action=choice.lower();ns=None
    if action!='open':
        ns=namespace(None,path)
        if cmds.namespace(exists=ns):
            response=cmds.promptDialog(title='Namespace已存在',message='输入新的root namespace',text=ns+'_new',button=['OK','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')
            if response!='OK':return {'cancelled':True}
            ns=namespace(cmds.promptDialog(q=True,text=True),path)
    return {'cancelled':False,'result':perform(path,action,ns,discard)}
def install():
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    from .qt_compat import QtCore,QtWidgets,wrapInstance
    from maya import OpenMayaUI
    app=QtWidgets.QApplication.instance()
    if app is None or QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Existing Maya Qt main thread required')
    close()
    class DropFilter(QtCore.QObject):
        def eventFilter(self,widget,event):
            if event.type() not in (QtCore.QEvent.DragEnter,QtCore.QEvent.DragMove,QtCore.QEvent.Drop):return False
            mime=event.mimeData()
            if not mime.hasUrls():return False
            urls=mime.urls()
            if len(urls)!=1 or not urls[0].isLocalFile():return False
            value=urls[0].toLocalFile()
            try:source(value)
            except ValueError:return False
            if event.type()==QtCore.QEvent.Drop:
                try:interactive(value,widget)
                except Exception as e:cmds.warning(str(e))
            event.acceptProposedAction();return True
    for panel in cmds.getPanel(type='modelPanel') or []:
        pointer=OpenMayaUI.MQtUtil.findControl(panel)
        if not pointer:continue
        widget=wrapInstance(int(pointer),QtWidgets.QWidget);owned=DropFilter(widget);widget.installEventFilter(owned);_filters.append((widget,owned))
    if not _filters:raise RuntimeError('No model-panel widgets found')
    return len(_filters)
def close():
    for widget,owned in list(_filters):
        try:widget.removeEventFilter(owned);owned.deleteLater()
        except RuntimeError:pass
    _filters.clear()
def _mel_drop(value):interactive(value);return 1
class FileDropActionTool(BaseMayaTool):
    tool_id='perform_file_drop_action';tool_name='文件拖拽导入/打开/引用';category='pipeline_io';version='1.0.0'
    description='Explicit Import/Open/Reference/Cancel file action, optional owned model-panel drop filters; never replaces Maya built-in MEL'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','choose','import','open','reference','enable_drop','disable_drop'],'default':'inspect'},'path':{'type':'string'},'namespace':{'type':'string'},'confirm_discard':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            if type(kw.get('confirm_discard',False)) is not bool:raise ValueError('Strict discard boolean')
            if action in ('choose','import','open','reference'):
                p=source(kw.get('path'))
                if action in ('import','reference'):
                    from maya import cmds
                    ns=namespace(kw.get('namespace'),p)
                    if cmds.namespace(exists=ns):raise ValueError('Existing namespace preserved')
                if action=='open':
                    from maya import cmds
                    if cmds.file(q=True,modified=True) and not kw.get('confirm_discard'):raise ValueError('Modified scene requires explicit discard confirmation or save first')
            return ToolResult.ok(message='无拖拽hook/MEL覆写/文件写/scene修改的预检')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'active_filters':len(_filters),'original_global_proc_replaced':False,'formats':['ma','mb'],'gui_acceptance':'not_run'})
        if action=='enable_drop':return ToolResult.ok(data={'filters':install()})
        if action=='disable_drop':close();return ToolResult.ok()
        if action=='choose':return ToolResult.ok(data=interactive(kw['path']))
        return ToolResult.ok(data={'result':perform(kw['path'],action,kw.get('namespace'),kw.get('confirm_discard',False)),'undo_guaranteed':False,'impact':'Maya file import/reference/open are not reliably undoable; use a backup scene'})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        paths=cmds.fileDialog2(fileMode=1,fileFilter='Maya (*.ma *.mb)',caption='选择导入、打开或引用的文件')
        return interactive(paths[0],parent) if paths else None
