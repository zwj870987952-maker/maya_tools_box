import ast
import hashlib
from pathlib import Path
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.brs_loc_transfer import LocatorTransferTool
    TOOL = LocatorTransferTool()
from maya_toolkit.tools.brs_loc_transfer.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.brs_loc_transfer'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_complete_source_and_no_executable_import(self):
        data = TOOL.execute(action='inventory').data
        self.assertEqual(17, len(data['original_functions']))
        for row in data['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        source = (PACKAGE / 'legacy.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertTrue(set(data['original_functions']).issubset(functions))
        self.assertNotIn('urllib', source)
        self.assertNotIn('cycleCheck', source)
        self.assertNotIn('exec(', source)
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in tree.body))
        self.assertIn('preserveOutsideKeys=True', source)
        self.assertIn('timeMultiple=1.0', source)
        self.assertIn("_bridge.dispatch('redirect')", source)

    def test_helpers_preserve_original_algorithms(self):
        raw = ast.parse((PACKAGE / 'upstream/BRSLocTransfer.py').read_text(encoding='utf-8-sig'))
        adapted = ast.parse((PACKAGE / 'legacy.py').read_text(encoding='utf-8'))
        old = {n.name: n for n in raw.body if isinstance(n, ast.FunctionDef)}
        new = {n.name: n for n in adapted.body if isinstance(n, ast.FunctionDef)}
        for name in TOOL.execute(action='inventory').data['algorithm_helpers']:
            new[name].body = new[name].body[1:]
            self.assertEqual(ast.dump(old[name], include_attributes=False), ast.dump(new[name], include_attributes=False))

    def test_contract_schema_and_no_maya_inventory(self):
        for args in [{'constrain': 1}, {'action': 'unknown'}, {'objects': ['a', 'a']}, {'objects': ['a.x']}, {'action': 'apply', 'translate': False, 'rotate': False}, {'bad': 1}]:
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('brs_loc_transfer', TOOL.to_mcp_tool()['name'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
