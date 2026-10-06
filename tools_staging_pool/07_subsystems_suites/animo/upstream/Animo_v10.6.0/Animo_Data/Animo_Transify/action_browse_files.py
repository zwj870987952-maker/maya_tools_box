from maya import cmds

from transify_common import show_styled_error


def run(ui):
    json_files = ui.tool.get_all_json_files()

    if not json_files:
        show_styled_error("No Files Found", "No animation JSON files found in Documents folder.")
        return

    result = cmds.fileDialog2(
        fileMode=1,
        caption="Select Animation File",
        fileFilter="JSON Files (*.json)",
        startingDirectory=ui.tool.documents_path
    )

    if result:
        ui.selected_file = result[0]
        ui.update_file_info()

    ui.clear_focus()
