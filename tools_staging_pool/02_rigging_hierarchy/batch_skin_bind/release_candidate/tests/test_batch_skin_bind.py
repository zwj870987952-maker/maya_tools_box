import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    tool = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.batch_skin_bind import BatchSkinBindTool
    tool = BatchSkinBindTool()
mod = sys.modules[tool.__class__.__module__]
PKG = Path(mod.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_all_originals_and_full_functions_preserved(self):
        c = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(2, len(c['files']))
        for row in c['files']:
            self.assertEqual(hashlib.sha256((PKG / row['archive']).read_bytes()).hexdigest(), row['sha256'])
        tree = ast.parse((PKG / 'engine.py').read_text(encoding='utf-8'))
        self.assertEqual(c['proxy_functions'], [n.name for n in tree.body if isinstance(n, ast.FunctionDef)])
        native = ast.parse((PKG / 'native_ui.py').read_text(encoding='utf-8'))
        cls = next(n for n in native.body if isinstance(n, ast.ClassDef))
        self.assertEqual(c['ui_methods'], [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in native.body))
        self.assertEqual('batch_skin_bind', tool.to_mcp_tool()['name'])

    def test_full_batch_and_destructive_branch_guards(self):
        for arguments in ({'action': 'bind'}, {'action': 'bind', 'pairs': []}, {'action': 'bind', 'pairs': [{'joint': 'j', 'mesh': 'm'}], 'objects': ['m']}, {'skinning': True}, {'proxy_type': 'cube', 'skinning': True, 'allow_source_key_removal': True}, {'allow_source_key_removal': True}, {'skinning': True, 'allow_source_key_removal': True, 'start_frame': 2, 'end_frame': 1}, {'skinning': True, 'allow_source_key_removal': True, 'start_frame': float('nan'), 'end_frame': 5}):
            with self.assertRaises(ValueError):
                mod.normalize(**arguments)
        self.assertEqual('bind', mod.normalize(action='bind', pairs=[{'joint': 'j', 'mesh': 'm'}])['action'])


if __name__ == '__main__':
    unittest.main()
