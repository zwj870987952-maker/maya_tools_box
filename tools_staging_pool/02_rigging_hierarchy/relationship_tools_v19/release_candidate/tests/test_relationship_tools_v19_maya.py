import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Temporary isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.relationship_tools_v19 import runtime, engine


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        engine.CACHE.clear()

    def call(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, result.message)
        return result

    def test_owned_mark_source_messages_motion_step_undo_and_cleanup_foreign_preserved(self):
        child = cmds.createNode('transform', name='childControl')
        parent = cmds.createNode('transform', name='parentControl')
        cmds.setAttr(child + '.tx', 4)
        foreign = cmds.spaceLocator(name='unrelated_locatorTag')[0]
        cmds.select([child, parent])
        state = runtime.snapshot()
        before = runtime.uuids()
        dry = TOOL.run(dry_run=True, action='mark', objects=[child, parent])
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, runtime.uuids())
        self.assertEqual(state, runtime.snapshot())
        self.call(action='mark', objects=[child, parent])
        mapping = engine.mark_map()
        self.assertEqual(1, len(mapping))
        cmds.setAttr(parent + '.tx', 3)
        self.call(action='one_step', objects=[child])
        self.assertAlmostEqual(7, cmds.getAttr(child + '.tx'))
        self.assertTrue(cmds.keyframe(child, attribute='tx', query=True, timeChange=True))
        cmds.undo()
        self.assertAlmostEqual(4, cmds.getAttr(child + '.tx'))
        self.call(action='delete_marks')
        self.assertFalse(engine.owned())
        self.assertTrue(cmds.objExists(foreign))
        cmds.undo()
        self.assertTrue(engine.mark_map())

    def test_mark_foot_static_and_animated_exclusive_samples_endpoint(self):
        child = cmds.createNode('transform', name='animatedChild')
        parent = cmds.createNode('transform', name='animatedParent')
        cmds.setKeyframe(child, attribute='tx', time=1, value=1)
        cmds.setKeyframe(child, attribute='tx', time=5, value=5)
        cmds.setKeyframe(parent, attribute='tx', time=1, value=0)
        cmds.setKeyframe(parent, attribute='tx', time=5, value=2)
        result = self.call(action='mark_animation', objects=[child, parent], frame_range=[1, 5], step=2)
        tag = next(iter(engine.mark_map().values()))
        curve = cmds.listConnections(tag + '.translateX', source=True, destination=False, type='animCurve')[0]
        self.assertEqual([1., 3., 4.], cmds.keyframe(curve, query=True, timeChange=True))
        self.call(action='delete_marks')
        self.call(action='mark_foot', objects=[child])
        cmds.currentTime(2)
        expected = cmds.xform(next(iter(engine.mark_map().values())), query=True, worldSpace=True, translation=True)
        self.call(action='one_step', objects=[child])
        self.assertAlmostEqual(expected[0], cmds.xform(child, query=True, worldSpace=True, translation=True)[0])

    def test_world_copy_uuid_rename_paste_range_disabled_keys_and_pose_files(self):
        obj = cmds.createNode('transform', name='copyControl')
        cmds.setAttr(obj + '.tx', 8)
        self.call(action='copy_world', objects=[obj])
        obj = cmds.rename(obj, 'renamedControl')
        cmds.setKeyframe(obj, attribute='tx', time=0, value=2)
        cmds.setKeyframe(obj, attribute='tx', time=9, value=3)
        cmds.setKeyframe(obj, attribute='ry', time=2, value=20)
        cmds.setKeyframe(obj, attribute='sy', time=2, value=2)
        cmds.select(obj)
        state = runtime.snapshot()
        self.call(action='more_step', objects=[obj], world_coords=True, rotate=False, frame_range=[1, 5], step=2)
        self.assertEqual([0., 1., 3., 4., 9.], cmds.keyframe(obj, attribute='tx', query=True, timeChange=True))
        self.assertEqual([2.], cmds.keyframe(obj, attribute='ry', query=True, timeChange=True))
        self.assertEqual([2.], cmds.keyframe(obj, attribute='sy', query=True, timeChange=True))
        self.assertEqual(state, runtime.snapshot())
        for frame in (1, 3, 4):
            self.assertAlmostEqual(8, cmds.keyframe(obj, attribute='tx', query=True, eval=True, time=(frame, frame))[0])
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'pose.json')
            self.call(action='export_pose', file_path=path)
            self.assertFalse(TOOL.run(action='export_pose', file_path=path).success)
            engine.CACHE.clear()
            self.call(action='import_pose', file_path=path)
            self.assertEqual([obj], [n.rsplit('|', 1)[-1] for n in engine.pose_cache()])
            data = json.loads(Path(path).read_text())
            data['poses'][next(iter(data['poses']))]['pos'][0] = float('nan')
            Path(path).write_text(json.dumps(data))
            before = dict(engine.CACHE)
            self.assertFalse(TOOL.run(action='import_pose', file_path=path).success)
            self.assertEqual(before, engine.CACHE)

    def test_align_key_only_empty_no_dense_bake_single_layer_and_restore(self):
        target = cmds.createNode('transform', name='alignTarget')
        source = cmds.createNode('transform', name='alignSource')
        cmds.setAttr(target + '.tx', 6)
        result = self.call(action='align', objects=[source, target], translate=True, rotate=False, bake=False, frame_range=[1, 5])
        self.assertEqual([], result.data['frames'])
        self.assertFalse(cmds.keyframe(source, attribute='tx', query=True, timeChange=True))
        self.call(action='align', objects=[source, target], rotate=False)
        self.assertAlmostEqual(6, cmds.getAttr(source + '.tx'))
        cmds.undo()
        before = runtime.uuids()
        self.call(action='align', objects=[source, target], rotate=False, frame_range=[1, 4], layer=True)
        layers = [n for n in cmds.ls(type='animLayer') or [] if n != 'BaseAnimation']
        self.assertEqual(1, len(layers))
        self.assertFalse(cmds.animLayer(layers[0], query=True, selected=True))
        self.assertEqual(3, len(cmds.animLayer(layers[0], query=True, attribute=True)))
        for frame in (1, 2, 3):
            self.assertAlmostEqual(6, cmds.getAttr(source + '.tx', time=frame))
        cmds.undo()
        self.assertEqual(before, runtime.uuids())

    def test_foreign_name_child_output_instance_lock_and_cache_no_dry_writes(self):
        child = cmds.createNode('transform', name='guardChild')
        parent = cmds.createNode('transform', name='guardParent')
        foreign = cmds.spaceLocator(name='guardChild_locatorTag')[0]
        before = runtime.uuids()
        self.assertFalse(TOOL.run(action='mark', objects=[child, parent]).success)
        self.assertEqual(before, runtime.uuids())
        cmds.delete(foreign)
        self.call(action='mark', objects=[child, parent])
        tag = next(iter(engine.mark_map().values()))
        cmds.createNode('transform', parent=tag, name='foreignDescendant')
        self.assertFalse(TOOL.run(action='delete_marks').success)
        self.assertTrue(cmds.objExists('foreignDescendant'))
        cmds.setAttr(child + '.tx', lock=True)
        self.assertFalse(TOOL.run(action='one_step', objects=[child]).success)
        a = cmds.createNode('transform', name='parentA')
        b = cmds.createNode('transform', name='parentB')
        inst = cmds.createNode('transform', name='multi', parent=a)
        cmds.parent(inst, b, add=True)
        result = TOOL.run(action='copy_world', objects=['|parentA|multi'])
        self.assertFalse(result.success)
        self.assertIn('Instanced', result.message)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
