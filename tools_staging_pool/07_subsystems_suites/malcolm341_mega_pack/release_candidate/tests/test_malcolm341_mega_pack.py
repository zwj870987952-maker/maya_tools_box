import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_m341',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.malcolm341_mega_pack import Malcolm341MegaPackTool
    tool=Malcolm341MegaPackTool()
from maya_toolkit.tools.malcolm341_mega_pack import runtime,file_guard
class Checks(unittest.TestCase):
    def test_complete_source_and_inventory(self):
        result=tool.run();self.assertTrue(result.success,result.message)
        self.assertEqual(len(result.data['buttons']),49)
        self.assertEqual(result.data['buttons'][17]['label'],'pivot')
        self.assertNotIn('maya.mel',sys.modules)
        _,c=runtime.lookup('button_006','menu_002');self.assertEqual(runtime.temp_mode('button_006','menu_002'),2)
        self.assertGreater(len(c['command']),9000)
        self.assertIn('paid script pack',c['command'])
        self.assertIn('mtbM341NewFile',c['command'])
        self.assertIn('MTB_m341_',c['command'])
        self.assertFalse(tool.run(action='inspect',confirm_native=1).success)
        self.assertFalse(tool.run(action='not_real').success)
        with self.assertRaises(ValueError):runtime.lookup('button_001','menu_001')
    def test_no_overwrite_and_exact_backup(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'prefs.mel';p.write_bytes(b'// original\r\n\xff')
            before=p.read_bytes()
            with self.assertRaises(FileExistsError):file_guard.require_new(str(p))
            self.assertEqual(p.read_bytes(),before)
            backup=file_guard.backup_existing(str(p));self.assertEqual(Path(backup['backup']).read_bytes(),before)
            self.assertEqual(p.read_bytes(),before)
            out=Path(td)/'new.ma';self.assertEqual(file_guard.require_new(str(out)),str(out));self.assertFalse(out.exists())
            with self.assertRaises(ValueError):file_guard.require_new('relative.ma')
            with self.assertRaises(ValueError):file_guard.require_new(str(Path(td)/'missing/out.ma'))
if __name__=='__main__':unittest.main()
