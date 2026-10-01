"""Read-only inventory of the full skeleton plus mesh merge/split source."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools_staging_pool/01_animation/pose_matcher/PoseMatcher.py'
tree = ast.parse(SOURCE.read_bytes())
rows = [{'name': n.name, 'line': n.lineno, 'end_line': n.end_lineno,
         'calls': sorted({ast.unparse(x.func) for x in ast.walk(n) if isinstance(x, ast.Call)})}
        for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
data = {'source': SOURCE.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'source_bytes': SOURCE.stat().st_size, 'total_lines': len(SOURCE.read_text(encoding='utf-8-sig').splitlines()),
        'functions': rows, 'license': 'No independent license/author notice in source; local preparation only',
        'issues': ['Two complete workflows: skeleton alignment and NumPy merge/split with OBJ/JSON plus scene meshes',
                   'getNormals needed: vertex normals array paired with face-vertex normal IDs is inconsistent',
                   'Raw MFnMesh creation/setters are not standard cmds Undo; candidate needs an undoable creation command',
                   'Missing target checked after parent access; root/duplicate leaf/twist effective-parent guards',
                   'Merge/split/map writes overwrite directly; explicit output group and publication checks needed',
                   'ProcessUV uses V maximum for U offset and mutates the source array; cancellation leaves partial arrays',
                   'Split assumes normal indices equal vertex indices, fails hard-edge/seam data',
                   'Private UI names, stable list-row removal, callbacks with Maya positional args and refresh finally',
                   'All original algorithms and original 56-or-actual-count functions must remain traceable']}
(ROOT / 'plans/staging_run/pose_matcher_source_inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'functions': len(rows), 'source_bytes': data['source_bytes'], 'sha256': data['sha256']}))
