import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process only; no Maya standalone init')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.studiolibrary_patch import runtime
class QtChecks(unittest.TestCase):
    def test_full_extension_interfaces_theme_and_hook_ownership(self):
        runtime.ensure_paths()
        import studiolibrary,studiolibrary.libraryitem,studiolibrary.librarywindow,studiolibrary.widgets,studioqt
        from studiolibrary_wanimation import localization
        with tempfile.TemporaryDirectory() as td:
            QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat);QtCore.QSettings.setPath(QtCore.QSettings.IniFormat,QtCore.QSettings.UserScope,td)
            original=studiolibrary.libraryitem.LibraryItem.safeSave;runtime.activate();own=studiolibrary.libraryitem.LibraryItem.safeSave
            try:
                self.assertIsNot(own,original);self.assertEqual({cls.__name__ for cls in studiolibrary.registeredItems()},{'WPoseItem','WAnimationItem'})
                callback=lambda:None;schema=[{'name':'Blend','label':'Blend','callback':callback}];copy=localization.translate_schema(schema);self.assertIs(copy[0]['callback'],callback);self.assertEqual(schema[0]['label'],'Blend')
                theme=studiolibrary.widgets.Theme();theme.setAccentColor('rgb(108, 92, 231)');theme.setBackgroundColor('rgb(24, 25, 32)')
                from maya_toolkit.tools.studiolibrary_patch.theme_io import CSS
                css=studioqt.StyleSheet.fromPath(str(CSS),options=theme.options(),dpi=theme.dpi()).data();self.assertNotIn('FOREGROUND_COLOR_R',css);self.assertNotIn('RESOURCE_DIRNAME',css);self.assertIn('108',css)
                menu=studioqt.menu.Menu();menu.addAction('Settings');self.assertIsNotNone(menu.findAction('Settings'));menu.deleteLater()
                win=studiolibrary.librarywindow.LibraryWindow(name='MTB_offscreen_fixture');win.setCheckForUpdateEnabled(False)
                runtime.window=win;runtime.apply_theme();self.assertIn('108',win.styleSheet());win.close();runtime.window=None;win.deleteLater()
                def foreign(*args,**kw):return own(*args,**kw)
                studiolibrary.libraryitem.LibraryItem.safeSave=foreign
                with self.assertRaises(RuntimeError):runtime.deactivate()
                self.assertIs(studiolibrary.libraryitem.LibraryItem.safeSave,foreign);studiolibrary.libraryitem.LibraryItem.safeSave=own
            finally:
                studiolibrary.libraryitem.LibraryItem.safeSave=own;runtime.deactivate()
            self.assertIs(studiolibrary.libraryitem.LibraryItem.safeSave,original)
if __name__=='__main__':unittest.main()
