"""Retain all original UI and business methods with guarded writes and unique layers."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/root_motion_bake'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/root_motion_bake'


def main():
    raw=UNIT/'root动画生成.py'
    source=raw.read_text(encoding='utf-8-sig')
    tree=ast.parse(source)
    original=next(n for n in tree.body if isinstance(n,ast.ClassDef))
    methods=[n.name for n in original.body if isinstance(n,ast.FunctionDef)]
    tree.body=[n for n in tree.body if not isinstance(n,ast.Try)]
    class Fix(ast.NodeTransformer):
        def visit_Import(self,n):
            if any(a.name=='maya.cmds' for a in n.names):
                return ast.parse('from .runtime import native_cmds as cmds').body[0]
            return n
        def visit_Constant(self,n):
            if n.value=='constraintBakeToolWin':
                n.value='mtkRootMotionBakeCandidateWindow'
            return n
        def visit_If(self,n):
            self.generic_visit(n)
            if isinstance(n.test,ast.Call) and isinstance(n.test.func,ast.Attribute) and n.test.func.attr=='objExists' and n.test.args and isinstance(n.test.args[0],ast.Name) and n.test.args[0].id=='layer_name':
                return None
            return n
        def visit_FunctionDef(self,n):
            self.generic_visit(n)
            if n.name in ('create_constraint','bake_animation','set_relative_transform','process_single_group'):
                n.body.insert(1,ast.parse('require_scope()').body[0])
            if n.name=='process_single_group':
                code=ast.unparse(n)
                code=code.replace('layer_name = f"{root_obj.replace(\':\', \'_\')}_offsetLayer"', 'layer_name = safe_layer_name(root_obj)')
                code=code.replace('    if cmds.objExists(layer_name):\n        cmds.delete(layer_name)\n', '')
                code=code.replace('cmds.animLayer(anim_layer, edit=True, selected=True)', 'cmds.animLayer(anim_layer, edit=True, selected=True, preferred=True)')
                n=ast.parse(code).body[0]
            return n
    tree=Fix().visit(tree)
    tree.body=ast.parse('from .runtime import require_scope, safe_layer_name').body+tree.body
    native=ast.unparse(ast.fix_missing_locations(tree))+'\n\nfrom .ui_bridge import install\ninstall(ConstraintBakeTool)\n'
    PKG.mkdir(parents=True,exist_ok=True)
    (PKG/'native.py').write_text(native,encoding='utf-8',newline='\n')
    upstream=PKG/'upstream'
    upstream.mkdir(exist_ok=True)
    shutil.copyfile(raw,upstream/'root_motion_original.py.original')
    (UNIT/'.gitattributes').write_text('root动画生成.py -text\n',encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n',encoding='utf-8')
    cat={'methods':methods,'raw_files':[{'path':'root_motion_original.py.original','sha256':hashlib.sha256(raw.read_bytes()).hexdigest()}], 'native_sha256':hashlib.sha256(native.encode()).hexdigest(),'license':'Original header author Assistant; no independent license supplied, local personal preparation only','relative_transform':'Original world translation/Euler subtraction retained; not relative matrix or quaternion transform'}
    (PKG/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    docs=RC/'docs/tools'
    docs.mkdir(parents=True,exist_ok=True)
    (docs/'root_motion_bake_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),native.splitlines(True),fromfile='upstream/root_motion_original.py.original',tofile='native.py')),encoding='utf-8')
    launcher=(ROOT/'tools_staging_pool/01_animation/pose_transfer_remote/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('pose_transfer_remote','root_motion_bake').replace('PoseTransferRemoteTool','RootMotionBakeTool')
    (RC/'launch_candidate.py').write_text(launcher,encoding='utf-8')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    data={'tool_id':'root_motion_bake','registration':{'module':'root_motion_bake','class_name':'RootMotionBakeTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':['catalog.json','upstream/root_motion_original.py.original'],'dependencies':['Maya cmds/mel','BaseMayaTool/ToolResult/Undo'],'acceptance_required':True,'change_summary':'All original 13 methods and native UI retained; complete center constraints/root baking/offset layer workflow, strict batch preflight, unique layers and tracked temporary cleanup, selected-range fix and explicit center snapshots.', 'verification_limitations':['Original Maya UI and production rig/layers/rotation orders need human acceptance','Original relative position is world translation/Euler arithmetic, not matrix-relative rotation/scale','Original bake operates all root keyable attributes and preserveOutsideKeys=False','No independent license supplied; local only']}
    (RC/'promotion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'original_methods':len(methods),'native_bytes':len(native.encode())}))


if __name__=='__main__':
    main()
