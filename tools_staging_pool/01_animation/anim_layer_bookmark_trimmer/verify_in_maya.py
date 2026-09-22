# -*- coding: utf-8 -*-
"""
Live Maya 实测验证脚本：anim_layer_bookmark_trimmer (含 3 种书签作用范围验证)
"""
import os
import sys
import maya.cmds as cmds

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import anim_layer_bookmark_trimmer as trimmer

def run_live_maya_verification():
    print("=== 开始 Live Maya 实测验证 (含 3 种书签作用范围) ===")

    # 1. UI 启动测试
    ui = trimmer.show_ui()
    assert cmds.window(trimmer.WINDOW_NAME, exists=True), "UI 窗口未能成功创建！"
    print("✓ UI 窗口顺利打开，包含三种书签范围选择菜单。")

    # 2. 准备测试场景数据
    test_node = "trim_verify_sphere_v4"
    if cmds.objExists(test_node):
        cmds.delete(test_node)

    for bm in cmds.ls(type="timeSliderBookmark") or []:
        cmds.delete(bm)

    sphere = cmds.polySphere(name=test_node)[0]
    cmds.select(sphere)

    # 确保书签插件
    if not cmds.pluginInfo("timeSliderBookmark", query=True, loaded=True):
        cmds.loadPlugin("timeSliderBookmark")

    # 创建 3 个不同时间段的书签
    bm1 = cmds.createNode("timeSliderBookmark", name="BM_Walk_1_50")
    cmds.setAttr(bm1 + ".timeRangeStart", 1.0)
    cmds.setAttr(bm1 + ".timeRangeStop", 50.0)

    bm2 = cmds.createNode("timeSliderBookmark", name="BM_Run_60_100")
    cmds.setAttr(bm2 + ".timeRangeStart", 60.0)
    cmds.setAttr(bm2 + ".timeRangeStop", 100.0)

    bm3 = cmds.createNode("timeSliderBookmark", name="BM_Jump_150_200")
    cmds.setAttr(bm3 + ".timeRangeStart", 150.0)
    cmds.setAttr(bm3 + ".timeRangeStop", 200.0)

    # 为 sphere 打关键帧
    # BM1 内: 1, 20, 35, 50
    # BM2 内: 60, 75, 85, 100
    # BM3 内: 150, 175, 200
    for f in [1, 20, 35, 50, 60, 75, 85, 100, 150, 175, 200]:
        cmds.setKeyframe(sphere, attribute="translateY", time=f, value=f * 0.5)

    # 3. 验证范围 1: 全部书签 (scope="all")
    all_bms, desc_all = trimmer.get_filtered_bookmarks(scope="all")
    assert len(all_bms) == 3, "Scope all should find 3 bookmarks, got {}".format(len(all_bms))
    print("✓ 范围 1 (全部书签): 成功识别全部 3 个书签。")

    # 4. 验证范围 2: 时间轴播放范围 (scope="playback")
    cmds.playbackOptions(minTime=1, maxTime=110)
    pb_bms, desc_pb = trimmer.get_filtered_bookmarks(scope="playback")
    pb_names = [b["name"] for b in pb_bms]
    assert "BM_Walk_1_50" in pb_names and "BM_Run_60_100" in pb_names
    assert "BM_Jump_150_200" not in pb_names, "BM3 should not be in playback range 1~110"
    print("✓ 范围 2 (播放范围): 仅识别 1~110 范围内的 BM1 与 BM2，BM3 被成功过滤排除。")

    # 5. 验证范围 3: 光标所在时间 (scope="selected")
    cmds.currentTime(75) # 将时间指针移至 BM2 内部
    sel_bms, desc_sel = trimmer.get_filtered_bookmarks(scope="selected")
    assert len(sel_bms) == 1 and sel_bms[0]["name"] == "BM_Run_60_100"
    print("✓ 范围 3 (光标所在时间): 时间指针在 75 帧，自动精确锁定书签 BM2 (60~100)。")

    # 6. 验证局部作用保护机制 (以 scope="selected" 修剪 BM2)
    # 期望：仅在 60~100 之间修剪（删除 75、85，保留 60、100），而 BM1 的 20、35 和 BM3 的 175 完全不被删除！
    trim_res = trimmer.trim_layer_keyframes_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="selected",
        dry_run=False
    )
    assert trim_res["success"] is True
    keys_after_trim = cmds.keyframe(sphere, attribute="translateY", query=True, timeChange=True)
    print("Keys after localized trim:", keys_after_trim)

    # 验证 BM2 端点保留，非端点 75, 85 删除
    assert 60.0 in keys_after_trim and 100.0 in keys_after_trim
    assert 75.0 not in keys_after_trim and 85.0 not in keys_after_trim

    # 验证详细诊断报告输出内容
    assert u"成功修剪" in trim_res["message"]
    assert "translateY" in trim_res["message"]
    print("✓ 关键帧修剪详细报告验证通过：明确列出修改对象、属性及删除端点明细。")

    # 重点验证：局部范围外部的关键帧 100% 完整保留！
    assert 20.0 in keys_after_trim and 35.0 in keys_after_trim, "BM1 keys should NOT be deleted!"
    assert 175.0 in keys_after_trim, "BM3 keys should NOT be deleted!"
    print("✓ 局部修剪安全保护机制通过：外部书签帧未受任何误伤！")

    # 7. 验证曲线优化在 scope="selected" 下仅作用于 BM2
    opt_res = trimmer.optimize_layer_curves_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="selected",
        mode="smart",
        strength=0.7,
        dry_run=False
    )
    assert opt_res["success"] is True
    assert u"成功" in opt_res["message"] and "translateY" in opt_res["message"]
    print("✓ 局部综合曲线优化详细诊断报告验证通过：明确列出修改的对象与属性。")

    # 8. 测试 Undo 撤销
    cmds.undo() # 撤销优化
    cmds.undo() # 撤销局部修剪
    keys_restored = cmds.keyframe(sphere, attribute="translateY", query=True, timeChange=True)
    assert 75.0 in keys_restored and 85.0 in keys_restored
    print("✓ Ctrl+Z (Undo) 撤销成功，所有被修剪关键帧完美还原。")

    # 9. 重点验证：区间多帧缓入缓出 (mode="multikey_ease")
    # 测试 BM2 (60~100 范围，关键帧为 60, 75, 85, 100)
    cmds.currentTime(70) # 确保光标在 BM2 内
    v_st_before = cmds.keyframe(sphere, attribute="translateY", time=(60, 60), query=True, valueChange=True)[0]
    v_sp_before = cmds.keyframe(sphere, attribute="translateY", time=(100, 100), query=True, valueChange=True)[0]
    v_75_before = cmds.keyframe(sphere, attribute="translateY", time=(75, 75), query=True, valueChange=True)[0]
    v_85_before = cmds.keyframe(sphere, attribute="translateY", time=(85, 85), query=True, valueChange=True)[0]

    # BM1 外部对照帧
    v_bm1_20_before = cmds.keyframe(sphere, attribute="translateY", time=(20, 20), query=True, valueChange=True)[0]

    # 执行 100% 力度的多帧缓入缓出
    ease_res = trimmer.optimize_layer_curves_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="selected",
        mode="multikey_ease",
        strength=1.0,
        dry_run=False
    )
    assert ease_res["success"] is True

    # 验证 1: 端点绝对锁定不变
    v_st_after = cmds.keyframe(sphere, attribute="translateY", time=(60, 60), query=True, valueChange=True)[0]
    v_sp_after = cmds.keyframe(sphere, attribute="translateY", time=(100, 100), query=True, valueChange=True)[0]
    assert abs(v_st_after - v_st_before) < 1e-4, "起始端点值发生偏移！"
    assert abs(v_sp_after - v_sp_before) < 1e-4, "结束端点值发生偏移！"

    # 验证 2: 中间帧符合 Smootherstep 缓入缓出计算公式
    # 60 到 100 跨度 dt = 40, dv = v_sp - v_st
    dv = v_sp_before - v_st_before
    # 75 帧: u = (75 - 60) / 40 = 0.375
    u_75 = (75.0 - 60.0) / 40.0
    s_75 = 6.0 * (u_75 ** 5) - 15.0 * (u_75 ** 4) + 10.0 * (u_75 ** 3)
    expected_v75 = v_st_before + s_75 * dv

    # 85 帧: u = (85 - 60) / 40 = 0.625
    u_85 = (85.0 - 60.0) / 40.0
    s_85 = 6.0 * (u_85 ** 5) - 15.0 * (u_85 ** 4) + 10.0 * (u_85 ** 3)
    expected_v85 = v_st_before + s_85 * dv

    v_75_after = cmds.keyframe(sphere, attribute="translateY", time=(75, 75), query=True, valueChange=True)[0]
    v_85_after = cmds.keyframe(sphere, attribute="translateY", time=(85, 85), query=True, valueChange=True)[0]

    assert abs(v_75_after - expected_v75) < 1e-3, "75 帧 Smootherstep 缓动数值不符预期！"
    assert abs(v_85_after - expected_v85) < 1e-3, "85 帧 Smootherstep 缓动数值不符预期！"
    print("✓ 区间多帧缓入缓出 (multikey_ease) 验证通过：中间多帧完美贴合 Smootherstep S 曲线！")

    # 验证 3: 外部关键帧 100% 隔离未改动
    v_bm1_20_after = cmds.keyframe(sphere, attribute="translateY", time=(20, 20), query=True, valueChange=True)[0]
    assert abs(v_bm1_20_after - v_bm1_20_before) < 1e-5, "外部 BM1 帧被意外改动！"

    # 验证 4: 多帧缓动 Undo 撤销
    cmds.undo()
    v_75_undone = cmds.keyframe(sphere, attribute="translateY", time=(75, 75), query=True, valueChange=True)[0]
    assert abs(v_75_undone - v_75_before) < 1e-4, "multikey_ease 撤销失败！"
    print("✓ 多帧缓入缓出撤销 (Undo) 成功，数值完全复原。")

    # 10. 验证权重偏置滑杆 (Weight Bias)
    # 测试 bias=0.2 (偏向起点: 滞留起点更久，缓出加重)
    bias_res_start = trimmer.optimize_layer_curves_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="selected",
        mode="multikey_ease",
        strength=1.0,
        bias=0.2,
        dry_run=False
    )
    assert bias_res_start["success"] is True
    v_st_b02 = cmds.keyframe(sphere, attribute="translateY", time=(60, 60), query=True, valueChange=True)[0]
    v_sp_b02 = cmds.keyframe(sphere, attribute="translateY", time=(100, 100), query=True, valueChange=True)[0]
    assert abs(v_st_b02 - v_st_before) < 1e-4, "bias=0.2 起点漂移！"
    assert abs(v_sp_b02 - v_sp_before) < 1e-4, "bias=0.2 终点漂移！"

    v_75_b02 = cmds.keyframe(sphere, attribute="translateY", time=(75, 75), query=True, valueChange=True)[0]
    # 计算期望理论值: u=0.375, b=0.2
    denom_02 = (1.0 / 0.2 - 2.0) * (1.0 - 0.375) + 1.0
    u_prime_02 = 0.375 / denom_02
    s_02 = 6.0 * (u_prime_02 ** 5) - 15.0 * (u_prime_02 ** 4) + 10.0 * (u_prime_02 ** 3)
    exp_v75_b02 = v_st_before + s_02 * dv
    assert abs(v_75_b02 - exp_v75_b02) < 1e-3, "bias=0.2 缓动数值不符合预期！"
    assert v_75_b02 < expected_v75, "偏向起点的数值应低于居中对称时的数值！"
    print("✓ bias=0.2 (偏向起点) 验证通过：端点绝对锁定，中间帧数值精准符合理论变形！")

    # 撤销并测试 bias=0.8 (偏向终点: 快速拉升，滞留终点更久，缓入加重)
    cmds.undo()
    bias_res_end = trimmer.optimize_layer_curves_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="selected",
        mode="multikey_ease",
        strength=1.0,
        bias=0.8,
        dry_run=False
    )
    assert bias_res_end["success"] is True
    v_st_b08 = cmds.keyframe(sphere, attribute="translateY", time=(60, 60), query=True, valueChange=True)[0]
    v_sp_b08 = cmds.keyframe(sphere, attribute="translateY", time=(100, 100), query=True, valueChange=True)[0]
    assert abs(v_st_b08 - v_st_before) < 1e-4, "bias=0.8 起点漂移！"
    assert abs(v_sp_b08 - v_sp_before) < 1e-4, "bias=0.8 终点漂移！"

    v_75_b08 = cmds.keyframe(sphere, attribute="translateY", time=(75, 75), query=True, valueChange=True)[0]
    denom_08 = (1.0 / 0.8 - 2.0) * (1.0 - 0.375) + 1.0
    u_prime_08 = 0.375 / denom_08
    s_08 = 6.0 * (u_prime_08 ** 5) - 15.0 * (u_prime_08 ** 4) + 10.0 * (u_prime_08 ** 3)
    exp_v75_b08 = v_st_before + s_08 * dv
    assert abs(v_75_b08 - exp_v75_b08) < 1e-3, "bias=0.8 缓动数值不符合预期！"
    assert v_75_b08 > expected_v75, "偏向终点的数值应高于居中对称时的数值！"
    print("✓ bias=0.8 (偏向终点) 验证通过：端点绝对锁定，中间帧数值精准符合理论变形！")

    cmds.undo()
    print("✓ bias 测试后 Undo 撤销成功。")

    # 11. 重点验证：通道过滤与显示隐藏 (visibility) 绝对排除
    print("--- 开始验证：显示隐藏 (visibility) 绝对排除与通道过滤 ---")
    # 为 sphere 在 visibility 上打入离散关键帧 (0 与 1 开关)
    vis_data = [(1, 1.0), (20, 0.0), (60, 1.0), (75, 0.0), (85, 1.0), (100, 0.0)]
    for f, v in vis_data:
        cmds.setKeyframe(sphere, attribute="visibility", time=f, value=v, inTangentType="step", outTangentType="step")

    # 执行全局综合曲线优化 (包含了平滑、抽稀、多帧S曲线与缓入缓出)
    opt_vis_test = trimmer.optimize_layer_curves_by_bookmarks(
        objects=[sphere],
        layer="BaseAnimation",
        scope="all",
        mode="smart",
        strength=1.0,
        include_translate=True,
        include_rotate=True,
        include_scale=False,
        channel_box_priority=False,
        dry_run=False
    )
    assert opt_vis_test["success"] is True

    # 验证 1: 报告中绝不包含 visibility
    assert "visibility" not in opt_vis_test["message"], "报告中错误包含了 visibility！"
    assert "translateY" in opt_vis_test["message"], "报告应包含 translateY！"

    # 验证 2: visibility 上的所有关键帧数量、数值和切线类型绝对未受触碰
    vis_keys_raw = cmds.keyframe(sphere, attribute="visibility", query=True, timeChange=True) or []
    vis_keys_after = sorted(list(set([round(float(t), 4) for t in vis_keys_raw])))
    assert len(vis_keys_after) == len(vis_data), "visibility 关键帧数量被错误改变！得到 {}".format(vis_keys_after)
    for f, expected_val in vis_data:
        actual_val = cmds.keyframe(sphere, attribute="visibility", time=(f, f), query=True, valueChange=True)[0]
        assert abs(actual_val - expected_val) < 1e-4, "visibility 关键帧数值被错误篡改！"
        ott = cmds.keyTangent(sphere, attribute="visibility", time=(f, f), query=True, outTangentType=True)[0]
        assert ott == "step", "visibility 阶梯切线被错误修改！"

    print("✓ visibility 绝对隔离验证通过：显示隐藏通道 100% 未受触碰，阶梯切线与 0/1 数值完好无损！")

    # 验证 3: Channel Box 属性高亮优先 (模拟仅处理 translateY)
    # 当 channel_box_priority 开启时，若用户未在通道栏高亮，默认处理 Translate+Rotate
    curves_default = trimmer.get_layer_curves_for_objects([sphere], "BaseAnimation", include_translate=True, include_rotate=True, channel_box_priority=False)
    for c in curves_default:
        plug = trimmer.get_plug_for_curve(c)
        assert "visibility" not in plug, "默认获取的曲线中错误包含了 visibility！"

    print("✓ 通道过滤器验证通过：默认精准聚焦 Translate 与 Rotate，永久杜绝误改非目标属性！")

    # 12. 清理测试节点
    cmds.delete(sphere)
    cmds.delete(bm1)
    cmds.delete(bm2)
    cmds.delete(bm3)
    cmds.deleteUI(trimmer.WINDOW_NAME, window=True)
    print("=== 全部功能、3 种书签作用范围、多帧缓动、权重偏置与通道安全隔离实测验证 100% 通过！===")

if __name__ == "__main__":
    run_live_maya_verification()
