import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    tool = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.base_overrig_v9_0 import BaseOverRigTool
    tool = BaseOverRigTool()
module = sys.modules[tool.__class__.__module__]
PKG = Path(module.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_full_distribution_and_public_signature_coverage(self):
        c = module.catalog()
        self.assertEqual(10, len(c['files']))
        self.assertEqual(308, c['declaration_count'])
        self.assertEqual(307, len(c['procedures']))
        self.assertEqual(57, len(c['public']))
        self.assertEqual([], c['top_level_lines'])
        self.assertFalse(c['vendor_modified'])
        for row in c['files']:
            self.assertEqual(hashlib.sha256((PKG / 'vendor' / row['path']).read_bytes()).hexdigest(), row['sha256'])
        for name in ('assign_jiggle_bone_soft', 'execute_overlap_command', 'apply_rebike_3_or_more_object_to_IK', 'base_OverRig_scripts'):
            self.assertIn(name, c['public'])
        self.assertEqual(sorted(c['public']), tool.parameters_schema['properties']['procedure']['enum'])
        self.assertIn('You may not', (PKG / 'vendor/License.txt').read_text(encoding='utf-8-sig'))

    def test_typed_call_guards_no_mel_injection(self):
        good = module.normalize(action='call', procedure='scale_selected_lock_or_joint', arguments=[1.5], objects=['locator'])
        self.assertEqual('scale_selected_lock_or_joint(1.5);', good['command'])
        arguments = [dict(action='call', procedure='eval', arguments=['delete -all']), dict(action='call', procedure='scale_selected_lock_or_joint', arguments=[True]), dict(action='call', procedure='scale_selected_lock_or_joint', arguments=[0]), dict(action='call', procedure='scale_selected_lock_or_joint', arguments=[float('nan')]), dict(action='call', procedure='barn_sel_set_member', arguments=['mySet;delete -all']), dict(action='call', procedure='barn_sel_set_member', arguments=['mySet`']), dict(action='inspect', objects=['obj']), dict(action='call', procedure='apply_Fast_Bake', arguments=[1])]
        for p in arguments:
            with self.assertRaises(ValueError):
                module.normalize(**p)
        self.assertEqual('{"node"}', module.literal(['node'], 'string[]'))


if __name__ == '__main__':
    unittest.main()
