import copy
import json
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
from maya_toolkit.tools.jop_retarget_anim import runtime, native


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.currentUnit(angle='deg', linear='cm')
        cmds.autoKeyframe(state=False)
        self.parent = cmds.createNode('transform', name='space')
        self.node = cmds.createNode('transform', name='control', parent=self.parent)
        circle = cmds.circle(constructionHistory=False)[0]
        cmds.parent(cmds.listRelatives(circle, shapes=True, fullPath=True)[0], self.node, shape=True, relative=True)
        cmds.delete(circle)
        for frame, values in ((1, (1, 2, 3, 10, 20, 30)), (3, (4, 5, 6, 50, 60, 70)), (5, (-1, 7, 9, 100, -20, 80))):
            for attr, value in zip(('tx', 'ty', 'tz', 'rx', 'ry', 'rz'), values):
                cmds.setKeyframe(self.node, attribute=attr, time=frame, value=value)
        cmds.currentTime(3)
        cmds.select(self.node)

    def capture(self, **kwargs):
        result = TOOL.run(action='capture', objects=[self.node], start=1, end=5, **kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    def retarget(self, data, **kwargs):
        result = TOOL.run(action='retarget', snapshot_data=data, **kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result

    def assertMatrix(self, a, b):
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, places=6)

    def test_readonly_capture_dry_and_parent_order_retarget_undo(self):
        before = (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True))
        self.assertTrue(TOOL.run(dry_run=True, objects=[self.node], start=1, end=5).success)
        data = self.capture()
        self.assertEqual(before, (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True)))
        self.assertEqual([1, 3, 5], [s['time'] for s in data['records'][0]['samples']])
        for order in range(6):
            cmds.setAttr(self.node + '.rotateOrder', order)
            cmds.setAttr(self.parent + '.translate', 20, 10, -5)
            original = cmds.keyframe(self.node, query=True, valueChange=True)
            self.retarget(data)
            for sample in data['records'][0]['samples']:
                self.assertMatrix(sample['matrix'], cmds.getAttr(self.node + '.worldMatrix[0]', time=sample['time']))
            self.assertEqual([], cmds.ls('mtbJop_*'))
            cmds.undo()
            self.assertEqual(original, cmds.keyframe(self.node, query=True, valueChange=True))

    def test_dense_multiple_frozen_capture_equivalent_to_original_dg(self):
        cmds.setAttr(self.node + '.rotatePivot', 2, -3, 1)
        other = cmds.createNode('transform', name='other', parent=self.parent)
        cmds.setKeyframe(other, attribute='tx', time=1, value=2)
        result = TOOL.run(action='capture', objects=[self.node, other], bake=True, start=1, end=5)
        self.assertTrue(result.success, result.message)
        self.assertEqual([5, 5], [len(r['samples']) for r in result.data['records']])
        point = cmds.createNode('pointMatrixMult')
        dec = cmds.createNode('decomposeMatrix')
        comp = cmds.createNode('composeMatrix')
        cmds.setAttr(point + '.inPoint', 2, -3, 1)
        cmds.connectAttr(point + '.output', comp + '.inputTranslate')
        cmds.connectAttr(dec + '.outputRotate', comp + '.inputRotate')
        for sample in result.data['records'][0]['samples']:
            raw = cmds.getAttr(self.node + '.worldMatrix[0]', time=sample['time'])
            cmds.setAttr(point + '.inMatrix', raw, type='matrix')
            cmds.setAttr(dec + '.inputMatrix', raw, type='matrix')
            self.assertMatrix(sample['matrix'], cmds.getAttr(comp + '.outputMatrix'))
        cmds.delete(point, dec, comp)
        cmds.setAttr(self.parent + '.translate', 20, 10, -5)
        self.retarget(result.data)
        for row in result.data['records']:
            node = runtime.resolve_row(row)
            for sample in row['samples']:
                self.assertMatrix(sample['matrix'], runtime.world_matrix(node, sample['time']))
        cmds.undo()

    def test_json_rename_mapping_reload_and_gui_business_bridge(self):
        data = json.loads(json.dumps(self.capture()))
        old = self.node
        self.node = cmds.rename(self.node, 'renamed')
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'backup.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii')
            cmds.file(path, open=True, force=True)
            cmds.setAttr(self.parent + '.tx', 30)
            self.retarget(data)
            cmds.undo()
        dictionaries = [{s['time']: s['matrix'] for s in row['samples']} for row in data['records']]
        runtime._CACHE[runtime.cache_key([old], dictionaries)] = copy.deepcopy(data)
        native.snapCtlFromMatrixDic([old], dictionaries)
        cmds.undo()
        new = cmds.createNode('transform', name='targetCopy', parent=self.parent)
        self.retarget(data, objects=[new])
        for s in data['records'][0]['samples']:
            self.assertMatrix(s['matrix'], cmds.getAttr(new + '.worldMatrix[0]', time=s['time']))
        cmds.undo()
        cmds.delete(self.node)
        self.assertFalse(TOOL.validate(action='retarget', snapshot_data=data).success)

    def test_guards_and_partial_failure_cleanup_undo(self):
        data = self.capture()
        cmds.setAttr(self.node + '.tx', lock=True)
        self.assertFalse(TOOL.validate(action='retarget', snapshot_data=data).success)
        cmds.setAttr(self.node + '.tx', lock=False)
        foreign = cmds.createNode('transform', name='foreign')
        curve = cmds.listConnections(self.node + '.tx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', foreign + '.tx')
        self.assertFalse(TOOL.validate(action='retarget', snapshot_data=data).success)
        cmds.disconnectAttr(curve + '.output', foreign + '.tx')
        cmds.setKeyframe(self.node, attribute='rotatePivotX', time=1, value=2)
        self.assertFalse(TOOL.validate(objects=[self.node]).success)
        cmds.undo()
        cmds.currentUnit(linear='m')
        self.assertFalse(TOOL.validate(objects=[self.node]).success)
        cmds.currentUnit(linear='cm')
        bad = copy.deepcopy(data)
        bad['records'][0]['samples'][0]['matrix'] = [0] * 16
        self.assertFalse(TOOL.validate(action='retarget', snapshot_data=bad).success)
        self.assertFalse(TOOL.validate(action='open_ui').success)
        cmds.setAttr(self.node + '.rotateAxisX', 10)
        self.assertFalse(TOOL.validate(action='retarget', snapshot_data=data).success)
        cmds.setAttr(self.node + '.rotateAxisX', 0)
        cmds.setAttr(self.parent + '.tx', 30)
        before = cmds.keyframe(self.node, query=True, valueChange=True)
        original = cmds.setKeyframe
        calls = []
        def fail(*args, **kwargs):
            calls.append(args)
            if len(calls) == 2:
                raise RuntimeError('injected second key failure')
            return original(*args, **kwargs)
        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'setKeyframe', side_effect=fail):
            result = TOOL.run(action='retarget', snapshot_data=data)
        self.assertFalse(result.success)
        self.assertEqual([], cmds.ls('mtbJop_*'))
        self.assertEqual(3, cmds.currentTime(query=True))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertFalse(runtime._ACTIVE)
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(self.node, query=True, valueChange=True))

    def test_actual_reference_context_and_explicit_edit_permission(self):
        data = self.capture()
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'rig.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii')
            cmds.file(rename=str(Path(folder) / 'working.ma'))
            cmds.file(path, reference=True, namespace='ref')
            reference = 'ref:control'
            captured = TOOL.run(action='capture', objects=[reference], start=1, end=5)
            self.assertTrue(captured.success, str((captured.message, cmds.ls('*control*', long=True), cmds.ls(reference, long=True), cmds.ls(reference, allPaths=True, long=True))))
            row = captured.data['records'][0]
            self.assertEqual(data['records'][0]['node_uuid'], row['node_uuid'])
            self.assertNotEqual('', row['reference_uuid'])
            self.assertEqual('|ref:space|ref:control', runtime.resolve_row(row))
            self.assertFalse(TOOL.validate(action='retarget', snapshot_data=captured.data).success)
            # Referenced animation curves are intentionally immutable; explicit mapping
            # to a local control still supports capture from referenced rigs.
            self.assertFalse(TOOL.validate(action='retarget', snapshot_data=captured.data, allow_reference_edits=True).success)
            self.retarget(captured.data, objects=[self.node])
            cmds.undo()


if __name__ == '__main__':
    unittest.main(verbosity=2)
