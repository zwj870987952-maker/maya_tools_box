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
    from maya_toolkit.tools.fd_multi_space import MultiSpaceTool
    TOOL = MultiSpaceTool()
from maya_toolkit.tools.fd_multi_space.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.fd_multi_space'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_resources_and_two_modes(self):
        data = TOOL.inventory()
        self.assertEqual(4, len(data['raw_files']))
        for item in data['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        self.assertEqual(4, len(data['source_functions']['reference']))
        self.assertEqual(4, len(data['source_functions']['local']))
        text = (PACKAGE / 'runtime.py').read_text(encoding='utf-8')
        self.assertIn('maintainOffset=True', text)
        self.assertIn('centerPivots=True', text)
        self.assertNotIn('force=True', text)

    def test_schema_and_lazy_readonly(self):
        self.assertTrue(TOOL.validate().success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('fd_multi_space', TOOL.to_mcp_tool()['name'])
        for args in ({'attribute': 'bad.name'}, {'attribute': '1bad'}, {'driven': 'x.vtx[0]'}, {'allow_reference_edits': 1}, {'mode': 'bad'}, {'action': 'bad'}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
