import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import SCHEMA
from .engine import plan


class Back2OriginTool(BaseMayaTool):
    tool_id = 'back2origin_v05_gaiv3'
    tool_name = 'Back2Origin 根运动转换'
    category = 'animation'
    version = '0.5.1-adapter'
    description = '完整原 X/Z 根运动转换、反向操作、控制器发现及原生界面；保留原局部/世界坐标约定。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'discover':
            from .engine import discover
            return ToolResult.ok(data=discover(args['namespace']))
        if args['action'] == 'open_ui':
            from . import native_ui
            native_ui.show_back2origin_ui()
            return ToolResult.ok(data={'window': 'mtbB2O_back2OriginWindow'})
        from .engine import execute
        data = execute(args)
        return ToolResult.ok(message='Back2Origin 操作完成', data=data, warnings=data['warnings'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
