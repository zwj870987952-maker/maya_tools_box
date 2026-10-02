import importlib.util,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_drop',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.perform_file_drop_action import FileDropActionTool
    tool=FileDropActionTool()
from maya_toolkit.tools.perform_file_drop_action import source,namespace,_filters
class Checks(unittest.TestCase):
    def test_no_global_override_and_literal_namespace_paths(self):
        self.assertTrue(tool.validate().success);self.assertEqual(_filters,[])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'123 shot.ma';p.write_text('test');self.assertEqual(source(str(p)),str(p));self.assertEqual(namespace(None,str(p)),'file_123_shot')
            with self.assertRaises(ValueError):namespace('bad:ns',str(p))
if __name__=='__main__':unittest.main()
