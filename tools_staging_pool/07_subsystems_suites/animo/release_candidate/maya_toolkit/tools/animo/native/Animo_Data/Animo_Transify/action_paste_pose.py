from maya import cmds


def run(ui):
    cmds.undoInfo(openChunk=True, chunkName="Paste Pose")
    try:
        target_ns = ui.get_target_namespace()
        selected = cmds.ls(selection=True)

        if ui.selected_file:
            ui.tool.paste_pose_from_json(
                filepath=ui.selected_file,
                target_namespace=target_ns if target_ns else None,
                selected_objects=selected if selected else None,
                skip_undo_chunk=True
            )
        else:
            ui.tool.paste_pose_from_json(
                target_namespace=target_ns if target_ns else None,
                selected_objects=selected if selected else None,
                skip_undo_chunk=True
            )
    except Exception:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)
        ui.clear_focus()
