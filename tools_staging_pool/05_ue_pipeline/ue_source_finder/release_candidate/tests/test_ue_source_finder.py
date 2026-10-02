from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_source_finder as t
class Asset:
    def __init__(self, folder, name, sources): self.folder, self.name, self.sources = folder, name, sources
    def get_name(self): return self.name
    def get_path_name(self): return self.folder + '/' + self.name + '.' + self.name
    def get_editor_property(self, name): return types.SimpleNamespace(extract_filenames=lambda: self.sources)
class Tests(unittest.TestCase):
    def fake(self, assets): return types.SimpleNamespace(EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda:assets), log=lambda s:None)
    def test_distinct_folder_copy_and_all_reports_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); src=root/'old.fbx'; src.write_bytes(b'FBX original bytes'); src2=root/'extra.fbx'; src2.write_bytes(b'second source')
            assets = [Asset('/Game/A/Hero', 'Body', [str(src),str(src2)]), Asset('/Game/B/Hero','Body',[str(src)]), Asset('/Game/A/Hero','Missing',[str(root/'missing.fbx')])]
            with patch.object(t, '_unreal', return_value=self.fake(assets)):
                args = dict(action='copy_sources', output_dir=d, session_name='Batch', source_mode='all')
                before = sorted(p.name for p in root.iterdir()); self.assertTrue(t.run(**args)['success']); self.assertEqual(sorted(p.name for p in root.iterdir()), before)
                result = t.run(dry_run=False, **args); self.assertTrue(result['success'], result)
                data = result['data']; self.assertEqual(data['total_success'], 3); self.assertEqual(data['total_missing'], 1)
                self.assertEqual((root/'Batch/Game/A/Hero/Body.fbx').read_bytes(), src.read_bytes())
                self.assertEqual((root/'Batch/Game/B/Hero/Body.fbx').read_bytes(), src.read_bytes())
                self.assertEqual((root/'Batch/Game/A/Hero/Body_src2.fbx').read_bytes(), b'second source')
                self.assertTrue((root/'Batch/summary.json').is_file()); self.assertTrue(any('名单' in p for p in data['logs']))
                self.assertTrue(any('源文件缺失' in p for p in data['logs']))
                self.assertFalse(t.run(dry_run=False, **args)['success'])
            self.assertEqual(src.read_bytes(), b'FBX original bytes')
    def test_failed_copy_report_and_first_source_default(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'raw.fbx'; src.write_bytes(b'bytes')
            with patch.object(t, '_unreal', return_value=self.fake([Asset('/Game/X','Hero',[str(src),str(src)])])):
                args=dict(action='copy_sources',output_dir=d,session_name='Batch')
                preview=t.run(**args); self.assertEqual(len(preview['data']['rows'][0]['copies']),1)
                with patch.object(t.shutil, 'copyfileobj', side_effect=OSError('copy failed')):
                    result=t.run(dry_run=False, **args); self.assertFalse(result['success']); self.assertEqual(result['data']['total_failed'],1)
                self.assertFalse((Path(d)/'Batch/Game/X/Hero.fbx').exists()); self.assertEqual(src.read_bytes(),b'bytes')
    def test_no_relative_guess_and_path_escape_refusal(self):
        with tempfile.TemporaryDirectory() as d, patch.object(t, '_unreal', return_value=self.fake([Asset('/Game/X','Hero',['../raw.fbx'])])):
            result=t.run(output_dir=d,session_name='Batch'); self.assertTrue(result['success']); self.assertEqual(result['data']['rows'][0]['copies'],[])
            self.assertFalse(t.run(output_dir=d,session_name='../escape')['success'])
if __name__ == '__main__': unittest.main()
