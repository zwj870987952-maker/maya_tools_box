import sys
import maya.cmds as cmds
from .operations import *

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
                  u"• 🎛️ 曲线优化：保留端点值；切线可能影响范围外插值。支持平滑、简化与缓动。",
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
            label=u"🎛️ 书签区间动画曲线优化 (保留本层曲线端点值)",
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
        cmds.menuItem(label=u"端点缓入缓出 (Ease In/Out - 内部帧加减速数值缓动)")
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
