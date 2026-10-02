import hashlib
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_bone_exporter as tool

class Mesh:
    def __init__(self, name, path=None, bones=None):
        self.name, self.path, self.bones = name, path or '/Game/' + name, bones or ['root', '腕']
    def get_name(self): return self.name
    def get_path_name(self): return self.path

class Modifier:
    def set_skeletal_mesh(self, mesh): self.mesh = mesh; return True
    def get_all_bone_names(self): return self.mesh.bones
    def commit_skeleton_to_skeletal_mesh(self): raise AssertionError('Asset mutation forbidden')

class Tests(unittest.TestCase):
    def fake(self, directory, assets):
        return types.SimpleNamespace(SkeletalMesh=Mesh, SkeletonModifier=Modifier,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: assets),
            Paths=types.SimpleNamespace(project_dir=lambda: directory), load_asset=lambda path: None)
    def test_preview_export_and_preexisting_protection(self):
        with tempfile.TemporaryDirectory() as d, patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Hero')])):
            result = tool.run(action='export')
            self.assertTrue(result['success']); self.assertEqual(list(Path(d).iterdir()), [])
            result = tool.run(dry_run=False, action='export')
            self.assertTrue(result['success'], result)
            target = Path(d) / 'Hero_BoneList.txt'; data = target.read_bytes()
            self.assertEqual(data, 'root\n腕\n'.encode())
            self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertEqual(target.read_bytes(), data)
    def test_entire_batch_preflight_and_path_collision(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d) / 'Bad_BoneList.txt'; old.write_bytes(b'preserve')
            with patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Good'), Mesh('Bad')])):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertEqual([p.name for p in Path(d).iterdir()], ['Bad_BoneList.txt'])
            with patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Hero', '/Game/A/Hero'), Mesh('Hero', '/Game/B/Hero')])):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
    def test_failure_cleans_owned_file_and_preserves_racing_existing(self):
        with tempfile.TemporaryDirectory() as d, patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('A'), Mesh('B')])):
            open_original = Path.open
            def raced(path, mode='r', *a, **kw):
                if mode == 'xb' and path.name == 'B_BoneList.txt':
                    with open_original(path, 'wb') as stream: stream.write(b'other writer')
                return open_original(path, mode, *a, **kw)
            with patch.object(Path, 'open', raced):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertFalse((Path(d) / 'A_BoneList.txt').exists())
            self.assertEqual((Path(d) / 'B_BoneList.txt').read_bytes(), b'other writer')

if __name__ == '__main__': unittest.main()
