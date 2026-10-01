import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
import maya_toolkit.tools.camera_f_fix as package


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        for suffix in ('Translate','Rotate','Scale'):
            cmds.optionVar(intValue=('resetTransformations'+suffix,1))
        self.cube=cmds.polyCube(name='unrelated')[0]
        cmds.setAttr('persp.translate',20,30,40)
        cmds.setAttr('persp.rotate',15,25,35)
        cmds.setAttr('persp.scale',2,3,4)
        cmds.select(self.cube)

    def call(self,**p):
        result=TOOL.run(**p)
        self.assertTrue(result.success,result.message)
        return result

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),[cmds.getAttr('persp.'+n)[0] for n in ('translate','rotate','scale')],cmds.getAttr('perspShape.focalLength'))

    def test_default_original_mel_equivalence_dry_and_single_undo(self):
        before=self.state()
        self.call(dry_run=True)
        self.assertEqual(before,self.state())
        self.call()
        after=self.state()
        self.assertEqual([(1,1,1),(0,0,0),(1,1,1)],after[4])
        self.assertEqual(['|persp'],after[1])
        self.assertEqual(before[5],after[5])
        cmds.undo()
        self.assertEqual(before[4],self.state()[4])
        self.assertEqual(before[1],self.state()[1])
        pkg=Path(package.__file__).parent
        raw=next((pkg/'upstream').glob('*.mel')).read_text(encoding='utf8')
        # Maya's exact built-in original Reset Transformations implementation.
        mel.eval('source "performResetTransformations.mel";')
        mel.eval(raw)
        self.assertEqual(after[4],self.state()[4])
        self.assertEqual(after[1],self.state()[1])

    def test_disabled_preferences_and_explicit_override_shape_and_autokey(self):
        for suffix in ('Translate','Rotate','Scale'):
            cmds.optionVar(intValue=('resetTransformations'+suffix,0))
        cmds.autoKeyframe(state=True)
        before=self.state()
        self.call(camera='perspShape',preserve_selection=True)
        self.assertEqual([(1,1,1),before[4][1],before[4][2]],self.state()[4])
        self.assertEqual(before[1],self.state()[1])
        self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        self.call(reset_rotation=True,reset_scale=True,preserve_selection=True)
        self.assertEqual([(1,1,1),(0,0,0),(1,1,1)],self.state()[4])
        self.assertEqual(0,cmds.optionVar(query='resetTransformationsRotate'))

    def test_locked_driven_orthographic_child_rig_ambiguous_instance_rejection(self):
        before=self.state()
        for p in ({'camera':'missing'},{'camera':self.cube},{'camera':'top'},{'camera':'persp;delete'}):
            self.assertFalse(TOOL.run(**p).success)
        self.assertEqual(before,self.state())
        cmds.setAttr('persp.tx',lock=True)
        state=self.state()
        self.assertFalse(TOOL.run().success)
        self.assertEqual(state,self.state())
        cmds.setAttr('persp.tx',lock=False)
        cmds.setKeyframe('persp',attribute='tx')
        state=self.state()
        self.assertFalse(TOOL.run().success)
        self.assertEqual(state,self.state())
        camera=cmds.camera(name='cameraTarget')[0]
        child=cmds.createNode('transform',parent=camera,name='rigChild')
        self.assertFalse(TOOL.run(camera=camera).success)
        cmds.delete(child)
        other=cmds.createNode('transform',name='otherParent')
        cmds.parent(camera,other,add=True)
        self.assertFalse(TOOL.run(camera='|cameraTarget').success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__=='__main__':
    unittest.main()
