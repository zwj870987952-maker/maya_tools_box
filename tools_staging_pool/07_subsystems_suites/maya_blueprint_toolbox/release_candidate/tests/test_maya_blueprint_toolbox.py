import copy,importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.maya_blueprint_toolbox import MayaBlueprintToolboxTool
    tool=MayaBlueprintToolboxTool()
from maya_toolkit.tools.maya_blueprint_toolbox import workflow,file_io
def graph():return {'version':1,'nodes':[{'id':'n','type':'constant.number','parameters':{'value':7}},{'id':'p','type':'debug.print_result','parameters':{}}],
    'connections':[{'source_node':'n','source_port':'value','target_node':'p','target_port':'input'}]}
class Checks(unittest.TestCase):
    def test_native_complete_and_strict_graph(self):
        result=tool.run();self.assertTrue(result.success);self.assertEqual(len(result.data['node_specs']),45)
        self.assertNotIn('PySide6',sys.modules)
        data=graph();normalized=workflow.normalize_graph(data);self.assertNotIn('label',data['nodes'][1]['parameters'])
        bad=copy.deepcopy(data);bad['nodes'].append(copy.deepcopy(bad['nodes'][0]))
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['connections'].append(copy.deepcopy(bad['connections'][0]))
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['nodes'][0]['parameters']['value']=True
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['connections'][0]['source_port']='wrong'
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        with self.assertRaises(ValueError):workflow.scoped_graph(normalized,['missing'])
        self.assertEqual(len(workflow.scoped_graph(normalized,['p'])['nodes']),2)
    def test_graph_persistence_exact_backup(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'graph.json'
            dry=tool.run(action='save_workflow',workflow=graph(),path=str(p),dry_run=True)
            self.assertTrue(dry.success,dry.message);self.assertFalse(p.exists())
            result=tool.run(action='save_workflow',workflow=graph(),path=str(p));self.assertTrue(result.success,result.message)
            before=p.read_bytes();self.assertFalse(tool.run(action='save_workflow',workflow=graph(),path=str(p)).success);self.assertEqual(p.read_bytes(),before)
            self.assertTrue(tool.run(action='save_workflow',workflow=graph(),path=str(p),overwrite_existing=True).success)
            self.assertEqual(next(Path(td).glob('*.mtb_backup_*')).read_bytes(),before)
            self.assertTrue(tool.run(action='read_workflow',path=str(p)).success)
            p.write_text('{"a":1,"a":2}',encoding='utf8')
            with self.assertRaises(ValueError):file_io.read_json(str(p))
if __name__=='__main__':unittest.main()
