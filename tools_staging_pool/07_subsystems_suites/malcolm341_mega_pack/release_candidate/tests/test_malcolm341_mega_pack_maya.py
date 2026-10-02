import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
rc=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('launch_m341',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.malcolm341_mega_pack import runtime
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_full_shelf_declaration_and_guards(self):
        before=set(cmds.ls())
        runtime.compile_guards()
        mel.eval((runtime.HERE/'native/shelf.mel').read_text(encoding='utf8'))
        self.assertEqual(set(cmds.ls()),before)
        self.assertIn('Mel procedure',mel.eval('whatIs MTB_shelf_malcolm341_mega_pack'))
        self.assertFalse(tool.run(action='show_ui',dry_run=True).success)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'original.ma';p.write_text('preserved',encoding='utf8');before=p.read_bytes()
            with self.assertRaises(RuntimeError):mel.eval('mtbM341NewFile('+json.dumps(p.as_posix())+');')
            self.assertEqual(p.read_bytes(),before)
            prefs=Path(td)/'prefs.mel';prefs.write_bytes(b'old data')
            mel.eval('int $mtbFile = `mtbM341Fopen '+json.dumps(prefs.as_posix())+' "a"`; fprint $mtbFile "new data"; fclose $mtbFile;')
            copies=list(Path(td).glob('prefs.mel.mtb_backup_*'));self.assertEqual(len(copies),1);self.assertEqual(copies[0].read_bytes(),b'old data')
    def test_native_pivot_preflight_scene_and_one_undo(self):
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',5)
        cmds.xform(cube,worldSpace=True,pivots=(9,0,0));cmds.select(cube+'.vtx[0:7]',replace=True)
        selection=cmds.ls(selection=True,long=True,flatten=True);pivot=cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True)
        kwargs={'action':'run_button','button_id':'button_018','confirm_native':True}
        self.assertTrue(tool.run(dry_run=True,**kwargs).success)
        self.assertEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True),pivot)
        result=tool.run(**kwargs);self.assertTrue(result.success,result.message)
        self.assertAlmostEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True)[0],5)
        self.assertEqual(cmds.ls(selection=True,long=True,flatten=True),selection)
        cmds.undo();self.assertEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True),pivot)
        self.assertEqual(cmds.ls(selection=True,long=True,flatten=True),selection)
        cmds.setAttr(cube+'.rotatePivotX',lock=True)
        self.assertFalse(tool.run(**kwargs).success);cmds.setAttr(cube+'.rotatePivotX',lock=False)
        other=cmds.polyCube()[0];cmds.select([cube,other]);self.assertFalse(tool.run(**kwargs).success)
        cmds.select(clear=True);self.assertFalse(tool.run(**kwargs).success)
if __name__=='__main__':
    result=unittest.main(exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
