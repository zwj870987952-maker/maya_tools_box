import ast
import copy
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.timeline_enhanced import TimelineEnhancedTool
    TOOL = TimelineEnhancedTool()
from maya_toolkit.tools.timeline_enhanced import model
from maya_toolkit.tools.timeline_enhanced.tool import normalize, file_path
PKG = Path(sys.modules['maya_toolkit.tools.timeline_enhanced'].__file__).parent


class Offline(unittest.TestCase):
    def test_complete_originals_and_all_methods_lazy_schema(self):
        import hashlib
        catalog = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(3, len(catalog['files']))
        for row in catalog['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG / row['archive']).read_bytes()).hexdigest())
            if row['path'].endswith('.py'):
                name = 'native_enhanced.py' if 'enhanced' in row['path'] else 'native_basic.py'
                tree = ast.parse((PKG / name).read_bytes())
                methods = {n.name for c in tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)}
                self.assertEqual(set(catalog['original_methods'][row['path']]), methods)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('timeline_enhanced', TOOL.to_mcp_tool()['name'])
        self.assertIn('blocks', TOOL.parameters_schema['properties']['state']['properties'])

    def test_full_copy_paste_parity_relative_spacing_and_clipping(self):
        source = ast.parse((PKG / 'upstream/maya_timeline_tool_enhanced.py.original').read_bytes())
        cls = next(n for n in source.body if isinstance(n, ast.ClassDef))
        functions = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in ('copy_selected_blocks', 'paste_blocks')]
        scope = {'cmds': SimpleNamespace(intField=lambda *a, **k: 98)}
        exec(compile(ast.Module(body=functions, type_ignores=[]), 'actual_legacy_methods', 'exec'), scope)
        original = SimpleNamespace(blocks={10: {'color': (1., 0., 0.), 'label': 'A'}, 14: {'color': (0., 1., 0.), 'label': 'B'}}, selected_blocks={10, 14}, clipboard={}, start_frame=1, frame_count=100, current_frame_field='fixed_gui_frame', update_blocks_display=lambda: None, update_status=lambda *a: None)
        scope['copy_selected_blocks'](original)
        scope['paste_blocks'](original)
        data = model.document({'blocks': {'10': {'color': [1., 0., 0.], 'label': 'A'}, '14': {'color': [0., 1., 0.], 'label': 'B'}}, 'selected': [10, 14]})
        untouched = copy.deepcopy(data)
        copied = model.transform(data, 'copy')
        pasted = model.transform(copied, 'paste', frame=98)
        self.assertEqual(untouched, data)
        self.assertEqual(model.mapping({str(k): v for k, v in original.blocks.items()}), pasted['blocks'])
        self.assertIn('98', pasted['blocks'])
        self.assertNotIn('102', pasted['blocks'])
        copied['clipboard']['10']['color'][0] = .2
        self.assertEqual(1., data['blocks']['10']['color'][0])

    def test_move_same_frame_selection_conflicts_and_custom_blocks(self):
        state = model.transform(None, 'configure', start_frame=-10, frame_count=20)
        state = model.transform(state, 'add', frame=-5, block_type='effect')
        state = model.transform(state, 'select', frames=[-5])
        self.assertEqual(state, model.transform(state, 'move', source_frame=-5, frame=-5))
        moved = model.transform(state, 'move', source_frame=-5, frame=2)
        self.assertEqual([2], moved['selected'])
        self.assertNotIn('-5', moved['blocks'])
        edited = model.transform(moved, 'edit', frame=2, block={'label': 'Custom', 'color': [.1, .2, .3]})
        self.assertEqual('Custom', edited['blocks']['2']['label'])
        with self.assertRaises(ValueError):
            model.transform(edited, 'add', frame=2)
        added = model.transform(edited, 'add', frame=3)
        before = copy.deepcopy(added)
        with self.assertRaises(ValueError):
            model.transform(added, 'move', source_frame=2, frame=3)
        self.assertEqual(before, added)
        replaced = model.transform(added, 'move', source_frame=2, frame=3, overwrite=True)
        self.assertEqual([3], replaced['selected'])
        self.assertEqual({}, model.transform(replaced, 'delete')['blocks'])
        # Range changes preserve hidden markers.
        self.assertIn('2', model.transform(edited, 'configure', start_frame=100)['blocks'])

    def test_config_and_argument_failures_do_not_mutate(self):
        for raw in (b'{"blocks":{"01":{}}}', b'{"frame_count":1001}', b'{"blocks":{"1":{"color":[2,0,0]}}}', b'{"blocks":{},"blocks":{}}', b'{"selected":[1]}', b'{"unknown":1}'):
            with self.assertRaises(ValueError):
                model.load_bytes(raw)
        for args in ({'action': 'move', 'frame': 1}, {'action': 'inspect', 'overwrite': True}, {'action': 'add', 'frame': True}, {'action': 'select', 'frames': [1, 1]}, {'unknown': 1}, {'action': 'add', 'frame': 1, 'block_type': 'unknown'}):
            with self.assertRaises(ValueError):
                normalize(**args)
        with self.assertRaises(ValueError):
            file_path('relative.json')


if __name__ == '__main__':
    unittest.main(verbosity=2)
