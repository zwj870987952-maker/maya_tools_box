import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    tool = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
    pkg = Path(sys.modules[tool.__class__.__module__].__file__).parent
else:
    from maya_toolkit.tools.w_retarget_tool import WRetargetTool
    tool = WRetargetTool()
    pkg = Path(sys.modules[tool.__class__.__module__].__file__).parent
mod = sys.modules[tool.__class__.__module__]


class OfflineChecks(unittest.TestCase):
    def test_archive_and_full_method_engine_coverage(self):
        catalog = json.loads((pkg / 'catalog.json').read_text(encoding='utf-8'))
        archive = pkg / catalog['files'][0]['archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), catalog['files'][0]['sha256'])
        native = ast.parse((pkg / 'native_ui.py').read_text(encoding='utf-8'))
        cls = next(n for n in native.body if isinstance(n, ast.ClassDef))
        self.assertEqual(catalog['original_methods'], [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in native.body))
        engine = (pkg / 'engine.py').read_text(encoding='utf-8')
        for operation in ('multMatrix', 'decomposeMatrix', 'parentConstraint', 'pointConstraint', 'worldInverseMatrix[0]', 'outputRotate', 'outputTranslate'):
            self.assertIn(operation, engine)
        self.assertIn('value=valueAttr', engine)
        self.assertEqual(tool.to_mcp_tool()['name'], 'w_retarget_tool')

    def test_argument_and_file_guards(self):
        for arguments in ({}, {'pairs': []}, {'pairs': [{'source': 's', 'target': 't'}], 'end_frame': 0}, {'pairs': [{'source': 's', 'target': 't'}], 'start_frame': True}, {'action': 'export', 'exports': [], 'bake': 1}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                mod.normalize(**arguments)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'new.fbx'
            self.assertEqual(mod.output_path(str(path)), path.resolve())
            path.write_bytes(b'keep')
            with self.assertRaises(ValueError):
                mod.output_path(str(path))
            self.assertEqual(path.read_bytes(), b'keep')
            for name in ('CON.fbx', 'name:stream.fbx', 'other.txt'):
                with self.assertRaises(ValueError):
                    mod.output_path(str(Path(folder) / name))


if __name__ == '__main__':
    unittest.main()
