from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import config_io
class FloatingToolbarTool(BaseMayaTool):
    tool_id='floating_toolbar';tool_name='浮动工具栏';category='pipeline_io';version='1.0.0'
    description='Full editable draggable floating Maya shelf with explicit Python/MEL language, flow layout and portable icon JSON'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','enable_drag','disable_drag','load_config','save_config','set_buttons','get_buttons','execute_button','clear'],'default':'inspect'},'path':{'type':'string'},'buttons':{'type':'array','maxItems':256,'items':{'type':'object'}},'index':{'type':'integer','minimum':0,'maximum':255},'confirm_execute':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/arguments')
            if action=='load_config':config_io.read(kw.get('path'))
            if action=='save_config':config_io.new_path(kw.get('path'))
            if action=='set_buttons':config_io.rows(kw.get('buttons'))
            if action=='execute_button':
                if type(kw.get('index')) is not int or not 0<=kw['index']<256 or kw.get('confirm_execute') is not True:raise ValueError('Explicit index and confirm_execute=True required')
            return ToolResult.ok(message='无副作用预检；未执行按钮命令/启动窗口/修改原shelf')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'features':['flow_layout','add_edit_delete','shelf_drag','save_load','portable_png','explicit_python_mel'],'gui_acceptance':'not_run'})
        from . import session
        if action=='show_ui':session.show();return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if action in ('enable_drag','disable_drag'):return ToolResult.ok(data=getattr(session,action)())
        if session.window is None:raise RuntimeError('Open this floating toolbar first')
        if action=='load_config':return ToolResult.ok(data={'count':session.replace_buttons(session.window,config_io.read(kw['path']))})
        if action=='save_config':return ToolResult.ok(data={'path':config_io.write(kw['path'],session.snapshot()),'undo':'External config is not Maya Undo'})
        if action=='set_buttons':return ToolResult.ok(data={'count':session.replace_buttons(session.window,kw['buttons'])})
        if action=='get_buttons':return ToolResult.ok(data={'buttons':session.snapshot()})
        if action=='clear':session.window.clear_toolbar();return ToolResult.ok()
        if kw['index']>=session.window.toolbar_flow.count():raise ValueError('Button index out of range')
        value=session.execute_button(session.window.toolbar_flow.itemAt(kw['index']).widget(),True);return ToolResult.ok(data={'result':value})
    def show_ui(self,parent=None):
        from .session import show
        return show(parent)
