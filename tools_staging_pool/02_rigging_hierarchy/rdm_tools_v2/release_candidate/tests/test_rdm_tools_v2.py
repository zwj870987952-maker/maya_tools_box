import ast
import hashlib
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    tool = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.rdm_tools_v2 import RdmToolsTool
    tool = RdmToolsTool()
module = sys.modules[tool.__class__.__module__]
PKG = Path(module.__file__).parent
from maya_toolkit.tools.rdm_tools_v2 import support


class OfflineChecks(unittest.TestCase):
    def test_full_resources_original_functions_classes_and_deferred_actions(self):
        c = module.catalog()
        self.assertEqual(164, len(c['files']))
        self.assertEqual(86, len(c['modules']))
        self.assertEqual(126, sum(len(i['functions']) for i in c['modules'].values()))
        self.assertEqual(3, sum(len(i['classes']) for i in c['modules'].values()))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG / row['vendor']).read_bytes()).hexdigest())
        for name, info in c['modules'].items():
            path = PKG / 'native' / (name.replace('.', '/') + '.py')
            if not path.is_file():
                path = PKG / 'native' / name.replace('.', '/') / '__init__.py'
            tree = ast.parse(path.read_text(encoding='utf-8'))
            functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
            self.assertTrue({p['name'] for p in info['functions']} <= functions, name)
            self.assertIn('run_script', functions)
            for cls, methods in info['classes'].items():
                actual = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
                self.assertTrue(set(methods) <= {n.name for n in actual.body if isinstance(n, ast.FunctionDef)})
            for statement in tree.body:
                if isinstance(statement, ast.Assign):
                    self.assertFalse(any(isinstance(n, ast.Call) for n in ast.walk(statement)))
                self.assertNotIsInstance(statement, (ast.For, ast.While, ast.With, ast.If, ast.Try))
        ui = ET.parse(PKG / 'native/RdMToolsV2/RdMV2.ui')
        self.assertGreater(len(ui.findall('.//widget')), 150)
        self.assertNotIn('RdMToolsV2.run_RdMTools', tool.parameters_schema['properties']['module']['enum'])

    def test_explicit_function_signature_json_and_export_no_overwrite(self):
        for p in (dict(action='call', module='os', function='system'), dict(action='script', module='RdMToolsV2.run_RdMTools'), dict(action='call', module='RdMToolsV2.RiggingTools.Curves.CurveColors', function='colorShape', arguments={'unknown': 1}), dict(action='call', module='RdMToolsV2.RiggingTools.Curves.CurveColors', function='colorShape', arguments={'Color': float('nan')})):
            with self.assertRaises(ValueError):
                module.normalize(**p)
        with self.assertRaises(ValueError):
            module.safe_json('x;delete -all')
        with tempfile.TemporaryDirectory() as folder:
            out = str(Path(folder) / 'curves.json')
            with support.export_context({'output_path': out}):
                with support.checked_output() as stream:
                    stream.write('retained')
                with self.assertRaises(ValueError):
                    support.checked_output()
            self.assertEqual('retained', Path(out).read_text())
            with self.assertRaises(RuntimeError):
                support.checked_output()


if __name__ == '__main__':
    unittest.main()
