from maya import cmds

from transify_common import show_styled_error


def run(ui):
    cmds.undoInfo(openChunk=True, chunkName="Copy Animation")
    try:
        result = ui.tool.copy_selected_animation_to_json()
        if result is None:
            show_styled_error("No Keys Selected", "You need to have keys selected in the Graph Editor.")
        else:
            ui.selected_file = None
            ui.update_file_info()
    except Exception:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)
        ui.clear_focus()
