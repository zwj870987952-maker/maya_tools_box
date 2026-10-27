"""Offline contract, parameter, curve filtering and archive integrity checks."""
import ast
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    tool = load_tool()
    tool_module = sys.modules[type(tool).__module__]
    PACKAGE = RC / 'maya_toolkit/tools/anim_layer_bookmark_trimmer'
else:
    from maya_toolkit.tools.anim_layer_bookmark_trimmer import AnimLayerBookmarkTrimmerTool
    tool = AnimLayerBookmarkTrimmerTool()
    tool_module = sys.modules[type(tool).__module__]
    PACKAGE = Path(tool_module.__file__).parent


def load_operations(cmds):
    maya = types.ModuleType('maya')
    maya.cmds = cmds
    maya.mel = types.SimpleNamespace(eval=lambda *_: '')
    with patch.dict(sys.modules, {'maya': maya, 'maya.cmds': cmds, 'maya.mel': maya.mel}):
        spec = importlib.util.spec_from_file_location('bookmark_operations_test', PACKAGE / 'operations.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class OfflineTests(unittest.TestCase):
    def test_parameters_reject_unknown_empty_invalid_and_nonfinite(self):
        for args in ({'extra': 1}, {'objects': []}, {'objects': 7}, {'scope': 'bogus'}, {'mode': 'bogus'},
                     {'strength': float('nan')}, {'bias': 1.1}, {'include_scale': 1}, {'layer': ''}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                tool_module.normalize(args)
        self.assertEqual(tool_module.normalize({'objects': 'cube'})['objects'], ['cube'])

    def test_schema_exports_exact_supported_parameters(self):
        schema = tool.to_openai_tool()['function']['parameters']
        self.assertEqual(set(schema['properties']), set(tool_module.DEFAULTS))
        self.assertFalse(schema['additionalProperties'])
        self.assertEqual(tool.to_mcp_tool()['inputSchema'], schema)

    def test_query_never_loads_bookmark_plugin(self):
        cmds = types.SimpleNamespace(pluginInfo=lambda *a, **k: False,
                                     loadPlugin=lambda *a, **k: self.fail('Plugin loaded in query'))
        with self.assertRaises(RuntimeError):
            load_operations(cmds).get_bookmark_details()

    def test_curve_query_normalizes_single_name_and_includes_other_float(self):
        plugs = ['cube.translateX', 'cube.customFloat', 'cube.visibility', 'cube.switch', 'cube.scaleX']
        types_by_attr = dict(translateX='doubleLinear', customFloat='double', visibility='bool', switch='enum', scaleX='double')
        cmds = types.SimpleNamespace(ls=lambda **k: ['BaseAnimation'], listAnimatable=lambda o: plugs,
                                    getAttr=lambda p, **k: types_by_attr[p.split('.')[-1]],
                                    animLayer=lambda l, **k: 'curve_' + k['findCurveForPlug'].split('.')[-1],
                                    objExists=lambda n: True, nodeType=lambda n: 'animCurveTL')
        op = load_operations(cmds)
        curves = op.get_layer_curves_for_objects(['cube'], 'BaseAnimation', include_others=True, channel_box_priority=False)
        self.assertEqual(curves, ['curve_customFloat', 'curve_translateX'])
        op.get_selected_channel_box_attributes = lambda: ['scaleX', 'visibility']
        self.assertEqual(op.get_layer_curves_for_objects(['cube'], 'BaseAnimation'), ['curve_scaleX'])

    def test_base_fallback_is_only_allowed_without_animation_layers(self):
        cmds = types.SimpleNamespace(ls=lambda **k: ['OtherLayer'], listAnimatable=lambda o: ['cube.translateX'],
                                    getAttr=lambda *a, **k: 'doubleLinear',
                                    listConnections=lambda *a, **k: self.fail('Fallback crossed layers'))
        self.assertEqual(load_operations(cmds).get_layer_curves_for_objects(['cube'], 'BaseAnimation', channel_box_priority=False), [])

    def test_boundary_insertion_errors_are_not_hidden(self):
        def failed_insert(*a, **k):
            raise RuntimeError('locked curve')
        op = load_operations(types.SimpleNamespace(keyframe=lambda *a, **k: [], setKeyframe=failed_insert))
        with self.assertRaisesRegex(RuntimeError, 'locked curve'):
            op._ensure_boundary_keys_on_curve('curve', 1, 5)

    def test_all_modes_preserved_and_ui_routes_four_actions(self):
        source = (PACKAGE / 'operations.py').read_text(encoding='utf-8')
        for name in tool_module.MODES:
            self.assertIn('"' + name + '"', source)
        tree = ast.parse((PACKAGE / 'ui.py').read_text(encoding='utf-8'))
        callbacks = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('_on_')]
        self.assertEqual(len(callbacks), 4)
        for callback in callbacks:
            self.assertTrue(any(isinstance(n, ast.Attribute) and n.attr == '_dispatch' for n in ast.walk(callback)))

    def test_upstream_archive_matches_original_when_staged(self):
        upstream = PACKAGE / 'upstream'
        if (RC / 'launch_candidate.py').exists():
            for name in ('anim_layer_bookmark_trimmer.py', 'README.md'):
                self.assertEqual((upstream / name).read_bytes(), (RC.parent / name).read_bytes())
        else:
            self.assertTrue((upstream / 'anim_layer_bookmark_trimmer.py').is_file())


if __name__ == '__main__':
    unittest.main(verbosity=2)
