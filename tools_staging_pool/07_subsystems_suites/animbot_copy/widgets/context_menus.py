"""
Comprehensive right-click context menus for animBot toolbar buttons.
Provides rich animation workflow options and presets matching animBot.
"""

from PySide6 import QtWidgets, QtCore, QtGui
from .menu import AnimBotMenu
from ..core.icons import AnimBotIconProvider

class AnimBotContextMenuBuilder:
    @staticmethod
    def create_menu(button, menu_type, toolbar=None):
        """Build and attach context menu to button based on menu_type."""
        menu = AnimBotMenu(button.toolTip() if button else "", button)
        
        if menu_type == "nudge_step":
            AnimBotContextMenuBuilder._build_nudge_step_menu(menu, toolbar)
        elif menu_type == "nudge_left_right":
            AnimBotContextMenuBuilder._build_nudge_direction_menu(menu, toolbar)
        elif menu_type == "bake_interval":
            AnimBotContextMenuBuilder._build_bake_interval_menu(menu, toolbar)
        elif menu_type == "bake_toggle":
            AnimBotContextMenuBuilder._build_bake_toggle_menu(menu, toolbar)
        elif menu_type == "bake_action":
            AnimBotContextMenuBuilder._build_bake_action_menu(menu, toolbar)
        elif menu_type == "share_keys":
            AnimBotContextMenuBuilder._build_share_keys_menu(menu, toolbar)
        elif menu_type.startswith("tangent_"):
            tangent_kind = menu_type.replace("tangent_", "")
            AnimBotContextMenuBuilder._build_tangent_menu(menu, tangent_kind, toolbar)
        elif menu_type.startswith("tint_"):
            tint_kind = menu_type.replace("tint_", "")
            AnimBotContextMenuBuilder._build_tint_menu(menu, tint_kind, toolbar)
        elif menu_type == "select_sets":
            AnimBotContextMenuBuilder._build_select_sets_menu(menu, toolbar)
        elif menu_type == "select_opposite":
            AnimBotContextMenuBuilder._build_select_opposite_menu(menu, toolbar)
        elif menu_type == "anim_transfer":
            AnimBotContextMenuBuilder._build_anim_transfer_menu(menu, toolbar)
        elif menu_type == "pose_transfer":
            AnimBotContextMenuBuilder._build_pose_transfer_menu(menu, toolbar)
        elif menu_type == "mirror":
            AnimBotContextMenuBuilder._build_mirror_menu(menu, toolbar)
        elif menu_type == "align":
            AnimBotContextMenuBuilder._build_align_menu(menu, toolbar)
        elif menu_type == "space_switcher":
            AnimBotContextMenuBuilder._build_space_switcher_menu(menu, toolbar)
        elif menu_type == "bookmarks":
            AnimBotContextMenuBuilder._build_bookmarks_menu(menu, toolbar)
        elif menu_type == "motion_trail":
            AnimBotContextMenuBuilder._build_motion_trail_menu(menu, toolbar)
        elif menu_type == "temp_controls":
            AnimBotContextMenuBuilder._build_temp_controls_menu(menu, toolbar)
        elif menu_type == "temp_pivot":
            AnimBotContextMenuBuilder._build_temp_pivot_menu(menu, toolbar)
        elif menu_type == "master_spline":
            AnimBotContextMenuBuilder._build_master_spline_menu(menu, toolbar)
        elif menu_type == "micro_manipulator":
            AnimBotContextMenuBuilder._build_micro_manipulator_menu(menu, toolbar)
        elif menu_type == "axis_toggle":
            AnimBotContextMenuBuilder._build_axis_toggle_menu(menu, toolbar)
        elif menu_type == "channel_box":
            AnimBotContextMenuBuilder._build_channel_box_menu(menu, toolbar)
        elif menu_type == "graph_editor":
            AnimBotContextMenuBuilder._build_graph_editor_menu(menu, toolbar)
        elif menu_type == "euler_filter":
            AnimBotContextMenuBuilder._build_euler_filter_menu(menu, toolbar)
        elif menu_type == "camera":
            AnimBotContextMenuBuilder._build_camera_menu(menu, toolbar)
        elif menu_type == "recovery":
            AnimBotContextMenuBuilder._build_recovery_menu(menu, toolbar)
        elif menu_type == "search":
            AnimBotContextMenuBuilder._build_search_menu(menu, toolbar)
            
        button.set_context_menu(menu)
        return menu

    @staticmethod
    def _build_nudge_step_menu(menu, toolbar):
        title_act = menu.addAction("Step Presets")
        title_act.setEnabled(False)
        menu.addSeparator()
        
        presets = [0.001, 0.010, 0.100, 0.500, 1.000, 2.000, 5.000, 10.000, 100.000]
        for p in presets:
            act = menu.addAction(f"Step: {p:.3f}")
            act.triggered.connect(lambda ch=False, val=p: toolbar.spin_nudge.setValue(val) if toolbar else None)
        
        menu.addSeparator()
        menu.addAction("Relative Nudge (Default)").setCheckable(True)
        menu.addAction("Absolute Transform").setCheckable(True)

    @staticmethod
    def _build_nudge_direction_menu(menu, toolbar):
        menu.addAction("Step by 1 Frame")
        menu.addAction("Step by 2 Frames")
        menu.addAction("Step by Nudge Value")
        menu.addSeparator()
        menu.addAction("Jump to Next / Previous Keyframe")
        menu.addAction("Ripple Move Downstream Keys")

    @staticmethod
    def _build_bake_interval_menu(menu, toolbar):
        title = menu.addAction("Interval Presets")
        title.setEnabled(False)
        menu.addSeparator()
        for i in [1, 2, 3, 4, 5, 8, 10]:
            act = menu.addAction(f"Interval: {i} ('Ones' if 1)")
            act.triggered.connect(lambda ch=False, val=i: toolbar.spin_bake_interval.setValue(val) if toolbar else None)

    @staticmethod
    def _build_bake_toggle_menu(menu, toolbar):
        menu.addAction("AutoBot Viewport Suspend")
        menu.addAction("Suspend During Playback Only")
        menu.addAction("Suspend During Scrubbing Only")
        menu.addSeparator()
        menu.addAction("Auto-Resume Delay: 500ms")
        menu.addAction("Auto-Resume Delay: 1000ms")

    @staticmethod
    def _build_bake_action_menu(menu, toolbar):
        menu.addAction("Bake Selected Channels Only")
        menu.addAction("Bake Entire Hierarchy")
        menu.addAction("Bake on Stepped Tangents")
        menu.addSeparator()
        menu.addAction("Bake Playback Time Range")
        menu.addAction("Bake Custom Time Range...")
        menu.addAction("Un-bake / Restore Pre-bake Keys")

    @staticmethod
    def _build_share_keys_menu(menu, toolbar):
        menu.addAction("Copy Key Times")
        menu.addAction("Paste Insert Key Times")
        menu.addAction("Paste Merge Key Times")
        menu.addAction("Paste Replace Key Times")
        menu.addAction("Paste Tinted Key Times")

    @staticmethod
    def _build_tangent_menu(menu, kind, toolbar):
        menu.addAction(f"Apply {kind.capitalize()} to Selected Keys")
        menu.addAction(f"Apply {kind.capitalize()} to All Keys on Curve")
        menu.addAction(f"Apply {kind.capitalize()} to First & Last Keys (Ends)")
        menu.addSeparator()
        menu.addAction("Fix Tangent Overhangs / Overshoots")
        menu.addAction("Weight Tangents")
        menu.addAction("Free Tangent Weights")
        menu.addAction("Lock Tangent Angles")

    @staticmethod
    def _build_tint_menu(menu, kind, toolbar):
        menu.addAction(f"Tint Selected Keys: {kind.capitalize()}")
        menu.addAction("Clear Tint on Selected Keys")
        menu.addAction("Clear All Tints in Scene")
        menu.addSeparator()
        menu.addAction(f"Select All Keys Tinted {kind.capitalize()}")
        menu.addAction(f"Remove All Keys Tinted {kind.capitalize()}")

    @staticmethod
    def _build_select_sets_menu(menu, toolbar):
        menu.addAction("Create New Selection Set...")
        menu.addAction("Add Selection to Set")
        menu.addAction("Remove Selection from Set")
        menu.addSeparator()
        menu.addAction("Export Selection Sets...")
        menu.addAction("Import Selection Sets...")
        menu.addAction("Clear All Selection Sets")

    @staticmethod
    def _build_select_opposite_menu(menu, toolbar):
        menu.addAction("Select Opposite Controls (L <-> R)")
        menu.addAction("Deselect Center Controls")
        menu.addAction("Deselect Left Controls")
        menu.addAction("Deselect Right Controls")
        menu.addSeparator()
        menu.addAction("Fix Opposite Controls Mapping...")
        menu.addAction("Clear Opposite Controls Cache")

    @staticmethod
    def _build_anim_transfer_menu(menu, toolbar):
        menu.addAction("Copy Animation Range")
        menu.addAction("Paste Insert Animation")
        menu.addAction("Paste Merge Animation")
        menu.addAction("Paste Mirror Animation (L <-> R)")
        menu.addSeparator()
        menu.addAction("Export Animation File (.anim)...")
        menu.addAction("Import Animation File...")

    @staticmethod
    def _build_pose_transfer_menu(menu, toolbar):
        menu.addAction("Copy Pose")
        menu.addAction("Paste Pose")
        menu.addAction("Paste Mirror Pose")
        menu.addAction("Paste Relative Pose (Keep Offset)")
        menu.addSeparator()
        menu.addAction("Export Pose File...")
        menu.addAction("Import Pose File...")

    @staticmethod
    def _build_mirror_menu(menu, toolbar):
        menu.addAction("Mirror Current Pose")
        menu.addAction("Mirror All Keys in Range")
        menu.addSeparator()
        menu.addAction("Mirror Across X-Axis (YZ Plane)")
        menu.addAction("Mirror Across Y-Axis (XZ Plane)")
        menu.addAction("Mirror Across Z-Axis (XY Plane)")
        menu.addSeparator()
        menu.addAction("Configure Mirror Names / Rules...")

    @staticmethod
    def _build_align_menu(menu, toolbar):
        menu.addAction("Align Position Only")
        menu.addAction("Align Orientation Only")
        menu.addAction("Align Position & Orientation")
        menu.addAction("Align Scale Only")
        menu.addSeparator()
        menu.addAction("Align Over Playback Range (All Frames)")
        menu.addAction("World Space Align vs Local Align")

    @staticmethod
    def _build_space_switcher_menu(menu, toolbar):
        menu.addAction("Switch to World Space")
        menu.addAction("Switch to Root / Cog Space")
        menu.addAction("Switch to Parent Space")
        menu.addSeparator()
        menu.addAction("Bake Seamless Counter-Motion")
        menu.addAction("Configure Space Switcher Attributes...")

    @staticmethod
    def _build_bookmarks_menu(menu, toolbar):
        menu.addAction("Create Time Bookmark Here")
        menu.addAction("Edit Time Bookmarks...")
        menu.addAction("Jump to Next Bookmark")
        menu.addAction("Jump to Previous Bookmark")
        menu.addSeparator()
        menu.addAction("Clear All Time Bookmarks")
        menu.addAction("Export Bookmarks...")
        menu.addAction("Import Bookmarks...")

    @staticmethod
    def _build_motion_trail_menu(menu, toolbar):
        menu.addAction("Create Editable Motion Trail")
        menu.addAction("Force Refresh Motion Trail")
        menu.addAction("Display Key Numbers on Trail")
        menu.addAction("Orientation Tracking Axes")
        menu.addSeparator()
        menu.addAction("Clear Motion Trails")

    @staticmethod
    def _build_temp_controls_menu(menu, toolbar):
        menu.addAction("Create Temporary Controls")
        menu.addAction("Create Aim Control Constraint")
        menu.addAction("Bake & Remove Temp Controls")
        menu.addSeparator()
        menu.addAction("Revert Temp Controls")

    @staticmethod
    def _build_temp_pivot_menu(menu, toolbar):
        menu.addAction("Create Temporary Pivot Point")
        menu.addAction("Snap Pivot to Selection Center")
        menu.addAction("Bake & Clear Temporary Pivot")

    @staticmethod
    def _build_master_spline_menu(menu, toolbar):
        menu.addAction("Create Master Spline IK")
        menu.addAction("Edit Master Spline Tangents")
        menu.addAction("Bake Master Spline Motion")

    @staticmethod
    def _build_micro_manipulator_menu(menu, toolbar):
        menu.addAction("Precision: 0.001x (Ultra Fine)")
        menu.addAction("Precision: 0.010x (Micro)")
        menu.addAction("Precision: 0.100x (Fine)")
        menu.addAction("Precision: 1.000x (Standard)")

    @staticmethod
    def _build_axis_toggle_menu(menu, toolbar):
        menu.addAction("Object Space")
        menu.addAction("World Space")
        menu.addAction("Gimbal Space")
        menu.addAction("Screen / Viewport Space")

    @staticmethod
    def _build_channel_box_menu(menu, toolbar):
        menu.addAction("Auto Clear Channel Box Selection")
        menu.addAction("Highlight Selected Channels on Timeline")
        menu.addAction("Isolate Selected Curves in Graph Editor")

    @staticmethod
    def _build_graph_editor_menu(menu, toolbar):
        menu.addAction("Auto Hide Static Animation Curves")
        menu.addAction("Normalize Curve Values")
        menu.addAction("Smart Frame Curves")

    @staticmethod
    def _build_euler_filter_menu(menu, toolbar):
        menu.addAction("Apply Smart Euler Filter")
        menu.addAction("Fix 360-Degree Flips Only")
        menu.addAction("Fix Gimbal Lock Interpolation")

    @staticmethod
    def _build_camera_menu(menu, toolbar):
        menu.addAction("Orient Controls to Active Camera")
        menu.addAction("Lock Camera Navigation")

    @staticmethod
    def _build_recovery_menu(menu, toolbar):
        menu.addAction("animRecovery Time Machine Status")
        menu.addAction("View Scene History Snapshots...")
        menu.addAction("Auto-Save Interval: 1 Minute")
        menu.addAction("Auto-Save Interval: 5 Minutes")
        menu.addAction("Clear Recovery Cache")

    @staticmethod
    def _build_search_menu(menu, toolbar):
        menu.addAction("Quick Tool Search...")
        menu.addAction("Set Hotkeys & Shortcuts...")
