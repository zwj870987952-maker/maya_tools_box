"""Full 45-node graph suite, headless API and original Chinese canvas."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import workflow,file_io
class MayaBlueprintToolboxTool(BaseMayaTool):
    tool_id='maya_blueprint_toolbox';tool_name='Maya 蓝图工具盒';category='pipeline_io';version='1.0.0'
    description='45种原生类型节点与完整中文蓝图画布；结构/连线/当前可解析操作预检、统一图执行和JSON持久化'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','validate_workflow','execute_workflow','read_workflow','save_workflow'],'default':'inspect'},
        'workflow':{'type':'object','description':'version1，nodes/parameters与connections typed graph'},
        'target_node_ids':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},
        'path':{'type':'string','description':'绝对JSON路径，parent已存在'},
        'overwrite_existing':{'type':'boolean','default':False}},'required':[]}
    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameter')
        action=kwargs.get('action','inspect');overwrite=kwargs.get('overwrite_existing',False)
        if action not in self.parameters_schema['properties']['action']['enum'] or type(overwrite) is not bool:raise ValueError('Invalid action/boolean')
        if action=='inspect':return {'action':action}
        if action in ('show_ui','close_ui'):
            from maya import cmds
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required')
            return {'action':action}
        if action=='read_workflow':
            return {'action':action,'workflow':workflow.normalize_graph(file_io.read_json(kwargs.get('path')),require_inputs=False)}
        graph=kwargs.get('workflow')
        if action=='save_workflow':
            graph=workflow.normalize_graph(graph,require_inputs=False)
            return {'action':action,'workflow':graph,'path':str(file_io.output_path(kwargs.get('path'),overwrite))}
        plan=workflow.plan_graph(graph,kwargs.get('target_node_ids'),resolve_scene=True)
        if plan['effects']:
            from maya import cmds
            if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo before graph operations')
        return {'action':action,**plan}
    def validate(self,**kwargs):
        try:return ToolResult.ok('Blueprint plan',data=self._plan(kwargs),dry_run=True)
        except Exception as error:return ToolResult.fail(str(error),errors=[str(error)])
    def execute(self,**kwargs):
        p=self._plan(kwargs);action=p['action']
        if action=='inspect':return ToolResult.ok('45 native nodes',data={'node_specs':[s.to_dict() for s in workflow.specs().values()],'gui_acceptance':'not_run'})
        if action=='show_ui':
            from .native import show
            window=show();return ToolResult.ok('Blueprint canvas opened',data={'object_name':window.objectName()})
        if action=='close_ui':
            from .native import main
            if main._window_instance is not None:
                try:main._window_instance.close();main._window_instance.deleteLater()
                except RuntimeError:pass
                main._window_instance=None
            return ToolResult.ok('Owned blueprint window closed')
        if action=='save_workflow':return ToolResult.ok('Workflow saved',data={'path':file_io.write_json(p['path'],p['workflow'],kwargs.get('overwrite_existing',False))})
        if action in ('read_workflow','validate_workflow'):return ToolResult.ok('Workflow plan',data=p)
        result=workflow.execute_graph(p['workflow'])
        return ToolResult.ok('Workflow completed',data={'results':workflow.serializable(result),'node_count':p['node_count']})
    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            result=self.validate(**kwargs)
            if result.success and not dry_run:result=self.execute(**kwargs)
        except Exception as error:result=ToolResult.fail(str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;return result
    def show_ui(self,parent=None):return self.run(action='show_ui')
