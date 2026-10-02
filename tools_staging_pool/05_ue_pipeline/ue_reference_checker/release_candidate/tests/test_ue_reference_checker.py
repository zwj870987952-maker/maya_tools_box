from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_reference_checker as t
class Tests(unittest.TestCase):
    def fake(self, rows, refs, loading=False):
        self.synced = []
        def query(name, options):
            self.assertTrue(options.include_hard_package_references); self.assertTrue(options.include_soft_package_references)
            self.assertFalse(options.include_searchable_names)
            value = refs[name]
            if isinstance(value, Exception): raise value
            return value
        obj = types.SimpleNamespace(get_path_name=lambda: '/Game/A/Hero.Hero')
        registry = types.SimpleNamespace(is_loading_assets=lambda: loading, get_referencers=query, get_assets=lambda f:[types.SimpleNamespace(get_asset=lambda: obj)])
        return types.SimpleNamespace(EditorUtilityLibrary=types.SimpleNamespace(get_selected_asset_data=lambda: rows),
            AssetRegistryHelpers=types.SimpleNamespace(get_asset_registry=lambda: registry),
            AssetRegistryDependencyOptions=lambda **kw:types.SimpleNamespace(**kw), ARFilter=lambda **kw:kw,
            EditorAssetLibrary=types.SimpleNamespace(sync_browser_to_objects=self.synced.append))
    def test_distinct_packages_regex_and_unknown(self):
        rows = [types.SimpleNamespace(package_name='/Game/A/Hero', asset_name='Hero'), types.SimpleNamespace(package_name='/Game/B/Hero', asset_name='Hero'), types.SimpleNamespace(package_name='/Game/C/Bad', asset_name='Bad')]
        refs = {'/Game/A/Hero':['/Game/ZOO/Map_ZOO','/Game/Other','/Game/Other'], '/Game/B/Hero':[], '/Game/C/Bad':RuntimeError('Registry error')}
        with patch.object(t, '_unreal', return_value=self.fake(rows, refs)):
            result = t.run(); self.assertFalse(result['success'])
            found = result['data']['rows']; self.assertEqual(len(found), 3)
            self.assertTrue(found[0]['correct']); self.assertEqual(found[0]['all_ref_count'], 2)
            self.assertFalse(found[1]['correct']); self.assertIsNone(found[2]['correct']); self.assertIsNone(found[2]['all_ref_count'])
    def test_loading_and_invalid_regex_fail_without_false_empty(self):
        with patch.object(t, '_unreal', return_value=self.fake([], {}, loading=True)):
            self.assertFalse(t.run()['success'])
        with patch.object(t, '_unreal') as unreal:
            self.assertFalse(t.run(pattern='[')['success']); unreal.assert_not_called()
    def test_browser_paths_and_dryrun_and_worker_rejection(self):
        with patch.object(t, '_unreal', return_value=self.fake([], {})):
            self.assertTrue(t.run(action='locate', package_name='/Game/A/Hero')['success']); self.assertEqual(self.synced, [])
            self.assertTrue(t.run(dry_run=False, action='locate', package_name='/Game/A/Hero')['success'])
            self.assertEqual(self.synced, [['/Game/A/Hero.Hero']])
        with patch.object(t.threading, 'current_thread', return_value=object()), patch.object(t, '_unreal') as unreal:
            self.assertFalse(t.run()['success']); unreal.assert_not_called()
if __name__ == '__main__': unittest.main()
