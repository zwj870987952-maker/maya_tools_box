import importlib.util
import json
import re
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC/'maya_toolkit/framework/base_tool.py').exists():
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.anim_mirror_helper_v1_1 import AnimMirrorHelperTool
    TOOL = AnimMirrorHelperTool()
else:
    spec = importlib.util.spec_from_file_location('mirror_candidate_loader',RC/'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    TOOL = loader.load_tool()
contracts = sys.modules[TOOL.__class__.__module__.rsplit('.',1)[0]+'.contracts']


class OfflineTests(unittest.TestCase):
    def test_intact_resources(self):
        contracts.resources()
        original = RC.parent/'Anim_Mirror_Helper_v1_1_studio_lic'
        if original.is_dir():
            for path in original.rglob('*'):
                if path.is_file():
                    self.assertEqual(path.read_bytes(),(contracts.PACKAGE/'upstream'/path.relative_to(original)).read_bytes())
        self.assertEqual(len(contracts.CATALOG['resources']),6)

    def test_inventory_and_schema(self):
        result = TOOL.validate()
        self.assertTrue(result.success,result.errors)
        self.assertEqual(len(result.data['procedures']),90)
        self.assertEqual(TOOL.to_mcp_tool()['inputSchema'],TOOL.parameters_schema)
        json.loads(result.to_json())

    def test_aliases_and_typed_commands(self):
        _,name,signature,command = contracts.normalize(dict(action='create_system',arguments=dict(mirror_axis='x',offset=12.5,cycled=1)))
        self.assertEqual(name,contracts.ALIASES['create_system'])
        self.assertIn('12.5',command)
        for name in contracts.ALIASES.values():
            self.assertIn(name,contracts.CATALOG['procedures'])
        self.assertEqual(contracts.mel_literal([[1,2,3],[4,5,6]],'vector[]'),'{<<1.0,2.0,3.0>>,<<4.0,5.0,6.0>>}')
        self.assertEqual(contracts.mel_literal('x";print("x")','string'),'"x\\";print(\\"x\\")"')

    def test_reject_invalid_inputs(self):
        for kwargs in [dict(extra=1),dict(force_reload=1),dict(action='invoke',procedure='source'),
                       dict(action='create_system',arguments=dict(mirror_axis='w',offset=0,cycled=1)),
                       dict(action='invoke',procedure='MIRR_e3bea614176fbceebe7c7aae67e953b0',arguments=dict(coords=[])),
                       dict(action='inventory',arguments={'x':1}),dict(action='load',procedure='MT_calcul_single')]:
            self.assertFalse(TOOL.validate(**kwargs).success,str(kwargs))
        for value,kind in [(True,'int'),(float('nan'),'float'),([1,2],'vector'),('x\n','string')]:
            with self.assertRaises(ValueError):
                contracts.mel_literal(value,kind)

    def test_catalog_matches_all_declarations(self):
        text = (contracts.PACKAGE/contracts.CATALOG['entry']).read_bytes().decode('latin-1')
        names = re.findall(r'global\s+proc\s+(?:(?:string|float|int|vector)(?:\s*\[\s*\])?\s+)?(\w+)\s*\(',text)
        self.assertEqual(set(names),set(contracts.CATALOG['procedures']))
        self.assertEqual({p['type'] for q in contracts.CATALOG['procedures'].values() for p in q['parameters']},{'int','float','string','string[]','vector[]'})


if __name__=='__main__':
    unittest.main()
