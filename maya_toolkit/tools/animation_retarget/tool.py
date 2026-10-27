"""Unified tool API. Importing this module does not import Qt or execute the source."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import SCHEMA, normalize
from . import operations


class AnimationRetargetTool(BaseMayaTool):
    tool_id = 'animation_retarget'
    tool_name = '动画重定向'
    category = 'animation'
    version = '1.0.0'
    description = '批量配对，保留偏移的 TRS 约束、按源关键帧复制数值、默认/智能烘焙、配置及姿态恢复。'
    parameters_schema = SCHEMA

    def _plan(self, action='align', pairs=None, start=None, end=None, smart=False, path='', **extra):
        return operations.plan(normalize(action, pairs, start, end, smart, path, **extra))

    def validate(self, **kwargs):
        try:
            args = self._plan(**kwargs)
            public = {key: value for key, value in args.items() if key != 'records'}
            if 'records' in args:
                public['record_count'] = len(args['records'])
            return ToolResult.ok(message='参数与对象预检通过；不创建约束、关键帧、信息节点或配置文件。', data=public, dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        data = operations.execute(self._plan(**kwargs))
        return ToolResult.ok(message='动画重定向操作完成', data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(parent)
