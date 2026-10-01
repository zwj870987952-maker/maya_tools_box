"""Preserve the complete six-version SAT distribution and prepare its private port."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'tools_staging_pool/01_animation/shape_animation_tool'
RAW = UNIT/'sat【修型插件】'
RC = UNIT/'release_candidate'
PKG = RC/'maya_toolkit/tools/shape_animation_tool'


def main():
    PKG.mkdir(parents=True, exist_ok=True)
    review = json.loads((ROOT/'plans/staging_run/shape_animation_source_review.json').read_text(encoding='utf-8'))
    files = []
    for row in review['files']:
        src = RAW/row['path']
        relative = row['path'] + ('.original' if src.suffix == '.py' else '')
        dst = PKG/'upstream'/relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        files.append({'path': relative, 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
    primary = RAW/'sat_2022_py3【汉化版】'
    source = (primary/'main.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    original = {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)] for n in tree.body if isinstance(n, ast.ClassDef)}
    class Port(ast.NodeTransformer):
        def visit_Import(self, n):
            kept = [a for a in n.names if a.name not in ('pymel.core', 'imp')]
            n.names = kept
            return n if kept else None
        def visit_Try(self, n):
            if n in tree.body:
                return None
            return self.generic_visit(n)
        def visit_Assign(self, n):
            if n in tree.body and any(isinstance(t, ast.Name) and t.id in ('modulePath','v') for t in n.targets):
                return ast.parse('modulePath = str(Path(__file__).resolve().parent)' if n.targets[0].id == 'modulePath' else 'v = ""').body[0]
            if isinstance(n.value,ast.Constant) and n.value.value=='pickShapeCtx':
                n.value=ast.parse('self._pick_context',mode='eval').body
            return self.generic_visit(n)
        def visit_Call(self,n):
            self.generic_visit(n)
            if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='fnMesh' and n.func.attr=='name':
                n.func.attr='fullPathName'
            if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='cmds' and n.func.attr=='ls' and any(k.arg=='type' and isinstance(k.value,ast.Constant) and k.value.value=='mesh' for k in n.keywords):
                n.keywords.append(ast.keyword(arg='long',value=ast.Constant(True)))
            return n
        def visit_FunctionDef(self, n):
            self.generic_visit(n)
            if n.name == '__init__':
                n.args.defaults = [ast.Constant(None)]
                n.body.insert(0, ast.parse('if parent is None:\n    parent = mayaMainWindow()').body[0])
            return n
    tree = Port().visit(tree)
    prefix = 'from pathlib import Path\nfrom .Qt import wrapInstance\nfrom . import pick_compat as pm\nuseShapesBrush = False\n'
    native = prefix + ast.unparse(ast.fix_missing_locations(tree)) + '\n\nfrom .ui_bridge import install\ninstall(MainWindow)\n'
    (PKG/'native.py').write_text(native, encoding='utf-8', newline='\n')
    generated = {'native.py': hashlib.sha256(native.encode()).hexdigest()}
    for filename in ('mainWindow.py','aboutWindow.py'):
        code = (primary/filename).read_text(encoding='utf-8-sig').replace('QtWidgets.QAction(', 'QtGui.QAction(')
        (PKG/filename).write_text(code, encoding='utf-8', newline='\n')
        generated[filename] = hashlib.sha256(code.encode()).hexdigest()
    docs = RC/'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs/'shape_animation_tool_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), native.splitlines(True), fromfile='upstream/main.py.original', tofile='native.py')), encoding='utf-8', newline='\n')
    cat = {'raw_files': files, 'classes': original, 'ported_sha256': generated, 'variants': [r for r in review['files'] if 'methods' in r], 'word_instructions': review['word_paragraphs'], 'license': 'Commercial purchase URL supplied; no redistribution license, SHAPESBrush plugin or MEL supplied. Personal local preparation only.', 'version_comparison': 'All six versions have the same 34 class methods. Older variants differ only in NoneType syntax/comments; English homePage and generated UI strings differ. Full distributions preserved byte for byte.'}
    (PKG/'catalog.json').write_text(json.dumps(cat, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    (UNIT/'.gitattributes').write_text('sat【修型插件】/** -text\n', encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n', encoding='utf-8')
    launch = (ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','shape_animation_tool').replace('RootMotionBakeTool','ShapeAnimationTool')
    (RC/'launch_candidate.py').write_text(launch, encoding='utf-8', newline='\n')
    payload = [p for f in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in f.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    data = {'tool_id':'shape_animation_tool', 'registration':{'module':'shape_animation_tool','class_name':'ShapeAnimationTool'}, 'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources':['catalog.json','upstream/ (39 unchanged original files including Word instructions)'], 'dependencies':['Maya cmds/mel/OpenMaya/OpenMayaUI','PySide6/shiboken6 or PySide2/shiboken2 for interactive UI','Optional separately installed SHAPESBrush.mll and SHAPESBrush MEL','BaseMayaTool/ToolResult/Undo'], 'acceptance_required':True, 'change_summary':'Complete original paired corrective blendShape target and keyframe/sculpt/brush/pick/UI workflow retained; private UUID-owned persistent sessions, strict graph preflight, guarded temporary cleanup, Qt6/Python3 and JSON/legacy pickle fixes. All six original distributions retained.', 'verification_limitations':['Real Maya GUI, Artisan first-activation behavior, pick/isolated viewport and saved-scene undo/reload require acceptance','SHAPESBrush plugin/MEL are absent and its optional button requires separate user installation','Commercial source has no redistribution license; local personal preparation only','Original .ui sources/pysideuic are absent; delivered generated UI needs no recompilation','Older Maya/Python/Qt versions require acceptance']}
    (RC/'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'original_files':len(files),'class_methods':sum(map(len,original.values()))}))


if __name__ == '__main__':
    main()
