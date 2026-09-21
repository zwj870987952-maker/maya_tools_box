# -*- coding: utf-8 -*-
"""
单元测试：framework 核心模型、注册表与 Schema 导出测试
"""
from __future__ import absolute_import, division, print_function

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import maya_toolkit
from maya_toolkit.framework import ToolResult, BaseMayaTool, ToolRegistry, execute_tool, export_tool_schemas


class DummyMockTool(BaseMayaTool):
    tool_id = "mock_test_tool"
    tool_name = "测试模拟工具"
    category = "Testing"
    description = "用于单测的模拟工具"

    parameters_schema = {
        "type": "object",
        "properties": {
            "val": {"type": "integer"}
        },
        "required": ["val"]
    }

    def validate(self, val=None, **kwargs):
        if val is None or val < 0:
            return ToolResult.fail("val 必须为非负整数")
        return ToolResult.ok("校验通过")

    def execute(self, val=0, **kwargs):
        return ToolResult.ok("计算成功", data={"doubled": val * 2})


class TestFrameworkAndRegistry(unittest.TestCase):

    def setUp(self):
        # 注册 mock 工具
        ToolRegistry.register(DummyMockTool)

    def test_tool_result_ok(self):
        res = ToolResult.ok("成功消息", data={"key": 123})
        self.assertTrue(res.success)
        self.assertEqual(res.message, "成功消息")
        self.assertEqual(res.data["key"], 123)
        self.assertFalse(res.dry_run)
        d = res.to_dict()
        self.assertIn("success", d)

    def test_tool_result_fail(self):
        res = ToolResult.fail("失败消息", errors=["Err1"])
        self.assertFalse(res.success)
        self.assertEqual(len(res.errors), 1)

    def test_tool_registry_discovery(self):
        tools = ToolRegistry.list_tools()
        tool_ids = [t["tool_id"] for t in tools]
        self.assertIn("mock_test_tool", tool_ids)
        self.assertIn("clean_namespaces", tool_ids)
        self.assertIn("fix_rotation_winding", tool_ids)
        self.assertIn("copy_overlapping_weights", tool_ids)
        self.assertIn("export_sets_to_fbx", tool_ids)
        self.assertIn("assign_materials_by_rows", tool_ids)
        self.assertIn("compare_and_sync_fbx", tool_ids)

    def test_export_openai_and_mcp_schemas(self):
        openai_tools = export_tool_schemas("openai")
        self.assertTrue(len(openai_tools) >= 7)
        for t in openai_tools:
            self.assertEqual(t["type"], "function")
            self.assertIn("name", t["function"])
            self.assertIn("parameters", t["function"])

        mcp_tools = export_tool_schemas("mcp")
        self.assertTrue(len(mcp_tools) >= 7)
        for t in mcp_tools:
            self.assertIn("name", t)
            self.assertIn("inputSchema", t)

    def test_execute_tool_success_and_dry_run(self):
        # Dry-run 预检模式
        dry_res = execute_tool("mock_test_tool", {"val": 10}, dry_run=True)
        self.assertTrue(dry_res.success)
        self.assertTrue(dry_res.dry_run)

        # 真实执行模式
        exec_res = execute_tool("mock_test_tool", {"val": 10}, dry_run=False)
        self.assertTrue(exec_res.success)
        self.assertFalse(exec_res.dry_run)
        self.assertEqual(exec_res.data.get("doubled"), 20)

    def test_execute_tool_validation_failure(self):
        # 传入非法负数
        fail_res = execute_tool("mock_test_tool", {"val": -5})
        self.assertFalse(fail_res.success)
        self.assertIn("非负整数", fail_res.message)


if __name__ == "__main__":
    unittest.main()
