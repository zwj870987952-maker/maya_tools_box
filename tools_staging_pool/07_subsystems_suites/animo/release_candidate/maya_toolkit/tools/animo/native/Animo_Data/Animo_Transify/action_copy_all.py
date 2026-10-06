from maya import cmds


def run(ui):
    cmds.undoInfo(openChunk=True, chunkName="Copy All Animation")
    try:
        ui.tool.copy_all_animation_to_json()
        ui.selected_file = None
        ui.update_file_info()
    except Exception:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)
        ui.clear_focus()
