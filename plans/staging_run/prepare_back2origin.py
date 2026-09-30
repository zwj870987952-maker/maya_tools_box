"""Keep original code/resources; generate complete native UI and algorithm modules."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/back2origin_v05_gaiv3'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/back2origin_v05_gaiv3'
SOURCE = UNIT / 'Back2Origin_v05_gaiv3.py'
HELPERS = ['calculate_ik_positions', 'calculate_other_positions', 'calculate_root_world_positions',
           'zero_out_root_control', 'reapply_ik_positions', 'reapply_other_positions',
           'reapply_root_world_positions', 'optimize_keyframes']
CONTROLS = ['back2OriginWindow', 'objectMenu', 'refreshNamespacesItem', 'rootControlField',
            'ikControlsField', 'pvControlsField', 'otherControlsField', 'globalControlField',
            'channelCheckBoxGrp', 'bakeFromTimesliderCheckBox', 'startFrameField', 'endFrameField', 'frameStepField']


def replacement(name, body):
    return ast.parse('def ' + name + '():\n    ' + body).body[0]


class AdaptUI(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value in CONTROLS:
            node.value = 'mtbB2O_' + node.value
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'menuItem':
            for keyword in node.keywords:
                if keyword.arg == 'command' and isinstance(keyword.value, ast.Constant):
                    text = keyword.value.value
                    if text in ('clear_all()', 'show_about()', 'show_contact()'):
                        keyword.value = ast.parse('lambda *_: ' + text, mode='eval').body
        return node


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    upstream = PACKAGE / 'upstream'
    upstream.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE, upstream / SOURCE.name)
    (upstream / '.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    original = SOURCE.read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    helper_tree = ast.Module(body=[ast.Import(names=[ast.alias(name='maya.cmds', asname='cmds')])] + [functions[name] for name in HELPERS], type_ignores=[])
    (PACKAGE / 'algorithms.py').write_text(ast.unparse(helper_tree) + '\n', encoding='utf-8', newline='\n')
    # Keep all original reverse frame loops, snapshots, xforms, keys and thinning.
    reverse = functions['return_to_root']
    body = next(node.body for node in reverse.body if isinstance(node, ast.Try))
    assignments = ast.parse("root_control = args['root_control']\nglobal_control = args['global_control']\nik_controls = args['ik_controls']\npv_controls = args['pv_controls']\nother_controls = args['other_controls']\nchannels = args['channels']\nstart_frame, end_frame = args['start'], args['end']").body
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'frame_step' for target in node.targets):
            node.value = ast.parse("args['frame_step']", mode='eval').body
    reverse.args = ast.parse('def reverse(args): pass').body[0].args
    reverse.name, reverse.body = 'reverse', assignments + body
    ast.fix_missing_locations(reverse)
    (PACKAGE / 'reverse.py').write_text('import maya.cmds as cmds\n\n' + ast.unparse(reverse) + '\n', encoding='utf-8', newline='\n')
    tree = ast.parse(original)
    replacements = {
        'run_root_motion_conversion': replacement('run_root_motion_conversion', "return bridge.dispatch('convert')"),
        'return_to_root': replacement('return_to_root', "return bridge.dispatch('reverse')"),
        'auto_identify_controllers': replacement('auto_identify_controllers', 'return bridge.identify()'),
        'fill_controller_fields': replacement('fill_controller_fields', 'return bridge.fill(None)'),
        'fill_by_namespace': ast.parse('def fill_by_namespace(namespace):\n    return bridge.fill(namespace)').body[0],
        'save_script_to_maya_default': replacement('save_script_to_maya_default', "raise RuntimeError('候选不自动安装或复制脚本；请使用晋级清单')")}
    output = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            continue  # Two import-time installer/UI calls only.
        if isinstance(node, ast.FunctionDef):
            if node.name in HELPERS:
                continue
            node = replacements.get(node.name, node)
            # Native Maya callbacks may pass an extra value.
            if not node.args.args and node.args.vararg is None:
                node.args.vararg = ast.arg(arg='_callback_args')
            if node.name == 'refresh_namespaces_menu':
                node.body = [statement for statement in node.body if not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and isinstance(statement.value.func, ast.Attribute) and statement.value.func.attr == 'refresh')]
        output.append(node)
    output.insert(0, ast.parse('from . import ui as bridge\nfrom .algorithms import ' + ', '.join(HELPERS)).body[0])
    output.insert(1, ast.parse('from .algorithms import ' + ', '.join(HELPERS)).body[0])
    adapted_tree = AdaptUI().visit(ast.Module(body=output, type_ignores=[]))
    ast.fix_missing_locations(adapted_tree)
    adapted = ast.unparse(adapted_tree) + '\n'
    (PACKAGE / 'native_ui.py').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'back2origin_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile=SOURCE.name, tofile='native_ui.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'back2origin_v05_gaiv3', 'raw_files': [{'path': 'upstream/' + SOURCE.name, 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}],
               'original_functions': list(functions), 'algorithm_functions': HELPERS, 'reverse_algorithm': 'reverse.py', 'ui_controls': CONTROLS,
               'source_license': 'User-provided enhanced script; no standalone redistribution license found',
               'behavior': ['Full original eight helpers and reverse loops preserved', 'Global optional for convert; mandatory for reverse', 'Original absolute frame modulus thinning and X/Z-only root transfer', 'World root values assigned to global local channels; reverse replaces root values, not additive inverse'],
               'changes': ['Import-time file copy and window removed; installer explicitly disabled', 'Original native UI preserved in module namespace with callable callbacks', 'Read-only UUID/long-path preflight and standard Undo dispatch', 'Single writer runtime state restored finally', 'Discovery avoids ambiguous root/global and namespace mixing; stale fields cleared']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'back2origin_v05_gaiv3', 'registration': {'module': 'back2origin_v05_gaiv3', 'class_name': 'Back2OriginTool'},
                   'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)],
                   'resources': ['catalog.json', 'upstream/' + SOURCE.name], 'dependencies': ['Maya Python3', 'Native Maya GUI for window', 'Existing maya_toolkit framework/core Undo'],
                   'source': '../' + SOURCE.name, 'change_summary': 'Complete original forward helpers, reverse loops and native UI; no import-time installation, typed API, read-only scene/channel preflight, reliable Undo and runtime state restoration, unambiguous controller discovery.',
                   'verification_limitations': ['Real GUI and production rig acceptance pending', 'Nonidentity parents/global transforms and root motion game-engine suitability require human review', 'X/Z local and world-space conventions preserved; reverse is not a general mathematical inverse', 'Original thinning can remove existing translate keys on unselected axes'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': len(functions), 'helpers': len(HELPERS), 'source_preserved': SOURCE.read_bytes() == (upstream / SOURCE.name).read_bytes()}))


if __name__ == '__main__':
    main()
