import maya.cmds as cmds


def _get_target_panels():
    return cmds.getPanel(type="modelPanel") or []


def _any_panel_isolated(panels):
    for panel in panels:
        try:
            if cmds.isolateSelect(panel, query=True, state=True):
                return True
        except Exception:
            pass
    return False


def _show_select_something_message():
    try:
        cmds.inViewMessage(
            amg='<span style="color:#DDDDDD;">Please select something.</span>',
            pos="midCenter",
            fade=True,
            fadeStayTime=1200,
            backColor=0xAA4D4D4D,
            alpha=0.9
        )
    except Exception:
        cmds.warning("Please select something.")


def toggle_isolate_selection():
    panels = _get_target_panels()

    if not panels:
        return

    if _any_panel_isolated(panels):
        for panel in panels:
            try:
                cmds.isolateSelect(panel, state=False)
            except Exception:
                pass
        return

    selection = cmds.ls(selection=True, long=True)

    if not selection:
        _show_select_something_message()
        return

    for panel in panels:
        try:
            cmds.isolateSelect(panel, state=False)
            cmds.isolateSelect(panel, state=True)
            cmds.select(selection, replace=True)
            cmds.isolateSelect(panel, addSelected=True)
        except Exception:
            pass

    cmds.select(selection, replace=True)


def toggle_isolate_selection_ui(*args):
    toggle_isolate_selection()


toggle_isolate_selection()