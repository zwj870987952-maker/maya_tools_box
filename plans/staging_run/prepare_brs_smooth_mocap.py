import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/brs_smooth_mocap'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/brs_smooth_mocap'
DEPENDENCY = ROOT / 'tools_staging_pool/01_animation/brs_loc_transfer/release_candidate/maya_toolkit/tools/brs_loc_transfer'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    entry = UNIT / 'BRSSmoothMocap.py'
    original = entry.read_text(encoding='utf-8-sig')
    (PACKAGE / 'upstream').mkdir(exist_ok=True)
    shutil.copyfile(entry, PACKAGE / 'upstream/BRSSmoothMocap.py')
    for target, data in [(UNIT / '.gitattributes', '/BRSSmoothMocap.py -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')]:
        target.write_text(data, encoding='utf-8', newline='\n')
    resources = [{'path': 'upstream/BRSSmoothMocap.py', 'sha256': hashlib.sha256(entry.read_bytes()).hexdigest()}]
    backend = PACKAGE / 'backend'
    for path in DEPENDENCY.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        target = backend / path.relative_to(DEPENDENCY)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.py' and 'upstream' not in path.parts:
            text = path.read_text(encoding='utf-8').replace('maya_toolkit.brs_loc_transfer.v1', 'maya_toolkit.brs_smooth_mocap.v1').replace('mtbBRSAnimLoc_Grp', 'mtbBRSSmoothAnimLoc_Grp').replace('mtbBRSRedirectGuide', 'mtbBRSSmoothRedirectGuide').replace('_mtbBRSSnapLoc', '_mtbBRSSmoothSnapLoc').replace('_mtbBRSannotate', '_mtbBRSSmoothAnnotate').replace('mtbBRSLOCTRANSFER', 'mtbBRSSMOOTH_BACKEND')
            target.write_text(text, encoding='utf-8', newline='\n')
        else:
            shutil.copyfile(path, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    # Exact original three-neighbor snapshot/commit algorithm, guarded but unaltered.
    tree = ast.parse(original)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    function = functions['valueAverage']
    function.body.insert(0, ast.parse('require_active()').body[0])
    module = ast.Module(body=ast.parse('from maya import cmds\nfrom .runtime import require_active').body + [function], type_ignores=[])
    ast.fix_missing_locations(module)
    adapted = ast.unparse(module) + '\n'
    (PACKAGE / 'algorithms.py').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'brs_smooth_mocap_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/BRSSmoothMocap.py', tofile='algorithms.py; orchestrator in runtime.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'brs_smooth_mocap', 'original_functions': list(functions), 'raw_files': resources, 'private_backend_origin': 'brs_loc_transfer candidate snapshot in this package; independent Owner/helper names; no staging path dependency at runtime', 'source_license': 'Original author family BRS; no independent redistribution license supplied; private preparation', 'changes': ['Remove scripts-directory exec/import-time dialog/scene operations', 'Exact valueAverage AST retained with guard', 'Explicit joint-only hierarchy and eligible locators; leaf/one-key cases guarded', 'Original smoothStrength-1 passes and six-channel bake', 'Owned constraints detached/cleaned after bake', 'Private full fixed locator dependency and explicit UI options']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'brs_smooth_mocap', 'registration': {'module': 'brs_smooth_mocap', 'class_name': 'SmoothMocapTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya Python3/cmds animation APIs', 'Bundled private BRS locator backend', 'Actual GUI for explicit options/confirm and Graph Editor selected keys', 'Existing framework/core Undo'], 'source': '../BRSSmoothMocap.py', 'change_summary': 'Original three-neighbor averaging/strength-minus-one passes and locator-driven mocap bake; full private backend bundled, explicit root/curve API, read-only plans and owned cleanup.', 'verification_limitations': ['Actual GUI/Graph Editor/mocap assets pending', 'Key timing/rounding/filterCurve/bake follow old BRS semantics', 'Selected-key smoothing preserves selected endpoints, not weighted time intervals', 'Private dependency copy is fixed, not automatically synced'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': list(functions), 'bundled_files': len(resources)}))


if __name__ == '__main__':
    main()
