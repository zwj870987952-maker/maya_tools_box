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
    from maya_toolkit.tools.relationship_tools_v19 import RelationshipToolsTool
    tool = RelationshipToolsTool()
module = sys.modules[tool.__class__.__module__]
PKG = Path(module.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_all50_original_methods_and_source_sha_preserved_no_autostart(self):
        c = json.loads((PKG / 'catalog.json').read_text())
        self.assertEqual(50, len(c['methods']))
        self.assertEqual(c['sha256'], hashlib.sha256((PKG / 'vendor/Relationship Tools_v19.py.original').read_bytes()).hexdigest())
        tree = ast.parse((PKG / 'original_logic.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(set(c['methods']), {n.name for n in cls.body if isinstance(n, ast.FunctionDef)})
        self.assertTrue(all(isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef)) for n in tree.body))
        self.assertEqual(set(module.ACTIONS), set(tool.parameters_schema['properties']['action']['enum']))

    def test_bounds_exclusive_ranges_flags_and_file_parameters(self):
        self.assertEqual([1, 5], module.normalize(action='align', frame_range=[1, 5])['frame_range'])
        for p in (dict(action='eval'), dict(action='align', frame_range=[5, 1]), dict(action='align', frame_range=[1, 1]), dict(action='align', step=True), dict(action='align', step=0), dict(action='align', translate=False, rotate=False), dict(action='align', objects=['a', 'a']), dict(action='export_pose'), dict(action='inspect', objects=['a'])):
            with self.assertRaises(ValueError):
                module.normalize(**p)


if __name__ == '__main__':
    unittest.main()
