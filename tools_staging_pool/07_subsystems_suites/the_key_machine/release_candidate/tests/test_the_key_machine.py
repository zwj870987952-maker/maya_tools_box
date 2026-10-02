import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.the_key_machine import TheKeyMachineTool
    tool=TheKeyMachineTool()
from maya_toolkit.tools.the_key_machine import session
class Checks(unittest.TestCase):
    def test_no_native_import_and_config_literals(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('TheKeyMachine',sys.modules);self.assertGreater(len(session.operations()),150)
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);prefs,tools,scripts=session.initialize_user_data();self.assertEqual(prefs.toolbar_size,1580);self.assertTrue(tools.tool_order)
            p=Path(td)/'bad.py';p.write_text('import os\nx=1')
            with self.assertRaises(ValueError):session.literal_module(p,'bad')
            session.data_root=None
    def test_exact_backup_and_no_source_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);p=Path(td)/'clip.json';p.write_bytes(b'old\r\n')
            with session.guarded_open(str(p),'w') as f:f.write('new')
            backups=list((Path(td)/'MTB_TheKeyMachine_user_data/.mtb_backups').glob('clip.json.*'));self.assertTrue(any(q.read_bytes()==b'old\r\n' for q in backups if q.suffix!='.json'))
            with self.assertRaises(ValueError):session.guarded_open(str(Path(session.__file__).resolve()),'w')
            with self.assertRaises(ValueError):session.json_proxy.loads('{"x":NaN}') if False else session.finite(float('nan'))
            discarded=session.discard(str(p));self.assertFalse(p.exists());self.assertEqual(Path(discarded).read_text(),'new');session.data_root=None
if __name__=='__main__':unittest.main()
