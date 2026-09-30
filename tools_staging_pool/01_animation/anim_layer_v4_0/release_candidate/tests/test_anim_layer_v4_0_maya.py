"""Intact NoUI suite checks; complete editor deliberately requires real GUI."""
import os
from pathlib import Path
import sys
import unittest

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use disposable mayapy; tests replace the scene and load global MEL')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.anim_layer_v4_0 import AnimLayerSuiteTool
    load_tool = AnimLayerSuiteTool


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.cube = cmds.polyCube()[0]
        for time in (1, 2.5, 5):
            cmds.setKeyframe(self.cube, attribute='translateX', time=time, value=time)
        cmds.select(self.cube)
        self.tool = load_tool()

    def assert_success(self, result):
        self.assertTrue(result.success, result.to_json())

    def test_preflight_does_not_source_and_preserves_scene_queue(self):
        before = mel.eval('whatIs "get_anim_time_range_from_anim_layer";')
        undo = cmds.undoInfo(query=True, undoName=True)
        time = cmds.currentTime(query=True)
        selection = cmds.ls(selection=True)
        result = self.tool.run(dry_run=True, action='invoke', procedure='get_anim_time_range_from_anim_layer', arguments={'anim_layer_name': 'BaseAnimation'})
        self.assert_success(result)
        self.assertEqual(mel.eval('whatIs "get_anim_time_range_from_anim_layer";'), before)
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo)
        self.assertEqual(cmds.currentTime(query=True), time)
        self.assertEqual(cmds.ls(selection=True), selection)

    def test_original_noui_load_and_query_base_and_named_layer(self):
        self.assert_success(self.tool.run(action='load'))
        result = self.tool.run(action='invoke', procedure='get_anim_time_range_from_anim_layer', arguments={'anim_layer_name': 'BaseAnimation'})
        self.assert_success(result)
        self.assertEqual(result.data['return_value'], [1, 5])
        layer = cmds.animLayer('fixtureLayer', addSelectedObjects=True)
        for time in (3, 7):
            cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=time, value=time)
        result = self.tool.run(action='invoke', procedure='get_anim_time_range_from_anim_layer', arguments={'anim_layer_name': layer})
        self.assert_success(result)
        self.assertEqual(result.data['return_value'], [3, 7])

    def test_string_array_selection_and_one_step_undo(self):
        other = cmds.polySphere()[0]
        cmds.select(self.cube)
        result = self.tool.run(action='invoke', procedure='select_skip_no_exist', arguments={'objs': [other, 'missingFixture']})
        self.assert_success(result)
        self.assertEqual(result.data['return_value'], [other])
        self.assertEqual(cmds.ls(selection=True), [other])
        cmds.undo()
        self.assertEqual(cmds.ls(selection=True), [self.cube])

    def test_explicit_layer_selection_and_multilayer_time_array(self):
        first = cmds.animLayer('fixtureA', addSelectedObjects=True)
        second = cmds.animLayer('fixtureB', addSelectedObjects=True)
        for layer, times in ((first, (2, 4)), (second, (6, 9))):
            for time in times:
                cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=time, value=time)
        result = self.tool.run(action='invoke', procedure='get_anim_time_range_from_multiply_anim_layers', arguments={'anim_layers_name': [first, second]})
        self.assert_success(result)
        self.assertEqual(result.data['return_value'], [2, 9])
        result = self.tool.run(action='invoke', procedure='select_few_Layers', arguments={'layers': [second]})
        self.assert_success(result)
        self.assertTrue(cmds.animLayer(second, query=True, selected=True))
        self.assertFalse(cmds.animLayer(first, query=True, selected=True))

    def test_numeric_types_and_untrusted_string_cannot_escape_outer_call(self):
        result = self.tool.run(action='invoke', procedure='select_skip_no_exist', arguments={'objs': ['absent\";delete ' + self.cube + ';\"']})
        self.assert_success(result)
        self.assertTrue(cmds.objExists(self.cube))
        self.assertFalse(self.tool.run(dry_run=True, action='invoke', procedure='select_few_Layers', arguments={'layers': [4]}).success)

    def test_noui_all_declarations_source_from_intact_package(self):
        self.assert_success(self.tool.run(action='load', force_reload=True))
        inventory = self.tool.run(dry_run=True, action='inventory')
        self.assert_success(inventory)
        for name in inventory.data['procedures']:
            origin = mel.eval('whatIs "' + name + '";')
            self.assertIn('layerEditor_no_UI.mel', origin, name)

    def test_full_editor_and_ui_only_procedures_are_refused_in_standalone(self):
        self.assertFalse(self.tool.run(action='load', edition='full').success)
        self.assertFalse(self.tool.run(action='open_ui').success)
        self.assertFalse(self.tool.run(action='invoke', procedure='create_and_select_anim_layer', arguments={'rotation_mod': 1}).success)

    def test_runtime_restores_evaluation_mode_and_reports_original_mel_error(self):
        self.assert_success(self.tool.run(action='load'))
        runtime = sys.modules[type(self.tool).__module__.rsplit('.', 1)[0] + '.runtime']
        before = cmds.evaluationManager(query=True, mode=True)
        result = runtime.invoke('evaluationManager -mode "off"; error "fixture failure";', True)
        self.assertIn('fixture failure', result['error'])
        self.assertEqual(cmds.evaluationManager(query=True, mode=True), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
