from maya_toolkit.framework import BaseMayaTool, ToolResult
from . import engine
from .catalog import OPERATIONS


class AdvancedSkeletonAnimationTool(BaseMayaTool):
    tool_id = 'advanced_skeleton_animation'
    tool_name = 'ADV 动画工具'
    category = 'animation'
    version = '1.0.0'
    description = '自动发现本机最新 ADV，调用原版动画功能；区分直接操作、原生交互窗口及确认对话框。catalog 返回逐入口条件和验证状态。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'operation': {'type': 'string', 'enum': ['catalog', 'status'] + list(OPERATIONS), 'default': 'catalog'},
            'namespace': {'type': 'string'},
            'nodes': {'type': 'array', 'items': {'type': 'string'}, 'description': '明确的有序选择；省略使用当前选择。'},
            'limb': {'type': 'string', 'description': 'FKIK 肢体，例如 Arm_L。'},
            'time_range': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2},
            'control_set': {'type': 'string', 'enum': ['ControlSet', 'FaceControlSet'], 'default': 'ControlSet'},
            'source_path': {'type': 'string', 'description': '省略自动发现本机最新安装；指定路径覆盖自动选择。'},
            'accept_undo_history_loss': {'type': 'boolean', 'default': False, 'description': '仅粘贴：明确接受 ADV 临时文件引用会清空 Maya Undo 历史。'},
        },
    }

    def validate(self, **kwargs):
        try:
            return ToolResult.ok('ADV 动画入口预检通过', data=engine.preflight(**kwargs))
        except (ValueError, TypeError, RuntimeError, OSError) as exc:
            return ToolResult.fail(str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        data = engine.execute(**kwargs)
        return ToolResult.ok('ADV 入口返回：' + data['state'], data=data)

    def show_ui(self, parent=None):
        from .ui import show
        return show(self)
