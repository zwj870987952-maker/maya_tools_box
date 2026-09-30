import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.kf_animrig_ikfk import runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.currentUnit(angle='deg', linear='cm')
        cmds.autoKeyframe(state=False)

    def test_full_native_compile_and_readonly_inspect_guards(self):
        runtime.load_native()
        for name in ('kfAnimRig_IKFK', 'matchTimeline', 'matchIKtoFK', 'matchFKtoIK', 'matchIKtoFKTen', 'matchFKtoIKTen', 'kfARI_Instruct'):
            self.assertTrue(mel.eval('exists "mtbKF_' + name + '"'))
        cmds.namespace(add='rig')
        control = cmds.createNode('transform', name='rig:CTRL_L_Hand')
        before = (cmds.ls(long=True), cmds.undoInfo(query=True, undoName=True))
        self.assertTrue(TOOL.run(action='inspect', control=control).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.undoInfo(query=True, undoName=True)))
        self.assertFalse(TOOL.validate(action='match_ik_to_fk', control=control).success)
        self.assertFalse(TOOL.validate(action='open_ui').success)
        with self.assertRaises(RuntimeError):
            runtime.delete_helpers(control)

    def test_referenced_hand_original_pole_matching_bake_and_undo(self):
        for name, position in (('CTRL_L_Hand', (0, 0, 0)), ('CTRL_L_ElbowPole', (0, 0, 0)), ('CTRL_FK_L_Shoulder', (0, 0, 0)), ('CTRL_FK_L_Elbow', (4, 1, 0)), ('CTRL_FK_L_Wrist', (8, 0, 0))):
            node = cmds.createNode('transform', name=name)
            cmds.setAttr(node + '.translate', *position)
        cmds.setAttr('CTRL_FK_L_Wrist.rotate', 10, 20, 30)
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'hand.ma')
            cmds.file(path, force=True, type='mayaAscii', exportAll=True)
            cmds.file(path, reference=True, namespace='rig')
            node = 'rig:CTRL_L_Hand'
            cmds.currentTime(3)
            cmds.select(node)
            cmds.autoKeyframe(state=True)
            dry = TOOL.run(dry_run=True, action='match_ik_to_fk', control=node, allow_reference_edits=True)
            self.assertTrue(dry.success, str((dry.message, dry.errors)))
            before = cmds.getAttr(node + '.translate')
            result = TOOL.run(action='match_ik_to_fk', control=node, allow_reference_edits=True)
            self.assertTrue(result.success, str((result.message, result.errors)))
            self.assertEqual([(8.0, 0.0, 0.0)], cmds.getAttr(node + '.translate'))
            self.assertAlmostEqual(10, cmds.getAttr(node + '.rx'))
            self.assertNotEqual([(0.0, 0.0, 0.0)], cmds.getAttr('rig:CTRL_L_ElbowPole.translate'))
            self.assertEqual(3, cmds.currentTime(query=True))
            self.assertTrue(cmds.autoKeyframe(query=True, state=True))
            self.assertFalse(cmds.ls('group*'))
            cmds.undo()
            self.assertEqual(before, cmds.getAttr(node + '.translate'))
            result = TOOL.run(action='bake_ik_to_fk', control=node, allow_reference_edits=True, start=1, end=3)
            self.assertTrue(result.success, str((result.message, result.errors)))
            self.assertEqual([1, 2, 3], cmds.keyframe(node, attribute='tx', query=True))
            cmds.undo()
            self.assertFalse(cmds.keyframe(node, attribute='tx', query=True))
            with patch.object(runtime, 'check_attr', side_effect=RuntimeError('injected helper attribute failure')):
                failed = TOOL.run(action='match_ik_to_fk', control=node, allow_reference_edits=True)
            self.assertFalse(failed.success)
            self.assertFalse(runtime._ACTIVE)
            self.assertFalse(cmds.ls('group*'))
            self.assertTrue(cmds.autoKeyframe(query=True, state=True))
            cmds.undo()
            self.assertEqual(before, cmds.getAttr(node + '.translate'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
