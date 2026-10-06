from maya import cmds

from transify_hotkeys import copy_selected_animation_to_json


def _clear_focus():
    try:
        cmds.setFocus("MayaWindow")
    except Exception:
        pass


try:
    copy_selected_animation_to_json()
except Exception:
    pass
finally:
    _clear_focus()
