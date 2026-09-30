import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/keyframe_overlap_v2_0'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/keyframe_overlap'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for source in sorted((UNIT / 'KFOverlap').rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        target = PACKAGE / 'upstream' / source.relative_to(UNIT / 'KFOverlap')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, text in ((UNIT / '.gitattributes', 'KFOverlap/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(text, encoding='utf-8', newline='\n')
    original = (UNIT / 'KFOverlap/KeyframeOverlap.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    methods = {}
    for cls in tree.body:
        if not isinstance(cls, ast.ClassDef):
            continue
        methods[cls.name] = [m.name for m in cls.body if isinstance(m, ast.FunctionDef)]
        for method in cls.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            name = method.name
            if cls.name == 'loc_delay_system':
                if name == '__init__':
                    method.body = [s for s in method.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and isinstance(s.value.func, ast.Name) and s.value.func.id == 'init_scene')]
                    method.body.insert(0, ast.parse('_r.require_active()').body[0])
                    method.body.extend(ast.parse('self.prefix = _r._PREFIX\nself.groups = dict(_r._GROUPS)').body)
                elif name == 'del_prefix':
                    method.body = ast.parse('_r.clear_transients()').body
                elif name in ('kf_overlap', 'kf_bake_animation'):
                    method.decorator_list.append(ast.parse('_r.business_bridge(%r)' % ('create' if name == 'kf_overlap' else 'bake'), mode='eval').body)
                else:
                    method.body.insert(0, ast.parse('_r.require_active()').body[0])
            elif cls.name == 'util' and name in ('get_space_locator', 'match_transform'):
                method.body.insert(0, ast.parse('_r.require_active()').body[0])
            if cls.name == 'kf_overlap':
                if name == '__init__':
                    method.body = [s for s in method.body if not (isinstance(s, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == 'lds' for t in s.targets))]
                    method.body.extend(ast.parse('self.lds = _r.UIBridge()\nself.win_id = "mtbKeyframeOverlap"\nself.dock_id = self.win_id + "_DOCK"').body)
                elif name == 'support':
                    method.body = ast.parse('self.is_connected = False  # Archived remote exec is never invoked.').body
                elif name == 'update_usr_cfg':
                    method.body = ast.parse('self.cfg_data = self.get_captured_param()\nself.usr_data = {"user_orig": self.user_original, "user_last": self.user_latest}\nself._presets = getattr(self, "_presets", {})').body
                elif name in ('save_preset', 'load_preset', 'rename_preset', 'delete_preset'):
                    method.body = ast.parse('return _r.preset(self, %r)' % name).body
                elif name == 'exec_script':
                    method.body = ast.parse('param = self.get_captured_param()\nparam["select_ls"] = cmds.ls(long=True, selection=True) or []\nreturn self.lds.kf_overlap(param) if exec_name == "overlap" else self.lds.kf_bake_animation(param)').body
            for node in ast.walk(method):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and isinstance(node.right, ast.Subscript) and isinstance(node.right.value, ast.Attribute) and node.right.value.attr == 'loc_names':
                    old_left, old_right = node.left, node.right
                    node.__class__ = ast.Call
                    node.func = ast.parse('_r.helper_name', mode='eval').body
                    node.args, node.keywords = [old_left, old_right], []
                if cls.name == 'loc_delay_system' and name == 'kf_overlap' and isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'short_name' for t in node.targets):
                    node.value = ast.Name(id='obj', ctx=ast.Load())
                if cls.name == 'loc_delay_system' and name == 'kf_bake_animation' and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'keyframe':
                    node.keywords = [k for k in node.keywords if k.arg != 'at']  # original undefined at, query already uses explicit plugs
                if cls.name == 'loc_delay_system' and name == 'kf_overlap' and isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bake_sample' for t in node.targets):
                    node.value = ast.Call(func=ast.Name(id='max', ctx=ast.Load()), args=[ast.Constant(1), node.value], keywords=[])
                if cls.name == 'loc_delay_system' and name == 'kf_overlap' and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'keyframe':
                    for keyword in node.keywords:
                        if keyword.arg == 'at':
                            keyword.value = ast.parse('["t" + i for i in ["x", "y", "z"] if i not in mode_param["skip"]]', mode='eval').body
                if cls.name == 'loc_delay_system' and name == 'keyframe_optimizer' and isinstance(node, ast.ListComp) and isinstance(node.elt, ast.Call) and isinstance(node.elt.func, ast.Attribute) and node.elt.func.attr in ('cutKey', 'keyframe'):
                    # Original used 0..len(range)-1 instead of actual frame numbers.
                    node.generators[0].iter = ast.Name(id='tc_ls', ctx=ast.Load())
                if isinstance(node, ast.FunctionDef) and node.name == 'reload_preset_name':
                    node.body = ast.parse('preset_name = cmds.optionMenu(self.element["preset_om"], q=True, v=True)\nfor item in cmds.optionMenu(self.element["preset_om"], q=True, ils=True) or []:\n    cmds.deleteUI(item)\ncmds.menuItem(parent=self.element["preset_om"], label="Defualt")\nfor name in sorted(self._presets):\n    cmds.menuItem(parent=self.element["preset_om"], label=name)\nif preset_name in self._presets:\n    cmds.optionMenu(self.element["preset_om"], e=True, v=preset_name)').body
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Import) and any(a.name == 'maya.cmds' for a in n.names)) and not (isinstance(n, ast.ImportFrom) and n.module == 'maya')]
    header = ast.parse('from .proxy import cmds\nfrom . import runtime as _r').body
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=header + tree.body, type_ignores=[])))
    text = '\n'.join(s.rstrip() for s in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'keyframe_overlap_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/KeyframeOverlap.py', tofile='native.py')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'methods': methods, 'raw_files': resources, 'license': 'Burased Uttha (DEX3D), original-machine restriction preserved. No independent license; local private only.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/jop_retarget_anim_v09/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('jop_retarget_anim', 'keyframe_overlap').replace('JopRetargetTool', 'KeyframeOverlapTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'keyframe_overlap', 'registration': {'module': 'keyframe_overlap', 'class_name': 'KeyframeOverlapTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya classic particles, constraints, pairBlend and native cmds UI', 'BaseMayaTool/Undo'], 'source': '../KFOverlap/KeyframeOverlap.py', 'change_summary': 'Complete original particle-delay/locator editing/constraint/bake optimizer/UI with persistent owner messages and guarded Undo; remote exec/config writes isolated; session presets.', 'verification_limitations': ['Real GUI and production particle/scale motion quality pending', 'Original-machine restriction; no independent redistribution license', 'Preset persistence changes to process memory; no external runtime file writes', 'Simulation evaluations can affect external dynamics; isolate backup scenes'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'methods': methods, 'resources': len(resources)}))


if __name__ == '__main__':
    main()
