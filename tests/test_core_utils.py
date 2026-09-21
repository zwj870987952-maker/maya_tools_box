# -*- coding: utf-8 -*-
"""
单元测试：core 字符串工具与通用公共函数测试
"""
from __future__ import absolute_import, division, print_function

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from maya_toolkit.core.string_utils import natural_sort_key, sanitize_node_name, format_markdown_table


class TestCoreUtils(unittest.TestCase):

    def test_natural_sort_key(self):
        raw_list = ["mesh_10", "mesh_1", "mesh_2", "mesh_20", "mesh_3"]
        sorted_list = sorted(raw_list, key=natural_sort_key)
        expected = ["mesh_1", "mesh_2", "mesh_3", "mesh_10", "mesh_20"]
        self.assertEqual(sorted_list, expected)

    def test_sanitize_node_name(self):
        self.assertEqual(sanitize_node_name("My Node Name!"), "My_Node_Name")
        self.assertEqual(sanitize_node_name("123_invalid_start"), "_123_invalid_start")
        self.assertEqual(sanitize_node_name("valid_name_01"), "valid_name_01")
        self.assertEqual(sanitize_node_name(""), "unnamed_node")

    def test_format_markdown_table(self):
        headers = ["Asset", "Status", "Faces"]
        rows = [
            ["Hero_Mesh", "Matched", "2048"],
            ["Weapon", "Diff", "512"]
        ]
        table = format_markdown_table(headers, rows)
        self.assertIn("| Asset", table)
        self.assertIn("| Hero_Mesh", table)
        self.assertIn("| Weapon", table)


if __name__ == "__main__":
    unittest.main()
