import json
import os
from pathlib import Path
import runpy
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.timeline_marker import runtime
from maya_toolkit.tools.timeline_marker.native import add, remove, clear, set as set_markers


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=True)
        self.node = cmds.createNode('transform', name='control')
        cmds.setKeyframe(self.node, attribute='tx', time=1, value=2)
        cmds.setKeyframe(self.node, attribute='tx', time=20, value=40)
        cmds.currentTime(7)
        cmds.select(self.node)
        cmds.flushUndo()

    def run_ok(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    def state(self):
        return (cmds.fileInfo('timelineMarkers', query=True), cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.autoKeyframe(query=True, state=True), cmds.keyframe(self.node, query=True, valueChange=True), cmds.undoInfo(query=True, undoName=True), cmds.file(query=True, modified=True), cmds.pluginInfo(query=True, listPlugins=True))

    def test_readonly_undo_redo_and_complete_commands(self):
        before = self.state()
        self.assertTrue(TOOL.run(dry_run=True, action='add', frames=[1, 2], comment='test').success)
        self.assertEqual(0, self.run_ok(action='inspect')['count'])
        self.assertEqual(before, self.state())
        original_keys = cmds.keyframe(self.node, query=True, valueChange=True)
        self.run_ok(action='add', frames=[1, 2], color=[12, 32, 64], comment='中文 "quote" \\ path\nnext')
        stored = cmds.fileInfo('timelineMarkers', query=True)
        self.assertEqual([1, 2], runtime.read_scene()['frames'])
        self.assertEqual('中文 "quote" \\ path\nnext', runtime.read_scene()['comments'][0])
        cmds.undo()
        self.assertFalse(cmds.fileInfo('timelineMarkers', query=True))
        cmds.redo()
        self.assertEqual(stored, cmds.fileInfo('timelineMarkers', query=True))
        add(2, [1, 2, 3], 'overwrite')
        self.assertEqual('overwrite', runtime.read_scene()['comments'][1])
        cmds.undo()
        self.assertEqual(stored, cmds.fileInfo('timelineMarkers', query=True))
        remove([1, 2])
        self.assertEqual(0, len(runtime.read_scene()['frames']))
        cmds.undo()
        self.assertEqual(stored, cmds.fileInfo('timelineMarkers', query=True))
        set_markers([4, 5], [[0, 0, 255], [255, 0, 0]], ['a', 'b'])
        self.assertEqual([4, 5], runtime.read_scene()['frames'])
        cmds.undo()
        clear()
        self.assertEqual(0, len(runtime.read_scene()['frames']))
        cmds.undo()
        self.assertEqual(stored, cmds.fileInfo('timelineMarkers', query=True))
        self.assertEqual(original_keys, cmds.keyframe(self.node, query=True, valueChange=True))
        self.assertEqual(7, cmds.currentTime(query=True))
        self.assertEqual([self.node], cmds.ls(selection=True))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertFalse(TOOL.validate(action='open_ui').success)
        self.assertFalse(TOOL.validate(action='hotkey').success)

    def test_old_format_saved_scene_and_colliding_remap(self):
        old = {'frames': [1, 2, 3, 4], 'colors': [[0, 255, 0]] * 4, 'comments': ['a', 'b', 'c', '中文 "slash \\ newline\n']}
        cmds.fileInfo('timelineMarkers', json.dumps(old, ensure_ascii=True))
        raw = cmds.fileInfo('timelineMarkers', query=True)
        self.assertEqual(old, runtime.read_scene())
        self.run_ok(action='remap', old_range=[1, 3], new_range=[2, 4])
        data = runtime.read_scene()
        self.assertEqual({2: 'a', 3: 'b', 4: 'c'}, dict(zip(data['frames'], data['comments'])))
        cmds.undo()
        self.assertEqual(raw, cmds.fileInfo('timelineMarkers', query=True))
        for extension, filetype in (('ma', 'mayaAscii'), ('mb', 'mayaBinary')):
            with tempfile.TemporaryDirectory() as directory:
                file = str(Path(directory) / ('fixture.' + extension))
                cmds.file(rename=file)
                cmds.file(save=True, type=filetype, force=True)
                cmds.file(new=True, force=True)
                cmds.file(file, open=True, force=True)
                self.assertEqual(old, runtime.read_scene())
                self.run_ok(action='add', frames=[8], comment='fresh')
                cmds.undo()
                self.assertEqual(old, runtime.read_scene())

    def test_malformed_metadata_strict_validation_and_failure_undo(self):
        cmds.fileInfo('timelineMarkers', '{broken')
        before = self.state()
        self.assertFalse(TOOL.validate(action='clear').success)
        self.assertFalse(TOOL.run(action='add', frames=[1]).success)
        self.assertEqual(before, self.state())
        cmds.fileInfo(remove='timelineMarkers')
        self.run_ok(action='add', frames=[1])
        raw = cmds.fileInfo('timelineMarkers', query=True)
        cmds.undoInfo(state=False)
        self.assertFalse(TOOL.validate(action='clear').success)
        cmds.undoInfo(state=True)
        command = getattr(cmds, runtime.COMMAND)
        def injected(*args, **kwargs):
            command(*args, **kwargs)
            raise RuntimeError('injected after metadata command')
        with patch.object(cmds, runtime.COMMAND, injected):
            result = TOOL.run(action='add', frames=[9])
        self.assertFalse(result.success)
        self.assertFalse(runtime.ACTIVE)
        cmds.undo()
        self.assertEqual(raw, cmds.fileInfo('timelineMarkers', query=True))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertEqual(7, cmds.currentTime(query=True))

    def test_callback_ownership_protocol_without_qt(self):
        # timeControl is a shim; real API callback registration is exercised, no Qt GUI.
        from maya_toolkit.tools.timeline_marker import gui_bridge as bridge
        state = {'press': 'oldPress;', 'release': 'oldRelease;'}
        events = []
        def control(name, **kwargs):
            if kwargs.get('exists'):
                return True
            for key in state:
                option = key + 'Command'
                if option in kwargs:
                    if kwargs.get('query'):
                        return state[key]
                    state[key] = kwargs[option]
        w = SimpleNamespace(readFromCurrentScene=lambda *args: events.append('read'), pressCommand=lambda *args: events.append('press'), releaseCommand=lambda *args: events.append('release'))
        utils_name = 'maya_toolkit.tools.timeline_marker.native.utils'
        utils = SimpleNamespace(getMayaTimeline=lambda: 'fixtureTimeline')
        with patch.dict(sys.modules, {utils_name: utils}), patch.object(cmds, 'timeControl', control), patch.object(bridge.mel, 'eval', lambda script: events.append(script)):
            bridge.add_callbacks(w)
            self.assertEqual(4, len(w._callbacks))
            bridge.dispatch(w._token, 'press')
            bridge.dispatch(w._token, 'release')
            self.assertEqual(['oldPress;', 'press', 'release', 'oldRelease;'], events)
            self.run_ok(action='add', frames=[1])
            cmds.undo()
            self.assertIn('read', events)
            state['release'] = 'laterForeignRelease;'
            bridge.remove_callbacks(w)
            self.assertEqual('oldPress;', state['press'])
            self.assertEqual('laterForeignRelease;', state['release'])
            self.assertEqual([], w._callbacks)
            self.assertIsNone(w._token)
            bridge.remove_callbacks(w)
        self.assertFalse(bridge._HOOKS)


if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    finally:
        maya.standalone.uninitialize()
