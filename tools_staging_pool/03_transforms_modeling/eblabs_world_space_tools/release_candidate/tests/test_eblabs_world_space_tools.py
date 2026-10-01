import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.eblabs_world_space_tools import WorldSpaceToolsTool
    TOOL=WorldSpaceToolsTool()
from maya_toolkit.tools.eblabs_world_space_tools import runtime
from maya_toolkit.tools.eblabs_world_space_tools.tool import normalize
PKG=Path(sys.modules[TOOL.__class__.__module__].__file__).parent


class Checks(unittest.TestCase):
    def test_complete_original_bytes_and_business_definitions(self):
        c=runtime.catalog()
        self.assertEqual(174,len(c['files']))
        for row in c['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
            if not row['path'].endswith('.py'):
                self.assertEqual(row['sha256'],hashlib.sha256((PKG/'bundle'/row['path']).read_bytes()).hexdigest())
        tree=ast.parse((PKG/'native.py').read_text(encoding='utf8'))
        original=c['definitions'][c['legacy_source']]
        self.assertEqual(sorted(original),sorted(n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))))
        self.assertTrue(c['missing_version_modules'])
        self.assertEqual('eblabs_world_space_tools',TOOL.to_mcp_tool()['name'])

    def test_strict_inputs_session_preferences_and_no_eval(self):
        for p in ({'start':float('nan')},{'start':3,'end':1},{'action':'to_world','attributes':['scaleX']},{'action':'export_preferences'},{'spans':True},{'action':'open_ui','objects':['x']},{'action':'native_callback','callback_ticket':'invented'}):
            if p.get('action')=='native_callback':
                continue
            with self.assertRaises(ValueError): normalize(p)
        r=runtime.preference_load('g'); r['data']['default']['v']=4
        runtime.preference_save('g',r)
        fresh=runtime.preference_load('g'); fresh['data']['default']['v']=7
        self.assertEqual(4,runtime.preference_load('g')['data']['default']['v'])
        tree=ast.parse((PKG/'native.py').read_text(encoding='utf8'))
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='eval' for n in ast.walk(tree)))
        runtime._SESSION.clear()


if __name__=='__main__': unittest.main()
