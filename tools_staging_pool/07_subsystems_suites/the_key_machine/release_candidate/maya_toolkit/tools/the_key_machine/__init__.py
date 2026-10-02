"""Complete original TheKeyMachine with source-enumerated API and owned session."""
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import session
OPS=[r['id'] for r in session.operations()]
class TheKeyMachineTool(BaseMayaTool):
    tool_id='the_key_machine';tool_name='TheKeyMachine 完整动画工具集';category='animation';version='1.0.0'
    description='Full native toolbar/selection sets/graph editor/mirror/pose/animation/worldspace/hotkey tools with isolated user data and Chinese localization'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','invoke','set_language'],'default':'inspect'},
        'data_root':{'type':'string'},'operation':{'type':'string','enum':OPS},'arguments':{'type':'object'},
        'objects':{'type':'array','items':{'type':'string'},'maxItems':4096},'language':{'type':'string','enum':['en_US','zh_CN'],'default':'zh_CN'}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            if kw.get('language','zh_CN') not in ('en_US','zh_CN'):raise ValueError('Invalid language')
            if action in ('show_ui','invoke'):session.root_path(kw.get('data_root'))
            if action=='invoke':session.operation(kw.get('operation'),kw.get('arguments'),kw.get('objects'))
            return ToolResult.ok(message='纯参数/目标预检；未导入native、写目录、注册job/UI或timer',data={'action':action,'native_context_checks':'Deferred to original operation; GUI-only commands require real Maya'})
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'operations':len(OPS),'source_version':'0.1.4 build306','gui_acceptance':'not_run','full_resources':True})
        if action=='close_ui':return ToolResult.ok(data=session.close())
        if action=='set_language':
            session.language=kw.get('language','zh_CN')
            if session.toolbar_module and session.toolbar_module.tb:session.reload_ui()
            return ToolResult.ok(data={'language':session.language,'file_write':False})
        session.language=kw.get('language','zh_CN')
        if action=='show_ui':return ToolResult.ok(data=session.show(kw['data_root']))
        session.configure(kw['data_root']);value=session.invoke(kw['operation'],kw.get('arguments'),kw.get('objects'))
        return ToolResult.ok(data={'operation':kw['operation'],'result':value if isinstance(value,(dict,list,str,int,float,bool,type(None))) else str(value),'external_files_undoable':False})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        roots=cmds.fileDialog2(fileMode=3,caption='TheKeyMachine 候选：选择独立数据目录')
        return session.show(roots[0]) if roots else None
