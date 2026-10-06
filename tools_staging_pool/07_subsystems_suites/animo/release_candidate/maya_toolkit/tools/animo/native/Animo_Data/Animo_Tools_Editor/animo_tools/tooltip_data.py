from __future__ import absolute_import, division, print_function, unicode_literals

TOOLTIP_DATA = {
    "Align Objects": {
        "title": "Align Objects",
        "description": "Align selected objects to a target object or to each other based on position, rotation, or scale.",
        "info_lines": [
            "Select multiple objects to align.",
            "Last selected object is the target.",
            "Works with transforms and joints."
        ],
        "shortcut": ""
    },
    
    "Animation Visibility Mode": {
        "title": "Animation Visibility Mode",
        "description": "Toggle viewport display to show only animation-relevant objects, hiding construction geometry and helpers.",
        "info_lines": [
            "Hides locators, curves, and joints.",
            "Keeps mesh and nurbs visible.",
            "Toggle again to restore visibility."
        ],
        "shortcut": ""
    },
    
    "Clear Animation": {
        "title": "Clear Animation",
        "description": "Remove all animation keyframes from selected objects, resetting them to their default pose.",
        "info_lines": [
            "Removes all keyframes on selection.",
            "Affects translate, rotate, and scale.",
            "Use with caution - cannot be undone easily."
        ],
        "shortcut": ""
    },
    
    "Crop Animation": {
        "title": "Crop Animation",
        "description": "Delete all keyframes outside the current timeline range, keeping only the visible animation.",
        "info_lines": [
            "Uses playback range start/end.",
            "Preserves keys within the range.",
            "Useful for cleaning up animation."
        ],
        "shortcut": ""
    },
    
    "Fast Bake": {
        "title": "Fast Bake",
        "description": "Quickly bake animation from constraints or expressions to keyframes on selected objects.",
        "info_lines": [
            "Bakes on every frame by default.",
            "Removes constraints after baking.",
            "Supports smart bake for optimization."
        ],
        "shortcut": ""
    },
    
    "Nudge Left": {
        "title": "Nudge Left",
        "description": "Move selected keyframes one frame earlier in the timeline.",
        "info_lines": [
            "Works with Graph Editor selection.",
            "Also works with timeline selection."
        ],
        "shortcut": ""
    },
    
    "Nudge Right": {
        "title": "Nudge Right",
        "description": "Move selected keyframes one frame later in the timeline.",
        "info_lines": [
            "Works with Graph Editor selection.",
            "Also works with timeline selection."
        ],
        "shortcut": ""
    },
    
    "Reset Pose": {
        "title": "Reset Pose",
        "description": "Reset selected controls to their default bind pose or zero position.",
        "info_lines": [
            "Resets translate, rotate, and scale.",
            "Respects default attribute values.",
            "Works with custom attributes too."
        ],
        "shortcut": ""
    },
    
    "Share Keys": {
        "title": "Share Keys",
        "description": "Copies keyframe timing from one control to another that has no keys, so both controls share the same key positions.",
        "info_lines": [
            "Select both controls together.",
            "Keys are added without changing values."
        ],
        "shortcut": ""
    },
    
    "Sliders Pop Up": {
        "title": "Sliders Pop Up",
        "description": "A floating panel with powerful animation sliders including Tween Machine, Blend to Neighbor, Scale to Neighboring Keys, and more.",
        "info_lines": [
            "HOTKEY RECOMMENDED",
            "UI appears at your mouse cursor.",
            "Quick access to common animation tools."
        ],
        "shortcut": ""
    },
    
    "Smart Go to Next Frame": {
        "title": "Smart Go to Next Frame",
        "description": "Move to the next frame in the timeline with smart detection of animation events.",
        "info_lines": [
            "Steps one frame forward.",
            "Respects playback range.",
            "Faster than standard navigation."
        ],
        "shortcut": ""
    },
    
    "Smart Go To Next Key": {
        "title": "Smart Go To Next Key",
        "description": "Jump to the next keyframe on selected objects or any visible animation curves.",
        "info_lines": [
            "Finds nearest key ahead.",
            "Works across all selected objects.",
            "Ignores muted channels."
        ],
        "shortcut": ""
    },
    
    "Smart Go to Next Keyframe": {
        "title": "Smart Go to Next Keyframe",
        "description": "Navigate to the next keyframe with intelligent detection across multiple objects.",
        "info_lines": [
            "Searches all selected controls.",
            "Finds the closest next key.",
            "Optimized for character animation."
        ],
        "shortcut": ""
    },
    
    "Smart Go to Previous Frame": {
        "title": "Smart Go to Previous Frame",
        "description": "Move to the previous frame in the timeline with smart detection.",
        "info_lines": [
            "Steps one frame backward.",
            "Respects playback range.",
            "Faster than standard navigation."
        ],
        "shortcut": ""
    },
    
    "Smart Go to Previous Keyframe": {
        "title": "Smart Go to Previous Keyframe",
        "description": "Navigate to the previous keyframe with intelligent detection across multiple objects.",
        "info_lines": [
            "Searches all selected controls.",
            "Finds the closest previous key.",
            "Optimized for character animation."
        ],
        "shortcut": ""
    },
    
    "Smart Snap Keys": {
        "title": "Smart Snap Keys",
        "description": "Snap selected keyframes to the nearest whole frame values.",
        "info_lines": [
            "Removes sub-frame keys.",
            "Works with Graph Editor selection.",
            "Cleans up imported animation."
        ],
        "shortcut": ""
    },
    
    "Toggle Geometry": {
        "title": "Toggle Geometry",
        "description": "Show or hide all geometry in the viewport for faster playback and cleaner view.",
        "info_lines": [
            "Toggles polygon meshes.",
            "Also affects NURBS surfaces.",
            "Useful for rig-only view."
        ],
        "shortcut": ""
    },
    
    "Toggle Imageplane": {
        "title": "Toggle Imageplane",
        "description": "Show or hide image planes in all cameras for reference image control.",
        "info_lines": [
            "Affects all camera image planes.",
            "Useful for blocking vs polish.",
            "Does not delete the planes."
        ],
        "shortcut": ""
    },
    
    "Toggle Locator": {
        "title": "Toggle Locator",
        "description": "Show or hide all locators in the scene for a cleaner viewport.",
        "info_lines": [
            "Toggles locator visibility.",
            "Includes annotation locators.",
            "Helpful for final preview."
        ],
        "shortcut": ""
    },
    
    "Toggle Wireframe Mode": {
        "title": "Toggle Wireframe Mode",
        "description": "Switch between shaded and wireframe display mode in the viewport.",
        "info_lines": [
            "Quick viewport toggle.",
            "Affects active panel only.",
            "Preserves other display settings."
        ],
        "shortcut": ""
    },
    
    "Toggle XRay Mode": {
        "title": "Toggle XRay Mode",
        "description": "Enable or disable X-Ray mode to see through geometry while animating.",
        "info_lines": [
            "See joints through mesh.",
            "Helpful for weight painting.",
            "Toggle for current viewport."
        ],
        "shortcut": ""
    },
    
    "Delete Redundant Keys": {
        "title": "Delete Redundant Keys",
        "description": "Removes static keys that have no animation value and deletes flat curves.",
        "info_lines": [
            "Deletes keys with same value as neighbors.",
            "Removes curves with no animation.",
            "Cleans up baked animation."
        ],
        "shortcut": ""
    },
}


def get_tooltip_data(tool_name):
    return TOOLTIP_DATA.get(tool_name, {
        "title": tool_name,
        "description": "No description available for this tool.",
        "info_lines": [],
        "shortcut": ""
    })
