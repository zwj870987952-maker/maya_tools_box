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
from maya_toolkit.tools.base_overrig_v9_0 import runtime


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_complete_original_compiles_all307_without_auto_ui_or_scene_change(self):
        before = runtime.uuids()
        time = cmds.currentTime(query=True)
        selection = cmds.ls(selection=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        runtime.load_vendor()
        for name in runtime.catalog()['procedures']:
            self.assertTrue(mel.eval('whatIs ' + name).startswith('Mel procedure found in:'), name)
        self.assertEqual(before, runtime.uuids())
        self.assertEqual(time, cmds.currentTime(query=True))
        self.assertEqual(selection, cmds.ls(selection=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        self.assertFalse(cmds.window('basic_anim_scripts_ui', exists=True))

    def test_actual_native_locator_scale_and_single_undo_restore_dry(self):
        locator = cmds.spaceLocator(name='sourceLocator')[0]
        shape = cmds.listRelatives(locator, shapes=True)[0]
        cmds.currentTime(12)
        cmds.select(locator)
        cmds.autoKeyframe(state=True)
        args = dict(action='call', procedure='scale_selected_lock_or_joint', arguments=[1.5], objects=[locator])
        before = runtime.snapshot()
        nodes = runtime.uuids()
        undo = cmds.undoInfo(query=True, undoName=True)
        dry = TOOL.run(dry_run=True, **args)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, runtime.snapshot())
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        result = TOOL.run(**args)
        self.assertTrue(result.success, result.message)
        self.assertEqual(1.5, cmds.getAttr(shape + '.localScaleX'))
        self.assertEqual(nodes, runtime.uuids())
        self.assertEqual(before, runtime.snapshot())
        cmds.undo()
        self.assertEqual(1., cmds.getAttr(shape + '.localScaleX'))
        cmds.redo()
        self.assertEqual(1.5, cmds.getAttr(shape + '.localScaleX'))

    def test_native_normalized_locator_created_at_original_pose_and_undo(self):
        node = cmds.createNode('transform', name='posedControl')
        cmds.setAttr(node + '.tx', 4)
        cmds.setAttr(node + '.ry', 30)
        cmds.select(node)
        before = runtime.uuids()
        result = TOOL.run(action='call', procedure='create_normalised_locators_on_selected', objects=[node])
        self.assertTrue(result.success, result.message)
        created = result.data['native_result']
        self.assertEqual(1, len(created))
        self.assertAlmostEqual(4, cmds.getAttr(created[0] + '.tx'))
        self.assertAlmostEqual(30, cmds.getAttr(created[0] + '.ry'))
        self.assertTrue(result.data['created_node_uuids'])
        cmds.undo()
        self.assertEqual(before, runtime.uuids())

    def test_readonly_inspect_scope_lock_and_batch_workflows_honestly_rejected(self):
        node = cmds.spaceLocator()[0]
        cmds.select(node)
        before = runtime.snapshot()
        result = TOOL.run(dry_run=True)
        self.assertTrue(result.success, result.message)
        self.assertEqual(57, len(result.data['public']))
        self.assertEqual(before, runtime.snapshot())
        cmds.setAttr(node + '.tx', lock=True)
        failed = TOOL.run(action='call', procedure='create_normalised_locators_on_selected', objects=[node])
        self.assertFalse(failed.success)
        cmds.setAttr(node + '.tx', lock=False)
        result = TOOL.run(action='call', procedure='apply_Fast_Bake', objects=[node])
        self.assertFalse(result.success)
        self.assertIn('real Maya', result.message)
        self.assertEqual(before, runtime.snapshot())
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()

    def test_real_vendor_constraint_attribute_cleanup_is_scoped_and_undoable(self):
        node = cmds.createNode('transform', name='cleanupControl')
        other = cmds.createNode('transform', name='outsideScope')
        for target in (node, other):
            cmds.addAttr(target, longName='blendParent1', attributeType='double', keyable=True)
            cmds.setKeyframe(target, attribute='blendParent1', time=1, value=.5)
        cmds.addAttr(node, longName='userNote', dataType='string')
        cmds.setAttr(node + '.userNote', 'retain', type='string')
        result = TOOL.run(action='call', procedure='delete_constraint_attributes_on_objects', arguments=[[node]], objects=[node])
        self.assertTrue(result.success, result.message)
        self.assertFalse(cmds.attributeQuery('blendParent1', node=node, exists=True))
        self.assertTrue(cmds.attributeQuery('blendParent1', node=other, exists=True))
        self.assertEqual('retain', cmds.getAttr(node + '.userNote'))
        cmds.undo()
        self.assertTrue(cmds.attributeQuery('blendParent1', node=node, exists=True))
        self.assertEqual([.5], cmds.keyframe(node + '.blendParent1', query=True, valueChange=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
