# -*- coding: utf-8 -*-
"""
动画欧拉角 360 度异常跳变修正工具：标准 Tool 实现类
"""
from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False

from ...framework.base_tool import BaseMayaTool
from ...framework.models import ToolResult
from .engine import scan_rotation_winding_issues, fix_rotation_winding_on_nodes


class EulerWindingTool(BaseMayaTool):
    """
    动画欧拉角 360 度异常跳变修正工具：
    自动识别并消除控制器在制作、Euler Flip、动捕解算、烘焙或外部导入时
    因数值突增突减 360 度整数倍而导致的空转与插值阶跃。
    """

    tool_id = "fix_rotation_winding"
    tool_name = "欧拉旋转360度跳变修正工具"
    category = "Animation"
    version = "1.2.0"
    description = (
        "自动扫描并修复 Maya 控制器动画曲线上因 360 度整数倍异常增加或减少导致的旋转空转与插值跳变。"
        "支持指定节点、指定旋转轴、自定义容差和时间段范围，严格保留切线类型。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "nodes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要检测和修复的控制器/骨骼 Transform 节点列表。若未传则默认处理视口当前选中的物体。"
            },
            "channels": {
                "type": "array",
                "items": {"type": "string", "enum": ["rotateX", "rotateY", "rotateZ"]},
                "default": ["rotateX", "rotateY", "rotateZ"],
                "description": "需要扫描和修正的旋转通道轴向。"
            },
            "tolerance": {
                "type": "number",
                "default": 90.0,
                "description": "判定是否为 360 度倍数跳变的容差阈值（度），默认 90.0°。"
            },
            "time_range": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 2,
                "maxItems": 2,
                "description": "限制检测的关键帧时间范围 [start_frame, end_frame]，不填则处理整条曲线。"
            }
        },
        "required": [],
        "additionalProperties": False
    }

    def validate(self, nodes=None, channels=None, tolerance=90.0, time_range=None, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        target_nodes = nodes
        if not target_nodes:
            target_nodes = cmds.ls(selection=True, type="transform") or []
            if not target_nodes:
                return ToolResult.fail("未指定 target nodes，且场景中未选中任何 Transform 物体。")

        missing = [n for n in target_nodes if not cmds.objExists(n)]
        if missing:
            return ToolResult.fail("以下节点在当前场景中不存在: {}".format(missing[:5]), errors=missing)

        # 预检扫描跳变点
        jumps = scan_rotation_winding_issues(
            nodes=target_nodes,
            channels=channels,
            tolerance=tolerance,
            time_range=time_range
        )
        return ToolResult.ok(
            message="预检扫描完成，检测到 {} 个异常 360 度跳变点。".format(len(jumps)),
            data={
                "target_nodes": target_nodes,
                "detected_jumps_count": len(jumps),
                "jumps": [j.to_dict() for j in jumps[:20]]
            }
        )

    def execute(self, nodes=None, channels=None, tolerance=90.0, time_range=None, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        target_nodes = nodes
        if not target_nodes:
            target_nodes = cmds.ls(selection=True, type="transform") or []

        stats = fix_rotation_winding_on_nodes(
            nodes=target_nodes,
            channels=channels,
            tolerance=tolerance,
            time_range=time_range
        )
        msg = "成功修正 {} 条动画曲线，平滑对齐 {} 处跳变点，重映射 {} 个关键帧数值。".format(
            stats.get("modified_curves", 0),
            stats.get("jump_events_count", 0),
            stats.get("fixed_keys_count", 0)
        )
        return ToolResult.ok(message=msg, data=stats)

    def show_ui(self, parent=None):
        import fix_rotation_winding
        try:
            return fix_rotation_winding.show_ui(parent=parent)
        except TypeError:
            return fix_rotation_winding.show_ui()
