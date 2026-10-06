"""Verify the local Animo candidate without importing vendor code or Maya.

Export its actual framework schemas and record offline evidence. Never overwrite
the user's acceptance record, install a runtime, or promote an official tool.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / 'tools_staging_pool/07_subsystems_suites/animo'
CANDIDATE = ROOT / 'release_candidate'
PACKAGE = CANDIDATE / 'maya_toolkit/tools/animo'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def main():
    manifest = read(CANDIDATE / 'manifest.json')
    assert digest(ROOT / 'archives/Animo_v10.6.0.zip') == manifest['zip_sha256']
    hashes = read(PACKAGE / 'runtime_files.json')
    patches = read(CANDIDATE / 'patches.json')
    changed = []
    parsed = 0
    for relative, expected in hashes.items():
        native = PACKAGE / 'native' / relative
        original = ROOT / 'upstream/Animo_v10.6.0' / relative
        assert digest(native) == expected, relative
        if digest(native) != digest(original):
            changed.append(relative)
        if native.suffix == '.py':
            ast.parse(native.read_text(encoding='utf-8-sig'), filename=relative)
            parsed += 1
    assert set(changed) == {patch['path'] for patch in patches}
    for path in CANDIDATE.rglob('*.py'):
        if 'native' not in path.parts:
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    loader = runpy.run_path(str(CANDIDATE / 'launch_candidate.py'), run_name='animo_verify_loader')
    tool = loader['load_tool']()
    rows = read(PACKAGE / 'operations.json')['operations']
    assert len(rows) == len({row['id'] for row in rows}) == 553
    assert len({row['category'] for row in rows}) == 55
    assert tool.parameters_schema['properties']['operation_id']['enum'] == [row['id'] for row in rows]
    from maya_toolkit.framework import ToolRegistry
    assert ToolRegistry.get('animo') is None
    write(CANDIDATE / 'schemas/openai_tool.json', tool.to_openai_tool())
    write(CANDIDATE / 'schemas/mcp_tool.json', tool.to_mcp_tool())
    suite = unittest.defaultTestLoader.discover(str(CANDIDATE / 'tests'), pattern='test_animo.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    verification = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'python_version': sys.version.split()[0], 'kind': 'offline_only',
        'archive_sha256_matches': True, 'native_assets_hash_checked': len(hashes),
        'native_python_ast_parsed': parsed, 'changed_native_files': changed,
        'operations': len(rows), 'categories': 55, 'official_registration': False,
        'test_count': result.testsRun, 'test_success': result.wasSuccessful(),
        'failures': len(result.failures), 'errors': len(result.errors),
        'maya_verified': False, 'maya_acceptance': 'pending_user',
        'limits': '语法、资源和适配器边界检查；未导入供应方模块、启动 Maya、验证原算法或测量性能。',
    }
    write(CANDIDATE / 'verification.json', verification)
    acceptance_path = CANDIDATE / 'acceptance.json'
    if not acceptance_path.exists():
        write(acceptance_path, {
            'status': 'pending_user', 'maya_version': '', 'os': '', 'tester': '',
            'scene': '', 'tested_at': '', 'verified_versions': [],
            'scope': '逐项记录；未运行入口不能随着部分样例通过而标成已验证。',
            'operations': [{'operation_id': row['id'], 'name': row['name'],
                            'category': row['category'], 'status': 'not_run',
                            'scene_or_fixture': '', 'expected': '', 'observed': '',
                            'undo_result': '', 'script_editor_errors': '', 'evidence': ''}
                           for row in rows],
        })
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
