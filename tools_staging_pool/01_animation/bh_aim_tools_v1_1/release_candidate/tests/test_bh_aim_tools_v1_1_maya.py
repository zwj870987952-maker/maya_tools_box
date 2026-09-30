import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('必须通过隔离 runner 运行')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.bh_aim_tools_v1_1 import BhAimTool
    load_tool = BhAimTool
tool = load_tool()
from maya_toolkit.tools.bh_aim_tools_v1_1 import runtime, state


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.controller = cmds.createNode('transform', name='control')
        cmds.setKeyframe(self.controller, attribute='tx', time=1, value=0)
        cmds.setKeyframe(self.controller, attribute='tx', time=3, value=2)
        cmds.setKeyframe(self.controller, attribute='tx', time=5, value=4)
        cmds.playbackOptions(min=1, max=5)
        cmds.currentTime(1)
        cmds.select(self.controller)
        cmds.flushUndo()

    def ok(self, result):
        self.assertTrue(result.success, result.to_dict())
        return result.data

    def create(self):
        result = self.ok(tool.run(action='create', objects=[self.controller]))
        locator = result['items'][0]['locator']
        cmds.setAttr(locator + '.tz', 5)
        return locator

    def snapshot(self):
        return (sorted(cmds.ls(long=True)), cmds.currentTime(query=True), cmds.ls(selection=True, long=True),
                cmds.evaluationManager(query=True, mode=True), cmds.refresh(query=True, suspend=True),
                bool(mel.eval('evaluator -q -name "cache";')), cmds.undoInfo(query=True, undoName=True))

    def test_complete_load_origin_and_guard_no_gui(self):
        before = self.snapshot()
        data = runtime.load_suite()
        self.assertEqual(len(data['procedures']), 17)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(cmds.window('mtbAim_bh_aimTools', exists=True))
        with self.assertRaises(RuntimeError):
            mel.eval('mtbAim_bh_createAimLoc();')
        self.assertFalse(tool.run(action='open_ui', dry_run=True).success)

    def test_create_uuid_link_selection_and_single_undo(self):
        result = self.ok(tool.run(action='create', objects=[self.controller]))
        locator = result['items'][0]['locator']
        self.assertEqual(state.load(locator)['controller'], state.identity(self.controller))
        self.assertEqual(cmds.ls(selection=True, long=True), [locator])
        cmds.undo()
        self.assertFalse(cmds.objExists(locator))
        self.assertTrue(cmds.objExists(self.controller))

    def test_attach_keys_only_and_all_frames_actual_locator_keys(self):
        for only, expected in ((True, [1, 3, 5]), (False, [1, 2, 3, 4, 5])):
            locator = self.create()
            self.ok(tool.run(action='attach', objects=[locator], keys_only=only))
            self.assertEqual(cmds.keyframe(locator, attribute='tx', query=True, timeChange=True), expected)
            self.assertAlmostEqual(cmds.getAttr(locator + '.tx', time=5), 4)
            self.assertFalse(cmds.listRelatives(locator, type='parentConstraint'))
            self.ok(tool.run(action='clear', objects=[locator]))
            self.assertTrue(cmds.objExists(self.controller))

    def test_aim_bake_actual_rotation_keys_cleanup_and_undo(self):
        locator = self.create()
        self.ok(tool.run(action='attach', objects=[locator], keys_only=False))
        self.ok(tool.run(action='aim', objects=[locator]))
        self.assertTrue(cmds.ls(type='aimConstraint'))
        cmds.setKeyframe(locator, attribute='ty', time=1, value=0)
        cmds.setKeyframe(locator, attribute='ty', time=5, value=5)
        expected = [cmds.getAttr(self.controller + '.rotate', time=frame)[0] for frame in range(1, 6)]
        self.ok(tool.run(action='bake', objects=[locator], keys_only=False))
        self.assertFalse(cmds.objExists(locator))
        self.assertTrue(cmds.objExists(self.controller))
        self.assertFalse(cmds.ls(type='aimConstraint'))
        self.assertEqual(cmds.keyframe(self.controller, attribute='rx', query=True, timeChange=True), [1, 2, 3, 4, 5])
        for frame, wanted in enumerate(expected, 1):
            actual = cmds.getAttr(self.controller + '.rotate', time=frame)[0]
            for value, target in zip(actual, wanted):
                self.assertAlmostEqual(value, target, places=4)
        cmds.undo()
        self.assertTrue(cmds.objExists(locator))
        self.assertTrue(cmds.ls(type='aimConstraint'))

    def test_keys_only_delete_all_old_rotations_explicit_and_no_empty_keys(self):
        locator = self.create()
        self.assertFalse(tool.run(action='bake', objects=[locator], delete_rotation_keys=True, dry_run=True).success)
        self.ok(tool.run(action='attach', objects=[locator], keys_only=True))
        cmds.setKeyframe(self.controller, attribute='rz', time=0, value=10)
        cmds.setKeyframe(self.controller, attribute='rz', time=6, value=20)
        # Existing animation is present before aim; Maya then creates the owned
        # pairBlend inside that action. Adding keys afterward creates a foreign
        # consumer, which is intentionally refused by ownership protection.
        self.ok(tool.run(action='aim', objects=[locator]))
        self.ok(tool.run(action='bake', objects=[locator], keys_only=True, delete_rotation_keys=True))
        self.assertNotIn(0, cmds.keyframe(self.controller, attribute='rz', query=True, timeChange=True))
        self.assertNotIn(6, cmds.keyframe(self.controller, attribute='rz', query=True, timeChange=True))
        self.assertTrue(cmds.objExists(self.controller))

    def test_foreign_child_ctrl_rewire_and_foreign_constraint_refused(self):
        locator = self.create()
        child = cmds.createNode('transform', name='foreignChild', parent=locator)
        self.assertFalse(tool.run(action='clear', objects=[locator], dry_run=True).success)
        cmds.parent(child, world=True)
        stranger = cmds.createNode('transform', name='stranger')
        cmds.disconnectAttr(self.controller + '.message', locator + '.ctrl')
        cmds.connectAttr(stranger + '.message', locator + '.ctrl')
        self.assertFalse(tool.run(action='attach', objects=[locator], dry_run=True).success)
        cmds.disconnectAttr(stranger + '.message', locator + '.ctrl')
        cmds.connectAttr(self.controller + '.message', locator + '.ctrl')
        constraint = cmds.parentConstraint(stranger, locator)[0]
        self.assertFalse(tool.run(action='attach', objects=[locator], dry_run=True).success)
        self.assertTrue(cmds.objExists(constraint))

    def test_dry_run_and_exception_restore_runtime(self):
        before = self.snapshot()
        self.ok(tool.run(action='create', objects=[self.controller], dry_run=True))
        self.assertEqual(before, self.snapshot())
        locator = self.create()
        saved = self.snapshot()
        original = mel.eval
        def fail(command):
            if command == 'mtbAim_bh_attachLoc();':
                cmds.currentTime(4)
                cmds.refresh(suspend=True)
                raise RuntimeError('intentional fixture failure')
            return original(command)
        with patch.object(mel, 'eval', side_effect=fail):
            self.assertFalse(tool.run(action='attach', objects=[locator]).success)
        after = self.snapshot()
        self.assertEqual(saved[1:6], after[1:6])
        self.assertTrue(state.load(locator)['failed'])
        self.ok(tool.run(action='clear', objects=[locator]))

    def test_long_path_collision_actual_name_protects_foreign_temp_root(self):
        group = cmds.createNode('transform', name='group')
        self.controller = cmds.parent(self.controller, group)[0]
        foreign = cmds.spaceLocator(name='control_ROOTLOCATOR')[0]
        locator = self.create()
        self.ok(tool.run(action='aim', objects=[locator]))
        self.assertTrue(cmds.objExists(foreign))
        self.ok(tool.run(action='clear', objects=[locator]))
        self.assertTrue(cmds.objExists(self.controller))

    def test_duplicate_leaf_controller_batch_uuid_rename_and_scene_reload(self):
        import tempfile
        first_parent = cmds.createNode('transform', name='firstRig')
        second_parent = cmds.createNode('transform', name='secondRig')
        first = cmds.ls(cmds.parent(self.controller, first_parent)[0], long=True)[0]
        cmds.createNode('transform', name='control', parent=second_parent)
        second = cmds.listRelatives(second_parent, children=True, fullPath=True, type='transform')[0]
        result = self.ok(tool.run(action='create', objects=[first, second]))
        locators = [item['locator'] for item in result['items']]
        self.assertEqual(len(set(locators)), 2)
        values = [state.load(node)['controller'] for node in locators]
        self.assertEqual(values, [state.identity(first), state.identity(second)])
        renamed = cmds.rename(locators[0], 'renamedAim')
        with tempfile.TemporaryDirectory(prefix='bh_aim_scene_') as folder:
            path = str(Path(folder) / 'fixture.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, open=True, force=True)
            self.assertEqual(state.load(renamed)['controller'], values[0])
            self.ok(tool.run(action='clear', objects=[renamed, locators[1]]))
            self.assertTrue(cmds.objExists(first))
            self.assertTrue(cmds.objExists(second))


if __name__ == '__main__':
    unittest.main(verbosity=2)
