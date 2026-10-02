from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import backend
class ShelfManagerTool(BaseMayaTool):
    tool_id='shelf_manager';tool_name='跨版本工具架管理器';category='scene_hygiene';version='1.0.0'
    description='Complete original bilingual/version shelf manager with scoped scans, explicit MEL loading, recoverable quarantine and collision-safe migration'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','scan','show_ui','close_ui','load','quarantine','migrate'],'default':'inspect'},'roots':{'type':'array','items':{'type':'string'},'maxItems':32},'files':{'type':'array','items':{'type':'string'},'maxItems':1000},'target_dir':{'type':'string'},'include_defaults':{'type':'boolean','default':False},'include_icons':{'type':'boolean','default':True},'overwrite':{'type':'boolean','default':False},'confirm_execute_mel':{'type':'boolean','default':False},'confirm_quarantine':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for key in ('include_defaults','include_icons','overwrite','confirm_execute_mel','confirm_quarantine'):
                if key in kw and type(kw[key]) is not bool:raise ValueError('Strict boolean '+key)
            if action not in ('inspect','close_ui'):backend.roots(kw.get('roots'))
            if action in ('load','quarantine'):backend.selected(kw['roots'],kw.get('files'),kw.get('include_icons',True))
            if action=='load' and not kw.get('confirm_execute_mel'):raise ValueError('Loading executes MEL; explicit confirm_execute_mel required')
            if action=='quarantine' and not kw.get('confirm_quarantine'):raise ValueError('Explicit quarantine confirmation required')
            if action=='migrate':backend.migration(kw['roots'],kw.get('files'),kw.get('target_dir'),kw.get('include_icons',True),kw.get('overwrite',False))
            return ToolResult.ok(message='只读文件预检/扫描，无MEL执行/UI/复制或移动')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'versions':'2018-2026','default_delete':'recoverable quarantine','gui_acceptance':'not_run'})
        if action=='scan':return ToolResult.ok(data={'shelves':backend.scan(kw['roots'],kw.get('include_defaults',False))})
        if action=='migrate':return ToolResult.ok(data={'receipts':backend.migrate(backend.migration(kw['roots'],kw['files'],kw['target_dir'],kw.get('include_icons',True),kw.get('overwrite',False)))})
        if action=='quarantine':return ToolResult.ok(data={'receipts':backend.quarantine(backend.selected(kw['roots'],kw['files'],kw.get('include_icons',True)))})
        from . import session
        if action=='show_ui':session.show(kw['roots']);return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya shelf GUI required')
        return ToolResult.ok(data={'loaded':[session.load_shelf(value) for value in kw['files']]})
    def show_ui(self,parent=None):
        from . import session
        return session.show()
