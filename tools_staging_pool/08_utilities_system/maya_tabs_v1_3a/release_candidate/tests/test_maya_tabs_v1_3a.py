import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.maya_tabs_v1_3a import MayaTabsTool
    tool=MayaTabsTool()
from maya_toolkit.tools.maya_tabs_v1_3a import storage
class Checks(unittest.TestCase):
    def test_typed_complete_themes_and_transactional_session(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.maya_tabs_v1_3a.native',sys.modules)
        themes=list((Path(storage.__file__).parent/'resources/Themes').glob('*.mttheme'));self.assertGreaterEqual(len(themes),19)
        for theme in themes:storage.read(str(theme))
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'session.tabs-session';data=[{'name':'Empty','fname':'','autosave':False,'active':False,'thumbnail':''}];storage.write(str(p),data);before=p.read_bytes();row=storage.write(str(p),data,True);self.assertEqual(Path(row['backup']).read_bytes(),before)
            with self.assertRaises(ValueError):storage.write(str(p),data+[{'name':'Bad','fname':'','autosave':1}],True)
            self.assertEqual(p.read_bytes(),before)
if __name__=='__main__':unittest.main()
