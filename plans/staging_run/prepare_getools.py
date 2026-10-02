"""Complete localized GETools with pinned MIT dependencies and a real suite adapter."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from prepare_small_candidate import put

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/getools_overlappy'
RC=UNIT/'release_candidate'; PKG=RC/'maya_toolkit/tools/getools_overlappy'
DEP=RC/'dependency_source'; BUNDLE=PKG/'bundle/GETOOLS_SOURCE'
provenance=json.loads((RC/'dependency_provenance.json').read_text(encoding='utf-8'))
review=[]
for row in provenance['files']:
    src=DEP/row['path']
    if not src.exists() and src.suffix=='.py':src=src.with_suffix('.py.original')
    assert hashlib.sha256(src.read_bytes()).hexdigest()==row['sha256']
    dst=PKG/'upstream_dependency'/row['path']
    if src.suffix=='.py':dst=dst.with_suffix('.py.original')
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    rel=src.relative_to(DEP)
    if rel.parts[0]!='GETOOLS_SOURCE' or '_prototypes' in rel.parts:continue
    live=PKG/'bundle'/rel
    live.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,live)
for src in UNIT.glob('*.py'):
    if src.name!='__init__.py':shutil.copyfile(src,BUNDLE/'modules'/src.name)
put(PKG/'bundle/__init__.py','')
put(PKG/'dependency_provenance.json',json.dumps(provenance,ensure_ascii=False,indent=2))

def edit(path,old,new):
    s=path.read_text(encoding='utf-8')
    if old not in s:raise ValueError('Expected source missing '+str(path))
    put(path,s.replace(old,new))

# Preserve MIT notices, relative imports and every original feature. Shelf snippets use final package.
for src in sorted(BUNDLE.rglob('*.py')):
    s=src.read_text(encoding='utf-8'); tree=ast.parse(s)
    review.append({'path':src.relative_to(BUNDLE).as_posix(),'lines':len(s.splitlines()),
                   'imports':[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))],
                   'classes':[n.name for n in ast.walk(tree) if isinstance(n,ast.ClassDef)]})
    s=s.replace('import GETOOLS_SOURCE.', 'import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.')
    s=s.replace('from GETOOLS_SOURCE.', 'from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.')
    if src.name=='Locators.py':s=s.replace(' is not 0:', ' != 0:')
    put(src,s)
put(PKG/'source_review.json',json.dumps(review,ensure_ascii=False,indent=2))
settings=BUNDLE/'Settings.py'
edit(settings,'windowName = "windowGETools"','windowName = "MTB_windowGETools"')
edit(settings,'dockName = "dockGETools"','dockName = "MTB_dockGETools"')
edit(BUNDLE/'modules/Overlappy.py','prefix = "ovlp"','prefix = "MTB_ovlp"')

# Retain each native module instance for explicit API, not ephemeral UI-only callbacks.
general=BUNDLE/'modules/GeneralWindow.py'
for module in ('Transformations','Tools','Rigging','Overlappy','CenterOfMass','Experimental'):
    edit(general,f'\t\t{module}.{module}(self.optionsPlugin).UICreate(self.frame{module})',
         f'\t\tself.module{module} = {module}.{module}(self.optionsPlugin)\n\t\tself.module{module}.UICreate(self.frame{module})')
edit(general,'\t\tMayaSettings.HelpPopupActivate()\n\t\tMayaSettings.CachedPlaybackDeactivate()',
     '\t\t# Candidate launch does not change global help/cached-playback preferences.')

# Source methods deleting a fixed setup group must prove the exact group UUID belongs to this instance.
overlap=BUNDLE/'modules/Overlappy.py'
edit(overlap,'\tdef ParticleSetupDelete(self, deselect=False, clearCache=True, *args):',
     '\tdef ParticleSetupDelete(self, deselect=False, clearCache=True, *args):\n\t\tfrom .... import ownership\n\t\townership.assert_group_owned(self, OverlappySettings.nameGroup)')
edit(overlap,'\t\tcmds.group(empty = True, name = OverlappySettings.nameGroup)',
     '\t\tgroup = cmds.group(empty = True, name = OverlappySettings.nameGroup)\n\t\tself._owned_group_uuid = cmds.ls(group, uuid=True)[0]')

# Broken nested list in native COM constraint inputs fixed without changing weighted point semantics.
com=BUNDLE/'modules/CenterOfMass.py'
edit(com,'\t\tfinalList.append(self.COMObject)\n\t\tfinalList.append(selectedList)',
     '\t\tfinalList.extend(selectedList)\n\t\tfinalList.append(self.COMObject)')
edit(com,'\tdef COMClean(self, *args):',
     '\tdef COMClean(self, *args):\n\t\tfrom .... import ownership\n\t\townership.assert_com_owned(self)')
edit(com,'\t\tcmds.setAttr(self.COMObject + ".drawLabel", 1)',
     '\t\tself._owned_com_uuid = cmds.ls(self.COMObject, uuid=True)[0]\n\t\tcmds.setAttr(self.COMObject + ".drawLabel", 1)')

# Preset IO is bounded, does not pollute module globals and refuses overwriting any file.
filemod=BUNDLE/'utils/File.py'
notice='\n'.join(filemod.read_text(encoding='utf-8').splitlines()[:22])
put(filemod,notice+'''
import ast
import os
from pathlib import Path
import maya.cmds as cmds
_basicFileDialogFilter='*.txt';_dialogStyle=2

def ReadLogic(filepath,*args):
    path=Path(filepath)
    if not path.is_file():return None
    if path.stat().st_size>1024*1024:raise ValueError('Preset exceeds 1 MiB')
    result={}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if ' = ' not in line:continue
        key,value=line.strip().split(' = ',1)
        if not key.isidentifier() or key in result:raise ValueError('Invalid or duplicate preset key')
        result[key]=ast.literal_eval(value)
    return result,str(path)

def SaveLogic(filepath,variablesDictionary,title='',*args):
    path=Path(filepath)
    if path.exists():raise FileExistsError('Choose a new preset filename; existing file protected')
    if not isinstance(variablesDictionary,dict) or len(variablesDictionary)>1000:raise ValueError('Invalid preset')
    lines=[str(title).replace('\\n',' '),''] if title else []
    for key,value in variablesDictionary.items():
        if not isinstance(key,str) or not key.isidentifier():raise ValueError('Invalid preset key')
        ast.literal_eval(repr(value));lines.append(key+' = '+repr(value))
    text='\\n'.join(lines)+'\\n'
    if len(text.encode('utf-8'))>1024*1024:raise ValueError('Preset exceeds 1 MiB')
    if not path.parent.is_dir():raise ValueError('Output parent must exist')
    with path.open('x',encoding='utf-8',newline='\\n') as stream:stream.write(text)
    return str(path)

def SaveDialog(startingDirectory,variablesDict,title='',*args):
    result=cmds.fileDialog2(fileMode=0,startingDirectory=startingDirectory,fileFilter=_basicFileDialogFilter,dialogStyle=2)
    if result: return SaveLogic(result[0],variablesDict,title)
def ReadDialog(startingDirectory,*args):
    result=cmds.fileDialog2(fileMode=1,startingDirectory=startingDirectory,fileFilter=_basicFileDialogFilter,dialogStyle=2)
    return ReadLogic(result[0]) if result else None
''')
# Do not create directories on read/get-dictionary; default path resides in Maya preferences.
s=overlap.read_text(encoding='utf-8')
s=s.replace('self.directoryPresets = self.optionsPlugin.directory + Settings.pathPresets',
            'self.directoryPresets = cmds.internalVar(userAppDir=True) + "MTB_GETools_PRESETS/"')
s=s.replace('\t\tif not os.path.exists(self.directoryPresets):\n\t\t\tos.makedirs(self.directoryPresets)',
            '\t\t# No implicit directory writes while reading or collecting preset values.')
put(overlap,s)

# Wrap only native scene business callbacks; try/finally restores global time/selection/refresh.
put(PKG/'ownership.py','''import functools
import maya.cmds as cmds
from maya_toolkit.core.context import UndoChunkContext

def assert_group_owned(instance,name):
    if not cmds.objExists(name):return
    actual=cmds.ls(name,uuid=True)
    if len(actual)!=1 or actual[0]!=getattr(instance,'_owned_group_uuid',None):raise RuntimeError('Existing setup group is not owned by this instance; rename or inspect it first')
def assert_com_owned(instance):
    node=getattr(instance,'COMObject',None)
    if node and cmds.objExists(node) and cmds.ls(node,uuid=True)!=[getattr(instance,'_owned_com_uuid',None)]:raise RuntimeError('Borrowed COM object cannot be deleted by this candidate')

def scene_operation(function):
    @functools.wraps(function)
    def wrapped(*args,**kwargs):
        if not cmds.undoInfo(q=True,state=True):raise RuntimeError('Enable Maya Undo before native scene operations')
        selected=cmds.ls(selection=True,long=True) or [];time=cmds.currentTime(q=True)
        suspend=cmds.refresh(q=True,suspend=True)
        bounds={flag:cmds.playbackOptions(q=True,**{flag:True}) for flag in ('minTime','maxTime','animationStartTime','animationEndTime')}
        cached=cmds.optionVar(q='cachedPlaybackEnable') if cmds.optionVar(exists='cachedPlaybackEnable') else None
        with UndoChunkContext('GETools_'+function.__name__):
            try:return function(*args,**kwargs)
            finally:
                cmds.playbackOptions(**bounds);cmds.currentTime(time)
                cmds.refresh(suspend=suspend)
                if cached is not None:cmds.optionVar(intValue=('cachedPlaybackEnable',cached))
                cmds.select([n for n in selected if cmds.objExists(n)],replace=True) if selected else cmds.select(clear=True)
    return wrapped
''')
for module, methods in {
    'Overlappy':['ParticleSetupLogic','ParticleSetupDelete','BakeParticleLogic','BakeParticleVariants','LayerMoveToSafeOrTemp'],
    'CenterOfMass':['COMCreate','COMClean','COMConstrainToSelected','COMDisconnectTargets','COMFloorProjection','BakeScenario2','BakeScenario3','BakeCached'],
    'Transformations':['MoveSelected','SetPivotAttributes']}.items():
    p=BUNDLE/'modules'/(module+'.py');s=p.read_text(encoding='utf-8')
    s += '\nfrom ....ownership import scene_operation as _scene_operation\n'
    for method in methods:s+=f'{module}.{method} = _scene_operation({module}.{method})\n'
    put(p,s)
# Undo/context restores refresh on Baker exception even when called by non-Overlappy UI.
p=BUNDLE/'utils/Baker.py';s=p.read_text(encoding='utf-8')
s+='\nfrom ....ownership import scene_operation as _scene_operation\nBakeSelected = _scene_operation(BakeSelected)\n'
put(p,s)
# Keep force-reload/quit features, require an explicit UI confirmation and backup first.
p=BUNDLE/'utils/Scene.py';s=p.read_text(encoding='utf-8')
s=s.replace('def Reload(*args):','def Reload(*args):\n\tif cmds.about(batch=True) or cmds.confirmDialog(title="Reload scene", message="Discard unsaved changes and reload? Save a backup first.", button=["Cancel","Reload"], defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel") != "Reload": return')
s=s.replace('def ExitMaya(*args):','def ExitMaya(*args):\n\tif cmds.about(batch=True) or cmds.confirmDialog(title="Quit Maya", message="Quit and discard unsaved changes?", button=["Cancel","Quit"], defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel") != "Quit": return')
put(p,s)

put(PKG/'runtime.py','''"""Explicit native suite lifecycle and scene API; no import-time window or scene changes."""
from pathlib import Path
import maya.cmds as cmds
from .bundle.GETOOLS_SOURCE import Settings
from .bundle.GETOOLS_SOURCE.modules import GeneralWindow,Options,CenterOfMass
WINDOW=None
COM=None

class BoolValue:
    def __init__(self,value=False):self.value=value
    def Get(self):return self.value

def com_instance():
    global COM
    if COM is None:
        options=Options.PluginVariables();options.menuCheckboxEulerFilter=BoolValue(False)
        COM=CenterOfMass.CenterOfMass(options)
    return COM

def show():
    global WINDOW
    if cmds.about(batch=True):raise RuntimeError('Interactive Maya required')
    WINDOW=GeneralWindow.GeneralWindow()
    WINDOW.RUN_DOCKED(str(Path(__file__).parent/'bundle'),forced=True)
    return WINDOW

def close():
    global WINDOW
    if cmds.dockControl(Settings.dockName,exists=True):cmds.deleteUI(Settings.dockName,control=True)
    if cmds.window(Settings.windowName,exists=True):cmds.deleteUI(Settings.windowName)
    WINDOW=None

def overlap_instance():
    if WINDOW is None or not cmds.window(Settings.windowName,exists=True):raise RuntimeError('Open the candidate GETools window before configuring/baking its existing UI controls')
    return WINDOW.moduleOverlappy
''')
put(PKG/'__init__.py','''import math
import time
from pathlib import Path
from maya_toolkit.framework import BaseMayaTool,ToolResult

class GEToolsOverlappyTool(BaseMayaTool):
    tool_id='getools_overlappy';tool_name='GETools / Overlappy / CenterOfMass';category='animation'
    description='完整中文GETools与固定MIT依赖；GUI重叠动力学/完整套件，COM和预设独立API'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close','create_com','activate_com','add_com_targets','project_com','delete_com','setup_overlap','bake_overlap','clear_overlap','read_preset','save_preset'],'default':'inspect'},
        'targets':{'type':'array','uniqueItems':True,'items':{'type':'string'}},'weight':{'type':'number','minimum':0.001,'maximum':1000,'default':1},
        'mode':{'type':'string','enum':['point','aim','combo'],'default':'point'},'axis':{'type':'string','enum':['x','y','z'],'default':'y'},
        'preset_path':{'type':'string'},'preset_values':{'type':'object'},'confirm_bake':{'type':'boolean','default':False}}}
    def plan(self,**kw):
        if set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameter')
        action=kw.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Invalid action')
        weight=kw.get('weight',1)
        if isinstance(weight,bool) or not isinstance(weight,(int,float)) or not math.isfinite(weight) or not 0.001<=weight<=1000:raise ValueError('Invalid weight')
        if kw.get('mode','point') not in ('point','aim','combo') or kw.get('axis','y') not in ('x','y','z'):raise ValueError('Invalid mode/axis')
        if not isinstance(kw.get('confirm_bake',False),bool):raise ValueError('confirm_bake must be boolean')
        data={'action':action,'impact':'Native suite scene operations; physics depends on frame rate, bake modifies keys/layers. External preset writes are not Undo-able.'}
        if action=='inspect':
            import json
            provenance=json.loads(Path(__file__).with_name('dependency_provenance.json').read_text(encoding='utf-8'))
            data.update(dependency_commit=provenance['commit'],localized_modules=8,features=['Transformations','Tools','Rigging','Overlappy point/aim/combo','CenterOfMass','MotionTrail','Experimental'],maya_gui_acceptance='not_run')
            return data
        if action in ('read_preset','save_preset'):
            from .preset_io import preset_plan
            data.update(preset_plan(action,kw.get('preset_path'),kw.get('preset_values')));return data
        import maya.cmds as cmds
        from . import runtime,ownership
        if action not in ('show_ui','close','activate_com') and not cmds.undoInfo(q=True,state=True):raise ValueError('Enable Maya Undo first')
        if action in ('show_ui','setup_overlap','bake_overlap','clear_overlap') and cmds.about(batch=True):raise ValueError('Interactive Maya required')
        if action=='bake_overlap' and not kw.get('confirm_bake',False):raise ValueError('confirm_bake=True required; back up animation first')
        targets=kw.get('targets',[])
        if not isinstance(targets,list) or not all(isinstance(t,str) and t for t in targets) or len(targets)!=len(set(targets)):raise ValueError('Invalid targets')
        resolved=[]
        for target in targets:
            names=cmds.ls(target,long=True) or []
            if len(names)!=1 or not cmds.objectType(names[0],isAType='transform'):raise ValueError('Expected unique transform '+target)
            if cmds.referenceQuery(names[0],isNodeReferenced=True) or cmds.lockNode(names[0],q=True,lock=True)[0]:raise ValueError('Reference/locked target refused')
            resolved.append(names[0])
        if action in ('activate_com','setup_overlap') and len(resolved)!=1:raise ValueError('Exactly one target required')
        if action=='add_com_targets' and not resolved:raise ValueError('At least one target required')
        if action in ('add_com_targets','project_com','delete_com'):
            # Do not construct or activate state during preflight.
            instance=runtime.COM
            if instance is None or not instance.COMObject or not cmds.objExists(instance.COMObject):raise ValueError('Create or activate COM first')
            if action=='delete_com':ownership.assert_com_owned(instance)
            if cmds.referenceQuery(instance.COMObject,isNodeReferenced=True) or cmds.lockNode(instance.COMObject,q=True,lock=True)[0]:raise ValueError('Locked/reference COM refused')
            data['com_object']=instance.COMObject
            if action=='add_com_targets' and any(cmds.ls(n,uuid=True)==cmds.ls(instance.COMObject,uuid=True) for n in resolved):raise ValueError('COM cannot constrain itself')
            if action=='add_com_targets' and any(cmds.getAttr(instance.COMObject+'.'+a,lock=True) for a in ('tx','ty','tz')):raise ValueError('COM translation locked')
        if action in ('setup_overlap','bake_overlap','clear_overlap'):
            instance=runtime.overlap_instance()
            from .bundle.GETOOLS_SOURCE.modules.Overlappy import OverlappySettings
            ownership.assert_group_owned(instance,OverlappySettings.nameGroup)
            if action=='bake_overlap' and not instance.setupCreated:raise ValueError('Create current setup first')
        if len(resolved)!=len(set(resolved)):raise ValueError('Duplicate resolved target')
        data['targets']=resolved;return data
    def validate(self,**kw):
        try:return ToolResult.ok(message='GETools预检通过，无窗口/场景/文件写入',data=self.plan(**kw),dry_run=True)
        except Exception as error:return ToolResult.fail(message=str(error),errors=[str(error)],dry_run=True)
    def execute(self,**kw):
        plan=self.plan(**kw);action=plan['action']
        if action=='inspect':return ToolResult.ok(data=plan)
        if action in ('read_preset','save_preset'):
            from .preset_io import execute_preset
            return ToolResult.ok(data=execute_preset(action,kw['preset_path'],kw.get('preset_values')))
        import maya.cmds as cmds
        from . import runtime
        if action=='show_ui':runtime.show()
        elif action=='close':runtime.close()
        elif action=='create_com':runtime.com_instance().COMCreate();plan['com_object']=runtime.COM.COMObject
        elif action=='activate_com':runtime.com_instance().COMObject=plan['targets'][0];plan['com_object']=runtime.COM.COMObject
        elif action=='delete_com':runtime.COM.COMClean()
        elif action=='add_com_targets':
            for target in plan['targets']:
                if target==runtime.COM.COMObject:raise ValueError('COM cannot constrain itself')
                cmds.pointConstraint(target,runtime.COM.COMObject,maintainOffset=False,weight=kw.get('weight',1))
            plan['constraints']=cmds.listConnections(runtime.COM.COMObject,source=True,destination=False,type='pointConstraint') or []
        elif action=='project_com':runtime.COM.COMFloorProjection(kw.get('axis','y'))
        elif action=='setup_overlap':
            cmds.select(plan['targets'],replace=True)
            runtime.overlap_instance().ParticleSetupLogic({'point':1,'aim':2,'combo':3}[kw.get('mode','point')])
            plan['setup_created']=runtime.overlap_instance().setupCreated
            if not plan['setup_created']:return ToolResult.fail(message='Native setup not created',data=plan)
        elif action=='clear_overlap':runtime.overlap_instance().ParticleSetupDelete()
        elif action=='bake_overlap':
            if not runtime.overlap_instance().BakeParticleLogic():return ToolResult.fail(message='Native baking failed',data=plan)
        return ToolResult.ok(message='GETools操作完成',data=plan)
    def run(self,dry_run=False,**kw):
        start=time.time()
        if not isinstance(dry_run,bool):return ToolResult.fail(message='dry_run must be boolean',tool_id=self.tool_id)
        result=self.validate(**kw)
        if result.success and not dry_run:
            try:
                if kw.get('action','inspect') in ('inspect','read_preset','save_preset','show_ui','close','activate_com'):result=self.execute(**kw)
                else:
                    from .ownership import scene_operation
                    result=scene_operation(self.execute)(**kw)
            except Exception as error:result=ToolResult.fail(message=str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;result.execution_time=round(time.time()-start,4);return result
    def show_ui(self,parent=None):
        from .runtime import show
        return show()
''')
put(PKG/'preset_io.py','''"""Pure preset IO for structured API, independent of Maya UI and Undo."""
import ast
import hashlib
from pathlib import Path

def preset_plan(action,path,values=None):
    if not isinstance(path,str) or not path:raise ValueError('preset_path required')
    target=Path(path)
    if not target.is_absolute() or target.suffix.lower()!='.txt':raise ValueError('Absolute .txt path required')
    if action=='read_preset':
        if not target.is_file() or target.stat().st_size>1024*1024:raise ValueError('Existing preset <=1 MiB required')
        return {'preset_path':str(target),'source_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    if target.exists() or not target.parent.is_dir():raise ValueError('Fresh file and existing parent required')
    if not isinstance(values,dict) or not values or len(values)>1000:raise ValueError('Nonempty bounded preset_values required')
    for key,value in values.items():
        if not isinstance(key,str) or not key.isidentifier():raise ValueError('Invalid key')
        ast.literal_eval(repr(value))
    text='\\n'.join(key+' = '+repr(value) for key,value in values.items())+'\\n'
    if len(text.encode('utf-8'))>1024*1024:raise ValueError('Preset too large')
    return {'preset_path':str(target),'text':text}

def execute_preset(action,path,values):
    plan=preset_plan(action,path,values);target=Path(path)
    if action=='save_preset':
        with target.open('x',encoding='utf-8',newline='\\n') as output:output.write(plan['text'])
        return {'preset_path':str(target),'saved':True}
    result={}
    for line in target.read_text(encoding='utf-8-sig').splitlines():
        if ' = ' not in line:continue
        key,value=line.strip().split(' = ',1)
        if not key.isidentifier() or key in result:raise ValueError('Invalid/duplicate key')
        result[key]=ast.literal_eval(value)
    return {'preset_path':str(target),'values':result,'source_sha256':plan['source_sha256']}
''')
put(RC/'tests/test_getools_overlappy.py','''from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py');launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
else:
    sys.path.insert(0,str(ROOT));from maya_toolkit.tools.getools_overlappy import GEToolsOverlappyTool
    tool=GEToolsOverlappyTool()
class Tests(unittest.TestCase):
    def test_fresh_preset_roundtrip_no_overwrite_dry(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'preset.txt';args={'action':'save_preset','preset_path':str(path),'preset_values':{'flagLayer':True,'values':[1,2,3]}}
            self.assertTrue(tool.run(dry_run=True,**args).success);self.assertFalse(path.exists())
            self.assertTrue(tool.run(**args).success);before=path.read_bytes()
            self.assertFalse(tool.run(**args).success);self.assertEqual(path.read_bytes(),before)
            self.assertEqual(tool.run(action='read_preset',preset_path=str(path)).data['values'],args['preset_values'])
            bad=Path(d)/'bad.txt';bad.write_text('x = __import__("os").system("bad")')
            self.assertFalse(tool.run(action='read_preset',preset_path=str(bad)).success)
    def test_inspect_and_schema_no_native_import(self):
        result=tool.run();self.assertTrue(result.success)
        self.assertEqual(result.data['dependency_commit'],'45c4e17504fded01262941843ed186e9ac73c477')
        self.assertNotIn('maya_toolkit.tools.getools_overlappy.runtime',sys.modules)
        self.assertFalse(tool.run(weight=True).success)
        self.assertFalse(tool.run(confirm_bake='yes').success)
        self.assertFalse(tool.run(dry_run='no').success)
        self.assertFalse(tool.run(action='unsupported').success)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_getools_overlappy_maya.py','''import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Maya only')
import importlib.util
from pathlib import Path
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py');launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
class Tests(unittest.TestCase):
    def test_complete_native_import_no_scene_change_and_com_undo(self):
        cmds.undoInfo(state=True)
        before=cmds.ls(uuid=True)
        from maya_toolkit.tools.getools_overlappy import runtime
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.modules import GeneralWindow,Overlappy,Tools,Rigging,CenterOfMass,Experimental,Transformations
        self.assertEqual(cmds.ls(uuid=True),before)
        self.assertTrue(tool.run(dry_run=True,action='create_com').success);self.assertEqual(cmds.ls(uuid=True),before)
        a=cmds.group(empty=True,name='massA');b=cmds.group(empty=True,name='massB');cmds.setAttr(b+'.tx',10);cmds.select(a)
        old_time=cmds.currentTime(q=True);bounds=(cmds.playbackOptions(q=True,min=True),cmds.playbackOptions(q=True,max=True))
        result=tool.run(action='create_com');self.assertTrue(result.success,result)
        com=result.data['com_object'];uuid=cmds.ls(com,uuid=True)[0]
        self.assertEqual(cmds.ls(selection=True),[a]);self.assertEqual(cmds.currentTime(q=True),old_time)
        self.assertTrue(tool.run(action='add_com_targets',targets=[a,b]).success)
        self.assertAlmostEqual(cmds.getAttr(com+'.tx'),5)
        cmds.undo();self.assertAlmostEqual(cmds.getAttr(com+'.tx'),0)
        self.assertTrue(tool.run(action='delete_com').success);self.assertFalse(cmds.objExists(com))
        cmds.undo();self.assertEqual(cmds.ls(com,uuid=True),[uuid])
        self.assertEqual((cmds.playbackOptions(q=True,min=True),cmds.playbackOptions(q=True,max=True)),bounds)
        result=tool.run(action='activate_com',targets=[a]);self.assertTrue(result.success)
        self.assertFalse(tool.run(action='delete_com').success);self.assertTrue(cmds.objExists(a))
        self.assertFalse(tool.run(dry_run=True,action='show_ui').success)
    def test_foreign_setup_refused_and_preset_global_not_polluted(self):
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.modules import Overlappy,Options
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils import File
        instance=Overlappy.Overlappy(Options.PluginVariables())
        group=cmds.group(empty=True,name=Overlappy.OverlappySettings.nameGroup)
        with self.assertRaises(RuntimeError):instance.ParticleSetupDelete()
        self.assertTrue(cmds.objExists(group))
        fixture=Path(File.__file__).parents[1]/'PRESETS/overlappyDefault.txt'
        data=File.ReadLogic(str(fixture));self.assertIn('flagLayer',data[0]);self.assertFalse(hasattr(File,'flagLayer'))
        cmds.delete(group)
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/getools_overlappy.md','''# GETools / Overlappy / CenterOfMass 完整候选

原池仅八个中文module，不是可运行完整GETools。候选保留原始bytes/SHA/MIT说明，补完整Settings、29+公共工具/物理/枚举/代码示例、预设和四图标，固定官方commit 45c4e17504fded01262941843ed186e9ac73c477。直接GitHub/git/raw下载超时，jsDelivr固定提交文件经目录SHA256+size全部复核，来源/每文件清单归档；未运行官方安装器、prototypes只归档不作为运行入口。所有中文module覆盖在完整独立bundle/GETOOLS_SOURCE，相对依赖无待整理路径；Shelf代码示例改正式完整package import。MIT声明/原数据保留。[官方来源](https://github.com/GenEugene/GETools/tree/45c4e17504fded01262941843ed186e9ac73c477)。

完整Transformations/Tools/Rigging/Overlappy point-aim-combo/nucleus-nParticle惯性/烘焙/层/预设/CenterOfMass约束投影与缓存/MotionTrail/Experimental UI和算法都保留。COM是原joint加加权pointConstraint定位近似，不计算网格体积/真实物理质量。Overlap依赖FPS，不同20/30/60结果不同，真实角色/单位/FPS/循环接缝与reference rig需人工确认；碰撞功能原TODO，不承诺可用。

GEToolsOverlappyTool继承Base/ToolResult/animation/JSON Schema。默认inspect只读完整来源与feature清单；show_ui/close显式候选窗口。create_com新joint，activate_com/targets=[唯一对象]绑定现有目标，add_com_targets/targets/weight连接现COM加权pointConstraint，project_com/axis跳过x/y/z的平面投影（完整原实现），delete_com只允许本实例创建UUID。setup_overlap/targets=[唯一transform]/mode point-aim-combo操作已打开窗口实际控件参数，bake_overlap/confirm_bake=True烘焙当前setup，clear_overlap清理当前自有group。schema没有泛化任意eval/method调用，全部原工具仍可在完整native UI使用；API明确范围不等于删除其他功能。

```python
from maya_toolkit.tools.getools_overlappy import GEToolsOverlappyTool
tool=GEToolsOverlappyTool()
tool.run(dry_run=True,action='create_com')
tool.run(action='create_com')
tool.run(action='add_com_targets',targets=['pelvis','chest'],weight=1)
tool.show_ui()
tool.run(action='setup_overlap',targets=['tailCtrl'],mode='point')
tool.run(action='bake_overlap',confirm_bake=True)
```

validate/dry不建窗口/节点/目录/预设/改变选择；UI需要真实Maya。API scene operations与核心native回调用现有UndoChunk分组，finally还原currentTime/playback bounds/selection/refresh suspend/cachedPlaybackEnable已有值。Undo不等于所有solver内部状态/缓存/层拓扑完全恢复，实际复杂physics Undo/Redo必须实测。原固定ovlpGroup删除改MTB_ovlp组且必须匹配本实例UUID，foreign同名拒绝；COMActivate可指向现有对象但候选不允许借用对象一键删除。中文模块原COM约束nested list错改targets+COM顺序。单个操作失败可能留下部分可Undo的场景结果，务必使用备份场景。

read_preset/preset_path与save_preset/preset_values支持绝对txt/1MiB/合法唯一键/ast.literal_eval，无exec/globals.update。save只新文件+已存在parent，不覆盖，dry不mkdir；原UI读preset也不污染globals，原默认写路径改Maya userAppDir/MTB_GETools_PRESETS，启动不自动创建目录/写文件；用户保存前自行创建新目录并选择新文件，default重复保存不覆盖。UI reload/强制quit保留但Cancel为默认的显式确认；启动不再自动关闭CachedPlayback/启用HelpPopup。原其他native Shelf/导出/层删除/scene实验菜单仍有外部或广范围影响，独立真实GUI验收及备份不可省，不能通过API验收推定整套功能均通过。

非Maya单测验证配置/预设，不等于真实GUI。隔离mayapy仅有限native import/COM/ownership检查；完整7模块真实UI/physics/solver/层烘焙/跨版本/默认保存/已有rig引用/Undo-Redo not_run。整体保留第三方依赖未未经直验下沉到core；共享UndoChunk/Base，未改正式库。全部代码/资源/文档/tests/注册已有promotion，真实Maya满意前不得转正。
''')
put(RC/'acceptance.md','''# 真实Maya整套验收 not_run

1. 备份场景与动画，打开完整候选窗，7模块中文布局/全部slider/menu/相对图标/关闭重开/独立正式原GETools窗口互不关闭；启动不自动改全局CachedPlayback/HelpPopup，不下载资源/安装Shelf，原候选包/原脚本bytes不改。
2. COM create/activate/加权targets（同权两点应中点）/不同权重/投影x-y-z/缓存bake；borrowed COM删除拒绝、foreign MTB_ovlpGroup拒绝，不因名称碰撞删用户节点，锁/reference/不存在目标/坏最后对象预检拒绝。dry nodes/选择/dirty/Undo/文件无变化。真实原projection命令和引用rig需实测。
3. 使用非reference简单动画测试point/aim/combo/nucleus/particle参数/非零aim-upoffset、setup/当前bake/层输出/循环边界/删除setup；20/30/60 FPS结果需各自检查。确认bake才替换keys/layers；出错后选择/currentTime/range/refresh恢复，Undo/Redo关键帧与节点/层恢复与solver缓存差异实记。不在正式rig上试原删除全部层/骨骼/实验功能。
4. 完整Tools locator/bake/Animation/Timeline、Rigging blendshape/curve/skin、MotionTrail/Experimental、Shelf原菜单逐项检查：源filename与正式完整import可用、不会依赖池路径。文件IO/导出/Shelf偏好不可由scene Undo回滚，手动保存/备份再测，原广范围功能结果实记，不笼统宣布全部实测。
5. 预设literal读取不exec、不污染File.globals，非法/malformed拒绝；userAppDir/MTB_GETools_PRESETS手动创建，default只首次save，新filename另存，不覆盖旧文件；dry不mkdir。Reload/Quit默认Cancel，只在保存完备份后测试显式确认；验证跨Maya版本。candidate_sha256/maya_version/accepted_by/date/passed=true后执行预制晋级。
''')
# Downloaded source snapshot is archival, never another runnable entry tree.
for row in provenance['files']:
    src=DEP/row['path']
    if src.suffix=='.py' and src.exists():
        target=src.with_suffix('.py.original')
        if target.exists():
            assert target.read_bytes()==src.read_bytes()
            src.unlink()
        else:src.rename(target)
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/getools_overlappy',
    '--class-name','GEToolsOverlappyTool','--summary','Complete localized seven-module GETools with pinned MIT dependencies/resources, COM and preset API, owned setup guards and explicit native GUI physics',
    '--dependencies','Maya cmds/MEL nParticle/nucleus','Bundled fixed MIT GETools dependencies',
    '--limitations','Full Maya GUI, physics bake, native broad operations and cross-version acceptance not_run'],check=True)
