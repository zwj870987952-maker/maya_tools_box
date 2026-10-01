import copy
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only temporary isolated Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()


def scene():
    return (cmds.ls(long=True), cmds.ls(selection=True), cmds.currentTime(query=True), cmds.keyframe('foreign', query=True, timeChange=True), cmds.keyframe('foreign', query=True, valueChange=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.createNode('transform', name='foreign')
        cmds.setKeyframe('foreign', attribute='tx', time=1, value=3)
        cmds.select('foreign')

    def test_document_actions_and_preview_never_move_scene_keys(self):
        state = TOOL.run(action='add', frame=10, block_type='camera').data['state']
        state = TOOL.run(action='select', state=state, frames=[10]).data['state']
        state = TOOL.run(action='copy', state=state).data['state']
        before = scene()
        original = copy.deepcopy(state)
        dry = TOOL.run(dry_run=True, action='move', state=state, source_frame=10, frame=20)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, scene())
        result = TOOL.run(action='paste', state=state, frame=30)
        self.assertTrue(result.success, result.message)
        self.assertIn('30', result.data['state']['blocks'])
        self.assertEqual(original, state)
        self.assertEqual(before[:5], scene()[:5])
        self.assertFalse(TOOL.run(action='move', state=result.data['state'], source_frame=10, frame=30).success)

    def test_json_temp_save_backups_bad_load_and_dry_run(self):
        state = TOOL.run(action='add', frame=5).data['state']
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'plan.json'
            before = scene()
            self.assertTrue(TOOL.run(dry_run=True, action='save', state=state, path=str(path)).success)
            self.assertEqual(before, scene())
            self.assertFalse(path.exists())
            self.assertTrue(TOOL.run(action='save', state=state, path=str(path)).success)
            old = path.read_bytes()
            self.assertFalse(TOOL.run(action='save', path=str(path)).success)
            self.assertEqual(old, path.read_bytes())
            result = TOOL.run(action='save', path=str(path), overwrite=True)
            self.assertTrue(result.success, result.message)
            self.assertEqual(old, Path(result.data['backup']).read_bytes())
            path.write_text('{"blocks":{"1":{"color":[2,0,0]}}}', encoding='utf-8')
            self.assertFalse(TOOL.run(action='load', state=state, path=str(path)).success)
            self.assertEqual('K', state['blocks']['5']['label'])
            self.assertEqual(before[:5], scene()[:5])

    def test_sync_time_batch_play_refusal_and_complete_native_import_no_ui(self):
        cmds.playbackOptions(minTime=-10, maxTime=20)
        before = scene()
        dry = TOOL.run(dry_run=True, action='sync')
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(-10, dry.data['state']['start_frame'])
        self.assertEqual(31, dry.data['state']['frame_count'])
        self.assertEqual(before, scene())
        self.assertTrue(TOOL.run(dry_run=True, action='set_current_frame', frame=5).success)
        self.assertEqual(before, scene())
        self.assertTrue(TOOL.run(action='set_current_frame', frame=5).success)
        self.assertEqual(5, cmds.currentTime(query=True))
        self.assertFalse(TOOL.run(action='play').success)
        from maya_toolkit.tools.timeline_enhanced.ui import BasicUI, EnhancedUI
        # Constructors only initialize Python state: no QWidget/window created.
        basic, enhanced = BasicUI(TOOL), EnhancedUI(TOOL)
        self.assertIsNone(enhanced.config_file)
        self.assertEqual({}, basic.snapshot()['blocks'])
        self.assertEqual(6, len(enhanced.block_types))
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()
        cmds.playbackOptions(minTime=1.5, maxTime=20.5)
        self.assertFalse(TOOL.run(action='sync').success)


if __name__ == '__main__':
    unittest.main(verbosity=2)
