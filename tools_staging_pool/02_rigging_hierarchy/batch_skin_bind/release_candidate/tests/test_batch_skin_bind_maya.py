import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()


def state():
    return (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), cmds.autoKeyframe(query=True, state=True), cmds.namespaceInfo(currentNamespace=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)

    def test_explicit_pairs_one_influence_weights_and_undo_redo(self):
        meshes = [cmds.polyCube(name='body' + str(i))[0] for i in range(2)]
        joints = []
        for i in range(2):
            cmds.select(clear=True)
            joints.append(cmds.joint(name='influence' + str(i)))
        pairs = [{'joint': j, 'mesh': m} for j, m in zip(joints, meshes)]
        cmds.select(meshes)
        before = state()
        dry = TOOL.run(dry_run=True, action='bind', pairs=pairs)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, state())
        result = TOOL.run(action='bind', pairs=pairs)
        self.assertTrue(result.success, result.message)
        for row in result.data['bindings']:
            self.assertEqual([row['joint'].split('|')[-1]], cmds.skinCluster(row['skin_cluster'], query=True, influence=True))
            self.assertEqual([1.], cmds.skinPercent(row['skin_cluster'], row['mesh'] + '.vtx[0]', query=True, value=True))
        cmds.undo()
        self.assertEqual(before[0], state()[0])
        cmds.redo()
        self.assertEqual(2, len(cmds.ls(type='skinCluster')))

    def test_all_proxy_kinds_actual_suffixes_sets_and_constraints(self):
        for mode in ('joint', 'locator', 'cube'):
            cmds.file(new=True, force=True)
            source = cmds.createNode('transform', name='source')
            cmds.setAttr(source + '.tx', 3)
            existing = cmds.createNode('transform', name='source_' + mode)
            saved = cmds.sets([existing], name='ISS_joint' if mode == 'joint' else 'ISS_cube')
            cmds.select(source)
            cmds.currentTime(7)
            before = state()
            result = TOOL.run(objects=[source], proxy_type=mode)
            self.assertTrue(result.success, result.message)
            proxy = result.data['mappings'][0]['proxy']
            self.assertNotEqual(existing, proxy)
            self.assertAlmostEqual(3, cmds.getAttr(proxy + '.tx'))
            self.assertEqual([existing], cmds.sets(saved, query=True))
            self.assertTrue(result.data['created']['constraints'])
            self.assertEqual(before[1:5], state()[1:5])
            cmds.setAttr(source + '.tx', 6)
            self.assertAlmostEqual(6, cmds.getAttr(proxy + '.tx'))
            cmds.undo()
            cmds.undo()
            self.assertEqual(before[0], state()[0])

    def test_skinned_proxy_bake_collision_independent_motion_key_removal_undo(self):
        source = cmds.polyCube(name='animatedBody')[0]
        existing = cmds.createNode('transform', name='animatedBody_joint')
        for frame, value in ((1, 0), (2, 2), (3, 4), (4, 6)):
            cmds.setKeyframe(source, attribute='tx', time=frame, value=value)
        cmds.setKeyframe(source, attribute='tx', time=20, value=8)
        cmds.addAttr(source, longName='customValue', attributeType='double', keyable=True)
        cmds.setKeyframe(source, attribute='customValue', time=1, value=1)
        cmds.setKeyframe(source, attribute='customValue', time=20, value=2)
        cmds.keyTangent(source, attribute='tx', edit=True, inTangentType='linear', outTangentType='linear')
        cmds.currentTime(4)
        original_point = cmds.pointPosition(source + '.vtx[0]', world=True)
        cmds.currentTime(9)
        cmds.select(source)
        before = state()
        args = dict(objects=[source], proxy_type='joint', skinning=True, allow_source_key_removal=True, start_frame=1, end_frame=4)
        dry = TOOL.run(dry_run=True, **args)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, state())
        result = TOOL.run(**args)
        self.assertTrue(result.success, result.message)
        proxy = result.data['mappings'][0]['proxy']
        self.assertNotEqual(existing, proxy)
        self.assertEqual([], result.data['created']['constraints'])
        self.assertFalse(cmds.keyframe(source, query=True, keyframeCount=True))
        self.assertEqual([1., 2., 3., 4.], cmds.keyframe(proxy, attribute='tx', query=True, timeChange=True))
        self.assertEqual([0., 2., 4., 6.], cmds.keyframe(proxy, attribute='tx', query=True, valueChange=True))
        self.assertEqual(before[1:5], state()[1:5])
        cmds.currentTime(4)
        for expected, actual in zip(original_point, cmds.pointPosition(source + '.vtx[0]', world=True)):
            self.assertAlmostEqual(expected, actual, places=5)
        cmds.undo()
        cmds.undo()
        self.assertEqual(before[0], state()[0])
        self.assertEqual([0., 2., 4., 6., 8.], cmds.keyframe(source, attribute='tx', query=True, valueChange=True))
        self.assertEqual([1., 2.], cmds.keyframe(source, attribute='customValue', query=True, valueChange=True))

    def test_all_batch_preflight_rejects_bound_or_hierarchical_or_driven_scale(self):
        first = cmds.polyCube(name='first')[0]
        second = cmds.polyCube(name='second')[0]
        cmds.select(clear=True)
        joint = cmds.joint(name='bone')
        cmds.skinCluster(joint, second, toSelectedBones=True)
        before = state()
        result = TOOL.run(action='bind', pairs=[{'joint': joint, 'mesh': first}, {'joint': joint, 'mesh': second}])
        self.assertFalse(result.success)
        self.assertEqual(before, state())
        cmds.setKeyframe(first, attribute='sx', time=1, value=1)
        result = TOOL.run(objects=[first], skinning=True, allow_source_key_removal=True, start_frame=1, end_frame=3)
        self.assertFalse(result.success)
        self.assertFalse(TOOL.run(objects=[first], skinning=True).success)
        cmds.file(new=True, force=True)
        parent = cmds.polyCube(name='parentMesh')[0]
        child = cmds.polyCube(name='childMesh')[0]
        child = cmds.parent(child, parent)[0]
        cmds.select(clear=True)
        joint = cmds.joint(name='hierarchyBone')
        before = state()
        result = TOOL.run(action='bind', pairs=[{'joint': joint, 'mesh': parent}, {'joint': joint, 'mesh': child}])
        self.assertFalse(result.success)
        self.assertEqual(before, state())
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
