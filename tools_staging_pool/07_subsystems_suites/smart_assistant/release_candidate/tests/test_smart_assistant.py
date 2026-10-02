import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.smart_assistant import SmartAssistantTool
    tool=SmartAssistantTool()
from maya_toolkit.tools.smart_assistant import config_io
class Checks(unittest.TestCase):
    def test_prefs_no_automatic_hooks_and_file_overwrite(self):
        self.assertTrue(tool.run().success);self.assertNotIn('PySide6',sys.modules)
        self.assertFalse(tool.run(action='inspect',open_view=1).success)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'prefs.json';values={'workingUnitLinear':'cm','gridSize':12.5,'gridDivisions':8}
            self.assertTrue(tool.run(action='save_prefs',path=str(p),preferences=values,dry_run=True).success);self.assertFalse(p.exists())
            self.assertTrue(tool.run(action='save_prefs',path=str(p),preferences=values).success)
            before=p.read_bytes();self.assertEqual(config_io.read_prefs(str(p)),values)
            self.assertFalse(tool.run(action='save_prefs',path=str(p),preferences=values).success);self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(ValueError):config_io.prefs({'gridSize':True})
            with self.assertRaises(ValueError):config_io.prefs({'unexpected':'x'})
    def test_sequence_is_unambiguous_and_numerically_ordered(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for n in (8,9,10):(p/f'img.{n:04d}.png').write_bytes(b'fixture')
            s=config_io.sequence(td);self.assertEqual(s['first_frame'],8);self.assertEqual(s['last_frame'],10)
            (p/'img.0012.png').write_bytes(b'gap')
            with self.assertRaises(ValueError):config_io.sequence(td)
            (p/'img.0012.png').unlink();(p/'other.0001.png').write_bytes(b'x');(p/'other.0002.png').write_bytes(b'x')
            with self.assertRaises(ValueError):config_io.sequence(td)
if __name__=='__main__':unittest.main()
