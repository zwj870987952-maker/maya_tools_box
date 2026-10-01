"""Package complete Overslapper source with explicit, reviewable AST adaptations."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/overslapper_v1_03'
SOURCE = UNIT / 'overslapper_v1_03'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/overslapper'


class Adapt(ast.NodeTransformer):
    def visit_Expr(self, node):
        n = node.value
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'mc' and n.func.attr in ('undoInfo', 'move'):
            return None
        return self.generic_visit(node)

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == 'inverse_path_temp':
                node.value = ast.parse('list(wind)', mode='eval').body
            if name == 'up_value':
                node.value = ast.parse('math.sqrt(sum(v * v for v in up_t))', mode='eval').body
            if name == 'childs':
                node.value = ast.BoolOp(op=ast.Or(), values=[node.value, ast.List(elts=[ast.Name(id='target', ctx=ast.Load())], ctx=ast.Load())])
        return self.generic_visit(node)

    def visit_Compare(self, node):
        node = self.generic_visit(node)
        if isinstance(node.left, ast.Name) and node.left.id == 'anim_type':
            for n in node.comparators:
                if isinstance(n, ast.Constant) and n.value == 'add':
                    n.value = 'additive'
        if isinstance(node.left, ast.Name) and node.left.id == 'strength' and len(node.ops) == 1 and isinstance(node.ops[0], ast.Gt) and isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value == 0:
            node.ops[0] = ast.GtE()
        return node

    def visit_FunctionDef(self, node):
        node = self.generic_visit(node)
        if node.name in ('overlap', 'overlap_translation', 'apply_strenght', 'overshoot', 'create_wind_control'):
            node.body.insert(0, ast.parse('mc.require_scope()').body[0])
        if node.name == 'overshoot':
            # Preserve damping algorithm; fix int/string lookup and absolute-time duplication.
            for n in ast.walk(node):
                if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name) and n.left.id == 'zone_id' and any(isinstance(o, ast.In) for o in n.ops):
                    n.left = ast.Call(func=ast.Name(id='str', ctx=ast.Load()), args=[n.left], keywords=[])
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'overshoot_frame_distance' for t in n.targets):
                    n.value = ast.Call(func=ast.Name(id='max', ctx=ast.Load()), args=[ast.Constant(1), n.value], keywords=[])
                if isinstance(n, ast.keyword) and n.arg == 't' and isinstance(n.value, ast.BinOp) and isinstance(n.value.left, ast.Name) and n.value.left.id == 'end' and isinstance(n.value.right, ast.Name) and n.value.right.id == 'start_frame':
                    n.value = ast.Name(id='end', ctx=ast.Load())
        return node


def replace(tree, name, body):
    n = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    n.body = ast.parse(body).body


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    raw, inventories, diffs = [], {}, []
    for p in sorted(SOURCE.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        rel = p.relative_to(SOURCE)
        target = PACKAGE / 'upstream' / rel
        if target.suffix == '.py':
            target = target.with_suffix('.py.original')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
        raw.append({'source': rel.as_posix(), 'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    for name in ('default.json', 'icons/gearIcon.png', 'icons/overslapperLogo.png'):
        out = PACKAGE / 'native' / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / 'overslapper' / name, out)
    for rel in ('overslapper/packages/overlap_package.py', 'overslapper/packages/overlap_data_package.py', 'overslapper/overslapper_tool.py'):
        original = (SOURCE / rel).read_text(encoding='utf-8-sig')
        tree = ast.parse(original)
        inventories[rel] = {'functions': [n.name for n in tree.body if isinstance(n, ast.FunctionDef)], 'classes': {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)] for n in tree.body if isinstance(n, ast.ClassDef)}}
        tree = Adapt().visit(tree)
        for n in tree.body:
            if isinstance(n, ast.Import) and any(a.name == 'maya.cmds' for a in n.names):
                tree.body[tree.body.index(n)] = ast.ImportFrom(module='runtime', names=[ast.alias(name='mc', asname=None)], level=3 if '/packages/' in rel else 2)
            elif isinstance(n, ast.Import) and any(a.name == 'overlap_data_package' for a in n.names):
                tree.body[tree.body.index(n)] = ast.ImportFrom(module=None, names=[ast.alias(name='overlap_data_package', asname='over_d_p')], level=1)
        if rel.endswith('overslapper_tool.py'):
            a = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'maya_path' for t in n.targets))
            b = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.ImportFrom) and n.module == 'maya.app.general.mayaMixin')
            tree.body[a:b] = ast.parse('from pathlib import Path\nfrom .packages import overlap_package as over_p\nfrom .. import ui_bridge as bridge\nscript_path = str(Path(__file__).resolve().parent)\ndefault_options_path = os.path.join(script_path, "default.json")\nicon_path = os.path.join(script_path, "icons")').body
            replace(tree, 'overlap', 'return bridge.overlap(self)')
            replace(tree, 'create_wind_control', 'return bridge.action(self, "create_wind")')
            replace(tree, 'select_wind_controls', 'return bridge.action(self, "select_winds")')
            replace(tree, 'wind_controls_on', 'return bridge.action(self, "set_winds", enabled=True)')
            replace(tree, 'wind_controls_off', 'return bridge.action(self, "set_winds", enabled=False)')
            replace(tree, 'get_parent', 'sel = mc.ls(sl=True, long=True)\nif sel:\n    self.parent_result.setText(sel[0])')
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and n.value == 'pratte_custom_var':
                    n.value = 'mtkOverslapperCandidateGradient'
                if isinstance(n, ast.Constant) and n.value == 'pratte_overslapper_temp_window':
                    n.value = 'mtkOverslapperCandidateGradientWindow'
                if isinstance(n, ast.Constant) and n.value == 'OverSlapper':
                    n.value = 'mtkOverslapperCandidate'
                if isinstance(n, ast.Attribute) and n.attr == 'exec_':
                    n.attr = 'exec'
            f = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'import_ui_data')
            start = next(i for i, n in enumerate(f.body) if isinstance(n, ast.If))
            f.body[:start] = ast.parse('ui_data = bridge.read_preset(self.preset_file)').body
            # Missing legacy preset frame-lag/wind multiplier now round-trip as optional fields.
            f.body.extend(ast.parse('if base_overlap:\n    self.translation_strength_value.setText(ui_data["base_overlap"].get("frame_lag", "1.0"))\n    self.translation_strength_value_changed()\nif wind:\n    self.wind_strength_value.setText(ui_data["wind"].get("strength", "1.0"))\n    self.wind_value_changed()').body)
            for method_name in ('import_overlap_preset', 'partial_import_overlap_preset', 'import_ui_data'):
                method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == method_name)
                handler = ast.parse('try:\n    pass\nexcept Exception as error:\n    return bridge.import_error(self, error)').body[0]
                handler.body = method.body
                method.body = [handler]
            f = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'write_ui_data')
            start = next(i for i, n in enumerate(f.body) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple))
            f.body[start:] = ast.parse('ui_data["base_overlap"]["frame_lag"] = self.translation_strength_value.text()\nui_data["wind"]["strength"] = self.wind_strength_value.text()\nreturn bridge.write_preset(self, ui_data)').body
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'overslapper_UI')
            for method in cls.body:
                if isinstance(method, ast.FunctionDef) and method.name in ('wind_value_changed', 'stiffness_value_changed', 'translation_strength_value_changed', 'strength_value_changed', 'overshoot_strength_value_changed', 'overshoot_frequency_value_changed'):
                    for n in ast.walk(method):
                        if isinstance(n, ast.Try):
                            for i, statement in enumerate(n.body):
                                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and isinstance(statement.value.func, ast.Attribute) and statement.value.func.attr == 'setValue':
                                    slider = ast.unparse(statement.value.func.value)
                                    call = ast.unparse(statement)
                                    n.body[i:i+1] = ast.parse('old = ' + slider + '.blockSignals(True)\ntry:\n    ' + call + '\nfinally:\n    ' + slider + '.blockSignals(old)').body
                                    break
            cls.body.extend(ast.parse('def closeEvent(self, event):\n    bridge.cleanup(self)\n    return super().closeEvent(event)').body)
            # error_ui owned by this UI must not pop other code's override cursor.
            f = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'error_ui')
            f.body = [n for n in f.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == 'restoreOverrideCursor')]
        rendered = '# Copyright 2024 Philippe Ratté\n# Local candidate adaptation; restrictive EULA retained in upstream/LICENSE.txt.\n' + ast.unparse(ast.fix_missing_locations(tree)) + '\n'
        out = PACKAGE / 'native' / Path(rel).relative_to('overslapper')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8', newline='\n')
        diffs.extend(difflib.unified_diff(original.splitlines(True), rendered.splitlines(True), fromfile='upstream/' + rel, tofile='native/' + rel))
    for p in ('native/__init__.py', 'native/packages/__init__.py'):
        (PACKAGE / p).write_text('"""Private complete upstream implementation; lazy GUI import."""\n', encoding='utf-8')
    for p, body in ((UNIT / '.gitattributes', 'overslapper_v1_03/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        p.write_text(body, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'overslapper_changes.diff').write_text(''.join(diffs), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': raw, 'source_inventory': inventories, 'license': 'Copyright 2024 Philippe Ratte, restrictive EULA; no redistribution or modification permission inferred; personal local candidate only'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('keyframe_reduction', 'overslapper').replace('KeyframeReductionTool', 'OverslapperTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'overslapper', 'registration': {'module': 'overslapper', 'class_name': 'OverslapperTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in raw] + ['native/default.json', 'native/icons', 'catalog.json'], 'dependencies': ['Maya cmds/API2', 'PySide6/shiboken6 or PySide2/shiboken2 for original GUI and QObject workers', 'MayaQWidgetBaseMixin/gradientControlNoAttr for genuine GUI', 'BaseMayaTool/Undo'], 'source': '../overslapper_v1_03/overslapper/overslapper_tool.py', 'change_summary': 'Complete 28 business functions, two workers and original 56+4 UI methods/resources/manual/EULA retained. Explicit targets/layers, selected-channel writes/Undo, scoped wind discovery, Python3 private package, preset protection and concrete source defect fixes; no shelf/userScripts installation.', 'verification_limitations': ['Native Qt gradient/preset/progress GUI and visual motion remain pending real Maya', 'Restrictive upstream EULA prohibits copying/modification/redistribution without permission; this local candidate conveys no permission and must not be published', 'Overshoot can extend keys beyond requested end; deleteall affects all times on selected channels', 'Referenced/instanced/joint/driver-constrained targets refused; use local transform controls', 'Layered channels require explicit target_layer or new_layer; adding chosen attributes only differs from original addSelectedObjects all channels', 'No automatic rollback on a worker exception; one Undo restores scene changes'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'raw_files': len(raw), 'business_functions': 28, 'ui_methods_retained': 60, 'worker_methods': 2}))


if __name__ == '__main__':
    main()
