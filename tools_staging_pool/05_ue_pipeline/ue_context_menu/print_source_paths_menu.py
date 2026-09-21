#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unreal

def get_source_paths_from_selected():
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    if not selected_assets:
        unreal.log_warning('No assets selected. Please select assets in the Content Browser.')
        return

    unreal.log('========== Selected Assets: Source File Paths ==========')
    for asset in selected_assets:
        asset_name = asset.get_name()
        if not asset.has_editor_property('asset_import_data'):
            unreal.log(f'{asset_name}: No import data available.')
            continue

        import_data = asset.get_editor_property('asset_import_data')
        paths = []
        if hasattr(import_data, 'get_all_filenames'):
            paths = list(import_data.get_all_filenames())
        if not paths and hasattr(import_data, 'extract_filenames'):
            paths = list(import_data.extract_filenames())
        if not paths and hasattr(import_data, 'get_first_filename'):
            first = import_data.get_first_filename()
            if first:
                paths = [first]
        if not paths and hasattr(import_data, 'get_source_data'):
            try:
                files = import_data.get_source_data().source_files
                paths = [sf.relative_filename for sf in files if sf.relative_filename]
            except Exception:
                pass

        if paths:
            unreal.log(f'{asset_name}:')
            for p in paths:
                unreal.log(f'  {p}')
        else:
            unreal.log(f'{asset_name}: Unable to resolve source file paths.')
    unreal.log('=======================================================')

def register_menu():
    menus = unreal.ToolMenus.get()
    menu = menus.extend_menu('ContentBrowser.AssetContextMenu.AssetActions')
    entry = unreal.ToolMenuEntry(
        name='PrintSourcePaths',
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert('', unreal.ToolMenuInsertType.FIRST)
    )
    entry.set_label('Print Source Paths')
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, '', 'import print_source_paths_menu; print_source_paths_menu.get_source_paths_from_selected()')
    menu.add_menu_entry('AssetActions', entry)
    menus.refresh_all_widgets()

# register on module load
register_menu() 