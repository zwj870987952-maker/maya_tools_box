"""Explicit UE source-path menu lifecycle and read-only import data reporting."""
OWNER = 'EngineToolkitUESourcePaths'
ENTRY = 'EngineToolkitPrintSourcePaths'
MENU = 'ContentBrowser.AssetContextMenu'
SECTION = 'EngineToolkitSourcePaths'
parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'print_source_paths', 'register_menu', 'unregister_menu'], 'default': 'inspect'}}}

def _unreal():
    import unreal
    return unreal

def read_source_paths(asset):
    """All available import paths with provenance; no has_editor_property assumption."""
    row = {'asset': str(asset.get_path_name()), 'name': str(asset.get_name()), 'paths': [], 'method': None, 'errors': []}
    try:
        data = asset.get_editor_property('asset_import_data')
    except Exception as error:
        row['status'] = 'no_import_data'; row['errors'].append(str(error)); return row
    if data is None:
        row['status'] = 'no_import_data'; return row
    for method in ('get_all_filenames', 'extract_filenames', 'get_first_filename'):
        if not callable(getattr(data, method, None)):
            continue
        try:
            value = getattr(data, method)()
            paths = [value] if method == 'get_first_filename' else list(value or [])
            paths = list(dict.fromkeys(str(p) for p in paths if p))
            if paths:
                row.update(paths=paths, method=method, status='resolved'); return row
        except Exception as error:
            row['errors'].append(method + ': ' + str(error))
    try:
        info = data.get_source_data() if callable(getattr(data, 'get_source_data', None)) else data.get_editor_property('source_data')
        paths = list(dict.fromkeys(str(f.relative_filename) for f in info.source_files if f.relative_filename))
        row.update(paths=paths, method='source_data_raw', status='raw_relative' if paths else 'unresolved')
    except Exception as error:
        row['errors'].append('source_data: ' + str(error)); row['status'] = 'unresolved'
    return row

def validate(**kwargs):
    if set(kwargs) - {'action'}: raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
    u = _unreal()
    if action in ('register_menu', 'unregister_menu'):
        if not hasattr(u, 'ToolMenus'): raise RuntimeError('UE ToolMenus unavailable')
        return {'action': action, 'menu': MENU, 'section': SECTION, 'owner': OWNER, 'asset_mutations': []}
    assets = list(u.EditorUtilityLibrary.get_selected_assets())
    if len(assets) > 10000: raise ValueError('Selection exceeds 10000 assets')
    return {'action': action, 'rows': [read_source_paths(a) for a in assets], 'asset_mutations': [], 'files_written': []}

def unregister_menu():
    u = _unreal(); menus = u.ToolMenus.get()
    menus.unregister_owner_by_name(OWNER)
    menus.refresh_all_widgets()

def register_menu():
    u = _unreal(); menus = u.ToolMenus.get()
    menus.unregister_owner_by_name(OWNER)
    try:
        menu = menus.extend_menu(MENU)
        entry = u.ToolMenuEntry(name=ENTRY, owner=u.ToolMenuOwner(name=OWNER), type=u.MultiBlockType.MENU_ENTRY,
            insert_position=u.ToolMenuInsert('', u.ToolMenuInsertType.FIRST))
        entry.set_label('Print Source Paths')
        entry.set_tool_tip('Read selected assets import sources; no file writes')
        entry.set_string_command(u.ToolMenuStringCommandType.PYTHON, '',
            "from engine_toolkit.tools import ue_context_menu as t; t.run(dry_run=False, action='print_source_paths')")
        menu.add_menu_entry(SECTION, entry)
        menus.refresh_all_widgets()
    except Exception:
        menus.unregister_owner_by_name(OWNER)
        raise

def execute(**kwargs):
    plan = validate(**kwargs)
    action = plan['action']
    if action == 'register_menu': register_menu()
    elif action == 'unregister_menu': unregister_menu()
    elif action == 'print_source_paths':
        u = _unreal(); u.log('========== Selected Assets: Source File Paths ==========')
        if not plan['rows']: u.log_warning('No assets selected.')
        for row in plan['rows']:
            u.log(row['name'] + ': ' + row['status'])
            for path in row['paths']: u.log('  ' + path)
            for error in row['errors']: u.log_warning('  ' + error)
        u.log('=======================================================')
    return plan

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        return {'success': True, 'tool_id': 'ue_context_menu', 'dry_run': dry_run, 'data': data, 'errors': []}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_context_menu', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui(): return run(dry_run=False, action='register_menu')
