import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_drop',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class MayaChecks(unittest.TestCase):
    def test_actual_import_undo_reference_open_and_scriptnode_block(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'source.ma';cmds.file(new=True,force=True);cmds.polyCube(name='testCube');cmds.file(rename=str(p));cmds.file(save=True,force=True,type='mayaAscii');cmds.file(new=True,force=True);cmds.undoInfo(state=True);before=cmds.ls(long=True)
            self.assertTrue(tool.run(action='import',path=str(p),namespace='drop_ns',dry_run=True).success);self.assertEqual(cmds.ls(long=True),before)
            result=tool.run(action='import',path=str(p),namespace='drop_ns');self.assertTrue(result.success,result.errors);self.assertTrue(cmds.objExists('drop_ns:testCube'));self.assertFalse(result.data['undo_guaranteed']);cmds.file(new=True,force=True)
            result=tool.run(action='reference',path=str(p),namespace='ref_ns');self.assertTrue(result.success,result.errors);self.assertTrue(cmds.referenceQuery('ref_ns:testCube',isNodeReferenced=True))
            cmds.createNode('transform',name='modifiedMarker');denied=tool.run(action='open',path=str(p));self.assertFalse(denied.success);self.assertTrue(cmds.objExists('ref_ns:testCube'))
            opened=tool.run(action='open',path=str(p),confirm_discard=True);self.assertTrue(opened.success,opened.errors);self.assertTrue(cmds.objExists('testCube'))
            bridge=Path(__file__).resolve().parents[1]/'maya_toolkit/tools/perform_file_drop_action/mtb_performFileDropAction.mel';mel.eval(bridge.read_text());self.assertTrue(mel.eval('exists "mtb_performFileDropAction"'))
if __name__=='__main__':unittest.main()
