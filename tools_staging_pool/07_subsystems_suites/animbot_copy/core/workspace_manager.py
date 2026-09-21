"""
Complete Workspace & Tool Library Registry matching 100% of animBot's tool library.
Supports independent configurations for Main Toolbar and Graph Editor Toolbar:
- Independent locations (Main vs Graph Editor)
- Independent alignments (Left, Right, Center, Single Row)
- Independent active tools set
- Structured Slider Mode Registries with 2-letter abbreviations and dynamic tool synchronization
"""

from PySide6 import QtCore

SLIDER_CATEGORY_MODES = {
    "key_slider": [
        {"id": "slider_ease", "abbr": "EA", "label": "Ease in | Out"},
        {"id": "slider_connect_neighbors", "abbr": "CN", "label": "Connect to Neighbors"},
        {"id": "slider_gap_stitcher", "abbr": "GS", "label": "Gap Stitcher"},
        {"id": "slider_noise_wave", "abbr": "NW", "label": "Noise | Wave"},
        {"id": "slider_pull_push", "abbr": "PP", "label": "Pull | Push"},
        {"id": "slider_simplify_bake", "abbr": "SB", "label": "Simplify | Bake Keys"},
        {"id": "slider_smooth_rough", "abbr": "SR", "label": "Smooth | Rough"},
        {"id": "slider_time_offsetter", "abbr": "TO", "label": "Time Offsetter"},
        {"id": "slider_time_offsetter_stagger", "abbr": "TS", "label": "Time Offsetter Stagger"},
        {"id": "slider_scale_average", "abbr": "SA", "label": "Scale From Average"},
        {"id": "slider_scale_default", "abbr": "SD", "label": "Scale From Default"},
        {"id": "slider_scale_frame", "abbr": "SF", "label": "Scale From Frame"},
        {"id": "slider_scale_neighbor_left", "abbr": "SL", "label": "Scale From Neighbor Left"},
        {"id": "slider_scale_neighbor_right", "abbr": "SR", "label": "Scale From Neighbor Right"},
    ],
    "tween_slider": [
        {"id": "slider_tween", "abbr": "TW", "label": "Tweener"},
        {"id": "slider_tweener_world", "abbr": "WS", "label": "Tweener World Space"},
        {"id": "slider_blend_buffer", "abbr": "BB", "label": "Blend to Buffer"},
        {"id": "slider_blend_default", "abbr": "BD", "label": "Blend to Default"},
        {"id": "slider_blend_ease", "abbr": "BE", "label": "Blend to Ease"},
        {"id": "slider_blend_frame", "abbr": "BF", "label": "Blend to Frame"},
        {"id": "slider_blend_frame_world", "abbr": "FW", "label": "Blend to Frame World Space"},
        {"id": "slider_blend_neighbors", "abbr": "BN", "label": "Blend to Neighbors"},
        {"id": "slider_blend_neighbors_world", "abbr": "NW", "label": "Blend to Neighbors World Space"},
        {"id": "slider_blend_infinity", "abbr": "BI", "label": "Blend to Infinity"},
        {"id": "slider_blend_infinity_world", "abbr": "IW", "label": "Blend to Infinity World Space"},
        {"id": "slider_blend_undo", "abbr": "BU", "label": "Blend to Undo"},
    ],
    "tangent_slider": [
        {"id": "slider_tangent_best_guess", "abbr": "TB", "label": "Blend to Best Guess Tangent"},
        {"id": "slider_tangent_polished", "abbr": "TP", "label": "Blend to Polished Tangent"},
        {"id": "slider_tangent_flow", "abbr": "TF", "label": "Blend to Flow Tangent"},
        {"id": "slider_tangent_bounce", "abbr": "TB", "label": "Blend to Bounce Tangent"},
        {"id": "slider_tangent_auto", "abbr": "TA", "label": "Blend to Auto Tangent"},
        {"id": "slider_tangent_spline", "abbr": "TS", "label": "Blend to Spline Tangent"},
        {"id": "slider_tangent_clamped", "abbr": "TC", "label": "Blend to Clamped Tangent"},
        {"id": "slider_tangent_linear", "abbr": "TL", "label": "Blend to Linear Tangent"},
        {"id": "slider_tangent_flat", "abbr": "TF", "label": "Blend to Flat Tangent"},
        {"id": "slider_tangent_plateau", "abbr": "TP", "label": "Blend to Plateau Tangent"},
    ],
    "xform_slider": [
        {"id": "slider_blend_mirror", "abbr": "MR", "label": "Blend to Mirror"},
        {"id": "slider_mirror_frame", "abbr": "MF", "label": "Mirror to Frame"},
        {"id": "slider_blend_align", "abbr": "MA", "label": "Blend to Align"},
        {"id": "slider_blend_xform_rel", "abbr": "XR", "label": "Blend to Xform Relationship"},
        {"id": "slider_blend_xform_world", "abbr": "XW", "label": "Blend to Xform World Space"},
    ]
}

class WorkspaceManager(QtCore.QObject):
    workspaceChanged = QtCore.Signal(str)       # toolbar_type: "main" or "graph_editor"
    toolToggled = QtCore.Signal(str, bool, str) # tool_id, active, toolbar_type
    layoutConfigChanged = QtCore.Signal(str)    # toolbar_type

    MAIN_LOCATIONS = [
        "时间轴顶部", "时间轴底部", "工具架顶部", "工具架底部",
        "状态栏顶部", "状态栏底部", "视口顶部", "视口底部", "悬浮"
    ]
    
    GRAPH_EDITOR_LOCATIONS = [
        "图形编辑器顶部", "在图形编辑器菜单下", "图形编辑器底部"
    ]
    
    ALIGNMENTS = ["左对齐", "右对齐", "居中对齐", "单行"]

    # 100% Complete Full Tool Library
    MAIN_TOOL_LIBRARY = {
        "green": {
            "name": "Green",
            "display_name": "绿色 (Green)",
            "color": "#84F296",
            "modules": {
                "precise_transform": {
                    "label": "Precise Transform",
                    "tools": [
                        {"id": "decrease_precise_transform", "label": "Decrease Precise Transform", "icon": "minus", "tip": "Decrease Precise Transform Value"},
                        {"id": "precise_transform_value", "label": "Precise Transform Value", "icon": "spinbox", "tip": "Precise Transform Value", "is_widget": True},
                        {"id": "increase_precise_transform", "label": "Increase Precise Transform", "icon": "plus", "tip": "Increase Precise Transform Value"},
                    ]
                },
                "nudge": {
                    "label": "Nudge",
                    "tools": [
                        {"id": "nudge_left", "label": "Nudge Left", "icon": "nudge_left", "tip": "Nudge Left"},
                        {"id": "nudge_right", "label": "Nudge Right", "icon": "nudge_right", "tip": "Nudge Right"},
                        {"id": "nudge_left_time_offsetter", "label": "Nudge Left Time Offsetter", "icon": "nudge_left", "tip": "Nudge Left Time Offsetter"},
                        {"id": "nudge_right_time_offsetter", "label": "Nudge Right Time Offsetter", "icon": "nudge_right", "tip": "Nudge Right Time Offsetter"},
                        {"id": "nudge_left_all_keys", "label": "Nudge Left All Keys", "icon": "nudge_left", "tip": "Nudge Left All Keys"},
                        {"id": "nudge_right_all_keys", "label": "Nudge Right All Keys", "icon": "nudge_right", "tip": "Nudge Right All Keys"},
                        {"id": "nudge_left_scene", "label": "Nudge Left Scene", "icon": "nudge_left", "tip": "Nudge Left Scene"},
                        {"id": "nudge_right_scene", "label": "Nudge Right Scene", "icon": "nudge_right", "tip": "Nudge Right Scene"},
                        {"id": "nudge_value", "label": "Nudge Value", "icon": "spinbox", "tip": "Nudge Value", "is_widget": True},
                        {"id": "set_inbetween", "label": "Set Inbetween", "icon": "set_inbetween_on_ones", "tip": "Set Inbetween on Ones"},
                        {"id": "insert_inbetween", "label": "Insert Inbetween", "icon": "set_inbetween_on_ones", "tip": "Insert Inbetween"},
                        {"id": "remove_inbetween", "label": "Remove Inbetween", "icon": "set_inbetween_on_ones", "tip": "Remove Inbetween"},
                        {"id": "insert_inbetween_scene", "label": "Insert Inbetween Scene", "icon": "set_inbetween_on_ones", "tip": "Insert Inbetween Scene"},
                        {"id": "remove_inbetween_scene", "label": "Remove Inbetween Scene", "icon": "set_inbetween_on_ones", "tip": "Remove Inbetween Scene"},
                    ]
                },
                "default_pose": {
                    "label": "Default Pose",
                    "tools": [
                        {"id": "reset_pose", "label": "Reset Pose", "icon": "reset_pose", "tip": "Reset Pose to Default"},
                        {"id": "reset_translation", "label": "Reset Translation", "icon": "reset_translation", "tip": "Reset Translation"},
                        {"id": "reset_rotation", "label": "Reset Rotation", "icon": "reset_rotation", "tip": "Reset Rotation"},
                        {"id": "reset_scale", "label": "Reset Scale", "icon": "reset_scale", "tip": "Reset Scale"},
                        {"id": "reset_trs", "label": "Reset Translation Rotation Scale", "icon": "reset_trs", "tip": "Reset TRS"},
                        {"id": "snapshot_default_pose", "label": "Snapshot Preferred Default Pose", "icon": "restore_rig_default_pose", "tip": "Snapshot Preferred Default Pose"},
                    ]
                },
                "baking": {
                    "label": "Baking Tools",
                    "tools": [
                        {"id": "bake_interval_val", "label": "Bake Interval Value", "icon": "spinbox", "tip": "Bake Interval (Ones, Twos...)", "is_widget": True},
                        {"id": "viewport_suspend_toggle", "label": "Suspend Viewport Toggle", "icon": "as", "tip": "Auto Viewport Suspend Toggle"},
                        {"id": "bake_on_ones", "label": "Bake on Ones", "icon": "baking_step_tangent", "tip": "Bake on Ones / Custom Interval"},
                        {"id": "bake_on_twos", "label": "Bake on Twos", "icon": "bake_on_twos", "tip": "Bake on Twos"},
                        {"id": "bake_on_threes", "label": "Bake on Threes", "icon": "bake_on_threes", "tip": "Bake on Threes"},
                        {"id": "bake_on_fours", "label": "Bake on Fours", "icon": "bake_on_fours", "tip": "Bake on Fours"},
                        {"id": "bake_custom_interval", "label": "Bake Custom Interval", "icon": "bake_custom_interval", "tip": "Bake Custom Interval"},
                        {"id": "bake_from_last_selected", "label": "Bake From Last Selected", "icon": "bake_on_ones", "tip": "Bake From Last Selected"},
                        {"id": "bake_infinity", "label": "Bake Infinity", "icon": "bake_infinity", "tip": "Bake Infinity Cycle"},
                        {"id": "share_key_times", "label": "Share Key Times", "icon": "share_key_times", "tip": "Share Key Times"},
                        {"id": "share_key_times_last_selected", "label": "Share Key Times From Last Selected", "icon": "share_key_times", "tip": "Share Key Times From Last Selected"},
                        {"id": "copy_key_times", "label": "Copy Key Times", "icon": "copy_key_times", "tip": "Copy Key Times"},
                        {"id": "copy_color_key_times", "label": "Copy Color Key Times", "icon": "copy_color_key_times", "tip": "Copy Color Key Times"},
                        {"id": "paste_merge_key_times", "label": "Paste Merge Key Times", "icon": "paste_merge_key_times", "tip": "Paste Merge Key Times"},
                        {"id": "paste_insert_key_times", "label": "Paste Insert Key Times", "icon": "paste_insert_key_times", "tip": "Paste Insert Key Times"},
                        {"id": "paste_replace_key_times", "label": "Paste Replace Key Times", "icon": "paste_replace_key_times", "tip": "Paste Replace Key Times"},
                        {"id": "paste_tint_key_times", "label": "Paste Tint Key Times", "icon": "paste_tint_key_times", "tip": "Paste Tint Key Times"},
                    ]
                },
                "key_slider": {
                    "label": "Key Slider",
                    "tools": [
                        {"id": m["id"], "label": f"{m['abbr']} - {m['label']}", "icon": "ea", "tip": f"{m['label']} Slider", "is_slider": True, "abbr": m["abbr"], "slider_group": "key_slider"}
                        for m in SLIDER_CATEGORY_MODES["key_slider"]
                    ]
                }
            }
        },
        "yellow": {
            "name": "Yellow",
            "display_name": "黄色 (Yellow)",
            "color": "#F2E66C",
            "modules": {
                "tween_slider": {
                    "label": "Tween Slider",
                    "tools": [
                        {"id": m["id"], "label": f"{m['abbr']} - {m['label']}", "icon": "tw", "tip": f"{m['label']} Slider", "is_slider": True, "abbr": m["abbr"], "slider_group": "tween_slider"}
                        for m in SLIDER_CATEGORY_MODES["tween_slider"]
                    ]
                }
            }
        },
        "orange": {
            "name": "Orange",
            "display_name": "橙色 (Orange)",
            "color": "#F2A785",
            "modules": {
                "tangents": {
                    "label": "Tangents",
                    "tools": [
                        {"id": "tangent_cycle_match", "label": "Cycle Match Tangent", "icon": "auto_tangent", "tip": "Cycle Match Tangent"},
                        {"id": "tangent_best_guess", "label": "Best Guess Tangent", "icon": "best_guess_tangent", "tip": "Best Guess Tangent"},
                        {"id": "tangent_polished", "label": "Polished Tangent", "icon": "bpt", "tip": "Polished / Stepped Tangent"},
                        {"id": "tangent_flow", "label": "Flow Tangent", "icon": "bounce_tangent", "tip": "Flow Tangent"},
                        {"id": "tangent_bounce", "label": "Bounce Tangent", "icon": "bounce_tangent", "tip": "Bounce Tangent"},
                        {"id": "tangent_auto", "label": "Auto Tangent", "icon": "auto_tangent", "tip": "Auto Tangent / Spline"},
                        {"id": "tangent_spline", "label": "Spline Tangent", "icon": "auto_tangent", "tip": "Spline Tangent"},
                        {"id": "tangent_clamped", "label": "Clamped Tangent", "icon": "bct", "tip": "Clamped Tangent"},
                        {"id": "tangent_linear", "label": "Linear Tangent", "icon": "blt", "tip": "Linear Tangent"},
                        {"id": "tangent_flat", "label": "Flat Tangent", "icon": "bft", "tip": "Flat Tangent"},
                        {"id": "tangent_stepped", "label": "Step Tangent", "icon": "bpt", "tip": "Step Tangent"},
                        {"id": "tangent_plateau", "label": "Plateau Tangent", "icon": "bft", "tip": "Plateau Tangent"},
                    ]
                },
                "tangent_slider": {
                    "label": "Tangent Slider",
                    "tools": [
                        {"id": m["id"], "label": f"{m['abbr']} - {m['label']}", "icon": "auto_tangent", "tip": f"{m['label']} Slider", "is_slider": True, "abbr": m["abbr"], "slider_group": "tangent_slider"}
                        for m in SLIDER_CATEGORY_MODES["tangent_slider"]
                    ]
                }
            }
        },
        "colors": {
            "name": "Colors",
            "display_name": "颜色 (Colors)",
            "color": "#888888",
            "modules": {
                "color_keys": {
                    "label": "Color Keys",
                    "tools": [
                        {"id": "tint_key_red", "label": "Tint Key Red", "icon": "tint_key_red", "tip": "Tint Key Red"},
                        {"id": "tint_key_yellow", "label": "Tint Key Yellow", "icon": "tint_key_yellow", "tip": "Tint Key Yellow"},
                        {"id": "tint_key_green", "label": "Tint Key Green", "icon": "tint_key_green", "tip": "Tint Key Green"},
                        {"id": "smart_tint_keys", "label": "Smart Tint Keys", "icon": "smart_tint_keys", "tip": "Smart Tint Keys / Clear Tint"},
                    ]
                }
            }
        },
        "purple": {
            "name": "Purple",
            "display_name": "Purple",
            "color": "#D9D0F2",
            "modules": {
                "selection_tools": {
                    "label": "Selection Tools",
                    "tools": [
                        {"id": "select_sets", "label": "Select Sets", "icon": "select_sets", "tip": "Smart Select Sets"},
                        {"id": "select_opposite", "label": "Select Opposite", "icon": "auto_select_opposite", "tip": "Select Opposite Controls"},
                        {"id": "snapshot_opposite", "label": "Snapshot Opposite Controls", "icon": "auto_select_opposite", "tip": "Snapshot Opposite Controls"},
                    ]
                },
                "anim_pose_transfer": {
                    "label": "Anim Pose Transfer",
                    "tools": [
                        {"id": "copy_anim", "label": "Copy Animation", "icon": "copy_animation", "tip": "Copy Animation Range"},
                        {"id": "paste_insert_anim", "label": "Paste Insert Animation", "icon": "paste_insert_animation", "tip": "Paste Insert Animation"},
                        {"id": "paste_replace_anim", "label": "Paste Replace Animation", "icon": "paste_insert_animation", "tip": "Paste Replace Animation"},
                        {"id": "copy_pose", "label": "Copy Pose", "icon": "copy_pose", "tip": "Copy Pose"},
                        {"id": "paste_pose", "label": "Paste Pose", "icon": "paste_pose", "tip": "Paste Pose"},
                    ]
                }
            }
        },
        "pink": {
            "name": "Pink",
            "display_name": "Pink",
            "color": "#F2C3ED",
            "modules": {
                "mirror": {
                    "label": "Mirror",
                    "tools": [
                        {"id": "mirror_pose", "label": "Mirror Pose", "icon": "mirror_pose", "tip": "Mirror Pose"},
                        {"id": "mirror_to_right", "label": "Mirror to Right", "icon": "mirror_pose", "tip": "Mirror to Right"},
                        {"id": "mirror_to_left", "label": "Mirror to Left", "icon": "mirror_pose", "tip": "Mirror to Left"},
                        {"id": "mirror_all_keys", "label": "Mirror All Keys", "icon": "mirror_pose", "tip": "Mirror All Keys"},
                        {"id": "snapshot_mirror", "label": "Snapshot Mirror Settings", "icon": "mirror_pose", "tip": "Snapshot Mirror Settings"},
                    ]
                },
                "align_objects": {
                    "label": "Align Objects",
                    "tools": [
                        {"id": "align_objects", "label": "Align Objects", "icon": "align_objects", "tip": "Align Objects"},
                        {"id": "align_objects_all_keys", "label": "Align Objects All Keys", "icon": "align_objects", "tip": "Align Objects Across Range"},
                    ]
                },
                "xform_tools": {
                    "label": "Xform Tools",
                    "tools": [
                        {"id": "copy_xform_relationship", "label": "Copy Xform Relationship", "icon": "asset_attribute_space_switcher", "tip": "Copy Xform Relationship"},
                        {"id": "paste_xform_relationship", "label": "Paste Xform Relationship", "icon": "asset_attribute_space_switcher", "tip": "Paste Xform Relationship"},
                        {"id": "copy_xform_world_space", "label": "Copy Xform World Space", "icon": "asset_attribute_space_switcher", "tip": "Copy Xform World Space"},
                        {"id": "paste_xform_world_space", "label": "Paste Xform World Space", "icon": "asset_attribute_space_switcher", "tip": "Paste Xform World Space"},
                    ]
                },
                "attribute_space_switcher": {
                    "label": "Attribute Space Switcher",
                    "tools": [
                        {"id": "space_switcher", "label": "Selection Attribute Space Switcher", "icon": "asset_attribute_space_switcher", "tip": "Attribute Space Switcher"},
                        {"id": "asset_space_switcher", "label": "Asset Attribute Space Switcher", "icon": "asset_attribute_space_switcher", "tip": "Asset Attribute Space Switcher"},
                    ]
                },
                "xform_slider": {
                    "label": "Xform Slider",
                    "tools": [
                        {"id": m["id"], "label": f"{m['abbr']} - {m['label']}", "icon": "mirror_pose", "tip": f"{m['label']} Slider", "is_slider": True, "abbr": m["abbr"], "slider_group": "xform_slider"}
                        for m in SLIDER_CATEGORY_MODES["xform_slider"]
                    ]
                }
            }
        },
        "turquoise": {
            "name": "Turquoise",
            "display_name": "Turquoise",
            "color": "#9DECF2",
            "modules": {
                "master_spline": {
                    "label": "Master Spline",
                    "tools": [
                        {"id": "master_spline", "label": "Master Spline", "icon": "create_master_spline", "tip": "Master Spline IK Tool"},
                    ]
                },
                "temp_controls": {
                    "label": "Temp Controls",
                    "tools": [
                        {"id": "temp_controls", "label": "Temp Controls", "icon": "clear_temp_controls", "tip": "Temporary Animation Controls"},
                        {"id": "temp_controls_grab", "label": "Temp Controls Grab Release Space", "icon": "clear_temp_controls", "tip": "Grab Release Space"},
                        {"id": "temp_controls_anim", "label": "Temp Controls Anim Controls", "icon": "clear_temp_controls", "tip": "Temp Controls Anim Controls"},
                    ]
                },
                "temp_pivot": {
                    "label": "Temp Pivot",
                    "tools": [
                        {"id": "temp_pivot", "label": "Temp Pivot", "icon": "temp_pivot", "tip": "Temporary Pivot Point"},
                        {"id": "temp_pivot_last_object", "label": "Temp Pivot to Last Object", "icon": "temp_pivot", "tip": "Temp Pivot to Last Object"},
                        {"id": "temp_pivot_centered", "label": "Temp Pivot Centered", "icon": "temp_pivot", "tip": "Temp Pivot Centered"},
                        {"id": "temp_pivot_world", "label": "Temp Pivot World Space", "icon": "temp_pivot", "tip": "Temp Pivot World Space"},
                        {"id": "toggle_edit_temp_pivot", "label": "Toggle Edit Temp Pivot", "icon": "temp_pivot", "tip": "Toggle Edit Temp Pivot"},
                        {"id": "reset_temp_pivot", "label": "Reset Temp Pivot", "icon": "temp_pivot", "tip": "Reset Temp Pivot"},
                    ]
                },
                "micro_manipulator": {
                    "label": "Micro Manipulator",
                    "tools": [
                        {"id": "micro_manipulator", "label": "Micro Manipulator", "icon": "micro_manipulator", "tip": "Micro Manipulator"},
                    ]
                },
                "global_offset": {
                    "label": "Global Offset",
                    "tools": [
                        {"id": "global_offset", "label": "Global Offset", "icon": "global_offset", "tip": "Global Offset Animation"},
                        {"id": "global_offset_falloff", "label": "Global Offset Set Falloff", "icon": "global_offset", "tip": "Global Offset Set Falloff"},
                        {"id": "global_offset_pre_falloff", "label": "Global Offset Set Pre Falloff", "icon": "global_offset", "tip": "Global Offset Set Pre Falloff"},
                        {"id": "global_offset_post_falloff", "label": "Global Offset Set Post Falloff", "icon": "global_offset", "tip": "Global Offset Set Post Falloff"},
                    ]
                }
            }
        },
        "red": {
            "name": "Red",
            "display_name": "红色 (Red)",
            "color": "#FF6B6B",
            "modules": {
                "motion_trail": {
                    "label": "Motion Trail",
                    "tools": [
                        {"id": "motion_trail", "label": "Motion Trail", "icon": "create_motion_trail", "tip": "Create Editable Motion Trail"},
                        {"id": "motion_trail_offset", "label": "Motion Trail Offset", "icon": "create_motion_trail", "tip": "Motion Trail Offset"},
                        {"id": "motion_trail_orientation", "label": "Motion Trail Orientation Tracking", "icon": "create_motion_trail", "tip": "Motion Trail Orientation Tracking"},
                        {"id": "motion_trail_style", "label": "Motion Trail Style", "icon": "create_motion_trail", "tip": "Motion Trail Style"},
                        {"id": "motion_trail_frames", "label": "Motion Trail Frames Before After", "icon": "create_motion_trail", "tip": "Motion Trail Frames Before After"},
                        {"id": "motion_trail_space", "label": "Motion Trail Space", "icon": "create_motion_trail", "tip": "Motion Trail Space"},
                    ]
                },
                "viewport_suspend": {
                    "label": "Viewport Suspend",
                    "tools": [
                        {"id": "auto_suspend", "label": "Suspend Viewport", "icon": "auto_suspend_viewport", "tip": "Auto Suspend Viewport Refresh"},
                    ]
                },
                "time_bookmarks": {
                    "label": "Time Bookmarks",
                    "tools": [
                        {"id": "time_bookmarks", "label": "Time Bookmarks", "icon": "edit_time_bookmark", "tip": "Time Bookmarks Manager"},
                        {"id": "time_bookmarks_visibility", "label": "Time Bookmarks Visibility", "icon": "edit_time_bookmark", "tip": "Time Bookmarks Visibility"},
                        {"id": "go_to_time_bookmark", "label": "Go to Time Bookmark", "icon": "edit_time_bookmark", "tip": "Go to Time Bookmark"},
                        {"id": "go_to_prev_time_bookmark", "label": "Go to Previous Time Bookmark", "icon": "edit_time_bookmark", "tip": "Go to Previous Time Bookmark"},
                        {"id": "go_to_next_time_bookmark", "label": "Go to Next Time Bookmark", "icon": "edit_time_bookmark", "tip": "Go to Next Time Bookmark"},
                        {"id": "edit_time_bookmark", "label": "Edit Time Bookmark", "icon": "edit_time_bookmark", "tip": "Edit Time Bookmark"},
                        {"id": "remove_time_bookmark", "label": "Remove Time Bookmark", "icon": "edit_time_bookmark", "tip": "Remove Time Bookmark"},
                    ]
                },
                "playback_tools": {
                    "label": "Playback Tools",
                    "tools": [
                        {"id": "play_keys", "label": "Play Keys", "icon": "bake_on_ones", "tip": "Play Keys Only"},
                        {"id": "play_color_keys", "label": "Play Color Keys", "icon": "bake_on_ones", "tip": "Play Color Keys"},
                        {"id": "play_on_ones", "label": "Play on Ones", "icon": "bake_on_ones", "tip": "Play on Ones"},
                        {"id": "play_on_twos", "label": "Play on Twos", "icon": "bake_on_twos", "tip": "Play on Twos"},
                        {"id": "play_on_threes", "label": "Play on Threes", "icon": "bake_on_threes", "tip": "Play on Threes"},
                        {"id": "play_on_fours", "label": "Play on Fours", "icon": "bake_on_fours", "tip": "Play on Fours"},
                    ]
                }
            }
        },
        "blue": {
            "name": "Blue",
            "display_name": "Blue",
            "color": "#C1E2F2",
            "modules": {
                "anim_curve_extra": {
                    "label": "Anim Curve Extra Tools",
                    "tools": [
                        {"id": "anim_curve_extra_tools", "label": "Anim Curve Extra Tools", "icon": "anim_curve_extra_tools", "tip": "Anim Curve Extra Tools"},
                        {"id": "euler_filter", "label": "Apply Smart Euler Filter", "icon": "apply_smart_euler_filter", "tip": "Smart Euler Filter"},
                        {"id": "clear_animation", "label": "Clear Animation", "icon": "auto_clear_channel_box_selection", "tip": "Clear Animation"},
                        {"id": "crop_animation", "label": "Crop Animation", "icon": "anim_curve_extra_tools", "tip": "Crop Animation Range"},
                        {"id": "remove_redundant_keys", "label": "Remove Redundant Keys", "icon": "anim_curve_extra_tools", "tip": "Remove Redundant Keys"},
                        {"id": "remove_static_anim_curves", "label": "Remove Static Anim Curves", "icon": "anim_curve_extra_tools", "tip": "Remove Static Anim Curves"},
                        {"id": "reverse_animation", "label": "Reverse Animation", "icon": "anim_curve_extra_tools", "tip": "Reverse Animation"},
                        {"id": "copy_keys", "label": "Copy Keys", "icon": "copy_key_times", "tip": "Copy Keys"},
                        {"id": "cut_keys", "label": "Cut Keys", "icon": "copy_key_times", "tip": "Cut Keys"},
                        {"id": "paste_keys", "label": "Paste Keys", "icon": "paste_insert_animation", "tip": "Paste Keys"},
                        {"id": "paste_keys_relative", "label": "Paste Keys Relative", "icon": "paste_insert_animation", "tip": "Paste Keys Relative"},
                        {"id": "delete_keys", "label": "Delete Keys", "icon": "auto_clear_channel_box_selection", "tip": "Delete Keys"},
                        {"id": "set_smart_key", "label": "Set Smart Key", "icon": "set_inbetween_on_ones", "tip": "Set Smart Key"},
                        {"id": "smart_snap_keys", "label": "Smart Snap Keys", "icon": "set_inbetween_on_ones", "tip": "Smart Snap Keys"},
                    ]
                },
                "channel_box_extra": {
                    "label": "Channel Box Extra Tools",
                    "tools": [
                        {"id": "channel_box_tools", "label": "Channel Box Extra Tools", "icon": "auto_clear_channel_box_selection", "tip": "Channel Box Extra Tools"},
                        {"id": "sliders_helper", "label": "Channel Box Multi Selection Helper", "icon": "channel_box_multi_selection_helper", "tip": "Multi Selection Helper"},
                        {"id": "auto_clear_channel_box", "label": "Auto Clear Channel Box Selection", "icon": "auto_clear_channel_box_selection", "tip": "Auto Clear Channel Box Selection"},
                        {"id": "clear_channel_box", "label": "Clear Channel Box Selection", "icon": "auto_clear_channel_box_selection", "tip": "Clear Channel Box Selection"},
                    ]
                },
                "graph_editor_extra": {
                    "label": "Graph Editor Extra Tools",
                    "tools": [
                        {"id": "graph_editor_tools", "label": "Graph Editor Extra Tools", "icon": "anim_curve_extra_tools", "tip": "Graph Editor Extra Tools"},
                        {"id": "graph_editor_toolbar_toggle", "label": "Graph Editor Toolbar", "icon": "anim_curve_extra_tools", "tip": "Toggle Graph Editor Toolbar"},
                        {"id": "auto_hide_static_curves", "label": "Auto Hide Static Anim Curves", "icon": "anim_curve_extra_tools", "tip": "Auto Hide Static Curves"},
                        {"id": "frame_current_second", "label": "Frame Current Second", "icon": "anim_curve_extra_tools", "tip": "Frame Current Second"},
                        {"id": "frame_next_second", "label": "Frame Next Second", "icon": "anim_curve_extra_tools", "tip": "Frame Next Second"},
                    ]
                },
                "manipulator_extra": {
                    "label": "Manipulator Extra Tools",
                    "tools": [
                        {"id": "axis_toggle", "label": "Axis Orientation Toggle", "icon": "axis_orientation_toggle", "tip": "Toggle Axis Orientation"},
                        {"id": "cam_orient", "label": "Axis Orient to Camera", "icon": "axis_orient_to_camera", "tip": "Orient to Active Camera"},
                        {"id": "axis_orient_last_selected", "label": "Axis Orient to Last Selected", "icon": "axis_orientation_toggle", "tip": "Axis Orient to Last Selected"},
                    ]
                },
                "selection_extra": {
                    "label": "Selection Extra Tools",
                    "tools": [
                        {"id": "select_objects_from_keys", "label": "Select Objects From Keys", "icon": "select_sets", "tip": "Select Objects From Keys"},
                        {"id": "deselect_static_objects", "label": "Deselect Static Objects", "icon": "select_sets", "tip": "Deselect Static Objects"},
                        {"id": "select_all_anim_curves", "label": "Select All Anim Curves in the Scene", "icon": "anim_curve_extra_tools", "tip": "Select All Anim Curves"},
                        {"id": "grow_keys_selection", "label": "Grow Keys Selection", "icon": "select_sets", "tip": "Grow Keys Selection"},
                        {"id": "shrink_keys_selection", "label": "Shrink Keys Selection", "icon": "select_sets", "tip": "Shrink Keys Selection"},
                    ]
                },
                "subrow_extra": {
                    "label": "More Extra Utilities",
                    "tools": [
                        {"id": "bookmark_sub", "label": "Bookmark Ribbon Submenu", "icon": "edit_time_bookmark", "tip": "Bookmark Ribbon"},
                        {"id": "bake_sub", "label": "Baking Tools Submenu", "icon": "baking_step_tangent", "tip": "Baking Submenu"},
                        {"id": "more_tools", "label": "More Extra Tools", "icon": "more", "tip": "More Extra Tools"},
                        {"id": "euler_e", "label": "Euler Filter Tool E", "icon": "apply_smart_euler_filter", "tip": "Euler Filter Tool"},
                    ]
                }
            }
        },
        "white": {
            "name": "White",
            "display_name": "White",
            "color": "#FFFFFF",
            "modules": {
                "global_tools": {
                    "label": "Global Tools",
                    "tools": [
                        {"id": "recovery_monitor", "label": "Anim Recovery Time Machine", "icon": "anim_recovery_green", "tip": "animRecovery Time Machine Status"},
                        {"id": "global_search", "label": "Search & Hotkeys", "icon": "search", "tip": "Quick Tool Search & Hotkey Manager"},
                    ]
                }
            }
        }
    }

    CLASSIC_DEFAULT_TOOLS = [
        "decrease_precise_transform", "precise_transform_value", "increase_precise_transform",
        "nudge_left", "nudge_right",
        "bake_interval_val", "viewport_suspend_toggle", "bake_on_ones", "share_key_times",
        "slider_ease",
        "slider_tween",
        "tangent_best_guess", "tangent_stepped", "tangent_bounce", "tangent_auto",
        "tangent_clamped", "tangent_linear", "tangent_flat",
        "smart_tint_keys", "tint_key_red", "tint_key_yellow", "tint_key_green",
        "select_sets", "select_opposite", "copy_anim", "paste_insert_anim", "copy_pose", "paste_pose",
        "mirror_pose", "align_objects", "space_switcher",
        "time_bookmarks", "motion_trail", "auto_suspend",
        "temp_controls", "temp_pivot", "master_spline",
        "slider_blend_mirror",
        "micro_manipulator", "axis_toggle", "channel_box_tools", "graph_editor_tools",
        "euler_filter", "bookmark_sub", "bake_sub", "more_tools", "euler_e",
        "sliders_helper", "cam_orient", "recovery_monitor", "global_search"
    ]

    CLASSIC_GRAPH_EDITOR_TOOLS = [
        "decrease_precise_transform", "precise_transform_value", "increase_precise_transform",
        "nudge_left", "nudge_right", "bake_on_ones",
        "slider_ease", "slider_tween",
        "tangent_auto", "tangent_spline", "tangent_clamped", "tangent_linear", "tangent_flat", "tangent_stepped",
        "smart_tint_keys", "copy_keys", "paste_keys", "euler_filter", "auto_hide_static_curves"
    ]

    PRESETS = {
        "Classic *": {
            "main": {
                "active_tools": CLASSIC_DEFAULT_TOOLS,
                "location": "时间轴顶部",
                "alignment": "居中对齐",
                "single_row": False,
            },
            "graph_editor": {
                "active_tools": CLASSIC_GRAPH_EDITOR_TOOLS,
                "location": "在图形编辑器菜单下",
                "alignment": "居中对齐",
                "single_row": False,
            }
        },
        "新手 (Beginner)": {
            "main": {
                "active_tools": [
                    "decrease_precise_transform", "precise_transform_value", "increase_precise_transform",
                    "nudge_left", "nudge_right", "slider_tween",
                    "tangent_auto", "tangent_linear", "tangent_flat", "tangent_stepped",
                    "copy_pose", "paste_pose", "mirror_pose"
                ],
                "location": "时间轴顶部",
                "alignment": "居中对齐",
                "single_row": False,
            },
            "graph_editor": {
                "active_tools": CLASSIC_GRAPH_EDITOR_TOOLS,
                "location": "在图形编辑器菜单下",
                "alignment": "居中对齐",
                "single_row": False,
            }
        },
        "Compact": {
            "main": {
                "active_tools": [
                    "decrease_precise_transform", "precise_transform_value", "increase_precise_transform",
                    "slider_ease", "slider_tween",
                    "tangent_auto", "tangent_linear", "tangent_flat", "tangent_stepped",
                    "copy_anim", "paste_insert_anim", "mirror_pose", "slider_blend_mirror"
                ],
                "location": "时间轴顶部",
                "alignment": "居中对齐",
                "single_row": True,
            },
            "graph_editor": {
                "active_tools": CLASSIC_GRAPH_EDITOR_TOOLS,
                "location": "在图形编辑器菜单下",
                "alignment": "居中对齐",
                "single_row": True,
            }
        },
        "Expert": {
            "main": {
                "active_tools": None,
                "location": "时间轴顶部",
                "alignment": "居中对齐",
                "single_row": False,
            },
            "graph_editor": {
                "active_tools": None,
                "location": "在图形编辑器菜单下",
                "alignment": "居中对齐",
                "single_row": False,
            }
        }
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_preset = "Classic *"
        
        self.toolbar_configs = {
            "main": {
                "location": "时间轴顶部",
                "alignment": "center",
                "single_row": False,
                "active_tools": set(self.CLASSIC_DEFAULT_TOOLS),
            },
            "graph_editor": {
                "location": "在图形编辑器菜单下",
                "alignment": "center",
                "single_row": False,
                "active_tools": set(self.CLASSIC_GRAPH_EDITOR_TOOLS),
            }
        }

    def _init_all_active(self, target="all"):
        all_ids = set()
        for cat in self.MAIN_TOOL_LIBRARY.values():
            for mod in cat["modules"].values():
                for t in mod["tools"]:
                    all_ids.add(t["id"])
        if target in ("all", "main"):
            self.toolbar_configs["main"]["active_tools"] = set(all_ids)
        if target in ("all", "graph_editor"):
            self.toolbar_configs["graph_editor"]["active_tools"] = set(all_ids)

    def get_location(self, toolbar_type="main"):
        return self.toolbar_configs.get(toolbar_type, {}).get("location", "时间轴顶部" if toolbar_type == "main" else "在图形编辑器菜单下")

    def set_location(self, toolbar_type, location):
        if toolbar_type in self.toolbar_configs:
            self.toolbar_configs[toolbar_type]["location"] = location
            self.layoutConfigChanged.emit(toolbar_type)

    def get_alignment(self, toolbar_type="main"):
        return self.toolbar_configs.get(toolbar_type, {}).get("alignment", "center")

    def set_alignment(self, toolbar_type, alignment):
        if toolbar_type in self.toolbar_configs:
            self.toolbar_configs[toolbar_type]["alignment"] = alignment
            self.layoutConfigChanged.emit(toolbar_type)

    def get_single_row(self, toolbar_type="main"):
        return self.toolbar_configs.get(toolbar_type, {}).get("single_row", False)

    def set_single_row(self, toolbar_type, single_row):
        if toolbar_type in self.toolbar_configs:
            self.toolbar_configs[toolbar_type]["single_row"] = single_row
            self.layoutConfigChanged.emit(toolbar_type)

    def is_tool_active(self, tool_id, toolbar_type="main"):
        return tool_id in self.toolbar_configs.get(toolbar_type, {}).get("active_tools", set())

    def set_tool_active(self, tool_id, active, toolbar_type="main"):
        target_set = self.toolbar_configs.get(toolbar_type, {}).get("active_tools")
        if target_set is not None:
            if active:
                target_set.add(tool_id)
            else:
                target_set.discard(tool_id)
            self.toolToggled.emit(tool_id, active, toolbar_type)
            self.workspaceChanged.emit(toolbar_type)

    def apply_preset(self, preset_name):
        if preset_name in self.PRESETS:
            self.current_preset = preset_name
            p_data = self.PRESETS[preset_name]
            
            for t_type in ("main", "graph_editor"):
                cfg = p_data.get(t_type, {})
                tools = cfg.get("active_tools")
                if tools is None:
                    self._init_all_active(t_type)
                else:
                    self.toolbar_configs[t_type]["active_tools"] = set(tools)
                    
                align_str = cfg.get("alignment", "居中对齐")
                if "左" in align_str:
                    self.toolbar_configs[t_type]["alignment"] = "left"
                elif "右" in align_str:
                    self.toolbar_configs[t_type]["alignment"] = "right"
                else:
                    self.toolbar_configs[t_type]["alignment"] = "center"
                    
                self.toolbar_configs[t_type]["single_row"] = cfg.get("single_row", False)
                self.toolbar_configs[t_type]["location"] = cfg.get("location", "时间轴顶部" if t_type == "main" else "在图形编辑器菜单下")
                
            self.workspaceChanged.emit("main")
            self.workspaceChanged.emit("graph_editor")
            self.layoutConfigChanged.emit("main")
            self.layoutConfigChanged.emit("graph_editor")

# Singleton instance
WORKSPACE_MGR = WorkspaceManager()
