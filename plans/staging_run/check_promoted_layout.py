"""Verify candidate imports and registry in a temporary future layout only."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--test', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    candidate = Path(args.candidate).resolve()
    description = json.loads((candidate / 'promotion.json').read_text(encoding='utf-8'))
    spec = importlib.util.spec_from_file_location('layout_promotion', ROOT / 'plans/staging_run/promote_candidate.py')
    promotion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(promotion)
    original_registry = (ROOT / 'maya_toolkit/tools/__init__.py').read_bytes()
    with tempfile.TemporaryDirectory(prefix='staging_promoted_layout_') as folder:
        temporary = Path(folder)
        shutil.copytree(ROOT / 'maya_toolkit', temporary / 'maya_toolkit', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if (ROOT / 'compat').is_dir():
            shutil.copytree(ROOT / 'compat', temporary / 'compat', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        promotion.ROOT = temporary
        for source, target in promotion.payload(candidate, description):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        registry, unused_original, merged = promotion.registry_change(description)
        registry.write_bytes(merged)
        env = dict(os.environ, PYTHONPATH=str(temporary), PYTHONDONTWRITEBYTECODE='1')
        test = subprocess.run([sys.executable, str(temporary / args.test)], cwd=folder, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
        probe = "from maya_toolkit.framework import ToolRegistry; t=ToolRegistry.get(%r); assert t is not None; assert t.category == 'animation'; assert callable(t.show_ui); assert t.to_mcp_tool()['name']==%r; print('Registered tool and panel entry verified')" % (description['tool_id'], description['tool_id'])
        registered = subprocess.run([sys.executable, '-c', probe], cwd=folder, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
    changed = (ROOT / 'maya_toolkit/tools/__init__.py').read_bytes() != original_registry
    report = {'kind': 'promoted_layout_offline', 'passed': test.returncode == 0 and registered.returncode == 0 and not changed,
              'returncode': test.returncode, 'output': test.stdout.decode('utf-8', errors='replace'),
              'registry_returncode': registered.returncode, 'registry_output': registered.stdout.decode('utf-8', errors='replace'),
              'production_changed': changed}
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
