"""Only run in disposable mayapy; tests create scenes and bookmarks."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use isolated mayapy runner; tests replace the scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.anim_layer_keyframe_bookmark import AnimLayerKeyframeBookmarkTool
    load_tool = AnimLayerKeyframeBookmarkTool


def bookmark_snapshot():
    return {n: dict(start=cmds.getAttr(n + '.timeRangeStart'), stop=cmds.getAttr(n + '.timeRangeStop'),
                    name=cmds.getAttr(n + '.name'), color=cmds.getAttr(n + '.color'),
                    priority=cmds.getAttr(n + '.priority')) for n in cmds.ls(type='timeSliderBookmark') or []}


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.loadPlugin('timeSliderBookmark', quiet=True)
        self.cube = cmds.polyCube()[0]
        for time in (1, 2.5, 5):
            cmds.setKeyframe(self.cube, attribute='translateX', time=time, value=time)
        self.other = cmds.polySphere()[0]
        self.old = cmds.createNode('timeSliderBookmark', skipSelect=True)
        self.old_id = cmds.ls(self.old, uuid=True)[0]
        cmds.setAttr(self.old + '.name', 'unrelated old bookmark', type='string')
        cmds.setAttr(self.old + '.timeRangeStart', -3)
        cmds.setAttr(self.old + '.timeRangeStop', -1)
        cmds.currentTime(20)
        cmds.select(self.other)
        self.tool = load_tool()
        self.args = dict(objects=[self.cube], layer='BaseAnimation')

    def assert_success(self, result):
        self.assertTrue(result.success, result.to_json())

    def test_dry_run_previews_intervals_deletion_colors_without_scene_writes(self):
        before = bookmark_snapshot()
        undo = cmds.undoInfo(query=True, undoName=True)
        requirement = cmds.pluginInfo('timeSliderBookmark', query=True, writeRequires=True)
        result = self.tool.run(dry_run=True, clear_existing=True, **self.args)
        self.assert_success(result)
        self.assertEqual(result.data['deleted_bookmarks'], [self.old])
        self.assertEqual([(i['start'], i['stop']) for i in result.data['intervals']], [(1, 2.5), (2.5, 5)])
        self.assertEqual(bookmark_snapshot(), before)
        self.assertEqual(cmds.currentTime(query=True), 20)
        self.assertEqual(cmds.ls(selection=True), [self.other])
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo)
        self.assertEqual(cmds.pluginInfo('timeSliderBookmark', query=True, writeRequires=True), requirement)

    def test_four_palettes_generate_alternate_with_single_undo(self):
        for palette in ('dual', 'vibrant', 'pastel', 'cyberpunk'):
            with self.subTest(palette=palette):
                before = bookmark_snapshot()
                result = self.tool.run(palette_name=palette, **self.args)
                self.assert_success(result)
                self.assertEqual(result.data['count'], 2)
                nodes = result.data['bookmarks']
                self.assertNotEqual(cmds.getAttr(nodes[0] + '.color'), cmds.getAttr(nodes[1] + '.color'))
                for node, planned in zip(nodes, result.data['intervals']):
                    self.assertAlmostEqual(cmds.getAttr(node + '.timeRangeStart'), planned['start'])
                    self.assertAlmostEqual(cmds.getAttr(node + '.timeRangeStop'), planned['stop'])
                    self.assertEqual(cmds.getAttr(node + '.name'), planned['name'])
                    self.assertEqual(cmds.getAttr(node + '.priority'), planned['priority'])
                self.assertEqual(cmds.currentTime(query=True), 20)
                self.assertEqual(cmds.ls(selection=True), [self.other])
                cmds.undo()
                self.assertEqual(bookmark_snapshot(), before)

    def test_clear_existing_and_clear_action_undo_entire_scene_bookmarks(self):
        before = bookmark_snapshot()
        result = self.tool.run(clear_existing=True, **self.args)
        self.assert_success(result)
        self.assertEqual(cmds.ls(self.old_id), [])
        self.assertEqual(len(cmds.ls(type='timeSliderBookmark')), 2)
        cmds.undo()
        self.assertEqual(bookmark_snapshot(), before)
        cmds.select(clear=True)
        result = self.tool.run(action='clear')
        self.assert_success(result)
        self.assertEqual(result.data['count'], 1)
        self.assertEqual(cmds.ls(type='timeSliderBookmark'), [])
        cmds.undo()
        self.assertEqual(bookmark_snapshot(), before)

    def test_locked_bookmark_rejects_before_any_creation_or_deletion(self):
        cmds.lockNode(self.old, lock=True)
        before = bookmark_snapshot()
        self.assertFalse(self.tool.run(clear_existing=True, **self.args).success)
        self.assertFalse(self.tool.run(action='clear').success)
        self.assertEqual(bookmark_snapshot(), before)
        self.assert_success(self.tool.run(clear_existing=False, **self.args))

    def test_inspect_empty_animation_and_generation_count_cap(self):
        result = self.tool.run(dry_run=True, action='inspect', objects=[self.other])
        self.assert_success(result)
        self.assertEqual(result.data['keyframes'], [])
        before = bookmark_snapshot()
        self.assertFalse(self.tool.run(objects=[self.other], clear_existing=True).success)
        self.assertFalse(self.tool.run(max_bookmarks=1, clear_existing=True, **self.args).success)
        self.assertEqual(bookmark_snapshot(), before)

    def test_layer_specific_and_all_keyframes_do_not_cross_layers(self):
        cmds.select(self.cube)
        layer = cmds.animLayer('fixtureLayer', addSelectedObjects=True)
        for time in (3, 4):
            cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=time, value=20)
        for name, frames in [('BaseAnimation', [1, 2.5, 5]), (layer, [3, 4]), ('All', [1, 2.5, 3, 4, 5])]:
            result = self.tool.run(dry_run=True, objects=[self.cube], layer=name)
            self.assert_success(result)
            self.assertEqual(result.data['keyframes'], frames)

    def test_plugin_not_loaded_query_fails_without_loading_or_writing(self):
        before = bookmark_snapshot()
        tool_module = sys.modules[type(self.tool).__module__]
        self.tool.validate(**self.args)
        query = sys.modules[tool_module.__package__ + '.layer_queries']
        original_info = cmds.pluginInfo
        def plugin_info(name, **kwargs):
            if kwargs.get('loaded'):
                return False
            return original_info(name, **kwargs)
        with patch.object(query.cmds, 'pluginInfo', side_effect=plugin_info), patch.object(query.cmds, 'loadPlugin', side_effect=AssertionError('Loaded during preflight')):
            self.assertFalse(self.tool.run(dry_run=True, **self.args).success)
            self.assert_success(self.tool.run(dry_run=True, action='inspect', **self.args))
        self.assertEqual(bookmark_snapshot(), before)

    def test_partial_attribute_failure_reports_created_node_and_can_undo(self):
        self.tool.validate(**self.args)
        query = sys.modules[type(self.tool).__module__.rsplit('.', 1)[0] + '.layer_queries']
        original_set = cmds.setAttr
        def set_attribute(plug, *args, **kwargs):
            if plug.endswith('.color'):
                raise RuntimeError('fixture color failure')
            return original_set(plug, *args, **kwargs)
        before = bookmark_snapshot()
        with patch.object(query.cmds, 'setAttr', side_effect=set_attribute):
            result = self.tool.run(clear_existing=True, **self.args)
        self.assertFalse(result.success)
        self.assertEqual(len(result.data['bookmarks']), 1)
        self.assertEqual(result.data['deleted_bookmarks'], [self.old])
        self.assertIn('fixture color failure', result.errors[0])
        cmds.undo()
        self.assertEqual(bookmark_snapshot(), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
