import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.floating_toolbar import FloatingToolbarTool
    tool=FloatingToolbarTool()
from maya_toolkit.tools.floating_toolbar import config_io
class Checks(unittest.TestCase):
    def test_preflight_full_python_and_config_no_overwrite(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.floating_toolbar.ui',sys.modules)
        data=[{'command':'x=1\nx+=2','source_type':'python','text':'Code'}]
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,data);self.assertEqual(config_io.read(p)[0]['command'],'x=1\nx+=2')
            with self.assertRaises(ValueError):config_io.write(p,data)
        self.assertFalse(tool.validate(action='execute_button',index=0).success)
        self.assertFalse(tool.validate(action='set_buttons',buttons=[{'command':'if','source_type':'python'}]).success)
if __name__=='__main__':unittest.main()
