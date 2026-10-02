from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py');launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
else:
    sys.path.insert(0,str(ROOT));from maya_toolkit.tools.getools_overlappy import GEToolsOverlappyTool
    tool=GEToolsOverlappyTool()
class Tests(unittest.TestCase):
    def test_fresh_preset_roundtrip_no_overwrite_dry(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'preset.txt';args={'action':'save_preset','preset_path':str(path),'preset_values':{'flagLayer':True,'values':[1,2,3]}}
            self.assertTrue(tool.run(dry_run=True,**args).success);self.assertFalse(path.exists())
            self.assertTrue(tool.run(**args).success);before=path.read_bytes()
            self.assertFalse(tool.run(**args).success);self.assertEqual(path.read_bytes(),before)
            self.assertEqual(tool.run(action='read_preset',preset_path=str(path)).data['values'],args['preset_values'])
            bad=Path(d)/'bad.txt';bad.write_text('x = __import__("os").system("bad")')
            self.assertFalse(tool.run(action='read_preset',preset_path=str(bad)).success)
    def test_inspect_and_schema_no_native_import(self):
        result=tool.run();self.assertTrue(result.success)
        self.assertEqual(result.data['dependency_commit'],'45c4e17504fded01262941843ed186e9ac73c477')
        self.assertNotIn('maya_toolkit.tools.getools_overlappy.runtime',sys.modules)
        self.assertFalse(tool.run(weight=True).success)
        self.assertFalse(tool.run(confirm_bake='yes').success)
        self.assertFalse(tool.run(dry_run='no').success)
        self.assertFalse(tool.run(action='unsupported').success)
if __name__=='__main__':unittest.main()
