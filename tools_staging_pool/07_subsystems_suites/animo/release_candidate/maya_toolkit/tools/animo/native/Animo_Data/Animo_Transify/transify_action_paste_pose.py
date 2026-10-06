from maya import cmds

from transify_hotkeys import paste_pose_from_json


def _clear_focus():
    try:
        cmds.setFocus("MayaWindow")
    except Exception:
        pass


try:
    paste_pose_from_json()
except Exception:
    pass
finally:
    _clear_focus()
