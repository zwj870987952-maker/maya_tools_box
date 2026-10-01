import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Temporary isolated Maya process only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.joint_optimal_pro_v4_1 import runtime


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_all143_original_names_compile_without_ui_or_scene_change(self):
        state = runtime.snapshot()
        nodes = runtime.uuids()
        undo = cmds.undoInfo(query=True, undoName=True)
        runtime.load_vendor()
        for name in runtime.catalog()['procedures']:
            self.assertEqual('Mel procedure entered interactively.', mel.eval('whatIs ' + name), name)
        self.assertEqual(state, runtime.snapshot())
        self.assertEqual(nodes, runtime.uuids())
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        self.assertFalse(cmds.window('create_skeleton_tools', exists=True))

    def test_actual_radius_color_handle_and_single_undo_redo_dry(self):
        joint = cmds.createNode('joint', name='jointA')
        other = cmds.createNode('joint', name='outsideScope')
        cmds.currentTime(12)
        cmds.select(joint)
        cmds.autoKeyframe(state=True)
        for proc, arg, attr in ((runtime.RADIUS, 2., 'radius'), (runtime.COLOR, 17, 'overrideColor'), (runtime.HANDLE, 1, 'displayHandle')):
            state = runtime.snapshot()
            previous = cmds.getAttr(joint + '.' + attr)
            untouched = cmds.getAttr(other + '.' + attr)
            undo = cmds.undoInfo(query=True, undoName=True)
            params = dict(action='call', procedure=proc, arguments=[arg], objects=[joint])
            dry = TOOL.run(dry_run=True, **params)
            self.assertTrue(dry.success, dry.message)
            self.assertEqual(state, runtime.snapshot())
            self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
            result = TOOL.run(**params)
            self.assertTrue(result.success, result.message)
            self.assertEqual(arg, cmds.getAttr(joint + '.' + attr))
            self.assertEqual(untouched, cmds.getAttr(other + '.' + attr))
            self.assertEqual(state, runtime.snapshot())
            cmds.undo()
            self.assertEqual(previous, cmds.getAttr(joint + '.' + attr))
            cmds.redo()
            self.assertEqual(arg, cmds.getAttr(joint + '.' + attr))

    def test_real_ordered_joint_creation_pose_namespace_restore_and_undo(self):
        cmds.namespace(add='rig')
        cmds.namespace(setNamespace='rig')
        a = cmds.createNode('transform', name='A')
        b = cmds.createNode('transform', name='B')
        cmds.setAttr(a + '.tx', 5)
        cmds.setAttr(b + '.ty', 3)
        cmds.selectPref(trackSelectionOrder=True)
        cmds.select([a, b])
        before = runtime.uuids()
        state = runtime.snapshot()
        result = TOOL.run(action='call', procedure=runtime.CREATE, objects=[a, b])
        self.assertTrue(result.success, result.message)
        created = result.data['native_result']
        self.assertEqual(2, len(created))
        self.assertAlmostEqual(5., cmds.xform(created[0], query=True, translation=True, worldSpace=True)[0])
        self.assertAlmostEqual(3., cmds.xform(created[1], query=True, translation=True, worldSpace=True)[1])
        self.assertEqual(state, runtime.snapshot())
        self.assertTrue(result.data['created_node_uuids'])
        cmds.undo()
        self.assertEqual(before, runtime.uuids())
        cmds.redo()
        self.assertEqual(2, len(cmds.ls(type='joint')))

    def test_locked_driven_instances_bounds_and_interactive_refusal(self):
        joint = cmds.createNode('joint')
        params = dict(action='call', procedure=runtime.RADIUS, arguments=[2], objects=[joint])
        cmds.setAttr(joint + '.radius', lock=True)
        self.assertFalse(TOOL.run(**params).success)
        cmds.setAttr(joint + '.radius', lock=False)
        cmds.setKeyframe(joint, attribute='radius', time=1, value=1)
        self.assertFalse(TOOL.run(**params).success)
        cmds.cutKey(joint, attribute='radius', clear=True)
        a = cmds.createNode('transform', name='multiParentA')
        b = cmds.createNode('transform', name='multiParentB')
        node = cmds.createNode('transform', name='instanced', parent=a)
        cmds.parent(node, b, add=True)
        rejected = TOOL.run(action='call', procedure=runtime.HANDLE, arguments=[1], objects=['|multiParentA|instanced'])
        self.assertFalse(rejected.success)
        self.assertIn('Instanced', rejected.message)
        cmds.select(joint)
        state = runtime.snapshot()
        result = TOOL.run(action='call', procedure='JOPA_skeleton_tools_menue', allow_native_scope=True)
        self.assertFalse(result.success)
        self.assertIn('interactive Maya', result.message)
        self.assertEqual(state, runtime.snapshot())
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()
        self.assertFalse(TOOL.run(action='call', procedure=runtime.LIMIT_CREATE, arguments=[1], objects=[joint]).success)


if __name__ == '__main__':
    unittest.main(verbosity=2)
