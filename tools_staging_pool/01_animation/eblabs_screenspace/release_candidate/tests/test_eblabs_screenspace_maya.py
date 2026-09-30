import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy may run disposable scenes')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.eblabs_screenspace import scene, runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.camera, self.shape = cmds.camera(name='camera')
        self.target = cmds.createNode('transform', name='animatedControl')
        for time, value in ((1, 0), (3, 4), (5, 8)):
            cmds.setKeyframe(self.target, attribute='tx', time=time, value=value)
        cmds.setAttr(self.target + '.tz', -10)
        cmds.currentTime(1)
        cmds.select(self.target)

    def create(self, **kwargs):
        result = TOOL.run(action='create', camera=self.camera, objects=[self.target], **kwargs)
        self.assertTrue(result.success, result.message + str(result.errors) + str(result.data))
        return result.data['results'][0]

    def test_read_only_guards_and_provenance(self):
        before = scene.snapshot()
        result = TOOL.run(dry_run=True, action='create', camera=self.camera)
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, scene.snapshot())
        cmds.setAttr(self.target + '.tx', lock=True)
        self.assertFalse(TOOL.validate(action='create', camera=self.camera).success)
        self.assertEqual(before, scene.snapshot())
        cmds.setAttr(self.target + '.tx', lock=False)
        runtime.load_suite()
        names = TOOL.execute(action='inventory').data['runtime_procedures']
        for name in names:
            self.assertIn('runtime.mel', mel.eval('whatIs ' + name + ';'))
        with self.assertRaises(RuntimeError):
            runtime.require_active()
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_projection_motion_control_edit_and_safe_cleanup(self):
        row = self.create()
        control = row['control']
        self.assertEqual([1, 3, 5], cmds.keyframe(control, attribute='tx', query=True, timeChange=True))
        self.assertAlmostEqual(0.4, cmds.getAttr(control + '.tx', time=3), places=4)
        self.assertAlmostEqual(-1, cmds.getAttr(control + '.tz', time=3), places=4)
        self.assertTrue(cmds.objExists(control + '.zDepth'))
        self.assertAlmostEqual(1.1 * cmds.getAttr(self.shape + '.nearClipPlane'), cmds.getAttr(control + '.planeAdjust'), places=4)
        cmds.currentTime(3)
        pos = cmds.xform(self.target, query=True, worldSpace=True, translation=True)
        self.assertAlmostEqual(4, pos[0], places=3)
        cmds.setKeyframe(control, attribute='tx', time=3, value=0.8)
        cmds.currentTime(2)
        cmds.currentTime(3)
        pos = cmds.xform(self.target, query=True, worldSpace=True, translation=True)
        self.assertGreater(pos[0], 4)
        self.assertFalse(TOOL.run(action='create', camera=self.camera, objects=[self.target]).success)
        result = TOOL.run(action='cleanup', record_ids=[row['record_uuid']])
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertTrue(cmds.objExists(self.target))
        self.assertFalse(cmds.objExists(control))
        self.assertFalse([n for n in cmds.ls(type='constraint') or [] if scene.owned(n)])

    def test_smart_bake_keeps_sparse_timing_and_undo(self):
        row = self.create()
        cmds.setKeyframe(row['control'], attribute='tx', time=3, value=0.8)
        cmds.flushUndo()
        before = scene.snapshot()
        result = TOOL.run(action='smart_bake', record_ids=[row['record_uuid']])
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertFalse(cmds.objExists(row['control']))
        self.assertEqual([1, 3, 5], cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        self.assertGreater(cmds.getAttr(self.target + '.tx', time=3), 4)
        cmds.undo()
        self.assertEqual(before, scene.snapshot())
        self.assertTrue(cmds.objExists(row['control']))

    def test_orientation_full_bake_dense_and_namespace_restore(self):
        for time, value in ((1, 0), (3, 20), (5, 40)):
            cmds.setKeyframe(self.target, attribute='ry', time=time, value=value)
        cmds.namespace(add='userNS')
        cmds.namespace(setNamespace='userNS')
        self.camera = cmds.ls(self.camera, long=True)[0]
        self.target = cmds.ls(self.target, long=True)[0]
        row = self.create(include_orientation=True)
        self.assertTrue(row['orientation'])
        self.assertEqual(':userNS', cmds.namespaceInfo(currentNamespace=True, absoluteName=True))
        self.assertTrue(cmds.keyframe(row['control'], attribute='ry', query=True))
        result = TOOL.run(action='full_bake', record_ids=[row['record_uuid']])
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(self.target, attribute='ry', query=True, timeChange=True))
        self.assertEqual(':userNS', cmds.namespaceInfo(currentNamespace=True, absoluteName=True))
        self.assertEqual(1, cmds.currentTime(query=True))

    def test_uuid_rename_reload_foreign_descendant_refusal(self):
        row = self.create()
        cmds.rename(row['control'], 'renamedScreenControl')
        rig = cmds.rename(row['rig'], 'renamedRig')
        self.target = cmds.rename(self.target, 'renamedTarget')
        foreign = cmds.createNode('transform', name='foreignChild', parent=rig)
        before = scene.snapshot()
        result = TOOL.run(action='cleanup', record_ids=[row['record_uuid']])
        self.assertFalse(result.success)
        self.assertEqual(before, scene.snapshot())
        cmds.parent(foreign, world=True)
        with tempfile.TemporaryDirectory() as scratch:
            path = str(Path(scratch) / 'screen.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, open=True, force=True)
            result = TOOL.run(action='smart_bake', record_ids=[row['record_uuid']])
            self.assertTrue(result.success, result.message + str(result.errors))
            self.assertTrue(cmds.objExists('renamedTarget'))
            self.assertTrue(cmds.objExists('foreignChild'))

    def test_partial_failure_and_standard_undo(self):
        before = scene.snapshot()
        real = mel.eval

        def fail(command):
            if command.startswith('mtbSS_ebLabs_animTools_screenSpaceRig('):
                cmds.createNode('transform', name='partialHelper')
                raise RuntimeError('injected')
            return real(command)

        cmds.flushUndo()
        with patch.object(mel, 'eval', side_effect=fail):
            result = TOOL.run(action='create', camera=self.camera, objects=[self.target])
        self.assertFalse(result.success)
        self.assertTrue(result.data['record_uuid'])
        self.assertFalse(runtime._ACTIVE)
        self.assertIsNone(runtime._RECORD)
        self.assertEqual(1, cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual(before, scene.snapshot())


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
