import hashlib
import json
from pathlib import Path
import runpy
import re
import sys
import tempfile
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.bb_tools import BBToolsTool
    TOOL = BBToolsTool()
mod = sys.modules[TOOL.__class__.__module__]
guard = __import__(mod.__package__+'.file_guard', fromlist=['file_guard'])
PKG = Path(mod.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_full_distribution_and_all_active_definitions(self):
        c = mod.catalog()
        self.assertEqual(81, len(c['files']))
        self.assertEqual(297, c['active_declarations'])
        self.assertEqual(31, len(c['native_files']))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG/'vendor'/row['path']).read_bytes()).hexdigest())
        for row in c['native_files']:
            self.assertGreaterEqual(row['native_procedures'], row['original_procedures'])
            self.assertEqual(row['sha256'], hashlib.sha256((PKG/'native'/row['path']).read_bytes()).hexdigest())
            for line in row['top_level_lines']:
                self.assertIsNone(re.match(r'\d+:\s*bbstg_\w+\s*(?:\(|;)', line), 'Top-level native UI call retained')
        self.assertEqual('bb_tools', TOOL.to_mcp_tool()['name'])
        main = (PKG/'native/bb_Tools.mel').read_text(encoding='utf-8')
        self.assertIn('-c $buttonArray[$i+1]', main)
        self.assertNotIn('source ', main)
        self.assertNotIn('os.remove', (PKG/'native/Script/bb_FixError.mel').read_text(encoding='utf-8'))

    def test_typed_argument_limits_and_mel_injection_rejected(self):
        for kwargs in ({'action': 'anything'}, {'procedure': 'bb_Tools'}, {'action': 'call', 'procedure': 'eval'}, {'action': 'call', 'procedure': 'wpRename_js_replaceHash', 'arguments': ['x;delete all;', 1]}, {'action': 'call', 'procedure': 'bb_CtrlTool_createShape', 'arguments': ['fake', 'ctrl']}, {'action': 'call', 'procedure': 'bb_CtrlTool_changeColorApply', 'arguments': ['node', 32]}, {'action': 'call', 'procedure': 'bb_attr_addAttr', 'arguments': ['node', ['n', 'Float', '1 -dv 9', '10', '1', '1']]}):
            with self.assertRaises(ValueError):
                mod.normalize(**kwargs)
        self.assertIn('bbstg_wpRename_js_replaceHash', mod.normalize(action='call', procedure='wpRename_js_replaceHash', arguments=['ctrl_###', 2])['command'])

    def test_copy_move_no_overwrite_shell_or_original_file_loss(self):
        with tempfile.TemporaryDirectory(prefix='bb_guard_test_') as root:
            p = Path(root)
            source = p/'source with spaces.bin'
            source.write_bytes(b'original bytes')
            target = p/'copy with spaces.bin'
            guard.system_request('copy "'+str(source)+'" "'+str(target)+'"')
            self.assertEqual(source.read_bytes(), target.read_bytes())
            with self.assertRaises(FileExistsError):
                guard.copy_file(source, target, move=True)
            self.assertTrue(source.is_file())
            moved = p/'moved.bin'
            guard.copy_file(source, moved, move=True)
            self.assertFalse(source.exists())
            self.assertEqual(b'original bytes', moved.read_bytes())
            for command in ('del "'+str(moved)+'"', 'copy "'+str(moved)+'" "'+str(p/'out')+'" & echo x'):
                with self.assertRaises(ValueError):
                    guard.system_request(command)
            with self.assertRaises(ValueError):
                guard.delete_scratch(moved)

    def test_only_settings_values_not_executable_qc_commands(self):
        self.assertEqual(('text', 'bb_QC_ctrlSuffixTF', '控制器'), guard.parse_qc_line('textField -e -tx "控制器" bb_QC_ctrlSuffixTF;'))
        self.assertEqual(('checkbox', 'bb_QC_renamePlyCB', 1), guard.parse_qc_line('checkBox -e -v 1 bb_QC_renamePlyCB;'))
        self.assertEqual(('append_list', 'bb_QC_ctrlAttrTSL', 'tx'), guard.parse_qc_line('textScrollList -e -append "tx" bb_QC_ctrlAttrTSL;'))
        for line in ('python("bad");', 'delete all;', 'checkBox -e -v 1 bb_QC_renamePlyCB; delete all;', 'textField -e -tx `delete all` bb_QC_ctrlSuffixTF;', 'textField -e -tx "x" otherUI;'):
            with self.assertRaises(ValueError):
                guard.parse_qc_line(line)

    def test_new_settings_reservation_and_weight_scratch_only_deletion(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'settings.bb'
            guard.reserve(path)
            with self.assertRaises(FileExistsError):
                guard.reserve(path)
            unrelated = Path(root)/'userSetup.py'
            unrelated.write_bytes(b'preserve personal startup')
            with self.assertRaises((ValueError, FileExistsError)):
                guard.reserve(unrelated)
            owned = guard.scratch()/'bb_skin2Deform_weight.xml'
            owned.write_bytes(b'temp')
            guard.delete_scratch(owned)
            self.assertFalse(owned.exists())
            with self.assertRaises(ValueError):
                guard.delete_scratch(unrelated)
            self.assertEqual(b'preserve personal startup', unrelated.read_bytes())


if __name__ == '__main__':
    unittest.main()
