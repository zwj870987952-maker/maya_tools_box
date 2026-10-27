"""Offline, pinned, non-overwriting installer. Never imports vendor code."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
import zipfile

COMMIT = 'eb8ede026c61f3cf5e38bafbc709d3bbed4d90c1'
SHA256 = '290cc3ff67d81347037b3b6d011547b76bd2bdf158e5c27c93c3f74b2a2758d9'
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = PACKAGE / 'upstream' / ('tbAnimTools-' + COMMIT + '.zip')
PREFIX = 'tbAnimTools-' + COMMIT
RECEIPT = '.maya-toolkit-tb-install.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def members(archive):
    """Reject ZIP traversal, links, encrypted data and Windows name aliases."""
    rows = archive.infolist()
    if not rows or len(rows) > 10000 or sum(x.file_size for x in rows) > 120 * 1024 * 1024:
        raise ValueError('Archive size/member limit exceeded')
    result, seen = [], set()
    for item in rows:
        name = item.filename
        path = PurePosixPath(name)
        if '\\' in name or name.startswith('/') or any(x in ('', '.', '..') for x in name.rstrip('/').split('/')):
            raise ValueError('Unsafe ZIP path: ' + name)
        if not path.parts or path.parts[0] != PREFIX:
            raise ValueError('Unexpected archive root')
        for part in path.parts:
            if re.search(r'[<>:"|?*\x00-\x1f]', part) or part.endswith((' ', '.')) or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', part, re.I):
                raise ValueError('Unsafe Windows name: ' + name)
        mode = (item.external_attr >> 16) & 0xffff
        if stat.S_ISLNK(mode) or item.flag_bits & 1 or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
            raise ValueError('Links/encrypted/special entries are unsupported')
        if item.file_size > 32 * 1024 * 1024 or item.file_size / max(item.compress_size, 1) > 1000:
            raise ValueError('ZIP expansion limit exceeded')
        relative = PurePosixPath(*path.parts[1:]).as_posix()
        if relative == '.':
            if not item.is_dir():
                raise ValueError('Root must be a directory')
            continue
        key = relative.casefold()
        if key in seen:
            raise ValueError('Duplicate ZIP path')
        seen.add(key)
        result.append((item, relative))
    file_paths = {p.casefold() for i, p in result if not i.is_dir()}
    for _, path in result:
        if any(p.as_posix().casefold() in file_paths for p in PurePosixPath(path).parents if p.as_posix() != '.'):
            raise ValueError('File/directory collision')
    required = {'tbtoolsInstaller.py', 'module_startup.py', 'userSetup.py', 'LICENSE'}
    if not required.issubset({p for i, p in result if not i.is_dir()}):
        raise ValueError('Incomplete vendor snapshot')
    return result


def snapshot():
    data = ARCHIVE.read_bytes()
    if digest(data) != SHA256:
        raise ValueError('Pinned upstream SHA256 mismatch')
    with zipfile.ZipFile(ARCHIVE) as archive:
        rows = members(archive)
        files = [{'path': p, 'bytes': i.file_size, 'sha256': digest(archive.read(i))} for i, p in rows if not i.is_dir()]
    return {'commit': COMMIT, 'archive_sha256': SHA256, 'members': len(rows), 'files': files, 'total_bytes': sum(x['bytes'] for x in files)}


def explicit_path(value):
    if not isinstance(value, str) or not value.strip() or '\n' in value or '\r' in value or '"' in value:
        raise ValueError('Supply an explicit absolute filesystem path')
    path = Path(value)
    if not path.is_absolute():
        raise ValueError('Path must be absolute')
    if any(x in ('.', '..') for x in value.replace('\\', '/').split('/')):
        raise ValueError('Dot path segments are unsupported')
    # Junctions and symlinks also redirect Windows file writes.
    for node in [path] + list(path.parents):
        if node.exists() or node.is_symlink():
            attributes = getattr(node.lstat(), 'st_file_attributes', 0)
            if node.is_symlink() or attributes & 0x400:
                raise ValueError('Symlink/reparse point path is unsupported')
    return path.resolve()


def install_plan(destination):
    path = explicit_path(destination)
    if os.name != 'nt':
        raise ValueError('This candidate installer targets Windows Maya')
    if path.exists():
        raise ValueError('Destination must not exist; existing installs are never overwritten')
    if not path.parent.is_dir():
        raise ValueError('Choose an existing parent directory')
    data = snapshot()
    return dict(data, destination=str(path), file_effect='Creates a new complete suite folder; Maya Undo cannot remove files', gui_acceptance='not_run')


def install(destination):
    plan = install_plan(destination)
    path = Path(plan['destination'])
    stage = Path(tempfile.mkdtemp(prefix='.tb-staging-', dir=str(path.parent)))
    try:
        with zipfile.ZipFile(ARCHIVE) as archive:
            for item, relative in members(archive):
                target = stage / relative
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as stream:
                        stream.write(archive.read(item))
        (stage / RECEIPT).write_text(json.dumps({'commit': COMMIT, 'archive_sha256': SHA256, 'files': plan['files']}, indent=2) + '\n', encoding='utf-8')
        # Check again immediately before publishing; on Windows os.rename also
        # refuses a concurrently-created destination, including an empty one.
        install_plan(str(path))
        os.rename(str(stage), str(path))
    finally:
        # Only this invocation's private temporary folder can be removed.
        if stage.exists() and stage.parent.resolve() == path.parent.resolve() and stage.name.startswith('.tb-staging-'):
            shutil.rmtree(stage)
    return plan


def installed(destination):
    path = explicit_path(destination)
    data = snapshot()
    receipt = json.loads((path / RECEIPT).read_text(encoding='utf-8'))
    if receipt.get('commit') != COMMIT or receipt.get('archive_sha256') != SHA256:
        raise ValueError('Not an installation created from this pinned candidate')
    for item in data['files']:
        target = explicit_path(str(path / item['path']))
        if not target.is_file() or digest(target.read_bytes()) != item['sha256']:
            raise ValueError('Installed vendor resource changed/missing: ' + item['path'])
    return dict(data, destination=str(path), receipt=str(path / RECEIPT))


def module_text(destination, version):
    if not re.fullmatch(r'[0-9]{4}(?:\.[0-9]+)?', version):
        raise ValueError('Unsupported Maya version label')
    return ('+ tbAnimTools 1.0 ' + destination + '\nPYTHONPATH+:=\nPYTHONPATH+:=apps\nMAYA_SCRIPT_PATH+:=scripts\n'
            'MAYA_PLUG_IN_PATH+:=plugins/common\nXBMLANGPATH+:=Icons\n\n'
            '+ PLATFORM:win64 MAYAVERSION:' + version + ' tbAnimTools 1.0 ' + destination + '\n'
            'MAYA_PLUG_IN_PATH+:=plugins/' + version + '\n')
