"""Preserve complete v19 class, port option reads without GUI emulation."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/relationship_tools_v19'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/relationship_tools_v19'
OPTIONS = {'translate_checkbox': 'translate', 'rotate_checkbox': 'rotate', 'bake_checkbox': 'bake', 'world_coords_checkbox': 'world_coords', 'anim_layer_checkbox': 'layer', 'frame_step': 'step'}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(line.rstrip() for line in value.splitlines()).rstrip() + '\n', encoding='utf-8', newline='\n')


class Options(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'cmds' and node.func.attr in ('checkBox', 'intField') and node.args and isinstance(node.args[0], ast.Attribute) and node.args[0].attr in OPTIONS:
            flags = {k.arg: k.value for k in node.keywords}
            if any(key in flags for key in ('q', 'query')):
                return ast.Call(func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='option', ctx=ast.Load()), args=[ast.Constant(value=OPTIONS[node.args[0].attr])], keywords=[])
        return node


def main():
    source = UNIT / 'Relationship Tools_v19.py'
    vendor = PKG / 'vendor/Relationship Tools_v19.py.original'
    vendor.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, vendor)
    original = ast.parse(source.read_bytes())
    klass = next(n for n in original.body if isinstance(n, ast.ClassDef))
    methods = [n.name for n in klass.body if isinstance(n, ast.FunctionDef)]
    tree = Options().visit(ast.Module(body=[n for n in original.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef))], type_ignores=[]))
    ast.fix_missing_locations(tree)
    write(PKG / 'original_logic.py', ast.unparse(tree))
    write(PKG / 'catalog.json', json.dumps({'source': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'class_name': klass.name, 'methods': methods, 'author': 'ZWJ; original history/comments preserved in vendor', 'original_top_level_launch_removed': True}, indent=2))
    write(UNIT / '.gitattributes', '*.py -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'relationship_tools_v19').replace('RootMotionBakeTool', 'RelationshipToolsTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'relationship_tools_v19', 'registration': {'module': 'relationship_tools_v19', 'class_name': 'RelationshipToolsTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [source.name], 'dependencies': ['Maya cmds/MEL with real timeline for GUI range selection'], 'acceptance_required': True, 'change_summary': 'Complete original RelationshipTool v19 class and UI preserved; safe full API/GUI mark/foot/animation marks, one/more step, world copy/paste, align, layers and owned mark deletion. Stable message/UUID ownership instead of suffix/global cache, explicit inclusive/exclusive range/selected channels, no unrelated key removal, read-only preflight and caller/Undo restoration.', 'verification_limitations': ['Real Maya GUI, complex production rigs/constraints/animation layers and other versions not_run', 'Maya Undo does not restore in-memory copied pose cache or explicit exported JSON', 'Original broad suffix deletion and shared system temp cache intentionally replaced; unknown old marks require explicit review, never auto-delete']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'methods': len(methods), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
