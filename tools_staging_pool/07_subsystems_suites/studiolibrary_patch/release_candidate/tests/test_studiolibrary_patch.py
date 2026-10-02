import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.studiolibrary_patch import StudioLibraryPatchTool
    tool=StudioLibraryPatchTool()
from maya_toolkit.tools.studiolibrary_patch import guards,theme_io,history_safety
class Checks(unittest.TestCase):
    def test_pure_preflight_and_theme_exact_restore(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('studiolibrary',sys.modules)
        with self.assertRaises(ValueError):guards.frames(1,float('inf'),1)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'css').mkdir();p=root/'css/default.css';p.write_bytes(b'original\r\nCSS')
            row=theme_io.install(str(root));self.assertEqual(Path(row['backup']).read_bytes(),b'original\r\nCSS');theme_io.install(str(root))
            p.write_bytes(b'foreign')
            with self.assertRaises(ValueError):theme_io.uninstall(str(root))
            self.assertEqual(p.read_bytes(),b'foreign');p.write_bytes(theme_io.CSS.read_bytes());theme_io.uninstall(str(root));self.assertEqual(p.read_bytes(),b'original\r\nCSS')
    def test_history_payload_failure_and_success(self):
        source=Path(history_safety.__file__).parent/'native/studiolibrary_wanimation/history.py';spec=importlib.util.spec_from_file_location('offline_history',source);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);history_safety.install(h)
        class Item:EXTENSION='.wpose'
        with tempfile.TemporaryDirectory() as td:
            asset=Path(td)/'x.wpose';asset.mkdir();(asset/'payload').write_bytes(b'old');(asset/'.history/v0001').mkdir(parents=True);(asset/'.history/v0001/data').write_bytes(b'version')
            row=h.stage_existing_asset(str(asset),Item());(asset/'payload').write_bytes(b'broken');self.assertTrue(h.restore_stage(row));self.assertEqual((asset/'payload').read_bytes(),b'old');self.assertEqual((asset/'.history/v0001/data').read_bytes(),b'version')
            row=h.stage_existing_asset(str(asset),Item());(asset/'payload').write_bytes(b'new');version=h.commit_stage(row,str(asset));self.assertEqual(Path(version).name,'v0002');self.assertEqual((Path(version)/'payload').read_bytes(),b'old');self.assertEqual((asset/'.history/v0001/data').read_bytes(),b'version');self.assertEqual((asset/'payload').read_bytes(),b'new')
if __name__=='__main__':unittest.main()
