"""Suite contracts, intact resources and no-execution offline checks."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    tool = load_tool()
else:
    from maya_toolkit.tools.anim_layer_v4_0 import AnimLayerSuiteTool
    tool = AnimLayerSuiteTool()
MODULE = sys.modules[type(tool).__module__]
CONTRACTS = sys.modules[MODULE.__package__ + '.contracts']
PACKAGE = CONTRACTS.PACKAGE


class OfflineTests(unittest.TestCase):
    def test_all_global_signatures_preserved_and_schema_both_protocols(self):
        catalog = CONTRACTS.CATALOG
        self.assertEqual(len(catalog['editions']['full']['procedures']), 197)
        self.assertEqual(len(catalog['editions']['no_ui']['procedures']), 33)
        schema = tool.to_openai_tool()['function']['parameters']
        self.assertEqual(set(schema['properties']), set(CONTRACTS.DEFAULTS))
        self.assertEqual(set(schema['properties']['procedure']['enum']) - {''}, set(CONTRACTS.PROCEDURES))
        self.assertEqual(tool.to_mcp_tool()['inputSchema'], schema)

    def test_resource_hashes_and_original_bytes_including_legacy_encoding(self):
        CONTRACTS.resources()
        self.assertEqual(len(CONTRACTS.CATALOG['resources']), 6)
        if (RC / 'launch_candidate.py').exists():
            for relative in CONTRACTS.CATALOG['resources']:
                self.assertEqual((PACKAGE / relative).read_bytes(),
                                 (RC.parent / 'anim_layer_v4_0' / Path(relative).relative_to('upstream')).read_bytes())
        with self.assertRaises(UnicodeDecodeError):
            (PACKAGE / 'upstream/layerEditor.mel').read_bytes().decode('utf-8')

    def test_inventory_never_imports_or_sources_maya(self):
        with patch.dict(sys.modules, {'maya': None, 'maya.cmds': None, 'maya.mel': None}):
            result = tool.validate(action='inventory', edition='full', procedure='animLayersSaveExportClbc')
        self.assertTrue(result.success, result.to_json())
        self.assertFalse(result.data['source_executed'])
        self.assertEqual([p['name'] for p in result.data['signature']['parameters']], ['file', 'type'])

    def test_exact_argument_names_types_and_finite_values(self):
        base = dict(action='invoke', procedure='create_and_select_anim_layer', arguments={'rotation_mod': 1})
        self.assertEqual(CONTRACTS.normalize(base)[2], 'create_and_select_anim_layer(1);')
        for args in ({'extra': 1}, {'edition': 'unknown'}, {'procedure': 'source'}, {'arguments': []},
                     {'force_reload': 1}, dict(base, arguments={'rotation_mod': True}),
                     dict(base, arguments={'rotation_mod': 2}), dict(base, arguments={}),
                     dict(base, arguments={'rotation_mod': 1, 'extra': 2})):
            with self.subTest(args=args), self.assertRaises(ValueError):
                CONTRACTS.normalize(args)
        for kind, value in [('float', float('nan')), ('float', float('inf')), ('int', 2**35), ('string', '\x00'), ('int[]', [1, 'bad'])]:
            with self.subTest(kind=kind, value=value), self.assertRaises(ValueError):
                CONTRACTS.mel_literal(value, kind)

    def test_array_float_string_literals_and_domain_constraints(self):
        self.assertEqual(CONTRACTS.mel_literal([1, 3.5], 'float[]'), '{1.0,3.5}')
        text = 'node";delete *;\\path`about`'
        self.assertEqual(json.loads(CONTRACTS.mel_literal(text, 'string')), text)
        with self.assertRaises(ValueError):
            CONTRACTS.normalize(dict(action='invoke', procedure='animLayerMerge_toAdditive', arguments={'layers': ['a'], 'timerange': [2, 1]}))
        with self.assertRaises(ValueError):
            CONTRACTS.normalize(dict(action='invoke', procedure='get_anim_time_range_from_multiply_anim_layers', arguments={'anim_layers_name': []}))

    def test_signature_catalog_covers_all_global_declarations(self):
        # Independent structural check: all literal global proc names in the intact source.
        import re
        for entry in CONTRACTS.CATALOG['editions'].values():
            source = (PACKAGE / entry['entry']).read_bytes().decode('latin-1')
            names = re.findall(r'\bglobal\s+proc\s+(?:(?:string|int|float)\s*(?:\[\s*\])?\s+)?([A-Za-z_]\w*)\s*\(', source)
            self.assertEqual(set(names), set(entry['procedures']))

    def test_export_collision_guard_is_readonly(self):
        cmds = types.SimpleNamespace(undoInfo=lambda **k: True, about=lambda **k: False, ls=lambda **k: [])
        maya = types.ModuleType('maya')
        maya.cmds = cmds
        with tempfile.TemporaryDirectory() as directory, patch.dict(sys.modules, {'maya': maya, 'maya.cmds': cmds}):
            path = Path(directory) / 'export.ma'
            args = dict(action='invoke', edition='full', procedure='animLayersSaveExportClbc', arguments={'file': str(path), 'type': 'mayaAscii'})
            self.assertTrue(tool.validate(**args).success)
            self.assertFalse(path.exists())
            path.write_text('existing fixture', encoding='utf-8')
            self.assertFalse(tool.validate(**args).success)
            self.assertEqual(path.read_text(encoding='utf-8'), 'existing fixture')

    def test_adapter_never_executes_installer_or_rewrites_original(self):
        files = ['contracts.py', 'runtime.py', 'tool.py', 'ui.py']
        for name in files:
            source = (PACKAGE / name).read_text(encoding='utf-8')
            ast.parse(source)
            self.assertNotIn('write_text(', source)
            self.assertNotIn('Drag_and_Drop', source)
            self.assertNotIn('tools_staging_pool', source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
