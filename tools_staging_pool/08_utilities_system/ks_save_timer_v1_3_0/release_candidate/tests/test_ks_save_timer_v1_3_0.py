import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.ks_save_timer_v1_3_0 import KSSaveTimerTool
    tool=KSSaveTimerTool()
from maya_toolkit.tools.ks_save_timer_v1_3_0 import storage,session
class Checks(unittest.TestCase):
    def test_pure_preflight_typed_config_history_and_backups(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('ks_saveTimer',sys.modules)
        self.assertEqual(storage.config_value('general','timer_autopause','False'),'False')
        with tempfile.TemporaryDirectory() as td:
            session.data_root=Path(td);p=Path(td)/'KSSaveTimer_timeTrackHistory.json';storage.write_history(p,{'desktop':{}});original=p.read_bytes();row=storage.write_history(p,{'desktop':{}});self.assertEqual(Path(row['backup']).read_bytes(),original)
            with self.assertRaises(ValueError):storage.write_history(p,{'desktop':{'bad':{'totalTime':-1,'history':{}}}})
            self.assertEqual(p.read_bytes(),original)
            with self.assertRaises(ValueError):storage.ini('[general]\ntimer_autopause=malformed\n')
            with self.assertRaises(ValueError):storage.atomic(Path(td)/'foreign.json',b'{}')
            self.assertFalse((Path(td)/'foreign.json').exists());session.data_root=None
if __name__=='__main__':unittest.main()
