from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import config_io
from pathlib import Path
class KSNodeOutlinerTool(BaseMayaTool):
    tool_id='ks_node_outliner_v2_2';tool_name='KS Node Outliner 双大纲';category='scene_hygiene';version='1.0.0'
    description='Complete native double Outliner, filter manager/presets/custom output and script filters with owned UI/filter cleanup'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','query_nodes','show_ui','close_ui','set_custom_output','read_config','write_config','restore_ui_settings'],'default':'inspect'},
        'config_path':{'type':'string'},'config_data':{'type':'object'},'overwrite':{'type':'boolean','default':False},
        'objects':{'type':'array','items':{'type':'string'},'maxItems':100000},'node_types':{'type':'array','items':{'type':'string'},'maxItems':512},'search':{'type':'string','default':'*'},
        'include_hierarchy':{'type':'boolean','default':False},'ignore_hierarchy':{'type':'boolean','default':False},'allow_custom_scripts':{'type':'boolean','default':False},'outliner_index':{'type':'integer','enum':[0,1],'default':0}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for k in ('overwrite','include_hierarchy','ignore_hierarchy','allow_custom_scripts'):
                if k in kw and type(kw[k]) is not bool:raise ValueError('Strict boolean '+k)
            if type(kw.get('outliner_index',0)) is not int or kw.get('outliner_index',0) not in (0,1):raise ValueError('Outliner index 0/1')
            if 'search' in kw and (not isinstance(kw['search'],str) or len(kw['search'])>1024):raise ValueError('Invalid search pattern')
            if 'node_types' in kw and (not isinstance(kw['node_types'],list) or len(kw['node_types'])>512 or any(not isinstance(n,str) or not n or len(n)>256 for n in kw['node_types'])):raise ValueError('Invalid node types')
            if action in ('read_config','write_config','show_ui'):
                p=config_io.path(kw.get('config_path'))
                if action=='read_config' or p.exists() and action=='show_ui':config_io.read(str(p))
                else:config_io.output(str(p),kw.get('overwrite',False))
            if action=='write_config':config_io.config(kw.get('config_data'))
            if 'objects' in kw:
                from .session import nodes
                nodes(kw['objects'])
            if action=='set_custom_output' and 'objects' not in kw:raise ValueError('Explicit objects required')
            return ToolResult.ok(message='无副作用预检；未导入Qt/native配置或创建过滤器/窗口')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'default_filters':list(config_io.read(Path(__file__).parent/'native/ks_nodeOutliner/ksNodeOutliner_filterData.json')['FILTERS']),'gui_acceptance':'not_run','complete_original':True})
        if action=='read_config':return ToolResult.ok(data={'config':config_io.read(kw['config_path'])})
        if action=='write_config':return ToolResult.ok(data=config_io.write(kw['config_path'],kw['config_data'],kw.get('overwrite',False)))
        from . import session
        if action=='show_ui':session.show(kw['config_path'],allow_custom=kw.get('allow_custom_scripts',False));return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if action=='restore_ui_settings':session.restore_options();return ToolResult.ok()
        if action=='query_nodes':return ToolResult.ok(data={'nodes':session.query(kw.get('node_types'),kw.get('objects'),kw.get('search','*'),kw.get('include_hierarchy',False))})
        if session.window is None:raise RuntimeError('Open owned Outliner first')
        session.window.allOutliners[kw.get('outliner_index',0)].setFilter_customOutput(session.nodes(kw['objects']),kw.get('ignore_hierarchy',False));return ToolResult.ok(data={'objects':kw['objects']})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=0,caption='KS Outliner：选择独立过滤器配置JSON',fileFilter='JSON (*.json)')
        if not values:return None
        from .session import show
        return show(values[0],parent)
