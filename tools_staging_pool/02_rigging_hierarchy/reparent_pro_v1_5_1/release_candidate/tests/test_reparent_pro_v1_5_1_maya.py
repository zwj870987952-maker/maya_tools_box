import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Temporary isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.reparent_pro_v1_5_1 import runtime


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.playbackOptions(minTime=1, maxTime=4)

    def call(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, result.message)
        return result

    def test_all_native_procedures_compile_without_scene_or_gui(self):
        before = runtime.scene_map()
        state = runtime.snapshot()
        runtime.load_native()
        self.assertEqual(before, runtime.scene_map())
        self.assertEqual(state, runtime.snapshot())
        for row in runtime.catalog()['adapted_procedures']:
            self.assertNotEqual('Unknown', mel.eval('whatIs ' + row['name']))

    def test_default_preserves_baked_motion_clear_ack_dry_undo_and_safe_final_bake(self):
        control = cmds.circle(name='control')[0]
        for frame, value in ((-5, -5), (1, 1), (4, 4), (12, 12)):
            cmds.setKeyframe(control, attribute='tx', time=frame, value=value)
        foreign = cmds.spaceLocator(name='TempLocator')[0]
        cmds.select(control)
        before = runtime.scene_map()
        state = runtime.snapshot()
        rejected = TOOL.run(action='reparent', objects=[control], frame_range=[1, 4])
        self.assertFalse(rejected.success)
        self.assertEqual(before, runtime.scene_map())
        dry = self.call(dry_run=True, action='reparent', objects=[control], allow_clear_animation=True, frame_range=[1, 4])
        self.assertTrue(dry.data['clear_all_TR_keys'])
        self.assertEqual(state, runtime.snapshot())
        values = [cmds.getAttr(control + '.tx', time=f) for f in range(1, 5)]
        self.call(action='reparent', objects=[control], frame_range=[1, 4], delete_redundant=False, allow_clear_animation=True)
        loc = cmds.sets(runtime.SETS['last_locators'], query=True)[0]
        self.assertEqual([1., 2., 3., 4.], cmds.keyframe(loc, attribute='tx', query=True, timeChange=True))
        self.assertEqual(values, [cmds.getAttr(control + '.tx', time=f) for f in range(1, 5)])
        self.assertTrue(runtime.is_owned(loc))
        self.assertTrue(cmds.objExists(foreign))
        self.assertEqual(state['time'], cmds.currentTime(query=True))
        self.call(action='bake_delete', frame_range=[1, 4])
        self.assertEqual(values, [cmds.getAttr(control + '.tx', time=f) for f in range(1, 5)])
        self.assertFalse(cmds.objExists(loc))
        self.assertTrue(cmds.objExists(foreign))
        cmds.undo()
        self.assertTrue(cmds.objExists(loc))
        cmds.undo()
        self.assertEqual({n: p for n, p in before.items()}, runtime.scene_map())
        self.assertEqual([-5., 1., 4., 12.], cmds.keyframe(control, attribute='tx', query=True, timeChange=True))

    def test_pin_manual_go_cancel_and_relative_complete_native(self):
        a = cmds.circle(name='manualControl')[0]
        cmds.setAttr(a + '.tx', 3)
        self.call(action='manual_start', objects=[a])
        loc = cmds.sets(runtime.SETS['last_locators'], query=True)[0]
        cmds.setAttr(loc + '.tx', 5)
        self.call(action='manual_go', pin=True, allow_clear_animation=True)
        self.assertAlmostEqual(3, cmds.getAttr(a + '.tx'))
        cmds.setAttr(loc + '.tx', 7)
        self.assertAlmostEqual(5, cmds.getAttr(a + '.tx'))
        self.call(action='bake_delete', frame_range=[1, 4])
        b = cmds.circle(name='cancelControl')[0]
        self.call(action='manual_start', objects=[b])
        loc = cmds.sets(runtime.SETS['last_locators'], query=True)[0]
        self.call(action='manual_cancel')
        self.assertFalse(cmds.objExists(loc))
        c = cmds.circle(name='relativeControl')[0]
        parent = cmds.circle(name='relativeParent')[0]
        cmds.setAttr(c + '.tx', 2)
        self.call(action='relative', objects=[c, parent], allow_clear_animation=True, delete_redundant=False)
        cmds.setAttr(parent + '.tx', 3)
        self.assertAlmostEqual(5, cmds.getAttr(c + '.tx'))
        self.call(action='bake_delete')
        d = cmds.circle(name='pinControl')[0]
        self.call(action='reparent', objects=[d], pin=True, allow_clear_animation=True)
        self.assertTrue(runtime.sessions('all_controls'))

    def test_guards_ownership_instances_channels_and_headless_ui(self):
        a = cmds.circle(name='guardControl')[0]
        cmds.setAttr(a + '.rx', lock=True)
        self.assertFalse(TOOL.run(dry_run=True, action='reparent', objects=[a], allow_clear_animation=True).success)
        cmds.setAttr(a + '.rx', lock=False)
        foreign = cmds.createNode('transform', name='rppstg_TempLocator')
        self.assertFalse(TOOL.run(dry_run=True, action='reparent', objects=[a], allow_clear_animation=True).success)
        cmds.delete(foreign)
        other = cmds.createNode('transform', name='instanceParent')
        cmds.parent(a, other, add=True)
        self.assertFalse(TOOL.run(dry_run=True, action='reparent', objects=['|guardControl'], allow_clear_animation=True).success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()

    def test_tampered_membership_foreign_descendants_and_final_override_layer(self):
        a = cmds.circle(name='ownedControl')[0]
        self.call(action='reparent', objects=[a], pin=True, allow_clear_animation=True)
        b = cmds.circle(name='foreignMember')[0]
        cmds.sets(b, add=runtime.SETS['all_controls'])
        self.assertFalse(TOOL.run(dry_run=True, action='bake_delete').success)
        cmds.sets(b, remove=runtime.SETS['all_controls'])
        loc = cmds.sets(runtime.SETS['last_locators'], query=True)[0]
        child = cmds.createNode('transform', name='foreignChild', parent=loc)
        self.assertFalse(TOOL.run(dry_run=True, action='bake_delete').success)
        cmds.delete(child)
        self.call(action='bake_delete', bake_on_layer=True, frame_range=[1, 4])
        self.assertTrue(cmds.objExists('RPPStage_FinalBake'))
        self.assertFalse(runtime.is_owned('RPPStage_FinalBake'))
        self.assertTrue(cmds.animLayer('RPPStage_FinalBake', query=True, attribute=True))
        self.assertFalse(cmds.objExists(loc))
        cmds.undo()
        self.assertTrue(cmds.objExists(loc))

    def test_original_ik_bent_limb_and_final_bake(self):
        parent = cmds.createNode('transform', name='rigParent')
        a = cmds.circle(name='fkShoulder')[0]
        b = cmds.circle(name='fkElbow')[0]
        c = cmds.circle(name='fkWrist')[0]
        cmds.parent(a, parent)
        cmds.xform(b, worldSpace=True, translation=(2, 3, 0))
        cmds.xform(c, worldSpace=True, translation=(0, 6, 0))
        for node in (a, b, c):
            cmds.setKeyframe(node, attribute='rx', time=1, value=0)
            cmds.setKeyframe(node, attribute='rx', time=4, value=10)
        self.call(action='ik', objects=[a, b, c], frame_range=[1, 4], allow_clear_animation=True)
        self.assertTrue(cmds.ls('*_RPPStage_ikHandle'))
        before = [cmds.getAttr(n + '.rx', time=f) for n in (a, b, c) for f in range(1, 5)]
        self.call(action='bake_delete', frame_range=[1, 4])
        after = [cmds.getAttr(n + '.rx', time=f) for n in (a, b, c) for f in range(1, 5)]
        for x, y in zip(before, after):
            self.assertAlmostEqual(x, y, places=4)
        self.assertFalse(cmds.ls('*_RPPStage_ikHandle'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
