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
import numpy as np
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.pose_matcher import runtime


class Maya(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.a = cmds.polyCube(name='a')[0]
        self.b = cmds.polyCube(name='b')[0]
        cmds.setAttr(self.b + '.tx', 1)
        cmds.currentTime(7)
        cmds.select(self.a)
        cmds.autoKeyframe(state=True)

    def ok(self, **kw):
        r = TOOL.run(**kw)
        self.assertTrue(r.success, str((r.message, r.errors)))
        return r.data

    def state(self):
        return [cmds.currentTime(q=True), cmds.ls(sl=True, long=True), cmds.autoKeyframe(q=True, state=True), cmds.refresh(q=True, suspend=True), cmds.namespaceInfo(currentNamespace=True), cmds.namespace(q=True, relativeNames=True)]

    def test_readonly_and_original_numeric(self):
        before, nodes, undo = self.state(), sorted(cmds.ls(long=True)), cmds.undoInfo(q=True, undoName=True)
        self.ok(action='inspect')
        data = self.ok(action='overlaps', meshes=[self.a, self.b])
        self.assertEqual(4, len(data['indices'][0]))
        with tempfile.TemporaryDirectory() as folder:
            self.ok(dry_run=True, action='merge', meshes=[self.a, self.b], output_path=str(Path(folder) / 'x.obj'))
            self.assertEqual([], list(Path(folder).iterdir()))
        self.assertEqual(before, self.state())
        self.assertEqual(nodes, sorted(cmds.ls(long=True)))
        self.assertEqual(undo, cmds.undoInfo(q=True, undoName=True))
        native = runtime.backend()
        self.assertAlmostEqual(90, native.calculate_angle_3d([1,0,0], [0,1,0]))
        with self.assertRaises(ValueError):
            native.calculate_angle_3d([0,0,0], [1,0,0])
        uv1 = np.array([[0.,0.], [1.,1.]])
        uv2 = uv1.copy()
        combined, _ = native.ProcessUV(uv1, uv2)
        self.assertTrue(np.allclose(uv2, uv1))
        self.assertTrue(np.allclose(combined[2:,0], [1.,2.]))

    def test_merge_split_hard_normals_uv_topology_and_real_undo(self):
        before = self.state()
        originals = [runtime.mesh(n) for n in (self.a, self.b)]
        with tempfile.TemporaryDirectory() as folder:
            obj = Path(folder) / 'merged.obj'
            merged = self.ok(action='merge', meshes=[self.a, self.b], output_path=str(obj))
            node = merged['created_meshes'][0]
            info = obj.with_name('merged_MergeInfo.json')
            self.assertTrue(obj.exists() and info.exists())
            self.assertEqual(before, self.state())
            arrays = runtime.mesh(node)
            self.assertEqual(12, len(arrays[1]))
            self.assertEqual(12, len(np.unique(arrays[4][:,0])))
            scene = Path(folder) / 'roundtrip.ma'
            cmds.file(rename=str(scene))
            cmds.file(save=True, type='mayaAscii')
            cmds.file(str(scene), open=True, force=True)
            self.assertTrue(np.allclose(runtime.mesh(node)[1], arrays[1]))
            # Reopening resets the Undo queue; make a fresh merge for Undo/Redo evidence.
            merged2 = self.ok(action='merge', meshes=[self.a,self.b], output_path=str(Path(folder)/'second.obj'))
            undo_node = merged2['created_meshes'][0]
            cmds.undo()
            self.assertFalse(cmds.objExists(undo_node))
            self.assertTrue(obj.exists())
            cmds.redo()
            self.assertTrue(cmds.objExists(undo_node))
            split = self.ok(action='split', meshes=[node], map_path=str(info), output_path=str(Path(folder) / 'restored.obj'))
            for restored, orig in zip(split['created_meshes'], originals):
                actual = runtime.mesh(restored)
                self.assertTrue(np.allclose(actual[1], orig[1]))
                self.assertTrue(np.allclose(actual[2], orig[2]))
                self.assertTrue(np.array_equal(actual[4][:,:3], orig[4][:,:3]))
                self.assertTrue(np.allclose(actual[3][actual[4][:,3]], orig[3][orig[4][:,3]]))
            cmds.undo()
            self.assertTrue(all(not cmds.objExists(n) for n in split['created_meshes']))
            cmds.redo()
            self.assertTrue(all(cmds.objExists(n) for n in split['created_meshes']))
            self.assertFalse(TOOL.run(action='merge', meshes=[self.a,self.b], output_path=str(obj)).success)
            current = obj.read_bytes()
            with patch.object(runtime, 'publish', side_effect=RuntimeError('injected after scene creation')):
                fail = TOOL.run(action='merge', meshes=[self.a,self.b], output_path=str(obj), overwrite=True)
                self.assertFalse(fail.success)
            self.assertEqual(current, obj.read_bytes())
            cmds.undo()
            self.assertTrue(cmds.objExists(node))

    def test_align_original_matrix_six_orders_and_undo(self):
        cmds.select(clear=True)
        s = cmds.joint(name='sRoot', p=(3,0,0))
        se = cmds.joint(name='sEnd', p=(3,2,0))
        cmds.select(clear=True)
        t = cmds.joint(name='tRoot', p=(0,0,0))
        te = cmds.joint(name='tEnd', p=(1,0,0))
        cmds.select(self.a)
        before = self.state()
        for order in range(6):
            cmds.setAttr(t + '.rotateOrder', order)
            self.ok(action='align', source_root=s, target_root=t, joint_map={'sEnd':'tEnd'})
            direction = runtime.backend().get_joint_direction(te)
            self.assertTrue(np.allclose(np.array(direction)/np.linalg.norm(direction), [0,1,0], atol=1e-6))
            self.assertEqual(before, self.state())
            cmds.undo()
            self.assertTrue(np.allclose(cmds.getAttr(t + '.rotate')[0], [0,0,0]))
        cmds.setAttr(t + '.rx', lock=True)
        self.assertFalse(TOOL.run(action='align', source_root=s,target_root=t,joint_map={'sEnd':'tEnd'}).success)

    def test_map_file_guards_legacy_roundtrip_and_scope_failure(self):
        before = self.state()
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'map.json'
            self.ok(action='save_map', joint_map={'s':'t'}, output_path=str(file))
            self.assertEqual({'s':'t'}, self.ok(action='load_map', map_path=str(file))['joint_map'])
            self.assertFalse(TOOL.run(action='save_map', joint_map={'a':'b'}, output_path=str(file)).success)
            self.assertEqual({'s':'t'}, json.loads(file.read_text()))
            legacy = Path(folder) / 'legacy.json'
            legacy.write_text(json.dumps([{'mh_joint':'a','daz_joint':'b'}]))
            self.assertEqual({'a':'b'}, self.ok(action='load_map', map_path=str(legacy))['joint_map'])
            with patch.object(runtime.backend(), 'ProcessVertices', side_effect=RuntimeError('injected before publication')):
                result = TOOL.run(action='merge', meshes=[self.a,self.b], output_path=str(Path(folder)/'fail.obj'))
                self.assertFalse(result.success)
            self.assertFalse((Path(folder)/'fail.obj').exists())
        self.assertEqual(before, self.state())
        self.assertIsNone(runtime.ACTIVE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
