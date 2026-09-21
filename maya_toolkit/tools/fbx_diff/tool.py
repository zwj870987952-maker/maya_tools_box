# -*- coding: utf-8 -*-
"""
外部 FBX 资产深度比对与差异同步工具：标准 Tool 实现类
"""
from __future__ import absolute_import, division, print_function

import os

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False

from ...framework.base_tool import BaseMayaTool
from ...framework.models import ToolResult


class FBXDiffSyncTool(BaseMayaTool):
    """
    外部 FBX 资产深度比对与差异同步工具：
    通过纯内存读取外部 FBX 资产，比对当前 Maya 场景同名网格的拓扑几何、材质分面与空间变换，
    并支持差异精准同步与修复。
    """

    tool_id = "compare_and_sync_fbx"
    tool_name = "FBX外部资产深度比对与同步工具"
    category = "Pipeline"
    version = "1.3.0"
    description = (
        "纯内存直接解析外部 FBX 文件（零场景几何污染），与 Maya 场景中同名模型进行"
        "拓扑面数、UV集、材质网络、分面映射与空间位姿 (T/R/S) 的深度对比，"
        "并支持选择性一键同步材质分面或空间变换对齐。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "fbx_path": {
                "type": "string",
                "description": "要比对的外部 FBX 文件的绝对路径。"
            },
            "action": {
                "type": "string",
                "enum": ["diff_only", "sync_materials", "sync_transforms", "sync_all"],
                "default": "diff_only",
                "description": "执行动作：'diff_only' (仅比对并输出差异报告), 'sync_materials' (同步材质), 'sync_transforms' (同步位姿), 'sync_all' (全部同步)。"
            },
            "match_by_short_name": {
                "type": "boolean",
                "default": True,
                "description": "是否允许使用短名称匹配（忽略命名空间与长路径）。"
            },
            "case_insensitive": {
                "type": "boolean",
                "default": False,
                "description": "名称匹配时是否忽略大小写。"
            },
            "target_assets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "指定要同步的资产名称列表。若为空则作用于所有检测到差异的资产。"
            }
        },
        "required": ["fbx_path"],
        "additionalProperties": False
    }

    def validate(self, fbx_path, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        if not fbx_path or not os.path.isfile(fbx_path):
            return ToolResult.fail("指定的外部 FBX 文件不存在: [{}]".format(fbx_path))

        if not fbx_path.lower().endswith(".fbx"):
            return ToolResult.fail("输入的文件不是有效的 .fbx 文件: [{}]".format(fbx_path))

        # 检查 FBX SDK
        import compare_and_sync_fbx_assets as diff_mod
        if not diff_mod.FBXSDKManager.is_sdk_available():
            return ToolResult.fail("当前环境未检测到可用的 Autodesk FBX SDK 模块。")

        return ToolResult.ok(
            message="FBX 文件合法且 FBX SDK 已就绪。",
            data={"fbx_path": fbx_path}
        )

    def execute(self, fbx_path, action="diff_only", match_by_short_name=True, case_insensitive=False, target_assets=None, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        import compare_and_sync_fbx_assets as diff_mod

        # 1. 内存解析外部 FBX
        parsed_data = diff_mod.FBXSDKParser.parse_file(fbx_path)
        fbx_meshes = parsed_data.get("meshes", [])
        if not fbx_meshes:
            return ToolResult.fail("外部 FBX 中未找到任何可比对的有效 Mesh 网格资产。")

        # 2. 扫描场景
        scene_records = diff_mod.SceneMeshInspector.inspect_all_scene_meshes()

        # 3. 比对全维度属性
        diff_options = {
            "match_by_short_name": match_by_short_name,
            "case_insensitive": case_insensitive,
            "compare_transforms": True
        }
        diff_results = diff_mod.AssetDiffComparator.compare(parsed_data, scene_records, options=diff_options)

        # 整理比对摘要
        summary = {
            "total_compared": len(diff_results),
            "identical": 0,
            "material_diff": 0,
            "transform_diff": 0,
            "topology_diff": 0,
            "missing_in_maya": 0,
            "missing_in_fbx": 0
        }
        for item in diff_results:
            st = item.get("status")
            if st == diff_mod.AssetDiffStatus.IDENTICAL:
                summary["identical"] += 1
            elif st == diff_mod.AssetDiffStatus.MATERIAL_DIFF:
                summary["material_diff"] += 1
            elif st == diff_mod.AssetDiffStatus.TRANSFORM_DIFF:
                summary["transform_diff"] += 1
            elif st == diff_mod.AssetDiffStatus.TOPOLOGY_DIFF:
                summary["topology_diff"] += 1
            elif st == diff_mod.AssetDiffStatus.MISSING_IN_MAYA:
                summary["missing_in_maya"] += 1
            elif st == diff_mod.AssetDiffStatus.MISSING_IN_FBX:
                summary["missing_in_fbx"] += 1

        # 若动作仅是 diff_only，直接返回差异结构
        if action == "diff_only":
            diff_list_clean = []
            for item in diff_results:
                diff_list_clean.append({
                    "name": item["name"],
                    "status": item["status"],
                    "status_label": item["status_label"],
                    "diff_details": item["diff_details"]
                })
            return ToolResult.ok(
                message="比对完成: 共 {} 个资产，完全吻合 {}，材质差异 {}，变换差异 {}，拓扑差异 {}。".format(
                    summary["total_compared"], summary["identical"], summary["material_diff"],
                    summary["transform_diff"], summary["topology_diff"]
                ),
                data={
                    "summary": summary,
                    "diff_items": diff_list_clean
                }
            )

        # 执行差异同步动作
        selected_items = diff_results
        if target_assets:
            target_set = set(target_assets)
            selected_items = [it for it in diff_results if it["name"] in target_set or it["clean_name"] in target_set]

        sync_counts = {"materials_synced": 0, "transforms_synced": 0}

        if action in ("sync_materials", "sync_all"):
            mat_cnt = diff_mod.AssetDiffSyncEngine.sync_materials(selected_items, options=diff_options)
            sync_counts["materials_synced"] = mat_cnt

        if action in ("sync_transforms", "sync_all"):
            trans_cnt = diff_mod.AssetDiffSyncEngine.sync_transforms(selected_items)
            sync_counts["transforms_synced"] = trans_cnt

        return ToolResult.ok(
            message="差异同步完成: 同步材质 {} 项，同步位姿 {} 项。".format(
                sync_counts["materials_synced"], sync_counts["transforms_synced"]
            ),
            data={
                "summary": summary,
                "sync_counts": sync_counts
            }
        )

    def show_ui(self, parent=None):
        import compare_and_sync_fbx_assets as diff_mod
        return diff_mod.show_ui(parent=parent)
