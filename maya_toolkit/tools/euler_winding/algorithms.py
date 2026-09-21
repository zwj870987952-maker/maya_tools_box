# -*- coding: utf-8 -*-
"""
欧拉角旋转跳变数学与检测算法（纯 Python，独立可测，零 Maya 依赖）。
"""
from __future__ import absolute_import, division, print_function

import math


class RotationJumpEvent(object):
    """记录检测到的单个 360 度异常跳变点信息"""

    def __init__(
        self,
        node,
        attribute,
        curve,
        key_index,
        time,
        prev_time,
        old_val,
        prev_val,
        delta,
        k,
        correction,
    ):
        self.node = node
        self.attribute = attribute
        self.curve = curve
        self.key_index = key_index
        self.time = time
        self.prev_time = prev_time
        self.old_val = old_val
        self.prev_val = prev_val
        self.delta = delta
        self.k = k
        self.correction = correction

    def to_dict(self):
        return {
            "node": self.node,
            "attribute": self.attribute,
            "curve": self.curve,
            "key_index": self.key_index,
            "time": self.time,
            "prev_time": self.prev_time,
            "old_val": self.old_val,
            "prev_val": self.prev_val,
            "delta": self.delta,
            "k": self.k,
            "correction": self.correction,
        }

    def __repr__(self):
        return (
            "<JumpEvent node={self.node} attr={self.attribute} "
            "frame={self.time} delta={self.delta:.1f}° k={self.k} fix={self.correction:+.1f}°>".format(
                self=self
            )
        )


def detect_and_unwind_sequence(times, values, tolerance=90.0, max_time_gap=None):
    """
    对有序的关键帧时间序列和旋转数值进行连续欧拉解包（Cumulative Unwind），
    识别并消除相邻关键帧之间接近 ±360° * k 的多余插值阶跃。

    参数：
        times (list[float]): 升序排列的关键帧时间列表
        values (list[float]): 对应的原始旋转角度值列表
        tolerance (float): 容差阈值（度），默认 90.0°。判定条件：|diff - 360*k| <= tolerance
        max_time_gap (float or None): 判定跳变的最大两帧时间跨度限制。若超过此跨度则不视作突发跳变

    返回：
        tuple: (fixed_values, jump_events)
    """
    n = len(values)
    if n <= 1:
        return list(values), []

    fixed_values = list(values)
    jump_events = []

    cumulative_offset = 0.0
    prev_fixed_val = values[0]

    for i in range(1, n):
        t_curr = times[i]
        t_prev = times[i - 1]
        raw_val = values[i]

        if max_time_gap is not None and (t_curr - t_prev) > max_time_gap:
            v_fixed = raw_val + cumulative_offset
            fixed_values[i] = v_fixed
            prev_fixed_val = v_fixed
            continue

        v_tentative = raw_val + cumulative_offset
        diff = v_tentative - prev_fixed_val

        k = int(round(diff / 360.0))

        if k != 0:
            residual = abs(diff - 360.0 * k)
            if residual <= tolerance:
                step_correction = -360.0 * k
                cumulative_offset += step_correction
                v_tentative += step_correction

                jump_events.append({
                    "key_index": i,
                    "time": t_curr,
                    "prev_time": t_prev,
                    "old_val": raw_val,
                    "prev_val": values[i - 1],
                    "delta": diff,
                    "k": k,
                    "correction": step_correction,
                    "cumulative_offset_after": cumulative_offset,
                })

        fixed_values[i] = v_tentative
        prev_fixed_val = v_tentative

    return fixed_values, jump_events


def normalize_sequence_baseline(values, target_range="[-180, 180]"):
    """
    将整个数值序列整体偏移 360° 的整数倍，使其基准落入目标主值区间，同时完全保留原有曲线形状。
    """
    if not values:
        return [], 0.0

    ref_val = values[0]

    if target_range == "[0, 360]":
        k = int(math.floor(ref_val / 360.0))
        offset = -360.0 * k
    else:  # "[-180, 180]"
        k = int(round(ref_val / 360.0))
        offset = -360.0 * k

    if abs(offset) < 1e-4:
        return list(values), 0.0

    return [v + offset for v in values], offset
