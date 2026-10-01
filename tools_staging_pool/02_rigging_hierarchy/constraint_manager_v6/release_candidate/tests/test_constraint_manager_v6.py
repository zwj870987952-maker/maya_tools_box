import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.constraint_manager_v6 import ConstraintManagerTool
    TOOL = ConstraintManagerTool()
mod = sys.modules[TOOL.__class__.__module__]
PKG = Path(mod.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_original_sources_and_every_ui_method_retained_no_auto_run(self):
        c = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(2, len(c['files']))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
        native = ast.parse((PKG/'native_ui.py').read_text(encoding='utf-8'))
        classes = {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)] for n in native.body if isinstance(n, ast.ClassDef)}
        original = next(v['classes'] for v in c['declarations'].values() if v['classes'])
        self.assertEqual(original, classes)
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in native.body))
        rebuild = ast.parse((PKG/'native_rebuild.py').read_text(encoding='utf-8'))
        functions = [n.name for n in rebuild.body if isinstance(n, ast.FunctionDef)]
        self.assertEqual(next(v['functions'] for v in c['declarations'].values() if not v['classes']), functions)
        self.assertEqual(8, len(functions))
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in rebuild.body))
        self.assertEqual('constraint_manager_v6', TOOL.to_mcp_tool()['name'])

    def test_weight_and_list_contracts(self):
        for params in ({'action': 'bad'}, {'action': 'weights'}, {'action': 'weights', 'selected_weights': ['x.w'], 'value': float('nan')}, {'action': 'weights', 'selected_weights': ['x.w', 'x.w']}, {'action': 'weights', 'selected_weights': ['x.w'], 'keyframe': 1}, {'action': 'save_list', 'list_name': '../bad', 'items': []}, {'action': 'export_snapshot'}, {'action': 'save_list', 'list_name': 'good', 'items': [{'text': 'x', 'color': 'red'}]}):
            with self.assertRaises(ValueError):
                mod.normalize(**params)
        good = mod.normalize(action='save_list', list_name='saved', items=[{'text': '|a|b.nodeW0', 'color': '#ff0000', 'constraint_node': '|a|constraint', 'weight_attrs': ['|a|constraint.nodeW0']}])
        self.assertEqual('|a|b.nodeW0', good['items'][0]['text'])


if __name__ == '__main__':
    unittest.main()
