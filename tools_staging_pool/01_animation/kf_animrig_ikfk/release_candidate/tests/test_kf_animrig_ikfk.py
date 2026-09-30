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
    from maya_toolkit.tools.kf_animrig_ikfk import KFAnimRigTool
    TOOL = KFAnimRigTool()
from maya_toolkit.tools.kf_animrig_ikfk.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.kf_animrig_ikfk'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_source_resources_full_mel_procedures_and_guards(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(4, len(catalog['raw_files']))
        for item in catalog['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        source = (PACKAGE / 'native.mel').read_text(encoding='utf-8')
        declarations = re.findall(r'global proc (\w+)\(', source)
        self.assertTrue(all('mtbKF_' + p in declarations for p in catalog['source_procs']))
        self.assertEqual(7, len(catalog['source_procs']))
        self.assertIn('mtbKF_checkAttr', source)
        self.assertIn('mtbKF_delete($Dup)', source)
        self.assertIn('rebuildCurve -ch 1', source)
        self.assertNotRegex(source, r'\bdelete\s+\$')
        self.assertNotIn('mtbKF_matchIKtoFKTen(0)', source)

    def test_lazy_schema_and_mel_injection_rejection(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('kf_animrig_ikfk', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'action': 'bad'}, {'control': 'x; delete all;'}, {'control': 'a.tx'}, {'control': '|a'}, {'allow_reference_edits': 1}, {'start': True}, {'start': 3, 'end': 1}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
