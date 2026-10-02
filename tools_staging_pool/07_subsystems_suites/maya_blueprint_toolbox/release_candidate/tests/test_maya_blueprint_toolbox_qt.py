"""Offscreen native Qt canvas without Maya initialization; not GUI acceptance."""
import importlib.util,os,sys,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets,QtCore
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.maya_blueprint_toolbox.native.main import BlueprintToolboxWindow
from maya_toolkit.tools.maya_blueprint_toolbox.file_io import read_json
class QtChecks(unittest.TestCase):
    def test_whole_canvas_all_node_specs_and_example(self):
        window=BlueprintToolboxWindow();canvas=window.canvas_widget
        self.assertEqual(len(canvas.node_specs),45)
        for kind in canvas.node_specs:canvas.scene.add_node_type(kind)
        self.assertGreaterEqual(len(canvas.scene.nodes_by_id),45)
        example=read_json(str(rc/'maya_toolkit/tools/maya_blueprint_toolbox/native/examples/workflows/data_transform_test.json'))
        canvas.scene.load_workflow(example)
        serialized=canvas.scene.serialize();self.assertEqual(len(serialized['nodes']),len(example['nodes']))
        self.assertEqual(len(serialized['connections']),len(example['connections']))
        self.assertEqual(canvas.scene.validate_workflow(),[])
        window.close();window.deleteLater();app.sendPostedEvents(None,QtCore.QEvent.DeferredDelete);app.processEvents()
if __name__=='__main__':unittest.main()
