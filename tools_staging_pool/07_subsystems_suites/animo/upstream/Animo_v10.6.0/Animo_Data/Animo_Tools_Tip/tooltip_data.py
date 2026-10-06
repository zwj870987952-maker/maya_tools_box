"""
Tooltip Data for Animo Toolbar
Contains all tooltip content: titles, descriptions, tips, and GIF references
"""
from __future__ import absolute_import, division, print_function, unicode_literals

TOOLTIP_DATA = {
    # ============================================
    # Main Toolbar Icons (Group 0: Transify group)
    # ============================================
    
    "transify_launcher": {
        "title": "Anim Transfer",
        "description": "Copy animation or poses between characters, or even across different Maya scenes with ease.",
        "info_lines": [
            "Transfer animation between rigs.",
            "Copy poses across scenes.",
            "Works with different character setups."
        ],
        "shortcut": "",
        "gif": "transify",
        "title_color": "#E07070"
    },
    
    "keys_time_launcher": {
        "title": "Keys Time",
        "description": "Save and restore your keyframe timing. Perfect for when you bake animation and want your clean keys back.",
        "info_lines": [
            "Copy key positions from controls.",
            "Paste timing back after baking.",
            "Preserve your original key structure."
        ],
        "shortcut": "",
        "gif": "keys_time",
        "title_color": "#E07070"
    },
    
    "fast_anim_layer_launcher": {
        "title": "Fast Merge AnimLayers",
        "description": "Merge animation layers 10-50x faster than Maya's native tool. A must-have for animation layer workflows.",
        "info_lines": [
            "Blazing fast layer merging.",
            "Smart merge preserves key timing.",
            "Works with selected or all layers."
        ],
        "shortcut": "",
        "gif": "fast_anim_layer",
        "title_color": "#E07070"
    },
    
    # ============================================
    # Group 1: Pickify/Tweenify/Tracify
    # ============================================
    
    "pickify_launcher": {
        "title": "Selection Sets",
        "description": "Create powerful, color-coded selection sets. Export and reuse them across different animations.",
        "info_lines": [
            "Organize controls with color coding.",
            "Export sets for other scenes.",
            "Never recreate sets again."
        ],
        "shortcut": "",
        "gif": "pickify",
        "title_color": "#E8608C"
    },
    
    "tweenify_launcher": {
        "gif_width": 500,
        "title": "Anim Sliders",
        "description": "Powerful animation sliders including Tween Machine, Blend to Neighbor, and more. Works great with Graph Editor and Channel Box selection.",
        "info_lines": [
            "Tween between keyframes smoothly.",
            "Blend values to neighboring keys.",
            "Works with timeline selection too."
        ],
        "shortcut": "",
        "gif": "tweenify",
        "title_color": "#E8608C"
    },
    
    "tracify_launcher": {
        "gif_width": 500,
        "title": "Arc Tracker",
        "description": "A lightning-fast arc tracker that won't slow down your scene, even on heavy rigs.",
        "info_lines": [
            "Visualize motion arcs in real-time.",
            "Much faster than Maya's native tracker.",
            "Essential for polishing animation."
        ],
        "shortcut": "",
        "gif": "tracify",
        "title_color": "#E8608C"
    },
    
    # ============================================
    # Group 2: Spacify/Xform/Attributes
    # ============================================
    
    "spacify_launcher": {
        "title": "Temp Controls",
        "description": "An awesome toolset for space-switching and temporary animation controls. Play around and discover new workflows!",
        "info_lines": [
            "Create temporary animation controls.",
            "Space-switch without losing poses.",
            "Flexible workflow for any rig."
        ],
        "shortcut": "",
        "gif": "spacify",
        "title_color": "#B478C8"
    },
    
    "xform_align_launcher": {
        "title": "Xform - Align",
        "description": "Two powerful tools in one! Xform stores world positions and applies them back after space changes. Align matches objects to a target's transform.",
        "info_lines": [
            "Xform: Store and restore world positions.",
            "Great after switching control spaces.",
            "Align: Match position/rotation to target."
        ],
        "shortcut": "",
        "gif": "xform_align",
        "title_color": "#B478C8"
    },
    
    "attributes_space_switcher_launcher": {
        "gif_width": 500,
        "title": "Attributes Space Switcher",
        "description": "Change the space of your controls without losing animation. Also helps find the best rotate order to avoid gimbal lock.",
        "info_lines": [
            "Switch spaces seamlessly.",
            "Preserves all your animation.",
            "Optimize rotate order automatically."
        ],
        "shortcut": "",
        "gif": "attributes_space_switcher",
        "title_color": "#B478C8"
    },
    
    "temp_pivot_launcher": {
        "title": "Temp Pivot",
        "description": "Change the pivot point of your current pose without breaking the animation. Perfect for rotating entire characters from a custom pivot point.",
        "info_lines": [
            "Adjust pivot for current pose only.",
            "Rotate characters from any point.",
            "Grab world controls for full body rotation."
        ],
        "shortcut": "",
        "gif": "temp_pivot",
        "title_color": "#B478C8"
    },
    
    # ============================================
    # Group 3: Global Offset/Twosify/Vectorify
    # ============================================
    
    "global_offset_launcher": {
        "title": "Global Offset",
        "description": "Quickly offset poses for an entire range or selection. Like animation layers, but faster and without the merge cleanup.",
        "info_lines": [
            "Offset entire pose ranges.",
            "No layer merging needed.",
            "Keeps your keyframes clean."
        ],
        "shortcut": "",
        "gif": "global_offset",
        "title_color": "#4A90D9"
    },
    
    "twosify_launcher": {
        "title": "TWOSIFY",
        "description": "Make your splined animation look stepped without destroying your curves. Attach to camera space for that Spider-Verse style!",
        "info_lines": [
            "Stepped look, splined data.",
            "Camera-space attachment option.",
            "Perfect for stylized animation."
        ],
        "shortcut": "",
        "gif": "twosify",
        "title_color": "#4A90D9"
    },
    
    "vectorify_launcher": {
        "title": "Vectorify",
        "description": "A powerful tool for repathing animation while keeping feet locked to the ground. Your planted feet stay solid throughout the repath.",
        "info_lines": [
            "Repath motion trajectories.",
            "Maintains planted feet positions.",
            "Perfect for redirecting locomotion."
        ],
        "shortcut": "",
        "gif": "vectorify",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # Group 4: Tools Editor/Quick Exporter/Playblaster
    # ============================================
    
    "tools_editor_launcher": {
        "title": "Mirror Animation",
        "description": "Mirror the pose on your selected controls. If a range is selected, the entire range gets mirrored.",
        "info_lines": [
            "Mirrors the current pose instantly.",
            "Selected range mirrors all keys in it.",
            "Great for animation cycles."
        ],
        "shortcut": "",
        "gif": "mirror_animation",
        "title_color": "#D8D0E8"
    },
    
    "quick_exporer_launcher": {
        "title": "Quick Exporter",
        "description": "Export selected objects and quickly import them into another Maya scene. Perfect for transferring assets between files.",
        "info_lines": [
            "Fast object export/import.",
            "Great for layout artists.",
            "Streamlines asset transfer."
        ],
        "shortcut": "",
        "gif": "quick_exporter",
        "title_color": "#D8D0E8"
    },
    
    "fast_multi_view_playblaster_launcher": {
        "title": "Multi-View Playblaster",
        "description": "Playblast multiple camera views at once with a single click. Perfect for checking animation from different angles.",
        "info_lines": [
            "Capture multiple views simultaneously.",
            "Great for review sessions.",
            "Export to your editing software."
        ],
        "shortcut": "",
        "gif": "multi_view_playblaster",
        "title_color": "#D8D0E8"
    },
    
    # ============================================
    # Left Side Icons (Reset, Bake, Share Keys)
    # ============================================
    
    "reset_pose_launcher": {
        "title": "Reset Pose",
        "description": "Reset selected controls to their default pose. Works with Timeline, Graph Editor, and Channel Box selection too!",
        "info_lines": [
            "Resets translate, rotate, and scale.",
            "Respects default attribute values.",
            "Works with custom attributes."
        ],
        "shortcut": "",
        "gif": "reset_pose",
        "title_color": "#E07080"
    },
    
    "share_keys_launcher": {
        "title": "Share Keys",
        "description": "Add keys on all keyframe positions across your timeline with one click. Works with Timeline, Graph Editor, and Channel Box selection.",
        "info_lines": [
            "Select controls to share keys.",
            "Keys added without changing values.",
            "Great for syncing timing."
        ],
        "shortcut": "",
        "gif": "share_keys",
        "title_color": "#E8C050"
    },
    
    # ============================================
    # Tangent Icons
    # ============================================
    
    "auto_tangent": {
        "title": "Auto Tangent",
        "description": "Set curve tangents to Auto mode for smooth, natural interpolation between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Creates flowing, organic motion."
        ],
        "shortcut": "",
        "gif": "auto_tangent",
        "title_color": "#FF8C42"
    },
    
    "linear_tangent": {
        "title": "Linear Tangent",
        "description": "Set curve tangents to Linear mode for constant-speed, straight-line motion between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Even spacing with no ease in/out."
        ],
        "shortcut": "",
        "gif": "linear_tangent",
        "title_color": "#FF8C42"
    },
    
    "step_tangent": {
        "title": "Step Tangent",
        "description": "Set curve tangents to Step mode for instant value changes with no interpolation between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Perfect for blocking and pose-to-pose workflow."
        ],
        "shortcut": "",
        "gif": "step_tangent",
        "title_color": "#FF8C42"
    },
    
    # ============================================
    # Select Opposite
    # ============================================
    
    "SelectOppositeCtrls": {
        "title": "Select Opposite",
        "description": "Instantly select the opposite side controls. A hotkey is highly recommended for this one!",
        "info_lines": [
            "Left to Right, Right to Left.",
            "Works with most rig naming conventions.",
            "Essential for mirroring workflows."
        ],
        "shortcut": "Hotkey Recommended",
        "gif": "SelectOpposite",
        "title_color": "#4A90D9"
    },
    
    "SelectAddOppositeCtrls": {
        "title": "Add Opposite to Selection",
        "description": "Add the opposite side controls to your current selection without deselecting.",
        "info_lines": [
            "Keeps current selection.",
            "Adds opposite controls.",
            "Great for symmetrical edits."
        ],
        "shortcut": "",
        "gif": "SelectOpposite",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # Nudge Keys
    # ============================================
    
    "nudge_keys_widget": {
        "title": "Nudge Keys",
        "description": "Move your selected keys forward or backward in time by the amount shown. Works with Timeline, Graph Editor and Channel Box selection.",
        "info_lines": [
            "Left arrow nudges keys backward.",
            "Right arrow nudges keys forward.",
            "Type in the field to set your nudge amount."
        ],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # White Icons (Right Side)
    # ============================================
    
    "SmoothSelectedKeys": {
        "title": "Smooth Selected Keys",
        "description": "Smooth out jittery animation curves like butter. Perfect for cleaning up mocap or noisy keyframes.",
        "info_lines": [
            "Removes unwanted jitter.",
            "Preserves overall motion.",
            "Works on selected keys."
        ],
        "shortcut": "",
        "gif": "SmoothSelectedKeys",
        "title_color": "#4A90D9"
    },
    
    "SmartSnapKeys": {
        "title": "Smart Snap Keys",
        "description": "Snap keys to whole frames intelligently. Much smarter than Maya's native tool - won't break your poses!",
        "info_lines": [
            "Removes sub-frame keys.",
            "Preserves pose integrity.",
            "Handles compressed keys gracefully."
        ],
        "shortcut": "",
        "gif": "SmartSnapKeys",
        "title_color": "#4A90D9"
    },
    
    "CropAnimation": {
        "title": "Crop Animation",
        "description": "Keep only the keys within your selected range and remove everything outside. Clean up made easy!",
        "info_lines": [
            "Uses playback range start/end.",
            "Preserves keys within range.",
            "Perfect for trimming clips."
        ],
        "shortcut": "",
        "gif": "CropAnimation",
        "title_color": "#4A90D9"
    },
    
    "DeleteRedundantKeys": {
        "gif_width": 800,
        "title": "Delete Redundant Keys",
        "description": "Remove static keys and flat curves that aren't doing anything. Essential for cleaning up baked animation.",
        "info_lines": [
            "Deletes keys with identical values.",
            "Removes flat animation curves.",
            "Optimizes your scene."
        ],
        "shortcut": "",
        "gif": "DeleteRedundantKeys",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # About & Dock
    # ============================================
    
    "about_launcher": {
        "title": "About Animo",
        "description": "Information about Animo Launcher, version details, and credits.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    },
    
    "dock_position": {
        "title": "Dock Position",
        "description": "Change where the Animo toolbar is docked in Maya's interface.",
        "info_lines": [
            "Timeline, Status Line, Shelf, and more.",
            "Choose your preferred location.",
            "Remembers your setting."
        ],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # Fast Bake Menu Options
    # ============================================
    
    "fast_bake_launcher": {
        "gif_width": 500,
        "title": "Fast Bake",
        "description": "Bake your animation 10-50x faster than Maya's native bake. Choose your stepping interval from the menu.",
        "info_lines": [
            "Lightning fast baking.",
            "Multiple step options (1s to 7s).",
            "Removes constraints after baking."
        ],
        "shortcut": "",
        "gif": "fast_bake",
        "title_color": "#E89050"
    },
    
    # ============================================
    # Animation Sliders
    # ============================================
    
    "tween_slider": {
        "title": "Tween Machine",
        "description": "Easily create breakdowns between your poses. Slide to blend toward the previous or next keyframe.",
        "info_lines": [
            "Drag left to favor previous pose.",
            "Drag right to favor next pose.",
            "Works with current time, Graph Editor, and Channel Box selection."
        ],
        "shortcut": "",
        "gif": "tween",
        "title_color": "#E1AF2D"
    },
    
    "blend_slider": {
        "title": "Blend to Neighbor",
        "description": "Blend your current pose or selected keys toward neighboring keyframes. Perfect for fine-tuning spacing and favoring poses.",
        "info_lines": [
            "Nudge animation for perfect spacing.",
            "Great for easing into poses.",
            "Works with Graph Editor and Channel Box selection."
        ],
        "shortcut": "",
        "gif": "blend_to_neighbor",
        "title_color": "#DC8C3C"
    },
    
    "scale_slider": {
        "title": "Scale from Left",
        "description": "Scale your selected keys using the key to the left as the pivot point.",
        "info_lines": [
            "Scale from Left: Pivot on left key.",
            "Scale from Right: Pivot on right key.",
            "Scale from Average: Pivot at curve center."
        ],
        "shortcut": "",
        "gif": "scale_left",
        "title_color": "#64B4DC"
    },
    
    "cascade_slider": {
        "title": "Blend to World",
        "description": "Blend your selected object toward its neighboring keys in world space. Drag right to blend toward the next key, left to blend toward the previous one.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#B478C8"
    },
    "ease_slider": {
        "title": "Ease",
        "description": "Ease your pose in or out, softening the timing around the current keyframe. Shortcut: Ctrl+TW.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#5CB8D6"
    },
    
    "scale_right_slider": {
        "title": "Scale from Right",
        "description": "Scale your selected keys using the key to the right as the pivot point. Shortcut: Shift+SL.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#71A7D6"
    },
    
    "scale_avg_slider": {
        "title": "Scale from Average",
        "description": "Scale your selected keys using the average of the curve as the pivot point. Shortcut: Ctrl+SL.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#839ED8"
    },
    
    "scale_default_slider": {
        "title": "Scale from Default",
        "description": "Scale your selected keys using the attribute's default value as the pivot point. Drag right to exaggerate away from default, left to flatten back toward it.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#91A1E0"
    },
    
    "blend_default_slider": {
        "title": "Blend to Default",
        "description": "Blend your selected keys toward the attribute's default value. Drag right toward default, left to push away from it.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#9DA4E7"
    },
    
    "time_offset_slider": {
        "title": "Time Offset",
        "description": "Offsets the animation without offsetting the timing. The more keys you have selected, the better the result.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#9687DE"
    },
    
    "time_offset_stagger_slider": {
        "title": "Time Offset Stagger",
        "description": "Offsets the animation like Time Offset, but staggers the amount based on the order you selected your objects. The first object selected offsets the most, with each object selected after it offsetting progressively less.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#A387DE"
    },
    
    "noise_wave_slider": {
        "title": "Noise / Wave",
        "description": "Add a smooth wave to your selected keys by dragging right, or randomized noise by dragging left.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#B28CE3"
    },
    
    "blend_world_slider": {
        "title": "Connect to Neighbour",
        "description": "Connect multiple animation curves to a single selected keyframe without breaking their original motion. Best used in the Graph Editor.",
        "info_lines": [
            "Select one keyframe as anchor point.",
            "All curves connect to that key.",
            "Preserves original curve shapes."
        ],
        "shortcut": "",
        "gif": "blend_to_neighbor",
        "title_color": "#CD93E6"
    },
    
    "push_pull_slider": {
        "title": "Push / Pull",
        "description": "Push or pull your selected keys relative to a straight line between their neighbors. Left aligns them linearly, right pushes them further out.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#54CED4"
    },
    
    "blend_ease_slider": {
        "title": "Blend to Ease",
        "description": "Smooth out the timing around your selected keys by blending them toward the neighboring keys. Drag right for an ease in, left for an ease out.",
        "info_lines": [
            "Great for softening mechanical or linear motion.",
            "Drag again after releasing for a stronger ease."
        ],
        "shortcut": "",
        "gif": "",
        "title_color": "#64C0DA"
    },
    
    "smooth_harsh_slider": {
        "gif_width": 500,
        "title": "Smooth | Harsh",
        "description": "Smooth your selected keys toward their neighbors by dragging right or push them further apart for a harsher, snappier feel by dragging left.",
        "info_lines": [],
        "shortcut": "",
        "gif": "smooth_harsh",
        "title_color": "#D490E4"
    },
    
    "simplify_bake_slider": {
        "title": "Simplify | Bake",
        "description": "Clean up your curves by dragging left to remove extra keys while keeping the shape or drag right to bake in more keys for denser control.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#DA8EE2"
    },
    
    "blend_infinity_slider": {
        "title": "Blend to Infinity",
        "description": "Extend the motion of your selected keys past their neighbors, as if the animation kept going. Drag right to project forward, left to project backward.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#E08CE0"
    },
    
    "blend_mirror_slider": {
        "title": "Blend to Mirror",
        "description": "Blend your pose toward its mirrored side. Drag right to move toward the mirror, left to push away from it. Make sure you've snapshotted your rig's default pose first.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#E68ACD"
    },
}


# Maps known mistyped/legacy launcher keys to their real TOOLTIP_DATA key.
# Kept for keys where the mismatch isn't a simple missing/extra "_launcher"
# suffix (those are handled automatically below).
TOOLTIP_KEY_ALIASES = {
    "tracify_track_arcs": "tracify_launcher",
}


def _normalize_key(name):
    """Lowercase and strip separators so 'Tracify_Launcher', 'tracify-launcher',
    and 'tracifylauncher' all compare equal."""
    return name.lower().replace("_", "").replace("-", "").strip()


# Auto-generated lookup: normalized key -> real TOOLTIP_DATA key. This is the
# general version of the Tracify fix: it catches ANY tool whose registered
# key differs from its TOOLTIP_DATA entry only by casing, separators, or a
# missing/extra "_launcher" suffix, so a future naming slip elsewhere in the
# codebase still surfaces the real title/description instead of the generic
# placeholder.
_NORMALIZED_KEY_LOOKUP = {}
for _key in TOOLTIP_DATA:
    _NORMALIZED_KEY_LOOKUP[_normalize_key(_key)] = _key
    if _key.endswith("_launcher"):
        _NORMALIZED_KEY_LOOKUP[_normalize_key(_key[:-len("_launcher")])] = _key
    else:
        _NORMALIZED_KEY_LOOKUP[_normalize_key(_key + "_launcher")] = _key


def get_tooltip_data(launcher_name):
    """
    Get tooltip data for a specific launcher/tool

    Resolution order:
      1. Exact key match in TOOLTIP_DATA.
      2. Explicit alias in TOOLTIP_KEY_ALIASES (known historical typos).
      3. Normalized/suffix-tolerant match against every real key, so a small
         naming mismatch (casing, separators, missing "_launcher") still
         resolves to the correct tool instead of the generic placeholder.
      4. Generic placeholder, only if nothing above matches at all.

    Args:
        launcher_name: The launcher function name or tool identifier

    Returns:
        dict with title, description, info_lines, shortcut, gif, title_color
    """
    if launcher_name in TOOLTIP_DATA:
        return TOOLTIP_DATA[launcher_name]

    aliased_name = TOOLTIP_KEY_ALIASES.get(launcher_name)
    if aliased_name and aliased_name in TOOLTIP_DATA:
        return TOOLTIP_DATA[aliased_name]

    fuzzy_match = _NORMALIZED_KEY_LOOKUP.get(_normalize_key(launcher_name))
    if fuzzy_match:
        return TOOLTIP_DATA[fuzzy_match]

    return {
        "title": launcher_name.replace("_launcher", "").replace("_", " ").title(),
        "description": "Animation tool from the Animo Launcher.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    }