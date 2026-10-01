import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.physics_tools import PhysicsToolsTool
    TOOL = PhysicsToolsTool()
from maya_toolkit.tools.physics_tools.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.physics_tools'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_entire_mel_procedure_resource_and_private_entry(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(109, len(catalog['procedures']))
        raw = catalog['raw_files'][0]
        self.assertEqual(raw['sha256'], hashlib.sha256((PACKAGE / raw['path']).read_bytes()).hexdigest())
        source = (PACKAGE / 'native.mel').read_text(encoding='utf-8')
        self.assertEqual(catalog['native_sha256'], hashlib.sha256(source.encode()).hexdigest())
        for p in catalog['procedures']:
            self.assertIn('global proc mtkPTC_Native_' + p + '()', source)
            self.assertIn('global proc mtkPTC_' + p + '()', source)
        self.assertNotIn('diskCache -ea -da;', source)
        self.assertNotIn('PhysicsToolsWin();\n//---', source)
        self.assertIn('Autor: IURI MONTEIRO', source)
        self.assertIn('modified by k31', source)
        self.assertIn('mtkPTC_Delete', source)
        self.assertIn('mtkPTC_CreateJiggle', source)

    def test_strict_schema_and_lazy_import(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('physics_tools', TOOL.to_mcp_tool()['name'])
        for args in ({'action': 'invoke'}, {'procedure': 'unknown'}, {'weight': True}, {'overlap': float('nan')}, {'frame_range': [1, 0]}, {'frame_range': [1, 3.5]}, {'targets': ['a', 'a']}, {'allow_reference_edits': 1}, {'unknown': True}):
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertEqual('BakeVariosControladores', normalize(action='invoke', procedure='BakeVariosControladores')['procedure'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
