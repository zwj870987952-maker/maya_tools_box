import hashlib
import json
from pathlib import Path
import runpy
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.segment_scale_fix import SegmentScaleFixTool
    TOOL = SegmentScaleFixTool()
from maya_toolkit.tools.segment_scale_fix.tool import normalize
import maya_toolkit.tools.segment_scale_fix as package


class Checks(unittest.TestCase):
    def test_original_complete_and_schema(self):
        pkg = Path(package.__file__).parent
        c = json.loads((pkg / 'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(2, len(c['files']))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((pkg / 'vendor' / row['path']).read_bytes()).hexdigest())
        self.assertEqual('segment_scale_fix', TOOL.to_mcp_tool()['name'])
        self.assertFalse(TOOL.parameters_schema['additionalProperties'])
        self.assertEqual('disable', normalize()['action'])

    def test_input_types(self):
        for kwargs in ({'objects': []}, {'objects': ['j', 'j']}, {'objects': 'j'}, {'action': 'enable'}, {'action': 'inspect', 'objects': ['j']}, {'recursive': True}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main()
