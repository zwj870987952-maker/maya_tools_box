from maya import cmds

from transify_hotkeys import paste_latest_animation_original


def _clear_focus():
    try:
        cmds.setFocus("MayaWindow")
    except Exception:
        pass


try:
    cmds.waitCursor(state=True)
    paste_latest_animation_original()
except Exception:
    pass
finally:
    cmds.waitCursor(state=False)
    _clear_focus()
