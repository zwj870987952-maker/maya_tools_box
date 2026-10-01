"""Keep all 55 original functions/UI and adapt only checked bug/transaction boundaries."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/pose_matcher'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/pose_matcher'
SOURCE = UNIT / 'PoseMatcher.py'


def main():
    source = SOURCE.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    controls = ['skeletonAlignmentUI', 'mhRootField', 'dazRootField', 'dazNsField', 'jsonPathField', 'mhJointsList', 'dazJointsList']
    fnames = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]

    class Fix(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in controls:
                node.value = 'mtkPoseCandidate_' + node.value
            return node

    tree = Fix().visit(tree)
    body = []
    guarded = {'align_skeleton', 'align_parent_to_vector', 'resetTwist', 'rotate_joint_to_direction', 'build_mesh_from_numpy', 'assign_lambert_to_mesh', 'MergeMeshes', 'SplitMeshes', 'writeWithColor'}
    for node in tree.body:
        if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test):
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'g_lastPath' for t in node.targets):
            node.value = ast.Constant('')
        if isinstance(node, ast.FunctionDef):
            if node.name in guarded:
                index = 1 if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str) else 0
                node.body[index:index] = ast.parse('require_scope()').body
            if node.name == 'get_mesh_arrays_fast':
                code = ast.unparse(node).replace('mesh.getVertexNormals(angleWeighted=True, space=om.MSpace.kWorld)', '[[n.x, n.y, n.z] for n in mesh.getNormals(om.MSpace.kWorld)]')
                code = code.replace('mesh = om.MFnMesh(dag)', "cmds.dgeval(dag.fullPathName() + '.outMesh')\n    mesh = om.MFnMesh(dag)")
                node = ast.parse(code).body[0]
            if node.name == 'calculate_angle_3d':
                code = ast.unparse(node).replace('cos_theta = dot_product / (norm_a * norm_b)', "if norm_a <= 1e-12 or norm_b <= 1e-12:\n        raise ValueError('Zero-length direction')\n    cos_theta = np.clip(dot_product / (norm_a * norm_b), -1.0, 1.0)")
                node = ast.parse(code).body[0]
            if node.name == 'align_parent_to_vector':
                code = ast.unparse(node).replace('ordered_euler = new_rot_euler.reorderIt(order)', 'new_rot_euler.reorderIt(order)\n    ordered_euler = new_rot_euler')
                node = ast.parse(code).body[0]
            if node.name == 'align_skeleton':
                code = ast.unparse(node)
                needle = 'parent = cmds.listRelatives(daz_joint, parent=True, fullPath=True)'
                code = code.replace(needle, "if not daz_joint:\n            raise ValueError('Missing DAZ mapped joint: ' + daz_joint_name)\n        " + needle, 1)
                code = code.replace('joint_aim_map[parent[0]] =', "if not parent:\n            raise ValueError('Mapped target root has no parent')\n        joint_aim_map[parent[0]] =", 1)
                code += "\n    return {'processed_parents': sorted(processed_parents), 'errors': error_joints}\n"
                node = ast.parse(code).body[0]
            if node.name == 'find_joint_by_base_name':
                code = ast.unparse(node)
                start = code.index('    for joint in all_joints:')
                code = code[:start] + "    matches = [joint for joint in all_joints if get_base_name(joint) == base_name]\n    if len(matches) > 1:\n        raise ValueError('Duplicate base joint name: ' + base_name)\n    return matches[0] if matches else None\n"
                node = ast.parse(code).body[0]
            if node.name == 'auto_detect_namespace':
                code = ast.unparse(node).replace("ns = joint.split(':')[0]", "ns = joint.rsplit('|', 1)[-1].rsplit(':', 1)[0]")
                node = ast.parse(code).body[0]
            if node.name == 'ProcessUV':
                code = ast.unparse(node).replace('merged_uv = mesh1_uv.copy()', 'mesh1_uv = mesh1_uv.copy()\n    mesh2_uv = mesh2_uv.copy()\n    merged_uv = mesh1_uv.copy()').replace('uv1_range[3] - uv2_range[0]', 'uv1_range[2] - uv2_range[0]')
                node = ast.parse(code).body[0]
                for statement in node.body:
                    if isinstance(statement, ast.If) and isinstance(statement.test, ast.Call) and ast.unparse(statement.test.func) == 'is_overlap':
                        statement.body = statement.body[0].body
            if node.name in ('ProcessVertices', 'ProcessFaces'):
                code = ast.unparse(node).replace("cmds.warning('用户取消！')\n            break", "raise RuntimeError('Cancelled before publication')")
                if node.name == 'ProcessFaces':
                    code = code.replace('mesh2_f[i, 0] + mesh1_f.shape[0]', 'mesh2_f[i, 0] + int(mesh1_f[:, 0].max()) + 1')
                node = ast.parse(code).body[0]
            if node.name == 'build_mesh_from_numpy':
                # Keep complete original array→mesh algorithm for traceability, disallow unsafe raw creation.
                node.name = 'legacy_build_mesh_from_numpy'
                node.body.insert(0, ast.parse("raise RuntimeError('Use the undoable candidate mesh creation command')").body[0])
                body.append(node)
                node = ast.parse("def build_mesh_from_numpy(v, uv, vt, vn, name='newMesh'):\n    require_scope()\n    from .mesh_command import create\n    return create(v, uv, vt, vn, name)\n").body[0]
        body.append(node)
    header = ast.parse('from .runtime import require_scope\nfrom .progress import commands as progress_commands')
    # Keep original cmds UI/business operations, replace only progressWindow with owned state.
    class Progress(ast.NodeTransformer):
        def visit_Attribute(self, node):
            self.generic_visit(node)
            if isinstance(node.value, ast.Name) and node.value.id == 'cmds' and node.attr == 'progressWindow':
                node.value.id = 'progress_commands'
            return node
    tree.body = header.body + body
    tree = Progress().visit(tree)
    rendered = ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    PKG.mkdir(parents=True, exist_ok=True)
    (PKG / 'native.py').write_text(rendered, encoding='utf-8', newline='\n')
    (PKG / 'upstream').mkdir(exist_ok=True)
    shutil.copyfile(SOURCE, PKG / 'upstream/PoseMatcher.py.original')
    (PKG / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8')
    (UNIT / '.gitattributes').write_text('PoseMatcher.py -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'pose_matcher_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), rendered.splitlines(True), fromfile='upstream/PoseMatcher.py.original', tofile='native.py')), encoding='utf-8')
    catalog = dict(original_functions=fnames, private_controls=controls, raw_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), native_sha256=hashlib.sha256(rendered.encode()).hexdigest(), license='Source does not provide independent license/author notice; local personal candidate only')
    (PKG / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('keyframe_reduction', 'pose_matcher').replace('KeyframeReductionTool', 'PoseMatcherTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'pose_matcher', 'registration': {'module': 'pose_matcher', 'class_name': 'PoseMatcherTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': ['upstream/PoseMatcher.py.original', 'catalog.json'], 'dependencies': ['Maya cmds/API2', 'NumPy bundled in Maya', 'BaseMayaTool/Undo', 'Private undoable mesh command'], 'acceptance_required': True, 'change_summary': 'Full 55-function skeleton alignment and original native UI plus NumPy mesh merge/split pipelines retained; checked API, geometry/index repairs, undoable mesh construction and protected OBJ/JSON publication.', 'verification_limitations': ['Real native Maya GUI/production skeletons/skin rigs and topology/edit roundtrip pending', 'Original source lacks an independent distribution license; local preparation only', 'External output files cannot Maya Undo']}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'original_functions': len(fnames), 'raw_sha256': catalog['raw_sha256']}))


if __name__ == '__main__':
    main()
