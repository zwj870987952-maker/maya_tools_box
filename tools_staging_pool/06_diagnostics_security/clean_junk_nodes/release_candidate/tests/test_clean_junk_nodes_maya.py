from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class Tests(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_unknown_lifetime_connection_lock_and_one_undo_redo(self):
        node=cmds.createNode('unknown',name='missingData');cmds.addAttr(node,longName='amount',attributeType='double');cmds.setAttr(node+'.amount',4)
        cube=cmds.polyCube()[0];cmds.connectAttr(node+'.amount',cube+'.tx');uuid=cmds.ls(node,uuid=True)[0];cmds.lockNode(node,lock=True);cmds.select(node)
        before=(cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True))
        preview=tool.run(dry_run=True,action='clean',unlock_nodes=True,callback_policy='none');self.assertTrue(preview.success,preview)
        self.assertEqual((cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True)),before)
        result=tool.run(action='clean',unlock_nodes=True,callback_policy='none');self.assertTrue(result.success,result);self.assertFalse(cmds.objExists(node))
        cmds.undo();self.assertEqual(cmds.ls(node,uuid=True),[uuid]);self.assertTrue(cmds.lockNode(node,q=True,lock=True)[0]);self.assertTrue(cmds.isConnected(node+'.amount',cube+'.tx'));self.assertEqual(cmds.getAttr(node+'.amount'),4)
        cmds.redo();self.assertFalse(cmds.objExists(node));self.assertTrue(cmds.objExists(cube))
    def test_locked_last_refused_before_any_delete(self):
        first=cmds.createNode('unknown',name='aUnknown');last=cmds.createNode('unknown',name='zUnknown');cmds.lockNode(last,lock=True)
        result=tool.run(action='clean',callback_policy='none');self.assertFalse(result.success);self.assertTrue(cmds.objExists(first));self.assertTrue(cmds.objExists(last))
    def test_actual_unknown_plugin_metadata_irreversible_guard(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'unknown.ma';path.write_text('//Maya ASCII 2025 scene\nrequires maya "2025";\nrequires "mtbMissingPluginFixture" "1.0";\ncurrentUnit -l centimeter -a degree -t film;\n',encoding='utf-8')
            cmds.file(str(path),open=True,force=True,executeScriptNodes=False)
            self.assertIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            refused=tool.run(action='clean',remove_unknown_plugins=True,callback_policy='none');self.assertFalse(refused.success)
            self.assertIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            result=tool.run(action='clean',remove_unknown_plugins=True,confirm_plugin_metadata_loss=True,callback_policy='none');self.assertTrue(result.success,result)
            self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            cmds.undo();self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
            cmds.redo();self.assertNotIn('mtbMissingPluginFixture',cmds.unknownPlugin(q=True,list=True) or [])
if __name__=='__main__':unittest.main()
