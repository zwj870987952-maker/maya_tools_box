"""Explicit source collection/copy with owned fresh session output and reports."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from .source_paths import read_source_paths

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'copy_sources'], 'default': 'inspect'},
    'output_dir': {'type': 'string', 'description': 'Existing parent directory; empty defaults Desktop'},
    'session_name': {'type': 'string', 'description': 'Optional new directory basename, default unique timestamp/UUID'},
    'source_mode': {'type': 'string', 'enum': ['first', 'all'], 'default': 'first'},
    'open_folders': {'type': 'boolean', 'default': False}}}

def _unreal():
    import unreal
    return unreal

def _safe_name(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 or ord(c) == 92 or c in '<>:"/|?*' for c in name) or name.endswith(('.', ' ')) or name in ('.', '..'):
        raise ValueError('Unsafe filesystem component: ' + str(name))
    if name.split('.')[0].casefold() in {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1,10)), *(f'lpt{i}' for i in range(1,10))}:
        raise ValueError('Reserved Windows name: ' + name)
    return name

def _hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    action, mode = kwargs.get('action', 'inspect'), kwargs.get('source_mode', 'first')
    if action not in ('inspect', 'copy_sources') or mode not in ('first', 'all'): raise ValueError('Invalid action/source_mode')
    if not isinstance(kwargs.get('open_folders', False), bool): raise ValueError('open_folders must be boolean')
    raw = kwargs.get('output_dir') or str(Path.home() / 'Desktop')
    if not isinstance(raw, str): raise ValueError('output_dir must be string')
    parent = Path(raw).resolve()
    if not parent.is_dir(): raise ValueError('Output parent must already exist')
    session = _safe_name(kwargs.get('session_name') or ('UE_Sources_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]))
    target = parent / session
    if target.exists(): raise ValueError('Session directory already exists; no overwrite: ' + str(target))
    assets = list(_unreal().EditorUtilityLibrary.get_selected_assets())
    if not assets or len(assets) > 10000: raise ValueError('Select 1..10000 UE assets')
    rows, seen, targets = [], set(), set()
    for asset in assets:
        record = read_source_paths(asset); asset_path = record['asset']
        if asset_path in seen: continue
        seen.add(asset_path)
        package = asset_path.split('.', 1)[0]
        parts = PurePosixPath(package).parts
        if len(parts) < 3 or parts[0] != '/': raise ValueError('Invalid UE package path: ' + package)
        folder = target.joinpath(*(_safe_name(part) for part in parts[1:-1]))
        folder.resolve().relative_to(target.resolve())
        name = _safe_name(record['name'])
        record.update(folder=str(folder), copies=[], missing=[], failed=[])
        paths = record['paths'][:1] if mode == 'first' else record['paths']
        if not paths: record['missing'].append({'source': None, 'reason': record['status']})
        for index, raw_source in enumerate(paths):
            source = Path(raw_source)
            if record['status'] == 'raw_relative' or not source.is_absolute():
                record['missing'].append({'source': raw_source, 'reason': 'Unresolved relative import source; not joined against current working directory'}); continue
            if not source.is_file():
                record['missing'].append({'source': raw_source, 'reason': 'Source file missing'}); continue
            source = source.resolve()
            extension = source.suffix
            filename = _safe_name(name + (('_src' + str(index+1)) if index else '') + extension)
            destination = folder / filename; key = str(destination).casefold()
            if key in targets: raise ValueError('Selected assets collide at: ' + str(destination))
            targets.add(key)
            record['copies'].append({'asset_name': name, 'asset_path': asset_path, 'source_path': str(source),
                'target_path': str(destination), 'target_filename': filename, 'renamed': filename != source.name,
                'sha256': _hash(source), 'size': source.stat().st_size})
        rows.append(record)
    return {'action': action, 'source_mode': mode, 'session': str(target), 'rows': rows,
            'open_folders': kwargs.get('open_folders', False), 'asset_mutations': [],
            'file_impact': 'Copies source files into a new session tree; TXT/JSON reports. Sources and import metadata unchanged; filesystem output is outside UE Undo'}

def _write(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f: f.write(text)

def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect': return plan
    session = Path(plan['session'])
    session.mkdir()  # Exclusive ownership; no merge with existing output.
    groups, copied, warnings = {}, [], []
    for row in plan['rows']:
        folder = Path(row['folder'])
        report = groups.setdefault(str(folder), {'success': [], 'missing_source': [], 'failed': []})
        report['missing_source'].extend({'asset_name': row['name'], 'asset_path': row['asset'], **m} for m in row['missing'])
        try: folder.mkdir(parents=True, exist_ok=True)
        except Exception as error:
            report['failed'].append({'asset_name': row['name'], 'asset_path': row['asset'], 'error': 'Output folder creation failed: ' + str(error)})
            continue
        for item in row['copies']:
            path = Path(item['source_path']); dest = Path(item['target_path']); owned = False
            try:
                if path.stat().st_size != item['size'] or _hash(path) != item['sha256']: raise ValueError('Source changed after preflight')
                with path.open('rb') as f, dest.open('xb') as out:
                    owned = True; shutil.copyfileobj(f, out, 1024 * 1024)
                if _hash(dest) != item['sha256']: raise ValueError('Copied content differs from preflight SHA')
                shutil.copystat(path, dest)
                report['success'].append(item); copied.append(str(dest))
            except Exception as error:
                if owned: dest.unlink(missing_ok=True)
                report['failed'].append({**item, 'error': str(error)})
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    logs = []
    for raw_folder, report in sorted(groups.items()):
        folder = Path(raw_folder)
        try:
            for key, label in [('success', '成功复制'), ('missing_source', '源文件缺失'), ('failed', '处理失败')]:
                if report[key]:
                    path = folder / (folder.name + '_' + label + '_' + stamp + '.txt')
                    _write(path, '===== UE资产' + label + '日志 =====\n' + json.dumps(report[key], ensure_ascii=False, indent=2) + '\n')
                    logs.append(str(path))
            if report['success']:
                path = folder / (folder.name + '_名单_' + stamp + '.txt')
                _write(path, '===== 成功复制文件名单 =====\n' + '\n'.join(item['target_path'] for item in report['success']) + '\n'); logs.append(str(path))
        except Exception as error: warnings.append('Report write failed ' + str(folder) + ': ' + str(error))
    summary = {'session': str(session), 'total_assets': len(plan['rows']), 'total_folders': len(groups),
        'total_success': sum(len(g['success']) for g in groups.values()),
        'total_missing': sum(len(g['missing_source']) for g in groups.values()),
        'total_failed': sum(len(g['failed']) for g in groups.values()), 'folder_logs': groups, 'copied': copied, 'logs': logs, 'warnings': warnings}
    try: _write(session / 'summary.json', json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    except Exception as error: summary['warnings'].append('summary.json failed: ' + str(error))
    if plan['open_folders']:
        if os.name != 'nt': summary['warnings'].append('Explorer opening supported on Windows only')
        else:
            for folder in sorted(groups):
                try: subprocess.Popen(['explorer.exe', folder], shell=False)
                except Exception as error: summary['warnings'].append('Explorer failed: ' + str(error))
    _unreal().log('UE source copy summary: ' + str({k:v for k,v in summary.items() if k.startswith('total_')}))
    return summary

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        success = not data.get('total_failed', 0) and not data.get('warnings')
        return {'success': success, 'tool_id': 'ue_source_finder', 'dry_run': dry_run, 'data': data,
                'errors': [] if success else ['Partial copy/report failure; see session summary and retained output']}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_source_finder', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui():
    result = run()
    _unreal().log(str(result))
    return result
