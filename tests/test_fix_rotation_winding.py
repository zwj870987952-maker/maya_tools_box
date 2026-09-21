# -*- coding: utf-8 -*-
"""
单元测试：fix_rotation_winding 模块
测试核心欧拉解包与 360 度异常跳变检测、平滑修正、规范化基准算法。
"""

import math
import os
import sys
import unittest

# 将项目根目录加入 sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fix_rotation_winding import (
    detect_and_unwind_sequence,
    normalize_sequence_baseline,
)


class TestRotationWindingAlgorithms(unittest.TestCase):
    """测试核心数学算法与解包逻辑"""

    def test_clean_sequence_no_jumps(self):
        """测试正常平稳动画曲线，不应误检出任何跳变"""
        times = [1.0, 2.0, 3.0, 4.0, 5.0]
        # 每帧转 10 度
        values = [0.0, 10.0, 20.0, 30.0, 40.0]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 0)
        self.assertEqual(fixed, values)

    def test_positive_step_jump_360(self):
        """测试正向 +360° 阶跃跳变：第 3 帧突然加了 360 度，之后都在 360 度基准上运动"""
        times = [1.0, 2.0, 3.0, 4.0, 5.0]
        values = [10.0, 15.0, 376.0, 380.0, 395.0]
        # 期望修正后：[10.0, 15.0, 16.0, 20.0, 35.0]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0]["time"], 3.0)
        self.assertEqual(jumps[0]["k"], 1)
        self.assertEqual(jumps[0]["correction"], -360.0)

        expected = [10.0, 15.0, 16.0, 20.0, 35.0]
        for f, exp in zip(fixed, expected):
            self.assertAlmostEqual(f, exp, places=4)

    def test_negative_step_jump_360(self):
        """测试负向 -360° 阶跃跳变"""
        times = [10.0, 20.0, 30.0, 40.0]
        values = [0.0, -5.0, -366.0, -370.0]
        # 期望修正后：[0.0, -5.0, -6.0, -10.0]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0]["time"], 30.0)
        self.assertEqual(jumps[0]["k"], -1)
        self.assertEqual(jumps[0]["correction"], 360.0)

        expected = [0.0, -5.0, -6.0, -10.0]
        for f, exp in zip(fixed, expected):
            self.assertAlmostEqual(f, exp, places=4)

    def test_multi_multiplier_step_jump_720(self):
        """测试多倍数跳变（例如 +720°）"""
        times = [1.0, 2.0, 3.0]
        values = [5.0, 726.0, 730.0]
        # 期望修正后：[5.0, 6.0, 10.0]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0]["k"], 2)
        self.assertEqual(jumps[0]["correction"], -720.0)

        expected = [5.0, 6.0, 10.0]
        for f, exp in zip(fixed, expected):
            self.assertAlmostEqual(f, exp, places=4)

    def test_spike_isolated_jump(self):
        """测试单帧突刺（Spike）：单帧突变为 +360°，下一帧立即跳回"""
        times = [1.0, 2.0, 3.0, 4.0, 5.0]
        values = [10.0, 15.0, 375.0, 18.0, 22.0]
        # 帧 3 从 15 变成 375 (+360)，帧 4 从 375 回到 18 (-360)
        # 期望修正后：[10.0, 15.0, 15.0, 18.0, 22.0]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 2)
        self.assertEqual(jumps[0]["k"], 1)
        self.assertEqual(jumps[1]["k"], -1)

        expected = [10.0, 15.0, 15.0, 18.0, 22.0]
        for f, exp in zip(fixed, expected):
            self.assertAlmostEqual(f, exp, places=4)

    def test_continuous_rotation_spin(self):
        """测试正常的多圈旋转动画（例如每帧旋转 20 度，30 帧转了 600 度），不应被误判"""
        times = [float(i) for i in range(1, 31)]
        values = [float(i * 20) for i in range(1, 31)]

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 0)
        self.assertEqual(fixed, values)

    def test_tolerance_filter(self):
        """测试容差过滤：差值若远离 360 的整数倍（例如差 200 度），不应视作 360 度倍数跳变"""
        times = [1.0, 2.0]
        values = [0.0, 200.0]  # round(200/360) = 1, residual = |200 - 360| = 160 > 90

        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0)
        self.assertEqual(len(jumps), 0)
        self.assertEqual(fixed, values)

    def test_max_time_gap(self):
        """测试最大时间跨度限制：两关键帧如果相隔太远，可选择忽略"""
        times = [1.0, 1000.0]
        values = [0.0, 360.0]

        # 限制跨度为 100 帧
        fixed, jumps = detect_and_unwind_sequence(times, values, tolerance=90.0, max_time_gap=100.0)
        self.assertEqual(len(jumps), 0)
        self.assertEqual(fixed, values)

    def test_baseline_normalization(self):
        """测试基准规范化"""
        # 整体在 720 度附近
        values = [725.0, 730.0, 735.0]

        # 规范化到 [-180, 180]
        norm_vals, offset = normalize_sequence_baseline(values, target_range="[-180, 180]")
        self.assertEqual(offset, -720.0)
        self.assertEqual(norm_vals, [5.0, 10.0, 15.0])

        # 负角度规范化
        neg_values = [-355.0, -350.0]
        norm_vals2, offset2 = normalize_sequence_baseline(neg_values, target_range="[0, 360]")
        self.assertEqual(offset2, 360.0)
        self.assertEqual(norm_vals2, [5.0, 10.0])


class MockMayaCmds(object):
    """模拟 Maya cmds 的关键帧和对象行为"""

    def __init__(self):
        self.nodes = {"ctrl1": {"rotateX": "ctrl1_rotateX", "rotateY": "ctrl1_rotateY"}}
        self.curves = {
            "ctrl1_rotateX": {
                "times": [1.0, 2.0, 3.0, 4.0],
                "values": [0.0, 5.0, 366.0, 370.0],
            },
            "ctrl1_rotateY": {
                "times": [1.0, 2.0, 3.0],
                "values": [10.0, 20.0, 30.0],
            }
        }
        self.undo_chunks = []
        self.selected = ["ctrl1"]

    def objExists(self, name):
        if "." in name:
            node, attr = name.split(".", 1)
            return node in self.nodes and attr in self.nodes[node]
        return name in self.nodes or name in self.curves

    def listConnections(self, plug, type=None, source=True, destination=False, **kwargs):
        if "." in plug:
            node, attr = plug.split(".", 1)
            if node in self.nodes and attr in self.nodes[node]:
                return [self.nodes[node][attr]]
        return []

    def keyframe(self, target, query=False, edit=False, **kwargs):
        if query:
            if target in self.curves:
                c = self.curves[target]
                if kwargs.get("timeChange"):
                    return list(c["times"])
                if kwargs.get("valueChange"):
                    if kwargs.get("time"):
                        t_range = kwargs["time"]
                        t_target = t_range[0]
                        for idx, t in enumerate(c["times"]):
                            if abs(t - t_target) < 1e-4:
                                return [c["values"][idx]]
                        return []
                    return list(c["values"])
            return []
        if edit:
            if target in self.curves:
                c = self.curves[target]
                if kwargs.get("valueChange") is not None:
                    new_val = kwargs["valueChange"]
                    if kwargs.get("relative"):
                        c["values"] = [v + new_val for v in c["values"]]
                    elif kwargs.get("time"):
                        t_range = kwargs["time"]
                        t_target = t_range[0]
                        for idx, t in enumerate(c["times"]):
                            if abs(t - t_target) < 1e-4:
                                c["values"][idx] = new_val

    def undoInfo(self, openChunk=False, closeChunk=False, chunkName=""):
        if openChunk:
            self.undo_chunks.append(chunkName)
        if closeChunk and self.undo_chunks:
            self.undo_chunks.pop()

    def ls(self, selection=False, **kwargs):
        if selection:
            return list(self.selected)
        return []


class TestMayaIntegrationWithMock(unittest.TestCase):
    """测试通过 Mock 与 Maya API / cmds 的闭环集成"""

    def setUp(self):
        import fix_rotation_winding
        self.original_maya_available = fix_rotation_winding.MAYA_AVAILABLE
        self.original_cmds = fix_rotation_winding.cmds

        self.mock_cmds = MockMayaCmds()
        fix_rotation_winding.MAYA_AVAILABLE = True
        fix_rotation_winding.cmds = self.mock_cmds

    def tearDown(self):
        import fix_rotation_winding
        fix_rotation_winding.MAYA_AVAILABLE = self.original_maya_available
        fix_rotation_winding.cmds = self.original_cmds

    def test_scan_issues(self):
        import fix_rotation_winding
        events = fix_rotation_winding.scan_rotation_winding_issues(
            nodes=["ctrl1"], channels=["rotateX", "rotateY"]
        )
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual(ev.node, "ctrl1")
        self.assertEqual(ev.attribute, "rotateX")
        self.assertEqual(ev.time, 3.0)
        self.assertEqual(ev.k, 1)
        self.assertEqual(ev.correction, -360.0)

    def test_fix_on_nodes(self):
        import fix_rotation_winding
        res = fix_rotation_winding.fix_rotation_winding_on_nodes(
            nodes=["ctrl1"], channels=["rotateX", "rotateY"]
        )
        self.assertEqual(res["modified_curves"], 1)
        self.assertEqual(res["jump_events_count"], 1)

        # 检查修复后的数值
        rx_values = self.mock_cmds.curves["ctrl1_rotateX"]["values"]
        # 原值为 [0.0, 5.0, 366.0, 370.0]，修复后应为 [0.0, 5.0, 6.0, 10.0]
        self.assertAlmostEqual(rx_values[0], 0.0)
        self.assertAlmostEqual(rx_values[1], 5.0)
        self.assertAlmostEqual(rx_values[2], 6.0)
        self.assertAlmostEqual(rx_values[3], 10.0)

        # rotateY 没有跳变，数值应保持不变
        ry_values = self.mock_cmds.curves["ctrl1_rotateY"]["values"]
        self.assertEqual(ry_values, [10.0, 20.0, 30.0])


if __name__ == "__main__":
    unittest.main()

