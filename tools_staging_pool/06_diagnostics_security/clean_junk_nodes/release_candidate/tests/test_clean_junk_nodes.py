from pathlib import Path
import importlib.util
import sys
import types
import unittest
from unittest.mock import patch
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py'); launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch)
    instance=launch.load_tool()
else:
    sys.path.insert(0,str(rc))
    from maya_toolkit.tools.clean_junk_nodes import CleanJunkNodesTool
    instance=CleanJunkNodesTool()
module=sys.modules[instance.__class__.__module__]
class Tests(unittest.TestCase):
    def test_full_readonly_inventory_without_literal_list_bug(self):
        fake=types.SimpleNamespace(ls=lambda *a,**kw: ['node'] if kw.get('type')=='unknown' else ['uuid'] if kw.get('uuid') else [],
            referenceQuery=lambda *a,**kw:False,lockNode=lambda *a,**kw:[False],listRelatives=lambda *a,**kw:[],nodeType=lambda n:'unknown',unknownNode=lambda *a,**kw:'missingPlugin',
            unknownPlugin=lambda *a,**kw:[],about=lambda **kw:True)
        with patch.object(module,'_cmds',return_value=fake):
            result=instance.validate();self.assertTrue(result.success,result);self.assertEqual(result.data['nodes'][0]['node'],'node')
    def test_flags_must_be_explicit(self):
        with self.assertRaises(ValueError):module.normalize({'callback_policy':'all'})
        with self.assertRaises(ValueError):module.normalize({'unlock_nodes':'yes'})
        self.assertFalse(module.normalize({})['remove_unknown_plugins'])
if __name__=='__main__':unittest.main()
