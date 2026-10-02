import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process; do not initialize Maya')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtGui,QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.floating_toolbar import session,ui,config_io
class QtChecks(unittest.TestCase):
    def test_full_flow_buttons_png_config_and_clear(self):
        win=ui.FloatingToolbar();self.assertEqual(win.toolbar_flow.count(),10);data=[{'command':'x=1\nx+=2','source_type':'python','text':'Code'}];session.replace_buttons(win,data);self.assertEqual(win.toolbar_flow.count(),1)
        button=win.toolbar_flow.itemAt(0).widget();pix=QtGui.QPixmap(32,32);pix.fill(QtGui.QColor('red'));button.setIcon(QtGui.QIcon(pix));records=session.snapshot(win);self.assertTrue(records[0]['icon_png'])
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,records);session.replace_buttons(win,config_io.read(p));self.assertFalse(win.toolbar_flow.itemAt(0).widget().icon().isNull())
        before=win.toolbar_flow.count()
        with self.assertRaises(ValueError):session.replace_buttons(win,[{'command':'if','source_type':'python'}])
        self.assertEqual(win.toolbar_flow.count(),before);win.clear_toolbar();self.assertEqual(win.toolbar_flow.count(),0);win.deleteLater()
    def test_left_click_filter_does_not_consume(self):
        button=QtWidgets.QToolButton();hook=session.make_filter(button,'reference');event=QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,QtCore.QPointF(1,1),QtCore.Qt.LeftButton,QtCore.Qt.LeftButton,QtCore.Qt.NoModifier);self.assertFalse(hook.eventFilter(button,event));hook.deleteLater();button.deleteLater()
if __name__=='__main__':unittest.main()
