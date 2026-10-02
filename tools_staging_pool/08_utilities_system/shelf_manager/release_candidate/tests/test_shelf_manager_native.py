import importlib.util,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_shelf',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.shelf_manager import session
class FakeCommands:
    def __init__(self):self.count=0;self.items={};self.values={};self.selections={}
    def __getattr__(self,name):
        def call(*args,**kw):
            if name=='window' and kw.get('exists'):return False
            if name=='about':return '2025'
            if kw.get('query'):
                if kw.get('selectItem'):return self.selections.get(args[0],[])
                return self.values.get(args[0],[])
            if kw.get('edit'):
                target=args[0]
                if kw.get('removeAll') or kw.get('deleteAllItems'):self.items[target]=[]
                if 'append' in kw:self.items.setdefault(target,[]).extend(kw['append'])
                if 'value' in kw:self.values[target]=kw['value']
                return target
            self.count+=1;value=args[0] if args and name=='window' else name+str(self.count);self.items.setdefault(value,[]);return value
        return call
class NativeChecks(unittest.TestCase):
    def test_complete_native_ui_scan_lists_and_full_path_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'2025/prefs/shelves';folder.mkdir(parents=True);p=folder/'shelf_Mine.mel';p.write_text('global proc shelf_Mine() {}')
            session.source_roots=[str(root)]
            import maya_toolkit.tools.shelf_manager.native as native
            fake=FakeCommands();native.cmds=fake;win=native.ShelfManager();self.assertGreater(fake.count,20);self.assertEqual(win.maya_versions,['2025']);self.assertEqual(len(win.en_shelf_map),1)
            display=next(iter(win.en_shelf_map));fake.selections[win.en_shelf_list]=[display];self.assertEqual(win._get_selected_shelves()[0][1],str(p.resolve()))
if __name__=='__main__':unittest.main()
