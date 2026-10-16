"""Thin adapter to the unmodified AdvancedSkeleton Mirror procedure."""
from maya_toolkit.framework import BaseMayaTool, ToolResult
from . import runtime


class AdvancedSkeletonMirrorTool(BaseMayaTool):
    tool_id = 'advanced_skeleton_mirror'
    tool_name = 'ADV 原生 Mirror'
    category = 'animation'
    version = '1.0.0'
    description = ('直接调用 AdvancedSkeleton 自带 Mirror，无额外配对表或镜像算法。'
                   '支持当前姿态、原生选项窗口及无动画层角色的逐帧动画镜像。')
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'action': {'type': 'string', 'enum': ['mirror', 'mirror_animation', 'open_options'], 'default': 'mirror'},
            'namespace': {'type': 'string', 'description': '角色命名空间；省略时从选择或唯一 ControlSet 识别。'},
            'source_path': {'type': 'string', 'description': '本机原版 AdvancedSkeleton.mel；省略读取本工具已配置路径或当前加载来源。'},
            'side': {'type': 'string', 'enum': ['swap', 'left_to_right', 'right_to_left'], 'default': 'swap'},
            'axis': {'type': 'string', 'enum': ['X', 'Y', 'Z'], 'default': 'X'},
            'space': {'type': 'string', 'enum': ['world', 'main', 'root'], 'default': 'main'},
            'time_range': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2,
                           'description': '仅 mirror_animation，包含首尾帧，省略使用播放范围。'},
        },
    }

    def validate(self, **kwargs):
        try:
            plan = runtime.preflight(**kwargs)
            return ToolResult.ok('ADV 原生 Mirror 预检通过', data=plan,
                                 warnings=['Mirror 的配对和轴向由 ADV 原版处理；原生跳过的控制器不会额外补算。'])
        except (ValueError, RuntimeError, OSError) as exc:
            return ToolResult.fail(str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        return ToolResult.ok('ADV 原生 Mirror 调用完成', data=runtime.execute(**kwargs))

    def show_ui(self, parent=None):
        from .ui import show
        return show(self)
