"""Preserve the complete supplied UI prototype; do not invent animation algorithms."""
import ast
import json
from pathlib import Path
import subprocess
import sys
from prepare_small_candidate import put

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/07_subsystems_suites/animbot_copy'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/animbot_copy'
NATIVE = PKG / 'native'

# Read/parse every source; retain all classes, layouts, painters and menu entries.
audit = []
for src in sorted(UNIT.rglob('*.py')):
    if 'release_candidate' in src.parts or '__pycache__' in src.parts:
        continue
    source = src.read_text(encoding='utf-8')
    tree = ast.parse(source)
    audit.append({'file':src.relative_to(UNIT).as_posix(), 'lines':len(source.splitlines()),
                  'classes':[n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                  'functions':[n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]})
    rel = src.relative_to(UNIT)
    if len(rel.parts) == 1:
        continue
    source = source.replace('from PySide6 import ', 'from ..qt import ')
    source = source.replace('import shiboken6', 'from ..qt import shiboken').replace('shiboken6.', 'shiboken.')
    put(NATIVE / rel, source)
put(RC / 'source_review.json', json.dumps(audit, ensure_ascii=False, indent=2))
put(NATIVE / '__init__.py', '"""Complete supplied UI, explicitly and lazily launched."""')
put(NATIVE / 'core/__init__.py', '')
put(NATIVE / 'ui/__init__.py', '')
put(NATIVE / 'widgets/__init__.py', '')
put(NATIVE / 'qt.py', '''try:
    from PySide6 import QtCore, QtGui, QtWidgets
    import shiboken6 as shiboken
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    import shiboken2 as shiboken
''')

# Extract only assignment constants, not imported Qt or executable upstream entry.
source = ast.parse((UNIT / 'core/workspace_manager.py').read_bytes())
assignments = [n for n in source.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
               and n.targets[0].id == 'SLIDER_CATEGORY_MODES']
cls = next(n for n in source.body if isinstance(n, ast.ClassDef))
assignments += [n for n in cls.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id.isupper()]
scope = {}
exec(compile(ast.Module(body=assignments, type_ignores=[]), '<reviewed library constants>', 'exec'), scope)
fields = ['SLIDER_CATEGORY_MODES', 'MAIN_TOOL_LIBRARY', 'CLASSIC_DEFAULT_TOOLS', 'CLASSIC_GRAPH_EDITOR_TOOLS',
          'MAIN_LOCATIONS', 'GRAPH_EDITOR_LOCATIONS', 'ALIGNMENTS', 'PRESETS']
put(PKG / 'library.json', json.dumps({key:scope[key] for key in fields}, ensure_ascii=False, indent=2))
put(PKG / 'workspace.py', '''"""Pure in-memory configuration; no Qt import, file writes or Maya edits."""
import copy
import json
from pathlib import Path

LIBRARY = json.loads(Path(__file__).with_name('library.json').read_text(encoding='utf-8'))
KNOWN = {tool['id'] for cat in LIBRARY['MAIN_TOOL_LIBRARY'].values() for mod in cat['modules'].values() for tool in mod['tools']}
KNOWN.update(LIBRARY['CLASSIC_DEFAULT_TOOLS']); KNOWN.update(LIBRARY['CLASSIC_GRAPH_EDITOR_TOOLS'])
PRESETS = copy.deepcopy(LIBRARY['PRESETS'])
CONFIGS = {
    'main':{'active_tools':set(LIBRARY['CLASSIC_DEFAULT_TOOLS']), 'location':'时间轴顶部', 'alignment':'center', 'single_row':False},
    'graph_editor':{'active_tools':set(LIBRARY['CLASSIC_GRAPH_EDITOR_TOOLS']), 'location':'在图形编辑器菜单下', 'alignment':'center', 'single_row':False}}
CURRENT_PRESET = 'Classic *'

def snapshot():
    return {'current_preset':CURRENT_PRESET, 'configs':{key:dict(value, active_tools=sorted(value['active_tools'])) for key,value in CONFIGS.items()},
            'preset_names':sorted(PRESETS), 'tool_library_count':len(KNOWN), 'animation_algorithms_implemented':False,
            'capability':'Supplied toolbar/workspace UI prototype only; animation menu labels do not implement animation operations.'}

def configuration(toolbar, config):
    if toolbar not in CONFIGS: raise ValueError('toolbar must be main or graph_editor')
    if not isinstance(config,dict) or not config or set(config)-{'active_tools','location','alignment','single_row'}:
        raise ValueError('Nonempty supported config required')
    result = copy.deepcopy(CONFIGS[toolbar])
    for key,value in config.items():
        if key == 'active_tools':
            if not isinstance(value,list) or not all(isinstance(t,str) for t in value) or len(value)!=len(set(value)) or set(value)-KNOWN:
                raise ValueError('Unknown or duplicate tool ids')
            value=set(value)
        elif key == 'single_row':
            if not isinstance(value,bool): raise ValueError('single_row must be boolean')
        elif key == 'alignment':
            if value not in ('left','center','right'): raise ValueError('Invalid alignment')
        elif key == 'location':
            choices = LIBRARY['MAIN_LOCATIONS' if toolbar=='main' else 'GRAPH_EDITOR_LOCATIONS']
            if value not in choices: raise ValueError('Invalid location for toolbar')
        result[key]=value
    return result

def preset_plan(name):
    if not isinstance(name,str) or name not in PRESETS: raise ValueError('Unknown preset')
    result={}
    for toolbar in CONFIGS:
        cfg=copy.deepcopy(PRESETS[name][toolbar]); active=cfg['active_tools']
        cfg['active_tools']=sorted(KNOWN) if active is None else active
        cfg['alignment']={'左对齐':'left','居中对齐':'center','右对齐':'right','单行':'center'}.get(cfg['alignment'],cfg['alignment'])
        result[toolbar]=configuration(toolbar,cfg)
    return result

def apply_preset(name):
    global CURRENT_PRESET
    plan=preset_plan(name)
    for toolbar,cfg in plan.items(): CONFIGS[toolbar].clear(); CONFIGS[toolbar].update(cfg)
    CURRENT_PRESET=name
''')

# Preserve the original QObject API while sharing the pure configuration state.
p = NATIVE / 'core/workspace_manager.py'
s = p.read_text(encoding='utf-8')
tree = ast.parse(s)
c = next(n for n in tree.body if isinstance(n, ast.ClassDef))
ctor = next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name=='__init__')
lines = s.splitlines()
lines[ctor.lineno-1:ctor.end_lineno] = '''    def __init__(self, parent=None):
        super().__init__(parent)
        self.toolbar_configs = state.CONFIGS
        self.PRESETS = state.PRESETS
        self.current_preset = state.CURRENT_PRESET'''.splitlines()
s='\n'.join(lines)+'\n'
s=s.replace('from ..qt import QtCore', 'from ..qt import QtCore\nfrom ... import workspace as state')
start=s.index('    def apply_preset(self, preset_name):')
end=s.index('# Singleton instance',start)
s=s[:start]+'''    def apply_preset(self, preset_name):
        state.apply_preset(preset_name)
        self.current_preset = preset_name
        for toolbar in ('main','graph_editor'):
            self.workspaceChanged.emit(toolbar)
            self.layoutConfigChanged.emit(toolbar)

'''+s[end:]
put(p,s)

# No machine-specific or proprietary icons needed: supplied QPainter fallback is complete.
p=NATIVE / 'core/icons.py';s=p.read_text(encoding='utf-8')
s=s.replace('ANIMBOT_RESOURCES_DIR = r"D:\\Users\\zhongweijie\\Documents\\maya\\scripts\\animBot\\_resources\\img"',
            'ANIMBOT_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")')
put(p,s)

# Bound QObject slots disconnect on receiver deletion; original singleton lambdas retained dead widgets.
for name, toolbar in [('main_toolbar','main'), ('graph_editor_toolbar','graph_editor')]:
    p=NATIVE / 'ui' / (name+'.py');s=p.read_text(encoding='utf-8')
    s=s.replace(f'lambda t: self.update_tool_visibility() if t == "{toolbar}" else None','self._workspace_changed')
    s=s.replace(f'lambda t: self.relayout_groups() if t == "{toolbar}" else None','self._layout_changed')
    at=s.index('    def _register_tool(')
    s=s[:at]+f'''    @QtCore.Slot(str)
    def _workspace_changed(self, toolbar):
        if toolbar == '{toolbar}': self.update_tool_visibility()

    @QtCore.Slot(str)
    def _layout_changed(self, toolbar):
        if toolbar == '{toolbar}': self.relayout_groups()

'''+s[at:]
    s=s.replace('self.setObjectName("AnimBotMainToolbar")','self.setObjectName("MTBAnimBotCopyMainToolbar")')
    s=s.replace('self.setObjectName("AnimBotGraphEditorToolbar")','self.setObjectName("MTBAnimBotCopyGraphEditorToolbar")')
    if toolbar=='graph_editor':
        s=s.replace('    if GRAPH_EDITOR_TOOLBAR_INSTANCE:\n', '    if GRAPH_EDITOR_TOOLBAR_INSTANCE and not shiboken.isValid(GRAPH_EDITOR_TOOLBAR_INSTANCE):\n        GRAPH_EDITOR_TOOLBAR_INSTANCE = None\n    if GRAPH_EDITOR_TOOLBAR_INSTANCE:\n')
    put(p,s)

# Restrict tab hiding to a sole tab, capture prior native state and restore before closing.
p=NATIVE / 'ui/workspace_control.py';s=p.read_text(encoding='utf-8')
s=s.replace('CONTROL_NAME = "animBotCopyWorkspaceControl"','CONTROL_NAME = "MTBAnimBotCopyWorkspaceControl"\n_TAB_STATES = []')
start=s.index('def hide_workspace_control_tab(');end=s.index('def create_workspace_control(',start)
s=s[:start]+'''def restore_tabs():
    for tab, visible, minimum, maximum in _TAB_STATES:
        if shiboken.isValid(tab):
            tab.setMinimumHeight(minimum); tab.setMaximumHeight(maximum); tab.setVisible(visible)
    _TAB_STATES.clear()

def hide_workspace_control_tab(parent_widget):
    p = parent_widget
    for _ in range(6):
        if p is None: break
        if isinstance(p, QtWidgets.QTabWidget) and p.count()==1:
            tab = p.tabBar()
            if not any(t[0] is tab for t in _TAB_STATES):
                _TAB_STATES.append((tab,tab.isVisible(),tab.minimumHeight(),tab.maximumHeight()))
            tab.hide(); tab.setFixedHeight(0)
            break
        p=p.parentWidget()

'''+s[end:]
s=s.replace('    global _WINDOW_INSTANCE, _TOOLBAR_INSTANCE\n    if cmds.workspaceControl',
            '    global _WINDOW_INSTANCE, _TOOLBAR_INSTANCE\n    restore_tabs()\n    if cmds.workspaceControl')
s=s.replace('    for widget in app.topLevelWidgets():','    if app is None: return None\n    for widget in app.topLevelWidgets():')
s=s.replace('_WINDOW_INSTANCE.setWindowTitle("animBot")','_WINDOW_INSTANCE.setWindowTitle("animBot Copy · UI prototype")')
put(p,s)
p=NATIVE / 'widgets/workspace_window.py';s=p.read_text(encoding='utf-8')
s=s.replace('    for widget in app.topLevelWidgets():','    if app is None: return None\n    for widget in app.topLevelWidgets():')
s=s.replace('self.setObjectName("animBotWorkspaceWindow")','self.setObjectName("MTBAnimBotCopyWorkspaceWindow")')
s=s.replace('self.setWindowTitle("Workspace")','self.setWindowTitle("Workspace · animBot Copy UI prototype")')
s=s.replace('        if ok and name:\n', '''        name = name.strip()
        if ok and name and name in WORKSPACE_MGR.PRESETS:
            QtWidgets.QMessageBox.warning(self, '工作区已存在', '请选择新名称，保留现有预设。')
            return
        if ok and name and len(name) <= 128:
''')
s=s.replace('            WORKSPACE_MGR.current_preset = name', '            WORKSPACE_MGR.current_preset = name\n            from ... import workspace as state\n            state.CURRENT_PRESET = name')
put(p,s)

put(PKG / 'ui.py', '''"""Lazy native UI lifecycle; uses Maya's QApplication exclusively."""
import sys

def notify(toolbar):
    mod=sys.modules.get(__package__+'.native.core.workspace_manager')
    if mod:
        mod.WORKSPACE_MGR.workspaceChanged.emit(toolbar)
        mod.WORKSPACE_MGR.layoutConfigChanged.emit(toolbar)

def require_gui():
    import maya.cmds as cmds
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    from .native.qt import QtCore,QtWidgets
    app=QtWidgets.QApplication.instance()
    if not isinstance(app,QtWidgets.QApplication) or QtCore.QThread.currentThread()!=app.thread(): raise RuntimeError('Maya QApplication and UI main thread required')

def launch(floating=False):
    require_gui()
    from .native.ui import workspace_control as wc
    if floating: return wc.create_floating_window()
    from .workspace import CONFIGS
    return wc.dock_to_location(CONFIGS['main']['location'])

def attach_graph_editor():
    require_gui()
    from .native.ui.graph_editor_toolbar import attach_to_graph_editor
    result=attach_to_graph_editor()
    if result is None: raise RuntimeError('Graph Editor controls not found')
    return result

def open_workspace():
    require_gui()
    from .native.widgets.workspace_window import show_workspace_window
    return show_workspace_window()

def close():
    require_gui()
    mod=sys.modules.get(__package__+'.native.ui.workspace_control')
    if mod: mod.close_workspace_control()
    for module, attr in [('native.ui.graph_editor_toolbar','GRAPH_EDITOR_TOOLBAR_INSTANCE'),
                         ('native.widgets.workspace_window','_WORKSPACE_WINDOW_INSTANCE')]:
        mod=sys.modules.get(__package__+'.'+module)
        obj=getattr(mod,attr,None) if mod else None
        if obj is not None:
            from .native.qt import shiboken
            if shiboken.isValid(obj): obj.close();obj.deleteLater()
            setattr(mod,attr,None)
    # Session configuration persists across close/reopen; no module reload or preference save.

def reposition(toolbar):
    from .workspace import CONFIGS
    if toolbar=='main':
        mod=sys.modules.get(__package__+'.native.ui.workspace_control')
        if mod and mod._TOOLBAR_INSTANCE is not None: mod.dock_to_location(CONFIGS[toolbar]['location'])
    else:
        mod=sys.modules.get(__package__+'.native.ui.graph_editor_toolbar')
        if mod and mod.GRAPH_EDITOR_TOOLBAR_INSTANCE is not None: mod.dock_graph_editor_toolbar(CONFIGS[toolbar]['location'])
''')
put(PKG / '__init__.py', '''"""Full original toolbar UI prototype and validated in-memory workspace API."""
import sys
import time
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import workspace

class AnimBotCopyTool(BaseMayaTool):
    tool_id='animbot_copy';tool_name='animBot Copy UI与Workspace';category='animation'
    description='原工具栏/Graph Editor/Workspace UI原型；配置API不编辑动画，按钮名称不代表算法已实现'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','configure','apply_preset','show_ui','attach_graph_editor','open_workspace','close'],'default':'inspect'},
        'toolbar':{'type':'string','enum':['main','graph_editor'],'default':'main'},
        'config':{'type':'object','additionalProperties':False,'properties':{
            'active_tools':{'type':'array','uniqueItems':True,'items':{'type':'string'}},
            'location':{'type':'string'},'alignment':{'type':'string','enum':['left','center','right']},'single_row':{'type':'boolean'}}},
        'preset':{'type':'string'},'floating':{'type':'boolean','default':False}}}
    def plan(self,**kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']): raise ValueError('Unknown parameter')
        action=kwargs.get('action','inspect'); toolbar=kwargs.get('toolbar','main')
        if action not in self.parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
        if toolbar not in workspace.CONFIGS: raise ValueError('Invalid toolbar')
        if not isinstance(kwargs.get('floating',False),bool): raise ValueError('floating must be boolean')
        if 'config' in kwargs and action!='configure': raise ValueError('config only accepted for configure')
        if 'preset' in kwargs and action!='apply_preset': raise ValueError('preset only accepted for apply_preset')
        data={'action':action,'toolbar':toolbar,'state':workspace.snapshot(),'impact':'UI/session configuration only. No animation operation or file writes.'}
        qt=sys.modules.get(__name__+'.native.qt')
        if qt and action in ('configure','apply_preset'):
            app=qt.QtWidgets.QApplication.instance()
            if app is not None and qt.QtCore.QThread.currentThread()!=app.thread(): raise ValueError('UI config must run on main thread')
        if action=='configure':
            cfg=workspace.configuration(toolbar,kwargs.get('config'))
            data['planned_config']=dict(cfg,active_tools=sorted(cfg['active_tools']))
        if action=='apply_preset':
            configs=workspace.preset_plan(kwargs.get('preset'))
            data['planned_configs']={key:dict(cfg,active_tools=sorted(cfg['active_tools'])) for key,cfg in configs.items()}
        # No lazy Qt import or widget creation during preflight.
        if action in ('show_ui','attach_graph_editor','open_workspace','close'):
            import maya.cmds as cmds
            if cmds.about(batch=True): raise ValueError('Interactive Maya required')
        return data
    def validate(self,**kwargs):
        try:return ToolResult.ok(message='配置预检通过，无场景/窗口/文件修改',data=self.plan(**kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        plan=self.plan(**kwargs);action=plan['action'];toolbar=plan['toolbar']
        from . import ui
        if action=='configure':
            cfg=workspace.configuration(toolbar,kwargs['config'])
            workspace.CONFIGS[toolbar].clear(); workspace.CONFIGS[toolbar].update(cfg)
            ui.notify(toolbar)
            if 'location' in kwargs['config']: ui.reposition(toolbar)
        elif action=='apply_preset':
            workspace.apply_preset(kwargs['preset'])
            mod=sys.modules.get(__name__+'.native.core.workspace_manager')
            if mod: mod.WORKSPACE_MGR.current_preset=workspace.CURRENT_PRESET
            for key in workspace.CONFIGS: ui.notify(key);ui.reposition(key)
        elif action=='show_ui':ui.launch(kwargs.get('floating',False))
        elif action=='attach_graph_editor':ui.attach_graph_editor()
        elif action=='open_workspace':ui.open_workspace()
        elif action=='close':ui.close()
        return ToolResult.ok(message='UI/会话配置操作完成；不执行动画算法',data={'action':action,**workspace.snapshot()})
    def run(self,dry_run=False,**kwargs):
        start=time.time()
        if not isinstance(dry_run,bool):return ToolResult.fail(message='dry_run must be boolean',tool_id=self.tool_id)
        result=self.validate(**kwargs)
        if result.success and not dry_run:
            try:result=self.execute(**kwargs)
            except Exception as error:result=ToolResult.fail(message=str(error),errors=[str(error)],data={'state':workspace.snapshot()})
        result.tool_id=self.tool_id;result.dry_run=dry_run;result.execution_time=round(time.time()-start,4)
        return result
    def show_ui(self,parent=None):
        from .ui import launch
        return launch()

def launch(use_workspace_control=True):
    from .ui import launch as show
    return show(floating=not use_workspace_control)
def close():
    from .ui import close as shut
    return shut()
def attach_to_graph_editor():
    from .ui import attach_graph_editor
    return attach_graph_editor()
''')
put(RC / 'tests/test_animbot_copy.py', '''import copy
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
    launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
else:
    sys.path.insert(0,str(ROOT))
    from maya_toolkit.tools.animbot_copy import AnimBotCopyTool
    tool=AnimBotCopyTool()
from maya_toolkit.tools.animbot_copy import workspace

class Tests(unittest.TestCase):
    def setUp(self):workspace.apply_preset('Classic *')
    def test_atomic_dry_validation_and_preset_roundtrip(self):
        before=copy.deepcopy(workspace.snapshot())
        self.assertTrue(tool.run(dry_run=True,action='apply_preset',preset='Expert').success)
        self.assertEqual(workspace.snapshot(),before)
        self.assertFalse(tool.run(action='configure',config={'alignment':'right','active_tools':['missing']}).success)
        self.assertEqual(workspace.snapshot(),before)
        self.assertTrue(tool.run(action='configure',config={'alignment':'right','single_row':True}).success)
        self.assertEqual(workspace.CONFIGS['main']['alignment'],'right')
        self.assertEqual(workspace.CONFIGS['graph_editor']['alignment'],'center')
        for preset in workspace.PRESETS:self.assertTrue(tool.run(action='apply_preset',preset=preset).success)
        self.assertEqual(len(workspace.CONFIGS['main']['active_tools']),len(workspace.KNOWN))
        workspace.PRESETS['custom']={'main':{'active_tools':[],'location':'时间轴顶部','alignment':'right','single_row':True},
                                  'graph_editor':{'active_tools':[],'location':'图形编辑器底部','alignment':'left','single_row':False}}
        self.assertTrue(tool.run(action='apply_preset',preset='custom').success)
        self.assertEqual(workspace.CONFIGS['main']['alignment'],'right')
        workspace.PRESETS.pop('custom')
    def test_no_qt_import_unsupported_and_bad_bool(self):
        self.assertNotIn('maya_toolkit.tools.animbot_copy.native.qt',sys.modules)
        self.assertFalse(tool.run(action='configure',toolbar='graph_editor',config={'location':'时间轴顶部'}).success)
        self.assertFalse(tool.run(action='configure',config={'single_row':1}).success)
        self.assertFalse(tool.run(dry_run='false').success)
        self.assertFalse(tool.run(action='bake').success)
        self.assertFalse(tool.run(action='configure',config={'active_tools':['slider_ease','slider_ease']}).success)
        self.assertFalse(tool.run(action='inspect',config={'single_row':True}).success)
        self.assertFalse(tool.run(action='apply_preset',preset='unknown').success)
        self.assertFalse(tool.run().data['animation_algorithms_implemented'])
if __name__=='__main__':unittest.main()
''')
put(RC / 'tests/test_animbot_copy_maya.py', '''import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Use isolated runner')
import importlib.util
from pathlib import Path
import sys
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
from maya_toolkit.tools.animbot_copy import workspace

class Tests(unittest.TestCase):
    def test_scene_and_undo_untouched(self):
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',7)
        before=(cmds.ls(uuid=True),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True))
        self.assertTrue(tool.run(dry_run=True,action='apply_preset',preset='Expert').success)
        self.assertTrue(tool.run(action='configure',config={'alignment':'right','active_tools':['slider_ease','slider_tween']}).success)
        self.assertTrue(tool.run(action='apply_preset',preset='Compact').success)
        self.assertEqual((cmds.ls(uuid=True),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True)),before)
        self.assertFalse(tool.run(dry_run=True,action='show_ui').success)
        self.assertNotIn('maya_toolkit.tools.animbot_copy.native.qt',sys.modules)
    def test_offscreen_original_widget_construction_and_live_sync(self):
        from maya_toolkit.tools.animbot_copy.native.qt import QtWidgets,QtCore,shiboken
        app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        from maya_toolkit.tools.animbot_copy.native.ui.main_toolbar import AnimBotMainToolbar
        from maya_toolkit.tools.animbot_copy.native.ui.graph_editor_toolbar import AnimBotGraphEditorToolbar
        from maya_toolkit.tools.animbot_copy.native.widgets.workspace_window import WorkspaceWindow
        from maya_toolkit.tools.animbot_copy.native.core.workspace_manager import WORKSPACE_MGR
        main=AnimBotMainToolbar(); graph=AnimBotGraphEditorToolbar(); window=WorkspaceWindow()
        self.assertGreater(len(main.tools_map),40);self.assertGreater(len(graph.tools_map),20)
        for preset in WORKSPACE_MGR.PRESETS:WORKSPACE_MGR.apply_preset(preset)
        WORKSPACE_MGR.apply_preset('Expert')
        self.assertFalse(main.tools_map['slider_ease'].isHidden())
        WORKSPACE_MGR.set_tool_active('slider_ease',False,'main')
        self.assertTrue(main.tools_map['slider_ease'].isHidden())
        self.assertIn('UI prototype',window.windowTitle())
        for widget in (main,graph,window):widget.close();widget.deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(None,QtCore.QEvent.DeferredDelete)
        WORKSPACE_MGR.apply_preset('Classic *')
        self.assertFalse(shiboken.isValid(main))
if __name__=='__main__':unittest.main()
''')
maya_test = RC / 'tests/test_animbot_copy_maya.py'
text = maya_test.read_text(encoding='utf-8')
start = text.index('    def test_offscreen_original_widget_construction_and_live_sync')
end = text.index("if __name__=='__main__':unittest.main()", start)
method = text[start:end]
put(maya_test, text[:start] + text[end:])
put(RC / 'tests/test_animbot_copy_qt.py', '''import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Use isolated runner')
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
# Deliberately no maya.standalone initialization: it already owns a QGuiApplication,
# which cannot host QWidget or be upgraded to QApplication.
class Tests(unittest.TestCase):
''' + method + "if __name__=='__main__':unittest.main()\n")
put(RC / 'docs/tools/animbot_copy.md', '''# animBot Copy 工具栏与Workspace UI原型候选

原项目是自有UI复刻原型，完整主/Graph Editor工具栏、QPainter图标、右键预设菜单、各滑杆回弹/模式切换防重、独立main/graph配置、Workspace多列库/工具勾选、新预设、原子换行、左右居中/单行拖动滚轮、边缘大小调整和workspaceControl停靠均保留。源README声称动画工具库完整，但按钮与大多数菜单没有动画业务回调；本候选明确不提供烘焙、姿态复制、Mirror、Ease算法等，不把UI标签当可调用动画能力。原始源码与全部screenshots完整SHA归档，旧截图仅历史参考，不是本轮验收证据。来源未提供LICENSE，不推定第三方图标授权；候选使用自带完整程序绘图fallback，不读取原硬编码机器路径/商业安装，也不下载第三方素材。

AnimBotCopyTool继承Base/ToolResult/animation/JSON Schema，默认inspect给出current_preset、main/graph configs、preset_names和animation_algorithms_implemented=false。action configure配toolbar/config（active_tools精确已知唯一id、alignment left/center/right、single_row严格bool、location匹配main/graph选项），apply_preset/preset整套只在预检全部通过后更新；show_ui/floating、attach_graph_editor、open_workspace、close需真实Maya GUI主线程。dry_run/validate不import Qt、不开窗、不改配置、场景或文件，源码库常量在构建时提取到本地library.json。run专门用于UI/session配置，不开Undo chunk/不初始化Maya，不伪造scene Undo；配置不会由Maya Undo恢复，重新apply_preset可还原布局。全close清理自有三窗口/Graph Editor插入控件，配置仍驻session；Maya退出丢失，新workspace只存内存，不自动保存偏好/场景。

```python
from maya_toolkit.tools.animbot_copy import AnimBotCopyTool
tool=AnimBotCopyTool()
tool.run(dry_run=True, action='apply_preset', preset='Expert')
tool.run(action='configure', toolbar='main', config={'alignment':'right','single_row':True})
tool.show_ui()
tool.run(action='attach_graph_editor')
tool.run(action='open_workspace')
tool.run(action='close')
```

完整UI搬入自有native子包，relative imports无临时目录依赖；取消原每次launch广泛reload吞异常/重置配置。PySide6/shiboken6优先，PySide2/shiboken2 fallback，未保证所有老版本枚举/平台事件可用。singleton信号改bound Qt Slot，避免lambda保留已delete控件；自有UI对象名前缀MTB，与原独立脚本不混淆。关闭恢复记录的单独tab可见性/高度，不改多tab共享Maya样式；原会遍历祖先隐藏所有tab/改祖先高度，候选只隐藏唯一tab，多个共用tab可保留tabbar。原Viewport位置仍以TimeSlider映射，不承诺真实viewport上/下另有停靠；不同Maya面板控制名称/可关闭Graph Editor布局需实测。配置preset支持英文字对齐，修正原自建right/left预设被当center。新预设不覆盖已存在名称。

动画核心逻辑实际不存在，不能复用现有core几何/anim算法而声称补齐；共享Base/ToolResult并保持UI专用样式，无正式core修改。mayapy/offscreen构造和纯配置检查只验证有限功能，不算真实Maya docking、鼠标/滚轮、尺寸、menu、GUI验收。其UI工具标签不能作为其他动画候选的可组合API；可组合部分只有Workspace配置。真实验收通过后已有完整代码/资源/文档/tests/注册promotion，当前全部留在待整理池。
''')
put(RC / 'acceptance.md', '''# 真实Maya验收 not_run

1. 在备份场景、已打开真实Maya中用launch_candidate.load_tool().show_ui()；完整主toolbar/QPainter图标/多slider/右键动态模式防重/Workspace窗口打开。注意这是UI原型，动画按钮缺业务算法是原项目事实；确认这与预期一致再验收，不能以动画菜单出现判断算法可用。
2. main/Graph Editor独立位置、独立工具勾选、Classic/Beginner/Compact/Expert/新名称preset；自建right/left回切正确，重名不覆盖；左右居中/单行拖拽滚轮/原子换行/边缘尺寸，回弹计时器，UI双向同步，隐藏模式防重。GraphEditor顶部/菜单下/底部与关闭重开，主timeline/shelf/status/floating位置；Viewport原映射限制如实确认。
3. dry_run config/preset前后配置/scene nodes/选择/dirty/Undo不变，坏最后id/location/非bool/重复id全表拒绝；configure只改对应toolbar，existing UI实时更新。无场景/文件保存、无外部硬编码图标依赖。原历史截图不是本轮测试证据。
4. 两个套件脚本同时存在仍互不关闭；连续开关主/Graph/Workspace至少三次，close无残留插入控件或signal callback报错、旧计时器停止，重开保持session配置；共享多tab不隐藏其他tab，独立tab关闭恢复原高度可见性。原Qt构造离线通过不替代这些真实GUI操作。跨Maya/Qt/系统实测记录版本；满意后填写candidate_sha256、maya_version、accepted_by/date/passed=true才可执行预制promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/animbot_copy',
                '--class-name','AnimBotCopyTool','--summary','Complete supplied toolbar/Graph Editor/workspace UI prototype, honest missing animation algorithms, validated in-memory config and lazy lifecycle',
                '--dependencies','Maya UI cmds/OpenMayaUI','PySide6/shiboken6 or PySide2/shiboken2',
                '--limitations','Real Maya docking, mouse/menu/slider lifecycle and cross-version GUI not_run','Original is UI prototype, not animBot animation algorithms'],check=True)
