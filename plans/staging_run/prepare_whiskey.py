import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/eblabs_whiskey'
SOURCE = UNIT / 'Whiskey'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/eblabs_whiskey'
WRITES = {'setAttr', 'setKeyframe', 'cutKey', 'pasteKey', 'scaleKey', 'snapKey', 'keyTangent', 'keyframe', 'filterCurve', 'disconnectAttr', 'connectAttr', 'delete', 'animLayer', 'autoKeyframe'}


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for file in sorted(p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        target = PACKAGE / 'upstream' / file.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    for path, value in ((UNIT / '.gitattributes', 'Whiskey/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(value, encoding='utf-8', newline='\n')
    original = (SOURCE / 'eblabs_hub/Whiskey/scripts/WhiskeyPro.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    catalog_classes, methods, wrapped = [], [], []
    adapted_nodes = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            aliases = {a.name for a in node.names}
            if 'maya.cmds' in aliases or 'maya.mel' in aliases:
                continue
        if isinstance(node, ast.ImportFrom) and node.module == 'data':
            continue
        if isinstance(node, ast.ClassDef):
            catalog_classes.append(node.name)
            for method in node.body:
                if not isinstance(method, ast.FunctionDef):
                    if node.name == 'Functions' and isinstance(method, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'prefsFilepath' for t in method.targets):
                        method.value = ast.Constant('session://whiskey/preferences')
                    continue
                methods.append({'class': node.name, 'method': method.name, 'signature': ast.unparse(method.args), 'line': method.lineno})
                if node.name == 'Prefs' and method.name in ('getPrefsPath', 'loadPrefs', 'savePrefs', 'writeDataToFile', 'loadDataFromFile'):
                    bodies = {'getPrefsPath': "return 'session://whiskey/preferences'", 'loadPrefs': 'return _r.load_preferences(cls)', 'savePrefs': 'return _r.save_preferences(cls)', 'writeDataToFile': 'return _r.write_json(filePath, dictionary)', 'loadDataFromFile': 'return _r.read_json(filename)'}
                    method.body = ast.parse(bodies[method.name]).body
                elif node.name == 'Functions' and method.name in ('suspendUI', 'suspendUI_wrapped'):
                    method.body = ast.parse('return None  # Standard Undo stays enabled; do not alter pane/isolation.').body
                elif node.name == 'Functions' and method.name in ('writeDataToFile', 'loadDataFromFile'):
                    method.body = ast.parse('return _r.write_json(filePath, dictionary)' if method.name == 'writeDataToFile' else 'return _r.read_json(filename)').body
                elif node.name == 'Functions' and method.name == 'setProfilesData':
                    # Existing workflow uses memory, same native operation remains.
                    pass
                if node.name == 'Functions' and method.name == 'getBoundingBoxSize':
                    method.args.args.insert(0, ast.arg(arg='cls'))
                if node.name == 'slider_multiply':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Attribute) and item.attr in ('slider_realtime_layers', 'slider_realtime_finish_layers'):
                            item.attr = item.attr.replace('_layers', '_standard')
                if node.name == 'slider_tween' and method.name == 'collectData_layers':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'curveNode' for t in item.targets):
                            item.value = ast.parse('(cmds.keyframe(attribute, query=True, name=True) or [None])[0]', mode='eval').body
                if node.name == 'slider_tween' and method.name == 'slider_exec_layers':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr == 'setAttr':
                            replacement = ast.parse('cmds.keyframe(curveNode, edit=True, index=(index, index), valueChange=newValue)', mode='eval').body
                            item.func, item.args, item.keywords = replacement.func, replacement.args, replacement.keywords
                if method.name in ('collectData', 'collectData_layers', 'collectSnapshotData', 'smashBaker', 'cleanSubframeKeys', 'removeBoringKeys'):
                    for handler in ast.walk(method):
                        if isinstance(handler, ast.ExceptHandler) and handler.name:
                            handler.body.insert(0, ast.parse('_r.note_error(' + handler.name + ')').body[0])
                calls = [call for call in ast.walk(method) if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == 'cmds' and call.func.attr in WRITES and not any(k.arg in ('q', 'query') and isinstance(k.value, ast.Constant) and k.value.value for k in call.keywords)]
                if calls:
                    method.decorator_list.append(ast.parse("_r.native_operation('" + node.name + '.' + method.name + "')", mode='eval').body)
                    wrapped.append(node.name + '.' + method.name)
                # Rename only the native main window; preserve all widgets and business formulas.
                if node.name == 'window' and method.name == 'load':
                    for item in ast.walk(method):
                        if isinstance(item, ast.Constant) and item.value == 'whisKEY_Pro':
                            item.value = 'mtbWK_whisKEY_Pro'
        adapted_nodes.append(node)
    header = ast.parse('from .proxy import cmds, mel\nfrom .metadata import PackageData\nfrom . import runtime as _r').body
    text = ast.unparse(ast.fix_missing_locations(ast.Module(body=header + adapted_nodes, type_ignores=[]))) + '\n'
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    (PACKAGE / 'native.py').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'eblabs_whiskey_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/WhiskeyPro.py', tofile='native.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'eblabs_whiskey', 'classes': catalog_classes, 'methods': methods, 'wrapped_scene_methods': wrapped, 'raw_files': resources, 'license': 'Eric Bates / EB Labs proprietary supplied package; private local preparation, no independent redistribution grant. Original license managers unchanged/unused by standalone source adapter.', 'changes': ['Complete original native Python classes/methods and formulas', 'Metadata read from bundled JSON instead of missing hybrid compiled PackageData', 'Maya command adapter for scope/reference guards', 'Standard callback Undo/results and finally; remove native long-lived nested chunks/global Undo-off/isolation', 'Session preferences; explicit JSON import/export for persistence, no original prefs path writes', 'Complete native window and all slider/widget types']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'eblabs_whiskey', 'registration': {'module': 'eblabs_whiskey', 'class_name': 'WhiskeyTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya native cmds/API2; actual GUI for original complete panel', 'Existing framework/core Undo', 'Bundled original metadata and session preference preset'], 'source': '../Whiskey/eblabs_hub/Whiskey/scripts/WhiskeyPro.py', 'change_summary': 'Complete original Whiskey Pro suite/UI/resources, self-contained source metadata, explicit standard API and guarded native callbacks, Undo/finally and session preference import/export.', 'verification_limitations': ['Full native GUI/drag/pinning/profile/layer/production rig pending', 'Each GUI callback uses a standard Undo chunk; drag event grouping differs from original long-lived chunk', 'Original full-suite key/curve/dependency overwrite behavior must be verified in backups', 'Bundled compiled Hub installers/metadata loaders are archived, never executed', 'Private copyrighted resources; no public publication'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'classes': len(catalog_classes), 'methods': len(methods), 'wrapped': len(wrapped), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
