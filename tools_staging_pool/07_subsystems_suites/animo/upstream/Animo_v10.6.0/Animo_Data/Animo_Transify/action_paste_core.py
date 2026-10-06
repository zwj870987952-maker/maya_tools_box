from maya import cmds

from transify_common import (
    QtWidgets, QtGui, QtCore, PYSIDE_VERSION, dpi, get_maya_main_window,
)


def run(ui, paste_in_place=True):
    only_selected = ui.has_selection()
    target_ns = ui.get_target_namespace()

    cmds.waitCursor(state=True)
    cmds.undoInfo(openChunk=True, chunkName="Paste Animation")
    try:
        if only_selected:
            selected_objects = cmds.ls(selection=True)
            target_namespaces = ui.tool.detect_multiple_namespaces_from_selection(selected_objects)

            if len(target_namespaces) > 1:
                if ui.selected_file:
                    anim_data = ui.tool.load_animation_data(ui.selected_file)
                    filepath = ui.selected_file
                else:
                    latest_file = ui.tool.get_latest_json_file()
                    if latest_file:
                        anim_data = ui.tool.load_animation_data(latest_file)
                        filepath = latest_file
                    else:
                        anim_data = None
                        filepath = None

                if anim_data:
                    source_ns = ui.tool.detect_source_namespace(anim_data)
                    ui.tool.apply_animation_to_multiple_namespaces(
                        paste_in_place, True, source_ns, target_namespaces, filepath
                    )
                return
            else:
                target_ns_from_selection = target_namespaces[0] if target_namespaces else ""

                if ui.selected_file:
                    anim_data = ui.tool.load_animation_data(ui.selected_file)
                else:
                    latest_file = ui.tool.get_latest_json_file()
                    if latest_file:
                        anim_data = ui.tool.load_animation_data(latest_file)
                    else:
                        anim_data = None

                if anim_data:
                    source_ns = ui.tool.detect_source_namespace(anim_data)
                    if source_ns != target_ns_from_selection:
                        target_ns = target_ns_from_selection
                    else:
                        target_ns = None
        else:
            if target_ns == "":
                target_ns = None

        if ui.selected_file:
            ui.tool.paste_from_file(
                ui.selected_file,
                paste_in_place=paste_in_place,
                only_selected=only_selected,
                target_namespace=target_ns,
                skip_undo_chunk=True
            )
        else:
            ui.tool.paste_latest_animation(
                paste_in_place=paste_in_place,
                only_selected=only_selected,
                target_namespace=target_ns,
                skip_undo_chunk=True
            )
    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.waitCursor(state=False)
