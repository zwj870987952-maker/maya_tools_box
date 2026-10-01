import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.skin_info_and_super_connect import SkinInfoSuperConnectTool
    TOOL = SkinInfoSuperConnectTool()
import maya_toolkit.tools.skin_info_and_super_connect as package
from maya_toolkit.tools.skin_info_and_super_connect.tool import normalize
PKG = Path(package.__file__).parent


class Checks(unittest.TestCase):
    def test_all_resources_methods_procedures_and_callbacks(self):
        c = json.loads((PKG / 'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(7, len(c['files']))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG/'vendor'/row['path']).read_bytes()).hexdigest())
        for suite, data in c['suites'].items():
            original = (PKG/(suite+'_legacy.mel')).read_text(encoding='utf8')
            ui = (PKG/(suite+'_ui.mel')).read_text(encoding='utf8')
            for row in data['procedures']:
                self.assertIn('scpstg_'+suite+'_legacy_'+row['name'], original)
                if not row['parameters']:
                    self.assertIn('scpstg_'+suite+'_'+row['name']+'()', ui)
            self.assertNotIn('fopen', ui)
            self.assertNotIn('deformerWeights', ui)
            self.assertNotIn('eval `', ui)
        tree = ast.parse((PKG/'timal_original.py').read_text(encoding='utf8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(c['timal_methods'], [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        self.assertTrue(all(isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef)) for n in tree.body))

    def test_types_and_protocol(self):
        for p in ({'action': 'wrong'}, {'formats': []}, {'formats': ['exe']}, {'channels': []}, {'channels': ['tx','tx']}, {'objects': []}, {'objects': ['a','a']}, {'delete_history': True}, {'create_skin': 1}, {'action':'import','formats':['xml','json']}, {'convention':'timal','formats':['json']}):
            with self.assertRaises(ValueError):
                normalize(**p)
        self.assertEqual('skin_info_and_super_connect', TOOL.to_mcp_tool()['name'])


if __name__ == '__main__':
    unittest.main()
