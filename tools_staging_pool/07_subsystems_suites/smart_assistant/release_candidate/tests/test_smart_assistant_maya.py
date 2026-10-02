import base64,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.smart_assistant import session
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True);session.restore_prefs()
    def test_optionvar_types_restore_and_dry(self):
        captured=tool.run(action='capture_prefs');self.assertTrue(captured.success,captured.message)
        old={'exists':cmds.optionVar(exists='gridDivisions'),'value':cmds.optionVar(query='gridDivisions')}
        before=set(cmds.ls());cmds.optionVar(intValue=('gridDivisions',7))
        self.assertTrue(tool.run(action='apply_prefs',preferences={'gridDivisions':9},dry_run=True).success);self.assertEqual(cmds.optionVar(query='gridDivisions'),7)
        self.assertTrue(tool.run(action='apply_prefs',preferences={'gridDivisions':9}).success);self.assertIsInstance(cmds.optionVar(query='gridDivisions'),int)
        self.assertEqual(cmds.optionVar(query='gridDivisions'),9)
        self.assertTrue(tool.run(action='restore_prefs').success);self.assertEqual(cmds.optionVar(query='gridDivisions'),7)
        self.assertEqual(set(cmds.ls()),before)
        if old['exists']:cmds.optionVar(intValue=('gridDivisions',old['value']))
        else:cmds.optionVar(remove='gridDivisions')
        self.assertFalse(tool.run(action='enable',dry_run=True).success)
    def test_camera_image_sequence_whole_undo(self):
        cube=cmds.polyCube()[0];cmds.select(cube);before=set(cmds.ls());selection=cmds.ls(selection=True,long=True)
        png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jFWUAAAAASUVORK5CYII=')
        with tempfile.TemporaryDirectory() as td:
            for i in (1,2):(Path(td)/f'seq.{i:04d}.png').write_bytes(png)
            dry=tool.run(action='create_sequence_camera',path=td,dry_run=True);self.assertTrue(dry.success,dry.message);self.assertEqual(set(cmds.ls()),before)
            result=tool.run(action='create_sequence_camera',path=td);self.assertTrue(result.success,result.message)
            shape=result.data['image_plane_shape'];self.assertEqual(cmds.getAttr(shape+'.useFrameExtension'),1)
            self.assertEqual(cmds.ls(selection=True,long=True),selection)
            cmds.undo();self.assertEqual(set(cmds.ls()),before);cmds.redo()
            cmds.currentTime(2);self.assertEqual(cmds.getAttr(shape+'.frameExtension'),2)
    def test_file_batch_preflight_and_open_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/'source.ma';cube=cmds.polyCube(name='fixtureCube')[0];cmds.file(rename=str(src));cmds.file(save=True,type='mayaAscii',force=True)
            cmds.file(new=True,force=True);caller=cmds.createNode('transform',name='caller');before=set(cmds.ls())
            result=tool.run(action='import_file',paths=[str(src),str(Path(td)/'missing.ma')]);self.assertFalse(result.success);self.assertEqual(set(cmds.ls()),before)
            self.assertFalse(tool.run(action='open_scene',paths=[str(src)],confirm_replace_scene=True).success);self.assertTrue(cmds.objExists(caller))
            result=tool.run(action='import_file',paths=[str(src)]);self.assertTrue(result.success,result.message);self.assertTrue(cmds.objExists(caller))
            meshes=cmds.ls(type='mesh');self.assertEqual(len(meshes),1);self.assertEqual(cmds.polyEvaluate(meshes[0],face=True),6)
            parent=(cmds.listRelatives(meshes[0],parent=True,fullPath=True) or [None])[0];self.assertIn(parent,result.data['created_nodes'])
            cmds.file(new=True,force=True);result=tool.run(action='open_scene',paths=[str(src)],confirm_replace_scene=True);self.assertTrue(result.success,result.message)
            self.assertTrue(cmds.objExists('fixtureCube'))
    def test_python_dialog_wrapper_restores_and_respects_explicit_path(self):
        native=cmds.fileDialog2
        with tempfile.TemporaryDirectory() as td:
            cmds.file(rename=str(Path(td)/'caller.ma'));records=[]
            def fake(*args,**kwargs):records.append((args,kwargs));return ['unchanged result']
            cmds.fileDialog2=fake
            try:
                session.patch_dialog();owned=cmds.fileDialog2;session.patch_dialog();self.assertIs(cmds.fileDialog2,owned)
                self.assertEqual(cmds.fileDialog2('sentinel'),['unchanged result']);self.assertEqual(records[-1][0],('sentinel',));self.assertEqual(records[-1][1]['startingDirectory'],td)
                self.assertEqual(cmds.fileDialog2(startingDirectory='explicit'),['unchanged result']);self.assertEqual(records[-1][1]['startingDirectory'],'explicit')
                def foreign(*args,**kwargs):return owned(*args,**kwargs)
                cmds.fileDialog2=foreign
                with self.assertRaises(RuntimeError):session.restore_dialog()
                self.assertIs(cmds.fileDialog2,foreign)
                cmds.fileDialog2=owned;session.restore_dialog();self.assertIs(cmds.fileDialog2,fake)
            finally:cmds.fileDialog2=native;session.patch=None;session.original=None
if __name__=='__main__':
    result=unittest.main(exit=False).result;session.restore_prefs();maya.standalone.uninitialize();sys.exit(0 if result.wasSuccessful() else 1)
