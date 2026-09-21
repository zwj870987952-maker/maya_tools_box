# -*- coding: utf-8 -*-
"""
单元测试：测试各个工具的 show_ui() 接口在 Maya GUI / 自动化环境下的调用可用性
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


class TestToolUiLaunch(unittest.TestCase):

    def test_launcher_show_ui_callable(self):
        self.assertTrue(callable(maya_toolkit.show_ui))

    def test_tools_show_ui_callable(self):
        tool_ids = [
            "clean_namespaces",
            "fix_rotation_winding",
            "copy_overlapping_weights",
            "export_sets_to_fbx",
            "assign_materials_by_rows",
            "compare_and_sync_fbx",
        ]
        for tid in tool_ids:
            tool = maya_toolkit.ToolRegistry.get(tid)
            self.assertIsNotNone(tool, "Tool [{}] not found".format(tid))
            self.assertTrue(callable(tool.show_ui), "Tool [{}] show_ui not callable".format(tid))


if __name__ == "__main__":
    unittest.main()
