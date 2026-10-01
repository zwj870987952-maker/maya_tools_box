"""Preserve full original class/UI with UUID session and owned deletion boundaries."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/pose_transfer_remote'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/pose_transfer_remote'


def main():
    raw = UNIT / 'PoseTransfer.py'
    source = raw.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'create_pose_transfer_ui')]
    class Fix(ast.NodeTransformer):
        def visit_Constant(self, node):
            if node.value == 'PoseTransferTool':
                node.value = 'mtkPoseTransferCandidateWindow'
            return node
        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'cmds' and node.func.attr == 'delete':
                node.func = ast.Name(id='checked_delete', ctx=ast.Load())
            return node
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if node.name in ('create_locators_and_record_pose', 'move_locators_to_new_root_position', 'apply_pose_from_locators', 'cleanup_locators'):
                node.body.insert(1, ast.parse('require_scope()').body[0])
            if node.name == 'create_locators_and_record_pose':
                code = ast.unparse(node)
                code = code.replace("loc_name = f\"pose_loc_{ctrl.replace(':', '_')}_{i}\"", 'loc_name = helper_name(ctrl, i)')
                code = code.replace('locator = cmds.spaceLocator(name=loc_name)[0]', 'locator = cmds.spaceLocator(name=loc_name)[0]\n        self.locators.append(locator)')
                # Remove later append only; immediate tracking survives failed xform/addAttr.
                index = code.rfind('        self.locators.append(locator)')
                code = code[:index] + code[index:].replace('        self.locators.append(locator)\n', '', 1)
                node = ast.parse(code).body[0]
            if node.name == 'move_locators_to_new_root_position':
                code = ast.unparse(node).replace('    return True', '    self.original_root_pos = current_root_pos\n    return True')
                node = ast.parse(code).body[0]
            if node.name == 'is_controller':
                code = ast.unparse(node).replace('obj_name = obj.lower()', "obj_name = obj.rsplit('|', 1)[-1].lower()")
                node = ast.parse(code).body[0]
            if node.name == 'create_pose_transfer_ui':
                code = ast.unparse(node).replace('pose_transfer = PoseTransfer()', 'from .ui_bridge import SessionButtons\n    pose_transfer = SessionButtons()')
                code = code.replace('widthHeight=(350, 280)', 'widthHeight=(350, 550)')
                code = code.replace('pose_transfer = SessionButtons()', "pose_transfer = SessionButtons()\n    cmds.checkBox('mtkPoseTransferCandidateAllowReferences', label='Allow reference edits when applying pose', value=False)")
                node = ast.parse(code).body[0]
            return node
    tree = Fix().visit(tree)
    tree.body = ast.parse('from .runtime import require_scope, checked_delete, helper_name').body + tree.body
    native = ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    PKG.mkdir(parents=True, exist_ok=True)
    (PKG / 'native.py').write_text(native, encoding='utf-8', newline='\n')
    upstream = PKG / 'upstream'
    upstream.mkdir(exist_ok=True)
    for filename in ('PoseTransfer.py', 'Readme.txt'):
        shutil.copyfile(UNIT / filename, upstream / (filename + '.original' if filename.endswith('.py') else filename))
    (upstream / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    (UNIT / '.gitattributes').write_text('PoseTransfer.py -text\nReadme.txt -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    klass = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))
    catalog = {'methods': [n.name for n in klass.body if isinstance(n, ast.FunctionDef)], 'raw_files': [{'path': ('PoseTransfer.py.original' if f.endswith('.py') else f), 'sha256': hashlib.sha256((UNIT/f).read_bytes()).hexdigest()} for f in ('PoseTransfer.py','Readme.txt')], 'native_sha256': hashlib.sha256(native.encode()).hexdigest(), 'license': 'No independent license supplied; local personal candidate only'}
    (PKG / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'pose_transfer_remote_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), native.splitlines(True), fromfile='upstream/PoseTransfer.py.original', tofile='native.py')), encoding='utf-8')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('keyframe_reduction', 'pose_transfer_remote').replace('KeyframeReductionTool', 'PoseTransferRemoteTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8')
    payload = [p for folder in (RC/'maya_toolkit', RC/'docs', RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'pose_transfer_remote', 'registration': {'module':'pose_transfer_remote','class_name':'PoseTransferRemoteTool'}, 'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources':['catalog.json','upstream/PoseTransfer.py.original','upstream/Readme.txt'], 'dependencies':['Maya cmds and original legacy OpenMaya import','BaseMayaTool/Undo'], 'acceptance_required':True, 'change_summary':'Full original 9-method locator-based world-matrix pose capture/root translation/apply/cleanup and original UI retained with scene UUID sessions, scoped controller discovery and owned helper protections.', 'verification_limitations':['Real original Maya UI and production rig/rotation-scale/pivot/reference behavior require human acceptance','Original workflow offsets translation only and does not automatically remap across models','Scene helper metadata preserved; no external files written','No independent license supplied, local only']}
    (RC/'promotion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'original_methods':len(catalog['methods'])}))


if __name__ == '__main__':
    main()
