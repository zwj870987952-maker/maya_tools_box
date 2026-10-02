"""Full original toolbar UI prototype and validated in-memory workspace API."""
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
