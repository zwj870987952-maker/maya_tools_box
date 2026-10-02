from pathlib import Path
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import storage
class MayaTabsTool(BaseMayaTool):
    tool_id='maya_tabs_v1_3a';tool_name='Maya Tabs 多场景标签';category='scene_hygiene';version='1.0.0'
    description='Complete licensed original tab toolbar, thumbnails, autosave-on-switch, sessions and theme editor with independent backed-up state'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','read_settings','write_settings','read_session','write_session','read_theme','write_theme','open_theme_editor'],'default':'inspect'},'data_root':{'type':'string'},'path':{'type':'string'},'data':{},'overwrite':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            if type(kw.get('overwrite',False)) is not bool:raise ValueError('Strict overwrite boolean')
            if action in ('show_ui','read_settings','write_settings'):storage.root(kw.get('data_root'))
            if action.startswith('read_') or action.startswith('write_'):
                p=storage.root(kw['data_root'])/'Maya-Tabs.ini' if action.endswith('settings') else storage.path(kw.get('path'))
                if action.startswith('read_'):storage.read(str(p))
                else:
                    storage.payload(p,kw.get('data'))
                    if not p.parent.is_dir() or p.exists() and not kw.get('overwrite'):raise ValueError('Existing output requires explicit overwrite')
            return ToolResult.ok(message='无Qt/授权读取/回调/scene/file写入的预检')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'themes':len(list((Path(__file__).parent/'resources/Themes').glob('*.mttheme'))),'license_gate':'retained','original_version_gate':'2014-2023 allowlist retained; newer GUI acceptance pending','gui_acceptance':'not_run'})
        if action.startswith('read_') or action.startswith('write_'):
            p=storage.root(kw['data_root'])/'Maya-Tabs.ini' if action.endswith('settings') else storage.path(kw['path'])
            return ToolResult.ok(data={'value':storage.read(str(p))}) if action.startswith('read_') else ToolResult.ok(data=storage.write(str(p),kw['data'],kw.get('overwrite',False)))
        from . import session
        if action=='show_ui':session.show(kw['data_root']);return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if session.window is None:raise RuntimeError('Open licensed owned toolbar first')
        session.native.guiMayaTabs();return ToolResult.ok()
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=3,caption='Maya Tabs：选择独立配置/授权状态目录')
        if not values:return None
        from .session import show
        return show(values[0])
