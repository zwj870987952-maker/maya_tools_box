from maya import cmds

from transify_engine import AnimationCopyPasteJson


def copy_selected_animation_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_selected_animation_to_json()


def copy_all_animation_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_all_animation_to_json()


def paste_latest_animation_in_place():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=False)


def paste_latest_animation_original():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=False, only_selected=False)


def paste_to_selected_only():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=True)


def copy_pose_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_pose_to_json()


def paste_pose_from_json():
    tool = AnimationCopyPasteJson()
    selected = cmds.ls(selection=True)
    target_ns = tool.detect_most_common_namespace_from_selection(selected) if selected else ""
    return tool.paste_pose_from_json(
        target_namespace=target_ns if target_ns else None,
        selected_objects=selected if selected else None
    )
