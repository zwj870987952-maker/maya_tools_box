import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.ks_save_timer_v1_3_0 import session,storage
class QtChecks(unittest.TestCase):
    def test_complete_timer_history_config_and_owned_close(self):
        with tempfile.TemporaryDirectory() as td:
            watch=Path(td)/'asset_v001_work.ma';watch.write_text('unmodified');state=Path(td)/'state';state.mkdir()
            win=session.show(str(state),language=os.environ.get('KS_TEST_LOCALE','zh'),runtime='desktop',watch_file=str(watch))
            timer=win.TIMER;self.assertTrue(timer.isActive());self.assertGreaterEqual(len(win.contextMenu.actions()),6)
            timer.setTime(12);self.assertEqual(timer.counter,12)
            win._CONFIG_.set('general','timer_autopause','False');self.assertFalse(win._CONFIG_.get('general','timer_autopause'));win._CONFIG_.writeConfig()
            timer.CALLBACKS.fileSaved.emit();self.assertEqual(timer.counter,0);self.assertEqual(timer.saveCount,1)
            saved=storage.read_history(state/'KSSaveTimer_timeTrackHistory.json');self.assertEqual(next(iter(saved['desktop'].values()))['totalTime'],12)
            from ks_saveTimer.lib.GUI_config import saveTimer_config_GUI
            from ks_saveTimer.lib.GUI_tracker import GUI_timeTracker
            from ks_saveTimer.lib.GUI_saveTimer import aboutDialog_ksSaveTimer
            config=saveTimer_config_GUI(win);history=GUI_timeTracker(win);about=aboutDialog_ksSaveTimer(win)
            callbacks=timer.CALLBACKS;self.assertIn(str(watch),callbacks.systemWatcher.files())
            session.close();self.assertFalse(timer.isActive());self.assertEqual(callbacks.systemWatcher.files(),[]);self.assertEqual(callbacks.systemWatcher.directories(),[]);self.assertEqual(watch.read_text(),'unmodified')
            again=session.show(str(state),language=os.environ.get('KS_TEST_LOCALE','zh'),runtime='desktop',watch_file=str(watch));self.assertIsNot(again.TIMER,timer);session.close()
if __name__=='__main__':unittest.main()
