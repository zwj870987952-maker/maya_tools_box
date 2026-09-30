"""Offline validation, frame lookup and command execution separation tests."""
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
    MODULE = sys.modules[type(tool).__module__]
    PACKAGE = RC / 'maya_toolkit/tools/anim_layer_key_runner'
else:
    from maya_toolkit.tools.anim_layer_key_runner import AnimLayerKeyRunnerTool
    tool = AnimLayerKeyRunnerTool()
    MODULE = sys.modules[type(tool).__module__]
    PACKAGE = Path(MODULE.__file__).parent


def load_operations(cmds):
    maya = types.ModuleType('maya')
    maya.cmds, maya.mel = cmds, types.SimpleNamespace(eval=lambda *a: None)
    with patch.dict(sys.modules, {'maya': maya, 'maya.cmds': cmds, 'maya.mel': maya.mel}):
        spec = importlib.util.spec_from_file_location('key_runner_operations_test', PACKAGE / 'operations.py')
        op = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(op)
    return op


class OfflineTests(unittest.TestCase):
    def test_validation_rejects_unknown_empty_bad_types_and_invalid_python(self):
        for args in ({'unknown': 1}, {'objects': []}, {'objects': 4}, {'command': ''}, {'language': 'shell'},
                     {'only_in_playback': 1}, {'max_frames': True}, {'max_frames': 0}, {'layer': ''}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                MODULE.normalize(args)
        with self.assertRaises(SyntaxError):
            MODULE.normalize({'language': 'python', 'command': 'def broken('})

    def test_normalize_compiles_without_executing_python(self):
        args = MODULE.normalize({'objects': 'cube', 'language': 'python', 'command': "raise RuntimeError('must not execute')"})
        self.assertEqual(args['objects'], ['cube'])
        self.assertTrue(args['continue_on_error'])

    def test_schema_exact_parameters_and_both_export_protocols(self):
        schema = tool.to_openai_tool()['function']['parameters']
        self.assertEqual(set(schema['properties']), set(MODULE.DEFAULTS))
        self.assertFalse(schema['additionalProperties'])
        self.assertEqual(tool.to_mcp_tool()['inputSchema'], schema)

    def test_curve_name_string_layer_isolation_and_dedup(self):
        def ls(*args, **kwargs):
            return ['BaseAnimation', 'layerA']
        cmds = types.SimpleNamespace(ls=ls, listAnimatable=lambda o: [o + '.translateX'],
                                    animLayer=lambda l, **kw: l + '_curve', objExists=lambda n: True,
                                    nodeType=lambda n: 'animCurveTL',
                                    keyframe=lambda *a, **k: [1, 1.0002, 2.75, 1, 3],
                                    listConnections=lambda *a, **k: self.fail('Cross-layer fallback'))
        op = load_operations(cmds)
        frames, layer, curves = op.get_keyframes_from_layer(['cube'], 'All', False)
        self.assertEqual(frames, [1, 2.75, 3])
        self.assertEqual(curves, ['BaseAnimation_curve', 'layerA_curve'])
        self.assertEqual(op.get_keyframes_from_layer(['cube'], 'BaseAnimation', False)[2], ['BaseAnimation_curve'])

    def test_missing_base_does_not_fallback_through_other_layer(self):
        cmds = types.SimpleNamespace(ls=lambda *a, **k: ['layerA'], listAnimatable=lambda o: [o + '.tx'],
                                    listConnections=lambda *a, **k: self.fail('Cross-layer fallback'))
        self.assertEqual(load_operations(cmds).get_layer_curves_for_objects(['cube'], 'BaseAnimation'), [])

    def test_invalid_layer_and_nonfinite_frames_fail(self):
        cmds = types.SimpleNamespace(ls=lambda *a, **k: [], listAnimatable=lambda o: [o + '.tx'],
                                    listConnections=lambda *a, **k: ['curve'], objExists=lambda n: True,
                                    nodeType=lambda n: 'animCurveTL', keyframe=lambda *a, **k: [float('nan')])
        op = load_operations(cmds)
        with self.assertRaises(ValueError):
            op.get_keyframes_from_layer(['cube'], 'missing', False)
        with self.assertRaisesRegex(ValueError, 'Non-finite'):
            op.get_keyframes_from_layer(['cube'], 'BaseAnimation', False)

    def test_native_callbacks_overridden_and_mel_bridge_not_auto_executed(self):
        tree = ast.parse((PACKAGE / 'ui.py').read_text(encoding='utf-8'))
        callbacks = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in ('_on_execute', '_on_inspect')]
        self.assertEqual(len(callbacks), 2)
        for n in callbacks:
            self.assertTrue(any(isinstance(a, ast.Attribute) and a.attr == '_dispatch' for a in ast.walk(n)))
        source = (PACKAGE / 'launch_ui.mel').read_text(encoding='utf-8')
        self.assertTrue(source.strip().endswith('}'))
        self.assertIn('global proc mayaToolkitAnimLayerKeyRunnerUI()', source)

    def test_complete_original_python_mel_readme_archive(self):
        for name in ('anim_layer_key_runner.py', 'anim_layer_key_runner.mel', 'README.md'):
            archived = PACKAGE / 'upstream' / name
            self.assertTrue(archived.is_file())
            if (RC / 'launch_candidate.py').exists():
                self.assertEqual(archived.read_bytes(), (RC.parent / name).read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
