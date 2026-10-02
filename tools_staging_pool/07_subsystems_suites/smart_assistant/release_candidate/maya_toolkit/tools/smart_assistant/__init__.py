"""Full assistant suite contract, with zero global hooks on import/UI launch."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import config_io,session,operations
class SmartAssistantTool(BaseMayaTool):
    tool_id='smart_assistant';tool_name='Maya Smart Assistant';category='pipeline_io';version='1.0.0'
    description='五项偏好typed保存/应用/恢复，完整文件拖拽与图片序列相机，显式可撤销会话监听/Python文件对话框补丁'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','enable','disable','start_monitor','stop_monitor','patch_dialog','restore_dialog','capture_prefs','save_prefs','read_prefs','apply_prefs','restore_prefs','open_scene','import_file','reference_file','create_sequence_camera'],'default':'inspect'},
        'path':{'type':'string','description':'绝对JSON路径或序列目录'},'paths':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':64,'uniqueItems':True},
        'preferences':{'type':'object','description':'只允许原五项typed optionVar'},'namespace':{'type':'string','default':''},
        'confirm_replace_scene':{'type':'boolean','default':False},'open_view':{'type':'boolean','default':False}},'required':[]}
    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown argument')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Unknown action')
        for key in ('confirm_replace_scene','open_view'):
            if type(kwargs.get(key,False)) is not bool:raise ValueError('Strict boolean required')
        p={'action':action}
        if action=='inspect':return p
        if action in ('read_prefs','apply_prefs'):
            values=config_io.prefs(kwargs['preferences']) if 'preferences' in kwargs else config_io.read_prefs(kwargs.get('path'))
            return {**p,'preferences':values,'scene_undo':False}
        if action=='save_prefs':
            values=config_io.prefs(kwargs['preferences']) if 'preferences' in kwargs else session.capture_prefs()
            return {**p,'preferences':values,'path':str(config_io.output_path(kwargs.get('path')))}
        if action in ('open_scene','import_file','reference_file'):
            mode={'open_scene':'open','import_file':'import','reference_file':'reference'}[action]
            plan=operations.plan_files(kwargs.get('paths'),mode,kwargs.get('namespace',''),kwargs.get('confirm_replace_scene',False))
            if mode!='open':
                from maya import cmds
                if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
            return {**p,**plan}
        if action=='create_sequence_camera':
            p.update(config_io.sequence(kwargs.get('path')));p['open_view']=kwargs.get('open_view',False)
            from maya import cmds
            if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
            if p['open_view'] and cmds.about(batch=True):raise ValueError('Real Maya GUI required for view')
            return p
        if action in ('show_ui','close_ui','enable','disable','start_monitor','stop_monitor','patch_dialog','restore_dialog'):
            from maya import cmds
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required for session hooks')
        return p
    def validate(self,**kwargs):
        try:return ToolResult.ok('Assistant plan',data=self._plan(kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(str(e),errors=[str(e)])
    def execute(self,**kwargs):
        p=self._plan(kwargs);a=p['action']
        if a=='inspect':return ToolResult.ok('Assistant inventory',data={'preference_keys':list(config_io.KEYS),'file_types':sorted(config_io.FILES),'gui_acceptance':'not_run','hooks_automatic':False})
        if a=='read_prefs':return ToolResult.ok('Preference data',data={'preferences':p['preferences']})
        if a=='capture_prefs':return ToolResult.ok('Current preference optionVars',data={'preferences':session.capture_prefs()})
        if a=='save_prefs':return ToolResult.ok('Saved new config',data={'path':config_io.write_prefs(p['path'],p['preferences'])})
        if a=='apply_prefs':return ToolResult.ok('Typed optionVars applied',data=session.apply_prefs(p['preferences']))
        if a=='restore_prefs':session.restore_prefs();return ToolResult.ok('Pre-session optionVars restored')
        if a in ('open_scene','import_file','reference_file'):return ToolResult.ok('File operation completed',data=operations.execute_files(p))
        if a=='create_sequence_camera':return ToolResult.ok('Sequence camera created',data=operations.create_sequence(p,p['open_view']))
        from .native import main
        from .native.dragdrop import dragdrop_handler
        if a=='show_ui':return ToolResult.ok('Assistant controls',data={'window':main.show_main_window()})
        if a=='close_ui':main.close_ui();return ToolResult.ok('Owned controls closed; hooks retain explicit session state')
        if a=='start_monitor':dragdrop_handler.start_dragdrop_monitor()
        if a=='stop_monitor':dragdrop_handler.stop_dragdrop_monitor()
        if a=='patch_dialog':session.patch_dialog()
        if a=='restore_dialog':session.restore_dialog()
        if a=='enable':
            had_patch=session.patch is not None;had_monitor=dragdrop_handler._filter is not None
            session.patch_dialog()
            try:dragdrop_handler.start_dragdrop_monitor();main.show_main_window()
            except Exception:
                if not had_monitor:dragdrop_handler.stop_dragdrop_monitor()
                if not had_patch:session.restore_dialog()
                raise
        if a=='disable':
            dragdrop_handler.stop_dragdrop_monitor();session.restore_dialog();session.restore_prefs();main.close_ui()
        return ToolResult.ok('Explicit session state changed',data=session.state())
    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            r=self.validate(**kwargs)
            if r.success and not dry_run:r=self.execute(**kwargs)
        except Exception as e:r=ToolResult.fail(str(e),errors=[str(e)])
        r.tool_id=self.tool_id;r.dry_run=dry_run;return r
    def show_ui(self,parent=None):return self.run(action='show_ui')
