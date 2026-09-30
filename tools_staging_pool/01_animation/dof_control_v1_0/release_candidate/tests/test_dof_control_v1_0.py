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
    from maya_toolkit.tools.dof_control_v1_0 import DofControlTool
    TOOL = DofControlTool()
from maya_toolkit.tools.dof_control_v1_0.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.dof_control_v1_0'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_complete_mel_and_resources(self):
        catalog = TOOL.execute(action='inventory').data
        self.assertEqual(2, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        original = (PACKAGE / 'upstream/dofControl.mel').read_text(encoding='utf-8-sig')
        adapted = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        # All original graph/transform steps kept, only safe setup/name/argument adaptations.
        for text in ('polyCube -sx 1 -sy 1 -sz 1 -ch off', '.translateZ', '.input1', '.input2', '.outputX', '.focusDistance', '.scaleZ', '.fStop', '.sx', '.sy', 'parent -r', '"reverse"', '"addDoubleLinear"'):
            self.assertIn(text, original)
            self.assertIn(text, adapted)
        self.assertIn('require_active()', adapted)
        self.assertNotIn('connectAttr -f', adapted)
        self.assertNotIn('ls -sl -ca -dag', adapted)
        self.assertIn('$cubeShape[0] + ".primaryVisibility"', adapted)

    def test_contract_and_lazy_inventory(self):
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('dof_control_v1_0', TOOL.to_mcp_tool()['name'])
        for args in ({'action': 'bad'}, {'template': 1}, {'cameras': ['a', 'a']}, {'cameras': ['a.vtx[0]']}, {'record_ids': 'x'}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
