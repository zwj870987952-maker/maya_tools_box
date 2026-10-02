"""Real QObject/QDropEvent fixture; no Maya initialization or actual file drop."""
import importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtGui,QtWidgets
from maya_toolkit.tools.smart_assistant.native.dragdrop import dragdrop_handler,file_actions
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
class QtChecks(unittest.TestCase):
    def test_drop_filter_owned_subtree_supported_and_stop(self):
        main=QtWidgets.QWidget();child=QtWidgets.QWidget(main);foreign=QtWidgets.QWidget();records=[];native=file_actions.handle_drop
        def event(p):
            mime=QtCore.QMimeData();mime.setUrls([QtCore.QUrl.fromLocalFile(str(p))])
            drop=QtGui.QDropEvent(QtCore.QPointF(1,1),QtCore.Qt.CopyAction,mime,QtCore.Qt.LeftButton,QtCore.Qt.NoModifier)
            return mime,drop
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'test.ma';source.write_bytes(b'// fixture');unsupported=Path(td)/'script.py';unsupported.write_bytes(b'# fixture')
            hook=dragdrop_handler.make_filter(main,app);dragdrop_handler._filter=hook;app.installEventFilter(hook)
            file_actions.handle_drop=lambda paths:records.append(paths)
            try:
                mime,drop=event(source);self.assertTrue(hook.eventFilter(child,drop));self.assertTrue(drop.isAccepted());self.assertEqual([[Path(p) for p in values] for values in records],[[source]])
                mime,drop=event(source);self.assertFalse(hook.eventFilter(foreign,drop));self.assertEqual(len(records),1)
                mime,drop=event(unsupported);self.assertFalse(hook.eventFilter(child,drop));self.assertEqual(len(records),1)
                dragdrop_handler.stop_dragdrop_monitor();self.assertIsNone(dragdrop_handler._filter)
                dragdrop_handler.stop_dragdrop_monitor()
            finally:file_actions.handle_drop=native;dragdrop_handler.stop_dragdrop_monitor()
        main.deleteLater();foreign.deleteLater();app.sendPostedEvents(None,QtCore.QEvent.DeferredDelete);app.processEvents()
if __name__=='__main__':unittest.main()
