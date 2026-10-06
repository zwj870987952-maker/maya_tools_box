from maya import cmds

from transify_hotkeys import paste_latest_animation_in_place


def _clear_focus():
    try:
        cmds.setFocus("MayaWindow")
    except Exception:
        pass


try:
    cmds.waitCursor(state=True)
    paste_latest_animation_in_place()
except Exception:
    pass
finally:
    cmds.waitCursor(state=False)
    _clear_focus()
