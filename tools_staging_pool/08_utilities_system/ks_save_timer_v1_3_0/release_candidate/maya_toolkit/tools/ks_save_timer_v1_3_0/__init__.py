from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import storage
class KSSaveTimerTool(BaseMayaTool):
    tool_id='ks_save_timer_v1_3_0';tool_name='KS Save Timer 保存提醒与工时';category='scene_hygiene';version='1.0.0'
    description='Complete bilingual native timer, idle detection, color flashing, configuration and file-version history; never autosaves scenes'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','start','pause','reset','set_time','read_history','set_option'],'default':'inspect'},'data_root':{'type':'string'},'language':{'type':'string','enum':['zh','en'],'default':'zh'},'host':{'type':'string','enum':['maya','nuke','desktop'],'default':'maya'},'embed':{'type':'boolean','default':False},'watch_file':{'type':'string'},'minutes':{'type':'integer','minimum':0,'maximum':1000000},'section':{'type':'string','enum':['general','timerOptions']},'key':{'type':'string'},'value':{},'persist':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for key in ('embed','persist'):
                if key in kw and type(kw[key]) is not bool:raise ValueError('Strict boolean '+key)
            if kw.get('host','maya') not in ('maya','nuke','desktop') or kw.get('language','zh') not in ('zh','en'):raise ValueError('Unknown host/language')
            if action in ('show_ui','read_history'):storage.root(kw.get('data_root'))
            if action=='set_time' and (type(kw.get('minutes')) is not int or not 0<=kw['minutes']<=1000000):raise ValueError('Bounded integer minutes required')
            if action=='set_option':storage.config_value(kw.get('section'),kw.get('key'),kw.get('value'))
            if 'watch_file' in kw:
                from pathlib import Path
                p=Path(kw['watch_file'])
                if not p.is_absolute() or not p.is_file() or p.is_symlink():raise ValueError('Existing watch file required')
            return ToolResult.ok(message='无Qt/回调/计时/文件写入的预检')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'languages':['zh','en'],'hosts':['maya','nuke','desktop'],'autosave':False,'gui_acceptance':'not_run'})
        if action=='read_history':return ToolResult.ok(data={'history':storage.read_history(storage.root(kw['data_root'])/'KSSaveTimer_timeTrackHistory.json')})
        from . import session
        if action=='show_ui':session.show(kw['data_root'],kw.get('language','zh'),kw.get('host','maya'),kw.get('embed',False),kw.get('watch_file'));return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if session.window is None:raise RuntimeError('Open owned timer UI first')
        timer=session.window.TIMER
        if action=='start':session.window.setPauseToggle(False)
        elif action=='pause':session.window.setPauseToggle(True)
        elif action=='reset':timer.reset()
        elif action=='set_time':timer.setTime(kw['minutes'])
        elif action=='set_option':
            config=session.window._CONFIG_;config.set(kw['section'],kw['key'],kw['value'])
            if kw.get('persist'):config.writeConfig()
        return ToolResult.ok(data={'counter':timer.counter,'active':timer.isActive()})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=3,caption='KS Save Timer：选择独立计时配置与历史目录')
        if not values:return None
        from .session import show
        return show(values[0],parent=parent)
