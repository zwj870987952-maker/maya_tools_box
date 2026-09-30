import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/ik_fk_switch'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/ik_fk_switch'
UI_WRITES = {'saveIkFkCtrlsWin', 'matchIkFkWin', 'switchIkFkWin', 'switchFkIkWin', 'keyAll', 'bakeIkFkWin'}
FUNCTION_WRITES = {'fkikMatch', 'ikfkMatch', 'keyframeAll', 'saveIKFkCtrls', 'matchTransform', 'snap', 'poleVectorPosition', 'unlockAttributes', 'orientJoints'}


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for name in ('mog_ikFkSwitchPro.py', 'mog_ikFkSwitch.py', 'how to install and use.txt'):
        path = PACKAGE / 'upstream' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(UNIT / name, path)
        resources.append({'path': 'upstream/' + name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    for path, value in ((UNIT / '.gitattributes', 'mog_ikFkSwitch*.py -text\nhow* -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(value, encoding='utf-8', newline='\n')
    original = (UNIT / 'mog_ikFkSwitchPro.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    methods, functions, output = [], [], []
    for node in tree.body:
        if isinstance(node, ast.Import) and any(a.name == 'pymel.core' for a in node.names):
            continue
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if not isinstance(method, ast.FunctionDef):
                    continue
                methods.append(method.name)
                if method.name in UI_WRITES:
                    method.decorator_list.append(ast.parse("_r.ui_operation('" + method.name + "')", mode='eval').body)
                if method.name in ('exportStoreNode', 'importStoreNode'):
                    method.body = ast.parse("return _r.file_ui('" + ('export_store' if method.name == 'exportStoreNode' else 'import_store') + "')").body
                if method.name == 'bakeIkFkWin':
                    method.body.insert(0, ast.parse('autkeystate_remeber = pm.autoKeyframe(query=True, state=True)').body[0])
                    for assignment in ast.walk(method):
                        if isinstance(assignment, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'keying_frames' for t in assignment.targets) and isinstance(assignment.value, ast.Call) and isinstance(assignment.value.func, ast.Name) and assignment.value.func.id == 'sorted':
                            assignment.value = ast.parse('[t for t in ' + ast.unparse(assignment.value) + ' if minFrame <= t <= maxFrame]', mode='eval').body
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
            if node.name in FUNCTION_WRITES:
                node.body.insert(1 if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) else 0, ast.parse('_r.require_active()').body[0])
            if node.name == 'findStoreNodeFromSelection':
                node.body = ast.parse('return _r.find_store_from_selection()').body
            if node.name == 'loadIkFkCtrl':
                node.body = ast.parse('return _r.load_store(ns, limb, side)').body
            if node.name == 'saveIKFkCtrls':
                node.body = ast.parse('_r.require_active()\nreturn _r.save_from_native(limb, side, fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis)').body
        for item in ast.walk(node):
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                item.value = item.value.replace('ikfkswitchUI_', 'mtbIKFK_').replace('ikFkSwitch_UI', 'mtbIKFK_UI')
                if item.value == '  rotateY':
                    item.value = 'rotateY'
                if item.value == 'snapGrp':
                    item.value = 'mtbIKFK_private_snapGrp'
            if isinstance(item, ast.Name) and item.id == 'mutliplyer':
                item.id = 'multiplyer'
            if isinstance(item, ast.Compare) and any(isinstance(c, ast.Constant) for c in item.comparators):
                item.ops = [ast.Eq() if isinstance(op, ast.Is) else ast.NotEq() if isinstance(op, ast.IsNot) else op for op in item.ops]
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == 'eval':
                item.func = ast.parse('_r.literal_data', mode='eval').body
            if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ns' for t in item.targets) and isinstance(node, ast.FunctionDef) and node.name == 'saveIKFkCtrls':
                item.value = ast.parse('_r.store_namespace(fkwrist)', mode='eval').body
        if isinstance(node, ast.FunctionDef) and node.name == 'ikfkMatch':
            # Last switch value must use actual 0..1 / 0..10 range.
            for item in node.body[-3:]:
                for call in ast.walk(item):
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'setAttr' and len(call.args) == 2 and isinstance(call.args[1], ast.Constant) and call.args[1].value == 1:
                        call.args[1] = ast.Name(id='switchAttrRange', ctx=ast.Load())
        output.append(node)
    header = ast.parse('from .proxy import pm\nfrom . import runtime as _r').body
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=header + output, type_ignores=[])))
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'ik_fk_switch_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/pro.py', tofile='native.py')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': resources, 'functions': functions, 'ui_methods': methods, 'version': '3.0 PRO / 1.10 legacy', 'license': 'Monika Gelbmann credited supplied PRO/legacy source; no standalone redistribution grant supplied, private local preparation only.', 'external_dependency': 'pymel.core compatible with target Maya/Python, currently absent in local Maya2025'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'ik_fk_switch', 'registration': {'module': 'ik_fk_switch', 'class_name': 'IKFKTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['pymel.core compatible with target Maya; absent in local Maya2025', 'Maya native cmds/OpenMaya1/2 and actual GUI for original full panel', 'Existing BaseMayaTool/Undo'], 'source': '../mog_ikFkSwitchPro.py', 'change_summary': 'Complete PRO matching/temp IK chain/pole vector/full UI/baking retained, guarded standard API/callbacks and owned Store JSON transfer, legacy source also archived intact.', 'verification_limitations': ['PyMel absent: original matching/GUI/bake execution unverified', 'Rig-specific reference/control/joint orientation/pole vector behavior pending', 'Store transfer uses explicit guarded JSON metadata instead of original scene import/forced deletion', 'Source key deletion/rekey/temporary zero poses alter production animation; backup required'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': len(functions), 'ui_methods': len(methods), 'payload': len(files)}))


if __name__ == '__main__':
    main()
