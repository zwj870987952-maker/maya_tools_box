"""UE mesh bone export. Imports are inert; no Maya dependency or asset mutation."""
from pathlib import Path
import hashlib
import re

TOOL_ID = 'ue_bone_exporter'
parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'export'], 'default': 'inspect'},
    'output_dir': {'type': 'string', 'description': 'Existing directory; empty uses UE project root'},
    'asset_paths': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 1000,
                    'description': 'UE object paths; omitted uses selected Content Browser assets'}}}


def _unreal():
    import unreal
    return unreal


def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']):
        raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in ('inspect', 'export'):
        raise ValueError('Invalid action')
    u = _unreal()
    paths = kwargs.get('asset_paths')
    if paths is not None:
        if not isinstance(paths, list) or not 1 <= len(paths) <= 1000 or any(not isinstance(p, str) or not p.startswith('/') for p in paths):
            raise ValueError('asset_paths requires 1..1000 absolute UE object paths')
        assets = [u.load_asset(p) for p in paths]
        if any(a is None for a in assets):
            raise ValueError('An explicit asset path could not be loaded')
    else:
        assets = list(u.EditorUtilityLibrary.get_selected_assets())
    if not assets or len(assets) > 1000:
        raise ValueError('Select 1..1000 assets')
    raw_dir = kwargs.get('output_dir', '')
    if not isinstance(raw_dir, str):
        raise ValueError('output_dir must be a string')
    directory = Path(raw_dir or u.Paths.project_dir()).resolve()
    if not directory.is_dir():
        raise ValueError('Output directory must already exist: ' + str(directory))
    if not hasattr(u, 'SkeletonModifier'):
        raise RuntimeError('Enable UE Skeleton Editing tools: SkeletonModifier unavailable; C++ mesh menu is an independent alternative')
    rows, skipped, seen, targets = [], [], set(), set()
    for asset in assets:
        if not isinstance(asset, u.SkeletalMesh):
            skipped.append(asset.get_path_name())
            continue
        path = asset.get_path_name()
        if path in seen:
            continue
        seen.add(path)
        name = asset.get_name()
        if not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]+', name) or name.endswith(('.', ' ')):
            raise ValueError('Unsafe mesh name: ' + name)
        modifier = u.SkeletonModifier()
        if not modifier.set_skeletal_mesh(asset):
            raise ValueError('Cannot read mesh skeleton: ' + path)
        # Never call commit_skeleton_to_skeletal_mesh or any editing methods.
        bones = [str(n) for n in modifier.get_all_bone_names()]
        if not bones or any(not n or '\n' in n or '\r' in n for n in bones):
            raise ValueError('Empty/invalid bone names: ' + path)
        target = directory / (name + '_BoneList.txt')
        key = str(target).casefold()
        if key in targets:
            raise ValueError('Selected meshes produce the same file name: ' + str(target))
        if target.exists():
            raise ValueError('Existing output is protected: ' + str(target))
        targets.add(key)
        rows.append({'asset': path, 'scope': 'mesh', 'bones': bones, 'count': len(bones), 'output': str(target)})
    if not rows:
        raise ValueError('No SkeletalMesh selected')
    return {'action': action, 'rows': rows, 'skipped': skipped, 'asset_mutations': [],
            'file_impact': 'New UTF-8 without BOM txt files; no asset save/commit; files are outside UE Undo'}


def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect':
        return plan
    created = []
    try:
        for row in plan['rows']:
            target = Path(row['output'])
            data = ('\n'.join(row['bones']) + '\n').encode('utf-8')
            with target.open('xb') as stream:
                # Register ownership immediately so a partial write can be removed.
                created.append(target)
                stream.write(data)
            row['sha256'] = hashlib.sha256(data).hexdigest()
    except Exception:
        for target in reversed(created):
            target.unlink(missing_ok=True)
        raise
    plan['written'] = [str(p) for p in created]
    return plan


def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool):
            raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        return {'success': True, 'tool_id': TOOL_ID, 'dry_run': dry_run, 'data': data, 'errors': []}
    except Exception as error:
        return {'success': False, 'tool_id': TOOL_ID, 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}


def show_ui():
    # Native plugin supplies actual SaveFileDialog/menu UI. Python preview is inert.
    u = _unreal()
    result = run(action='inspect')
    u.log(str(result))
    return result
