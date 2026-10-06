from maya import cmds


def run(ui):
    cmds.undoInfo(openChunk=True, chunkName="Select Objects")
    try:
        if ui.selected_file:
            ui.tool.select_objects_from_json_file(ui.selected_file)
        else:
            ui.tool.select_objects_from_json()
    except Exception:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)
        ui.clear_focus()
