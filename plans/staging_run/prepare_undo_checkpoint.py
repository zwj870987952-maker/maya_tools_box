"""Complete undo bookmark API/marker/UI/standalone shortcuts and shelf candidate."""
import ast
from prepare_external_candidate import ROOT,put
import subprocess,sys
UNIT=ROOT/'tools_staging_pool/06_diagnostics_security/undo_checkpoint'
RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/undo_checkpoint'
put(PKG/'manager.py',r'''"""Named native Undo marker chunks and read-only queue presence checks."""
from pathlib import Path
import json
import re
import time
import uuid

PREFIX='mtbCheckpoint_'
COMMAND='mtbUndoCheckpointMarker'
items=[]
applied={}
last_undone=None

def _cmds():
    from maya import cmds
    return cmds

def parse_queue(messages):
    rows=[]
    for message in messages:
        for line in message.splitlines():
            match=re.fullmatch(r'\s*(\d+):\s*(.*?)\s*',line)
            if match:rows.append({'index':int(match.group(1)),'name':match.group(2)})
    if rows and [r['index'] for r in rows]!=list(range(len(rows))):raise RuntimeError('Unrecognized native Undo queue order; no rollback performed')
    return rows

def queue_snapshot():
    cmds=_cmds()
    if cmds.undoInfo(query=True,undoQueueEmpty=True):return []
    from maya.api import OpenMaya as om
    messages=[]
    def capture(message,kind,data):
        if re.match(r'^\s*\d+:',message):messages.append(message)
    # Maya 2025's Boolean-returning filter callback crashed during CPython teardown.
    # Plain output callbacks return None and leave console display untouched.
    handle=om.MCommandMessage.addCommandOutputCallback(capture)
    try:cmds.undoInfo(query=True,printQueue=True)
    finally:om.MMessage.removeCallback(handle)
    rows=parse_queue(messages)
    if not rows:raise RuntimeError('Unable to read native Undo queue; refusing speculative Undo')
    if len(rows)>100000:raise ValueError('Undo queue exceeds 100000 entries')
    return rows

class CheckpointItem:
    def __init__(self,identifier,name):
        self.id,self.name=identifier,name;self.time_str=time.strftime('%H:%M:%S')
    @property
    def status(self):return '有效 (Active)' if applied.get(self.id) else '已回退/失效 (Undone)'
    def to_dict(self):return {'id':self.id,'name':self.name,'time':self.time_str,'status':self.status}

def register_command():
    cmds=_cmds();path=Path(__file__).with_name('marker_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if COMMAND in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path:raise RuntimeError('Another candidate owns marker command; restart Maya')
            return
    cmds.loadPlugin(str(path),quiet=True)

def available():
    queue=queue_snapshot();names={r['name'] for r in queue}
    return [item for item in items if applied.get(item.id) and PREFIX+item.id in names]

def restore_plan(target_id=None,max_steps=5000):
    cmds=_cmds()
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
    if not isinstance(max_steps,int) or isinstance(max_steps,bool) or not 1<=max_steps<=100000:raise ValueError('max_steps must be 1..100000')
    if target_id:
        target=next((item for item in items if item.id==target_id),None)
    else:
        candidates=available();target=candidates[-1] if candidates else None
    if target is None or not applied.get(target.id):raise ValueError('No active checkpoint with this ID')
    queue=queue_snapshot();matches=[i for i,row in enumerate(queue) if row['name']==PREFIX+target.id]
    if len(matches)!=1:raise ValueError('Checkpoint marker is absent/ambiguous in Undo queue; no Undo performed')
    steps=len(queue)-matches[0]
    if steps>max_steps:raise ValueError('Target requires '+str(steps)+' Undo steps, exceeding max_steps; no partial rollback')
    return {'checkpoint':target.to_dict(),'steps':steps,'queue':queue,'impact':'Undo all later operations, including the marker; file IO/non-undoable operations are not reverted'}

class Manager:
    @property
    def checkpoints(self):return items
    def create_checkpoint(self,name=None,overwrite=False):
        cmds=_cmds()
        if not cmds.undoInfo(query=True,state=True):cmds.warning('Enable Maya Undo before creating checkpoint');return None
        if not isinstance(overwrite,bool):raise ValueError('overwrite must be boolean')
        if name is not None and (not isinstance(name,str) or len(name)>256):raise ValueError('name must be a string <=256 characters')
        register_command();identifier='cp_'+uuid.uuid4().hex;item=CheckpointItem(identifier,(name or '').strip() or ('唯一记录点' if overwrite else '记录点_'+time.strftime('%H%M%S')))
        if overwrite:self.clear()
        items.append(item);applied[identifier]=True
        cmds.undoInfo(openChunk=True,chunkName=PREFIX+identifier)
        try:getattr(cmds,COMMAND)(json.dumps({'id':identifier,'name':item.name}))
        except Exception:items.remove(item);applied.pop(identifier,None);raise
        finally:cmds.undoInfo(closeChunk=True)
        if not any(row['name']==PREFIX+identifier for row in queue_snapshot()):
            applied[identifier]=False
            raise RuntimeError('Checkpoint nested in another open chunk; marker not independently visible. Call outside an existing Undo chunk')
        return item
    def get_latest_active_checkpoint(self):
        found=available();return found[-1] if found else None
    def restore_to_checkpoint(self,target_id=None,max_steps=5000):
        global last_undone
        cmds=_cmds()
        try:plan=restore_plan(target_id,max_steps)
        except Exception as error:return False,0,str(error)
        # The full ordered queue is checked immediately before each Undo.
        expected=plan['queue'];last_undone=None;count=0
        suspended=bool(cmds.refresh(query=True,suspend=True)) if not cmds.about(batch=True) else False
        if not cmds.about(batch=True):cmds.refresh(suspend=True)
        try:
            while expected:
                current=queue_snapshot()
                if current!=expected:return False,count,'Undo queue changed unexpectedly; stopped before next step'
                cmds.undo();count+=1;expected=expected[:-1]
                if last_undone==plan['checkpoint']['id']:return True,count,'成功回退 '+str(count)+' 步到 '+plan['checkpoint']['name']
                if count>=plan['steps']:return False,count,'Marker command was not reached as predicted; stopped'
        except Exception as error:return False,count,'Undo failed after '+str(count)+' steps: '+str(error)
        finally:
            if not cmds.about(batch=True):cmds.refresh(suspend=suspended)
        return False,count,'Target not reached'
    def clear(self):
        global last_undone
        items.clear();applied.clear();last_undone=None
    def get_checkpoint_name(self,identifier):
        return next((item.name for item in items if item.id==identifier),identifier)
manager=Manager()
''')
put(PKG/'marker_command.py',r'''"""Static no-scene-mutation Undo marker; no generated temp plugin or MEL interpolation."""
import json
from maya.api import OpenMaya as om
def maya_useNewAPI():pass
class Marker(om.MPxCommand):
    def __init__(self):super().__init__();self.identifier=''
    @staticmethod
    def creator():return Marker()
    def doIt(self,args):
        data=json.loads(args.asString(0));self.identifier=data['id'];self.redoIt()
    def isUndoable(self):return True
    def redoIt(self):
        from maya_toolkit.tools.undo_checkpoint import manager as state
        if any(item.id==self.identifier for item in state.items):state.applied[self.identifier]=True
    def undoIt(self):
        from maya_toolkit.tools.undo_checkpoint import manager as state
        if any(item.id==self.identifier for item in state.items):state.applied[self.identifier]=False
        state.last_undone=self.identifier
def initializePlugin(obj):om.MFnPlugin(obj,'Maya Tools Box candidate','1.0','Any').registerCommand('mtbUndoCheckpointMarker',Marker.creator)
def uninitializePlugin(obj):om.MFnPlugin(obj).deregisterCommand('mtbUndoCheckpointMarker')
''')
put(PKG/'__init__.py',r'''"""Full Maya Undo checkpoints. Queue operations intentionally bypass outer UndoChunk."""
import time
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import manager

class UndoCheckpointTool(BaseMayaTool):
    tool_id='undo_checkpoint';tool_name='Maya 多记录点与Undo恢复';category='scene_hygiene'
    description='唯一/多记录点、只读队列预检、批量Undo、原面板/独立快捷/Shelf；不恢复文件IO'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','create','restore','clear','show_ui','install_shelf'],'default':'inspect'},
        'name':{'type':'string','maxLength':256},'overwrite':{'type':'boolean','default':False},'target_id':{'type':'string'},
        'max_steps':{'type':'integer','minimum':1,'maximum':100000,'default':5000},'shelf_name':{'type':'string'}}}
    def plan(self,**kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameters')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Invalid action')
        if not isinstance(kwargs.get('overwrite',False),bool):raise ValueError('overwrite must be bool')
        if kwargs.get('name') is not None and (not isinstance(kwargs['name'],str) or len(kwargs['name'])>256):raise ValueError('name must be <=256 characters')
        cmds=manager._cmds()
        if action in ('create','restore') and not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo')
        if action=='restore':return {'action':action,**manager.restore_plan(kwargs.get('target_id'),kwargs.get('max_steps',5000))}
        if action in ('show_ui','install_shelf'):
            if cmds.about(batch=True):raise ValueError('Interactive Maya required')
            if action=='install_shelf':
                from .shelf import shelf_plan
                return {'action':action,**shelf_plan(kwargs.get('shelf_name'))}
        queue=manager.queue_snapshot();names={row['name'] for row in queue}
        return {'action':action,'checkpoints':[dict(item.to_dict(),in_undo_queue=manager.PREFIX+item.id in names) for item in manager.items],
                'undo_queue_entries':len(queue),'impact':'Session-only marker metadata; restore undoes later scene actions. Never restores external writes or non-undoable commands.'}
    def validate(self,**kwargs):
        try:return ToolResult.ok(message='记录点预检通过，未注册marker/未改Undo队列/未开窗',data=self.plan(**kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        plan=self.plan(**kwargs);action=plan['action']
        if action=='create':
            item=manager.manager.create_checkpoint(kwargs.get('name'),kwargs.get('overwrite',False))
            if item is None:return ToolResult.fail(message='未创建记录点')
            return ToolResult.ok(message='已创建Undo标记',data=item.to_dict())
        if action=='restore':
            ok,count,message=manager.manager.restore_to_checkpoint(kwargs.get('target_id'),kwargs.get('max_steps',5000))
            return (ToolResult.ok if ok else ToolResult.fail)(message=message,data={'undid_steps':count,'target_id':plan['checkpoint']['id']})
        if action=='clear':manager.manager.clear()
        elif action=='show_ui':self.show_ui()
        elif action=='install_shelf':
            from .shelf import install_to_shelf
            return ToolResult.ok(message='四个owned Shelf按钮已就绪（不自动保存偏好）',data=install_to_shelf(kwargs.get('shelf_name')))
        return ToolResult.ok(message='记录点'+action+'完成',data=plan)
    def run(self,dry_run=False,**kwargs):
        from maya_toolkit.core.maya_utils import ensure_maya_initialized
        ensure_maya_initialized();start=time.time()
        if not isinstance(dry_run,bool):return ToolResult.fail(message='dry_run must be boolean',tool_id=self.tool_id)
        result=self.validate(**kwargs)
        if result.success and not dry_run:
            try:result=self.execute(**kwargs)
            except Exception as error:result=ToolResult.fail(message=str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=bool(dry_run);result.execution_time=round(time.time()-start,4)
        if not dry_run and kwargs.get('action') in ('create','restore','clear'):
            import sys,html
            ui=sys.modules.get(__name__+'.ui');window=getattr(ui,'_CURRENT_UI_INSTANCE',None) if ui else None
            if window is not None:
                try:window.refresh_table()
                except RuntimeError:pass
            cmds=manager._cmds()
            if not cmds.about(batch=True):
                try:cmds.inViewMessage(amg=html.escape(result.message),pos='topCenter',fade=True,fst=2000)
                except RuntimeError:pass
        return result
    def show_ui(self):
        from .ui import show
        return show()

def create_checkpoint_standalone(name='唯一记录点',overwrite=True):
    return UndoCheckpointTool().run(action='create',name=name,overwrite=overwrite)
def restore_checkpoint_standalone():return UndoCheckpointTool().run(action='restore')
def clear_checkpoint_standalone():return UndoCheckpointTool().run(action='clear')
''')

original=(UNIT/'maya_undo_checkpoint.py').read_text(encoding='utf-8');tree=ast.parse(original);parts=[]
for node in tree.body:
    if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in ('get_maya_main_window','UndoCheckpointUI','show'):
        parts.append('\n'.join(original.splitlines()[node.lineno-1:node.end_lineno]))
ui='\n\n'.join(parts)
ui=ui.replace('    # 注册命令\n    register_checkpoint_command()', '    if cmds.about(batch=True):\n        raise RuntimeError("Interactive Maya required")')
ui=ui.replace('"确认恢复记录点",','"确认恢复记录点",')
put(PKG/'ui.py','''"""Original complete Qt table/name/create/restore/latest/double-click/clear panel."""
from maya import cmds
import maya.OpenMayaUI as omui
try:
    from PySide6 import QtWidgets,QtCore,QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets,QtCore,QtGui
    from shiboken2 import wrapInstance
from .manager import manager as _GLOBAL_MANAGER
_CURRENT_UI_INSTANCE=None
''' + ui)
put(PKG/'shelf.py',r'''"""Four idempotent session Shelf shortcuts, package imports and real newlines."""
BUTTONS=[('panel','CP面板','history.png',"UndoCheckpointTool().show_ui()"),
         ('create','设记录','setKeyframe.png',"UndoCheckpointTool().run(action='create',overwrite=True,name='唯一记录点')"),
         ('restore','回记录','undo.png',"UndoCheckpointTool().run(action='restore')"),
         ('clear','清记录','delete.png',"UndoCheckpointTool().run(action='clear')")]
def command(expression):return 'from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool\n'+expression+'\n'
def shelf_plan(shelf_name=None):
    from maya import cmds,mel
    if cmds.about(batch=True):raise ValueError('Shelf requires interactive Maya')
    shelf=shelf_name or mel.eval('tabLayout -q -st $gShelfTopLevel;')
    if not shelf or not cmds.shelfLayout(shelf,exists=True):raise ValueError('Active Shelf missing')
    return {'shelf':shelf,'buttons':[{'id':identifier,'label':label,'image':image,'command':command(expression)} for identifier,label,image,expression in BUTTONS],
            'impact':'Changes 4 owned session Shelf buttons; preferences not automatically saved; not scene Undo'}
def install_to_shelf(shelf_name=None):
    from maya import cmds
    plan=shelf_plan(shelf_name);children=cmds.shelfLayout(plan['shelf'],query=True,childArray=True) or [];owned={}
    for child in children:
        if cmds.shelfButton(child,exists=True):
            tag=cmds.shelfButton(child,query=True,docTag=True)
            if tag.startswith('maya_toolkit.undo_checkpoint.'):owned[tag.rsplit('.',1)[1]]=child
    for button in plan['buttons']:
        options=dict(label=button['label'],annotation=button['label'],image1=button['image'],command=button['command'],sourceType='python',imageOverlayLabel=button['label'],docTag='maya_toolkit.undo_checkpoint.'+button['id'])
        if button['id'] in owned:cmds.shelfButton(owned[button['id']],edit=True,**options)
        else:cmds.shelfButton(parent=plan['shelf'],**options)
    return plan
''')
for filename,call in [('create_checkpoint.py',"create_checkpoint_standalone()"),('restore_checkpoint.py',"restore_checkpoint_standalone()"),('clear_checkpoints.py',"clear_checkpoint_standalone()")]:
    func=call.split('(')[0]
    put(PKG/filename,"from maya_toolkit.tools.undo_checkpoint import "+func+"\ndef main(): return "+call+"\nif __name__=='__main__': main()")
put(PKG/'install_shelf.py',"from maya_toolkit.tools.undo_checkpoint.shelf import install_to_shelf\nif __name__=='__main__': install_to_shelf()")
put(RC/'tests/test_undo_checkpoint.py',r'''from pathlib import Path
import importlib.util
import sys
import unittest
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    sys.path.insert(0,str(rc));from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool;tool=UndoCheckpointTool()
from maya_toolkit.tools.undo_checkpoint import manager
from maya_toolkit.tools.undo_checkpoint.shelf import BUTTONS,command
class Tests(unittest.TestCase):
    def test_queue_format_has_unnamed_entries_and_order_guard(self):
        rows=manager.parse_queue(['0: ','1: mtbCheckpoint_cp_A','2: ']);self.assertEqual([r['name'] for r in rows],['','mtbCheckpoint_cp_A',''])
        with self.assertRaises(RuntimeError):manager.parse_queue(['0: a','3: b'])
    def test_shelf_commands_real_newlines_compile_without_path_dependency(self):
        for identifier,label,image,expression in BUTTONS:
            value=command(expression);compile(value,'Shelf '+identifier,'exec');self.assertIn('\n',value);self.assertNotIn('sys.path',value)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_undo_checkpoint_maya.py',r'''from pathlib import Path
import importlib.util
import sys
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.undo_checkpoint import manager
class Tests(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True,infinity=True);manager.manager.clear()
    def test_true_marker_restore_two_points_undo_redo_and_name_injection(self):
        cube=cmds.polyCube(name='checkpointCube')[0];cmds.setAttr(cube+'.tx',1)
        old_queue=manager.queue_snapshot();before_nodes=cmds.ls();dry=tool.run(dry_run=True,action='create',name='a"; deleteAll;')
        self.assertTrue(dry.success,dry);self.assertEqual(manager.queue_snapshot(),old_queue);self.assertEqual(cmds.ls(),before_nodes)
        first=tool.run(action='create',name='a"; deleteAll;');self.assertTrue(first.success,first)
        cmds.setAttr(cube+'.tx',2);second=tool.run(action='create',name='second');self.assertTrue(second.success,second);cmds.setAttr(cube+'.tx',3)
        queue=manager.queue_snapshot();preview=tool.run(dry_run=True,action='restore',target_id=first.data['id']);self.assertTrue(preview.success,preview);self.assertEqual(manager.queue_snapshot(),queue);self.assertEqual(cmds.getAttr(cube+'.tx'),3)
        refused=tool.run(action='restore',target_id=first.data['id'],max_steps=1);self.assertFalse(refused.success);self.assertEqual(cmds.getAttr(cube+'.tx'),3);self.assertEqual(manager.queue_snapshot(),queue)
        result=tool.run(action='restore',target_id=second.data['id']);self.assertTrue(result.success,result);self.assertEqual(cmds.getAttr(cube+'.tx'),2)
        cmds.redo();self.assertTrue(manager.applied[second.data['id']]);cmds.redo();self.assertEqual(cmds.getAttr(cube+'.tx'),3)
        result=tool.run(action='restore',target_id=first.data['id']);self.assertTrue(result.success,result);self.assertEqual(cmds.getAttr(cube+'.tx'),1);self.assertTrue(cmds.objExists(cube))
    def test_flushed_queue_or_foreign_id_never_undo_unrelated_actions(self):
        cube=cmds.polyCube()[0];created=tool.run(action='create');self.assertTrue(created.success,created);cmds.flushUndo();cmds.setAttr(cube+'.tx',9);queue=manager.queue_snapshot()
        self.assertFalse(tool.run(action='restore',target_id=created.data['id']).success);self.assertEqual(cmds.getAttr(cube+'.tx'),9);self.assertEqual(manager.queue_snapshot(),queue)
        self.assertFalse(tool.run(action='restore',target_id='foreign').success);self.assertEqual(cmds.getAttr(cube+'.tx'),9)
    def test_clear_overwrite_queue_preserved_and_disabled_undo(self):
        cmds.polyCube();first=tool.run(action='create');second=tool.run(action='create',overwrite=True);self.assertTrue(first.success);self.assertTrue(second.success);self.assertEqual(len(manager.items),1)
        queue=manager.queue_snapshot();self.assertTrue(tool.run(action='clear').success);self.assertEqual(manager.items,[]);self.assertEqual(manager.queue_snapshot(),queue)
        cmds.undoInfo(stateWithoutFlush=False);self.assertFalse(tool.run(action='create').success);self.assertFalse(tool.run(action='restore').success);cmds.undoInfo(stateWithoutFlush=True)
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/undo_checkpoint.md','''# Maya多记录点与Undo恢复候选

完整保留唯一/多点创建、原深色Qt管理面板（名称/时间/状态/双击/选中恢复/最新恢复/清空/视口提示）、三个独立快捷入口、四个Shelf按钮。原6文件逐字节SHA归档，不自动加载UI；UI业务分离，静态自有MPx Marker，不再临时生成覆盖plugin脚本，不再MEL拼接用户名称，中文/引号名称纯JSON参数。

Base/ToolResult/Schema/scene_hygiene，action inspect默认、create/name/overwrite、restore/target_id/max_steps、clear、show_ui、install_shelf/shelf_name。run刻意不包通用UndoChunk：它管理原有Undo队列，restore不得在一个新chunk内Undo，create只给marker自己的唯一chunk名字mtbCheckpoint_cp_UUID，不能被外层通用框架chunk隐藏。显式调用需在其它open UndoChunk之外；嵌套时创建后发现marker不可独立可见会fail并标失效，不擅自关闭调用方chunk。dry-run不注册plugin、不加marker、不改队列、清空元数据或UI。

记录只在当前Maya进程内，不保存到scene文件，不跨重启恢复。create的no-op MPx只插Undo marker，不增加场景节点；overwrite/clear仅元数据不flush Undo、不删除native旧标记。manual Undo把已到marker标为已回退，Redo对应标记恢复Active（如果清空/overwrite旧标记则不复活UI旧记录）。队列被flush/scene切换/历史长度截断后，即使内存还记录ID，restore找不到唯一chunk会0步拒绝，绝不像原代码Undo到空队列。

read-only native printQueue临时MCommandMessage output callback捕获编号/命名chunk，未命名Python命令也计数，finally移除callback；不设置日志抑制偏好，队列输出仍可能出现在Script Editor。初测Boolean-returning filter callback导致本机Python退出bool_dealloc原生崩溃，改用返回None的output callback并核验正常退出，失败报告单独保留。格式/顺序无法识别拒绝恢复。目标steps超过max_steps（1..100000，default5000）在第一Undo前拒绝。每Undo前比较整队列与预期前缀，异步脚本/新操作改变队列停止，报实际已撤步骤不假称完成；真实plugin marker到达才成功。GUI加速suspend refresh并finally恢复原状态，batch不触viewport；原场景操作本身可能非Undoable或有文件副作用，记录点不能还原这些动作或文件IO，回退还可能执行用户原命令Undo代码。

```python
from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool
t=UndoCheckpointTool()
point=t.run(action='create',name='修改前')
# 后续可Undo场景编辑
t.run(dry_run=True,action='restore',target_id=point.data['id'])
t.run(action='restore',target_id=point.data['id'])
```

Shelf四owned docTag按钮按正式完整module调用，真实换行代码可编译、不硬编码临时sys.path；重复安装更新自身tag/不覆盖其他按钮，不自动savePrefs，不是场景Undo。独立create默认overwrite唯一，restore最新，clear仅metadata。面板全部原widget/styles/提示保留，不需QApplication新建；对已清点/队列变化须真实UI复核。native command owner路径不合拒绝，含Undo记录时不能随意unload其plugin。

2离线queue/真实Shelf command compile +3隔离Maya2025实际marker/多点tx1/2/3回退与Redo、引号名不执行MEL、dryqueue不变/max不足零步/flush旧点拒绝/foreignID/clear保队列/overwrite/Undo关闭拒绝/临时最终注册-domain-panel通过仅非GUI证据；真实MayaQt/Shelf/Refresh嵌套chunks/外部脚本队列竞争/跨版本not_run。原示例2020-2026/Python2未迁移为已支持承诺，候选目标Maya2025Python3。

参考：[MCommandMessage callback](https://help.autodesk.com/cloudhelp/2025/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_command_message.html)。自包含业务不修改框架/core，晋级注册与资源/知识/tests已预制；未验收仍待整理池。
''')
put(RC/'acceptance.md','''# Maya记录点直验 not_run

备份scene真实GUI中：import/dry create/restore/clear/install不改scene/Undo队列或UI；原Qt面板全部create/name/多行状态/双击与选中/最新恢复/clear/视口提示运行。tx1→记录A→tx2→记录B→tx3，B恢复tx2，Redo标记与编辑回tx3，A恢复tx1，标记本身无场景节点；中文/引号名不能执行MEL。max_steps不足/target foreign/flush/有限历史截断/scene新建切换必须零步拒绝，不Undo无关编辑；manual Undo/Redo状态一致，clear/overwrite只列表，不清原Undo。调用必须外层chunk外；嵌套marker不可见如实失败，不能擅关caller chunk。异常/其他脚本插队停止且报告已撤步骤，refresh原状态恢复；不能恢复文件IO/非undo命令。实际四Shelf owned buttons点击/重复安装不重复、不改其他button、完整模块callback、退出后prefs是否保存取决用户，不自动写prefs。真实GUI/Shelf/跨版本未验，mayapy不算直验，通过后当前SHA/版本/操作者/日期再晋级。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','06_diagnostics_security/undo_checkpoint','--class-name','UndoCheckpointTool','--summary','Complete Maya checkpoint marker/API/original Qt panel/standalone shortcuts/four Shelf buttons with read-only queue preflight and bounded guarded Undo restoration','--limitations','Real Maya GUI/Shelf/viewport refresh, nesting/queue concurrency and cross-version acceptance not_run'],check=True)
