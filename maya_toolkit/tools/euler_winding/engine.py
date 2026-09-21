# -*- coding: utf-8 -*-
"""
欧拉角旋转跳变 Maya 场景交互引擎。
"""
from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False

from .algorithms import detect_and_unwind_sequence, RotationJumpEvent
from ...core.context import UndoChunkContext

ROT_ATTRS = ["rotateX", "rotateY", "rotateZ"]


def _ensure_maya():
    if not MAYA_AVAILABLE or cmds is None:
        raise RuntimeError("此功能需要在 Autodesk Maya 运行环境中执行。")


def get_anim_curve_for_plug(node, attr):
    """获取指定节点和属性连接的动画曲线节点（若有）"""
    _ensure_maya()
    plug = "{}.{}".format(node, attr)
    if not cmds.objExists(plug):
        return None

    curves = cmds.listConnections(plug, type="animCurve", source=True, destination=False)
    return curves[0] if curves else None


def get_curve_keyframes_data(curve_node):
    """获取动画曲线的关键帧时间与数值列表"""
    _ensure_maya()
    if not cmds.objExists(curve_node):
        return [], []

    times = cmds.keyframe(curve_node, query=True, timeChange=True) or []
    values = cmds.keyframe(curve_node, query=True, valueChange=True) or []
    return times, values


def apply_keyframe_values(curve_node, times, new_values):
    """安全修改动画曲线上的关键帧数值，保留原本的切线类型与权重"""
    _ensure_maya()
    if not cmds.objExists(curve_node):
        return 0

    count = min(len(times), len(new_values))
    modified = 0

    for i in range(count):
        t = times[i]
        new_v = new_values[i]
        curr_v = cmds.keyframe(curve_node, time=(t, t), query=True, valueChange=True)
        if curr_v and abs(curr_v[0] - new_v) > 1e-4:
            cmds.keyframe(curve_node, edit=True, time=(t, t), valueChange=new_v)
            modified += 1

    return modified


def scan_rotation_winding_issues(
    nodes=None,
    channels=None,
    tolerance=90.0,
    max_time_gap=None,
    time_range=None,
):
    """扫描场景中指定对象和通道的 360 度旋转异常插值跳变"""
    _ensure_maya()

    if nodes is None:
        nodes = cmds.ls(selection=True, type="transform") or []
    if not nodes:
        return []

    if not channels:
        channels = ROT_ATTRS

    all_jump_events = []

    for node in nodes:
        for attr in channels:
            plug = "{}.{}".format(node, attr)
            curve = get_anim_curve_for_plug(node, attr)
            if not curve:
                continue

            times, values = get_curve_keyframes_data(curve)
            if len(times) <= 1:
                continue

            if time_range and len(time_range) == 2:
                t_min, t_max = time_range
                filtered_indices = [i for i, t in enumerate(times) if t_min <= t <= t_max]
                if len(filtered_indices) <= 1:
                    continue
                sub_times = [times[i] for i in filtered_indices]
                sub_values = [values[i] for i in filtered_indices]
            else:
                filtered_indices = list(range(len(times)))
                sub_times = times
                sub_values = values

            _, jumps = detect_and_unwind_sequence(
                sub_times, sub_values, tolerance=tolerance, max_time_gap=max_time_gap
            )

            for j in jumps:
                orig_idx = filtered_indices[j["key_index"]]
                event = RotationJumpEvent(
                    node=node,
                    attribute=attr,
                    curve=curve,
                    key_index=orig_idx,
                    time=j["time"],
                    prev_time=j["prev_time"],
                    old_val=j["old_val"],
                    prev_val=j["prev_val"],
                    delta=j["delta"],
                    k=j["k"],
                    correction=j["correction"],
                )
                all_jump_events.append(event)

    return all_jump_events


def fix_rotation_winding_on_nodes(
    nodes=None,
    channels=None,
    tolerance=90.0,
    max_time_gap=None,
    time_range=None,
):
    """一键自动检测并修复指定对象在各旋转轴上的 360 度倍数异常插值"""
    _ensure_maya()

    if nodes is None:
        nodes = cmds.ls(selection=True, type="transform") or []
    if not nodes:
        return {"modified_curves": 0, "fixed_keys_count": 0, "jump_events_count": 0}

    if not channels:
        channels = ROT_ATTRS

    total_modified_curves = 0
    total_fixed_keys = 0
    total_jumps = 0

    with UndoChunkContext("FixRotationWinding"):
        for node in nodes:
            for attr in channels:
                curve = get_anim_curve_for_plug(node, attr)
                if not curve:
                    continue

                times, values = get_curve_keyframes_data(curve)
                if len(times) <= 1:
                    continue

                if time_range and len(time_range) == 2:
                    t_min, t_max = time_range
                    in_range_indices = [i for i, t in enumerate(times) if t_min <= t <= t_max]
                    if len(in_range_indices) <= 1:
                        continue
                    sub_times = [times[i] for i in in_range_indices]
                    sub_values = [values[i] for i in in_range_indices]
                    new_sub_vals, jumps = detect_and_unwind_sequence(
                        sub_times, sub_values, tolerance=tolerance, max_time_gap=max_time_gap
                    )
                    if jumps:
                        mod_count = apply_keyframe_values(curve, sub_times, new_sub_vals)
                        if mod_count > 0:
                            total_modified_curves += 1
                            total_fixed_keys += mod_count
                            total_jumps += len(jumps)
                else:
                    new_vals, jumps = detect_and_unwind_sequence(
                        times, values, tolerance=tolerance, max_time_gap=max_time_gap
                    )
                    if jumps:
                        mod_count = apply_keyframe_values(curve, times, new_vals)
                        if mod_count > 0:
                            total_modified_curves += 1
                            total_fixed_keys += mod_count
                            total_jumps += len(jumps)

    return {
        "modified_curves": total_modified_curves,
        "fixed_keys_count": total_fixed_keys,
        "jump_events_count": total_jumps,
    }
