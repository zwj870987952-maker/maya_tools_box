import copy,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.maya_blueprint_toolbox import workflow
def connect(source,port,target,input):return {'source_node':source,'source_port':port,'target_node':target,'target_port':input}
def attribute_graph(names):return {'version':1,'nodes':[{'id':'names','type':'maya.nodes.node_names','parameters':{'names':names}},
    {'id':'refs','type':'maya.attributes.make_ref','parameters':{'attribute_items':['translateX']}},
    {'id':'value','type':'constant.number','parameters':{'value':8}}, {'id':'set','type':'maya.attributes.set','parameters':{}}],
    'connections':[connect('names','nodes','refs','nodes'),connect('refs','attrs','set','attrs'),connect('value','value','set','value')]}
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_graph_dry_complete_and_one_undo(self):
        a=cmds.createNode('transform',name='a');b=cmds.createNode('transform',name='b');cmds.setAttr(a+'.tx',2);cmds.setAttr(b+'.tx',3);cmds.select(a)
        graph=attribute_graph([a,b]);before=set(cmds.ls());selection=cmds.ls(selection=True);time=cmds.currentTime(query=True)
        result=tool.run(action='execute_workflow',workflow=graph,dry_run=True);self.assertTrue(result.success,result.message)
        self.assertEqual(cmds.getAttr(a+'.tx'),2);self.assertEqual(cmds.ls(selection=True),selection);self.assertEqual(set(cmds.ls()),before)
        result=tool.run(action='execute_workflow',workflow=graph);self.assertTrue(result.success,result.message)
        self.assertEqual(cmds.getAttr(a+'.tx'),8);self.assertEqual(cmds.getAttr(b+'.tx'),8)
        cmds.undo();self.assertEqual(cmds.getAttr(a+'.tx'),2);self.assertEqual(cmds.getAttr(b+'.tx'),3)
        self.assertEqual(cmds.currentTime(query=True),time)
        cmds.setAttr(b+'.tx',lock=True);result=tool.run(action='execute_workflow',workflow=graph);self.assertFalse(result.success);self.assertEqual(cmds.getAttr(a+'.tx'),2)
        cmds.setAttr(b+'.tx',lock=False)
        self.assertFalse(tool.run(action='execute_workflow',workflow=attribute_graph([a,'missing'])).success);self.assertEqual(cmds.getAttr(a+'.tx'),2)
        self.assertFalse(tool.run(action='show_ui',dry_run=True).success)
    def test_native_sample_and_guarded_file_json(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.maya_api import animation
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',7);cmds.currentTime(12)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.json';data=animation.copy_frame([cube],[1,2],save_json=True,json_path=str(p))
            self.assertEqual(cmds.currentTime(query=True),12);self.assertEqual(data.samples[0]['values']['translateX'],7)
            before=p.read_bytes()
            with self.assertRaises(ValueError):animation.copy_frame([cube],[1],save_json=True,json_path=str(p))
            self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(Exception):animation.normalize_frames({'start':0,'end':100000})
    def test_native_example_data_transform(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.core.executor import WorkflowExecutor
        from maya_toolkit.tools.maya_blueprint_toolbox.file_io import read_json
        graph=read_json(str(rc/'maya_toolkit/tools/maya_blueprint_toolbox/native/examples/workflows/data_transform_test.json'))
        results=WorkflowExecutor(workflow.specs()).execute(graph)
        self.assertEqual(results['filter_by_name_1']['matched_nodes'],['pCube1','pCube2'])
    def test_copy_world_paste_parented_rotation_and_one_undo(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.maya_api import animation,attributes
        from maya_toolkit.tools.maya_blueprint_toolbox.native.core.types import AttrRef
        source=cmds.createNode('transform',name='source');parent=cmds.createNode('transform',name='targetParent')
        target=cmds.createNode('transform',name='target',parent=parent)
        cmds.setAttr(parent+'.tx',10);cmds.setAttr(parent+'.ry',90);cmds.setAttr(parent+'.sx',2);cmds.setAttr(target+'.rotateOrder',3)
        cmds.setAttr(source+'.tx',7);cmds.setAttr(source+'.ty',3);cmds.setAttr(source+'.rx',15);cmds.setAttr(source+'.ry',25)
        cmds.currentTime(12)
        data=animation.copy_frame([source],[1,2],save_json=False)
        refs=[AttrRef(target,c) for c in animation.TRANSLATE_CHANNELS+animation.ROTATE_CHANNELS]
        before=cmds.xform(target,query=True,worldSpace=True,matrix=True)
        result=attributes.set_attribute_refs(refs,data)
        self.assertEqual(len(result),6);self.assertEqual(cmds.currentTime(query=True),12)
        cmds.undo();self.assertEqual(cmds.xform(target,query=True,worldSpace=True,matrix=True),before)
        cmds.redo()
        for frame in (1,2):
            cmds.currentTime(frame)
            self.assertAlmostEqual(cmds.xform(target,query=True,worldSpace=True,translation=True)[0],7)
            self.assertAlmostEqual(cmds.xform(target,query=True,worldSpace=True,translation=True)[1],3)
            actual=cmds.xform(target,query=True,worldSpace=True,rotation=True)
            for x,y in zip(actual,[15,25,0]):self.assertAlmostEqual(x,y,places=5)
        # Exact one Undo is asserted immediately after the operation, before
        # test-only time scrubbing adds its own native Undo entries.
        cmds.currentTime(12);redo_state=cmds.xform(target,query=True,worldSpace=True,matrix=True)
        cmds.setAttr(target+'.tz',lock=True)
        with self.assertRaises(ValueError):attributes.set_attribute_refs(refs,data)
        self.assertEqual(cmds.xform(target,query=True,worldSpace=True,matrix=True),redo_state)
if __name__=='__main__':
    result=unittest.main(exit=False).result;maya.standalone.uninitialize();sys.exit(0 if result.wasSuccessful() else 1)
