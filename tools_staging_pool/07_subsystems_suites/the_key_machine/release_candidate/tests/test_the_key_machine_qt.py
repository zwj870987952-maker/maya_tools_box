import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process only; Maya must not initialize')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtWidgets,QtTest
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.the_key_machine import session
class QtChecks(unittest.TestCase):
    def test_native_modules_resources_and_owned_timers(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);toolbar=session.native_module('TheKeyMachine.core.toolbar');self.assertIsNone(toolbar.tb)
            import TheKeyMachine.mods.mediaMod as media
            self.assertTrue(Path(media.shelf_icon).is_file());self.assertEqual(session.translate('Copy Pose'),'复制姿势')
            values=[];timer=session.repeat(0.001,lambda:values.append(1),lambda:len(values)<2);QtTest.QTest.qWait(30);self.assertEqual(len(values),2);self.assertFalse(timer.isActive())
            session.owned_timer.singleShot(100,lambda:values.append(9));widget=session.tracked_widget();label=QtWidgets.QLabel('Copy Pose',widget);session.translate_widget(widget);self.assertEqual(label.text(),'复制姿势');widget.show();session.close();QtTest.QTest.qWait(130);self.assertEqual(values,[1,1])
            import shiboken6
            self.assertFalse(shiboken6.isValid(widget));self.assertFalse(session.timers)
if __name__=='__main__':unittest.main()
