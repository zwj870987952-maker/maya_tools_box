import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/gimbal_lock_fix'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/gimbal_lock_fix'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    source = UNIT / 'maya_animation_gimbal_fix.py'
    target = PACKAGE / 'upstream' / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    for file, text in ((UNIT / '.gitattributes', 'maya_animation_gimbal_fix.py -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        file.write_text(text, encoding='utf-8', newline='\n')
    original = source.read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    output = []
    methods = []
    for node in tree.body:
        if isinstance(node, ast.Import) and any(alias.name == 'maya.cmds' for alias in node.names):
            continue
        if isinstance(node, ast.If):
            continue  # Original __main__ UI launch; no import side effects.
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if not isinstance(method, ast.FunctionDef):
                    continue
                methods.append(method.name)
                if method.name == 'get_animation_data':
                    for loop in ast.walk(method):
                        if isinstance(loop, ast.For) and isinstance(loop.target, ast.Name) and loop.target.id == 't':
                            loop.body = ast.parse("rot = cmds.getAttr(obj + '.rotate', time=t)[0]\nrotations.append(rot)").body
                if method.name == 'quaternion_to_euler':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == 'order' for t in item.targets):
                            item.__class__ = ast.Expr
                            item.value = ast.parse('euler.reorderIt(order_dict.get(rotation_order.lower(), om.MEulerRotation.kXYZ))', mode='eval').body
                if method.name == 'quaternion_slerp':
                    method.body.insert(1, ast.parse('quat2 = om.MQuaternion(quat2)').body[0])
                if method.name == 'detect_gimbal_issues':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr == 'angleShortestPath':
                            replacement = ast.parse('_r.shortest_angle(prev_quat, curr_quat)', mode='eval').body
                            item.func, item.args, item.keywords = replacement.func, replacement.args, replacement.keywords
                if method.name == '_apply_fixed_rotations':
                    method.body.insert(1, ast.parse('_r.require_active()').body[0])
        for item in ast.walk(node):
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                if item.value == 'animCurveTL':
                    item.value = 'animCurveTA'
                elif item.value == 'gimbalFixerUI':
                    item.value = 'mtbGimbalFixerUI'
                elif item.value == '整个动画':
                    item.value = '播放范围（原行为）'
                elif item.value == '时间滑块':
                    item.value = '动画范围（原行为）'
                elif item.value == '保留原始关键帧:':
                    item.value = '保留键时间（原选项未实现）:'
                elif '会消除万向锁问题' in item.value:
                    item.value = item.value.replace('但会消除万向锁问题', '需要视窗逐帧复验，不能保证消除所有万向锁')
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr == 'checkBoxGrp':
                item.keywords.append(ast.keyword(arg='enable', value=ast.Constant(False)))
        output.append(node)
    header = ast.parse('from .proxy import cmds\nfrom . import runtime as _r').body
    bridge = ast.parse('''
_Algorithm = GimbalLockFixer

class GimbalLockFixer(_Algorithm):
    def detect_gimbal_issues(self, obj, threshold=45.0):
        from .tool import GimbalFixTool
        result = GimbalFixTool().run(action='detect', objects=[obj], threshold=threshold)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['results'][0]['problem_ranges']

    def fix_animation_curves(self, obj, start_frame=None, end_frame=None, samples_per_frame=1):
        from .tool import GimbalFixTool
        result = GimbalFixTool().run(action='fix', objects=[obj], start=start_frame, end=end_frame, samples_per_frame=samples_per_frame)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['results'][0]['fixed']
''').body
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=header + output + bridge, type_ignores=[])))
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'gimbal_lock_fix_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/source.py', tofile='native.py')), encoding='utf-8', newline='\n')
    catalog = {'raw_files': [{'path': 'upstream/' + source.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}], 'source_methods': methods, 'source_ui': 'create_gimbal_fix_ui', 'license': 'User supplied script, author header Claude; no separate license supplied', 'changes': ['Full native algorithm/UI retained', 'Read-only time-context sampling', 'Quaternion→Euler reorderIt for non-XYZ orientation', 'Copy second quaternion before shortest-path sign flip', 'Angular fallback curve type', 'Standard GUI API callbacks/Undo', 'Disabled original unused preserve checkbox; accurate range/algorithm help']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'gimbal_lock_fix', 'registration': {'module': 'gimbal_lock_fix', 'class_name': 'GimbalFixTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': ['upstream/' + source.name, 'catalog.json'], 'dependencies': ['Maya cmds and OpenMaya API1', 'Existing BaseMayaTool/Undo', 'Maya GUI for native panel'], 'source': '../maya_animation_gimbal_fix.py', 'change_summary': 'Complete quaternion detection/interpolation/native UI, correct non-XYZ reconstruction and cache sign mutation, guarded direct rotation curves and read-only detection.', 'verification_limitations': ['Real Maya GUI/production gimbal effect pending', 'Canonical quaternion conversion does not guarantee elimination of all gimbal/long-spin issues', 'Direct angular rotation curves and degree units only; layers/constraints/animated order unsupported', 'Global spline tangents affect entire curves outside chosen key range'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'methods': len(methods), 'payload': len(files)}))


if __name__ == '__main__':
    main()
