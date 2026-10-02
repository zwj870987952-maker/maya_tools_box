"""UE direct hard/soft package referencers; explicit GUI and browser actions."""
import re
import threading

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'show_ui', 'locate', 'close_ui'], 'default': 'inspect'},
    'pattern': {'type': 'string', 'default': '_zoo', 'maxLength': 256},
    'package_name': {'type': 'string'}}}

def _unreal():
    import unreal
    return unreal

def _main_thread():
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError('Invoke on the UE Editor main thread; no Unreal API on workers')

def _package(name):
    if not isinstance(name, str) or not re.fullmatch(r'/[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)+', name):
        raise ValueError('Exact UE package path required, not object path')
    return name

def collect_results(pattern='_zoo'):
    _main_thread()
    if not isinstance(pattern, str) or not pattern or len(pattern) > 256: raise ValueError('Nonempty regex up to 256 characters required')
    compiled = re.compile(pattern, re.IGNORECASE)
    u = _unreal(); registry = u.AssetRegistryHelpers.get_asset_registry()
    if registry.is_loading_assets(): raise RuntimeError('Asset Registry is still loading; wait until it finishes before judging references')
    selected = list(u.EditorUtilityLibrary.get_selected_asset_data())
    if len(selected) > 10000: raise ValueError('Selection exceeds 10000 assets')
    options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True,
        include_searchable_names=False, include_soft_management_references=False, include_hard_management_references=False)
    rows, seen = [], set()
    for ad in selected:
        package = str(ad.package_name)
        if package in seen: continue
        seen.add(package)
        row = {'asset_name': str(ad.asset_name), 'package_path': package, 'correct': None, 'correct_refs': [], 'all_refs': [], 'all_ref_count': None, 'error': None}
        try:
            refs = registry.get_referencers(_package(package), options)
            if refs is None: raise RuntimeError('Registry query returned None; not a confirmed empty reference list')
            refs = sorted(set(str(p) for p in refs))
            matching = [p for p in refs if compiled.search(p)]
            row.update(correct=bool(matching), correct_refs=matching, all_refs=refs, all_ref_count=len(refs))
        except Exception as error: row['error'] = str(error)
        rows.append(row)
    return rows

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    _main_thread()
    action = kwargs.get('action', 'inspect')
    if action not in parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
    if action == 'locate':
        name = _package(kwargs.get('package_name'))
        u = _unreal(); registry = u.AssetRegistryHelpers.get_asset_registry()
        assets = list(registry.get_assets(u.ARFilter(package_names=[name])) or [])
        paths = []
        for asset in assets:
            obj = asset.get_asset()
            if obj is not None: paths.append(str(obj.get_path_name()))
        if not paths: raise ValueError('No loadable asset in exact package: ' + name)
        return {'action': action, 'package_name': name, 'object_paths': paths, 'asset_mutations': []}
    if action == 'close_ui': return {'action': action, 'asset_mutations': []}
    return {'action': action, 'pattern': kwargs.get('pattern', '_zoo'), 'rows': collect_results(kwargs.get('pattern', '_zoo')), 'asset_mutations': [], 'files_written': [],
            'scope': 'Direct on-disk package hard and soft referencers; regex case-insensitive. Not recursive/live-scene dependency validation'}

def execute(**kwargs):
    plan = validate(**kwargs)
    action = plan['action']
    if action == 'locate': _unreal().EditorAssetLibrary.sync_browser_to_objects(plan['object_paths'])
    elif action == 'show_ui':
        from .ui import show_result_window
        show_result_window(plan['rows'])
    elif action == 'close_ui':
        from .ui import close_ui
        close_ui()
    return plan

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        errors = [row['package_path'] + ': ' + row['error'] for row in data.get('rows', []) if row['error']]
        return {'success': not errors, 'tool_id': 'ue_reference_checker', 'dry_run': dry_run, 'data': data, 'errors': errors}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_reference_checker', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui(pattern='_zoo'): return run(dry_run=False, action='show_ui', pattern=pattern)
