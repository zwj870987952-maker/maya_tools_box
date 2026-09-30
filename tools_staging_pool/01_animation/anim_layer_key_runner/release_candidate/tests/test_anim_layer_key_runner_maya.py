"""Benign MEL/Python fixtures; restricted to the disposable mayapy runner."""
import os
from pathlib import Path
import sys
import unittest

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use isolated mayapy runner; tests replace the current scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/anim_layer_key_runner'
else:
    from maya_toolkit.tools.anim_layer_key_runner import AnimLayerKeyRunnerTool
    load_tool = AnimLayerKeyRunnerTool
    PACKAGE = Path(sys.modules[AnimLayerKeyRunnerTool.__module__].__file__).parent


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.cube = cmds.polyCube()[0]
        cmds.addAttr(self.cube, longName='marker', attributeType='double', keyable=True)
        for time in (1, 2.5, 5):
            cmds.setKeyframe(self.cube, attribute='translateX', time=time, value=time * 2)
        self.curve = cmds.listConnections(self.cube + '.translateX', source=True, destination=False)[0]
        self.other = cmds.polySphere()[0]
        cmds.currentTime(20)
        cmds.select(self.other)
        self.tool = load_tool()
        self.args = dict(objects=[self.cube], only_in_playback=False, layer='BaseAnimation')

    def assert_success(self, result):
        self.assertTrue(result.success, result.to_json())

    def test_dry_run_never_evaluates_python_and_preserves_time_selection_undo(self):
        undo = cmds.undoInfo(query=True, undoName=True)
        result = self.tool.run(dry_run=True, command="cmds.setAttr(objects[0] + '.marker', 77); raise RuntimeError('executed')", language='python', **self.args)
        self.assert_success(result)
        self.assertEqual(result.data['frames'], [1, 2.5, 5])
        self.assertEqual(cmds.getAttr(self.cube + '.marker'), 0)
        self.assertEqual(cmds.currentTime(query=True), 20)
        self.assertEqual(cmds.ls(selection=True), [self.other])
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo)

    def test_python_each_frame_namespace_and_one_step_undo(self):
        command = "cmds.setKeyframe(objects[0], attribute='marker', time=frame, value=f)"
        result = self.tool.run(command=command, language='python', **self.args)
        self.assert_success(result)
        self.assertEqual(result.data['completed_frames'], [1, 2.5, 5])
        self.assertEqual(cmds.keyframe(self.cube, attribute='marker', query=True, valueChange=True), [1, 2.5, 5])
        self.assertEqual(cmds.currentTime(query=True), 20)
        self.assertEqual(cmds.ls(selection=True), [self.other])
        cmds.undo()
        self.assertFalse(cmds.listConnections(self.cube + '.marker', source=True, destination=False))

    def test_mel_command_execution_and_preview_has_no_eval(self):
        self.assert_success(self.tool.run(dry_run=True, command='thisProcedureDoesNotExist;', **self.args))
        result = self.tool.run(command='setAttr "' + self.cube + '.marker" 33;', **self.args)
        self.assert_success(result)
        self.assertEqual(cmds.getAttr(self.cube + '.marker'), 33)
        cmds.undo()
        self.assertEqual(cmds.getAttr(self.cube + '.marker'), 0)

    def test_frame_errors_continue_or_stop_and_restore(self):
        command = "if f == 2.5: raise RuntimeError('fixture error')\ncmds.setAttr(objects[0] + '.marker', f)"
        result = self.tool.run(command=command, language='python', **self.args)
        self.assertFalse(result.success)
        self.assertEqual(result.data['completed_frames'], [1, 5])
        self.assertEqual(result.data['errors'][0]['frame'], 2.5)
        self.assertEqual(cmds.currentTime(query=True), 20)
        self.assertEqual(cmds.ls(selection=True), [self.other])
        cmds.undo()
        result = self.tool.run(command=command, language='python', continue_on_error=False, **self.args)
        self.assertEqual(result.data['completed_frames'], [1])
        self.assertEqual(cmds.getAttr(self.cube + '.marker'), 1)

    def test_layer_base_and_all_scheduling_isolated(self):
        cmds.select(self.cube)
        layer = cmds.animLayer('fixtureLayer', addSelectedObjects=True)
        cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=3, value=10)
        cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=4, value=12)
        for layer_name, expected in [('BaseAnimation', [1, 2.5, 5]), (layer, [3, 4]), ('All', [1, 2.5, 3, 4, 5])]:
            result = self.tool.run(dry_run=True, objects=[self.cube], only_in_playback=False, layer=layer_name)
            self.assert_success(result)
            self.assertEqual(result.data['frames'], expected)

    def test_playback_filter_cap_empty_animation_and_invalid_layer(self):
        cmds.playbackOptions(minTime=2, maxTime=4)
        result = self.tool.run(dry_run=True, objects=[self.cube])
        self.assert_success(result)
        self.assertEqual(result.data['frames'], [2.5])
        self.assertFalse(self.tool.run(dry_run=True, max_frames=1, **self.args).success)
        self.assertFalse(self.tool.run(dry_run=True, objects=[self.cube], layer='absent').success)
        empty = self.tool.run(objects=[self.other], command="raise RuntimeError('must not execute')", language='python')
        self.assert_success(empty)
        self.assertEqual(empty.data['count'], 0)

    def test_target_rename_does_not_break_later_frames_or_selection_restore(self):
        cmds.select(self.cube)
        command = "if f == 1: cmds.rename(objects[0], 'renamedFixture')\ncmds.setAttr((cmds.ls(selection=True, long=True) or [])[0] + '.marker', f)"
        result = self.tool.run(command=command, language='python', **self.args)
        self.assert_success(result)
        self.assertEqual(cmds.getAttr('renamedFixture.marker'), 5)
        self.assertEqual(cmds.ls(selection=True), ['renamedFixture'])
        cmds.undo()
        self.assertTrue(cmds.objExists(self.cube))

    def test_deleted_target_reports_remaining_frames_and_restores_other_selection(self):
        result = self.tool.run(command='cmds.delete(objects)', language='python', **self.args)
        self.assertFalse(result.success)
        self.assertEqual(result.data['completed_frames'], [1])
        self.assertEqual(len(result.data['errors']), 2)
        self.assertEqual(cmds.currentTime(query=True), 20)
        self.assertEqual(cmds.ls(selection=True), [self.other])
        cmds.undo()
        self.assertTrue(cmds.objExists(self.cube))

    def test_mel_bridge_source_defines_without_running_ui(self):
        source = (PACKAGE / 'launch_ui.mel').read_text(encoding='utf-8')
        mel.eval(source)
        self.assertIn('Mel procedure', mel.eval('whatIs mayaToolkitAnimLayerKeyRunnerUI'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
