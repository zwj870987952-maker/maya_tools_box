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
    from maya_toolkit.tools.eblabs_screenspace import ScreenSpaceTool
    TOOL = ScreenSpaceTool()
from maya_toolkit.tools.eblabs_screenspace.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.eblabs_screenspace'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_full_resource_bytes_and_native_suite(self):
        catalog = TOOL.execute(action='inventory').data
        self.assertEqual(148, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        text = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        self.assertEqual(21, len(catalog['runtime_procedures']))
        for name in catalog['runtime_procedures']:
            self.assertIn(name + '(', text)
        for value in ('bufferCurve -overwrite true $inputObj', '$normalizer', 'mag $diffVector', 'copyKey -time', 'pasteKey -option', 'keyTangent -itt plateau', 'pointConstraint -sk', '.zDepth', '.planeAdjust', 'current_target()', 'require_active()'):
            self.assertIn(value, text)
        self.assertNotIn('namespace -set ":";', text)
        self.assertNotIn('paneLayout -e -m', text)

    def test_schema_lazy_inventory_and_types(self):
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('eblabs_screenspace', TOOL.to_mcp_tool()['name'])
        for args in ({'camera': 'cam.vtx[0]'}, {'objects': ['x', 'x']}, {'include_orientation': 1}, {'record_ids': 'x'}, {'action': 'bad'}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
