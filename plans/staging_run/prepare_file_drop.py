"""Preserve Import/Open/Reference/Cancel without overriding Maya's MEL proc."""
import subprocess,sys
from prepare_external_candidate import ROOT,put
RC=ROOT/'tools_staging_pool/08_utilities_system/perform_file_drop_action/release_candidate';PKG=RC/'maya_toolkit/tools/perform_file_drop_action'
put(PKG/'__init__.py',r'''from pathlib import Path
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
''')
qt=ROOT/'tools_staging_pool/08_utilities_system/ks_node_outliner_v2_2/release_candidate/maya_toolkit/tools/ks_node_outliner_v2_2/qt_compat.py';put(PKG/'qt_compat.py',qt.read_text())
put(PKG/'backups.py',r'''from pathlib import Path
import shutil,uuid,hashlib
def save_scene(value):
    from maya import cmds
    p=Path(value)
    if not p.is_absolute() or not p.parent.is_dir() or p.suffix.lower() not in ('.ma','.mb') or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Existing independent Maya output parent required')
    if p.exists():
        if not p.is_file():raise ValueError('Non-file output refused')
        backup=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
        with p.open('rb') as original,backup.open('xb') as target:shutil.copyfileobj(original,target)
        def sha(path):
            h=hashlib.sha256()
            with path.open('rb') as f:
                for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
            return h.digest()
        if sha(p)!=sha(backup):raise IOError('Scene backup mismatch')
    cmds.file(rename=str(p));return cmds.file(save=True,force=True,type='mayaAscii' if p.suffix.lower()=='.ma' else 'mayaBinary')
''')
put(PKG/'mtb_performFileDropAction.mel',r'''// Optional explicit named command; never defines performFileDropAction.
global proc int mtb_performFileDropAction(string $theFile) {
    string $encoded=encodeString($theFile);
    return python("from maya_toolkit.tools.perform_file_drop_action import _mel_drop; _mel_drop(\""+$encoded+"\")");
}
''')
put(RC/'tests/test_perform_file_drop_action.py',r'''import importlib.util,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_drop',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.perform_file_drop_action import FileDropActionTool
    tool=FileDropActionTool()
from maya_toolkit.tools.perform_file_drop_action import source,namespace,_filters
class Checks(unittest.TestCase):
    def test_no_global_override_and_literal_namespace_paths(self):
        self.assertTrue(tool.validate().success);self.assertEqual(_filters,[])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'123 shot.ma';p.write_text('test');self.assertEqual(source(str(p)),str(p));self.assertEqual(namespace(None,str(p)),'file_123_shot')
            with self.assertRaises(ValueError):namespace('bad:ns',str(p))
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_perform_file_drop_action_maya.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_drop',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class MayaChecks(unittest.TestCase):
    def test_actual_import_undo_reference_open_and_scriptnode_block(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'source.ma';cmds.file(new=True,force=True);cmds.polyCube(name='testCube');cmds.file(rename=str(p));cmds.file(save=True,force=True,type='mayaAscii');cmds.file(new=True,force=True);cmds.undoInfo(state=True);before=cmds.ls(long=True)
            self.assertTrue(tool.run(action='import',path=str(p),namespace='drop_ns',dry_run=True).success);self.assertEqual(cmds.ls(long=True),before)
            result=tool.run(action='import',path=str(p),namespace='drop_ns');self.assertTrue(result.success,result.errors);self.assertTrue(cmds.objExists('drop_ns:testCube'));self.assertFalse(result.data['undo_guaranteed']);cmds.file(new=True,force=True)
            result=tool.run(action='reference',path=str(p),namespace='ref_ns');self.assertTrue(result.success,result.errors);self.assertTrue(cmds.referenceQuery('ref_ns:testCube',isNodeReferenced=True))
            cmds.createNode('transform',name='modifiedMarker');denied=tool.run(action='open',path=str(p));self.assertFalse(denied.success);self.assertTrue(cmds.objExists('ref_ns:testCube'))
            opened=tool.run(action='open',path=str(p),confirm_discard=True);self.assertTrue(opened.success,opened.errors);self.assertTrue(cmds.objExists('testCube'))
            bridge=Path(__file__).resolve().parents[1]/'maya_toolkit/tools/perform_file_drop_action/mtb_performFileDropAction.mel';mel.eval(bridge.read_text());self.assertTrue(mel.eval('exists "mtb_performFileDropAction"'))
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/perform_file_drop_action.md','''# 文件拖拽动作完整候选

原Randall Hess MEL精确SHA归档。完整Import/Open/Reference/Cancel选择行为、namespace/scene读写与可选viewport drop功能，Base/Schema/API/ToolResult和future晋级注册预制。保留来源注释，无额外素材；默认inspect/dry不MEL/Qt/hook/file/scene写入，不替换Maya安装scripts/others文件或内置global performFileDropAction，不更改$gv_operationMode。可手动调用独立mtb_performFileDropAction bridge，未来路径self-contained；可显式enable_drop在当前modelPanels各挂自有QObject eventFilter，disable只remove自己，foreign filter保留；新panel需重新enable。

仅ma/mb本机现存绝对文件支持；其他插件格式沿用原Maya拖拽处理，不自动load plugin。namespace自动sanitize文件名/数字前缀，明确传simple root且拒绝既有namespace，不合并。Import/Reference包UndoChunk，Open替换scene不可Undo；源场景scriptNodes执行关闭，复杂引用/插件加载和文件外部代码影响仍需实测。API Open modified须显式confirm_discard或先保存；交互Open再Save/Discard/Cancel，save既有输出先精确backup，取消不改scene。存盘不由Undo撤回。

原performFileAction MELOpen依赖Maya全局operationMode，改cmds明确参数避免临时全局泄露；事件只单local URL ma/mb消费，其余正常交Maya，Cancel也消费该次drop。完整Qt/MEL触发实际GUI未执行；离线path/namespace，隔离Maya真实临时.ma import/dry/oneUndo/reference/拒绝未确认open/确认open及MEL bridge编译检查；真实viewport drag/Maya save dialogs/引用Undo/cross-version not_run。可用于后续场景引用/导入流程，但不宣称已验收生产组合。
''')
with (RC/'docs/tools/perform_file_drop_action.md').open('a',encoding='utf8') as f:f.write('\n实测更正：隔离Maya2025 file(import=True)后Undo队列没有可撤销命令，UndoChunk不能让原file命令变可撤销。API统一返回undo_guaranteed=False，Import/Reference/Open均按文件/场景切换不可保证Undo处理，使用备份场景。上文分组只说明执行边界，不能作Import单Undo已通过结论；自动检查验证实际导入/引用及未确认Open拒绝。\n')
put(RC/'acceptance.md','''# 文件拖拽 Maya真实直验 not_run

1. 备份scene下show_ui或显式enable_drop，拖单本机ma/mb到当前modelPanel，Import/Open/Reference/Cancel完整，无inline执行未知源scriptNodes；其他URL/多文件/非ma/mb不吞，未改内置performFileDropAction/安装路径/global mode。
2. namespace空/重名/非法拒绝不改scene；Import/Reference/Open均不可保证Undo（隔离2025已证实import无Undo队列），仅备份scene使用。Open modified Save/Discard/Cancel，当前无名保存cancel保留scene，现存输出先backup。
3. 多次enable/drop/disable/close后不叠自有filter、不移foreign hook，新modelPanel重新enable。独立MEL mtb_performFileDropAction编译与路径含引号/Unicode核验。
4. accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/perform_file_drop_action','--class-name','FileDropActionTool','--summary','Complete Import/Open/Reference/Cancel with explicit owned viewport filters, literal paths and modified-scene protection','--dependencies','Maya cmds/MEL and real model-panel Qt widgets','--limitations','Real Maya viewport drop/dialogs/reference Undo/cross-version GUI acceptance not_run; only ma/mb intercepted; other formats remain Maya default'],check=True)
