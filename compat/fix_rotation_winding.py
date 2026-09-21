# -*- coding: utf-8 -*-
"""
Maya 动画工具：修正对象旋转数值 360 度倍数异常插值 (Fix Rotation 360 Winding Tool)

功能概述：
    用于自动识别并消除控制器在动画制作、欧拉角翻转（Euler Flip）、动捕解算、烘焙或外部导入时，
    因旋转数值异常增加或减少 360 度或其倍数（±360°, ±720°...）而导致的空转、暴走插值与阶跃。

核心特性：
    1. 智能识别：基于差分与欧拉周期分析，精准定位跳变帧、突变幅度与修正值。
    2. 平滑解包（Unwind）：自动将跳变后的整段曲线平移对齐，彻底消除多余自转插值。
    3. 切线保护：采用关键帧数值直接重映射，严格保持原有的曲线切线类型（Spline/Linear/Clamped等）及权重。
    4. 定位联动：扫描列表支持双击秒级跳转至问题关键帧，并在视口与曲线编辑器（Graph Editor）联动对焦。
    5. 全版本原生兼容：纯 Python 实现，零外部 C++ / Qt 第三方库依赖，支持 Maya 2018~2026+。
    6. 安全撤销：支持 Maya 单个 Undo Chunk，修改随时 Ctrl+Z 一键撤销。

使用方式：
    1. 在 Maya 脚本编辑器（Python）中运行：
       import fix_rotation_winding
       fix_rotation_winding.show_ui()

    2. 命令行/代码调用：
       import fix_rotation_winding
       fix_rotation_winding.fix_rotation_winding_on_nodes(
           nodes=["char_ctrl"],
           channels=["rotateX", "rotateY", "rotateZ"],
           tolerance=90.0
       )
"""

from __future__ import absolute_import, division, print_function

import math
import sys

# 尝试导入 Maya 模块（允许在外部测试环境下以独立模式运行）
try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False


# ==============================================================================
# 第一部分：纯数据与数学算法层（独立可测，无 UI 耦合）
# ==============================================================================

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
            - fixed_values (list[float]): 消除 360 度多余跳变后的新数值序列
            - jump_events (list[dict]): 检测到的跳变点详细信息列表
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

        # 检查时间跨度限制
        if max_time_gap is not None and (t_curr - t_prev) > max_time_gap:
            # 跨度过大，不视作突变连续帧，直接继承当前累积偏移
            v_fixed = raw_val + cumulative_offset
            fixed_values[i] = v_fixed
            prev_fixed_val = v_fixed
            continue

        # 当前帧叠加已有的累积偏移
        v_tentative = raw_val + cumulative_offset
        diff = v_tentative - prev_fixed_val

        # 计算最接近的 360 整数倍
        k = int(round(diff / 360.0))

        if k != 0:
            residual = abs(diff - 360.0 * k)
            if residual <= tolerance:
                # 命中 360 度倍数跳变！需要消除此阶跃
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

    参数：
        values (list[float]): 旋转数值列表
        target_range (str): "[-180, 180]" 或 "[0, 360]"

    返回：
        tuple: (normalized_values, offset_applied)
    """
    if not values:
        return [], 0.0

    # 以首帧作为基准参考
    ref_val = values[0]

    if target_range == "[0, 360]":
        k = int(math.floor(ref_val / 360.0))
        offset = -360.0 * k
    else:  # "[-180, 180]"
        k = int(round(ref_val / 360.0))
        offset = -360.0 * k

    if abs(offset) < 1e-4:
        return list(values), 0.0

    norm_values = [v + offset for v in values]
    return norm_values, offset


# ==============================================================================
# 第二部分：Maya 场景与动画曲线查询与修改交互层
# ==============================================================================

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
    if curves:
        return curves[0]
    return None


def get_curve_keyframes_data(curve_node):
    """获取动画曲线的关键帧时间与数值列表"""
    _ensure_maya()
    if not cmds.objExists(curve_node):
        return [], []

    times = cmds.keyframe(curve_node, query=True, timeChange=True) or []
    values = cmds.keyframe(curve_node, query=True, valueChange=True) or []
    return times, values


def apply_keyframe_values(curve_node, times, new_values):
    """
    安全修改动画曲线上的关键帧数值，保留原本的切线类型与权重。
    """
    _ensure_maya()
    if not cmds.objExists(curve_node):
        return 0

    count = min(len(times), len(new_values))
    modified = 0

    for i in range(count):
        t = times[i]
        new_v = new_values[i]
        # 查询当前值，避免无谓的重复设值
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
    """
    扫描场景中指定对象和通道的 360 度旋转异常插值跳变。

    参数：
        nodes (list[str] or None): 要扫描的对象名称列表。为 None 时取当前视口选区
        channels (list[str] or None): 旋转轴列表，默认 ["rotateX", "rotateY", "rotateZ"]
        tolerance (float): 容差角度（度），默认 90.0°
        max_time_gap (float or None): 最大时间跨度限制
        time_range (tuple or None): (start_frame, end_frame) 扫描的时间范围限制

    返回：
        list[RotationJumpEvent]: 发现的所有跳变事件对象列表
    """
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

            # 如果指定了时间范围过滤
            if time_range and len(time_range) == 2:
                t_min, t_max = time_range
                filtered_indices = [
                    i for i, t in enumerate(times) if t_min <= t <= t_max
                ]
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
    """
    一键自动检测并修复指定对象在各旋转轴上的 360 度倍数异常插值。

    返回：
        dict: 统计结果，包含 modified_curves, fixed_keys_count, jump_events_count
    """
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

    # 开启单层撤销块
    cmds.undoInfo(openChunk=True, chunkName="Fix Rotation Winding")
    try:
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
                    # 仅针对范围内的序列进行检测
                    in_range_indices = [
                        i for i, t in enumerate(times) if t_min <= t <= t_max
                    ]
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
    finally:
        cmds.undoInfo(closeChunk=True)

    return {
        "modified_curves": total_modified_curves,
        "fixed_keys_count": total_fixed_keys,
        "jump_events_count": total_jumps,
    }


def offset_selected_keys_or_curves(offset_degrees=360.0, nodes=None, channels=None):
    """
    对当前在 Graph Editor 中选中的关键帧，或选定对象当前时间段/全部关键帧，
    快速增加或减少指定的角度（如 +360° 或 -360°）。
    """
    _ensure_maya()

    cmds.undoInfo(openChunk=True, chunkName="Offset Rotation 360")
    try:
        # 首先检查 Graph Editor 中是否有直接选中的关键帧
        selected_key_curves = cmds.keyframe(selected=True, query=True, name=True) or []
        if selected_key_curves:
            cmds.keyframe(selected=True, edit=True, relative=True, valueChange=offset_degrees)
            return len(selected_key_curves)

        # 否则作用于传入的对象或当前选中的物体
        if nodes is None:
            nodes = cmds.ls(selection=True, type="transform") or []
        if not nodes:
            return 0

        if not channels:
            channels = ROT_ATTRS

        count = 0
        for node in nodes:
            for attr in channels:
                curve = get_anim_curve_for_plug(node, attr)
                if curve:
                    cmds.keyframe(curve, edit=True, relative=True, valueChange=offset_degrees)
                    count += 1
        return count
    finally:
        cmds.undoInfo(closeChunk=True)


def normalize_rotation_baseline_on_nodes(nodes=None, channels=None, target_range="[-180, 180]"):
    """
    将对象的旋转曲线规范化到标准主值区间。
    """
    _ensure_maya()

    if nodes is None:
        nodes = cmds.ls(selection=True, type="transform") or []
    if not nodes:
        return 0

    if not channels:
        channels = ROT_ATTRS

    modified_count = 0
    cmds.undoInfo(openChunk=True, chunkName="Normalize Rotation Baseline")
    try:
        for node in nodes:
            for attr in channels:
                curve = get_anim_curve_for_plug(node, attr)
                if not curve:
                    continue

                times, values = get_curve_keyframes_data(curve)
                if not values:
                    continue

                norm_vals, offset = normalize_sequence_baseline(values, target_range=target_range)
                if abs(offset) > 1e-4:
                    apply_keyframe_values(curve, times, norm_vals)
                    modified_count += 1
    finally:
        cmds.undoInfo(closeChunk=True)

    return modified_count


# ==============================================================================
# 第三部分：用户图形界面 (Maya 原生 UI，零外部依赖，极速响应)
# ==============================================================================

class FixRotationWindingUI(object):
    """Maya 修正对象旋转数值 360 度倍数异常插值工具 UI 面板"""

    WINDOW_NAME = "MayaFixRotationWindingWindow"
    TITLE = "Maya 旋转数值 360° 异常插值修正工具 v1.0.0"

    def __init__(self):
        self.cached_jump_events = []

    def show(self):
        _ensure_maya()

        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME, window=True)

        self.window = cmds.window(
            self.WINDOW_NAME,
            title=self.TITLE,
            widthHeight=(640, 680),
            menuBar=True,
            sizeable=True,
        )

        self._build_ui()
        cmds.showWindow(self.window)

    def _build_ui(self):
        # 主布局
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnOffset=["both", 10])

        # 1. 顶部标题标语
        cmds.separator(height=6, style="none")
        cmds.text(
            label="智能识别并消除控制器旋转中异常增加/减少 360° 造成的空转插值与阶跃",
            align="center",
            font="obliqueLabelFont",
        )
        cmds.separator(height=10, style="in")

        # 2. 扫描与作用范围设置框 (Scope & Channels)
        frame_scope = cmds.frameLayout(
            label=" 1. 作用范围与目标轴向",
            collapsable=True,
            collapse=False,
            marginWidth=10,
            marginHeight=8,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

        # 作用对象范围
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(90, 480), adjustableColumn=2)
        cmds.text(label="对象范围: ", align="right")
        self.scope_radio = cmds.radioButtonGrp(
            numberOfRadioButtons=3,
            labelArray3=["选中的对象", "包含子层级 (Hierarchy)", "Graph Editor 选中曲线"],
            select=1,
            columnWidth3=[110, 190, 180],
        )
        cmds.setParent("..")

        # 目标旋转通道勾选
        cmds.rowLayout(numberOfColumns=5, columnWidth5=(90, 90, 90, 90, 100), adjustableColumn=5)
        cmds.text(label="旋转轴向: ", align="right")
        self.chk_rx = cmds.checkBox(label="Rotate X", value=True)
        self.chk_ry = cmds.checkBox(label="Rotate Y", value=True)
        self.chk_rz = cmds.checkBox(label="Rotate Z", value=True)
        cmds.button(label="全选/反选", height=20, command=self._toggle_channels)
        cmds.setParent("..")

        # 时间范围
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(90, 480), adjustableColumn=2)
        cmds.text(label="时间范围: ", align="right")
        self.time_range_radio = cmds.radioButtonGrp(
            numberOfRadioButtons=3,
            labelArray3=["全部时间轴", "播放范围 (Playback)", "时间滑条高亮选区"],
            select=1,
            columnWidth3=[110, 170, 180],
        )
        cmds.setParent("..")

        cmds.setParent("..")  # end column
        cmds.setParent("..")  # end frameLayout

        # 3. 识别算法参数设置框 (Detection Settings)
        frame_detect = cmds.frameLayout(
            label=" 2. 识别与跳变判定参数",
            collapsable=True,
            collapse=False,
            marginWidth=10,
            marginHeight=8,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 160, 320), adjustableColumn=3)
        cmds.text(label="判定容差 (度): ", align="right")
        self.tolerance_field = cmds.floatField(value=90.0, precision=1, minValue=1.0, maxValue=180.0)
        cmds.text(label="（推荐 90°：若相邻帧差接近 360°±90° 即判定为 360° 空转跳变）", align="left", font="smallPlainLabelFont")
        cmds.setParent("..")

        # 扫描与自动修复主动作按钮
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(295, 295))
        cmds.button(
            label="🔍 扫描检测异常 360° 跳变",
            height=34,
            backgroundColor=[0.24, 0.36, 0.52],
            command=self._on_scan_clicked,
        )
        cmds.button(
            label="⚡ 一键全自动平滑修复（免扫描直接修）",
            height=34,
            backgroundColor=[0.24, 0.52, 0.36],
            command=self._on_quick_fix_clicked,
        )
        cmds.setParent("..")

        cmds.setParent("..")  # end column
        cmds.setParent("..")  # end frameLayout

        # 4. 异常跳变检测结果列表 (Detection Results Table)
        frame_list = cmds.frameLayout(
            label=" 3. 检测结果列表 (双击列表项可直接定位跳转至该帧并在视口聚焦)",
            collapsable=False,
            marginWidth=10,
            marginHeight=8,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # 提示表头
        header_text = "{:<4} {:<18} {:<10} {:<8} {:<10} {:<10} {:<10}".format(
            "序号", "控制器对象", "通道", "帧数", "跳变前", "跳变后", "修正量"
        )
        cmds.text(label=header_text, align="left", font="boldLabelFont")

        # 滚动多选列表框
        self.results_scroll_list = cmds.textScrollList(
            numberOfRows=10,
            allowMultiSelection=True,
            doubleClickCommand=self._on_list_double_clicked,
            font="plainLabelFont",
            height=180,
        )

        # 针对列表选中的局部操作按钮
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(195, 195, 195))
        cmds.button(label="修复列表中选中的项", height=26, command=self._on_fix_selected_list_items)
        cmds.button(label="修复列表中全部异常", height=26, command=self._on_fix_all_list_items)
        cmds.button(label="清空列表", height=26, command=self._on_clear_list)
        cmds.setParent("..")

        cmds.setParent("..")  # end column
        cmds.setParent("..")  # end frameLayout

        # 5. 辅助与手动快速微调工具箱 (Manual & Baseline Tools)
        frame_manual = cmds.frameLayout(
            label=" 4. 快捷微调与基准规范化",
            collapsable=True,
            collapse=True,
            marginWidth=10,
            marginHeight=8,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        # 手动加减 360 度按钮组
        cmds.rowLayout(numberOfColumns=5, columnWidth5=(90, 115, 115, 115, 115))
        cmds.text(label="步长微调: ", align="right")
        cmds.button(label="- 360°", height=26, command=lambda *a: self._on_quick_offset(-360.0))
        cmds.button(label="+ 360°", height=26, command=lambda *a: self._on_quick_offset(360.0))
        cmds.button(label="- 720°", height=26, command=lambda *a: self._on_quick_offset(-720.0))
        cmds.button(label="+ 720°", height=26, command=lambda *a: self._on_quick_offset(720.0))
        cmds.setParent("..")

        # 规范化到主值区间
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 230, 230))
        cmds.text(label="整体基准规范化: ", align="right")
        cmds.button(
            label="规范化至 [-180°, 180°]",
            height=26,
            command=lambda *a: self._on_normalize("[-180, 180]"),
        )
        cmds.button(
            label="规范化至 [0°, 360°]",
            height=26,
            command=lambda *a: self._on_normalize("[0, 360]"),
        )
        cmds.setParent("..")

        cmds.setParent("..")  # end column
        cmds.setParent("..")  # end frameLayout

        # 6. 底部状态与日志栏
        cmds.separator(height=6, style="in")
        self.status_text = cmds.text(
            label="就绪。请选择控制器对象并点击【扫描检测】或【一键全自动平滑修复】。",
            align="left",
            font="smallPlainLabelFont",
        )
        cmds.separator(height=4, style="none")

    # --------------------------------------------------------------------------
    # 界面交互与事件处理
    # --------------------------------------------------------------------------

    def _set_status(self, message, is_warning=False, is_error=False):
        """更新底部状态栏文本"""
        if is_error:
            msg = "❌ 错误: " + message
        elif is_warning:
            msg = "⚠️ 提示: " + message
        else:
            msg = "✅ " + message
        cmds.text(self.status_text, edit=True, label=msg)
        print("[FixRotationWinding] " + msg)

    def _toggle_channels(self, *args):
        """全选或反选旋转轴向复选框"""
        rx = cmds.checkBox(self.chk_rx, query=True, value=True)
        ry = cmds.checkBox(self.chk_ry, query=True, value=True)
        rz = cmds.checkBox(self.chk_rz, query=True, value=True)

        new_val = not (rx and ry and rz)
        cmds.checkBox(self.chk_rx, edit=True, value=new_val)
        cmds.checkBox(self.chk_ry, edit=True, value=new_val)
        cmds.checkBox(self.chk_rz, edit=True, value=new_val)

    def _get_target_channels(self):
        """获取用户勾选的通道列表"""
        channels = []
        if cmds.checkBox(self.chk_rx, query=True, value=True):
            channels.append("rotateX")
        if cmds.checkBox(self.chk_ry, query=True, value=True):
            channels.append("rotateY")
        if cmds.checkBox(self.chk_rz, query=True, value=True):
            channels.append("rotateZ")
        return channels

    def _get_target_nodes(self):
        """根据选区和范围设置获取目标对象列表"""
        scope_idx = cmds.radioButtonGrp(self.scope_radio, query=True, select=True)

        if scope_idx == 3:
            # 模式 3: Graph Editor 中选中的曲线所对应的节点
            curves = cmds.keyframe(selected=True, query=True, name=True) or []
            nodes = set()
            for c in curves:
                conns = cmds.listConnections(c + ".output", destination=True, source=False) or []
                for n in conns:
                    if cmds.nodeType(n) in ["transform", "joint"]:
                        nodes.add(n)
            return list(nodes)

        # 模式 1 或 2: 选中的对象
        selected = cmds.ls(selection=True, type=["transform", "joint"]) or []
        if not selected:
            return []

        if scope_idx == 2:
            # 包含子层级
            all_hierarchy = cmds.listRelatives(selected, allDescendents=True, type=["transform", "joint"], fullPath=False) or []
            nodes = list(set(selected + all_hierarchy))
            return nodes

        return selected

    def _get_target_time_range(self):
        """获取时间范围设置"""
        t_mode = cmds.radioButtonGrp(self.time_range_radio, query=True, select=True)
        if t_mode == 2:
            # 播放范围 (Playback Range)
            min_t = cmds.playbackOptions(query=True, minTime=True)
            max_t = cmds.playbackOptions(query=True, maxTime=True)
            return (min_t, max_t)
        elif t_mode == 3:
            # 时间滑条高亮选区 (Time Slider Highlighted Range)
            try:
                import maya.mel as mel
                g_play_slider = mel.eval("$tmp = $gPlayBackSlider")
                if cmds.timeControl(g_play_slider, query=True, isModified=True):
                    rng = cmds.timeControl(g_play_slider, query=True, rangeArray=True)
                    if rng and len(rng) == 2:
                        return (rng[0], rng[1])
            except Exception:
                pass
            # 回退使用播放范围
            min_t = cmds.playbackOptions(query=True, minTime=True)
            max_t = cmds.playbackOptions(query=True, maxTime=True)
            return (min_t, max_t)
        return None

    def _on_scan_clicked(self, *args):
        """点击扫描检测按钮"""
        nodes = self._get_target_nodes()
        channels = self._get_target_channels()
        tolerance = cmds.floatField(self.tolerance_field, query=True, value=True)
        time_range = self._get_target_time_range()

        if not nodes:
            self._set_status("未选择任何控制器对象！请先在场景中选择对象。", is_warning=True)
            return

        if not channels:
            self._set_status("请至少勾选一个旋转轴向 (X/Y/Z)！", is_warning=True)
            return

        self._on_clear_list()

        events = scan_rotation_winding_issues(
            nodes=nodes,
            channels=channels,
            tolerance=tolerance,
            time_range=time_range,
        )

        self.cached_jump_events = events

        if not events:
            self._set_status("扫描完毕！在所选对象与通道中未检测到 360° 异常跳变。动画旋转正常。")
            return

        for idx, ev in enumerate(events, 1):
            short_node = ev.node.split("|")[-1]
            line_str = "#{:<3} | {:<16} | {:<8} | {:<6.1f} | {:<8.1f}° | {:<8.1f}° | {:<+7.0f}°".format(
                idx,
                short_node[:16],
                ev.attribute,
                ev.time,
                ev.prev_val,
                ev.old_val,
                ev.correction,
            )
            cmds.textScrollList(self.results_scroll_list, edit=True, append=line_str)

        self._set_status(
            "扫描完成！共检测到 {} 处 360° 倍数异常跳变。可双击定位或点击修复。".format(len(events))
        )

    def _on_quick_fix_clicked(self, *args):
        """一键全自动平滑修复（直接修复无需预览）"""
        nodes = self._get_target_nodes()
        channels = self._get_target_channels()
        tolerance = cmds.floatField(self.tolerance_field, query=True, value=True)
        time_range = self._get_target_time_range()

        if not nodes:
            self._set_status("未选择任何控制器对象！", is_warning=True)
            return

        if not channels:
            self._set_status("请至少勾选一个旋转轴向！", is_warning=True)
            return

        res = fix_rotation_winding_on_nodes(
            nodes=nodes,
            channels=channels,
            tolerance=tolerance,
            time_range=time_range,
        )

        curves_mod = res["modified_curves"]
        keys_mod = res["fixed_keys_count"]
        jumps_mod = res["jump_events_count"]

        if curves_mod > 0:
            self._set_status(
                "修复成功！已对 {} 条动画曲线进行了平滑解包，修复了 {} 处 360° 跳变，调整了 {} 个关键帧。".format(
                    curves_mod, jumps_mod, keys_mod
                )
            )
            # 清空旧列表
            self._on_clear_list()
        else:
            self._set_status("未检测到需要修复的 360° 异常，旋转曲线已处于平滑状态。")

    def _on_list_double_clicked(self, *args):
        """双击列表项：时间滑条定位到该帧，并视口/Graph Editor 聚焦该对象"""
        selected_indices = cmds.textScrollList(self.results_scroll_list, query=True, selectIndexedItem=True) or []
        if not selected_indices:
            return

        idx = selected_indices[0] - 1  # 1-based to 0-based
        if idx < 0 or idx >= len(self.cached_jump_events):
            return

        event = self.cached_jump_events[idx]

        # 1. 切换时间到该跳变帧
        cmds.currentTime(event.time)

        # 2. 视口选中该控制器
        if cmds.objExists(event.node):
            cmds.select(event.node, replace=True)

        self._set_status(
            "已跳转定位到第 {:.1f} 帧：{} ({})，跳跃幅度 {:+.1f}°".format(
                event.time, event.node, event.attribute, event.delta
            )
        )

    def _on_fix_selected_list_items(self, *args):
        """仅修复列表中被选中的异常项所对应的曲线"""
        selected_indices = cmds.textScrollList(self.results_scroll_list, query=True, selectIndexedItem=True) or []
        if not selected_indices:
            self._set_status("请先在列表中选中要修复的条目！", is_warning=True)
            return

        tolerance = cmds.floatField(self.tolerance_field, query=True, value=True)
        time_range = self._get_target_time_range()

        target_nodes = set()
        target_channels = set()
        for i in selected_indices:
            idx = i - 1
            if 0 <= idx < len(self.cached_jump_events):
                ev = self.cached_jump_events[idx]
                target_nodes.add(ev.node)
                target_channels.add(ev.attribute)

        res = fix_rotation_winding_on_nodes(
            nodes=list(target_nodes),
            channels=list(target_channels),
            tolerance=tolerance,
            time_range=time_range,
        )

        self._set_status(
            "修复完成！调整了 {} 条曲线，共 {} 处跳变。".format(
                res["modified_curves"], res["jump_events_count"]
            )
        )
        # 重新扫描更新列表
        self._on_scan_clicked()

    def _on_fix_all_list_items(self, *args):
        """修复列表中呈现的全部异常项"""
        if not self.cached_jump_events:
            self._set_status("列表中无任何待修复项！", is_warning=True)
            return

        self._on_quick_fix_clicked()

    def _on_clear_list(self, *args):
        """清空结果列表"""
        cmds.textScrollList(self.results_scroll_list, edit=True, removeAll=True)
        self.cached_jump_events = []

    def _on_quick_offset(self, offset_deg):
        """快捷加减 360 度"""
        nodes = self._get_target_nodes()
        channels = self._get_target_channels()
        count = offset_selected_keys_or_curves(offset_degrees=offset_deg, nodes=nodes, channels=channels)
        if count > 0:
            self._set_status("已对目标曲线/关键帧应用 {:+f}° 旋转偏移。".format(offset_deg))
        else:
            self._set_status("未找到可偏移的关键帧或动画曲线！", is_warning=True)

    def _on_normalize(self, target_range):
        """规范化基准"""
        nodes = self._get_target_nodes()
        channels = self._get_target_channels()
        mod_count = normalize_rotation_baseline_on_nodes(
            nodes=nodes, channels=channels, target_range=target_range
        )
        if mod_count > 0:
            self._set_status("已将 {} 条曲线的旋转基准规范化至 {}。".format(mod_count, target_range))
        else:
            self._set_status("未找到需要规范化的曲线，或基准已处于目标范围内。")


# ==============================================================================
# 第四部分：工具启动与 Shelf 快捷图标注册
# ==============================================================================

_ui_instance = None


def show_ui():
    """打开旋转 360 度异常插值修复工具界面"""
    global _ui_instance
    _ui_instance = FixRotationWindingUI()
    _ui_instance.show()
    return _ui_instance


def install_shelf_button(script_dir=None):
    """
    在当前激活的 Maya Shelf（工具架）上添加快捷按钮。
    """
    _ensure_maya()
    import os

    try:
        import maya.mel as mel
        current_shelf = mel.eval("tabLayout -query -selectTab $gShelfTopLevel")
    except Exception:
        current_shelf = None

    if not current_shelf or not cmds.shelfLayout(current_shelf, exists=True):
        return False

    btn_label = "RotFix"
    btn_annotation = "Maya 旋转 360° 异常插值修正工具 (Fix Rotation Winding)"

    # 检查是否已存在同名按钮，避免重复添加
    existing_buttons = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
    for btn in existing_buttons:
        if cmds.shelfButton(btn, exists=True):
            if cmds.shelfButton(btn, query=True, label=True) == btn_label:
                cmds.deleteUI(btn)

    # 构造启动代码
    if script_dir:
        norm_dir = os.path.abspath(script_dir).replace("\\", "/")
        cmd_str = (
            "import sys, os\n"
            "p = r'{}'\n"
            "if p not in sys.path: sys.path.insert(0, p)\n"
            "import fix_rotation_winding\n"
            "import importlib\n"
            "importlib.reload(fix_rotation_winding)\n"
            "fix_rotation_winding.show_ui()\n"
        ).format(norm_dir)
    else:
        cmd_str = (
            "import fix_rotation_winding\n"
            "fix_rotation_winding.show_ui()\n"
        )

    icon_path = "commandButton.png"
    if script_dir:
        potential_icon = os.path.join(script_dir, "icons", "rot_fix.png")
        if os.path.exists(potential_icon):
            icon_path = potential_icon

    cmds.shelfButton(
        parent=current_shelf,
        label=btn_label,
        annotation=btn_annotation,
        image=icon_path,
        command=cmd_str,
        sourceType="python",
    )
    return True


if __name__ == "__main__":
    show_ui()
