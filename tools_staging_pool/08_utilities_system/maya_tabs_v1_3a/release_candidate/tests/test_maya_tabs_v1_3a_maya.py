import importlib.util,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.maya_tabs_v1_3a import session
class MayaChecks(unittest.TestCase):
    def test_unbound_modified_scene_cancel_and_exact_save_backup(self):
        cmds.file(new=True,force=True);cube=cmds.polyCube(name='keepCube')[0]
        with patch.object(cmds,'confirmDialog',return_value='Cancel'):
            with self.assertRaises(RuntimeError):session.cmds.file(new=True,force=True)
        self.assertTrue(cmds.objExists(cube));self.assertEqual(session.callbacks,[])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'temp.ma';cmds.file(rename=str(p));cmds.file(save=True,type='mayaAscii',force=True);before=p.read_bytes();cmds.setAttr(cube+'.tx',5);session.cmds.file(save=True,force=True)
            backups=list(Path(td).glob('temp.ma.mtb_backup_*'));self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),before);self.assertNotEqual(p.read_bytes(),before)
if __name__=='__main__':unittest.main()
