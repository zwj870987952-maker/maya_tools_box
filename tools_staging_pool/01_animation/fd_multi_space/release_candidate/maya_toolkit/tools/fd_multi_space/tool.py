import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


class MultiSpaceTool(BaseMayaTool):
    tool_id = 'fd_multi_space'
    tool_name = 'FD Multi Space双模式'
    category = 'animation'
    version = '2023-candidate.1'
    description = '保留local插组/既有父级reference两算法与三步UI，明确权重alias与可恢复UUID记录，拒绝覆盖驱动。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            args = normalize(**kwargs)
            if args['action'] != 'records':
                from .scene import plan
                args = plan(args)
            return ToolResult.ok(data=args, dry_run=True, message='只读层级/引用编辑/驱动/target/alias预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .scene import plan
        from .runtime import execute
        args = plan(normalize(**kwargs))
        data = execute(args)
        warnings = ['local改变DAG层级，reference可能写入明确允许的引用编辑；create/每个三步动作各自Undo，不自动回滚失败']
        return ToolResult.ok(data=data, warnings=warnings)

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data

    def inventory(self):
        return json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8'))
