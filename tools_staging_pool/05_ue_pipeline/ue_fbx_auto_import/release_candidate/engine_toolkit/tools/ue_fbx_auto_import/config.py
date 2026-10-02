"""Pure configuration: exact legacy JSON shape, no Maya/UE imports."""
from pathlib import Path
import hashlib
import json
import os
import re

KEYS = {'fbx_files', 'destination_content_path', 'skeleton_path'}

def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def package_path(value):
    if not isinstance(value, str) or not re.fullmatch(r'/Game(?:/[A-Za-z0-9_]+)+', value):
        raise ValueError('Expected /Game/... package path (no file extension/object suffix): ' + str(value))
    return value

def check_config(data):
    if not isinstance(data, dict) or set(data) != KEYS: raise ValueError('Config must contain exactly the three legacy keys')
    package_path(data['destination_content_path']); package_path(data['skeleton_path'])
    paths = data['fbx_files']
    if not isinstance(paths, list) or not 1 <= len(paths) <= 1000: raise ValueError('fbx_files needs 1..1000 paths')
    seen, sources = set(), []
    for raw in paths:
        if not isinstance(raw, str): raise ValueError('FBX path must be string')
        path = Path(raw)
        if not path.is_absolute() or path.suffix.lower() != '.fbx' or not path.is_file(): raise ValueError('Existing absolute .fbx required: ' + str(raw))
        path = path.resolve(); key = str(path).casefold()
        if key in seen: raise ValueError('Duplicate source FBX: ' + str(path))
        if not re.fullmatch(r'[A-Za-z0-9_]+', path.stem): raise ValueError('Use UE-safe ASCII FBX basename: ' + path.name)
        seen.add(key); sources.append({'path': str(path), 'sha256': file_hash(path), 'name': path.stem})
    names = [s['name'].casefold() for s in sources]
    if len(set(names)) != len(names): raise ValueError('Duplicate FBX basenames in configuration')
    return {'config': dict(data, fbx_files=[s['path'] for s in sources]), 'sources': sources}

def load_config(path):
    path = Path(path)
    if path.stat().st_size > 4 * 1024 * 1024: raise ValueError('Config exceeds 4 MB')
    return check_config(json.loads(path.read_text(encoding='utf-8-sig')))

def content_root(path):
    root = Path(path).resolve()
    if not root.is_dir(): raise ValueError('Content/project directory missing')
    if root.name.casefold() == 'content': return root
    content = root / 'Content'
    if not content.is_dir(): raise ValueError('Select project root containing Content, or Content itself')
    return content.resolve()

def convert_to_ue_path(path, content=None):
    p = Path(path).resolve()
    if content is None:
        roots = [q for q in (p, *p.parents) if q.name.casefold() == 'content']
        if not roots: raise ValueError('Path is outside Content')
        content = roots[0]
    rel = p.relative_to(Path(content).resolve())
    if p.suffix.casefold() == '.uasset': rel = rel.with_suffix('')
    return package_path('/Game/' + rel.as_posix())

def find_target_paths(base):
    content = content_root(base); anim, skeleton = [], []
    count = 0
    for directory, dirs, files in os.walk(content, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
        count += len(dirs) + len(files)
        if count > 200000: raise ValueError('Content scan exceeds 200000 entries')
        for name in dirs:
            if name.casefold() == 'anim': anim.append(str(Path(directory) / name))
        for name in sorted(files):
            if 'skeleton' in name.casefold() and Path(name).suffix.casefold() == '.uasset': skeleton.append(str(Path(directory) / name))
    return anim, skeleton

def generate_config(data, output_dir):
    plan = check_config(data); directory = Path(output_dir).resolve()
    # This explicit file-writing operation alone creates the requested directory.
    directory.mkdir(parents=True, exist_ok=True)
    name = plan['config']['skeleton_path'].rsplit('/', 1)[1] + '_config'
    for index in range(100000):
        target = directory / (name + (('_' + str(index)) if index else '') + '.json')
        try:
            with target.open('x', encoding='utf-8', newline='\n') as stream:
                try: json.dump(plan['config'], stream, ensure_ascii=False, indent=4); stream.write('\n')
                except Exception: stream.close(); target.unlink(); raise
            return {'output': str(target), **plan}
        except FileExistsError: continue
    raise ValueError('Could not allocate unique configuration filename')
