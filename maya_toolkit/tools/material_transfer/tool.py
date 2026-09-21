# -*- coding: utf-8 -*-
"""
双列表按行一对一材质传递工具：标准 Tool 实现类
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
from ...core.maya_utils import resolve_selected_meshes


class MaterialTransferTool(BaseMayaTool):
    """
    双列表按行一对一材质指定工具：
    将源物体列表（A）的材质分配严格按顺序赋予给目标物体列表（B）。
    支持整物材质指定、分面多材质匹配以及拓扑面数不一致时的安全降级回退。
    """

    tool_id = "assign_materials_by_rows"
    tool_name = "按行一对一材质指定工具"
    category = "Modeling"
    version = "1.2.0"
    description = (
        "将源网格列表 (A) 的材质球与分面指派严格按列表顺序一对一赋予给目标网格列表 (B)。"
        "支持传入父级组（自动依序解析出所有网格），支持分面材质保护与拓扑不一致时的安全降级回退。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "source_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "源模型或组节点列表（提供材质来源）。"
            },
            "target_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "目标模型或组节点列表（接收材质指定）。"
            },
            "transfer_face_assignments": {
                "type": "boolean",
                "default": True,
                "description": "是否传递分面多材质（若目标面数不一致将自动降级）。"
            },
            "fallback_on_topology_mismatch": {
                "type": "boolean",
                "default": True,
                "description": "若拓扑面数不一致，是否安全降级为整物赋予源主材质（默认 True）。"
            }
        },
        "required": ["source_list", "target_list"],
        "additionalProperties": False
    }

    def validate(self, source_list, target_list, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        if not source_list or not target_list:
            return ToolResult.fail("必须同时提供 source_list 和 target_list 列表！")

        resolved_src = resolve_selected_meshes(source_list)
        resolved_tgt = resolve_selected_meshes(target_list)

        if not resolved_src:
            return ToolResult.fail("源列表解析后未找到任何有效的 Mesh 网格节点！")
        if not resolved_tgt:
            return ToolResult.fail("目标列表解析后未找到任何有效的 Mesh 网格节点！")

        warnings = []
        if len(resolved_src) != len(resolved_tgt):
            warnings.append(
                "源网格数量 ({}) 与目标网格数量 ({}) 不一致！多余的部分将被忽略。".format(
                    len(resolved_src), len(resolved_tgt)
                )
            )

        return ToolResult.ok(
            message="预检通过，解析出 {} 个源网格和 {} 个目标网格。".format(
                len(resolved_src), len(resolved_tgt)
            ),
            data={
                "resolved_source_count": len(resolved_src),
                "resolved_target_count": len(resolved_tgt),
                "source_meshes": resolved_src[:10],
                "target_meshes": resolved_tgt[:10]
            },
            warnings=warnings
        )

    def execute(self, source_list, target_list, transfer_face_assignments=True, fallback_on_topology_mismatch=True, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        # 调用经过生产验证的无头 API
        import assign_materials_between_groups as mat_module
        raw_result = mat_module.transfer_materials_by_rows(
            source_list=source_list,
            target_list=target_list,
            transfer_face_assignments=transfer_face_assignments,
            fallback_on_topology_mismatch=fallback_on_topology_mismatch
        )

        success_count = raw_result.get("success", 0)
        downgraded_count = raw_result.get("downgraded", 0)
        failed_count = raw_result.get("failed", 0)
        skipped_count = raw_result.get("skipped", 0)

        msg = "材质传递完成: 成功 {}, 降级 {}, 失败 {}, 跳过 {}。".format(
            success_count, downgraded_count, failed_count, skipped_count
        )
        has_errors = failed_count > 0

        return ToolResult(
            success=(not has_errors or success_count > 0),
            message=msg,
            data=raw_result,
            warnings=["存在失败项，请检查 data.details"] if has_errors else []
        )

    def show_ui(self, parent=None):
        import assign_materials_between_groups as mat_module
        return mat_module.show_ui()
