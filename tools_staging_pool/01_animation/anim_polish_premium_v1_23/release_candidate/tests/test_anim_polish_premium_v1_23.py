import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC/'maya_toolkit/framework/base_tool.py').exists():
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.anim_polish_premium_v1_23 import AnimPolishTool
    TOOL = AnimPolishTool()
else:
    spec = importlib.util.spec_from_file_location('polish_loader',RC/'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    TOOL = loader.load_tool()
PACKAGE = sys.modules[TOOL.__class__.__module__.rsplit('.',1)[0]]
contracts = sys.modules[PACKAGE.__name__+'.contracts']
guards = sys.modules[PACKAGE.__name__+'.file_guards']


class OfflineTests(unittest.TestCase):
    def test_original_byte_identity(self):
        contracts.resources()
        self.assertEqual(len(contracts.CATALOG['resources']),19)
        original = RC.parent
        if (original/'AnimPolish_README.txt').exists():
            for relative in contracts.CATALOG['resources']:
                source = original/Path(relative).relative_to('upstream')
                self.assertEqual(source.read_bytes(),(contracts.PACKAGE/relative).read_bytes())

    def test_complete_inventory_and_schema(self):
        result = TOOL.validate()
        self.assertTrue(result.success,result.errors)
        self.assertEqual(len(result.data['functions']),160)
        self.assertEqual(len(contracts.API_FUNCTIONS),157)
        self.assertEqual(TOOL.to_openai_tool()['function']['parameters'],TOOL.parameters_schema)
        json.loads(result.to_json())
        self.assertNotIn(PACKAGE.__name__+'.vendor.animPolish.ui',sys.modules)

    def test_signature_coverage(self):
        found = set()
        for p in (contracts.PACKAGE/'upstream/animPolish').glob('*.py'):
            found.update(p.stem+'.'+n.name for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef))
        self.assertEqual(found,set(contracts.CATALOG['functions']))
        for p in (contracts.PACKAGE/'vendor').rglob('*.py'):
            ast.parse(p.read_bytes())

    def test_defaults_and_strict_names(self):
        _,fn,bound = contracts.normalize(dict(action='invoke',function='growShrink.run',arguments={'geo':'mesh'}))
        self.assertEqual(bound['dfrmverts'],[])
        bound['dfrmverts'].append('mutation')
        self.assertEqual(contracts.normalize(dict(action='invoke',function='growShrink.run',arguments={'geo':'mesh'}))[2]['dfrmverts'],[])
        for kwargs in [dict(action='invoke',function='user_settings.run'),dict(action='invoke',function='ui.saveSettings_run'),dict(action='invoke',function='iron.run'),dict(action='invoke',function='quickBake.run',arguments={'objs':[],'bad':1}),dict(dock=True),dict(action='open_ui',arguments={'x':1}),dict(action='invoke',function='subdue.run',arguments={'rate':0})]:
            self.assertFalse(TOOL.validate(**kwargs).success,str(kwargs))

    def test_cache_collision_and_input_checks(self):
        with tempfile.TemporaryDirectory(prefix='polish_path_') as directory:
            parent = Path(directory)
            folder = parent/'new'
            guards.cache_path(folder.as_posix(),'geometry.abc',True)
            self.assertFalse(folder.exists())
            folder.mkdir()
            (folder/'geometry.abc').write_bytes(b'existing')
            with self.assertRaises(ValueError):
                guards.cache_path(folder.as_posix(),'geometry.abc',True)
            guards.cache_path(folder.as_posix(),'geometry.abc',False)
            with self.assertRaises(ValueError):
                guards.cache_path('relative','geometry.abc',True)
            with self.assertRaises(ValueError):
                guards.cache_path(contracts.PACKAGE.as_posix(),'geometry.abc',True)
            self.assertEqual((folder/'geometry.abc').read_bytes(),b'existing')

    def test_vendor_namespace_and_callbacks(self):
        for p in (contracts.PACKAGE/'vendor/animPolish').glob('*.py'):
            tree = ast.parse(p.read_bytes())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    self.assertFalse(any(a.name=='animPolish' or a.name.startswith('animPolish.') for a in node.names))
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and 'import '+PACKAGE.__name__+'.vendor' in node.value:
                    if not node.value.startswith('\n'):
                        ast.parse(node.value)


if __name__=='__main__':
    unittest.main()
