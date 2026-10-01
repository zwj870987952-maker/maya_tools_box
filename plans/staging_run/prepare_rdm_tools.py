"""Complete Python 3 port with explicit legacy script entry points and resources."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from lib2to3.refactor import RefactoringTool

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/rdm_tools_v2'
RAW = UNIT / 'RdMToolsV2'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/rdm_tools_v2'
PREFIX = 'maya_toolkit.tools.rdm_tools_v2.native'
CONVERTER = RefactoringTool(['lib2to3.fixes.fix_' + name for name in ('print', 'long', 'xrange', 'dict', 'except', 'raise', 'has_key', 'unicode', 'zip', 'map', 'filter', 'itertools')])


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


def constant_assignment(node):
    if not isinstance(node, ast.Assign):
        return False
    try:
        ast.literal_eval(node.value)
        return True
    except (ValueError, TypeError):
        return isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name) and node.value.value.id in ('QtWidgets', 'QtGui')


class Port(ast.NodeTransformer):
    def visit_Import(self, node):
        items = []
        for alias in node.names:
            if alias.name == 'RmdTools_Path':
                items.append(ast.ImportFrom(module=PREFIX, names=[ast.alias(name='RmdTools_Path', asname=alias.asname)], level=0))
            elif alias.name == 'RdMToolsV2' or alias.name.startswith('RdMToolsV2.'):
                if '.' in alias.name:
                    items.append(ast.Import(names=[ast.alias(name=PREFIX + '.' + alias.name, asname=alias.asname)]))
                items.append(ast.ImportFrom(module=PREFIX, names=[ast.alias(name='RdMToolsV2', asname=None)], level=0))
            else:
                items.append(ast.Import(names=[alias]))
        return items

    def visit_ImportFrom(self, node):
        if node.module and node.module.startswith('RdMToolsV2'):
            node.module = PREFIX + '.' + node.module
        elif node.module in ('PySide2', 'shiboken2'):
            node.module = 'maya_toolkit.tools.rdm_tools_v2.qt_compat'
        elif node.module in ('PySide2.QtWidgets', 'PySide2.QtGui'):
            kind = node.module.split('.')[1]
            return [ast.ImportFrom(module='maya_toolkit.tools.rdm_tools_v2.qt_compat', names=[ast.alias(name=kind)], level=0)] + [ast.Assign(targets=[ast.Name(id=n.asname or n.name, ctx=ast.Store())], value=ast.Attribute(value=ast.Name(id=kind, ctx=ast.Load()), attr=n.name, ctx=ast.Load())) for n in node.names]
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == 'reload':
            node.func.id = 'legacy_reload'
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in ('cmds', 'mc') and node.func.attr == 'internalVar':
            node.func = ast.Name(id='bundled_scripts_dir', ctx=ast.Load())
        return node

    def visit_FunctionDef(self, node):
        for i, default in enumerate(node.args.defaults):
            if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == 'maya_main_window':
                node.args.defaults[i] = ast.Constant(value=None)
                node.body.insert(0, ast.parse('if parent is None:\n    parent = maya_main_window()').body[0])
        return self.generic_visit(node)


def main():
    rows, modules, missing = [], {}, []
    for source in sorted(UNIT.rglob('*')):
        if not source.is_file() or 'release_candidate' in source.parts or source.name == '.gitattributes':
            continue
        relative = source.relative_to(UNIT)
        vendor = PKG / 'vendor' / relative
        if source.suffix == '.py':
            vendor = vendor.with_suffix('.py.original')
        vendor.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, vendor)
        rows.append({'path': relative.as_posix(), 'vendor': vendor.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
        if RAW not in source.parents:
            continue
        target = PKG / 'native/RdMToolsV2' / source.relative_to(RAW)
        if source.suffix != '.py':
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            continue
        text = source.read_bytes().decode('utf-8-sig').expandtabs(8)
        if source.name == 'AddRemoveJoints.py':
            text = text.replace('from maya import cmds', 'from maya import cmds, mel').replace('cmds.skinCluster=(e = True, lw=True, ai = joints, SkinCluster)', 'cmds.skinCluster(SkinCluster, e=True, lw=True, ai=joints)')
        try:
            converted = str(CONVERTER.refactor_string(text.rstrip() + '\n', str(source)))
        except Exception:
            print('Source parse failure:', source)
            raise
        tree = ast.parse(converted)
        name = 'RdMToolsV2.' + source.relative_to(RAW).with_suffix('').as_posix().replace('/', '.')
        if name.endswith('.__init__'):
            name = name[:-9]
        definitions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                definitions.append({'name': node.name, 'parameters': [a.arg for a in node.args.args], 'required': len(node.args.args) - len(node.args.defaults), 'vararg': node.args.vararg.arg if node.args.vararg else None, 'defaults': [ast.unparse(v) for v in node.args.defaults]})
        classes = {node.name: [m.name for m in node.body if isinstance(m, ast.FunctionDef)] for node in tree.body if isinstance(node, ast.ClassDef)}
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('RdMToolsV2'):
                imports.append(node.module)
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names if a.name.startswith('RdMToolsV2'))
        # Unused PyMel imports do not impose an unnecessary dependency.
        if not any(isinstance(n, ast.Name) and n.id == 'pm' and isinstance(n.ctx, ast.Load) for n in ast.walk(tree)):
            tree.body = [n for n in tree.body if not (isinstance(n, ast.Import) and any(a.name == 'pymel.core' for a in n.names))]
        tree = Port().visit(tree)
        ast.fix_missing_locations(tree)
        safe, deferred = [], []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)) or isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                safe.append(node)
            elif constant_assignment(node):
                safe.append(node)
            else:
                deferred.append(node)
        module_info = {'functions': definitions, 'classes': classes, 'imports': sorted(set(imports)), 'deferred_statements': len(deferred), 'pymel_required': 'pymel.core' in ast.unparse(ast.Module(body=safe, type_ignores=[])), 'original': source.relative_to(UNIT).as_posix()}
        modules[name] = module_info
        # Original reload reset every module-level constant before script logic.
        replay = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)) and not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
        replay = [statement for node in replay for statement in (node.body if isinstance(node, ast.If) and ast.unparse(node.test) == "__name__ == '__main__'" else [node])]
        executable = ast.unparse(ast.Module(body=replay, type_ignores=[]))
        if source.name == 'CurveToJson.py':
            executable = executable.replace("open('C:Users/Usuario/Desktop/Foot.json', mode='w')", 'checked_output()')
        if source.name == 'UItoPY.py':
            executable = executable.replace("open(myPY, 'w')", 'checked_output()').replace('pyside2uic.compileUi(myUI,', 'pyside2uic.compileUi(explicit_ui_input(),')
        head = 'from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input\n'
        result = head + ast.unparse(ast.Module(body=safe, type_ignores=[]))
        result += '\n\n\ndef run_script():\n    exec(compile(' + repr(executable) + ', __file__, "exec"), globals())\n'
        # Two original hardcoded development exports become explicit, exclusive outputs.
        if source.name == 'CurveToJson.py':
            result = result.replace("open('C:Users/Usuario/Desktop/Foot.json', mode='w')", 'checked_output()')
        if source.name == 'UItoPY.py':
            result = result.replace("open(myPY, 'w')", 'checked_output()').replace('pyside2uic.compileUi(myUI,', 'pyside2uic.compileUi(explicit_ui_input(),')
        # Main ShowUI always reads only its bundled tree, not user scripts.
        ast.parse(result)
        write(target, result)
    for name, info in modules.items():
        for dependency in info['imports']:
            if dependency not in modules:
                missing.append({'module': name, 'import': dependency})
    write(PKG / 'native/__init__.py', '')
    write(PKG / 'native/RmdTools_Path.py', 'from pathlib import Path\n_RdMlocpath = str(Path(__file__).resolve().parent)')
    write(PKG / 'catalog.json', json.dumps({'files': rows, 'modules': modules, 'missing_original_imports': missing, 'license': 'Source ShowUI cites EULA https://www.eulatemplate.com/live.php?token=Izv1fodFF2LI2iq8rhySiedABF6e3rti ; link inaccessible in this run. Original attribution and bytes retained; no public redistribution or license assumption.', 'vendor_modified': False}, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', 'RdMToolsV2/** -text\n*.doc -text\n*.jpg -text\n*.png -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'rdm_tools_v2').replace('RootMotionBakeTool', 'RdmToolsTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'rdm_tools_v2', 'registration': {'module': 'rdm_tools_v2', 'class_name': 'RdmToolsTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [row['path'] for row in rows], 'dependencies': ['Maya cmds/MEL, Qt6 or Qt5', 'PyMel needed by original AutoRig/Facial and other modules; absent in current isolated Maya2025', 'pyside2uic required only for original optional UItoPY developer export', 'Legacy RdMTools optional button is a separate unbundled original dependency'], 'acceptance_required': True, 'change_summary': 'Complete original distribution, docs/UI/icons, all Python functions/classes and legacy script logic preserved in Python3 candidate; import-time scene actions deferred to explicit run_script, full original UI redirected to bundled resources, Qt compatibility and isolated namespaced imports, typed function/script API with read-only inspect/dry, Undo/context restoration and exclusive explicit outputs. No installer/user scripts write.', 'verification_limitations': ['Real Qt GUI, complete auto rig/facial/skin/IKFK workflows and production scenes not_run', 'PyMel absent in isolated Maya2025; dependent modules are not claimed to execute', 'Legacy optional package/template resources missing in original distribution remain explicitly reported', 'EULA link inaccessible, original provenance retained without inferring redistribution rights', 'Original hardcoded rig naming and broad hierarchy/deletion/callback behaviors require explicit backup-scene scope']}
    write(RC / 'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(rows), 'modules': len(modules), 'functions': sum(len(i['functions']) for i in modules.values()), 'classes': sum(len(i['classes']) for i in modules.values()), 'missing': missing}, ensure_ascii=True))


if __name__ == '__main__':
    main()
