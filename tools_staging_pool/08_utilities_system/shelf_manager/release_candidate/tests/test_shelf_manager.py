import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_shelf',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.shelf_manager import ShelfManagerTool
    tool=ShelfManagerTool()
from maya_toolkit.tools.shelf_manager import backend
class Checks(unittest.TestCase):
    def test_scoped_bilingual_duplicate_names_collision_backup_and_quarantine(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.shelf_manager.native',sys.modules)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'maya';en=root/'2025/prefs/shelves';zh=root/'2025/zh_CN/prefs/shelves';en.mkdir(parents=True);zh.mkdir(parents=True);output=Path(td)/'out';output.mkdir()
            a=en/'shelf_CustomTool.mel';a.write_text('global proc shelf_CustomTool() {}');a.with_suffix('.png').write_bytes(b'icon');b=zh/'shelf_CustomTool.mel';b.write_text('different content');(en/'shelf_Animation.mel').write_text('default')
            roots=[str(root)];rows=backend.scan(roots);self.assertEqual(len(rows),2);self.assertEqual({r['language'] for r in rows},{'zh','en'})
            with self.assertRaises(ValueError):backend.migration(roots,[str(a),str(b)],str(output))
            self.assertEqual(list(output.iterdir()),[])
            receipts=backend.migrate(backend.migration(roots,[str(a)],str(output)));self.assertEqual(len(receipts),2);self.assertTrue(a.is_file());target=output/a.name;old=target.read_bytes();a.write_text('updated content')
            with self.assertRaises(ValueError):backend.migration(roots,[str(a)],str(output))
            receipts=backend.migrate(backend.migration(roots,[str(a)],str(output),overwrite=True));self.assertEqual(Path(receipts[0]['backup']).read_bytes(),old)
            with self.assertRaises(ValueError):backend.selected(roots,[str(a),str(output/a.name)])
            self.assertTrue(a.exists());receipts=backend.quarantine(backend.selected(roots,[str(a)]));self.assertFalse(a.exists());self.assertTrue(b.exists());self.assertTrue(all(Path(r['quarantine']).exists() for r in receipts));self.assertTrue(list(root.glob('.mtb_shelf_trash_*/receipt.json')))
if __name__=='__main__':unittest.main()
