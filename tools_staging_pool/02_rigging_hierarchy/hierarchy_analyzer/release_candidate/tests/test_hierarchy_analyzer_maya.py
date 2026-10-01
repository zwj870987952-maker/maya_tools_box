import os
from pathlib import Path
import runpy
import sys
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
mod = sys.modules[TOOL.__class__.__module__]
engine = __import__(mod.__package__+'.engine', fromlist=['engine'])


def state():
    return (sorted(cmds.ls(long=True)), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), cmds.autoKeyframe(query=True, state=True), cmds.namespaceInfo(currentNamespace=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)

    def test_full_dag_parents_namespaced_duplicate_leaves_and_readonly_state(self):
        cmds.namespace(add='rig')
        roots = [cmds.createNode('transform', name='rig:root'+str(i)) for i in range(2)]
        leaves = [cmds.createNode('transform', name='rig:same', parent=root) for root in roots]
        leaves = [engine.resolve(root)+'|rig:same' for root in roots]
        root = engine.resolve(roots[0])
        cmds.select(leaves+[root])
        before = state()
        dry = TOOL.run(dry_run=True)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, state())
        result = TOOL.run(objects=leaves+[root], include_graph=True)
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, state())
        self.assertTrue(result.data['valid'])
        self.assertEqual([[leaves[1], root], [leaves[0]]], result.data['layers'])
        self.assertEqual([root], result.data['hierarchy'][leaves[0]])
        self.assertEqual(3, len(result.data['object_uuids']))
        self.assertFalse(TOOL.run(objects=['rig:same']).success)

    def test_real_point_constraint_direction_indirect_unselected_nodes_and_parent_retention(self):
        a, hidden, c = [cmds.createNode('transform', name=x) for x in ('source', 'hidden', 'last')]
        parent = cmds.createNode('transform', name='parent')
        c = cmds.parent(c, parent)[0]
        cmds.pointConstraint(a, hidden)
        cmds.pointConstraint(hidden, c)
        before = state()
        result = TOOL.run(objects=[c, a, parent], include_graph=True)
        self.assertTrue(result.success, result.message)
        self.assertTrue(result.data['valid'])
        aa, cc, pp = map(engine.resolve, [a, c, parent])
        self.assertEqual([[aa, pp], [cc]], result.data['layers'])
        self.assertIn(cc, result.data['selected_influence'][aa])
        self.assertIn(cc, result.data['direct_graph'][pp])
        self.assertEqual([engine.resolve(hidden)], result.data['drivers'][cc])
        self.assertEqual(before, state())
        self.assertFalse(engine.verify_influence_hierarchy([[cc], [aa], [pp]]))
        self.assertTrue(engine.verify_influence_hierarchy([[aa, pp], [cc]]))

    def test_geometry_constraint_and_joints_are_complete(self):
        mesh = cmds.polyPlane(name='surface')[0]
        driven = cmds.createNode('transform', name='surfaceFollower')
        cmds.geometryConstraint(mesh, driven)
        cmds.select(clear=True)
        root = cmds.joint(name='rootJoint')
        child = cmds.joint(name='childJoint')
        result = TOOL.run(objects=[driven, mesh, child, root])
        self.assertTrue(result.success, result.message)
        self.assertTrue(result.data['valid'])
        self.assertEqual([engine.resolve(mesh)], result.data['drivers'][engine.resolve(driven)])
        self.assertEqual([engine.resolve(root)], result.data['hierarchy'][engine.resolve(child)])
        self.assertEqual(4, sum(len(x) for x in result.data['layers']))

    def test_real_structural_constraint_cycle_and_explicit_budget_instance_refusal(self):
        a, b = [cmds.createNode('transform', name=x) for x in ('cycleA', 'cycleB')]
        cmds.pointConstraint(a, b)
        cmds.pointConstraint(b, a)
        before = state()
        result = TOOL.run(objects=[a, b])
        self.assertTrue(result.success, result.message)
        self.assertFalse(result.data['valid'])
        self.assertEqual([], result.data['layers'])
        self.assertEqual([[engine.resolve(a), engine.resolve(b)]], result.data['cycles'])
        self.assertEqual(before, state())
        self.assertFalse(TOOL.run(objects=[a], max_nodes=1).success)
        self.assertFalse(TOOL.run(objects=[a, engine.resolve(a)]).success)
        cmds.file(new=True, force=True)
        mesh = cmds.polyCube()[0]
        parent = cmds.createNode('transform', name='instanceParent')
        cmds.parent(mesh, parent, add=True)
        before = state()
        self.assertFalse(TOOL.run(objects=[mesh]).success)
        self.assertEqual(before, state())


if __name__ == '__main__':
    unittest.main()
