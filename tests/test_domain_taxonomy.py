# -*- coding: utf-8 -*-
"""
单元测试：6 大业务领域分类体系 (Domain Taxonomy) 与分片导出验证
"""
from __future__ import absolute_import, division, print_function

import os
import sys
import unittest

# 将项目根目录加入 sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import maya_toolkit
from maya_toolkit.framework import (
    ToolDomain,
    TOOL_DOMAINS,
    get_domain_info,
    list_domains,
    ToolRegistry,
)


class TestDomainTaxonomy(unittest.TestCase):
    """测试领域常量与工具分类契约"""

    def test_domains_constant_definition(self):
        """测试 6 大核心领域常量完整性"""
        expected_keys = {
            "animation",
            "rigging",
            "modeling_surfacing",
            "pipeline_io",
            "scene_hygiene",
            "engine_bridge",
        }
        self.assertEqual(set(TOOL_DOMAINS.keys()), expected_keys)
        self.assertEqual(len(list_domains()), 6)

        # 检查排序
        orders = [d["order"] for d in list_domains()]
        self.assertEqual(orders, sorted(orders))

    def test_get_domain_info_fallback(self):
        """测试未知领域的回退机制与旧别名兼容"""
        info_pipe = get_domain_info("pipeline")
        self.assertEqual(info_pipe["id"], ToolDomain.PIPELINE_IO)

        info_unknown = get_domain_info("unclassified_future_stuff")
        self.assertEqual(info_unknown["order"], 99)

    def test_registered_tools_belong_to_valid_domains(self):
        """测试所有内置注册的工具其 category 必须是 6 大标准领域之一"""
        valid_domain_keys = set(TOOL_DOMAINS.keys())
        all_tools = ToolRegistry.list_tools()
        self.assertGreaterEqual(len(all_tools), 6)

        for tool_meta in all_tools:
            cat = tool_meta["category"]
            self.assertIn(
                cat,
                valid_domain_keys,
                "工具 [{}] 的 category '{}' 不属于 6 大业务领域之一！".format(tool_meta["tool_id"], cat)
            )

    def test_list_tools_by_domain_filtering(self):
        """测试按领域过滤工具列表"""
        anim_tools = ToolRegistry.list_tools(domain=ToolDomain.ANIMATION)
        self.assertTrue(any(t["tool_id"] == "fix_rotation_winding" for t in anim_tools))
        # 不应包含 rigging 工具
        self.assertFalse(any(t["tool_id"] == "copy_overlapping_weights" for t in anim_tools))

        rig_tools = ToolRegistry.list_tools(domain=ToolDomain.RIGGING)
        self.assertTrue(any(t["tool_id"] == "copy_overlapping_weights" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "base_overrig_v9_0" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "batch_skin_bind" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "bb_tools" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "constraint_manager_v6" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "hierarchy_analyzer" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "joint_optimal_pro_v4_1" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "rdm_tools_v2" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "relationship_tools_v19" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "reparent_pro_v1_5_1" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "segment_scale_fix" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "skeleton_generator" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "skin_info_and_super_connect" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "skin_magic" for t in rig_tools))
        self.assertTrue(any(t["tool_id"] == "skin_weight_transfer" for t in rig_tools))

        model_tools = ToolRegistry.list_tools(domain=ToolDomain.MODELING_SURFACING)
        self.assertTrue(any(t["tool_id"] == "camera_f_fix" for t in model_tools))
        self.assertTrue(any(t["tool_id"] == "cvwrap_weightdriver" for t in model_tools))

    def test_domains_summary(self):
        """测试 list_domains_summary 的统计完整性"""
        summary = ToolRegistry.list_domains_summary()
        self.assertEqual(len(summary), 6)

        total_counted = sum(d["tool_count"] for d in summary)
        total_registered = len(ToolRegistry.list_tools())
        self.assertEqual(total_counted, total_registered)

    def test_export_tool_schemas_with_domain_filtering(self):
        """测试按领域分片导出 OpenAI 与 MCP Schema"""
        # 全部导出
        all_openai = maya_toolkit.export_tool_schemas("openai")
        self.assertEqual(len(all_openai), len(ToolRegistry.list_tools()))

        # 仅导出 animation
        anim_openai = maya_toolkit.export_tool_schemas("openai", domain=ToolDomain.ANIMATION)
        self.assertEqual({t["function"]["name"] for t in anim_openai},
                         {"fix_rotation_winding", "advanced_skeleton_mirror", "advanced_skeleton_animation", "stagger_offset", "stagger_gui", "bh_wave_it", "bh_local_nudge", "keyframe_overlap", "back2origin_v05_gaiv3", "animirror_v2_0", "gimbal_lock_fix", "anim_filters", "tweener_v1_0_2", "root_motion_bake", "copy_animation", "shift_animation_v3_2", "overslapper", "spring_magic_v3_5a", "cg_shake_py3", "directional_cycle_tool_v1_1", "retime_tools", "dof_control_v1_0", "eblabs_screenspace", "eblabs_whiskey", "anim_layer_bookmark_trimmer", "anim_layer_keyframe_bookmark", "anim_layer_key_runner", "anim_layer_v4_0", "anim_mirror_helper_v1_1", "anim_polish_premium_v1_23", "animation_retarget", "bh_aim_tools_v1_1", "bh_speedlines", "brs_loc_transfer", "brs_smooth_mocap", "fd_multi_space", "ik_fk_switch", "jop_retarget_anim", "kf_animrig_ikfk", "lock_to_world", "keyframe_reduction", "timeline_marker", "mov_playblast", "physics_tools", "pose_matcher", "pose_transfer_remote", "shape_animation_tool", "sword_anim_polishing_tool_v4", "tb_anim_tools", "timeline_enhanced", "velocity_calculator", "w_retarget_tool"})

        # 仅导出 pipeline_io
        pipe_mcp = maya_toolkit.export_tool_schemas("mcp", domain=ToolDomain.PIPELINE_IO)
        self.assertEqual(len(pipe_mcp), 2)
        pipe_names = {t["name"] for t in pipe_mcp}
        self.assertEqual(pipe_names, {"compare_and_sync_fbx", "export_sets_to_fbx"})


if __name__ == "__main__":
    unittest.main()
