import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets,QtGui,QtCore
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.maya_tabs_v1_3a import session,storage
class QtChecks(unittest.TestCase):
    def test_complete_toolbar_and_thumbnail_without_maya_or_license_bypass(self):
        with tempfile.TemporaryDirectory() as td:
            module=session.load(td,True);win=session.install_toolbar();self.assertEqual(len(win._slots),8);self.assertEqual(session.callbacks,[])
            win.on_new_tab();self.assertEqual(len(win._slots),9);data=storage.read(str(Path(td)/'Maya-Tabs.ini'));self.assertEqual(len(data['tabs']),9)
            pix=QtGui.QPixmap(32,16);pix.fill(QtCore.Qt.red);encoded=win._serialise_thumnail(pix);self.assertTrue(encoded);module.__.settings['tabs'][0]['thumbnail']=encoded;session.save_settings()
            called=[];timer=session.later(0,lambda:called.append(True));self.assertTrue(timer.isActive());session.close();app.processEvents();self.assertEqual(called,[]);self.assertIsNone(module.MayaTabs.instance)
if __name__=='__main__':unittest.main()
