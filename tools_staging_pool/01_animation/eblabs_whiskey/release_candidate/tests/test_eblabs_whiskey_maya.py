import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy may run disposable scenes')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.eblabs_whiskey import runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        self.node = cmds.createNode('transform', name='animatedControl')
        for time, value in ((1, 0), (3, 8), (5, 10)):
            cmds.setKeyframe(self.node, attribute='tx', time=time, value=value)
        cmds.currentTime(3)
        cmds.select(self.node)

    def run_tool(self, action, **kwargs):
        result = TOOL.run(action=action, objects=[self.node], attributes=['tx'], **kwargs)
        self.assertTrue(result.success, result.message + str(result.errors) + str(result.data))
        return result.data

    def test_preflight_shared_curve_reference_and_dry(self):
        before = (cmds.ls(uuid=True), cmds.getAttr(self.node + '.tx'), cmds.undoInfo(query=True, undoName=True))
        result = TOOL.run(dry_run=True, action='slider', objects=[self.node], attributes=['tx'])
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, (cmds.ls(uuid=True), cmds.getAttr(self.node + '.tx'), cmds.undoInfo(query=True, undoName=True)))
        cmds.setAttr(self.node + '.tx', lock=True)
        self.assertFalse(TOOL.validate(action='slider', objects=[self.node], attributes=['tx']).success)
        cmds.setAttr(self.node + '.tx', lock=False)
        foreign = cmds.createNode('transform', name='foreign')
        curve = cmds.listConnections(self.node + '.tx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', foreign + '.tx')
        self.assertFalse(TOOL.validate(action='slider', objects=[self.node], attributes=['tx']).success)
        self.assertFalse(TOOL.validate(action='open_ui').success)
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'reference.ma')
            cmds.select(self.node)
            cmds.file(path, force=True, type='mayaAscii', exportSelected=True)
            cmds.file(path, reference=True, namespace='ref')
            self.assertFalse(TOOL.validate(action='slider', objects=['ref:animatedControl'], attributes=['tx']).success)

    def test_native_tween_hotkey_world_pose_multiply_and_undo(self):
        for kind, expected in (('tween', 5), ('worldSpace', 5), ('PosePusher', 15.5), ('multiply', 8)):
            data = self.run_tool('slider', slider_kind=kind, value=0.0)
            self.assertTrue(data['collected_data'])
            self.assertAlmostEqual(expected, cmds.getAttr(self.node + '.tx'), places=6, msg=kind)
            cmds.undo()
            self.assertAlmostEqual(8, cmds.getAttr(self.node + '.tx'))
        self.run_tool('inbetween', value=0.5, from_current_value=True)
        self.assertAlmostEqual(9, cmds.getAttr(self.node + '.tx'))
        cmds.undo()
        self.run_tool('inbetween', use_set_value=True)
        self.assertAlmostEqual(5, cmds.getAttr(self.node + '.tx'))
        cmds.undo()
        self.run_tool('slider', use_all_layers=False, value=0)
        self.assertAlmostEqual(5, cmds.getAttr(self.node + '.tx'))
        cmds.undo()
        self.assertEqual([1, 3, 5], cmds.keyframe(self.node, attribute='tx', query=True))

    def test_snapshot_and_explicit_camera_inout(self):
        self.node = cmds.createNode('transform', name='snapshotControl')
        cmds.setAttr(self.node + '.tx', 8)
        cmds.select(self.node)
        snap = self.run_tool('capture_snapshot')['native_result']
        cmds.setAttr(self.node + '.tx', 2)
        self.run_tool('slider', slider_kind='snapshot', snapshot_data=snap, value=1)
        self.assertAlmostEqual(8, cmds.getAttr(self.node + '.tx'))
        cmds.undo()
        self.assertAlmostEqual(2, cmds.getAttr(self.node + '.tx'))
        camera, shape = cmds.camera(name='camera')
        cmds.setAttr(camera + '.tz', 10)
        self.assertFalse(TOOL.validate(action='slider', slider_kind='inOut', objects=[self.node]).success)
        data = self.run_tool('slider', slider_kind='inOut', camera=camera, value=1)
        self.assertTrue(data['collected_data'])
        self.assertLess(cmds.getAttr(self.node + '.tx'), 2)
        cmds.undo()

    def test_subframe_constant_cleanup_keying_and_rekey(self):
        cmds.setKeyframe(self.node, attribute='tx', time=2.4, value=7)
        self.run_tool('clean_subframes')
        self.assertEqual([1, 2, 3, 5], cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.undo()
        self.assertIn(2.4, cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.cutKey(self.node, attribute='tx', clear=True)
        for frame in (1, 2, 3, 4):
            cmds.setKeyframe(self.node, attribute='tx', time=frame, value=7)
        self.run_tool('remove_boring')
        self.assertEqual([1], cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.undo()
        self.run_tool('remove_boring', leave_first=False)
        self.assertFalse(cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.undo()
        cmds.currentTime(7)
        self.run_tool('set_keys', special=True)
        self.assertIn(7, cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.undo()
        template = cmds.createNode('transform', name='template')
        for frame in (2, 6):
            cmds.setKeyframe(template, attribute='tx', time=frame, value=frame)
        result = TOOL.run(action='rekey', objects=[self.node, template], attributes=['tx'], match_last=True)
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual([2, 6], cmds.keyframe(self.node, attribute='tx', query=True))
        cmds.undo()

    def test_smash_bake_native_callback_failure_and_state(self):
        from maya_toolkit.tools.eblabs_whiskey import native
        self.run_tool('smash_bake', start=1, end=5)
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(self.node, attribute='tx', query=True))
        self.assertEqual(3, cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual([1, 3, 5], cmds.keyframe(self.node, attribute='tx', query=True))
        # An actual original decorated callback goes through standard Tool.run.
        native.Hotkeys.inbetween(0.0)
        self.assertAlmostEqual(5, cmds.getAttr(self.node + '.tx'))
        cmds.undo()
        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'setAttr', side_effect=RuntimeError('injected native write failure')):
            result = TOOL.run(action='inbetween', objects=[self.node], attributes=['tx'])
        self.assertFalse(result.success)
        self.assertTrue(cmds.undoInfo(query=True, state=True))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertFalse(runtime._ACTIVE)
        self.assertEqual(3, cmds.currentTime(query=True))
        self.assertEqual([self.node], cmds.ls(selection=True))
        self.assertFalse(runtime._CALLBACKS)

    def test_real_animation_layer_and_autokey(self):
        layer = cmds.animLayer('candidateLayer')
        cmds.animLayer(layer, edit=True, attribute=self.node + '.tx')
        cmds.animLayer(layer, edit=True, selected=True, preferred=True)
        for frame, value in ((1, 0), (3, 6), (5, 2)):
            cmds.setKeyframe(self.node, attribute='tx', time=frame, value=value, animLayer=layer)
        cmds.currentTime(3)
        curve = cmds.keyframe(self.node + '.tx', query=True, name=True)[0]
        before = cmds.keyframe(curve, query=True, valueChange=True)
        data = self.run_tool('slider', use_all_layers=False, value=0)
        row = data['collected_data'][curve]
        self.assertAlmostEqual((row['prevValue'] + row['nextValue']) / 2, cmds.keyframe(curve, query=True, index=(row['index'], row['index']), valueChange=True)[0])
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(curve, query=True, valueChange=True))
        cmds.file(new=True, force=True)
        self.node = cmds.createNode('transform', name='autoControl')
        for frame, value in ((1, 0), (3, 8), (5, 10)):
            cmds.setKeyframe(self.node, attribute='tx', time=frame, value=value)
        cmds.currentTime(3)
        cmds.select(self.node)
        cmds.autoKeyframe(state=True)
        self.run_tool('inbetween', value=0)
        self.assertAlmostEqual(5, cmds.getAttr(self.node + '.tx', time=3))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        cmds.undo()
        self.assertAlmostEqual(8, cmds.getAttr(self.node + '.tx', time=3))

    def test_session_profiles_explicit_files_and_tangent(self):
        from maya_toolkit.tools.eblabs_whiskey import native
        native.Prefs.setPrefsKey('activeProfile', 'testPrivateSession')
        self.assertEqual('testPrivateSession', native.Prefs.getActiveProfile())
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'preferences.json')
            self.assertTrue(TOOL.run(action='export_preferences', file_path=path).success)
            self.assertFalse(TOOL.run(action='export_preferences', file_path=path).success)
            self.assertTrue(TOOL.run(action='import_preferences', file_path=path).success)
            self.assertEqual('testPrivateSession', native.Prefs.getPrefsKey('activeProfile'))
        old_in = cmds.keyTangent(query=True, g=True, inTangentType=True)
        old_out = cmds.keyTangent(query=True, g=True, outTangentType=True)
        try:
            data = self.run_tool('set_tangent', tangent='linear')
            self.assertTrue(data['warnings'])
            self.assertEqual(['linear'], cmds.keyTangent(query=True, g=True, outTangentType=True))
            cmds.undo()
        finally:
            cmds.keyTangent(g=True, inTangentType=old_in[0], outTangentType=old_out[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
