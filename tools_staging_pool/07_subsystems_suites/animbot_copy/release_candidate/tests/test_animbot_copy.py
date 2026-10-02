import copy
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
    launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
else:
    sys.path.insert(0,str(ROOT))
    from maya_toolkit.tools.animbot_copy import AnimBotCopyTool
    tool=AnimBotCopyTool()
from maya_toolkit.tools.animbot_copy import workspace

class Tests(unittest.TestCase):
    def setUp(self):workspace.apply_preset('Classic *')
    def test_atomic_dry_validation_and_preset_roundtrip(self):
        before=copy.deepcopy(workspace.snapshot())
        self.assertTrue(tool.run(dry_run=True,action='apply_preset',preset='Expert').success)
        self.assertEqual(workspace.snapshot(),before)
        self.assertFalse(tool.run(action='configure',config={'alignment':'right','active_tools':['missing']}).success)
        self.assertEqual(workspace.snapshot(),before)
        self.assertTrue(tool.run(action='configure',config={'alignment':'right','single_row':True}).success)
        self.assertEqual(workspace.CONFIGS['main']['alignment'],'right')
        self.assertEqual(workspace.CONFIGS['graph_editor']['alignment'],'center')
        for preset in workspace.PRESETS:self.assertTrue(tool.run(action='apply_preset',preset=preset).success)
        self.assertEqual(len(workspace.CONFIGS['main']['active_tools']),len(workspace.KNOWN))
        workspace.PRESETS['custom']={'main':{'active_tools':[],'location':'时间轴顶部','alignment':'right','single_row':True},
                                  'graph_editor':{'active_tools':[],'location':'图形编辑器底部','alignment':'left','single_row':False}}
        self.assertTrue(tool.run(action='apply_preset',preset='custom').success)
        self.assertEqual(workspace.CONFIGS['main']['alignment'],'right')
        workspace.PRESETS.pop('custom')
    def test_no_qt_import_unsupported_and_bad_bool(self):
        self.assertNotIn('maya_toolkit.tools.animbot_copy.native.qt',sys.modules)
        self.assertFalse(tool.run(action='configure',toolbar='graph_editor',config={'location':'时间轴顶部'}).success)
        self.assertFalse(tool.run(action='configure',config={'single_row':1}).success)
        self.assertFalse(tool.run(dry_run='false').success)
        self.assertFalse(tool.run(action='bake').success)
        self.assertFalse(tool.run(action='configure',config={'active_tools':['slider_ease','slider_ease']}).success)
        self.assertFalse(tool.run(action='inspect',config={'single_row':True}).success)
        self.assertFalse(tool.run(action='apply_preset',preset='unknown').success)
        self.assertFalse(tool.run().data['animation_algorithms_implemented'])
if __name__=='__main__':unittest.main()
