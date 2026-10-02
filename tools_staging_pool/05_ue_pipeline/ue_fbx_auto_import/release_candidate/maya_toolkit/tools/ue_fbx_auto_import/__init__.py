"""Maya configuration generator only. UE importing lives in engine_toolkit."""
from pathlib import Path
from maya_toolkit.framework import BaseMayaTool, ToolResult
from engine_toolkit.tools.ue_fbx_auto_import import config as c

class UEFbxAutoImportTool(BaseMayaTool):
    tool_id = 'ue_fbx_auto_import'
    tool_name = 'UE FBX 动画配置生成器'
    category = 'engine_bridge'
    description = 'Maya配置生成窗口与纯文件API；不在Maya执行UE资产导入'
    parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
        'action': {'type': 'string', 'enum': ['inspect_config', 'generate_config', 'detect_paths', 'show_ui'], 'default': 'inspect_config'},
        'config': {'type': 'object'}, 'output_dir': {'type': 'string'}, 'root_path': {'type': 'string'}}}
    def plan(self, **kwargs):
        if set(kwargs) - set(self.parameters_schema['properties']): raise ValueError('Unknown parameters')
        action = kwargs.get('action', 'inspect_config')
        if action not in self.parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
        if action == 'show_ui':
            from maya import cmds
            if cmds.about(batch=True): raise ValueError('UI requires interactive Maya')
            return {'action': action}
        if action == 'detect_paths':
            root = kwargs.get('root_path', ''); anim, skeleton = c.find_target_paths(root)
            return {'action': action, 'anim_paths': [c.convert_to_ue_path(p, c.content_root(root)) for p in anim], 'skeleton_paths': [c.convert_to_ue_path(p, c.content_root(root)) for p in skeleton]}
        plan = c.check_config(kwargs.get('config'))
        if action == 'generate_config':
            directory = Path(kwargs.get('output_dir') or (Path.home() / 'Desktop/FBX_Configs')).resolve()
            if directory.exists() and not directory.is_dir(): raise ValueError('Output directory is a file')
            plan['output_dir'] = str(directory)
        return {'action': action, **plan}
    def validate(self, **kwargs):
        try: return ToolResult.ok(message='配置预检通过；不写文件、不导入UE资产', data=self.plan(**kwargs), dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e), errors=[str(e)], dry_run=True)
    def execute(self, **kwargs):
        plan = self.plan(**kwargs)
        if plan['action'] == 'generate_config': return ToolResult.ok(message='已独占生成新JSON；文件不受Maya Undo撤销', data=c.generate_config(plan['config'], plan['output_dir']))
        if plan['action'] == 'show_ui': self.show_ui(); return ToolResult.ok(message='配置窗口已打开')
        return ToolResult.ok(message='配置查询完成', data=plan)
    def show_ui(self):
        from .ui import show_fbx_config_generator
        return show_fbx_config_generator()
