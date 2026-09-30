import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable tests only in isolated mayapy')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.dof_control_v1_0 import scene, runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.currentUnit(linear='cm')
        cmds.undoInfo(state=True)
        self.camera, self.shape = cmds.camera(name='testCam')
        cmds.setAttr(self.shape + '.focusDistance', 12)
        cmds.setAttr(self.shape + '.fStop', 5.6)
        cmds.currentTime(7)
        cmds.select(self.camera)

    def create(self, **kwargs):
        result = TOOL.run(action='create', cameras=[self.camera], **kwargs)
        self.assertTrue(result.success, result.message + str(result.errors) + str(result.data))
        return result.data['results'][0]

    def test_actual_graph_focus_fstop_shape_flags_and_cleanup_restore(self):
        data = self.create()
        cube = data['cube']
        self.assertEqual(12, cmds.getAttr(self.shape + '.focusDistance'))
        self.assertAlmostEqual(5.6, cmds.getAttr(self.shape + '.fStop'), places=4)
        self.assertEqual(-12, cmds.getAttr(cube + '.tz'))
        self.assertEqual(-12, cmds.getAttr(cube + '.sx'))
        self.assertEqual(-12, cmds.getAttr(cube + '.sy'))
        shape = cmds.listRelatives(cube, shapes=True, fullPath=True)[0]
        for attr in ('castsShadows', 'primaryVisibility', 'visibleInReflections', 'visibleInRefractions'):
            self.assertFalse(cmds.getAttr(shape + '.' + attr))
        self.assertFalse(cmds.getAttr(self.shape + '.depthOfField'))
        cmds.setAttr(cube + '.tz', -30)
        cmds.setAttr(cube + '.sz', 8)
        self.assertEqual(30, cmds.getAttr(self.shape + '.focusDistance'))
        self.assertEqual(8, cmds.getAttr(self.shape + '.fStop'))
        cmds.flushUndo()
        result = TOOL.run(action='cleanup', record_ids=[data['record_uuid']])
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual(12, cmds.getAttr(self.shape + '.focusDistance'))
        self.assertAlmostEqual(5.6, cmds.getAttr(self.shape + '.fStop'), places=4)
        self.assertFalse(scene.records())
        self.assertFalse([n for n in cmds.ls(long=True) or [] if scene.owned(n)])
        self.assertTrue(cmds.objExists(self.camera))
        cmds.undo()
        self.assertTrue(cmds.objExists(cube))
        self.assertEqual(30, cmds.getAttr(self.shape + '.focusDistance'))
        self.assertEqual(8, cmds.getAttr(self.shape + '.fStop'))
        cmds.redo()
        self.assertFalse(scene.records())

    def test_dry_run_locked_animated_duplicate_and_guard(self):
        before = set(cmds.ls(long=True))
        selection = cmds.ls(selection=True, long=True)
        result = TOOL.run(dry_run=True, action='create')
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, set(cmds.ls(long=True)))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        cmds.setKeyframe(self.shape, attribute='focusDistance', time=1, value=12)
        self.assertFalse(TOOL.validate(action='create', cameras=[self.camera]).success)
        cmds.delete(cmds.listConnections(self.shape + '.focusDistance', source=True, destination=False))
        cmds.setAttr(self.shape + '.fStop', lock=True)
        self.assertFalse(TOOL.validate(action='create', cameras=[self.camera]).success)
        cmds.setAttr(self.shape + '.fStop', lock=False)
        self.create()
        self.assertFalse(TOOL.run(action='create', cameras=[self.camera]).success)
        with self.assertRaises(RuntimeError):
            runtime.require_active()
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_batch_camera_shapes_namespaces_unique_graph_and_template_undo(self):
        cmds.namespace(add='rig')
        second, second_shape = cmds.camera(name='rig:camera')
        result = TOOL.run(action='create', cameras=[self.shape, second])
        self.assertTrue(result.success, result.message)
        rows = result.data['results']
        self.assertEqual(2, len(rows))
        self.assertNotEqual(rows[0]['cube'], rows[1]['cube'])
        ids = [row['record_uuid'] for row in rows]
        cmds.flushUndo()
        result = TOOL.run(action='set_template', record_ids=ids, template=True)
        self.assertTrue(result.success, result.message)
        for row in rows:
            shape = cmds.listRelatives(row['cube'], shapes=True, fullPath=True)[0]
            self.assertTrue(cmds.getAttr(shape + '.template'))
        cmds.undo()
        for row in rows:
            shape = cmds.listRelatives(row['cube'], shapes=True, fullPath=True)[0]
            self.assertFalse(cmds.getAttr(shape + '.template'))
        cleaned = TOOL.run(action='cleanup', record_ids=ids)
        self.assertTrue(cleaned.success, cleaned.message)

    def test_foreign_child_and_extra_graph_use_refuse_no_write(self):
        data = self.create()
        foreign = cmds.createNode('transform', name='foreignChild', parent=data['cube'])
        before = set(cmds.ls(long=True))
        result = TOOL.run(action='cleanup', record_ids=[data['record_uuid']])
        self.assertFalse(result.success)
        self.assertEqual(before, set(cmds.ls(long=True)))
        cmds.parent(foreign, world=True)
        other = cmds.createNode('transform', name='externalTarget')
        cmds.connectAttr(data['cube'] + '.tz', other + '.tz')
        self.assertFalse(TOOL.validate(action='cleanup', record_ids=[data['record_uuid']]).success)
        cmds.disconnectAttr(data['cube'] + '.tz', other + '.tz')
        self.assertTrue(TOOL.run(action='cleanup', record_ids=[data['record_uuid']]).success)
        self.assertTrue(cmds.objExists(foreign))
        self.assertTrue(cmds.objExists(other))

    def test_rename_save_reload_and_undo_entire_create(self):
        before = {scene.identity(n) for n in cmds.ls(long=True)}
        cmds.flushUndo()
        data = self.create()
        self.assertEqual(7, cmds.currentTime(query=True))
        self.assertEqual(self.camera, cmds.ls(selection=True)[0])
        cmds.undo()
        self.assertEqual(before, {scene.identity(n) for n in cmds.ls(long=True)})
        data = self.create()
        cmds.rename(data['cube'], 'renamedDofCube')
        cmds.rename(self.camera, 'renamedCamera')
        with tempfile.TemporaryDirectory() as scratch:
            path = str(Path(scratch) / 'dof.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, open=True, force=True)
            result = TOOL.run(action='cleanup', record_ids=[data['record_uuid']])
            self.assertTrue(result.success, result.message)
            self.assertTrue(cmds.objExists('renamedCamera'))

    def test_mid_creation_failure_preserves_record_and_undo(self):
        before = {scene.identity(n) for n in cmds.ls(long=True)}
        real = mel.eval

        def fail(command):
            if command.startswith('mtbDOF_build('):
                cmds.createNode('reverse', name='partialReverse')
                raise RuntimeError('injected')
            return real(command)

        cmds.flushUndo()
        with patch.object(mel, 'eval', side_effect=fail):
            result = TOOL.run(action='create', cameras=[self.camera])
        self.assertFalse(result.success)
        self.assertTrue(result.data['record_uuid'])
        self.assertFalse(runtime._ACTIVE)
        self.assertEqual(7, cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual(before, {scene.identity(n) for n in cmds.ls(long=True)})


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
