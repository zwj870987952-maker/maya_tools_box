import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.camera_f_fix import CameraFFixTool
    TOOL=CameraFFixTool()
from maya_toolkit.tools.camera_f_fix.tool import normalize
import maya_toolkit.tools.camera_f_fix as package


class Checks(unittest.TestCase):
    def test_original_complete_and_contract(self):
        pkg=Path(package.__file__).parent
        data=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))
        raw=(pkg/'upstream'/data['source']).read_bytes()
        self.assertEqual(data['sha256'],hashlib.sha256(raw).hexdigest())
        self.assertIn(b'ResetTransformations;',raw)
        self.assertIn(b'1 1 1',raw)
        self.assertEqual('camera_f_fix',TOOL.to_mcp_tool()['name'])

    def test_strict_types_preferences_omitted(self):
        p=normalize({})
        self.assertEqual('persp',p['camera'])
        self.assertFalse(p['preserve_selection'])
        self.assertNotIn('reset_rotation',p)
        for args in ({'camera':''},{'action':'frame'},{'reset_rotation':1},{'reset_scale':None},{'preserve_selection':'yes'},{'translate':[1,1,1]}):
            with self.assertRaises(ValueError):
                normalize(args)


if __name__=='__main__':
    unittest.main()
