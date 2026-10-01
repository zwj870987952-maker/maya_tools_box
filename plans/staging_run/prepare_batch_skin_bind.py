"""Bundle both full prototypes and adapt complete proxy engine/UI."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/batch_skin_bind'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/batch_skin_bind'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    files = []
    for source in sorted(UNIT.glob('*.py')):
        target = PKG / 'upstream' / (source.name + '.original')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        files.append({'path': source.name, 'archive': target.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    source = (UNIT / '生成代理.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    definitions = ast.Module(body=[node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))], type_ignores=[])
    native = ast.unparse(definitions)
    native = native.replace("'CreateObjectsWindow'", "'stagingCreateObjectsWindow'")
    native = native.replace("cmds.checkBox('SkinningCheckBox', label='Skinning')", "self.skinning_checkbox = cmds.checkBox(label='Skinning: bake and remove source animation')")
    native = native.replace("cmds.showWindow(self.window_name)", "cmds.button(label='Bind existing joints to meshes', command=self.show_bind_ui)\n        cmds.showWindow(self.window_name)")
    native = native.replace("cmds.checkBox('SkinningCheckBox', query=True, value=True)", "cmds.checkBox(self.skinning_checkbox, query=True, value=True)")
    write(PKG / 'native_ui.py', '# All original declarations retained; subclass overrides unsafe business callback.\n' + native)
    engine_tree = ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[])
    for function in engine_tree.body:
        if isinstance(function, ast.FunctionDef):
            function.body.append(ast.parse('return created_objects').body[0])
    engine = ast.unparse(engine_tree)
    engine = engine.replace('skinning_enabled=False):', 'skinning_enabled=False, frame_range=None):')
    engine = engine.replace('created_objects = []', 'created_objects = []\n    constraints = []', 1)
    engine = engine.replace('created_objects.append(joint_name)', 'created_objects.append(joint_name)\n        constraints.append(parent_constraint)', 1)
    engine = engine.replace('for transform_node in selected_transforms:\n            cmds.select(clear=True)\n            joint_name = \'{}_joint\'.format(transform_node.split(\'|\')[-1])', 'for transform_node, joint_name, parent_constraint in zip(selected_transforms, created_objects, constraints):\n            cmds.select(clear=True)')
    engine = engine.replace('time=(cmds.playbackOptions(query=True, min=True), cmds.playbackOptions(query=True, max=True))', 'time=frame_range')
    engine = engine.replace('cmds.cutKey(transform_node, clear=True)', 'cmds.delete(parent_constraint)\n            cmds.currentTime(frame_range[0])\n            cmds.cutKey(transform_node, clear=True)')
    engine = engine.replace('cmds.skinCluster(toSelectedBones=True, bindMethod=0)', 'cmds.skinCluster(joint_name, transform_node, toSelectedBones=True, bindMethod=0)')
    ast.parse(engine)
    write(PKG / 'engine.py', '# Complete original three proxy functions, explicit actual-name/bake fixes.\n' + engine)
    write(PKG / 'catalog.json', json.dumps({'files': files, 'proxy_functions': [n.name for n in tree.body if isinstance(n, ast.FunctionDef)], 'ui_methods': [n.name for c in tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)], 'license': 'User prototypes; no independent license file supplied'}, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', '*.py -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'batch_skin_bind').replace('RootMotionBakeTool', 'BatchSkinBindTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'batch_skin_bind', 'registration': {'module': 'batch_skin_bind', 'class_name': 'BatchSkinBindTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in files], 'dependencies': ['Maya cmds, standard skinCluster/bake/constraint commands; PyMel no longer required'], 'acceptance_required': True, 'change_summary': 'Both full original prototypes archived. Complete joint/locator/cube proxy functions and original UI with explicit batch joint/mesh capture. Whole-batch preflight, actual created-name mapping, independent baked proxy joints, explicit source animation removal, new skinClusters/sets and Undo/environment restoration.', 'verification_limitations': ['Real Maya full GUI/production rigs and simulation/animated parents not_run', 'Skinned proxy transfer restricted to unbound polygon meshes with unit static scale/shear and no animated ancestors', 'Source skinning deliberately removes ALL source transform animation keys; explicit allow_source_key_removal required; no automatic rollback on later execution failures', 'Existing skinClusters/locked or referenced targets rejected; does not add influences or copy skin weights', 'ParentConstraint transfers translation/rotation, not source scale; all original proxy set names retained with Maya collision suffixes']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'original_files': len(files), 'proxy_functions': 3}))


if __name__ == '__main__':
    main()
