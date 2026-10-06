"""Offline boundary tests. Never initialize Maya or execute original algorithms."""
import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

CANDIDATE = Path(__file__).resolve().parents[1]
loader = runpy.run_path(str(CANDIDATE / 'launch_candidate.py'), run_name='animo_test_loader')
TOOL = loader['load_tool']()
SESSION = sys.modules[TOOL.__class__.__module__.rsplit('.', 1)[0] + '.session']
REAL_PACKAGE = SESSION.PACKAGE


class FakeMaya:
    def __init__(self, directory):
        self.directory = directory
        self.reads = []

    def about(self, **kwargs):
        self.reads.append(('about', kwargs))
        return False if kwargs.get('batch') else '2025'

    def internalVar(self, **kwargs):
        self.reads.append(('internalVar', kwargs))
        return str(self.directory / 'maya/2025/scripts')

    def undoInfo(self, **kwargs):
        if kwargs != {'query': True, 'state': True}:
            raise AssertionError('Preflight attempted Undo mutation')
        return True

    def ls(self, *args, **kwargs):
        if args:
            return ['|rig|' + args[0]] if args[0] in ('ctrl', '|rig|ctrl') else []
        return ['|rig|ctrl']

    def __getattr__(self, key):
        raise AssertionError('Unexpected Maya API during preflight: ' + key)


class CatalogTests(unittest.TestCase):
    def test_complete_unique_catalog(self):
        rows = SESSION.operations()
        self.assertEqual(len(rows), 553)
        self.assertEqual(len({row['id'] for row in rows}), 553)
        self.assertEqual(sum(row['original_library'] is not None for row in rows), 540)
        self.assertEqual(len({row['category'] for row in rows}), 55)
        self.assertTrue(all(not row['maya_verified'] for row in rows))

    def test_every_entry_has_exact_source(self):
        for row in SESSION.operations():
            self.assertTrue(SESSION.source_path(row['entrypoint']).is_file())
            self.assertTrue(row['description'])
            self.assertTrue(row['input'])
            self.assertTrue(row['effects'])

    def test_schema_exports_same_contract(self):
        a = TOOL.to_openai_tool()
        b = TOOL.to_mcp_tool()
        self.assertEqual(a['function']['parameters'], b['inputSchema'])
        self.assertEqual(a['function']['name'], 'animo')
        self.assertFalse(b['inputSchema']['additionalProperties'])
        self.assertEqual(len(b['inputSchema']['properties']['operation_id']['enum']), 553)
        json.dumps(a, ensure_ascii=False)

    def test_catalog_search_pagination(self):
        first = TOOL.run(action='catalog', query='Tween', limit=2)
        self.assertTrue(first.success)
        self.assertEqual(len(first.data['operations']), 2)
        self.assertGreater(first.data['total'], 2)
        self.assertNotEqual(first.data['operations'][0]['id'],
                            TOOL.run(action='catalog', query='Tween', offset=1, limit=1).data['operations'][0]['id'])

    def test_loader_does_not_register(self):
        from maya_toolkit.framework import ToolRegistry
        self.assertIsNone(ToolRegistry.get('animo'))

    def test_no_vendor_import_on_inspect(self):
        before = set(sys.modules)
        result = TOOL.run(dry_run=True, action='inspect')
        self.assertTrue(result.success)
        self.assertTrue(result.dry_run)
        self.assertFalse(result.data['native_imported'])
        self.assertFalse(any(name.startswith('Animo_') for name in set(sys.modules) - before))

    def test_parameter_rejection(self):
        for kwargs in ({'action': 'unknown'}, {'action': 'inspect', 'code': 'print(1)'},
                       {'limit': True}, {'offset': -1}, {'limit': 201},
                       {'objects': ['ctrl']}, {'operation_id': 'suite.toolbar'},
                       {'action': 'invoke', 'operation_id': '../../evil.py'},
                       {'action': 'invoke', 'operation_id': 'suite.toolbar', 'objects': ['ctrl.tx']},
                       {'action': 'invoke', 'operation_id': 'suite.toolbar', 'objects': ['ctrl', 'ctrl']}):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(TOOL.validate(**kwargs).success)

    def test_path_traversal_rejected(self):
        for value in ('../../tool.py', str(CANDIDATE / 'launch_candidate.py'), None):
            with self.assertRaises(ValueError):
                SESSION.source_path(value)

    def test_patches_only_expected_lifecycle(self):
        launcher = REAL_PACKAGE / 'native/Animo_Data/Animo_Launcher/Animo_Launcher.py'
        tree = ast.parse(launcher.read_text(encoding='utf-8'))
        calls = {node.value.func.id for node in tree.body if isinstance(node, ast.Expr)
                 and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)}
        self.assertNotIn('enable_usersetup_security', calls)
        self.assertNotIn('_check_first_run_startup', calls)
        self.assertIn('_check_first_run_startup', {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        toggle = (REAL_PACKAGE / 'native/Animo_Data/Animo_Launcher/toggle.py').read_text(encoding='utf-8')
        self.assertIn('if name.startswith("Animo") and name.endswith("UIWindow"):', toggle)
        self.assertEqual(len(json.loads((CANDIDATE / 'patches.json').read_text(encoding='utf-8'))), 2)


class RuntimeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'package'
        native = self.package / 'native/Animo_Data'
        native.mkdir(parents=True)
        (native / 'entry.py').write_text('raise AssertionError("Native code must not run in preflight")\n', encoding='utf-8')
        (native / 'resource.bin').write_bytes(b'reference resource')
        hashes = {'Animo_Data/' + p.name: SESSION.sha256(p) for p in native.iterdir()}
        (self.package / 'runtime_files.json').write_text(json.dumps(hashes), encoding='utf-8')
        row = dict(SESSION.find_operation('suite.toolbar'), id='test.entry', entrypoint='Animo_Data/entry.py')
        (self.package / 'operations.json').write_text(json.dumps({'operations': [row]}), encoding='utf-8')
        self.fake = FakeMaya(self.root)
        self.addCleanup(patch.stopall)
        patch.object(SESSION, 'PACKAGE', self.package).start()
        patch.object(SESSION, 'maya_cmds', return_value=self.fake).start()
        self.destination = SESSION.runtime_destination(self.fake)

    def snapshot(self):
        return {str(p.relative_to(self.root)): SESSION.sha256(p) for p in self.root.rglob('*') if p.is_file()}

    def test_install_dryrun_zero_writes_and_imports(self):
        before = self.snapshot()
        modules = set(sys.modules)
        paths = list(sys.path)
        result = TOOL.run(dry_run=True, action='install_runtime')
        self.assertTrue(result.success)
        self.assertFalse(self.destination.exists())
        self.assertEqual(before, self.snapshot())
        self.assertEqual(paths, sys.path)
        self.assertFalse(any(name.startswith('Animo_') for name in set(sys.modules) - modules))

    def test_new_install_copies_resources_and_marker_without_running(self):
        data = SESSION.install_runtime(self.destination)
        self.assertEqual(data['state'], 'installed_unverified')
        self.assertFalse(data['startup_file_written'])
        self.assertTrue((self.destination / 'resource.bin').is_file())
        self.assertEqual(SESSION.verify_code(self.destination.parent, check_marker=True), 1)
        self.assertFalse((self.destination.parent / 'userSetup.py').exists())

    def test_existing_directory_is_never_overwritten(self):
        self.destination.mkdir(parents=True)
        custom = self.destination / 'personal.py'
        custom.write_text('personal source', encoding='utf-8')
        before = self.snapshot()
        self.assertFalse(TOOL.validate(action='install_runtime').success)
        with self.assertRaises(ValueError):
            SESSION.install_runtime(self.destination)
        self.assertEqual(before, self.snapshot())

    def test_changed_source_resource_refuses_install(self):
        (self.package / 'native/Animo_Data/resource.bin').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'SOURCE_RESOURCE_CHANGED'):
            SESSION.install_runtime(self.destination)
        self.assertFalse(self.destination.parent.exists())

    def test_invoke_dryrun_keeps_selection_paths_files_and_native_code(self):
        SESSION.install_runtime(self.destination)
        before = self.snapshot()
        paths = list(sys.path)
        with patch.object(SESSION.runpy, 'run_path', side_effect=AssertionError('dry_run executed vendor')):
            result = TOOL.run(dry_run=True, action='invoke', operation_id='test.entry', objects=['ctrl'])
        self.assertTrue(result.success, result.message)
        self.assertEqual(result.data['target_objects'], ['|rig|ctrl'])
        self.assertEqual(before, self.snapshot())
        self.assertEqual(paths, sys.path)

    def test_missing_object_rejected_without_changes(self):
        SESSION.install_runtime(self.destination)
        self.assertFalse(TOOL.validate(action='invoke', operation_id='test.entry', objects=['missing']).success)

    def test_changed_runtime_refuses_dispatch(self):
        SESSION.install_runtime(self.destination)
        (self.destination / 'entry.py').write_text('changed = True\n', encoding='utf-8')
        result = TOOL.validate(action='invoke', operation_id='test.entry')
        self.assertFalse(result.success)
        self.assertIn('RUNTIME_CODE_MISMATCH', result.message)

    def test_foreign_module_not_unloaded(self):
        SESSION.install_runtime(self.destination)
        module = types.ModuleType('spacify_core')
        module.__file__ = str(self.root / 'other_tool/spacify_core.py')
        with patch.dict(sys.modules, {'spacify_core': module}):
            result = TOOL.validate(action='invoke', operation_id='test.entry')
            self.assertFalse(result.success)
            self.assertIn('MODULE_COLLISION', result.message)
            self.assertIs(sys.modules['spacify_core'], module)

    def test_native_system_exit_becomes_failed_action(self):
        SESSION.install_runtime(self.destination)
        row = SESSION.find_operation('test.entry')
        before = list(sys.path)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), before))
        with patch.object(SESSION.runpy, 'run_path', side_effect=SystemExit(0)):
            with self.assertRaisesRegex(ValueError, 'NATIVE_ABORTED'):
                SESSION.invoke(row, self.destination)


if __name__ == '__main__':
    unittest.main()
