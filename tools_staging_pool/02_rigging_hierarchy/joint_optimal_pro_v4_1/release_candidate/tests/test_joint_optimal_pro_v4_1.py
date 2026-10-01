import hashlib
from pathlib import Path
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    tool = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.joint_optimal_pro_v4_1 import JointOptimalProTool
    tool = JointOptimalProTool()
module = sys.modules[tool.__class__.__module__]
PKG = Path(module.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_complete_original_and_every_signature(self):
        c = module.catalog()
        self.assertEqual(6, len(c['files']))
        self.assertEqual(144, c['declaration_count'])
        self.assertEqual(143, len(c['procedures']))
        self.assertEqual(142, len(c['public']))
        self.assertEqual([], c['top_level_lines'])
        self.assertFalse(c['vendor_modified'])
        self.assertNotIn('find', c['public'])
        self.assertIn('JOPA_skeleton_tools_menue', c['public'])
        self.assertEqual(sorted(c['public']), tool.parameters_schema['properties']['procedure']['enum'])
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG / 'vendor' / row['path']).read_bytes()).hexdigest())
        self.assertIn('You may not', (PKG / 'vendor/License.txt').read_text())
        for name, definition in c['public'].items():
            for parameter in definition['parameters']:
                self.assertIn(parameter['type'].replace('[]', ''), ('int', 'float', 'string', 'vector', 'matrix'))
        self.assertTrue(any(p['ui_references'] for p in c['public'].values()))

    def test_strict_types_vectors_matrices_and_injection_rejection(self):
        self.assertEqual('<<1.0,2.0,3.0>>', module.literal([1, 2, 3], 'vector'))
        self.assertEqual('{<<1.0,2.0,3.0>>}', module.literal([[1, 2, 3]], 'vector[]'))
        self.assertIn(';', module.literal([[1, 0, 0, 0]] * 4, 'matrix'))
        color = 'JOPA_4_1_cc20e95399a3b6da44eb78e45451d764'
        radius = 'JOPA_4_1_92de112c5c170c44ad9daf4d48b1acdd'
        self.assertEqual(radius + '(2.0);', module.normalize(action='call', procedure=radius, arguments=[2])['command'])
        for kwargs in ({'procedure': 'find', 'arguments': ['x']}, {'procedure': color, 'arguments': [32]}, {'procedure': color, 'arguments': [True]}, {'procedure': radius, 'arguments': [0]}, {'procedure': radius, 'arguments': [float('inf')]}, {'procedure': radius, 'arguments': [1], 'allow_native_scope': 1}, {'procedure': radius, 'arguments': [1], 'objects': ['x', 'x']}):
            with self.assertRaises(ValueError):
                module.normalize(action='call', **kwargs)
        for value in ('x;delete -all', 'x`', 'x"', 'x\\', 'x\n'):
            with self.assertRaises(ValueError):
                module.literal(value, 'string')
        with self.assertRaises(ValueError):
            module.literal([1, float('nan'), 2], 'vector')
        with self.assertRaises(ValueError):
            module.literal([[1] * 4] * 3, 'matrix')
        with self.assertRaises(ValueError):
            module.normalize(action='inspect', objects=['x'])


if __name__ == '__main__':
    unittest.main()
