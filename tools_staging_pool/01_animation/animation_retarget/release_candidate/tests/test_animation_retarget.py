"""Offline configuration and complete source/GUI adaptation checks."""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').is_file():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/animation_retarget'
else:
    from maya_toolkit.tools.animation_retarget import AnimationRetargetTool
    load_tool = AnimationRetargetTool
    PACKAGE = Path(sys.modules[AnimationRetargetTool.__module__].__file__).parent
tool = load_tool()
contracts = sys.modules[tool.__class__.__module__.rsplit('.', 1)[0] + '.contracts']


class OfflineTests(unittest.TestCase):
    def test_legacy_config_and_modes_round_trip(self):
        rows = contracts.pairs([{'text': ' a , b ', 'modes': {'translate': 'numeric', 'other': 'numeric'}}])
        self.assertEqual(rows[0]['source'], 'a')
        self.assertEqual(rows[0]['modes']['rotate'], 'constraint')
        self.assertEqual(contracts.pairs(rows), rows)

    def test_invalid_modes_names_duplicates_ranges_rejected(self):
        for row in ({'source': 'a', 'target': 'a'}, {'source': '*', 'target': 'b'}, {'source': 'a.tx', 'target': 'b'},
                    {'text': 'a,b,c'}, {'text': 'a,b', 'source': 'a'}, {'source': 'a', 'target': 'b', 'modes': {'other': 'constraint'}}):
            with self.assertRaises(ValueError):
                contracts.pairs([row])
        for kwargs in ({'start': 1}, {'start': 2, 'end': 1}, {'start': float('nan'), 'end': 2}, {'smart': 1}, {'unknown': True}):
            with self.assertRaises(ValueError):
                contracts.normalize(pairs_value=[{'source': 'a', 'target': 'b'}], **kwargs)

    def test_files_are_read_only_in_preflight_and_collision_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '配置.json'
            args = contracts.normalize(action='save_config', pairs_value=[], path=str(path))
            self.assertFalse(path.exists())
            path.write_text('[{"text":"a,b","modes":{}}]', encoding='utf-8-sig')
            before = path.read_bytes()
            self.assertEqual(contracts.normalize(action='load_config', path=str(path))['pairs'][0]['target'], 'b')
            self.assertEqual(path.read_bytes(), before)
            with self.assertRaises(ValueError):
                contracts.normalize(action='save_config', path=str(path))
            with self.assertRaises(ValueError):
                contracts.normalize(action='save_config', path='relative.json')

    def test_full_ui_classes_modes_and_edit_actions_retained(self):
        source = ast.parse((PACKAGE / 'upstream/动画重定向.py').read_bytes())
        adapted = ast.parse((PACKAGE / 'ui.py').read_bytes())
        original_classes = {node.name for node in source.body if isinstance(node, ast.ClassDef)}
        self.assertEqual(original_classes, {node.name for node in adapted.body if isinstance(node, ast.ClassDef)})
        code = (PACKAGE / 'ui.py').read_text(encoding='utf-8')
        self.assertIn('show_bake_menu', code)
        self.assertIn('show_load_menu', code)
        self.assertIn('InternalMove', code)
        self.assertIn('_menu_exec(menu,', code)
        self.assertNotIn('pointConstraint(', code)
        self.assertNotIn('bakeResults(', code)
        self.assertNotIn('PySide2 import', code)

    def test_source_hash_metadata_and_lazy_ui(self):
        import hashlib
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((PACKAGE / 'upstream/动画重定向.py').read_bytes()).hexdigest(), catalog['sha256'])
        raw = RC.parent / '动画重定向.py'
        if raw.exists():
            self.assertEqual(raw.read_bytes(), (PACKAGE / 'upstream/动画重定向.py').read_bytes())
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(set(tool.parameters_schema['properties']['action']['enum']), set(contracts.ACTIONS))
        self.assertNotIn(tool.__class__.__module__.rsplit('.', 1)[0] + '.ui', sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
