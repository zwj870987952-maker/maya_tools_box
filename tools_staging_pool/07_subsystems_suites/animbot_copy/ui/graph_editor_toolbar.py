"""
Dedicated animBot Graph Editor Toolbar.
Embedded directly inside Autodesk Maya's Graph Editor panel.
Supports:
1. 3 Dedicated Graph Editor dock locations:
   - '图形编辑器顶部' (Top of Graph Editor Window, above menu)
   - '在图形编辑器菜单下' (Under Graph Editor Menu Bar)
   - '图形编辑器底部' (Bottom of Graph Editor)
2. Logo menu, drag grip handle, responsive group-atomic flow layout (single/multi-row, alignment).
3. Maya native SplitVCursor edge stretching without distorting Maya.
4. Canonical slider ordering, 2-letter uppercase abbreviations, and 100% two-way Workspace synchronization.
"""

from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import shiboken6

from ..core.theme import AnimBotColors, AnimBotStyle
from ..core.icons import AnimBotIconProvider
from ..core.workspace_manager import WORKSPACE_MGR, SLIDER_CATEGORY_MODES
from ..widgets.drag_grip import AnimBotDragGrip
from ..widgets.icon_button import AnimBotButton
from ..widgets.slider_widget import AnimBotSlider
from ..widgets.tool_group import AnimBotToolGroup
from ..widgets.spinbox import AnimBotSpinBox, AnimBotDoubleSpinBox
from ..widgets.menu import AnimBotMenu
from ..widgets.context_menus import AnimBotContextMenuBuilder
from ..widgets.workspace_window import show_workspace_window

GRAPH_EDITOR_TOOLBAR_INSTANCE = None

class AnimBotGraphEditorToolbar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnimBotGraphEditorToolbar")
        self.setStyleSheet(AnimBotStyle.get_toolbar_stylesheet())
        self.setMouseTracking(True)
        
        self.workspace_mgr = WORKSPACE_MGR
        self.tools_map = {}
        self.groups_map = {}
        self.ordered_groups = []
        
        # Panning state for single row mode
        self.pan_offset_x = 0
        self._is_dragging_pan = False
        self._drag_start_x = 0
        self._start_pan_offset = 0
        self._total_content_width = 0
        
        # Edge-drag resizing state
        self._is_edge_resizing = False
        self._resize_edge = None
        self._resize_start_pos = QtCore.QPoint()
        self._resize_start_h = 42
        self._resize_start_w = 1200
        self._edge_margin = 6
        
        self._build_all_tools()
        
        # Connect workspace manager updates
        self.workspace_mgr.workspaceChanged.connect(lambda t: self.update_tool_visibility() if t == "graph_editor" else None)
        self.workspace_mgr.layoutConfigChanged.connect(lambda t: self.relayout_groups() if t == "graph_editor" else None)
        
        self.update_tool_visibility()

    def _register_tool(self, tool_id, widget, group=None):
        self.tools_map[tool_id] = widget
        if group:
            group.add_widget(widget)
        return widget

    def _create_group(self, group_id, title, color):
        grp = AnimBotToolGroup(title, color, self)
        self.groups_map[group_id] = grp
        self.ordered_groups.append(grp)
        return grp

    def get_active_slider_modes(self, requesting_slider=None):
        """Returns the set of active slider tool_ids currently visible on the toolbar, excluding requesting_slider."""
        active_tools = set()
        for tid, widget in self.tools_map.items():
            if isinstance(widget, AnimBotSlider) and not widget.isHidden() and widget is not requesting_slider:
                active_tools.add(widget.tool_id)
                active_tools.add(tid)
        return active_tools

    def on_slider_tool_switched(self, old_tool_id, new_tool_id):
        """Handle slider right-click mode switch: update WorkspaceManager and toolbar layout."""
        self.workspace_mgr.set_tool_active(old_tool_id, False, "graph_editor")
        self.workspace_mgr.set_tool_active(new_tool_id, True, "graph_editor")

    def _build_all_tools(self):
        # 0. Left Drag Grip & Logo Button Group
        grp_logo = self._create_group("grp_logo_ge", "animBot", "#FFFFFF")
        
        self.drag_grip = AnimBotDragGrip(grp_logo)
        grp_logo.add_widget(self.drag_grip)
        
        self.btn_logo = AnimBotButton("logo", tooltip="animBot Menu & Settings\nClick to access workspace layout, preferences, and tutorials", accent_color="#FFFFFF", color_category="white")
        self._setup_logo_menu()
        self._register_tool("logo", self.btn_logo, grp_logo)
        
        # 1. Green: Nudge & Precise Transform Group
        grp_nudge = self._create_group("grp_nudge_ge", "Nudge", AnimBotColors.GREEN)
        
        btn_dec_trans = AnimBotButton("minus", "Decrease Precise Transform", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_dec_trans, "nudge_step", self)
        self._register_tool("decrease_precise_transform", btn_dec_trans, grp_nudge)
        
        self.spin_nudge = AnimBotDoubleSpinBox(1.000, decimals=3, accent_color=AnimBotColors.GREEN)
        self.spin_nudge.setToolTip("Precise Transform Value")
        self._register_tool("precise_transform_value", self.spin_nudge, grp_nudge)
        
        btn_inc_trans = AnimBotButton("plus", "Increase Precise Transform", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_inc_trans, "nudge_step", self)
        self._register_tool("increase_precise_transform", btn_inc_trans, grp_nudge)
        
        btn_nudge_l = AnimBotButton("nudge_left", "Nudge Left", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_nudge_l, "nudge_left_right", self)
        self._register_tool("nudge_left", btn_nudge_l, grp_nudge)
        
        btn_nudge_r = AnimBotButton("nudge_right", "Nudge Right", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_nudge_r, "nudge_left_right", self)
        self._register_tool("nudge_right", btn_nudge_r, grp_nudge)
        
        extra_nudge = [
            ("nudge_left_time_offsetter", "nudge_left", "Nudge Left Time Offsetter", "nudge_left_right"),
            ("nudge_right_time_offsetter", "nudge_right", "Nudge Right Time Offsetter", "nudge_left_right"),
            ("nudge_left_all_keys", "nudge_left", "Nudge Left All Keys", "nudge_left_right"),
            ("nudge_right_all_keys", "nudge_right", "Nudge Right All Keys", "nudge_left_right"),
            ("nudge_left_scene", "nudge_left", "Nudge Left Scene", "nudge_left_right"),
            ("nudge_right_scene", "nudge_right", "Nudge Right Scene", "nudge_left_right"),
            ("nudge_value", "spinbox", "Nudge Value", "nudge_step"),
            ("set_inbetween", "set_inbetween_on_ones", "Set Inbetween on Ones", "bake_action"),
            ("insert_inbetween", "set_inbetween_on_ones", "Insert Inbetween", "bake_action"),
            ("remove_inbetween", "set_inbetween_on_ones", "Remove Inbetween", "bake_action"),
        ]
        for tid, icon, tip, mtype in extra_nudge:
            if icon == "spinbox":
                sp = AnimBotDoubleSpinBox(1.0, decimals=2, accent_color=AnimBotColors.GREEN)
                sp.setToolTip(tip)
                self._register_tool(tid, sp, grp_nudge)
            else:
                btn = AnimBotButton(icon, tip, AnimBotColors.GREEN, "green")
                AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
                self._register_tool(tid, btn, grp_nudge)

        # 2. Green: Default Pose Group
        grp_pose = self._create_group("grp_pose_ge", "Default Pose", AnimBotColors.GREEN)
        pose_tools = [
            ("reset_pose", "reset_pose", "Reset Pose to Default", "pose_transfer"),
            ("reset_translation", "reset_translation", "Reset Translation", "pose_transfer"),
            ("reset_rotation", "reset_rotation", "Reset Rotation", "pose_transfer"),
            ("reset_scale", "reset_scale", "Reset Scale", "pose_transfer"),
            ("reset_trs", "reset_trs", "Reset Translation Rotation Scale", "pose_transfer"),
            ("snapshot_default_pose", "restore_rig_default_pose", "Snapshot Preferred Default Pose", "pose_transfer"),
        ]
        for tid, icon, tip, mtype in pose_tools:
            btn = AnimBotButton(icon, tip, AnimBotColors.GREEN, "green")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_pose)

        # 3. Green: Baking Tools Group
        grp_bake = self._create_group("grp_bake_ge", "Bake", AnimBotColors.GREEN)
        
        self.spin_bake_interval = AnimBotSpinBox(1, accent_color=AnimBotColors.GREEN)
        self.spin_bake_interval.setToolTip("Bake Interval Value")
        self._register_tool("bake_interval_val", self.spin_bake_interval, grp_bake)
        
        btn_suspend_toggle = AnimBotButton("as", "Auto Viewport Suspend Toggle", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_suspend_toggle, "bake_toggle", self)
        self._register_tool("viewport_suspend_toggle", btn_suspend_toggle, grp_bake)
        
        btn_bake_ones = AnimBotButton("baking_step_tangent", "Bake on Ones / Custom Interval", AnimBotColors.GREEN, "green")
        AnimBotContextMenuBuilder.create_menu(btn_bake_ones, "bake_action", self)
        self._register_tool("bake_on_ones", btn_bake_ones, grp_bake)
        
        extra_bakes = [
            ("bake_on_twos", "bake_on_twos", "Bake on Twos", "bake_action"),
            ("bake_on_threes", "bake_on_threes", "Bake on Threes", "bake_action"),
            ("bake_on_fours", "bake_on_fours", "Bake on Fours", "bake_action"),
            ("bake_custom_interval", "bake_custom_interval", "Bake Custom Interval", "bake_action"),
            ("bake_infinity", "bake_infinity", "Bake Infinity Cycle", "bake_action"),
            ("share_key_times", "share_key_times", "Share Key Times", "share_keys"),
            ("copy_key_times", "copy_key_times", "Copy Key Times", "share_keys"),
            ("paste_merge_key_times", "paste_merge_key_times", "Paste Merge Key Times", "share_keys"),
            ("paste_insert_key_times", "paste_insert_key_times", "Paste Insert Key Times", "share_keys"),
            ("paste_replace_key_times", "paste_replace_key_times", "Paste Replace Key Times", "share_keys"),
        ]
        for tid, icon, tip, mtype in extra_bakes:
            btn = AnimBotButton(icon, tip, AnimBotColors.GREEN, "green")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_bake)

        # 4. Green: Key Sliders Group (Canonical order)
        grp_ease = self._create_group("grp_ease_ge", "Ease", AnimBotColors.GREEN)
        ease_modes = SLIDER_CATEGORY_MODES["key_slider"]
        for m in ease_modes:
            slider = AnimBotSlider(
                mode_label=m["abbr"],
                accent_color=AnimBotColors.GREEN,
                min_val=-100.0, max_val=100.0, default_val=0.0,
                modes=ease_modes,
                tool_id=m["id"],
                get_occupied_modes_func=self.get_active_slider_modes,
                parent=grp_ease
            )
            slider.setToolTip(f"{m['label']} Slider")
            slider.sliderToolSwitched.connect(self.on_slider_tool_switched)
            self._register_tool(m["id"], slider, grp_ease)

        # 5. Yellow: Tween Sliders Group
        grp_tween = self._create_group("grp_tween_ge", "Tween", AnimBotColors.YELLOW)
        tween_modes = SLIDER_CATEGORY_MODES["tween_slider"]
        for m in tween_modes:
            slider = AnimBotSlider(
                mode_label=m["abbr"],
                accent_color=AnimBotColors.YELLOW,
                min_val=-100.0, max_val=100.0, default_val=0.0,
                modes=tween_modes,
                tool_id=m["id"],
                get_occupied_modes_func=self.get_active_slider_modes,
                parent=grp_tween
            )
            slider.setToolTip(f"{m['label']} Slider")
            slider.sliderToolSwitched.connect(self.on_slider_tool_switched)
            self._register_tool(m["id"], slider, grp_tween)

        # 6. Orange: Tangents Group & Sliders
        grp_tangents = self._create_group("grp_tangents_ge", "Tangents", AnimBotColors.ORANGE)
        tangents_info = [
            ("tangent_cycle_match", "auto_tangent", "Cycle Match Tangent", "tangent_auto"),
            ("tangent_best_guess", "best_guess_tangent", "Best Guess Tangent", "tangent_best_guess"),
            ("tangent_polished", "bpt", "Polished Tangent", "tangent_stepped"),
            ("tangent_flow", "bounce_tangent", "Flow Tangent", "tangent_bounce"),
            ("tangent_bounce", "bounce_tangent", "Bounce Tangent", "tangent_bounce"),
            ("tangent_auto", "auto_tangent", "Auto Tangent", "tangent_auto"),
            ("tangent_spline", "auto_tangent", "Spline Tangent", "tangent_auto"),
            ("tangent_clamped", "bct", "Clamped Tangent", "tangent_clamped"),
            ("tangent_linear", "blt", "Linear Tangent", "tangent_linear"),
            ("tangent_flat", "bft", "Flat Tangent", "tangent_flat"),
            ("tangent_stepped", "bpt", "Step Tangent", "tangent_stepped"),
            ("tangent_plateau", "bft", "Plateau Tangent", "tangent_flat"),
        ]
        for tool_id, icon_name, tip, menu_type in tangents_info:
            btn = AnimBotButton(icon_name, tip, AnimBotColors.ORANGE, "orange")
            AnimBotContextMenuBuilder.create_menu(btn, menu_type, self)
            self._register_tool(tool_id, btn, grp_tangents)
            
        tangent_modes = SLIDER_CATEGORY_MODES["tangent_slider"]
        for m in tangent_modes:
            slider = AnimBotSlider(
                mode_label=m["abbr"],
                accent_color=AnimBotColors.ORANGE,
                min_val=-100.0, max_val=100.0, default_val=0.0,
                modes=tangent_modes,
                tool_id=m["id"],
                get_occupied_modes_func=self.get_active_slider_modes,
                parent=grp_tangents
            )
            slider.setToolTip(f"{m['label']} Slider")
            slider.sliderToolSwitched.connect(self.on_slider_tool_switched)
            self._register_tool(m["id"], slider, grp_tangents)

        # 7. Colors: Color Keys Group
        grp_tint = self._create_group("grp_tint_ge", "Colors", "#888888")
        btn_tint_clear = AnimBotButton("smart_tint_keys", "Smart Tint Keys (Clear)", "#AAAAAA", "misc")
        AnimBotContextMenuBuilder.create_menu(btn_tint_clear, "tint_clear", self)
        self._register_tool("smart_tint_keys", btn_tint_clear, grp_tint)
        
        btn_tint_red = AnimBotButton("tint_key_red", "Tint Key Red", "#FF6B6B", "misc")
        AnimBotContextMenuBuilder.create_menu(btn_tint_red, "tint_red", self)
        self._register_tool("tint_key_red", btn_tint_red, grp_tint)
        
        btn_tint_yellow = AnimBotButton("tint_key_yellow", "Tint Key Yellow", "#F2E66C", "misc")
        AnimBotContextMenuBuilder.create_menu(btn_tint_yellow, "tint_yellow", self)
        self._register_tool("tint_key_yellow", btn_tint_yellow, grp_tint)
        
        btn_tint_green = AnimBotButton("tint_key_green", "Tint Key Green", "#84F296", "misc")
        AnimBotContextMenuBuilder.create_menu(btn_tint_green, "tint_green", self)
        self._register_tool("tint_key_green", btn_tint_green, grp_tint)

        # 8. Purple: Selection & Anim Pose Transfer Group
        grp_selection = self._create_group("grp_selection_ge", "Purple", AnimBotColors.PURPLE)
        purple_tools = [
            ("select_sets", "select_sets", "Select Sets", "select_sets"),
            ("select_opposite", "auto_select_opposite", "Select Opposite", "select_opposite"),
            ("copy_anim", "copy_animation", "Copy Animation", "anim_transfer"),
            ("paste_insert_anim", "paste_insert_animation", "Paste Insert Animation", "anim_transfer"),
            ("paste_replace_anim", "paste_insert_animation", "Paste Replace Animation", "anim_transfer"),
            ("copy_pose", "copy_pose", "Copy Pose", "pose_transfer"),
            ("paste_pose", "paste_pose", "Paste Pose", "pose_transfer"),
        ]
        for tid, icon, tip, mtype in purple_tools:
            btn = AnimBotButton(icon, tip, AnimBotColors.PURPLE, "purple")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_selection)

        # 9. Pink: Mirror & Space Switcher Group & Sliders
        grp_mirror = self._create_group("grp_mirror_ge", "Pink", AnimBotColors.PINK)
        pink_tools = [
            ("mirror_pose", "mirror_pose", "Mirror Pose", "mirror"),
            ("mirror_to_right", "mirror_pose", "Mirror to Right", "mirror"),
            ("mirror_to_left", "mirror_pose", "Mirror to Left", "mirror"),
            ("mirror_all_keys", "mirror_pose", "Mirror All Keys", "mirror"),
            ("align_objects", "align_objects", "Align Objects", "align"),
            ("align_objects_all_keys", "align_objects", "Align Objects All Keys", "align"),
            ("copy_xform_relationship", "asset_attribute_space_switcher", "Copy Xform Relationship", "space_switcher"),
            ("paste_xform_relationship", "asset_attribute_space_switcher", "Paste Xform Relationship", "space_switcher"),
        ]
        for tid, icon, tip, mtype in pink_tools:
            btn = AnimBotButton(icon, tip, AnimBotColors.PINK, "pink")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_mirror)
            
        xform_modes = SLIDER_CATEGORY_MODES["xform_slider"]
        for m in xform_modes:
            slider = AnimBotSlider(
                mode_label=m["abbr"],
                accent_color=AnimBotColors.PINK,
                min_val=-100.0, max_val=100.0, default_val=0.0,
                modes=xform_modes,
                tool_id=m["id"],
                get_occupied_modes_func=self.get_active_slider_modes,
                parent=grp_mirror
            )
            slider.setToolTip(f"{m['label']} Slider")
            slider.sliderToolSwitched.connect(self.on_slider_tool_switched)
            self._register_tool(m["id"], slider, grp_mirror)

        # 10. Turquoise: Temp Controls Group
        grp_temp = self._create_group("grp_temp_ge", "Turquoise", AnimBotColors.TURQUOISE)
        turq_tools = [
            ("master_spline", "create_master_spline", "Master Spline", "master_spline"),
            ("temp_controls", "clear_temp_controls", "Temp Controls", "temp_controls"),
            ("temp_pivot", "temp_pivot", "Temp Pivot", "temp_pivot"),
            ("global_offset", "global_offset", "Global Offset Animation", "temp_controls"),
        ]
        for tid, icon, tip, mtype in turq_tools:
            btn = AnimBotButton(icon, tip, AnimBotColors.TURQUOISE, "turquoise")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_temp)

        # 11. Red: Bookmarks & Playback Group
        grp_bookmarks = self._create_group("grp_bookmarks_ge", "Red", AnimBotColors.RED)
        red_tools = [
            ("motion_trail", "create_motion_trail", "Motion Trail", "motion_trail"),
            ("auto_suspend", "auto_suspend_viewport", "Suspend Viewport", "bake_toggle"),
            ("time_bookmarks", "edit_time_bookmark", "Time Bookmarks", "bookmarks"),
            ("go_to_prev_time_bookmark", "edit_time_bookmark", "Go to Previous Time Bookmark", "bookmarks"),
            ("go_to_next_time_bookmark", "edit_time_bookmark", "Go to Next Time Bookmark", "bookmarks"),
            ("play_keys", "bake_on_ones", "Play Keys", "bake_action"),
        ]
        for tid, icon, tip, mtype in red_tools:
            btn = AnimBotButton(icon, tip, AnimBotColors.RED, "red")
            AnimBotContextMenuBuilder.create_menu(btn, mtype, self)
            self._register_tool(tid, btn, grp_bookmarks)

        # 12. Subrow / Extra Utilities (Blue & White)
        grp_extra = self._create_group("grp_extra_ge", "Curve Tools", AnimBotColors.BLUE)
        subrow_items = [
            ("micro_manipulator", "micro_manipulator", "Micro Manipulator", "micro_manipulator", AnimBotColors.TURQUOISE, "turquoise"),
            ("axis_toggle", "axis_orientation_toggle", "Axis Orientation Toggle", "axis_toggle", AnimBotColors.BLUE, "blue"),
            ("graph_editor_tools", "anim_curve_extra_tools", "Graph Editor Extra Tools", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("auto_hide_static_curves", "anim_curve_extra_tools", "Auto Hide Static Anim Curves", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("frame_current_second", "anim_curve_extra_tools", "Frame Current Second", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("frame_next_second", "anim_curve_extra_tools", "Frame Next Second", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("euler_filter", "apply_smart_euler_filter", "Apply Smart Euler Filter", "euler_filter", AnimBotColors.RED, "blue"),
            ("clear_animation", "auto_clear_channel_box_selection", "Clear Animation", "channel_box", AnimBotColors.BLUE, "blue"),
            ("crop_animation", "anim_curve_extra_tools", "Crop Animation", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("remove_redundant_keys", "anim_curve_extra_tools", "Remove Redundant Keys", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("remove_static_anim_curves", "anim_curve_extra_tools", "Remove Static Anim Curves", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("reverse_animation", "anim_curve_extra_tools", "Reverse Animation", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("copy_keys", "copy_key_times", "Copy Keys", "share_keys", AnimBotColors.GREEN, "green"),
            ("paste_keys", "paste_insert_animation", "Paste Keys", "anim_transfer", AnimBotColors.PURPLE, "purple"),
            ("select_all_anim_curves", "anim_curve_extra_tools", "Select All Anim Curves in the Scene", "graph_editor", AnimBotColors.BLUE, "blue"),
            ("more_tools", "more", "More Extra Tools", "search", AnimBotColors.BLUE, "blue"),
            ("global_search", "search", "Search & Hotkeys", "search", AnimBotColors.WHITE, "white"),
        ]
        for tool_id, icon_name, tip, menu_type, accent, cat in subrow_items:
            btn = AnimBotButton(icon_name, tip, accent, cat)
            AnimBotContextMenuBuilder.create_menu(btn, menu_type, self)
            self._register_tool(tool_id, btn, grp_extra)

    def _setup_logo_menu(self):
        menu = AnimBotMenu("animBot Graph Editor", self)
        
        act_workspace = menu.addAction("Workspace Layout Editor (工作区)...")
        act_workspace.setIcon(AnimBotIconProvider.get_icon("custom_tools", "white"))
        act_workspace.triggered.connect(self.open_workspace_editor)
        
        menu.addSeparator()
        
        menu_align = menu.addMenu("Alignment (对齐方式)...")
        act_left = menu_align.addAction("Left Align (左对齐)")
        act_left.triggered.connect(lambda: self.set_alignment("left"))
        act_center = menu_align.addAction("Center Align (居中对齐)")
        act_center.triggered.connect(lambda: self.set_alignment("center"))
        act_right = menu_align.addAction("Right Align (右对齐)")
        act_right.triggered.connect(lambda: self.set_alignment("right"))
        act_single = menu_align.addAction("Single Row Mode (单行模式切换)")
        act_single.triggered.connect(self.toggle_single_row)
        
        self.btn_logo.set_context_menu(menu)
        self.btn_logo.clicked.connect(lambda: menu.exec_(self.btn_logo.mapToGlobal(QtCore.QPoint(0, self.btn_logo.height()))))

    def set_alignment(self, alignment):
        self.workspace_mgr.set_alignment("graph_editor", alignment)

    def toggle_single_row(self):
        cur = self.workspace_mgr.get_single_row("graph_editor")
        self.workspace_mgr.set_single_row("graph_editor", not cur)

    def open_workspace_editor(self):
        return show_workspace_window()

    def update_tool_visibility(self):
        """Update tool and group visibility based on active tools in WorkspaceManager."""
        for tool_id, widget in self.tools_map.items():
            if tool_id == "logo":
                widget.setVisible(True)
            else:
                is_active = self.workspace_mgr.is_tool_active(tool_id, "graph_editor")
                widget.setVisible(is_active)
            
        for grp in self.ordered_groups:
            if grp is self.groups_map.get("grp_logo_ge"):
                grp.setVisible(True)
                continue
            any_active = False
            for i in range(grp.content_layout.count()):
                item = grp.content_layout.itemAt(i)
                if item and item.widget() and not item.widget().isHidden():
                    any_active = True
                    break
            grp.setVisible(any_active)
            
        self.relayout_groups()

    def relayout_groups(self):
        margin_x = 4
        margin_y = 4
        spacing_x = 6
        spacing_y = 6
        row_height = 38
        
        avail_w = max(100, self.width() - 2 * margin_x)
        is_single_row = self.workspace_mgr.get_single_row("graph_editor")
        alignment = self.workspace_mgr.get_alignment("graph_editor")
        
        visible_groups = [g for g in self.ordered_groups if g.isVisible()]
        
        if not visible_groups:
            self.setMinimumHeight(40)
            return

        if is_single_row:
            total_w = 0
            for grp in visible_groups:
                sz = grp.sizeHint()
                total_w += sz.width() + spacing_x
            total_w -= spacing_x
            self._total_content_width = total_w
            
            min_pan = min(0, self.width() - total_w - 2 * margin_x)
            self.pan_offset_x = max(min_pan, min(0, self.pan_offset_x))
            
            base_x = margin_x + self.pan_offset_x
            if total_w < avail_w:
                if alignment == "center":
                    base_x += (avail_w - total_w) // 2
                elif alignment == "right":
                    base_x += (avail_w - total_w)
                    
            curr_x = base_x
            for grp in visible_groups:
                sz = grp.sizeHint()
                grp.setGeometry(curr_x, margin_y, sz.width(), row_height)
                curr_x += sz.width() + spacing_x
                
            self.setMinimumHeight(row_height + 2 * margin_y)
            self.update()
            return

        # Multi-row wrapping
        self.pan_offset_x = 0
        lines = []
        curr_line = []
        curr_line_w = 0
        
        for grp in visible_groups:
            sz = grp.sizeHint()
            grp_w = sz.width()
            
            if curr_line and (curr_line_w + spacing_x + grp_w > avail_w):
                lines.append((curr_line, curr_line_w))
                curr_line = [(grp, grp_w)]
                curr_line_w = grp_w
            else:
                curr_line.append((grp, grp_w))
                curr_line_w += grp_w + (spacing_x if len(curr_line) > 1 else 0)
                
        if curr_line:
            lines.append((curr_line, curr_line_w))
            
        curr_y = margin_y
        for line_groups, line_w in lines:
            if alignment == "center":
                start_x = margin_x + max(0, (avail_w - line_w) // 2)
            elif alignment == "right":
                start_x = margin_x + max(0, avail_w - line_w)
            else: # left
                start_x = margin_x
                
            curr_x = start_x
            for grp, grp_w in line_groups:
                grp.setGeometry(curr_x, curr_y, grp_w, row_height)
                curr_x += grp_w + spacing_x
                
            curr_y += row_height + spacing_y
            
        total_h = curr_y - spacing_y + margin_y
        self.setMinimumHeight(total_h)
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_groups()

    def _detect_edge(self, pos):
        m = self._edge_margin
        w = self.width()
        h = self.height()
        
        on_left = pos.x() <= m
        on_right = pos.x() >= w - m
        on_top = pos.y() <= m
        on_bottom = pos.y() >= h - m
        
        if on_right and on_bottom:
            return 'corner'
        if on_bottom:
            return 'bottom'
        if on_top:
            return 'top'
        if on_right:
            return 'right'
        if on_left:
            return 'left'
        return None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            edge = self._detect_edge(event.pos())
            if edge:
                self._is_edge_resizing = True
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_h = self.height()
                self._resize_start_w = self.width()
                event.accept()
                return

            if self.workspace_mgr.get_single_row("graph_editor") and self._total_content_width > self.width():
                self._is_dragging_pan = True
                self._drag_start_x = event.pos().x()
                self._start_pan_offset = self.pan_offset_x
                self.setCursor(QtCore.Qt.ClosedHandCursor)
                event.accept()
                return
                
        elif event.button() == QtCore.Qt.MiddleButton:
            if self.workspace_mgr.get_single_row("graph_editor") and self._total_content_width > self.width():
                self._is_dragging_pan = True
                self._drag_start_x = event.pos().x()
                self._start_pan_offset = self.pan_offset_x
                self.setCursor(QtCore.Qt.ClosedHandCursor)
                event.accept()
                return
                
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_edge_resizing:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            target_h = self._resize_start_h
            target_w = self._resize_start_w
            
            if 'bottom' in self._resize_edge or self._resize_edge == 'corner':
                target_h = max(38, self._resize_start_h + delta.y())
            elif 'top' in self._resize_edge:
                target_h = max(38, self._resize_start_h - delta.y())
                
            self.setFixedHeight(target_h)
            self.relayout_groups()
            event.accept()
            return
            
        elif self._is_dragging_pan:
            dx = event.pos().x() - self._drag_start_x
            self.pan_offset_x = self._start_pan_offset + dx
            self.relayout_groups()
            event.accept()
            return
            
        edge = self._detect_edge(event.pos())
        if edge in ('top', 'bottom'):
            self.setCursor(QtCore.Qt.SplitVCursor)
        elif edge in ('left', 'right'):
            self.setCursor(QtCore.Qt.SplitHCursor)
        elif edge == 'corner':
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.workspace_mgr.get_single_row("graph_editor") and self._total_content_width > self.width():
            self.setCursor(QtCore.Qt.OpenHandCursor)
        else:
            self.unsetCursor()
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_edge_resizing:
            self._is_edge_resizing = False
            self._resize_edge = None
            self.unsetCursor()
            event.accept()
            return
        elif self._is_dragging_pan:
            self._is_dragging_pan = False
            self.setCursor(QtCore.Qt.OpenHandCursor if self.workspace_mgr.get_single_row("graph_editor") else QtCore.Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.workspace_mgr.get_single_row("graph_editor"):
            delta = event.angleDelta().y() or event.angleDelta().x()
            self.pan_offset_x += delta // 2
            self.relayout_groups()
            event.accept()
            return
        super().wheelEvent(event)


def dock_graph_editor_toolbar(location="在图形编辑器菜单下"):
    """
    Dock Graph Editor Toolbar to specified location in Maya Graph Editor:
    1. '图形编辑器顶部': Above Menu Bar (Top of graphEditor1Window)
    2. '在图形编辑器菜单下': Directly Under Graph Editor Menu Bar (Top of graphEditor1)
    3. '图形编辑器底部': Bottom of Graph Editor
    """
    global GRAPH_EDITOR_TOOLBAR_INSTANCE
    
    if not cmds.animCurveEditor("graphEditor1GraphEd", exists=True):
        try:
            cmds.GraphEditor()
        except Exception:
            pass
            
    ptr_win = omui.MQtUtil.findControl("graphEditor1Window")
    ptr_ge = omui.MQtUtil.findControl("graphEditor1")
    
    if not ptr_ge and not ptr_win:
        return None
        
    ge_win = shiboken6.wrapInstance(int(ptr_win), QtWidgets.QWidget) if ptr_win else None
    ge = shiboken6.wrapInstance(int(ptr_ge), QtWidgets.QWidget) if ptr_ge else None
    
    target_parent = ge if ge else ge_win
    
    if GRAPH_EDITOR_TOOLBAR_INSTANCE:
        try:
            if GRAPH_EDITOR_TOOLBAR_INSTANCE.parentWidget():
                p_layout = GRAPH_EDITOR_TOOLBAR_INSTANCE.parentWidget().layout()
                if p_layout:
                    p_layout.removeWidget(GRAPH_EDITOR_TOOLBAR_INSTANCE)
            GRAPH_EDITOR_TOOLBAR_INSTANCE.setParent(None)
            GRAPH_EDITOR_TOOLBAR_INSTANCE.deleteLater()
        except Exception:
            pass
            
    GRAPH_EDITOR_TOOLBAR_INSTANCE = AnimBotGraphEditorToolbar(target_parent)
    
    if "顶部" in location:
        # Positioned at the very top (above menu bar)
        if ge_win and ge_win.layout():
            ge_win.layout().insertWidget(0, GRAPH_EDITOR_TOOLBAR_INSTANCE)
        elif ge and ge.layout():
            ge.layout().insertWidget(0, GRAPH_EDITOR_TOOLBAR_INSTANCE)
    elif "底部" in location:
        # Positioned at the bottom
        if ge and ge.layout():
            ge.layout().addWidget(GRAPH_EDITOR_TOOLBAR_INSTANCE)
        elif ge_win and ge_win.layout():
            ge_win.layout().addWidget(GRAPH_EDITOR_TOOLBAR_INSTANCE)
    else: # 在图形编辑器菜单下 (Under Menu Bar)
        # Positioned directly inside graphEditor1 (under menu bar and above curve view)
        if ge and ge.layout():
            ge.layout().insertWidget(0, GRAPH_EDITOR_TOOLBAR_INSTANCE)
        elif ge_win and ge_win.layout():
            idx = min(1, ge_win.layout().count())
            ge_win.layout().insertWidget(idx, GRAPH_EDITOR_TOOLBAR_INSTANCE)
            
    GRAPH_EDITOR_TOOLBAR_INSTANCE.show()
    return GRAPH_EDITOR_TOOLBAR_INSTANCE

def attach_to_graph_editor():
    return dock_graph_editor_toolbar(WORKSPACE_MGR.get_location("graph_editor"))
