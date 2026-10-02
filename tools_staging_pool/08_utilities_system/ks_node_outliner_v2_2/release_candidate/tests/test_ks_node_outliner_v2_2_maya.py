import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.ks_node_outliner_v2_2 import session
class MayaChecks(unittest.TestCase):
    def test_queries_pure_ngon_and_foreign_filter_guard(self):
        cmds.file(new=True,force=True);parent=cmds.createNode('transform',name='parent');cube=cmds.polyCube(name='cube')[0];cmds.parent(cube,parent);ngon=cmds.polyCreateFacet(p=[(0,0,0),(2,0,0),(3,1,0),(1,3,0),(-1,1,0)],name='ngon')[0];cmds.select(parent);before=cmds.ls(sl=True,long=True);time=cmds.currentTime(q=True)
        result=tool.run(action='query_nodes',objects=[parent],include_hierarchy=True,node_types=['mesh']);self.assertTrue(result.success,result.errors);self.assertEqual(len(result.data['nodes']),1);self.assertEqual(cmds.ls(sl=True,long=True),before)
        with tempfile.TemporaryDirectory() as td:
            session.configure(str(Path(td)/'filters.json'));module=session.script_module('.ksMiscFilters');constraint=cmds.polySelectConstraint(q=True,stateString=True);output=module.ks_geometryWithNGons([cube,ngon]);self.assertEqual(output,[ngon]);self.assertEqual(cmds.ls(sl=True,long=True),before);self.assertEqual(cmds.polySelectConstraint(q=True,stateString=True),constraint);self.assertEqual(cmds.currentTime(q=True),time)
            own=session.cmdshim.itemFilter(byType='mesh',classification='user');foreign=cmds.itemFilter(byType='camera',classification='user')
            with self.assertRaises(ValueError):session.cmdshim.delete(foreign)
            self.assertTrue(cmds.objExists(foreign));session.close();self.assertFalse(cmds.objExists(own));self.assertTrue(cmds.objExists(foreign));cmds.delete(foreign)
if __name__=='__main__':unittest.main()
