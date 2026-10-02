import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.ks_save_timer_v1_3_0 import session
class MayaChecks(unittest.TestCase):
    def test_current_filename_query_and_dry_run_no_callbacks(self):
        cmds.file(new=True,force=True);session.host='maya';self.assertIsNone(session.current_file())
        with tempfile.TemporaryDirectory() as td:
            cmds.file(rename=str(Path(td)/'scene.ma'));result=tool.run(action='show_ui',data_root=td,dry_run=True);self.assertTrue(result.success,result.errors);self.assertEqual(Path(session.current_file()).name,'scene.ma');self.assertEqual(session.callback_ids,[]);self.assertIsNone(session.window);self.assertEqual(list(Path(td).iterdir()),[])
if __name__=='__main__':unittest.main()
