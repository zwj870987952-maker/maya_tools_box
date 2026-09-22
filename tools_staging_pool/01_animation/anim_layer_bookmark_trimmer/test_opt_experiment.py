# -*- coding: utf-8 -*-
"""
实验测试：书签区间内动画曲线平滑与简化算法
"""
import maya.cmds as cmds

def smooth_curve_segment(curve, start_time, stop_time, strength=0.5, iterations=1):
    """
    在指定时间区间 [start_time, stop_time] 内平滑动画曲线上的关键帧，
    区间端点 start_time 与 stop_time 的关键帧值严格保持不变。
    
    参数:
        curve (str): 动画曲线节点名
        start_time (float): 起始端点时间
        stop_time (float): 结束端点时间
        strength (float): 平滑力度 0.0 ~ 1.0
        iterations (int): 平滑迭代次数 (1 ~ 5)
    """
    if strength <= 0.0:
        return 0

    # 1. 确保端点有关键帧（姿态锁定）
    start_keys = cmds.keyframe(curve, time=(start_time, start_time), query=True, timeChange=True) or []
    if not start_keys:
        cmds.setKeyframe(curve, time=(start_time, start_time), insert=True)
    stop_keys = cmds.keyframe(curve, time=(stop_time, stop_time), query=True, timeChange=True) or []
    if not stop_keys:
        cmds.setKeyframe(curve, time=(stop_time, stop_time), insert=True)

    # 2. 查询该区间内的所有关键帧 (包含端点)
    key_times = cmds.keyframe(curve, time=(start_time, stop_time), query=True, timeChange=True) or []
    key_times = sorted(list(set([round(float(t), 4) for t in key_times])))
    if len(key_times) < 3:
        # 少于3个关键帧，内部没有可平滑的点
        return 0

    # 获取对应关键帧的值
    # 建立内部点索引列表: 排除第一个点 (start) 和最后一个点 (stop)
    inner_indices = range(1, len(key_times) - 1)

    for it in range(max(1, int(iterations))):
        current_values = []
        for t in key_times:
            val = cmds.keyframe(curve, time=(t, t), query=True, valueChange=True)[0]
            current_values.append(val)

        new_values = list(current_values)
        for i in inner_indices:
            t_prev, t_curr, t_next = key_times[i - 1], key_times[i], key_times[i + 1]
            v_prev, v_curr, v_next = current_values[i - 1], current_values[i], current_values[i + 1]

            # 考虑时间间隔非均匀加权
            dt_prev = max(0.001, t_curr - t_prev)
            dt_next = max(0.001, t_next - t_curr)
            w_prev = 1.0 / dt_prev
            w_next = 1.0 / dt_next
            target_val = (v_prev * w_prev + v_next * w_next) / (w_prev + w_next)

            # 混合力度调节
            blended_val = (1.0 - strength) * v_curr + strength * target_val
            new_values[i] = blended_val

        # 写回内部关键帧的值
        for i in inner_indices:
            t = key_times[i]
            cmds.keyframe(curve, time=(t, t), valueChange=new_values[i])

    # 3. 平滑切线
    cmds.keyTangent(curve, time=(start_time, stop_time), edit=True, itt="spline", ott="spline")
    return len(inner_indices)


def simplify_curve_segment(curve, start_time, stop_time, strength=0.5):
    """
    在指定时间区间 (start_time, stop_time) 内简化/抽稀动画曲线上的冗余关键帧，
    端点 start_time 与 stop_time 绝对不被删除。
    """
    if strength <= 0.0:
        return 0

    # 确保端点有帧
    start_keys = cmds.keyframe(curve, time=(start_time, start_time), query=True, timeChange=True) or []
    if not start_keys:
        cmds.setKeyframe(curve, time=(start_time, start_time), insert=True)
    stop_keys = cmds.keyframe(curve, time=(stop_time, stop_time), query=True, timeChange=True) or []
    if not stop_keys:
        cmds.setKeyframe(curve, time=(stop_time, stop_time), insert=True)

    # 查区间内全部帧
    inner_range = (start_time + 0.001, stop_time - 0.001)
    keys_before = cmds.keyframe(curve, time=inner_range, query=True, timeChange=True) or []
    if not keys_before:
        return 0

    # 根据 strength 映射容差
    # strength 0.1 -> 0.01; strength 0.5 -> 0.1; strength 1.0 -> 0.5
    val_tol = 0.01 + (strength ** 2) * 0.5
    time_tol = 0.05 + strength * 0.1

    cmds.simplify(curve, time=inner_range, timeTolerance=time_tol, valueTolerance=val_tol)
    keys_after = cmds.keyframe(curve, time=inner_range, query=True, timeChange=True) or []
    reduced_count = len(keys_before) - len(keys_after)
    return reduced_count


def test_experiment():
    cube = cmds.polyCube(name="test_opt_cube")[0]
    # 在 1~59 之间生成锯齿噪点动画
    for f in range(1, 60, 2):
        noise = 3.0 if (f // 2) % 2 == 0 else -3.0
        cmds.setKeyframe(cube, attribute="translateY", time=f, value=f * 0.5 + noise)

    curve = cmds.findKeyframe(cube, curve=True)[0]
    keys_orig = cmds.keyframe(curve, query=True, timeChange=True)
    v1_orig = cmds.keyframe(curve, time=(1, 1), query=True, valueChange=True)[0]
    v59_orig = cmds.keyframe(curve, time=(59, 59), query=True, valueChange=True)[0]
    print("Initial key count:", len(keys_orig))
    print("Start (frame 1) val:", v1_orig, "End (frame 59) val:", v59_orig)

    # 测试平滑
    smoothed_pts = smooth_curve_segment(curve, 1.0, 59.0, strength=0.8, iterations=2)
    print("Smoothed points count:", smoothed_pts)

    # 验证端点值绝对未变
    v1_after_smooth = cmds.keyframe(curve, time=(1, 1), query=True, valueChange=True)[0]
    v59_after_smooth = cmds.keyframe(curve, time=(59, 59), query=True, valueChange=True)[0]
    assert abs(v1_orig - v1_after_smooth) < 1e-5, "Start key changed!"
    assert abs(v59_orig - v59_after_smooth) < 1e-5, "End key changed!"
    print("✓ Smooth: Start and End keyframes 100% preserved!")

    # 测试简化
    reduced = simplify_curve_segment(curve, 1.0, 59.0, strength=0.7)
    print("Reduced keys count:", reduced)
    keys_final = cmds.keyframe(curve, query=True, timeChange=True)
    print("Final key count:", len(keys_final))
    assert 1.0 in keys_final and 59.0 in keys_final, "End points removed during simplify!"
    v1_final = cmds.keyframe(curve, time=(1, 1), query=True, valueChange=True)[0]
    v59_final = cmds.keyframe(curve, time=(59, 59), query=True, valueChange=True)[0]
    assert abs(v1_orig - v1_final) < 1e-5
    assert abs(v59_orig - v59_final) < 1e-5
    print("✓ Simplify: End points 100% preserved and keys reduced!")

    cmds.delete(cube)
    print("=== ALL EXPERIMENT CHECKS PASSED! ===")

if __name__ == "__main__":
    test_experiment()
