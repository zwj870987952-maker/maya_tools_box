import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/jop_retarget_anim_v09'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/jop_retarget_anim'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for source in sorted((UNIT / 'jop_retargetAnim').rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        target = PACKAGE / 'upstream' / source.relative_to(UNIT / 'jop_retargetAnim')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, text in ((UNIT / '.gitattributes', 'jop_retargetAnim/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(text, encoding='utf-8', newline='\n')
    original = (UNIT / 'jop_retargetAnim/jop_retargetAnim.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    functions, methods, output = [], [], []
    for node in tree.body:
        if isinstance(node, ast.Import) and any(a.name == 'maya.cmds' for a in node.names):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            continue  # Original import-time plugin loading.
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
            if node.name == 'checkEmptySelection':
                node.body = ast.parse("if not myCtrlList:\n    raise ValueError('需要选择控制器')\nreturn myCtrlList").body
            elif node.name == 'getWorldMatrix':
                node.body = ast.parse('return _r.world_matrix(myCtl, time)').body
            elif node.name in ('saveAnimToList', 'snapCtlFromMatrixDic'):
                node.decorator_list.append(ast.parse('_r.capture_bridge' if node.name == 'saveAnimToList' else '_r.restore_bridge', mode='eval').body)
            elif node.name in ('createMultDecompeCombo', 'createQuatToEuler', 'createPlusMinusAverage', 'setKeysToCtrl'):
                node.body.insert(0, ast.parse('_r.require_active()').body[0])
        if isinstance(node, ast.ClassDef):
            methods.extend(m.name for m in node.body if isinstance(m, ast.FunctionDef))
        for item in ast.walk(node):
            if isinstance(item, ast.Constant) and item.value == 'retargetAnimation':
                item.value = 'mtbJopRetargetAnimation'
        output.append(node)
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=ast.parse('from .proxy import mc\nfrom . import runtime as _r').body + output, type_ignores=[])))
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'jop_retarget_anim_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/source.py', tofile='native.py')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': resources, 'functions': functions, 'ui_methods': methods, 'license': 'Jesse ONG PHO commercial use license: personal/commercial use and modification allowed, sharing/distribution prohibited. Supplied private local candidate.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'jop_retarget_anim', 'registration': {'module': 'jop_retarget_anim', 'class_name': 'JopRetargetTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya cmds/OpenMaya API2; matrix/quat nodes lazily enabled if missing', 'Existing BaseMayaTool/Undo'], 'source': '../jop_retargetAnim/jop_retargetAnim.py', 'change_summary': 'Complete native matrix retarget/UI, frozen-pivot matrix capture via equivalent read-only API, structured UUID/context snapshot and guarded scene/key/plugin lifetime.', 'verification_limitations': ['Real GUI/production parent-scale/pivots/rotateOrder behavior pending', 'Current degree/cm units; animated pivots/joints/externally-driven target channels unsupported', 'License forbids third-party sharing; local only', 'Plugin enable/disable is Maya global state and not ordinary scene Undo'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': len(functions), 'methods': len(methods), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
