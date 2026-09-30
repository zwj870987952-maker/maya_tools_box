import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/lock_to_world'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/lock_to_world'
SHARED = ROOT / 'tools_staging_pool/01_animation/jop_retarget_anim_v09/release_candidate/maya_toolkit/tools/jop_retarget_anim'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for source in sorted(UNIT.glob('*.py')):
        target = PACKAGE / 'upstream' / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, text in ((UNIT / '.gitattributes', '*.py -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(text, encoding='utf-8', newline='\n')
    original = (UNIT / 'jop_lockToWorld.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    functions, methods, body = [], [], []
    for n in tree.body:
        if isinstance(n, ast.Import) and any(a.name == 'maya.cmds' for a in n.names):
            continue
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            continue
        if isinstance(n, ast.FunctionDef):
            functions.append(n.name)
            if n.name == 'getWorldMatrixStartPosition':
                n.body = ast.parse('return _r.world_matrix(myCtl, time)').body
            elif n.name == 'checkEmptySelection':
                n.body = ast.parse('if not myCtrlList:\n    raise ValueError("需要控制器")').body
            elif n.name == 'lockToWorld':
                n.decorator_list.append(ast.parse('_r.lock_bridge', mode='eval').body)
            elif n.name in ('createMultDecompeCombo', 'createQuatToEuler', 'createPlusMinusAverage', 'setKeysToCtrl', 'snapCtlFromMatrixList'):
                n.body.insert(0, ast.parse('_r.require_active()').body[0])
                if n.name == 'snapCtlFromMatrixList':
                    for nested in ast.walk(n):
                        if isinstance(nested, ast.Try):
                            nested.handlers = [ast.ExceptHandler(type=None, name=None, body=[ast.Raise()])]
        if isinstance(n, ast.ClassDef):
            methods = [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
        for item in ast.walk(n):
            if isinstance(item, ast.Constant) and item.value == 'lockToWorld':
                item.value = 'mtbLockToWorld'
        body.append(n)
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=ast.parse('from .proxy import mc\nfrom . import runtime as _r').body + body, type_ignores=[])))
    text = '\n'.join(s.rstrip() for s in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    # Vendored shared private matrix helpers are copied into the final payload;
    # future candidate has no dependency on another staging directory.
    helper_tree = ast.parse((SHARED / 'runtime.py').read_text(encoding='utf-8'))
    helper_nodes = [n for n in helper_tree.body if isinstance(n, ast.FunctionDef) and n.name in ('cmds_module', 'identity', 'world_matrix', 'ensure_nodes')]
    (PACKAGE / 'matrix_support.py').write_text(ast.unparse(ast.fix_missing_locations(ast.Module(body=helper_nodes, type_ignores=[]))) + '\n', encoding='utf-8', newline='\n')
    proxy = (SHARED / 'proxy.py').read_text(encoding='utf-8')
    proxy = proxy.replace("if name == 'checkBox' and query:\n                    return r._ARGS['bake']", "if name == 'channelBox' and query:\n                    return list(r._ARGS['attributes'])")
    (PACKAGE / 'proxy.py').write_text(proxy, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'lock_to_world_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/jop_lockToWorld.py', tofile='native.py')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': resources, 'functions': functions, 'ui_methods': methods, 'license': 'Jesse ONG PHO copyright; no separate license supplied. Private local candidate.', 'private_reuse': 'Vendored equivalent matrix/pivot/quat plugin and ownership helpers from reviewed JOP candidate, self-contained.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (SHARED.parents[2] / 'launch_candidate.py').read_text(encoding='utf-8').replace('jop_retarget_anim', 'lock_to_world').replace('JopRetargetTool', 'LockToWorldTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'lock_to_world', 'registration': {'module': 'lock_to_world', 'class_name': 'LockToWorldTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya cmds/OpenMaya API2, matrix/quat nodes loaded only if required', 'BaseMayaTool/Undo'], 'source': '../jop_lockToWorld.py', 'change_summary': 'Full native start-matrix/per-frame parent compensation, frozen pivot, channel mask/UI with readonly preflight/Undo and owned helpers; vendored support has no staging dependencies.', 'verification_limitations': ['Real GUI/production parent scale/pivots and foot contact acceptance pending', 'Partial local channels cannot promise complete world-space lock', 'Degree/cm, static pivots, zero target rotateAxis/pivotTranslate and identity offsetParentMatrix required', 'Integer frame ranges only; plugin state is not scene Undo'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': len(functions), 'methods': len(methods), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
