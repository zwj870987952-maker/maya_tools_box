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
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.physics_tools import runtime
from maya_toolkit.tools.physics_tools.tool import CATALOG, normalize


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.control = cmds.createNode('transform', name='control')
        for f, v in ((1, 0), (3, 2), (5, 0)):
            cmds.setKeyframe(self.control, at='tx', t=f, v=v)
        cmds.playbackOptions(min=1, max=5)
        cmds.select(self.control)
        cmds.currentTime(3)
        cmds.autoKeyframe(state=True)

    def ok(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    def context_state(self):
        return [cmds.currentTime(q=True), cmds.ls(sl=True, long=True), cmds.autoKeyframe(q=True, state=True), cmds.namespaceInfo(currentNamespace=True), cmds.namespace(q=True, relativeNames=True), cmds.refresh(q=True, suspend=True), cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]

    def test_compile_all_guard_and_readonly(self):
        before = self.context_state()
        nodes = sorted(cmds.ls(long=True))
        undo = cmds.undoInfo(q=True, undoName=True)
        self.ok(dry_run=True, action='invoke', procedure='toLocator', targets=[self.control], frame_range=[1, 5])
        self.ok(action='inspect')
        self.assertEqual(before, self.context_state())
        self.assertEqual(nodes, sorted(cmds.ls(long=True)))
        self.assertEqual(undo, cmds.undoInfo(q=True, undoName=True))
        runtime.load()
        for n in CATALOG['procedures']:
            self.assertTrue(mel.eval('exists "mtkPTC_Native_' + n + '"'))
        with self.assertRaises(RuntimeError):
            mel.eval('mtkPTC_Native_toLocator();')
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_full_locator_proxy_cleanup_undo_and_namespace(self):
        cmds.namespace(add='working')
        cmds.namespace(set=':working')
        before = self.context_state()
        foreign = cmds.createNode('transform', name='imLocator_protected')
        cmds.select(self.control)
        before = self.context_state()
        data = self.ok(action='invoke', procedure='toLocator', targets=[self.control], frame_range=[1, 5])
        self.assertEqual(before, self.context_state())
        session = runtime.existing_session()
        locs = [n for n in data['owned_nodes'] if cmds.nodeType(n) == 'transform']
        self.assertEqual(1, len(locs))
        self.assertAlmostEqual(cmds.getAttr(self.control + '.tx'), cmds.getAttr(locs[0] + '.tx'))
        self.assertTrue(cmds.objExists(foreign))
        cmds.undo()
        self.assertFalse(cmds.objExists(locs[0]))
        cmds.redo()
        self.assertTrue(cmds.objExists(locs[0]))
        self.ok(action='cleanup_session')
        self.assertTrue(cmds.objExists(foreign))
        self.assertFalse(cmds.objExists(locs[0]))
        cmds.undo()
        self.assertTrue(cmds.objExists(locs[0]))

    def test_native_particle_preview_and_bake(self):
        before = self.context_state()
        foreign = cmds.createNode('transform', name='MagicDust_protected')
        cmds.select(self.control)
        before = self.context_state()
        setup = self.ok(action='invoke', procedure='PhysicsMagicButton', targets=[self.control], frame_range=[1, 5])
        self.assertTrue(any(cmds.nodeType(n) == 'particle' for n in setup['owned_nodes']))
        self.assertEqual(before, self.context_state())
        self.assertTrue(cmds.objExists(foreign))
        self.ok(action='cleanup_session')
        self.assertTrue(cmds.objExists(self.control))
        self.assertFalse(cmds.lockNode(self.control, q=True, lock=True)[0])
        cmds.undo()
        self.assertTrue(cmds.objExists(self.control))
        self.ok(action='invoke', procedure='BakeinfoController', frame_range=[1, 5])
        self.assertTrue(cmds.objExists(self.control))
        self.assertTrue(cmds.objExists(foreign))
        self.assertTrue(cmds.ls(type='animLayer'))
        cmds.undo()
        self.assertTrue(any(cmds.objExists(n) and cmds.nodeType(n) == 'particle' for n in setup['owned_nodes']))

    def test_native_jiggle_cache_scoped_and_context_restore_failure(self):
        plan = runtime.prepare(normalize(action='invoke', procedure='toLocator', targets=[self.control], frame_range=[1, 5]))
        before = self.context_state()
        with self.assertRaises(RuntimeError):
            with runtime.scope(normalize(action='invoke', procedure='toLocator'), plan):
                plane = cmds.polyPlane(name='JiggleMe', sx=1, sy=1)[0]
                runtime.create_jiggle()
                own = runtime.alive_owned()
                self.assertTrue(any(cmds.nodeType(n) == 'jiggle' for n in own.values()))
                runtime.cache(False)
                with tempfile.TemporaryDirectory() as directory:
                    runtime._ACTIVE['options']['cache_directory'] = directory
                    runtime.cache(True)
                    self.assertTrue(runtime._LAST_FILES)
                    self.assertTrue(all(Path(p).exists() for p in runtime._LAST_FILES))
                    runtime.cache(False)
                    self.assertFalse(any(Path(p).exists() for p in runtime._LAST_FILES))
                cmds.refresh(suspend=True)
                raise RuntimeError('injected after native operation')
        self.assertEqual(before, self.context_state())
        self.assertIsNone(runtime._ACTIVE)

    def test_embedded_cycle_noise_and_private_name_scope(self):
        original = (cmds.keyframe(self.control, at='tx', q=True, tc=True), cmds.keyframe(self.control, at='tx', q=True, vc=True))
        self.ok(action='invoke', procedure='curvesloop', targets=[self.control], frame_range=[1, 5])
        self.assertEqual(original, (cmds.keyframe(self.control, at='tx', q=True, tc=True), cmds.keyframe(self.control, at='tx', q=True, vc=True)))
        self.ok(action='invoke', procedure='ruidoA', targets=[self.control], frame_range=[1, 5], attributes=['tx'])
        self.assertTrue(runtime.existing_session())
        self.assertTrue(cmds.ls(type='animLayer'))

    def test_foreign_child_driver_and_locked_refusal(self):
        data = self.ok(action='invoke', procedure='toLocator', targets=[self.control], frame_range=[1, 5])
        loc = [n for n in data['owned_nodes'] if cmds.nodeType(n) == 'transform'][0]
        child = cmds.createNode('transform', name='externalChild', parent=loc)
        self.assertFalse(TOOL.run(action='cleanup_session').success)
        self.assertTrue(cmds.objExists(child))
        self.assertTrue(cmds.objExists(loc))
        cmds.setAttr(self.control + '.ry', lock=True)
        self.assertFalse(TOOL.run(action='invoke', procedure='PhysicsMagicButton', targets=[self.control]).success)


if __name__ == '__main__':
    unittest.main(verbosity=2)
