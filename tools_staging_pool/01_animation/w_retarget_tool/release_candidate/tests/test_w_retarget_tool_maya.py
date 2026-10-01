import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest import mock
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Isolated temporary mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()


def snapshot():
    return (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), cmds.autoKeyframe(query=True, state=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.autoKeyframe(state=False)
        cmds.undoInfo(state=True)
        self.source = cmds.createNode('transform', name='source')
        self.target = cmds.createNode('transform', name='target')
        cmds.setAttr(self.target + '.tx', 10)
        for frame, value in ((1, 0), (2, 2), (3, 4), (4, 6)):
            cmds.setKeyframe(self.source, attribute='tx', time=frame, value=value)
        cmds.currentTime(9)
        cmds.select(self.target)
        self.args = {'pairs': [{'source': self.source, 'target': self.target}], 'start_frame': 1, 'end_frame': 4}

    def assert_no_helpers(self):
        self.assertEqual([], cmds.ls('wRetarget_*'))
        self.assertEqual([], cmds.ls('*.wRetargetTemporaryOwner', objectsOnly=True))

    def test_pose_offset_exclusive_end_restore_and_one_undo(self):
        cmds.autoKeyframe(state=True)
        before = snapshot()
        result = TOOL.run(dry_run=True, **self.args)
        self.assertTrue(result.success, result.message)
        self.assertEqual(snapshot(), before)
        result = TOOL.run(**self.args)
        self.assertTrue(result.success, result.message)
        self.assertEqual(cmds.currentTime(query=True), 9)
        self.assertEqual(cmds.ls(selection=True), [self.target])
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assert_no_helpers()
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True), [1., 2., 3.])
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, valueChange=True), [10., 12., 14.])
        self.assertEqual(cmds.keyframe(self.target, attribute='sx', query=True, valueChange=True), [1., 1., 1.])
        cmds.undo()
        self.assertFalse(cmds.keyframe(self.target, query=True, keyframeCount=True))
        self.assert_no_helpers()
        cmds.redo()
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, valueChange=True), [10., 12., 14.])
        self.assert_no_helpers()

    def test_parent_namespaces_existing_keys_and_atomic_batch_preflight(self):
        cmds.namespace(add='character')
        parent = cmds.createNode('transform', name='character:parent')
        target_parent = cmds.createNode('transform', name='targetParent')
        cmds.setAttr(parent + '.tx', 5)
        self.source = cmds.parent(self.source, parent)[0]
        self.target = cmds.parent(self.target, target_parent)[0]
        # Parent preserves world values; target pose at start is the explicit 10.
        for frame, value in ((-1, 10), (1, 10), (9, 10)):
            cmds.setKeyframe(self.target, attribute='tx', time=frame, value=value)
        args = dict(self.args, pairs=[{'source': self.source, 'target': self.target}])
        blocked = cmds.createNode('transform', name='lockedTarget')
        cmds.setAttr(blocked + '.tx', lock=True)
        before = snapshot()
        failed = TOOL.run(**dict(args, pairs=args['pairs'] + [{'source': self.source, 'target': blocked}]))
        self.assertFalse(failed.success)
        self.assertEqual(before, snapshot())
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True), [-1., 1., 9.])
        result = TOOL.run(**args)
        self.assertTrue(result.success, result.message)
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True), [-1., 1., 2., 3., 9.])
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, time=(1, 3), valueChange=True), [10., 12., 14.])
        self.assert_no_helpers()
        cmds.undo()
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True), [-1., 1., 9.])

    def test_injected_write_failure_cleans_owned_helpers_restores_and_undo(self):
        real = cmds.setKeyframe
        calls = []
        def failing(*args, **kwargs):
            calls.append(kwargs)
            if len(calls) == 10:
                raise RuntimeError('injected target write failure')
            return real(*args, **kwargs)
        before = snapshot()
        with mock.patch.object(cmds, 'setKeyframe', side_effect=failing):
            result = TOOL.run(**self.args)
        self.assertFalse(result.success)
        self.assertIn('injected target', result.message)
        self.assertEqual(before[1:4], snapshot()[1:4])
        self.assert_no_helpers()
        self.assertTrue(cmds.keyframe(self.target, query=True, keyframeCount=True))
        cmds.undo()
        self.assertFalse(cmds.keyframe(self.target, query=True, keyframeCount=True))
        self.assert_no_helpers()

    def test_fbx_export_new_file_preserves_settings_selection_and_no_overwrite(self):
        # Loading is confined to this fresh temporary standalone process.
        cmds.loadPlugin('fbxmaya', quiet=True)
        options = ['FBXExportUpAxis', 'FBXExportInAscii', 'FBXExportFileVersion', 'FBXExportBakeComplexAnimation', 'FBXExportBakeComplexStart', 'FBXExportBakeComplexEnd', 'FBXExportBakeComplexStep']
        old = {name: mel.eval(name + ' -q') for name in options}
        before = snapshot()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'new.fbx'
            args = {'action': 'export', 'exports': [{'nodes': [self.source], 'path': str(path)}], 'start_frame': 1, 'end_frame': 4, 'up_axis': 'z', 'ascii': True, 'fbx_version': 'FBX201800'}
            dry = TOOL.run(dry_run=True, **args)
            self.assertTrue(dry.success, dry.message)
            self.assertFalse(path.exists())
            self.assertEqual(before, snapshot())
            result = TOOL.run(**args)
            self.assertTrue(result.success, result.message)
            self.assertGreater(path.stat().st_size, 0)
            self.assertEqual(old, {name: mel.eval(name + ' -q') for name in options})
            self.assertEqual(before[1:4], snapshot()[1:4])
            contents = path.read_bytes()
            result = TOOL.run(**args)
            self.assertFalse(result.success)
            self.assertEqual(contents, path.read_bytes())
            self.assertEqual([], list(Path(folder).glob('.wRetarget_*')))

    def test_shared_curve_timewarp_and_retarget_cycles_rejected(self):
        curve = cmds.listConnections(self.source + '.tx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', self.target + '.tx')
        self.assertFalse(TOOL.run(dry_run=True, **self.args).success)
        cmds.disconnectAttr(curve + '.output', self.target + '.tx')
        cmds.setKeyframe(self.target, attribute='tx', time=1, value=10)
        target_curve = cmds.listConnections(self.target + '.tx', source=True, destination=False)[0]
        warp = cmds.createNode('animCurveTT')
        cmds.connectAttr(warp + '.output', target_curve + '.input', force=True)
        self.assertFalse(TOOL.run(dry_run=True, **self.args).success)
        self.assertFalse(TOOL.run(dry_run=True, pairs=[{'source': self.target, 'target': self.target}]).success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
