from pathlib import Path
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_fbx_auto_import as t
from engine_toolkit.tools.ue_fbx_auto_import import config as c

class Obj:
    def __init__(self): self.props = {}; self.imported_object_paths = []
    def set_editor_property(self, key, value): self.props[key] = value
    def reset_to_default(self): self.anim_sequence_import_data = Obj()
class Skeleton: pass
class Tests(unittest.TestCase):
    def setup_files(self, d):
        fbx = Path(d) / 'Walk.FBX'; fbx.write_bytes(b'test fbx content')
        data = {'fbx_files': [str(fbx)], 'destination_content_path': '/Game/NewAnims', 'skeleton_path': '/Game/Hero_Skeleton'}
        config = Path(d) / 'config.json'; config.write_text(json.dumps(data))
        return fbx, data, config
    def fake(self, calls, existing=False, fail=False):
        def importer(tasks):
            calls.extend(tasks)
            for task in tasks: task.imported_object_paths = [] if fail else [task.props['destination_path'] + '/Walk.Walk']
        return types.SimpleNamespace(Skeleton=Skeleton, load_asset=lambda p: Skeleton(),
            EditorAssetLibrary=types.SimpleNamespace(does_directory_exist=lambda p: existing), FbxImportUI=Obj,
            FBXImportType=types.SimpleNamespace(FBXIT_ANIMATION=1), FBXAnimationLengthImportType=types.SimpleNamespace(FBXALIT_EXPORTED_TIME=2),
            AssetImportTask=Obj, FbxFactory=Obj, AssetToolsHelpers=types.SimpleNamespace(get_asset_tools=lambda: types.SimpleNamespace(import_asset_tasks=importer)))
    def test_config_detection_exclusive_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d)
            root = Path(d) / 'Project/Content/Hero/anim'; root.mkdir(parents=True)
            skeleton = root.parent / 'Hero_Skeleton.uasset'; skeleton.write_bytes(b'asset')
            (root.parent / 'Skeleton.txt').write_text('not an asset')
            anim, skel = c.find_target_paths(Path(d) / 'Project')
            self.assertEqual(anim, [str(root)]); self.assertEqual(skel, [str(skeleton)])
            self.assertEqual(c.convert_to_ue_path(skeleton), '/Game/Hero/Hero_Skeleton')
            with self.assertRaises(ValueError): c.convert_to_ue_path(fbx)
            out = Path(d) / 'Configs'; first = c.generate_config(data, out); old = Path(first['output']).read_bytes()
            second = c.generate_config(data, out); self.assertNotEqual(first['output'], second['output'])
            self.assertEqual(Path(first['output']).read_bytes(), old); self.assertEqual(c.load_config(second['output'])['config'], data)
    def test_dryrun_wholepreflight_native_success_and_failure(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d); calls = []
            with patch.object(t, '_unreal', return_value=self.fake(calls)):
                self.assertTrue(t.run(action='import', config_paths=[str(config)])['success']); self.assertEqual(calls, [])
                self.assertFalse(t.run(dry_run=False, action='import', config_paths=[str(config)])['success']); self.assertEqual(calls, [])
                result = t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config)])
                self.assertTrue(result['success'], result); task = calls[0]
                self.assertEqual(task.props['destination_path'], '/Game/NewAnims/Walk')
                self.assertFalse(task.props['replace_existing']); self.assertTrue(task.props['save'])
                self.assertFalse(task.props['options'].props['import_mesh']); self.assertFalse(task.props['options'].props['import_materials'])
            with patch.object(t, '_unreal', return_value=self.fake([], existing=True)):
                self.assertFalse(t.run(action='import', config_paths=[str(config)])['success'])
            with patch.object(t, '_unreal', return_value=self.fake([], fail=True)):
                self.assertFalse(t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config)])['success'])
            self.assertEqual(fbx.read_bytes(), b'test fbx content')
    def test_invalid_last_config_no_import(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d); bad = Path(d) / 'bad.json'; bad.write_text('{}'); calls=[]
            with patch.object(t, '_unreal', return_value=self.fake(calls)):
                self.assertFalse(t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config), str(bad)])['success']); self.assertEqual(calls, [])
if __name__ == '__main__': unittest.main()
