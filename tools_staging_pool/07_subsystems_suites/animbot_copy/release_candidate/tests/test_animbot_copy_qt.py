import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Use isolated runner')
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
# Deliberately no maya.standalone initialization: it already owns a QGuiApplication,
# which cannot host QWidget or be upgraded to QApplication.
class Tests(unittest.TestCase):
    def test_offscreen_original_widget_construction_and_live_sync(self):
        from maya_toolkit.tools.animbot_copy.native.qt import QtWidgets,QtCore,shiboken
        app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        from maya_toolkit.tools.animbot_copy.native.ui.main_toolbar import AnimBotMainToolbar
        from maya_toolkit.tools.animbot_copy.native.ui.graph_editor_toolbar import AnimBotGraphEditorToolbar
        from maya_toolkit.tools.animbot_copy.native.widgets.workspace_window import WorkspaceWindow
        from maya_toolkit.tools.animbot_copy.native.core.workspace_manager import WORKSPACE_MGR
        main=AnimBotMainToolbar(); graph=AnimBotGraphEditorToolbar(); window=WorkspaceWindow()
        self.assertGreater(len(main.tools_map),40);self.assertGreater(len(graph.tools_map),20)
        for preset in WORKSPACE_MGR.PRESETS:WORKSPACE_MGR.apply_preset(preset)
        WORKSPACE_MGR.apply_preset('Expert')
        self.assertFalse(main.tools_map['slider_ease'].isHidden())
        WORKSPACE_MGR.set_tool_active('slider_ease',False,'main')
        self.assertTrue(main.tools_map['slider_ease'].isHidden())
        self.assertIn('UI prototype',window.windowTitle())
        for widget in (main,graph,window):widget.close();widget.deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(None,QtCore.QEvent.DeferredDelete)
        WORKSPACE_MGR.apply_preset('Classic *')
        self.assertFalse(shiboken.isValid(main))
if __name__=='__main__':unittest.main()
