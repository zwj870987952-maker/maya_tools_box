"""Preserve sources and package native runtime candidates without a Maya adapter."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n', encoding='utf-8', newline='\n')


def prepare(tool, summary, dependencies, limitations, panel):
    unit = ROOT / 'tools_staging_pool' / tool
    rc = unit / 'release_candidate'
    pkg = rc / 'engine_toolkit/tools' / unit.name
    rows = []
    for src in sorted(unit.rglob('*')):
        rel = src.relative_to(unit)
        if not src.is_file() or 'release_candidate' in rel.parts or '__pycache__' in rel.parts or src.name == '.gitattributes':
            continue
        dst = pkg / 'upstream' / rel
        if src.suffix == '.py':
            dst = dst.with_suffix('.py.original')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        rows.append({'path': rel.as_posix(), 'archive': dst.relative_to(pkg).as_posix(), 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
    put(unit / '.gitattributes', '* -text')
    put(rc / '.gitattributes', '* -text')
    put(pkg / 'catalog.json', json.dumps({'files': rows, 'license': 'Original notices preserved; no redistribution permission inferred'}, ensure_ascii=False, indent=2))
    put(rc / 'launch_candidate.py', """import importlib
from pathlib import Path
import sys

def load_tool():
    root = str(Path(__file__).resolve().parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module('engine_toolkit.tools.TOOL')

def run(dry_run=True, **kwargs):
    return load_tool().run(dry_run=dry_run, **kwargs)

def show_ui():
    return load_tool().show_ui()
""".replace('TOOL', unit.name))
    payload = [p for folder in (rc / 'engine_toolkit', rc / 'docs', rc / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    put(rc / 'promotion.json', json.dumps({'tool_id': unit.name, 'runtime': 'unreal_editor', 'registration': None, 'entry_module': 'engine_toolkit.tools.' + unit.name, 'panel': panel, 'files': [{'source': p.relative_to(rc).as_posix(), 'target': p.relative_to(rc).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in rows], 'dependencies': dependencies, 'acceptance_required': True, 'change_summary': summary, 'verification_limitations': limitations}, ensure_ascii=False, indent=2))
    print(json.dumps({'tool': unit.name, 'original_files': len(rows), 'payload_files': len(payload), 'runtime': 'unreal_editor'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool', required=True)
    parser.add_argument('--summary', required=True)
    args = parser.parse_args()
    prepare(args.tool, args.summary, ['Unreal Editor + PythonScriptPlugin'], ['Real Unreal Editor acceptance not_run'], 'UE native entry')
