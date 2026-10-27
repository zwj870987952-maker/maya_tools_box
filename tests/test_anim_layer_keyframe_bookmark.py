"""Pure plans/Schema plus source integrity; no Maya scene or entry execution."""
import ast
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    tool = load_tool()
    MODULE = sys.modules[type(tool).__module__]
    PACKAGE = RC / 'maya_toolkit/tools/anim_layer_keyframe_bookmark'
else:
    from maya_toolkit.tools.anim_layer_keyframe_bookmark import AnimLayerKeyframeBookmarkTool
    tool = AnimLayerKeyframeBookmarkTool()
    MODULE = sys.modules[type(tool).__module__]
    PACKAGE = Path(MODULE.__file__).parent


class OfflineTests(unittest.TestCase):
    def test_schema_matches_supported_parameters_and_protocols(self):
        schema = tool.to_openai_tool()['function']['parameters']
        self.assertEqual(set(schema['properties']), set(MODULE.DEFAULTS))
        self.assertFalse(schema['additionalProperties'])
        self.assertEqual(tool.to_mcp_tool()['inputSchema'], schema)

    def test_invalid_parameters_rejected(self):
        for args in ({'extra': 1}, {'action': 'deleteNode'}, {'palette_name': 'missing'}, {'prefix': ''},
                     {'prefix': 'x'*241}, {'objects': []}, {'objects': 7}, {'layer': ''},
                     {'max_bookmarks': True}, {'max_bookmarks': 0}, {'clear_existing': 1}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                MODULE.normalize(args)
        self.assertEqual(MODULE.normalize({'objects': 'cube'})['objects'], ['cube'])

    def test_all_four_palettes_alternate_including_wraparound(self):
        for palette in ('dual', 'vibrant', 'pastel', 'cyberpunk'):
            colors = MODULE.COLOR_PALETTES[palette]['colors']
            intervals = MODULE.plan_intervals(list(range(0, len(colors)*3)), palette, 'BM')
            self.assertTrue(all(a['color'] != b['color'] for a, b in zip(intervals, intervals[1:])))
            self.assertEqual([i['priority'] for i in intervals], list(range(len(intervals))))

    def test_interval_plan_preserves_subframes_and_original_rounded_display_name(self):
        plan = MODULE.plan_intervals([1.1, 1.2, 2.75], 'dual', '节奏')
        self.assertEqual([(p['start'], p['stop']) for p in plan], [(1.1, 1.2), (1.2, 2.75)])
        self.assertEqual(plan[0]['name'], '节奏_1_1')
        self.assertEqual(plan[1]['name'], '节奏_1_3')

    def test_invalid_interval_inputs_rejected(self):
        for times in ([], [1], [1, 1], [2, 1], [1, float('inf')], [float('nan'), 2]):
            with self.subTest(times=times), self.assertRaises(ValueError):
                MODULE.plan_intervals(times, 'dual', 'BM')

    def test_palettes_exact_original_and_archive_byte_identical(self):
        archived = PACKAGE / 'upstream/anim_layer_keyframe_bookmark.py'
        tree = ast.parse(archived.read_text(encoding='utf-8'))
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'COLOR_PALETTES' for t in n.targets))
        self.assertEqual(ast.literal_eval(assignment.value), MODULE.COLOR_PALETTES)
        if (RC / 'launch_candidate.py').exists():
            for name in ('anim_layer_keyframe_bookmark.py', 'README.md'):
                self.assertEqual((PACKAGE / 'upstream' / name).read_bytes(), (RC.parent / name).read_bytes())

    def test_native_three_actions_override_original_callbacks(self):
        tree = ast.parse((PACKAGE / 'ui.py').read_text(encoding='utf-8'))
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        self.assertTrue({'_on_execute', '_on_clear_all', '_on_inspect_keys'} <= names)
        self.assertIn('self.tool.run(dry_run=True', (PACKAGE / 'ui.py').read_text(encoding='utf-8'))

    def test_runtime_has_no_staging_dependency_or_plugin_autoload_in_preflight(self):
        source = (PACKAGE / 'layer_queries.py').read_text(encoding='utf-8') + (PACKAGE / 'tool.py').read_text(encoding='utf-8')
        self.assertNotIn('tools_staging_pool', source)
        self.assertNotIn('loadPlugin(', source)
        self.assertNotIn('writeRequires', ast.get_source_segment((PACKAGE / 'tool.py').read_text(encoding='utf-8'),
                         next(n for n in ast.walk(ast.parse((PACKAGE / 'tool.py').read_text(encoding='utf-8'))) if isinstance(n, ast.FunctionDef) and n.name == '_prepare')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
