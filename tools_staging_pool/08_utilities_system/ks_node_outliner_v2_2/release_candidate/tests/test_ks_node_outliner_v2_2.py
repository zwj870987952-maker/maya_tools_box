import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.ks_node_outliner_v2_2 import KSNodeOutlinerTool
    tool=KSNodeOutlinerTool()
from maya_toolkit.tools.ks_node_outliner_v2_2 import config_io
class Checks(unittest.TestCase):
    def test_complete_config_pure_preflight_and_exact_backup(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('ks_nodeOutliner',sys.modules)
        defaults=config_io.read(Path(config_io.__file__).parent/'native/ks_nodeOutliner/ksNodeOutliner_filterData.json');self.assertGreaterEqual(len(defaults['FILTERS']),16)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,defaults);original=Path(p).read_bytes()
            with self.assertRaises(ValueError):config_io.write(p,defaults)
            row=config_io.write(p,defaults,True);self.assertEqual(Path(row['backup']).read_bytes(),original)
            bad={'FILTERS':{'x':{'baseFilter':1}}}
            with self.assertRaises(ValueError):config_io.write(str(Path(td)/'bad.json'),bad)
            self.assertFalse((Path(td)/'bad.json').exists())
if __name__=='__main__':unittest.main()
