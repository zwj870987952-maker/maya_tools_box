"""Read all source variants and the original Word instructions without executing them."""
import ast
import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'tools_staging_pool/01_animation/shape_animation_tool/sat【修型插件】'


def main():
    rows = []
    for p in sorted(RAW.rglob('*')):
        if not p.is_file():
            continue
        row = {'path': p.relative_to(RAW).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
        if p.name == 'main.py':
            src = p.read_text(encoding='utf-8-sig')
            try:
                tree = ast.parse(src)
            except SyntaxError:
                from lib2to3.refactor import RefactoringTool, get_fixers_from_package
                src = str(RefactoringTool(get_fixers_from_package('lib2to3.fixes')).refactor_string(src, str(p)))
                tree = ast.parse(src)
            row['classes'] = {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)] for n in tree.body if isinstance(n, ast.ClassDef)}
            row['methods'] = {f'{n.name}.{m.name}': hashlib.sha256(ast.dump(m, include_attributes=False).encode()).hexdigest() for n in tree.body if isinstance(n, ast.ClassDef) for m in n.body if isinstance(m, ast.FunctionDef)}
        rows.append(row)
    doc = next(RAW.rglob('*.docx'))
    with zipfile.ZipFile(doc) as z:
        tree = ET.fromstring(z.read('word/document.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = [''.join(p.itertext()) for p in tree.findall('.//w:p', ns)]
        media = [n for n in z.namelist() if n.startswith('word/media/')]
    report = {'files': rows, 'word_paragraphs': paragraphs, 'word_media': media}
    (ROOT / 'plans/staging_run/shape_animation_source_review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(rows), 'variants': [r['path'] for r in rows if 'methods' in r], 'word_paragraphs': paragraphs, 'word_media': media}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
