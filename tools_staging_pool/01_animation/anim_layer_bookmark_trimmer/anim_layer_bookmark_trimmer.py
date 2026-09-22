# -*- coding: utf-8 -*-
"""
Anim Layer Bookmark Keyframe Trimmer & Curve Optimizer
(动画层书签关键帧修剪与曲线优化器)
===========================================================
功能简介:
基于 Maya 时间滑块书签 (Time Slider Bookmark)，对选中的物体在当前激活的
动画层（或指定动画层）上执行两类核心操作：

1. ✂️ 关键帧修剪 (Trim Keyframes)：
   只保留指定作用范围内书签端点（起始帧和结束帧）上的关键帧，将其余非端点关键帧安全删除。
   例如：书签为 1~59 和 68~100 时，修剪后仅保留 1、59、68、100 帧。

2. 🎛️ 书签区间曲线优化 (Curve Optimization)：
   在书签的起始和结束位置关键帧（端点帧）绝对保持不变（姿态锁定）的前提下，
   对书签区间内部的动画曲线进行高级优化，提供滑动杆自由调节力度 (Strength 0~100%)：
   - 圆滑曲线 (Smooth Curves)：基于非均匀时间倒数加权高斯平滑滤波，消除抖动噪点。
   - 简化曲线 (Simplify Curves)：开区间自适应容差冗余抽稀，剔除共线与冗余帧。
   - 区间多帧缓入缓出 (Multi-key Ease In/Out)：保持端点绝对不动，内部所有多个关键帧按 Smootherstep S 曲线整体缓动重塑！
   - 端点缓入缓出 (Ease In/Out)：起始帧出切线水平缓出，结束帧入切线水平缓入，手柄权重按力度伸展。
   - 平滑切线 (Smooth Tangents)：自动优化出入切线为柔顺 Spline。
   - 综合优化 (Smart Optimize)：平滑滤波 + 冗余抽稀 + 多帧缓动三重协同。

3. 🔖 灵活的三重书签作用范围 (Bookmark Scope)：
   - 模式 1【全部 (All)】：作用于场景中的所有书签；
   - 模式 2【时间轴范围内 (Playback)】：仅作用于时间轴播放范围 (minTime ~ maxTime) 内的书签；
   - 模式 3【光标框选或所在时间轴 (Selected / Cursor)】：优先识别时间滑块鼠标高亮框选区域，若无框选则自动锁定当前时间滑块光标（指针）所在的书签。
   局部模式下，操作区域严格限定在目标书签范围内，范围外的任何关键帧 100% 保持不动！

核心特性:
- 端点绝对锚定：算法保证各个书签的起始与结束帧的时间点与数值绝对不发生任何漂移。
- 动画层精准隔离：自动识别当前激活的动画层，仅对该层上的专属动画曲线执行操作，绝不污染其他层。
- 完整的撤销机制：包裹在单一原子级 UndoChunk 中，支持 Ctrl+Z 一键撤销。
- 预检模式 (Dry Run)：支持在不改变任何关键帧的前提下，先预览修剪或优化的效果与统计。
- 双模式支持：提供原生 Maya 交互式深色窗口与无界面一键 Python API 调用。
"""

import sys
import maya.cmds as cmds
import maya.mel as mel

TOOL_NAME = "AnimLayerBookmarkTrimmer"
TOOL_TITLE = "动画层书签修剪与曲线优化器 (Trimmer & Optimizer)"
WINDOW_NAME = "AnimLayerBookmarkTrimmerWindow"

# 通道白名单与离散属性黑名单定义
ATTRS_TRANSLATE = {"translateX", "translateY", "translateZ", "tx", "ty", "tz"}
ATTRS_ROTATE = {"rotateX", "rotateY", "rotateZ", "rx", "ry", "rz"}
ATTRS_SCALE = {"scaleX", "scaleY", "scaleZ", "sx", "sy", "sz"}
# 🛡️ 永久安全排除：绝对不作为连续曲线进行平滑/重塑的布尔与离散属性
DISCRETE_EXCLUDES = {
    "visibility", "v", "lodvisibility", "intermediateobject", "overridevisibility",
    "nodestate", "caching", "ghosting"
}


# ==============================================================================
# 底层工具函数与层级/书签检索
# ==============================================================================
def ensure_bookmark_plugin():
    """确保 Maya 内置的 timeSliderBookmark 插件已正确加载"""
    if not cmds.pluginInfo("timeSliderBookmark", query=True, loaded=True):
        try:
            cmds.loadPlugin("timeSliderBookmark")
        except Exception as err:
            cmds.warning(u"加载 timeSliderBookmark 插件失败: {}".format(err))
            return False
    return True


def get_scene_anim_layers():
    """获取场景中所有的动画层列表（按显示次序排序，BaseAnimation 置顶）"""
    layers = cmds.ls(type="animLayer") or []
    valid_layers = [l for l in layers if cmds.objExists(l)]
    if "BaseAnimation" in valid_layers:
        valid_layers.remove("BaseAnimation")
        valid_layers.insert(0, "BaseAnimation")
    return valid_layers


def get_active_anim_layer():
    """
    自动检测当前在 Maya 动画层编辑器中高亮选中的动画层。
    若未选中任何层或仅选中 BaseAnimation，则返回 'BaseAnimation'。
    """
    layers = cmds.ls(type="animLayer") or []
    selected = [l for l in layers if cmds.animLayer(l, query=True, selected=True)]
    custom_selected = [l for l in selected if l != "BaseAnimation"]
    if custom_selected:
        return custom_selected[0]
    if "BaseAnimation" in selected:
        return "BaseAnimation"
    return "BaseAnimation"


def get_selected_channel_box_attributes():
    """
    获取用户当前在 Maya Channel Box (通道栏) 中高亮选中的主属性列表。
    若未选中任何属性，则返回空列表 []。
    """
    try:
        cb = mel.eval('$tmpVar=$gChannelBoxName')
        if cb and cmds.channelBox(cb, exists=True):
            attrs = cmds.channelBox(cb, query=True, selectedMainAttributes=True) or []
            return list(attrs)
    except Exception:
        pass
    return []


def get_plug_for_curve(curve):
    """
    反查动画曲线所驱动的具体节点与属性名（例如 'pSphere1.translateY', 'RootX_M.rotateX'）。
    支持各类动画层混合节点 (animBlendNodeAdditiveRotation, animBlendNodeAdditiveDL, pairBlend 等)。
    若无法通过下游连接精确解析，则返回动画曲线名称。
    """
    try:
        conns = cmds.listConnections(curve + ".output", plugs=True, destination=True, source=False) or []
        if not conns:
            conns = cmds.listConnections(curve, plugs=True, destination=True, source=False) or []

        for conn in conns:
            node = conn.split(".")[0]
            attr = conn.split(".")[1]
            node_type = cmds.nodeType(node)

            # 1. 旋转专用混合节点 (animBlendNodeAdditiveRotation)
            if node_type == "animBlendNodeAdditiveRotation":
                axis = ""
                if attr.endswith("X") or "inputAX" in attr or "inputBX" in attr:
                    axis = "rotateX"
                elif attr.endswith("Y") or "inputAY" in attr or "inputBY" in attr:
                    axis = "rotateY"
                elif attr.endswith("Z") or "inputAZ" in attr or "inputBZ" in attr:
                    axis = "rotateZ"

                dest_plugs = cmds.listConnections(node, plugs=True, destination=True, source=False) or []
                # 优先精确匹配对应轴向 (如 rotateY)
                if axis:
                    for dp in dest_plugs:
                        dp_node, dp_attr = dp.split(".")[0], dp.split(".")[1]
                        if cmds.nodeType(dp_node) != "animLayer" and dp_attr == axis:
                            return dp

                # 兜底匹配任意 rotate 属性
                for dp in dest_plugs:
                    dp_node, dp_attr = dp.split(".")[0], dp.split(".")[1]
                    if cmds.nodeType(dp_node) != "animLayer" and dp_attr.startswith("rotate"):
                        return dp

            # 2. 单轴线性/浮点混合节点 (animBlendNodeAdditiveDL, animBlendNodeAdditive, animBlendNodeAdditiveScale 等)
            elif "animBlendNode" in node_type or "blendColors" in node_type or "pairBlend" in node_type:
                dest_plugs = cmds.listConnections(node, plugs=True, destination=True, source=False) or []
                for dp in dest_plugs:
                    dp_node, dp_attr = dp.split(".")[0], dp.split(".")[1]
                    if cmds.nodeType(dp_node) != "animLayer":
                        return dp

            # 3. 直连目标节点
            else:
                return conn
    except Exception:
        pass
    return curve


def get_layer_curves_for_objects(
    objects,
    layer_name,
    include_translate=True,
    include_rotate=True,
    include_scale=False,
    include_others=False,
    channel_box_priority=True
):
    """
    精准获取指定对象在特定动画层上关联的所有动画曲线 (animCurves)。
    支持通道白名单过滤与 Channel Box (通道栏) 高亮属性智能优先。
    🛡️ 绝对安全排除 visibility (显示隐藏) 与布尔/枚举离散开关！

    参数:
        objects: 目标对象或控制器列表
        layer_name: 动画层名称 ('auto', 'BaseAnimation', 或自定义层)
        include_translate: 是否包含位移通道 (Translate X/Y/Z)
        include_rotate: 是否包含旋转通道 (Rotate X/Y/Z)
        include_scale: 是否包含缩放通道 (Scale X/Y/Z)
        include_others: 是否包含其他自定义连续浮点属性
        channel_box_priority: 是否优先使用 Channel Box 高亮选中的通道
    返回:
        list[str]: 匹配的动画曲线列表 (按名称排序)
    """
    if not objects or not layer_name:
        return []

    if isinstance(objects, (str, bytes)):
        objects = [objects]

    # 1. 检查 Channel Box 高亮属性
    cb_attrs = []
    if channel_box_priority:
        cb_attrs = get_selected_channel_box_attributes()

    # 构建目标属性白名单（若通道栏有高亮，则优先以此为准）
    target_attrs = set()
    use_cb_filter = bool(cb_attrs)
    if use_cb_filter:
        for a in cb_attrs:
            target_attrs.add(a.lower())
    else:
        if include_translate:
            target_attrs.update({a.lower() for a in ATTRS_TRANSLATE})
        if include_rotate:
            target_attrs.update({a.lower() for a in ATTRS_ROTATE})
        if include_scale:
            target_attrs.update({a.lower() for a in ATTRS_SCALE})

    collected_curves = set()
    obj_set = set(objects)

    for obj in objects:
        anim_plugs = cmds.listAnimatable(obj) or []
        for plug in anim_plugs:
            short_attr = plug.split(".")[-1]
            short_lower = short_attr.lower()

            # 🛡️ 核心安全防线：绝对排除 visibility 及离散布尔/枚举属性
            if short_lower in DISCRETE_EXCLUDES:
                continue

            # 检查是否为 bool/enum 离散类型
            try:
                attr_type = cmds.getAttr(plug, type=True)
                if attr_type in ("bool", "enum", "message", "string"):
                    continue
            except Exception:
                pass

            # 通道白名单匹配
            matched = False
            if target_attrs:
                if short_lower in target_attrs:
                    matched = True
            elif include_others:
                matched = True

            if not matched:
                continue

            # 查询动画层曲线
            try:
                curves = cmds.animLayer(layer_name, query=True, findCurveForPlug=plug) or []
                for c in curves:
                    if c and cmds.objExists(c):
                        collected_curves.add(c)
            except Exception:
                pass

    # 若为 BaseAnimation 且无动画层 curve，兜底匹配直接连接曲线
    if layer_name == "BaseAnimation" and not collected_curves:
        for obj in objects:
            direct_curves = cmds.findKeyframe(obj, curve=True) or []
            for c in direct_curves:
                if c and cmds.objExists(c):
                    # 对直连曲线做通道与排除校验
                    plug = get_plug_for_curve(c)
                    short_attr = plug.split(".")[-1]
                    short_lower = short_attr.lower()
                    if short_lower in DISCRETE_EXCLUDES:
                        continue
                    try:
                        attr_type = cmds.getAttr(plug, type=True)
                        if attr_type in ("bool", "enum", "message", "string"):
                            continue
                    except Exception:
                        pass
                    matched = False
                    if target_attrs:
                        if short_lower in target_attrs:
                            matched = True
                    elif include_others:
                        matched = True
                    if matched:
                        collected_curves.add(c)

    return sorted(list(collected_curves))


def get_bookmark_details():
    """
    获取场景中所有时间滑块书签的详细信息。
    返回:
        list[dict]: 包含 node, name, start, stop 的书签详情列表（按起始时间升序排列）。
    """
    ensure_bookmark_plugin()
    bookmarks = cmds.ls(type="timeSliderBookmark") or []
    details = []
    for bm in bookmarks:
        try:
            st = cmds.getAttr(bm + ".timeRangeStart")
            sp = cmds.getAttr(bm + ".timeRangeStop")
            if st is not None and sp is not None:
                start_val = float(st)
                stop_val = float(sp)
                if start_val > stop_val:
                    start_val, stop_val = stop_val, start_val
                name_attr = cmds.getAttr(bm + ".name") or bm
                details.append({
                    "node": bm,
                    "name": name_attr,
                    "start": round(start_val, 4),
                    "stop": round(stop_val, 4)
                })
        except Exception:
            pass
    details.sort(key=lambda x: x["start"])
    return details


def get_filtered_bookmarks(scope="all"):
    """
    根据 3 种范围规则筛选生效的书签列表：
    参数:
        scope (str): 范围模式:
            - 'all': 全部书签 (场景中所有书签)
            - 'playback': 仅时间轴播放范围 (playbackOptions minTime ~ maxTime) 内的书签
            - 'selected': 优先取时间滑块鼠标框选区域，若无框选则取当前时间滑块光标所在书签
    返回:
        tuple[list[dict], str]: (匹配的书签列表, 范围描述说明文字)
    """
    all_bms = get_bookmark_details()
    if not all_bms:
        return [], u"场景中无任何书签"

    if scope == "all" or not scope:
        desc = u"全部书签 (共 {} 个)".format(len(all_bms))
        return all_bms, desc

    if scope == "playback":
        min_t = float(cmds.playbackOptions(query=True, minTime=True))
        max_t = float(cmds.playbackOptions(query=True, maxTime=True))
        matched = []
        for bm in all_bms:
            if bm["start"] <= max_t and bm["stop"] >= min_t:
                matched.append(bm)
        desc = u"时间轴播放范围 ({} ~ {}): 匹配到 {} 个书签".format(
            int(min_t), int(max_t), len(matched)
        )
        return matched, desc

    if scope == "selected":
        has_range = False
        sel_range = None
        try:
            slider = mel.eval('$tmpVar=$gPlayBackSlider')
            if slider and cmds.timeControl(slider, exists=True):
                if cmds.timeControl(slider, query=True, rangeVisible=True):
                    r = cmds.timeControl(slider, query=True, rangeArray=True)
                    if r and len(r) >= 2:
                        s1, s2 = float(r[0]), float(r[1])
                        if abs(s2 - s1) > 0.001:
                            has_range = True
                            sel_range = (min(s1, s2), max(s1, s2))
        except Exception:
            pass

        if has_range and sel_range:
            matched = []
            for bm in all_bms:
                if bm["start"] <= sel_range[1] and bm["stop"] >= sel_range[0]:
                    matched.append(bm)
            desc = u"时间滑块框选范围 ({} ~ {}): 匹配到 {} 个书签".format(
                round(sel_range[0], 2), round(sel_range[1], 2), len(matched)
            )
            return matched, desc
        else:
            curr_time = float(cmds.currentTime(query=True))
            matched = [bm for bm in all_bms if bm["start"] <= curr_time <= bm["stop"]]
            if matched:
                desc = u"当前光标所在时间帧 ({}): 匹配到书签 [{}] ({}~{})".format(
                    int(curr_time), matched[0]["name"], matched[0]["start"], matched[0]["stop"]
                )
                return matched, desc
            else:
                closest = min(all_bms, key=lambda b: min(abs(b["start"] - curr_time), abs(b["stop"] - curr_time)))
                desc = u"当前光标帧 ({}) 未落入书签，已自动定位最邻近书签 [{}] ({}~{})".format(
                    int(curr_time), closest["name"], closest["start"], closest["stop"]
                )
                return [closest], desc

    return all_bms, u"全部书签"


def get_bookmark_boundary_frames(scope="all", tolerance=0.001):
    """
    根据 scope 提取匹配书签的起始与结束时间点列表（升序、去重）。
    例如书签为 1~59 和 68~100 时，返回 [1.0, 59.0, 68.0, 100.0]。
    """
    bms, _ = get_filtered_bookmarks(scope=scope)
    frames = set()
    for d in bms:
        frames.add(d["start"])
        frames.add(d["stop"])

    sorted_frames = sorted(list(frames))
    unique_frames = []
    for f in sorted_frames:
        if not unique_frames or abs(f - unique_frames[-1]) > tolerance:
            unique_frames.append(f)
    return unique_frames


# ==============================================================================
# 算法核心一：关键帧修剪执行 (Trim Keyframes)
# ==============================================================================
def trim_layer_keyframes_by_bookmarks(
    objects=None,
    layer="auto",
    scope="all",
    include_translate=True,
    include_rotate=True,
    include_scale=False,
    include_others=False,
    channel_box_priority=True,
    ensure_keys_at_bounds=False,
    dry_run=False
):
    """
    核心修剪执行函数：
    在指定动画层中，只保留目标书签范围起始和结束时间点处的关键帧，将其余帧安全删除。

    参数:
        objects (list[str] | str, optional): 目标物体/控制器。若为 None 则使用当前选中的物体。
        layer (str): 目标动画层。'auto' (自动检测当前选中层), 'BaseAnimation' 或具体层名称。
        scope (str): 书签范围:
            - 'all': 全部书签（全曲线上仅保留所有书签端点）
            - 'playback': 仅在时间轴播放范围内修剪，播放范围外的关键帧完全不受影响
            - 'selected': 仅在光标框选/所在书签范围内修剪，范围外的关键帧完全不受影响
        include_translate (bool): 是否包含位移通道 (Translate X/Y/Z)
        include_rotate (bool): 是否包含旋转通道 (Rotate X/Y/Z)
        include_scale (bool): 是否包含缩放通道 (Scale X/Y/Z)
        include_others (bool): 是否包含其他浮点属性
        channel_box_priority (bool): 是否优先使用 Channel Box 高亮选中的通道
        ensure_keys_at_bounds (bool): 若书签端点处物体原本没有关键帧，是否自动打入关键帧以固化姿态。
        dry_run (bool): 是否仅进行预检分析，不实际删除任何关键帧。

    返回:
        dict: 包含 success, dry_run, layer, objects, keep_frames, deleted_keys, remaining_keys, message 的结果字典。
    """
    target_objs = objects if objects is not None else (cmds.ls(sl=True) or [])
    if isinstance(target_objs, (str, bytes)):
        target_objs = [target_objs]

    if not target_objs:
        msg = u"【修剪拦截】未选择任何物体！请先在场景中选择带有动画的物体或控制器。"
        cmds.warning(msg)
        return {"success": False, "message": msg, "objects": [], "layer": layer}

    matched_bms, scope_desc = get_filtered_bookmarks(scope=scope)
    if not matched_bms:
        msg = u"【修剪拦截】在所选范围 [{}] 下未找到任何有效的时间滑块书签！".format(scope_desc)
        cmds.warning(msg)
        return {"success": False, "message": msg, "objects": target_objs, "layer": layer}

    keep_frames = get_bookmark_boundary_frames(scope=scope)
    actual_layer = get_active_anim_layer() if (layer == "auto" or not layer) else layer

    curves = get_layer_curves_for_objects(
        target_objs,
        actual_layer,
        include_translate=include_translate,
        include_rotate=include_rotate,
        include_scale=include_scale,
        include_others=include_others,
        channel_box_priority=channel_box_priority
    )
    if not curves:
        msg = u"【修剪拦截】所选物体在动画层 [{}] 上未找到符合通道过滤条件的动画曲线！\n" \
              u"❓ 原因排查: 关键帧可能在其他层 (如 BaseAnimation)，或通道未被勾选 (当前已永久排除 visibility 显示隐藏)。".format(actual_layer)
        cmds.warning(msg)
        return {"success": False, "message": msg, "objects": target_objs, "layer": actual_layer, "curves_count": 0}

    # 通道描述
    cb_attrs = get_selected_channel_box_attributes() if channel_box_priority else []
    if cb_attrs:
        ch_desc = u"通道栏高亮优先: [{}]".format(u", ".join(cb_attrs))
    else:
        active_channels = []
        if include_translate: active_channels.append(u"位移")
        if include_rotate: active_channels.append(u"旋转")
        if include_scale: active_channels.append(u"缩放")
        if include_others: active_channels.append(u"其他浮点")
        ch_desc = u"[{}] (已安全排除显示隐藏)".format(u", ".join(active_channels) if active_channels else u"无")

    if scope == "all":
        bound_range = None
    else:
        min_bound = min(bm["start"] for bm in matched_bms)
        max_bound = max(bm["stop"] for bm in matched_bms)
        bound_range = (min_bound, max_bound)

    # 逐对象、逐曲线诊断与统计明细
    modified_reports = []
    unmodified_reports = []

    # 1. 检查是否有选中对象完全没有动画曲线
    for obj in target_objs:
        obj_curves = get_layer_curves_for_objects(
            [obj],
            actual_layer,
            include_translate=include_translate,
            include_rotate=include_rotate,
            include_scale=include_scale,
            include_others=include_others,
            channel_box_priority=channel_box_priority
        )
        if not obj_curves:
            unmodified_reports.append(
                u"  • 物体 [{}] 在动画层 [{}] 上无符合通道条件的动画曲线 (请检查关键帧是否在其他层，或对象未添加到该层)".format(obj, actual_layer)
            )

    # 2. 分析每根曲线在各个书签区间中的修剪情况
    curve_actions = {}
    total_deleted_keys = set()
    for c in curves:
        plug = get_plug_for_curve(c)
        c_keys = cmds.keyframe(c, query=True, timeChange=True) or []
        c_unique_keys = sorted(list(set([round(float(k), 4) for k in c_keys])))

        c_to_delete = []
        for k in c_unique_keys:
            if bound_range is not None:
                if k < (bound_range[0] - 0.001) or k > (bound_range[1] + 0.001):
                    continue
            is_keep = any(abs(k - kf) < 0.001 for kf in keep_frames)
            if not is_keep:
                c_to_delete.append(k)

        curve_actions[c] = c_to_delete
        total_deleted_keys.update(c_to_delete)

        if c_to_delete:
            del_str = u", ".join([str(k) for k in c_to_delete])
            modified_reports.append(u"  • [{}] 删除非端点帧: [{}]，保留端点: {}".format(plug, del_str, keep_frames))
        else:
            # 判断无删除的原因
            in_bound_keys = [k for k in c_unique_keys if (bound_range is None or (bound_range[0]-0.001 <= k <= bound_range[1]+0.001))]
            if not in_bound_keys:
                unmodified_reports.append(u"  • [{}] 作用范围内无任何关键帧".format(plug))
            else:
                unmodified_reports.append(u"  • [{}] 仅包含端点帧 {}，无需清理非端点帧".format(plug, in_bound_keys))

    sorted_keys_to_delete = sorted(list(total_deleted_keys))

    if dry_run:
        range_text = u"全场景" if bound_range is None else u"{} ~ {}".format(bound_range[0], bound_range[1])
        title = u"🔍【预检修剪详细报告】"
        header = u"{}\n" \
                 u"🎯 目标层: [{}] | 作用范围: {}\n" \
                 u"🎯 作用通道: {}\n" \
                 u"⏳ 作用时间段: [{}] | 保留端点帧: {}\n" \
                 u"📌 涉及曲线数: {} 根 | 预计清理非端点帧总计: {} 处\n" \
                 u"------------------------------------------------------------\n".format(
                     title, actual_layer, scope_desc, ch_desc, range_text, keep_frames, len(curves), len(sorted_keys_to_delete)
                 )

        body_mod = u"✂️【预计将修剪的对象与属性】(共 {} 项):\n{}\n".format(
            len(modified_reports), u"\n".join(modified_reports) if modified_reports else u"  (无属性需要修剪)"
        )
        body_unmod = u"\n⚪【未修剪/跳过的对象与属性及原因】(共 {} 项):\n{}".format(
            len(unmodified_reports), u"\n".join(unmodified_reports) if unmodified_reports else u"  (无跳过项)"
        )

        full_msg = header + body_mod + body_unmod
        return {
            "success": True,
            "dry_run": True,
            "layer": actual_layer,
            "scope": scope,
            "objects": target_objs,
            "keep_frames": keep_frames,
            "keys_to_delete": sorted_keys_to_delete,
            "curves_count": len(curves),
            "message": full_msg
        }

    cmds.undoInfo(openChunk=True, chunkName="TrimLayerKeyframesByBookmarks")
    try:
        if ensure_keys_at_bounds:
            for kf in keep_frames:
                try:
                    cmds.setKeyframe(curves, time=(kf, kf), insert=True)
                except Exception:
                    pass

        for c, to_del in curve_actions.items():
            for k in to_del:
                cmds.cutKey(c, time=(k, k), clear=True)

    finally:
        cmds.undoInfo(closeChunk=True)

    post_keys = cmds.keyframe(curves, query=True, timeChange=True) or []
    post_unique_keys = sorted(list(set([round(float(k), 4) for k in post_keys])))

    title = u"✅【关键帧修剪成功执行报告】"
    header = u"{}\n" \
             u"🎯 目标层: [{}] | 作用范围: {}\n" \
             u"🎯 作用通道: {}\n" \
             u"📌 涉及曲线数: {} 根 | 成功删除非端点帧总计: {} 处\n" \
             u"🔒 当前保留端点帧为: {}\n" \
             u"------------------------------------------------------------\n".format(
                 title, actual_layer, scope_desc, ch_desc, len(curves), len(sorted_keys_to_delete), post_unique_keys
             )

    body_mod = u"✂️【已成功修剪的对象与属性】(共 {} 项):\n{}\n".format(
        len(modified_reports), u"\n".join(modified_reports) if modified_reports else u"  (无属性修剪)"
    )
    body_unmod = u"\n⚪【未修改/跳过的对象与属性及原因】(共 {} 项):\n{}".format(
        len(unmodified_reports), u"\n".join(unmodified_reports) if unmodified_reports else u"  (无跳过项)"
    )

    full_success_msg = header + body_mod + body_unmod

    return {
        "success": True,
        "dry_run": False,
        "layer": actual_layer,
        "scope": scope,
        "objects": target_objs,
        "keep_frames": keep_frames,
        "deleted_keys": sorted_keys_to_delete,
        "remaining_keys": post_unique_keys,
        "curves_count": len(curves),
        "message": full_success_msg
    }


# ==============================================================================
# 算法核心二：书签区间动画曲线优化 (Smooth, Simplify, Multi-key Ease, Ease In/Out)
# ==============================================================================
def smootherstep(u, bias=0.5):
    """
    带权重中心偏置 (Weight Bias) 的 Ken Perlin's Smootherstep 缓动函数。
    参数:
        u (float): 归一化时间 0.0 ~ 1.0
        bias (float): 权重偏置 0.0 ~ 1.0 (默认 0.5 居中)
            - bias = 0.5: 对称居中缓入缓出 (标准 Smootherstep)
            - bias < 0.5: 权重偏向起点 (滞留起点时间更长，缓出加重，后期发力)
            - bias > 0.5: 权重偏向终点 (快速到达终点附近，缓入加重，平缓刹车)
    """
    u = max(0.0, min(1.0, float(u)))
    b = max(0.01, min(0.99, float(bias)))
    if abs(b - 0.5) > 1e-4:
        # Schlick's Bias 双射变形映射
        denom = (1.0 / b - 2.0) * (1.0 - u) + 1.0
        if abs(denom) > 1e-6:
            u = u / denom
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def apply_multikey_ease_interval(curve, start_time, stop_time, strength=0.5, bias=0.5):
    """
    在单个书签区间 [start_time, stop_time] 内，
    在保持端点（起始与结束帧）数值和时间绝对不变的前提下，
    对区间内的所有多个内部关键帧整体应用 S 曲线缓入缓出 (Smootherstep S-Curve) 重塑。
    支持通过 bias 滑杆调控权重偏向中间、起点或终点。
    
    参数:
        curve (str): 动画曲线节点名
        start_time (float): 起始端点时间
        stop_time (float): 结束端点时间
        strength (float): 缓动重塑力度 0.0 ~ 1.0 (滑动条控制)
        bias (float): 权重中心偏置 0.0 ~ 1.0 (默认 0.5 中间)
    """
    if strength <= 0.0:
        return 0

    _ensure_boundary_keys_on_curve(curve, start_time, stop_time)

    key_times = cmds.keyframe(curve, time=(start_time, stop_time), query=True, timeChange=True) or []
    key_times = sorted(list(set([round(float(t), 4) for t in key_times])))
    if len(key_times) < 3:
        return 0

    t0, tn = key_times[0], key_times[-1]
    dt = tn - t0
    if dt < 1e-4:
        return 0

    v0 = cmds.keyframe(curve, time=(t0, t0), query=True, valueChange=True)[0]
    vn = cmds.keyframe(curve, time=(tn, tn), query=True, valueChange=True)[0]
    dv = vn - v0

    inner_indices = range(1, len(key_times) - 1)
    for i in inner_indices:
        t_curr = key_times[i]
        u = (t_curr - t0) / dt
        ease_u = smootherstep(u, bias=bias)
        target_val = v0 + ease_u * dv

        orig_val = cmds.keyframe(curve, time=(t_curr, t_curr), query=True, valueChange=True)[0]
        blended_val = (1.0 - strength) * orig_val + strength * target_val
        cmds.keyframe(curve, time=(t_curr, t_curr), valueChange=blended_val)

    try:
        cmds.keyTangent(curve, edit=True, weightedTangents=True)
        cmds.keyTangent(curve, time=(t0, t0), edit=True, ott="flat")
        cmds.keyTangent(curve, time=(tn, tn), edit=True, itt="flat")

        # 根据 bias 调配起止端点加权手柄长度
        base_multiplier = 1.0 + (strength * 1.5)
        out_bias_factor = max(0.2, min(2.0, 2.0 * (1.0 - bias)))
        in_bias_factor = max(0.2, min(2.0, 2.0 * bias))

        out_w = cmds.keyTangent(curve, time=(t0, t0), query=True, outWeight=True)
        if out_w and out_w[0] is not None:
            cmds.keyTangent(curve, time=(t0, t0), edit=True, outWeight=out_w[0] * base_multiplier * out_bias_factor)

        in_w = cmds.keyTangent(curve, time=(tn, tn), query=True, inWeight=True)
        if in_w and in_w[0] is not None:
            cmds.keyTangent(curve, time=(tn, tn), edit=True, inWeight=in_w[0] * base_multiplier * in_bias_factor)

        for i in inner_indices:
            cmds.keyTangent(curve, time=(key_times[i], key_times[i]), edit=True, itt="spline", ott="spline")
    except Exception:
        pass

    return len(inner_indices)


def smooth_curve_interval(curve, start_time, stop_time, strength=0.5):
    """
    在单个书签区间 [start_time, stop_time] 内平滑关键帧值。
    端点 start_time 与 stop_time 的关键帧值严格保持不变！
    采用非均匀时间倒数加权滤波，结合 strength 调控迭代轮次与平滑混合率。
    """
    if strength <= 0.0:
        return 0

    _ensure_boundary_keys_on_curve(curve, start_time, stop_time)

    key_times = cmds.keyframe(curve, time=(start_time, stop_time), query=True, timeChange=True) or []
    key_times = sorted(list(set([round(float(t), 4) for t in key_times])))
    if len(key_times) < 3:
        return 0

    inner_indices = range(1, len(key_times) - 1)
    iterations = 1 if strength < 0.4 else (2 if strength < 0.75 else 3)

    for _ in range(iterations):
        current_values = []
        for t in key_times:
            val = cmds.keyframe(curve, time=(t, t), query=True, valueChange=True)[0]
            current_values.append(val)

        new_values = list(current_values)
        for i in inner_indices:
            t_prev, t_curr, t_next = key_times[i - 1], key_times[i], key_times[i + 1]
            v_prev, v_curr, v_next = current_values[i - 1], current_values[i], current_values[i + 1]

            dt_prev = max(0.001, t_curr - t_prev)
            dt_next = max(0.001, t_next - t_curr)
            w_prev = 1.0 / dt_prev
            w_next = 1.0 / dt_next
            target_val = (v_prev * w_prev + v_next * w_next) / (w_prev + w_next)

            blended_val = (1.0 - strength) * v_curr + strength * target_val
            new_values[i] = blended_val

        for i in inner_indices:
            cmds.keyframe(curve, time=(key_times[i], key_times[i]), valueChange=new_values[i])

    cmds.keyTangent(curve, time=(start_time, stop_time), edit=True, itt="spline", ott="spline")
    return len(inner_indices)


def simplify_curve_interval(curve, start_time, stop_time, strength=0.5):
    """
    在单个书签区间内部开区间 (start_time, stop_time) 内简化冗余关键帧。
    绝对不删除 start_time 与 stop_time 的端点关键帧！
    """
    if strength <= 0.0:
        return 0

    _ensure_boundary_keys_on_curve(curve, start_time, stop_time)

    inner_range = (start_time + 0.001, stop_time - 0.001)
    keys_before = cmds.keyframe(curve, time=inner_range, query=True, timeChange=True) or []
    if not keys_before:
        return 0

    values = cmds.keyframe(curve, time=inner_range, query=True, valueChange=True) or [0.0]
    val_span = max(0.1, max(values) - min(values))

    val_tol = 0.005 + (strength ** 1.5) * (val_span * 0.15)
    time_tol = 0.01 + strength * 0.1

    cmds.simplify(curve, time=inner_range, timeTolerance=time_tol, valueTolerance=val_tol)
    keys_after = cmds.keyframe(curve, time=inner_range, query=True, timeChange=True) or []
    return max(0, len(keys_before) - len(keys_after))


def apply_ease_in_out_interval(curve, start_time, stop_time, strength=0.5, bias=0.5, soften_adjacent=True):
    """
    在书签端点及其紧邻关键帧上应用缓入缓出 (Ease In / Ease Out)。
    - start_time 起始端点：出切线设为 flat，手柄权重根据 strength 与 bias 调配；
    - stop_time 结束端点：入切线设为 flat，手柄权重根据 strength 与 bias 调配；
    - 开启加权切线 weightedTangents=True，手柄按倍率扩展；
    - bias 调控权重偏向：bias < 0.5 起点缓出加权更大；bias > 0.5 终点缓入加权更大；bias = 0.5 居中对称；
    - 若 soften_adjacent 为 True：对紧邻端点的内部第一帧和倒数第一帧采用平滑过渡。
    """
    _ensure_boundary_keys_on_curve(curve, start_time, stop_time)

    try:
        cmds.keyTangent(curve, edit=True, weightedTangents=True)
    except Exception:
        pass

    cmds.keyTangent(curve, time=(start_time, start_time), edit=True, ott="flat")
    cmds.keyTangent(curve, time=(stop_time, stop_time), edit=True, itt="flat")

    base_multiplier = 1.0 + (strength * 1.5)
    out_bias_factor = max(0.2, min(2.0, 2.0 * (1.0 - bias)))
    in_bias_factor = max(0.2, min(2.0, 2.0 * bias))

    try:
        out_w = cmds.keyTangent(curve, time=(start_time, start_time), query=True, outWeight=True)
        if out_w and out_w[0] is not None:
            cmds.keyTangent(curve, time=(start_time, start_time), edit=True, outWeight=out_w[0] * base_multiplier * out_bias_factor)
    except Exception:
        pass

    try:
        in_w = cmds.keyTangent(curve, time=(stop_time, stop_time), query=True, inWeight=True)
        if in_w and in_w[0] is not None:
            cmds.keyTangent(curve, time=(stop_time, stop_time), edit=True, inWeight=in_w[0] * base_multiplier * in_bias_factor)
    except Exception:
        pass

    if soften_adjacent:
        inner_times = cmds.keyframe(curve, time=(start_time + 0.001, stop_time - 0.001), query=True, timeChange=True) or []
        inner_times = sorted(list(set([round(float(t), 4) for t in inner_times])))
        if len(inner_times) >= 2:
            t_first = inner_times[0]
            cmds.keyTangent(curve, time=(t_first, t_first), edit=True, itt="spline", ott="spline")
            t_last = inner_times[-1]
            cmds.keyTangent(curve, time=(t_last, t_last), edit=True, itt="spline", ott="spline")

    return 2


def smooth_tangents_interval(curve, start_time, stop_time):
    """设置区间内所有关键帧的出入切线为平滑 Spline"""
    cmds.keyTangent(curve, time=(start_time, stop_time), edit=True, itt="spline", ott="spline")


def _ensure_boundary_keys_on_curve(curve, start_time, stop_time):
    """确保在书签端点处存在关键帧，起到姿态锚定作用"""
    st_keys = cmds.keyframe(curve, time=(start_time, start_time), query=True, timeChange=True) or []
    if not st_keys:
        try:
            cmds.setKeyframe(curve, time=(start_time, start_time), insert=True)
        except Exception:
            pass

    sp_keys = cmds.keyframe(curve, time=(stop_time, stop_time), query=True, timeChange=True) or []
    if not sp_keys:
        try:
            cmds.setKeyframe(curve, time=(stop_time, stop_time), insert=True)
        except Exception:
            pass


def optimize_layer_curves_by_bookmarks(
    objects=None,
    layer="auto",
    scope="all",
    mode="smooth",
    strength=0.5,
    bias=0.5,
    include_translate=True,
    include_rotate=True,
    include_scale=False,
    include_others=False,
    channel_box_priority=True,
    ease_bounds=True,
    dry_run=False
):
    """
    书签区间动画曲线优化主入口：
    在选定作用范围内各个书签的起始与结束位置（端点帧）严格保持不变的前提下，
    对书签区间内部的动画曲线进行平滑、简化、多帧 S 曲线重塑或端点缓入缓出。
    🛡️ 默认聚焦位移 (Translate) 与旋转 (Rotate)，且永久排除显示隐藏 (visibility) 等离散通道！

    参数:
        objects (list[str] | str, optional): 目标物体。若为 None 则使用当前选中的物体。
        layer (str): 目标动画层。'auto', 'BaseAnimation' 或具体层名称。
        scope (str): 书签作用范围: 'all', 'playback', 'selected'。
        mode (str): 优化模式:
            - 'smooth': 圆滑曲线 (消除噪点抖动)
            - 'simplify': 简化曲线 (剔除冗余帧)
            - 'multikey_ease': 区间多帧缓入缓出 (内部多帧按 Smootherstep S 曲线整体缓动重塑)
            - 'ease': 端点前后缓入缓出 (起止平缓手柄加权)
            - 'smart': 综合优化 (平滑 + 简化 + 缓动 + 切线)
            - 'tangents': 平滑切线 (出入切线优化为 Spline)
        strength (float): 优化力度 0.0 ~ 1.0 (对应滑动杆 0% ~ 100%)。
        bias (float): 权重偏置 0.0 ~ 1.0 (默认 0.5 居中，<0.5 偏向起点，>0.5 偏向终点)。
        include_translate (bool): 是否包含位移通道 (Translate X/Y/Z)
        include_rotate (bool): 是否包含旋转通道 (Rotate X/Y/Z)
        include_scale (bool): 是否包含缩放通道 (Scale X/Y/Z)
        include_others (bool): 是否包含其他浮点属性
        channel_box_priority (bool): 是否优先使用 Channel Box 高亮选中的通道
        ease_bounds (bool): 是否在优化时同时应用端点前后缓入缓出。
        dry_run (bool): 是否仅进行预检分析，不实际修改曲线。

    返回:
        dict: 执行结果统计与状态字典。
    """
    target_objs = objects if objects is not None else (cmds.ls(sl=True) or [])
    if isinstance(target_objs, (str, bytes)):
        target_objs = [target_objs]

    if not target_objs:
        msg = u"【优化拦截】未选择任何物体！请先在场景中选择带有动画的物体或控制器。"
        cmds.warning(msg)
        return {"success": False, "message": msg}

    matched_bms, scope_desc = get_filtered_bookmarks(scope=scope)
    if not matched_bms:
        msg = u"【优化拦截】在所选范围 [{}] 下未找到任何有效的时间滑块书签！".format(scope_desc)
        cmds.warning(msg)
        return {"success": False, "message": msg}

    actual_layer = get_active_anim_layer() if (layer == "auto" or not layer) else layer
    curves = get_layer_curves_for_objects(
        target_objs,
        actual_layer,
        include_translate=include_translate,
        include_rotate=include_rotate,
        include_scale=include_scale,
        include_others=include_others,
        channel_box_priority=channel_box_priority
    )
    if not curves:
        msg = u"【优化拦截】所选物体在动画层 [{}] 上未找到符合通道过滤条件的动画曲线！\n" \
              u"❓ 原因排查: 关键帧可能打在其他动画层 (如 BaseAnimation)，或通道未被勾选 (当前已永久排除 visibility 显示隐藏)。".format(actual_layer)
        cmds.warning(msg)
        return {"success": False, "message": msg}

    # 通道描述
    cb_attrs = get_selected_channel_box_attributes() if channel_box_priority else []
    if cb_attrs:
        ch_desc = u"通道栏高亮优先: [{}]".format(u", ".join(cb_attrs))
    else:
        active_channels = []
        if include_translate: active_channels.append(u"位移")
        if include_rotate: active_channels.append(u"旋转")
        if include_scale: active_channels.append(u"缩放")
        if include_others: active_channels.append(u"其他浮点")
        ch_desc = u"[{}] (已安全排除显示隐藏)".format(u", ".join(active_channels) if active_channels else u"无")

    mode_labels = {
        "smooth": u"圆滑曲线 (Smooth)",
        "simplify": u"简化曲线 (Simplify)",
        "multikey_ease": u"区间多帧缓入缓出 (Multi-key Ease S-Curve)",
        "ease": u"端点缓入缓出 (Ease In/Out)",
        "tangents": u"平滑切线 (Tangents)",
        "smart": u"综合优化 (Smart Optimize)"
    }
    mode_label = mode_labels.get(mode, mode)

    bias_label = u"居中 0.50 (对称)" if abs(bias - 0.5) < 0.01 else (
        u"偏向起点 {:.2f} (滞留起点/缓出重)".format(bias) if bias < 0.5 else u"偏向终点 {:.2f} (滞留终点/缓入重)".format(bias)
    )

    # 诊断数据收集
    modified_reports = []
    unmodified_reports = []

    # 1. 检查是否有选中对象完全没有动画曲线
    for obj in target_objs:
        obj_curves = get_layer_curves_for_objects(
            [obj],
            actual_layer,
            include_translate=include_translate,
            include_rotate=include_rotate,
            include_scale=include_scale,
            include_others=include_others,
            channel_box_priority=channel_box_priority
        )
        if not obj_curves:
            unmodified_reports.append(
                u"  • 物体 [{}] 在动画层 [{}] 上无符合通道条件的动画曲线 (请检查关键帧是否在其他层，或对象未添加到该层)".format(obj, actual_layer)
            )

    if dry_run:
        total_inner_keys = 0
        for bm in matched_bms:
            st, sp = bm["start"], bm["stop"]
            for c in curves:
                plug = get_plug_for_curve(c)
                k_times = cmds.keyframe(c, time=(st, sp), query=True, timeChange=True) or []
                k_times = sorted(list(set([round(float(t), 4) for t in k_times])))
                count = len(k_times)
                if count == 0:
                    unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 区间内无任何关键帧".format(plug, bm["name"], st, sp))
                elif count < 3:
                    unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 仅有 {} 个端点帧，无内部待优化关键帧 (端点依法锁定不变)".format(plug, bm["name"], st, sp, count))
                else:
                    inner_count = count - 2
                    total_inner_keys += inner_count
                    v0 = cmds.keyframe(c, time=(st, st), query=True, valueChange=True)[0]
                    vn = cmds.keyframe(c, time=(sp, sp), query=True, valueChange=True)[0]
                    if mode in ["multikey_ease", "smart"] and abs(vn - v0) < 1e-4:
                        unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 端点数值相同 ({:.2f} 水平平线)，位移重塑差为 0".format(plug, bm["name"], st, sp, v0))
                    else:
                        modified_reports.append(u"  • [{}] 书签 [{}]({}~{}): 预计优化 {} 个内部帧 (端点锁定不变)".format(plug, bm["name"], st, sp, inner_count))

        title = u"🔍【预检曲线优化详细报告】"
        header = u"{}\n" \
                 u"🎯 目标层: [{}] | 涉及曲线: {} 根\n" \
                 u"🎯 作用通道: {}\n" \
                 u"🔖 作用书签范围: {}\n" \
                 u"🎛️ 优化模式: {} | 力度: {:.0%} | 权重分布 (Bias): {}\n" \
                 u"🌊 端点缓入缓出: {}\n" \
                 u"------------------------------------------------------------\n".format(
                     title, actual_layer, len(curves), ch_desc, scope_desc, mode_label, strength, bias_label,
                     u"启用" if (ease_bounds or mode in ["ease", "multikey_ease"]) else u"未勾选"
                 )

        body_mod = u"✅【预计将优化的对象与属性】(共 {} 项):\n{}\n".format(
            len(modified_reports), u"\n".join(modified_reports) if modified_reports else u"  (无属性待优化)"
        )
        body_unmod = u"\n⚠️【未修改/跳过的对象与属性及原因诊断】(共 {} 项):\n{}".format(
            len(unmodified_reports), u"\n".join(unmodified_reports) if unmodified_reports else u"  (无跳过项)"
        )

        full_msg = header + body_mod + body_unmod
        return {
            "success": True,
            "dry_run": True,
            "layer": actual_layer,
            "scope": scope,
            "mode": mode,
            "strength": strength,
            "bias": bias,
            "curves_count": len(curves),
            "inner_keys_count": total_inner_keys,
            "message": full_msg
        }

    cmds.undoInfo(openChunk=True, chunkName="OptimizeLayerCurvesByBookmarks")
    smoothed_pts = 0
    simplified_keys = 0
    eased_multikey_count = 0
    eased_bounds_count = 0

    try:
        for bm in matched_bms:
            st, sp = bm["start"], bm["stop"]
            for c in curves:
                plug = get_plug_for_curve(c)
                _ensure_boundary_keys_on_curve(c, st, sp)
                orig_v_st = cmds.keyframe(c, time=(st, st), query=True, valueChange=True)[0]
                orig_v_sp = cmds.keyframe(c, time=(sp, sp), query=True, valueChange=True)[0]

                k_times = cmds.keyframe(c, time=(st, sp), query=True, timeChange=True) or []
                k_times = sorted(list(set([round(float(t), 4) for t in k_times])))
                count = len(k_times)

                if count < 3 and mode != "ease":
                    if count == 0:
                        unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 区间内无任何关键帧".format(plug, bm["name"], st, sp))
                    else:
                        unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 仅包含 {} 个端点帧，无内部关键帧可优化 (端点依法锁定不变)".format(plug, bm["name"], st, sp, count))
                else:
                    # 记录优化前的值
                    pre_vals = {t: cmds.keyframe(c, time=(t, t), query=True, valueChange=True)[0] for t in k_times}

                    # 执行对应算法
                    c_sm = 0
                    c_si = 0
                    c_em = 0
                    c_eb = 0

                    if mode == "smooth":
                        c_sm = smooth_curve_interval(c, st, sp, strength=strength)
                        if ease_bounds:
                            c_eb = apply_ease_in_out_interval(c, st, sp, strength=strength, bias=bias)
                    elif mode == "simplify":
                        c_si = simplify_curve_interval(c, st, sp, strength=strength)
                        if ease_bounds:
                            c_eb = apply_ease_in_out_interval(c, st, sp, strength=strength, bias=bias)
                    elif mode == "multikey_ease":
                        c_em = apply_multikey_ease_interval(c, st, sp, strength=strength, bias=bias)
                    elif mode == "ease":
                        c_eb = apply_ease_in_out_interval(c, st, sp, strength=strength, bias=bias)
                    elif mode == "tangents":
                        smooth_tangents_interval(c, st, sp)
                        if ease_bounds:
                            c_eb = apply_ease_in_out_interval(c, st, sp, strength=strength, bias=bias)
                    elif mode == "smart":
                        c_sm = smooth_curve_interval(c, st, sp, strength=strength)
                        c_si = simplify_curve_interval(c, st, sp, strength=strength)
                        c_em = apply_multikey_ease_interval(c, st, sp, strength=strength, bias=bias)
                        smooth_tangents_interval(c, st, sp)
                        c_eb = apply_ease_in_out_interval(c, st, sp, strength=strength, bias=bias)

                    # 强制锁定端点绝不漂移
                    cmds.keyframe(c, time=(st, st), valueChange=orig_v_st)
                    cmds.keyframe(c, time=(sp, sp), valueChange=orig_v_sp)

                    smoothed_pts += c_sm
                    simplified_keys += c_si
                    eased_multikey_count += c_em
                    eased_bounds_count += c_eb

                    # 检查数值变动明细
                    changed_frames = []
                    post_k_times = cmds.keyframe(c, time=(st, sp), query=True, timeChange=True) or []
                    post_k_times = sorted(list(set([round(float(t), 4) for t in post_k_times])))
                    for t in post_k_times:
                        if abs(t - st) > 0.001 and abs(t - sp) > 0.001:
                            post_val = cmds.keyframe(c, time=(t, t), query=True, valueChange=True)[0]
                            old_val = pre_vals.get(t, post_val)
                            if abs(post_val - old_val) > 0.001:
                                changed_frames.append(u"{}帧:{:.2f}->{:.2f}".format(t, old_val, post_val))

                    if changed_frames:
                        change_summary = u", ".join(changed_frames[:4])
                        if len(changed_frames) > 4:
                            change_summary += u" 等共{}帧".format(len(changed_frames))
                        modified_reports.append(u"  • [{}] 书签 [{}]({}~{}): 成功修改内部帧 [{}]，端点锁定不变".format(plug, bm["name"], st, sp, change_summary))
                    elif c_eb > 0:
                        modified_reports.append(u"  • [{}] 书签 [{}]({}~{}): 端点出入切线与加权手柄已优化缓动".format(plug, bm["name"], st, sp))
                    elif c_si > 0:
                        modified_reports.append(u"  • [{}] 书签 [{}]({}~{}): 成功抽稀清理 {} 处冗余帧".format(plug, bm["name"], st, sp, c_si))
                    else:
                        if abs(orig_v_sp - orig_v_st) < 1e-4:
                            unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 端点数值相同 ({:.2f} 水平平线)，位移重塑差为 0".format(plug, bm["name"], st, sp, orig_v_st))
                        else:
                            unmodified_reports.append(u"  • [{}] 书签 [{}]({}~{}) 关键帧数值已符合缓动，无显著位移改变".format(plug, bm["name"], st, sp))

    finally:
        cmds.undoInfo(closeChunk=True)

    title = u"✅【曲线优化成功执行报告】"
    header = u"{}\n" \
             u"🎯 目标层: [{}] | 涉及曲线: {} 根\n" \
             u"🎯 作用通道: {}\n" \
             u"🔖 作用书签范围: {}\n" \
             u"🎛️ 优化模式: {} | 力度: {:.0%} | 权重分布 (Bias): {}\n" \
             u"📌 统计: 平滑 {} 处 | 抽稀 {} 帧 | 多帧S曲线重塑 {} 帧 | 端点缓动 {} 处\n" \
             u"------------------------------------------------------------\n".format(
                 title, actual_layer, len(curves), ch_desc, scope_desc, mode_label, strength, bias_label,
                 smoothed_pts, simplified_keys, eased_multikey_count, eased_bounds_count
             )

    body_mod = u"✅【已成功优化的对象与属性】(共 {} 项):\n{}\n".format(
        len(modified_reports), u"\n".join(modified_reports) if modified_reports else u"  (无属性改变)"
    )
    body_unmod = u"\n⚠️【未修改/跳过的对象与属性及原因诊断】(共 {} 项):\n{}".format(
        len(unmodified_reports), u"\n".join(unmodified_reports) if unmodified_reports else u"  (无跳过项)"
    )

    full_success_msg = header + body_mod + body_unmod

    return {
        "success": True,
        "dry_run": False,
        "layer": actual_layer,
        "scope": scope,
        "mode": mode,
        "strength": strength,
        "bias": bias,
        "curves_count": len(curves),
        "smoothed_points": smoothed_pts,
        "simplified_keys": simplified_keys,
        "eased_multikey_count": eased_multikey_count,
        "eased_bounds_count": eased_bounds_count,
        "message": full_success_msg
    }


# ==============================================================================
# 原生 Maya 交互式图形界面 (Maya UI)
# ==============================================================================
class BookmarkTrimmerUI(object):
    """动画层书签关键帧修剪与曲线优化器 GUI 界面"""

    def __init__(self):
        self.window = WINDOW_NAME
        self.layer_menu = None
        self.scope_menu = None
        self.ensure_keys_cb = None
        self.ch_trans_cb = None
        self.ch_rotate_cb = None
        self.ch_scale_cb = None
        self.ch_other_cb = None
        self.ch_priority_cb = None
        self.bookmark_scroll = None
        self.status_field = None
        self.opt_mode_menu = None
        self.strength_slider = None
        self.bias_slider = None
        self.ease_bounds_cb = None

    def show(self):
        """打开或激活 UI 窗口"""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(
            self.window,
            title=TOOL_TITLE,
            widthHeight=(495, 830),
            sizeable=True
        )

        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        # 1. 顶部标头说明 (默认折叠，节省视野)
        cmds.frameLayout(
            label=u"📋 工具说明与使用场景",
            collapsable=True,
            collapse=True,
            marginWidth=8,
            marginHeight=4,
            parent=main_layout
        )
        cmds.text(
            label=u"以时间滑块书签 (Bookmarks) 为基准执行动画处理：\n"
                  u"• 🔖 范围可选：1.全部书签 / 2.时间轴播放范围 / 3.光标框选或所在时间轴。\n"
                  u"• 🎯 聚焦通道：默认位移与旋转，智能联动 Channel Box，永久排除显示隐藏 (visibility)。\n"
                  u"• ✂️ 关键帧修剪：仅保留书签起止端点帧，清理非端点帧。\n"
                  u"• 🎛️ 曲线优化：端点绝对锁定，提供平滑去噪、冗余简化、多帧S曲线缓动与端点缓入缓出。",
            align="left",
            wordWrap=True
        )
        cmds.setParent(main_layout)

        # 2. 目标动画层与书签作用范围设置
        cmds.frameLayout(
            label=u"🎯 目标动画层与书签范围设置",
            collapsable=False,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign3=("right", "left", "center"))
        cmds.text(label=u"动画层 (Layer): ")
        self.layer_menu = cmds.optionMenu(changeCommand=self._on_layer_changed)
        cmds.button(label=u"🔄 刷新层", width=70, command=self._refresh_layers)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign3=("right", "left", "center"))
        cmds.text(label=u"书签范围 (Scope): ")
        self.scope_menu = cmds.optionMenu(changeCommand=lambda *x: self._refresh_bookmarks())
        cmds.menuItem(label=u"1. 全部书签 (All Bookmarks)")
        cmds.menuItem(label=u"2. 时间轴范围内 (Playback Range)")
        cmds.menuItem(label=u"3. 光标框选或者所在的时间轴 (Selected / Cursor)")
        cmds.button(label=u"🔄 重新检测", width=70, command=self._refresh_bookmarks)
        cmds.setParent("..")

        self.ensure_keys_cb = cmds.checkBox(
            label=u"若书签端点无关键帧，自动插入关键帧锁定姿态 (Insert Key at Bounds)",
            value=True
        )
        cmds.setParent(main_layout)

        # 2.5 作用通道选择面板 (聚焦位移与旋转，排除显示隐藏)
        cmds.frameLayout(
            label=u"🎯 作用通道设置 (聚焦位移与旋转，排除显示隐藏)",
            collapsable=False,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(115, 110, 100, 120))
        self.ch_trans_cb = cmds.checkBox(label=u"位移 (Translate)", value=True)
        self.ch_rotate_cb = cmds.checkBox(label=u"旋转 (Rotate)", value=True)
        self.ch_scale_cb = cmds.checkBox(label=u"缩放 (Scale)", value=False)
        self.ch_other_cb = cmds.checkBox(label=u"其他连续浮点", value=False)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(275, 185))
        self.ch_priority_cb = cmds.checkBox(
            label=u"优先使用通道栏 (Channel Box) 选中的属性",
            value=True,
            annotation=u"若在 Maya 通道栏中高亮了具体属性(如 translateY)，则仅对选中的属性生效"
        )
        cmds.text(label=u"🛡️ 排除 visibility (显示隐藏)", font="obliqueLabelFont", align="right")
        cmds.setParent("..")
        cmds.setParent(main_layout)

        # 3. 最上方反馈与执行详细诊断区 (最新执行信息在此刷新置顶)
        feedback_frame = cmds.frameLayout(
            label=u"📝 执行结果与详细诊断反馈 (最新信息在最上方刷新)",
            collapsable=False,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(380, 80), parent=feedback_frame)
        cmds.text(label=u"💡 实时诊断报告：显示对谁作用、修改明细、未修改原因", font="obliqueLabelFont")
        cmds.button(
            label=u"🧹 清空反馈",
            width=80,
            command=lambda *x: cmds.scrollField(self.status_field, edit=True, text="")
        )
        cmds.setParent("..")

        self.status_field = cmds.scrollField(
            height=145,
            editable=False,
            wordWrap=True,
            font="smallFixedWidthFont",
            text=u"等待执行操作... 点击下方按钮后将在此实时刷新详尽诊断报告。\n",
            parent=feedback_frame
        )
        cmds.setParent(main_layout)

        # 4. 书签区间动画曲线优化面板
        cmds.frameLayout(
            label=u"🎛️ 书签区间动画曲线优化 (端点姿态绝对锁定)",
            collapsable=False,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(120, 320), columnAlign2=("right", "left"))
        cmds.text(label=u"优化模式 (Mode): ")
        self.opt_mode_menu = cmds.optionMenu()
        cmds.menuItem(label=u"圆滑曲线 (Smooth Curves - 去噪平滑)")
        cmds.menuItem(label=u"简化曲线 (Simplify Curves - 抽稀冗余)")
        cmds.menuItem(label=u"区间多帧缓入缓出 (Multi-key Ease - S曲线多帧重塑)")
        cmds.menuItem(label=u"端点缓入缓出 (Ease In/Out - 端点手柄平缓)")
        cmds.menuItem(label=u"综合优化 (Smart Optimize - 平滑+抽稀+缓动)")
        cmds.menuItem(label=u"平滑切线 (Smooth Tangents - Spline)")
        cmds.setParent("..")

        self.strength_slider = cmds.floatSliderGrp(
            label=u"优化力度 (Strength):",
            field=True,
            minValue=0.0,
            maxValue=1.0,
            value=0.5,
            step=0.05,
            fieldMinValue=0.0,
            fieldMaxValue=1.0,
            columnWidth3=(120, 60, 240)
        )

        self.bias_slider = cmds.floatSliderGrp(
            label=u"权重分布 (Weight Bias):",
            field=True,
            minValue=0.0,
            maxValue=1.0,
            value=0.5,
            step=0.05,
            precision=2,
            fieldMinValue=0.0,
            fieldMaxValue=1.0,
            columnWidth3=(120, 60, 240),
            annotation=u"调控缓动重心分布: 0.0=偏向起点 | 0.5=中间(默认) | 1.0=偏向终点"
        )
        cmds.text(
            label=u"       ◄ 0.0 偏向起点              ● 0.5 中间(默认)              1.0 偏向终点 ►",
            align="center",
            font="obliqueLabelFont"
        )

        self.ease_bounds_cb = cmds.checkBox(
            label=u"端点前后应用缓入缓出 (Apply Ease In/Out at Bounds)",
            value=True
        )

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(220, 220), columnAttach=[(1, "both", 2), (2, "both", 2)])
        cmds.button(
            label=u"🔍 预检曲线优化 (Dry Run)",
            backgroundColor=(0.28, 0.38, 0.48),
            height=32,
            command=self._on_dry_run_optimize_clicked
        )
        cmds.button(
            label=u"✨ 执行曲线优化 (Optimize)",
            backgroundColor=(0.25, 0.65, 0.45),
            height=32,
            command=self._on_optimize_clicked
        )
        cmds.setParent("..")
        cmds.setParent(main_layout)

        # 5. 原有一键修剪操作面板
        cmds.frameLayout(
            label=u"✂️ 关键帧修剪操作 (仅保留端点，清理非端点帧)",
            collapsable=True,
            collapse=False,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(220, 220), columnAttach=[(1, "both", 2), (2, "both", 2)])
        cmds.button(
            label=u"🔍 预检修剪 (Dry Run)",
            backgroundColor=(0.35, 0.35, 0.42),
            height=30,
            command=self._on_dry_run_trim_clicked
        )
        cmds.button(
            label=u"✂️ 执行关键帧修剪 (Trim)",
            backgroundColor=(0.75, 0.28, 0.28),
            height=30,
            command=self._on_trim_clicked
        )
        cmds.setParent("..")
        cmds.setParent(main_layout)

        # 6. 生效的书签区间展示列表 (参考区)
        cmds.frameLayout(
            label=u"🔖 生效的书签区间与保留端点 (参考列表)",
            collapsable=True,
            collapse=True,
            marginWidth=8,
            marginHeight=6,
            parent=main_layout
        )
        self.bookmark_scroll = cmds.scrollField(
            height=75,
            editable=False,
            wordWrap=True,
            font="smallFixedWidthFont"
        )
        cmds.setParent(main_layout)

        self._refresh_layers()
        self._refresh_bookmarks()

        cmds.showWindow(self.window)

    def _refresh_layers(self, *args):
        """刷新场景动画层下拉菜单"""
        existing_items = cmds.optionMenu(self.layer_menu, query=True, itemListLong=True) or []
        for item in existing_items:
            cmds.deleteUI(item)

        cmds.menuItem(label=u"Auto (自动识别当前激活层)", parent=self.layer_menu)

        layers = get_scene_anim_layers()
        active_layer = get_active_anim_layer()

        target_index = 1
        for idx, l in enumerate(layers):
            cmds.menuItem(label=l, parent=self.layer_menu)
            if l == active_layer:
                target_index = idx + 2

        cmds.optionMenu(self.layer_menu, edit=True, select=target_index)

    def _on_layer_changed(self, selected_label):
        self._log(u"当前选定目标动画层: {}".format(selected_label))

    def _get_scope(self):
        """从下拉菜单获取当前书签范围"""
        idx = cmds.optionMenu(self.scope_menu, query=True, select=True)
        scope_map = {1: "all", 2: "playback", 3: "selected"}
        return scope_map.get(idx, "all")

    def _refresh_bookmarks(self, *args):
        """重新扫描书签并更新滚动文本框"""
        scope = self._get_scope()
        matched_bms, desc = get_filtered_bookmarks(scope=scope)
        keep_frames = get_bookmark_boundary_frames(scope=scope)

        if not matched_bms:
            text = u"⚠️ 【{}】未匹配到任何书签！\n请检查时间滑块或调整作用范围。".format(desc)
        else:
            lines = [u"【当前作用范围】: {}".format(desc)]
            for i, d in enumerate(matched_bms):
                lines.append(u"  {}. [{}] 范围: {} ~ {}".format(i + 1, d["name"], d["start"], d["stop"]))
            lines.append(u"----------------------------------------")
            lines.append(u"🎯 锁定的书签端点帧 (共 {} 帧):".format(len(keep_frames)))
            lines.append(u"  {}".format(keep_frames))
            text = "\n".join(lines)

        cmds.scrollField(self.bookmark_scroll, edit=True, text=text)

    def _get_selected_layer(self):
        val = cmds.optionMenu(self.layer_menu, query=True, value=True)
        if not val or val.startswith("Auto"):
            return "auto"
        return val

    def _get_opt_mode(self):
        idx = cmds.optionMenu(self.opt_mode_menu, query=True, select=True)
        mode_map = {
            1: "smooth",
            2: "simplify",
            3: "multikey_ease",
            4: "ease",
            5: "smart",
            6: "tangents"
        }
        return mode_map.get(idx, "smooth")

    def _get_channel_settings(self):
        """获取界面通道设置"""
        inc_trans = cmds.checkBox(self.ch_trans_cb, query=True, value=True) if self.ch_trans_cb else True
        inc_rot = cmds.checkBox(self.ch_rotate_cb, query=True, value=True) if self.ch_rotate_cb else True
        inc_scale = cmds.checkBox(self.ch_scale_cb, query=True, value=True) if self.ch_scale_cb else False
        inc_other = cmds.checkBox(self.ch_other_cb, query=True, value=True) if self.ch_other_cb else False
        priority = cmds.checkBox(self.ch_priority_cb, query=True, value=True) if self.ch_priority_cb else True
        return inc_trans, inc_rot, inc_scale, inc_other, priority

    def _log(self, message):
        """在反馈窗口最上方刷新显示最新信息，并自动滚动到第一行"""
        current = cmds.scrollField(self.status_field, query=True, text=True) or ""
        # 去掉占位初始文字
        if u"等待执行操作" in current:
            current = ""
        if current.strip():
            separator = u"\n\n" + (u"=" * 60) + u"\n\n"
            updated = message + separator + current
        else:
            updated = message
        cmds.scrollField(self.status_field, edit=True, text=updated, insertionPosition=1)

    def _on_dry_run_trim_clicked(self, *args):
        layer = self._get_selected_layer()
        scope = self._get_scope()
        ensure_keys = cmds.checkBox(self.ensure_keys_cb, query=True, value=True)
        inc_t, inc_r, inc_s, inc_o, prio = self._get_channel_settings()
        res = trim_layer_keyframes_by_bookmarks(
            objects=None,
            layer=layer,
            scope=scope,
            include_translate=inc_t,
            include_rotate=inc_r,
            include_scale=inc_s,
            include_others=inc_o,
            channel_box_priority=prio,
            ensure_keys_at_bounds=ensure_keys,
            dry_run=True
        )
        self._log(res.get("message", ""))

    def _on_trim_clicked(self, *args):
        layer = self._get_selected_layer()
        scope = self._get_scope()
        ensure_keys = cmds.checkBox(self.ensure_keys_cb, query=True, value=True)
        inc_t, inc_r, inc_s, inc_o, prio = self._get_channel_settings()
        res = trim_layer_keyframes_by_bookmarks(
            objects=None,
            layer=layer,
            scope=scope,
            include_translate=inc_t,
            include_rotate=inc_r,
            include_scale=inc_s,
            include_others=inc_o,
            channel_box_priority=prio,
            ensure_keys_at_bounds=ensure_keys,
            dry_run=False
        )
        self._log(res.get("message", ""))

    def _on_dry_run_optimize_clicked(self, *args):
        layer = self._get_selected_layer()
        scope = self._get_scope()
        mode = self._get_opt_mode()
        strength = cmds.floatSliderGrp(self.strength_slider, query=True, value=True)
        bias = cmds.floatSliderGrp(self.bias_slider, query=True, value=True) if self.bias_slider else 0.5
        ease_bounds = cmds.checkBox(self.ease_bounds_cb, query=True, value=True)
        inc_t, inc_r, inc_s, inc_o, prio = self._get_channel_settings()
        res = optimize_layer_curves_by_bookmarks(
            objects=None,
            layer=layer,
            scope=scope,
            mode=mode,
            strength=strength,
            bias=bias,
            include_translate=inc_t,
            include_rotate=inc_r,
            include_scale=inc_s,
            include_others=inc_o,
            channel_box_priority=prio,
            ease_bounds=ease_bounds,
            dry_run=True
        )
        self._log(res.get("message", ""))

    def _on_optimize_clicked(self, *args):
        layer = self._get_selected_layer()
        scope = self._get_scope()
        mode = self._get_opt_mode()
        strength = cmds.floatSliderGrp(self.strength_slider, query=True, value=True)
        bias = cmds.floatSliderGrp(self.bias_slider, query=True, value=True) if self.bias_slider else 0.5
        ease_bounds = cmds.checkBox(self.ease_bounds_cb, query=True, value=True)
        inc_t, inc_r, inc_s, inc_o, prio = self._get_channel_settings()
        res = optimize_layer_curves_by_bookmarks(
            objects=None,
            layer=layer,
            scope=scope,
            mode=mode,
            strength=strength,
            bias=bias,
            include_translate=inc_t,
            include_rotate=inc_r,
            include_scale=inc_s,
            include_others=inc_o,
            channel_box_priority=prio,
            ease_bounds=ease_bounds,
            dry_run=False
        )
        self._log(res.get("message", ""))


def show_ui():
    """打开修剪与曲线优化工具界面的全局快捷入口"""
    ui = BookmarkTrimmerUI()
    ui.show()
    return ui


if __name__ == "__main__":
    show_ui()
