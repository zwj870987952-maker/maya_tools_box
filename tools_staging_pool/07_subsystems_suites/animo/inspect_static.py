"""Inspect downloaded source without importing or executing vendor code."""
import ast
import collections
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'upstream' / 'Animo_v10.6.0'
modules = []
errors = []
imports = collections.Counter()
for path in sorted(ROOT.rglob('*.py')):
    relative = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding='utf-8-sig', errors='replace')
    item = {'path': relative, 'lines': len(text.splitlines()), 'bytes': path.stat().st_size}
    try:
        tree = ast.parse(text, filename=relative)
        item['functions'] = [{'name': n.name, 'line': n.lineno} for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        item['classes'] = [{'name': n.name, 'line': n.lineno} for n in tree.body if isinstance(n, ast.ClassDef)]
        item['imports'] = sorted(set(
            alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names
        ) | set(n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module))
        for name in item['imports']:
            imports[name.split('.')[0]] += 1
    except SyntaxError as exc:
        errors.append({'path': relative, 'line': exc.lineno, 'message': exc.msg})
    modules.append(item)
library = [m for m in modules if '/tools_library/' in m['path']]
summary = {
    'python_files': len(modules), 'python_lines': sum(m['lines'] for m in modules),
    'library_entries': len(library), 'library_categories': len({m['path'].split('/tools_library/')[1].split('/')[0] for m in library}),
    'non_library_files': len(modules) - len(library), 'syntax_errors': errors,
    'largest_modules': sorted(modules, key=lambda x: x['lines'], reverse=True)[:18],
    'imports': imports.most_common(25),
    'zip_sha256': hashlib.sha256((BASE / 'archives' / 'Animo_v10.6.0.zip').read_bytes()).hexdigest(),
}
(BASE / 'source_inventory.json').write_text(json.dumps({'summary': summary, 'modules': modules}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k != 'largest_modules'}, ensure_ascii=False, indent=2))
print('LARGEST MODULES')
for m in summary['largest_modules']:
    print(m['lines'], m['path'])
print('MODULE DIRECTORIES')
for p in sorted((ROOT / 'Animo_Data').iterdir()):
    if p.is_dir():
        print(p.name, len(list(p.rglob('*.py'))))
