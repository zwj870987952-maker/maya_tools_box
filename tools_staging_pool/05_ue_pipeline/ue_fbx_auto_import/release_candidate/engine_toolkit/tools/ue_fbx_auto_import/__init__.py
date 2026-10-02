"""Explicit UE animation import. Dry-run never creates import options/tasks/assets."""
from pathlib import Path
from .config import load_config, file_hash

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'import'], 'default': 'inspect'},
    'config_paths': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000},
    'config_directory': {'type': 'string', 'description': 'Explicit directory of JSON configurations'},
    'save_assets': {'type': 'boolean', 'default': True},
    'confirm_import': {'type': 'boolean', 'default': False}}, 'description': 'Legacy FBX animation import into wholly fresh /Game destination folders'}

def _unreal():
    import unreal
    return unreal

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in ('inspect', 'import'): raise ValueError('Invalid action')
    if not isinstance(kwargs.get('save_assets', True), bool) or not isinstance(kwargs.get('confirm_import', False), bool): raise ValueError('Boolean flags required')
    paths, directory = kwargs.get('config_paths'), kwargs.get('config_directory')
    if (paths is None) == (directory is None): raise ValueError('Provide config_paths OR config_directory explicitly')
    if directory is not None:
        root = Path(directory)
        if not root.is_dir(): raise ValueError('Config directory missing')
        paths = [str(p) for p in sorted(root.glob('*.json'))]
    if not isinstance(paths, list) or not 1 <= len(paths) <= 1000 or any(not isinstance(p, str) for p in paths): raise ValueError('1..1000 config paths required')
    plans = [dict(load_config(p), config_path=str(Path(p).resolve()), config_sha256=file_hash(p)) for p in paths]
    u = _unreal(); seen = []
    for plan in plans:
        config = plan['config']; dest = config['destination_content_path']; folded = dest.casefold()
        if any(folded == old or folded.startswith(old + '/') or old.startswith(folded + '/') for old in seen): raise ValueError('Overlapping config destinations')
        seen.append(folded)
        if u.EditorAssetLibrary.does_directory_exist(dest): raise ValueError('Destination must be a completely new folder: ' + dest)
        skeleton = u.load_asset(config['skeleton_path'])
        if not isinstance(skeleton, u.Skeleton): raise ValueError('Configured Skeleton asset is missing/wrong type: ' + config['skeleton_path'])
    return {'action': action, 'configs': plans, 'save_assets': kwargs.get('save_assets', True),
        'confirm_import': kwargs.get('confirm_import', False), 'asset_impact': 'New AnimationSequences and native importer metadata; shared Skeleton may gain curve metadata; import/save is not promised undoable',
        'file_impact': 'Source FBX/JSON unchanged; save_assets=True writes new UE packages; failures can leave partial assets'}

def get_import_options(skeleton_path):
    u = _unreal(); skeleton = u.load_asset(skeleton_path)
    if not isinstance(skeleton, u.Skeleton): raise ValueError('Invalid Skeleton')
    options = u.FbxImportUI(); options.reset_to_default()
    for key, value in {'automated_import_should_detect_type': False, 'mesh_type_to_import': u.FBXImportType.FBXIT_ANIMATION,
        'skeleton': skeleton, 'import_as_skeletal': True, 'import_animations': True, 'import_mesh': False, 'import_materials': False, 'import_textures': False}.items():
        options.set_editor_property(key, value)
    options.anim_sequence_import_data.set_editor_property('animation_length', u.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    # Original writes skeletal settings onto static_mesh_import_data; these are not applicable to animation-only import.
    return options

def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect': return plan
    if not plan['confirm_import']: raise ValueError('confirm_import=True required for native import/save')
    u = _unreal()
    # Pre-create all transient import options before any native importer runs.
    options = [get_import_options(p['config']['skeleton_path']) for p in plan['configs']]
    tasks = []
    for config, opts in zip(plan['configs'], options):
        if file_hash(config['config_path']) != config['config_sha256']: raise ValueError('Config changed after preflight')
        for source in config['sources']:
            if file_hash(source['path']) != source['sha256']: raise ValueError('FBX changed after preflight')
            task = u.AssetImportTask()
            # Private per-file child avoids multi-take FBX name collisions between files.
            for key, value in {'filename': source['path'], 'destination_path': config['config']['destination_content_path'] + '/' + source['name'],
                'destination_name': source['name'], 'replace_existing': False, 'replace_existing_settings': False, 'save': plan['save_assets'],
                'automated': True, 'options': opts, 'factory': u.FbxFactory()}.items(): task.set_editor_property(key, value)
            tasks.append((task, source))
    result = dict(plan, imports=[], success=True)
    for config in plan['configs']:
        if u.EditorAssetLibrary.does_directory_exist(config['config']['destination_content_path']): raise ValueError('Destination appeared after preflight')
    tools = u.AssetToolsHelpers.get_asset_tools()
    for task, source in tasks:
        try:
            if file_hash(source['path']) != source['sha256']: raise ValueError('FBX changed immediately before import')
            tools.import_asset_tasks([task])
            paths = [str(p) for p in task.imported_object_paths]
            row = {'source': source['path'], 'imported_object_paths': paths, 'success': bool(paths)}
            if not paths: row['error'] = 'Native importer returned no assets'
        except Exception as error:
            row = {'source': source['path'], 'imported_object_paths': [], 'success': False, 'error': str(error)}
        result['imports'].append(row)
        if not row['success']:
            result['success'] = False
            break
    return result

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        success = data.get('success', True)
        return {'success': success, 'tool_id': 'ue_fbx_auto_import', 'dry_run': dry_run, 'data': data,
                'errors': [] if success else ['Native import failed; inspect per-file results and partial new assets']}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_fbx_auto_import', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui():
    raise RuntimeError('UE importer uses explicit configuration API; Maya config generator supplies the full dialog')
