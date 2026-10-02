import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.batch_processor_v3.tool import digest

class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='script batch '); self.directory=Path(self.temp.name)
        cmds.file(new=True,force=True); cmds.polyCube(name='sourceCube')
        self.ma=self.directory/'scene.ma'; cmds.file(rename=str(self.ma)); cmds.file(save=True,type='mayaAscii')
        self.mb=self.directory/'scene.mb'; cmds.file(rename=str(self.mb)); cmds.file(save=True,type='mayaBinary')
        self.sha={str(p):digest(p) for p in (self.ma,self.mb)}
        self.python=self.directory/'step 1.py'; self.python.write_text("from maya import cmds\ncmds.setAttr('sourceCube.translateX',3)\ncmds.createNode('transform',name='pythonMarker')\n",encoding='utf8')
        self.mel=self.directory/'step 2.mel'; self.mel.write_text('setAttr "sourceCube.translateX" 7; createNode transform -n "melMarker";',encoding='utf8')
        cmds.file(new=True,force=True); cmds.polySphere(name='liveUnsaved'); cmds.select('liveUnsaved'); cmds.currentTime(9); cmds.autoKeyframe(state=True)
        TOOL.progress=None; TOOL.cancelled=None

    def tearDown(self): TOOL.progress=None; TOOL.cancelled=None; cmds.file(new=True,force=True); self.temp.cleanup()
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.file(query=True,sceneName=True),cmds.file(query=True,modified=True),cmds.undoInfo(query=True,undoName=True))
    def call(self,**p):
        result=TOOL.run(**p); self.assertTrue(result.success,result.message+' '+str(result.data)); return result

    def test_ordered_python_mel_exact_backups_after_and_dirty_caller(self):
        p=dict(files=[str(self.ma),str(self.mb)],scripts=[str(self.python),str(self.mel)],base_dir=str(self.directory),save_backup=True,save_after=True)
        before=self.state(); preview=self.call(dry_run=True,**p); self.assertEqual(before,self.state()); self.assertFalse((self.directory/'BF_Backup').exists())
        result=self.call(action='process',**p); self.assertEqual(before,self.state()); self.assertEqual(2,result.data['processed'])
        for row in result.data['scenes']:
            self.assertEqual(self.sha[row['source']],digest(row['backup'])); self.assertEqual(self.sha[row['source']],digest(row['source'])); self.assertEqual([True,True],[r['success'] for r in row['scripts']])
            path=row['outputs'][0]['path']; self.assertTrue(path.endswith('.ma')); cmds.file(path,open=True,force=True,executeScriptNodes=False); self.assertEqual(7,cmds.getAttr('sourceCube.tx')); self.assertTrue(cmds.objExists('pythonMarker')); self.assertTrue(cmds.objExists('melMarker'))
        self.assertFalse(TOOL.run(action='process',**p).success)

    def test_binary_overwrite_and_script_fail_scene_switch_no_automatic_save(self):
        result=self.call(action='process',files=[str(self.mb)],scripts=[str(self.python)],overwrite=True)
        row=result.data['scenes'][0]; self.assertEqual(self.sha[str(self.mb)],digest(row['backup'])); self.assertEqual('mayaBinary',row['outputs'][0]['type'])
        cmds.file(str(self.mb),open=True,force=True,executeScriptNodes=False); self.assertEqual(3,cmds.getAttr('sourceCube.tx')); self.assertEqual(['mayaBinary'],cmds.file(query=True,type=True))
        bad=self.directory/'fail.py'; bad.write_text("raise RuntimeError('selected script failed')",encoding='utf8')
        result=TOOL.run(action='process',files=[str(self.ma)],scripts=[str(bad)],save_backup=True,save_after=True)
        self.assertFalse(result.success); row=result.data['scenes'][0]; self.assertEqual([],row['outputs']); self.assertEqual(self.sha[str(self.ma)],digest(self.ma)); self.assertTrue(Path(row['backup']).is_file()); self.assertFalse(row['scripts'][0]['success'])
        changed=self.directory/'changed.py'; changed.write_text('from maya import cmds\ncmds.file(new=True,force=True)',encoding='utf8')
        result=TOOL.run(action='process',files=[str(self.ma)],scripts=[str(changed)],save_after=True)
        self.assertFalse(result.success); self.assertIn('switched',result.data['scenes'][0]['message']); self.assertFalse((self.directory/'backup').exists())

    def test_save_current_correct_format_and_refusals_and_cancel(self):
        cmds.file(str(self.ma),open=True,force=True,executeScriptNodes=False); cmds.setAttr('sourceCube.ty',4)
        target=self.directory/'fresh.mb'; before=self.state(); self.call(action='save_current',output=str(target),dry_run=True); self.assertEqual(before,self.state()); self.assertFalse(target.exists())
        self.call(action='save_current',output=str(target)); self.assertEqual(self.sha[str(self.ma)],digest(self.ma)); cmds.file(str(target),open=True,force=True); self.assertEqual(4,cmds.getAttr('sourceCube.ty')); self.assertEqual(['mayaBinary'],cmds.file(query=True,type=True))
        cmds.file(str(self.ma),open=True,force=True); cmds.setAttr('sourceCube.tz',5); result=self.call(action='save_current',overwrite=True); self.assertEqual(self.sha[str(self.ma)],digest(result.data['backup'])); cmds.file(str(self.ma),open=True,force=True); self.assertEqual(5,cmds.getAttr('sourceCube.tz'))
        fbx=self.directory/'fake.fbx'; fbx.write_bytes(b'fake'); self.assertFalse(TOOL.run(files=[str(fbx)],overwrite=True).success)
        self.assertFalse(TOOL.run(files=[str(self.mb)],execution_mode='interactive').success)
        before=self.state(); TOOL.cancelled=lambda:True; result=TOOL.run(action='process',files=[str(self.mb)]); self.assertFalse(result.success); self.assertTrue(result.data['cancelled']); self.assertEqual(0,result.data['processed']); self.assertEqual(before,self.state())
        with self.assertRaises(RuntimeError): TOOL.show_ui()

if __name__=='__main__': unittest.main()
