from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .settings import SCHEMA, normalize


class OverslapperTool(BaseMayaTool):
    tool_id = 'overslapper'
    tool_name = 'Overslapper 延迟与风控'
    category = 'animation'
    version = '1.0.3-candidate.1'
    description = '完整旋转/平移延迟、分组刚度、循环、动画层、过冲与风控。真实 Maya 验收前仅为候选。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过', data=prepare(normalize(**kwargs)), dry_run=True)
        except Exception as error:
            return ToolResult.fail('Overslapper 预检失败', errors=str(error), dry_run=True)

    def execute(self, **kwargs):
        try:
            from .runtime import execute, prepare
            options = normalize(**kwargs)
            return execute(options, prepare(options))
        except Exception as error:
            return ToolResult.fail('Overslapper 执行失败；场景写入可用一次 Undo 撤回', errors=str(error))

    def show_ui(self, parent=None):
        return self.run(action='open_ui')
