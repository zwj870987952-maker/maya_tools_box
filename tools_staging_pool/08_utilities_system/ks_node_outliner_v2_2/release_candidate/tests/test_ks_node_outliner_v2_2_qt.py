import importlib.util,os,tempfile,unittest
from pathlib import Path
import faulthandler
faulthandler.dump_traceback_later(20)
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.ks_node_outliner_v2_2 import session
class QtChecks(unittest.TestCase):
    def test_explicit_desktop_preview_full_qt_manager(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(str(Path(td)/'filters.json'),True);print('config loaded',flush=True)
            from ks_nodeOutliner.lib.GUI_NodeOutliner import GUI_NodeOutliner
            from ks_nodeOutliner.lib.GUI_FilterManager import GUI_FilterManager
            print('native imports done',flush=True)
            win=GUI_NodeOutliner();print('double Outliner constructed',flush=True);self.assertEqual(len(win.allOutliners),2);self.assertEqual(len(win.CONFIG.getFilterNames()),16)
            manager=GUI_FilterManager(win);print('manager constructed',flush=True);self.assertIs(manager.CONFIG,win.CONFIG)
            win.CONFIG.snapshotData();win.CONFIG.filter_rename('Cameras','RenamedCamera');win.CONFIG.filter_delete('Joints');win.CONFIG.saveData();session.config_io.read(str(Path(td)/'filters.json'));win.CONFIG.restoreData();win.CONFIG.saveData()
            manager.close();win.close();manager.deleteLater();win.deleteLater();faulthandler.cancel_dump_traceback_later()
if __name__=='__main__':unittest.main()
