import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.keyframe_overlap import runtime, native


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.currentUnit(angle='deg', linear='cm', time='film')
        cmds.playbackOptions(minTime=10, maxTime=16)
        cmds.autoKeyframe(state=False)
        self.node = cmds.circle(name='control', constructionHistory=False)[0]
        for frame in (10, 13, 16):
            for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                cmds.setKeyframe(self.node, attribute=attr, time=frame, value=(frame - 10) * (3 if attr.startswith('r') else 1))
        cmds.currentTime(13)
        cmds.select(self.node)

    def create(self, **kwargs):
        result = TOOL.run(action='create', objects=[self.node], **kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    def test_create_editable_graph_bake_and_undo(self):
        before = cmds.keyframe(self.node, query=True, valueChange=True)
        foreign = cmds.createNode('transform', name='kfo_user_data')
        data = self.create(mode_name='pos_xyzb', dynamic=3, offset=1)
        self.assertTrue(cmds.objExists(foreign))
        self.assertEqual(1, len(runtime.records()))
        row = runtime.get_record(data['record_id'])
        self.assertTrue(runtime.validate_graph(row))
        self.assertTrue(cmds.objExists(data['editable_group']))
        cmds.undo()
        self.assertEqual([], runtime.records())
        self.assertEqual(before, cmds.keyframe(self.node, query=True, valueChange=True))
        cmds.redo()
        row = runtime.get_record(data['record_id'])
        # User edits the intended red locator with a direct animation curve.
        editable = cmds.listRelatives(data['editable_group'], children=True, fullPath=True)[0]
        cmds.setKeyframe(editable, attribute='tx', time=13, value=5)
        result = TOOL.run(action='bake', record_id=row['record_id'])
        self.assertTrue(result.success, str((result.message, result.errors)))
        self.assertEqual([], runtime.records())
        self.assertFalse(cmds.objExists(data['editable_group']))
        self.assertFalse(cmds.listRelatives(self.node, type='constraint'))
        self.assertTrue(cmds.objExists(foreign))
        cmds.undo()
        self.assertEqual(1, len(runtime.records()))
        self.assertTrue(cmds.objExists(data['editable_group']))

    def test_rotation_modes_sparse_optimizer_real_frame_indices(self):
        for mode in ('aim_xb', 'aim_yb', 'aim_zb', 'pos_xzb', 'pos_yb'):
            data = self.create(mode_name=mode)
            result = TOOL.run(action='bake', record_id=data['record_id'])
            self.assertTrue(result.success, str((mode, result.message, result.errors)))
            self.assertEqual(13, cmds.currentTime(query=True))
            self.assertEqual(['control'], cmds.ls(selection=True))
            cmds.undo()
            cmds.undo()
        # Probe the actual original optimizer on nonzero frame indices.
        data = self.create(mode_name='pos_xyzb')
        result = TOOL.run(action='bake', record_id=data['record_id'])
        self.assertTrue(result.success, result.message)
        for curve in cmds.keyframe(self.node, query=True, name=True):
            times = cmds.keyframe(curve, query=True, timeChange=True)
            self.assertIn(10, times)
            self.assertIn(16, times)
            self.assertEqual([10, 13, 16], times)

    def test_rename_reload_dry_scope_and_failure_finally(self):
        before = (cmds.ls(long=True), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True), cmds.evaluationManager(query=True, mode=True))
        self.assertTrue(TOOL.run(dry_run=True, action='create', objects=[self.node]).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True), cmds.evaluationManager(query=True, mode=True)))
        data = self.create()
        self.node = cmds.rename(self.node, 'renamed')
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'backup.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii')
            cmds.file(path, open=True, force=True)
            result = TOOL.run(action='bake', record_id=data['record_id'])
            self.assertTrue(result.success, str((result.message, result.errors)))
            cmds.undo()
        row = runtime.get_record(data['record_id'])
        foreign = cmds.createNode('transform', name='foreign')
        cmds.parent(foreign, row['prefix'] + 'overlap_grp')
        self.assertFalse(TOOL.validate(action='bake', record_id=row['record_id']).success)
        cmds.parent(foreign, world=True)
        cmds.autoKeyframe(state=True)
        mode = cmds.evaluationManager(query=True, mode=True)
        with patch.object(cmds, 'bakeResults', side_effect=RuntimeError('injected bake failure')):
            result = TOOL.run(action='bake', record_id=row['record_id'])
        self.assertFalse(result.success)
        self.assertFalse(runtime._ACTIVE)
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertEqual(mode, cmds.evaluationManager(query=True, mode=True))
        self.assertFalse(cmds.refresh(query=True, suspend=True))
        cmds.undo()
        self.assertEqual(1, len(runtime.records()))

    def test_readonly_guards_and_native_write_guard(self):
        self.assertFalse(TOOL.validate(action='open_ui').success)
        cmds.setAttr(self.node + '.tx', lock=True)
        self.assertFalse(TOOL.validate(action='create', objects=[self.node]).success)
        cmds.setAttr(self.node + '.tx', lock=False)
        other = cmds.circle(name='other', constructionHistory=False)[0]
        curve = cmds.listConnections(self.node + '.tx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', other + '.tx')
        self.assertFalse(TOOL.validate(action='create', objects=[self.node]).success)
        cmds.disconnectAttr(curve + '.output', other + '.tx')
        cmds.pointConstraint(other, self.node)
        self.assertFalse(TOOL.validate(action='create', objects=[self.node]).success, repr((cmds.listRelatives(self.node, type='constraint'), cmds.listConnections(self.node), cmds.listHistory(self.node))))
        with self.assertRaises(RuntimeError):
            native.loc_delay_system()


if __name__ == '__main__':
    unittest.main(verbosity=2)
