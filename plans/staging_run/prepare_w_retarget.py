"""Archive full Walter Delgado source and port its complete declarations."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/w_retarget_tool'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/w_retarget_tool'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


class EnginePort(ast.NodeTransformer):
    def visit_Assign(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == 'cmds.intFieldGrp':
            attr = ast.unparse(node.targets[0])
            if attr in ('self.StartFrame', 'self.EndFrame'):
                node.value = ast.Name(id='start_frame' if attr.endswith('StartFrame') else 'end_frame', ctx=ast.Load())
        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if ast.unparse(node.func) in ('cmds.group', 'cmds.shadingNode'):
            for kw in node.keywords:
                if kw.arg == 'n' and isinstance(kw.value, ast.BinOp):
                    kw.value.left = ast.Name(id='prefix', ctx=ast.Load())
        return node

    def visit_Try(self, node):
        # Exact original nine-channel write loop: preserve sampled values but
        # key explicit values on already animated targets and surface failures.
        if any(isinstance(n, ast.Call) and ast.unparse(n.func) == 'cmds.setKeyframe' for n in ast.walk(node)):
            return ast.parse("valueAttr = cmds.getAttr(locGrpTgt3 + '.' + attr)\nif not math.isfinite(valueAttr):\n    raise ValueError('Non-finite sampled channel')\ncmds.setKeyframe(target, attribute=attr, time=i, value=valueAttr)").body
        # Avoid suppressing constraint/parent failures on genuinely parented rigs.
        first = ast.unparse(node.body[0])
        if first.startswith('sourceFather =') or first.startswith('sourceFatherTgt ='):
            variable = 'sourceFather' if first.startswith('sourceFather =') else 'sourceFatherTgt'
            operand = 'source' if variable == 'sourceFather' else 'target'
            body = [ast.parse(variable + ' = parents[0]').body[0]] + node.body[1:]
            return [ast.parse('parents = cmds.listRelatives(' + operand + ', parent=True, fullPath=True) or []').body[0], ast.If(test=ast.Name(id='parents', ctx=ast.Load()), body=body, orelse=[])]
        return self.generic_visit(node)


def main():
    source = UNIT / 'WretargetTool.py'
    archive = PKG / 'upstream/WretargetTool.py.original'
    archive.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, archive)
    original = ast.parse(source.read_text(encoding='utf-8-sig'))
    cls = next(n for n in original.body if isinstance(n, ast.ClassDef))
    methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    engine = copy.deepcopy(next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'CopyAnim'))
    engine.name = 'copy_anim'
    engine.args = ast.parse('def copy_anim(self, source, target, start_frame, end_frame, prefix, ValidObj=1, initTime=0): pass').body[0].args
    engine = EnginePort().visit(engine)
    ast.fix_missing_locations(engine)
    write(PKG / 'engine.py', '# Complete original CopyAnim matrix/constraint sampling, explicitly adapted.\nimport math\nimport time\nfrom maya import cmds\n\n' + ast.unparse(engine))
    # All original help functions, class methods and full UI declarations remain.
    native = copy.deepcopy(original)
    native.body = [n for n in native.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Call)]
    text = ast.unparse(native)
    text = text.replace("'WretargetTool V1.0'", "'stagingWRetargetTool'")
    text = text.replace("'instructionWindow'", "'stagingWRetargetInstruction'").replace("'aboutWindow'", "'stagingWRetargetAbout'")
    text = text.replace('cmds.deleteUI("instructionWindow")', 'cmds.deleteUI("stagingWRetargetInstruction")').replace('cmds.deleteUI("aboutWindow")', 'cmds.deleteUI("stagingWRetargetAbout")')
    text = text.replace('self.DeletePlaceHolders = cmds.', 'self.DeletePlaceHoldersControl = cmds.').replace('self.CopyAll = cmds.', 'self.CopyAllControl = cmds.')
    # Maya invokes callbacks with extra arguments; only constructor keeps its signature.
    for method in methods:
        if method != '__init__':
            if method == 'CopyAnim':
                text = text.replace('ValidObj=1, initTime=0):', 'ValidObj=1, initTime=0, *args):')
            else:
                text = text.replace('def ' + method + '(self):', 'def ' + method + '(self, *args):')
    write(PKG / 'native_ui.py', '# Full original declarations; business callbacks overridden by candidate bridge.\n' + text)
    catalog = {'author': 'Walter Delgado', 'files': [{'path': source.name, 'archive': archive.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}], 'original_methods': methods, 'license': 'No independent license file supplied; original author/header preserved without relicensing'}
    write(PKG / 'catalog.json', json.dumps(catalog, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', '*.py -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'w_retarget_tool').replace('RootMotionBakeTool', 'WRetargetTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'w_retarget_tool', 'registration': {'module': 'w_retarget_tool', 'class_name': 'WRetargetTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [source.name], 'dependencies': ['Maya cmds/mel; loaded fbxmaya plugin for explicit export'], 'acceptance_required': True, 'change_summary': 'Complete Walter Delgado source/full four-pair UI retained. Original pose-offset matrix/constraint algorithm with exclusive-end sampling and nine-channel scale behavior; bounded batch preflight, owned helper cleanup, explicit key values/Undo, environment restoration and new-file FBX export/settings restoration.', 'verification_limitations': ['Real Maya GUI/production rigs/jointOrient/rotate orders/pivots and FBX reimport not_run', 'Original algorithm retargets pose offsets, not direct source transforms; proxy scale generally 1', 'Constraints/driven or layered target channels rejected; use an unlocked independent target', 'Exceptions may leave partial keys in one Undo chunk; files cannot be undone; earlier successful export files remain after later errors', 'No independent license supplied; original source/author retained']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'original_files': 1, 'original_methods': len(methods)}))


if __name__ == '__main__':
    main()
