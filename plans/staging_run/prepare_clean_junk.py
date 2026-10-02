from prepare_external_candidate import ROOT, put
import subprocess, sys
RC = ROOT / 'tools_staging_pool/06_diagnostics_security/clean_junk_nodes/release_candidate'
PKG = RC / 'maya_toolkit/tools/clean_junk_nodes'
put(PKG / '__init__.py', r'''"""Unknown nodes/plugins and explicit viewport callbacks; no PyMel dependency."""
from pathlib import Path
import json
from maya_toolkit.framework import BaseMayaTool, ToolResult

def _cmds():
    from maya import cmds
    return cmds

def normalize(values):
    allowed={'action','include_unknown_dag','remove_unknown_plugins','confirm_plugin_metadata_loss','unlock_nodes','callback_policy','confirm_all_callbacks'}
    if set(values)-allowed: raise ValueError('Unknown parameters')
    p=dict(action='inspect',include_unknown_dag=False,remove_unknown_plugins=False,confirm_plugin_metadata_loss=False,unlock_nodes=False,callback_policy='known',confirm_all_callbacks=False)
    p.update(values)
    if p['action'] not in ('inspect','clean') or p['callback_policy'] not in ('none','known','all'): raise ValueError('Invalid action/callback_policy')
    for key in allowed-{'action','callback_policy'}:
        if not isinstance(p[key],bool): raise ValueError('Boolean required: '+key)
    if p['callback_policy']=='all' and not p['confirm_all_callbacks']: raise ValueError('All ModelEditor callbacks requires confirm_all_callbacks=True')
    if p['remove_unknown_plugins'] and not p['confirm_plugin_metadata_loss']: raise ValueError('Unknown plugin removal is not reliably Undoable; back up scene and pass confirm_plugin_metadata_loss=True')
    return p

def plan(p):
    cmds=_cmds(); types=['unknown']+(['unknownDag','unknownTransform'] if p['include_unknown_dag'] else [])
    nodes=sorted(set(n for typ in types for n in (cmds.ls(type=typ,long=True) or [])))
    rows=[]
    for node in nodes:
        referenced=cmds.referenceQuery(node,isNodeReferenced=True)
        locked=bool(cmds.lockNode(node,query=True,lock=True)[0])
        default=bool(cmds.ls(node,defaultNodes=True))
        descendants=cmds.listRelatives(node,allDescendents=True,fullPath=True) or []
        row={'node':node,'uuid':cmds.ls(node,uuid=True)[0],'type':cmds.nodeType(node),'locked':locked,'referenced':referenced,'descendants':descendants}
        try: row['original_plugin']=cmds.unknownNode(node,query=True,plugin=True)
        except Exception: row['original_plugin']=None
        rows.append(row)
        if p['action']=='clean':
            if referenced or default: raise ValueError('Referenced/default unknown node refused: '+node)
            if locked and not p['unlock_nodes']: raise ValueError('Locked unknown node requires explicit unlock_nodes=True: '+node)
            if descendants: raise ValueError('Unknown DAG with descendants refused; isolate intended scope: '+node)
            from maya.api import OpenMaya as om
            selection=om.MSelectionList(); selection.add(node); obj=selection.getDependNode(0)
            if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))>1: raise ValueError('Instanced unknown DAG refused')
    plugins=[]
    for name in sorted(cmds.unknownPlugin(query=True,list=True) or []):
        plugins.append({'name':name,'version':cmds.unknownPlugin(name,query=True,version=True),
                        'node_types':cmds.unknownPlugin(name,query=True,nodeTypes=True) or [],'data_types':cmds.unknownPlugin(name,query=True,dataTypes=True) or []})
    callbacks=[]
    if p['callback_policy']!='none' and not cmds.about(batch=True):
        for editor in sorted(set(cmds.lsUI(editors=True) or [])):
            if not cmds.modelEditor(editor,exists=True): continue
            callback=cmds.modelEditor(editor,query=True,editorChanged=True) or ''
            if callback and (p['callback_policy']=='all' or callback=='CgAbBlastPanelOptChangeCallback'):
                callbacks.append({'editor':editor,'callback':callback})
    if p['action']=='clean' and not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Undo before cleanup')
    return {'nodes':rows,'unknown_plugins':plugins,'callbacks':callbacks,'options':p,
        'impact':'Unknown is missing-plugin metadata, not proof of junk/virus. Delete listed local nodes/connections with lifetime Undo; plugin removal NOT reliably Undoable; callbacks restore through owned command. No external files saved.'}

def cleanup(p):
    cmds=_cmds(); data=plan(p)
    path=Path(__file__).with_name('delete_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbCleanJunkNodes' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path: raise ValueError('Another candidate owns cleanup command; restart Maya')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    value=cmds.mtbCleanJunkNodes(json.dumps(p)); data=json.loads(value[0] if isinstance(value,list) else value)
    data['removed_plugins']=[]; data['plugin_errors']=[]
    if p['remove_unknown_plugins']:
        for row in data['unknown_plugins']:
            try: cmds.unknownPlugin(row['name'],remove=True); data['removed_plugins'].append(row['name'])
            except Exception as error: data['plugin_errors'].append({'plugin':row['name'],'error':str(error)})
    return data

class CleanJunkNodesTool(BaseMayaTool):
    tool_id='clean_junk_nodes'; tool_name='HM 未知节点、插件与回调清理'; category='scene_hygiene'
    description='完整未知节点/插件/ModelEditor回调清理；预检不修改，未知不等于垃圾'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','clean'],'default':'inspect'},
        'include_unknown_dag':{'type':'boolean','default':False},'remove_unknown_plugins':{'type':'boolean','default':False},
        'confirm_plugin_metadata_loss':{'type':'boolean','default':False},
        'unlock_nodes':{'type':'boolean','default':False},'callback_policy':{'type':'string','enum':['none','known','all'],'default':'known'},
        'confirm_all_callbacks':{'type':'boolean','default':False}}}
    def validate(self,**kwargs):
        try: return ToolResult.ok(message='清理范围预检完成',data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        p=normalize(kwargs); data=cleanup(p) if p['action']=='clean' else plan(p)
        if data.get('plugin_errors'): return ToolResult.fail(message='节点已清理，部分插件仍被使用；可Undo',data=data,errors=[r['error'] for r in data['plugin_errors']])
        return ToolResult.ok(message='未知数据'+('清理' if p['action']=='clean' else '查询')+'完成',data=data)
    def show_ui(self):
        from .ui import show_ui
        return show_ui()
''')
put(PKG / 'delete_command.py', r'''"""Own lifetime deletion and explicit callback restoration as one undoable command."""
import json
from maya import cmds
from maya.api import OpenMaya as om
def maya_useNewAPI(): pass
class Cleanup(om.MPxCommand):
    def __init__(self): super().__init__(); self.modifier=om.MDagModifier(); self.rows=[]; self.callbacks=[]; self.selection=[]; self.data={}
    @staticmethod
    def creator(): return Cleanup()
    def doIt(self,args):
        from maya_toolkit.tools.clean_junk_nodes import normalize,plan
        self.data=plan(normalize(json.loads(args.asString(0)))); self.rows=self.data['nodes']; self.callbacks=self.data['callbacks']
        self.selection=cmds.ls(selection=True,long=True) or []
        for row in self.rows:
            names=cmds.ls(row['uuid'],long=True) or []
            if len(names)!=1: raise RuntimeError('Node identity changed')
            selection=om.MSelectionList(); selection.add(names[0]); obj=selection.getDependNode(0)
            if row['locked']: om.MFnDependencyNode(obj).isLocked=False
            self.modifier.deleteNode(obj,False)
        self.redoIt(); self.setResult(json.dumps(self.data))
    def isUndoable(self): return True
    def _guard(self,callback):
        enabled=cmds.undoInfo(query=True,state=True); cmds.undoInfo(stateWithoutFlush=False)
        try: callback()
        finally: cmds.undoInfo(stateWithoutFlush=enabled)
    def redoIt(self):
        def remove():
            unlocked=[]; cleared=[]
            try:
                for row in self.rows:
                    node=(cmds.ls(row['uuid'],long=True) or [None])[0]
                    if node is None: raise RuntimeError('Unknown node no longer exists')
                    if row['locked']: cmds.lockNode(node,lock=False); unlocked.append(row)
                for row in self.callbacks:
                    if cmds.modelEditor(row['editor'],exists=True):
                        if cmds.modelEditor(row['editor'],query=True,editorChanged=True)!=row['callback']: raise RuntimeError('ModelEditor callback changed; redo refused')
                        cmds.modelEditor(row['editor'],edit=True,editorChanged=''); cleared.append(row)
                self.modifier.doIt()
            except Exception:
                for row in cleared: cmds.modelEditor(row['editor'],edit=True,editorChanged=row['callback'])
                for row in unlocked:
                    names=cmds.ls(row['uuid'],long=True) or []
                    if names: cmds.lockNode(names[0],lock=True)
                raise
        self._guard(remove)
    def undoIt(self):
        def restore():
            self.modifier.undoIt()
            for row in self.rows:
                if row['locked']: cmds.lockNode((cmds.ls(row['uuid'],long=True) or [None])[0],lock=True)
            for row in self.callbacks:
                if cmds.modelEditor(row['editor'],exists=True): cmds.modelEditor(row['editor'],edit=True,editorChanged=row['callback'])
            valid=[n for n in self.selection if cmds.objExists(n)]
            cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        self._guard(restore)
def initializePlugin(obj): om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbCleanJunkNodes',Cleanup.creator)
def uninitializePlugin(obj): om.MFnPlugin(obj).deregisterCommand('mtbCleanJunkNodes')
''')
put(PKG / 'ui.py', r'''"""Original HM one-button workflow plus explicit scopes and full preflight display."""
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
''')
put(RC / 'tests/test_clean_junk_nodes.py', r'''from pathlib import Path
import importlib.util
import sys
import types
import unittest
from unittest.mock import patch
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py'); launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch)
    instance=launch.load_tool()
else:
    sys.path.insert(0,str(rc))
    from maya_toolkit.tools.clean_junk_nodes import CleanJunkNodesTool
    instance=CleanJunkNodesTool()
module=sys.modules[instance.__class__.__module__]
class Tests(unittest.TestCase):
    def test_full_readonly_inventory_without_literal_list_bug(self):
        fake=types.SimpleNamespace(ls=lambda *a,**kw: ['node'] if kw.get('type')=='unknown' else ['uuid'] if kw.get('uuid') else [],
            referenceQuery=lambda *a,**kw:False,lockNode=lambda *a,**kw:[False],listRelatives=lambda *a,**kw:[],nodeType=lambda n:'unknown',unknownNode=lambda *a,**kw:'missingPlugin',
            unknownPlugin=lambda *a,**kw:[],about=lambda **kw:True)
        with patch.object(module,'_cmds',return_value=fake):
            result=instance.validate();self.assertTrue(result.success,result);self.assertEqual(result.data['nodes'][0]['node'],'node')
    def test_flags_must_be_explicit(self):
        with self.assertRaises(ValueError):module.normalize({'callback_policy':'all'})
        with self.assertRaises(ValueError):module.normalize({'unlock_nodes':'yes'})
        self.assertFalse(module.normalize({})['remove_unknown_plugins'])
if __name__=='__main__':unittest.main()
''')
put(RC / 'tests/test_clean_junk_nodes_maya.py', r'''from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class Tests(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_unknown_lifetime_connection_lock_and_one_undo_redo(self):
        node=cmds.createNode('unknown',name='missingData');cmds.addAttr(node,longName='amount',attributeType='double');cmds.setAttr(node+'.amount',4)
        cube=cmds.polyCube()[0];cmds.connectAttr(node+'.amount',cube+'.tx');uuid=cmds.ls(node,uuid=True)[0];cmds.lockNode(node,lock=True);cmds.select(node)
        before=(cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True))
        preview=tool.run(dry_run=True,action='clean',unlock_nodes=True,callback_policy='none');self.assertTrue(preview.success,preview)
        self.assertEqual((cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True)),before)
        result=tool.run(action='clean',unlock_nodes=True,callback_policy='none');self.assertTrue(result.success,result);self.assertFalse(cmds.objExists(node))
        cmds.undo();self.assertEqual(cmds.ls(node,uuid=True),[uuid]);self.assertTrue(cmds.lockNode(node,q=True,lock=True)[0]);self.assertTrue(cmds.isConnected(node+'.amount',cube+'.tx'));self.assertEqual(cmds.getAttr(node+'.amount'),4)
        cmds.redo();self.assertFalse(cmds.objExists(node));self.assertTrue(cmds.objExists(cube))
    def test_locked_last_refused_before_any_delete(self):
        first=cmds.createNode('unknown',name='aUnknown');last=cmds.createNode('unknown',name='zUnknown');cmds.lockNode(last,lock=True)
        result=tool.run(action='clean',callback_policy='none');self.assertFalse(result.success);self.assertTrue(cmds.objExists(first));self.assertTrue(cmds.objExists(last))
    def test_actual_unknown_plugin_metadata_irreversible_guard(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'unknown.ma';path.write_text('//Maya ASCII 2025 scene\nrequires maya "2025";\nrequires "mtbMissingPluginFixture" "1.0";\ncurrentUnit -l centimeter -a degree -t film;\n',encoding='utf-8')
            cmds.file(str(path),open=True,force=True,executeScriptNodes=False)
            self.assertIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            refused=tool.run(action='clean',remove_unknown_plugins=True,callback_policy='none');self.assertFalse(refused.success)
            self.assertIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            result=tool.run(action='clean',remove_unknown_plugins=True,confirm_plugin_metadata_loss=True,callback_policy='none');self.assertTrue(result.success,result)
            self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            cmds.undo();self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            cmds.redo();self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
if __name__=='__main__':unittest.main()
''')
put(RC / 'docs/tools/clean_junk_nodes.md', '''# HM 未知节点、插件与视口回调清理候选

完整三功能（unknown nodes/unknownPlugin requires/ModelEditor editorChanged）与原一键按钮保留；原PyMel文件SHA归档，候选cmds/API2免PyMel，取消import即开窗。修复原检查字面量ls_unknownNodes导致不删除，以及未导入cmds；不把缺失插件生产数据称为确定垃圾/病毒。

Base/ToolResult/Schema/category scene_hygiene。inspect默认仅全表查询nodes UUID/锁/引用/descendants/original plugin、未知插件version/node/data types、受影响editor回调。clean删除局部unknown节点，include_unknown_dag=False保原unknown范围，可显式包含另外两类；locked默认拒绝，unlock_nodes=True才解锁；引用/default/含descendants/真实instance拒绝。requires列表默认只显示，remove_unknown_plugins=True+confirm_plugin_metadata_loss=True且先保存备份场景才删除（本机observed metadata不可Undo）；原一键默认改为显式范围以免误删元数据。callback_policy known默认仅CgAbBlastPanelOptChangeCallback，none不碰UI，all+confirm_all_callbacks=True保原清全ModelEditor功能且明确范围（包括用户正确回调）；batch不操作视口。所有kwargs与bool严格校验。

MDagModifier必须解锁后排队，includeParents=False保父对象，专用MPx命令生命周期、属性/连接/UUID/锁UndoRedo；callback原字串以自有command恢复/redo，关闭editor跳过，不重建UI；插件虽文档称undoable，本机fixture真实Undo不能恢复，明确元数据永久移除，需要已有备份scene恢复，外层UndoChunk也不提供metadata恢复。plugin仍被用native可能拒绝，返回fail/plugin_errors+此前nodes/plugin状态，不吞异常，不自动清数据；只有节点/回调可Undo。文件不保存、不删，依赖真实MayaUndo启用。known callback内容含其他空格/脚本不盲删，需要all明确操作；不通过eval执行未知回调。

```python
from maya_toolkit.tools.clean_junk_nodes import CleanJunkNodesTool
t=CleanJunkNodesTool()
t.run(dry_run=True,action='clean',unlock_nodes=True)
t.run(action='clean',unlock_nodes=True)
```

UI完整原一键按钮，补各范围checkbox/预检完整JSON/现场确认；用户真实Maya备份后操作，默认inspect也不打开UI。2mock/3隔离Maya2025（DG未知节点连接/锁/oneUndoRedo、后行locked全表拒绝、真实MA requires metadata显式确认与永久移除guard）与临时最终注册/domain/panel通过仅离线证据；真实GUI/引用/unknownDag/插件自定义payload/全部callback Undo待验。无需core改动，共用现有框架Undo/协议，仅持有自有command。

候选自包含upstream/cat/docs/tests/晋级注册信息；正式库未改。参考：[unknownPlugin](https://help.autodesk.com/cloudhelp/2025/ENU/Maya-Tech-Docs/CommandsPython/unknownPlugin.html)。Maya验收后需当前SHA版本操作者日期才能晋级；与文件清理器是不同范围，场景unknown清理不等于杀毒。
''')
put(RC / 'acceptance.md', '''# Maya直验 not_run

仅备份scene/临时refs/plugin fixture中操作。import无窗口，show_ui有原一键按钮与完整范围checkbox/预检/确认；unknown局部节点、locked节点、default/引用/含孩子Dag/instance全表拒绝；explicit unlock删除后oneUndo恢复UUID属性连接与锁、Redo同节点删除且父存留。unknownPlugin保留default、explicit移除需unused+confirm_plugin_metadata_loss、被node/data占用native失败如实报、元数据不能依赖Undo，需用户已有备份scene恢复。真实modelEditor保留自定义callback，known仅指定异常串，all显式确认全清并oneUndo/Redo恢复，editor已关不重建、不执行callback内容。UI关闭/reopen无pref破坏。验证当前scene时间AutoKey/选区和文件不被保存；未知不等于垃圾，生产缺失插件先安装/恢复。mayapy不算真实GUI验收；通过后记录版本/currentSHA/accepted_by/date再晋级。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','06_diagnostics_security/clean_junk_nodes','--class-name','CleanJunkNodesTool','--summary','Complete HM unknown node/plugin/callback cleanup with explicit scope, lifetime Undo and no PyMel','--limitations','Real Maya GUI/modelEditor callbacks, unknown DAG/reference/custom data and cross versions not_run'],check=True)
