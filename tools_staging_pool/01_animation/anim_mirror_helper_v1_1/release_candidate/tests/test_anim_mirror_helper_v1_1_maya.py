import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Only run via isolated mayapy runner; never in a user scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel
RC = Path(__file__).resolve().parents[1]
if (RC/'maya_toolkit/framework/base_tool.py').exists():
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.anim_mirror_helper_v1_1 import AnimMirrorHelperTool
    TOOL = AnimMirrorHelperTool()
else:
    spec = importlib.util.spec_from_file_location('mirror_loader',RC/'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    TOOL = loader.load_tool()
package = TOOL.__class__.__module__.rsplit('.',1)[0]
contracts = sys.modules[package+'.contracts']
runtime = sys.modules[package+'.runtime']


class StandaloneTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def test_01_dry_run_never_sources(self):
        before = str(mel.eval('whatIs "Mirror_tool_menue";'))
        nodes = cmds.ls()
        result = TOOL.run(action='load',dry_run=True)
        self.assertTrue(result.success,result.errors)
        self.assertEqual(before,str(mel.eval('whatIs "Mirror_tool_menue";')))
        self.assertEqual(nodes,cmds.ls())

    def test_02_load_all_original_declarations(self):
        nodes = cmds.ls()
        result = TOOL.run(action='load')
        self.assertTrue(result.success,result.errors)
        self.assertEqual(nodes,cmds.ls())
        for name in contracts.CATALOG['procedures']:
            self.assertTrue(str(mel.eval('whatIs "'+name+'";')).replace('\\','/').casefold().endswith((contracts.PACKAGE/contracts.CATALOG['entry']).as_posix().casefold()),name)
        self.assertEqual(mel.eval('$tmp=$mirror_tool_icon_path;'),(contracts.PACKAGE/'upstream/icons/mirror_tool.bmp').as_posix())

    def test_03_original_vector_array_average(self):
        result = TOOL.run(action='invoke',procedure='MIRR_e3bea614176fbceebe7c7aae67e953b0',arguments=dict(coords=[[1,2,3],[3,4,5]]))
        self.assertTrue(result.success,result.errors)
        self.assertEqual(list(result.data['outcome']['return_value']),[2.0,3.0,4.0])
        result.to_json()

    def test_04_original_unit_conversion(self):
        cmds.currentUnit(linear='cm')
        result = TOOL.run(action='invoke',procedure='MIRR_f71c299bf7b53f7243b078a9990e581c',arguments=dict(input=2.5))
        self.assertTrue(result.success,result.errors)
        self.assertEqual(result.data['outcome']['return_value'],2.5)

    def test_05_gui_operations_refused(self):
        for action in ('create_system','open_ui','calculate','bake_selected','delete_system'):
            kwargs = dict(action=action)
            if action=='create_system':
                kwargs['arguments'] = dict(mirror_axis='x',offset=0,cycled=1)
            result = TOOL.run(dry_run=True,**kwargs)
            self.assertFalse(result.success)
            self.assertIn('Interactive',str(result.errors))

    def test_06_runtime_restored_after_error(self):
        before = cmds.evaluationManager(query=True,mode=True)
        suspended = cmds.refresh(query=True,suspend=True)
        result = runtime.invoke('evaluationManager -mode "off"; refresh -suspend true; error "intentional isolated test";')
        self.assertIn('intentional',result['error'])
        self.assertEqual(before,cmds.evaluationManager(query=True,mode=True))
        self.assertEqual(suspended,cmds.refresh(query=True,suspend=True))
        self.assertEqual(result['runtime_state_errors'],[])

    def test_07_selection_guards_only_with_gui_flag_shim(self):
        # This only reaches read-only selection checks; never creates an actual GUI.
        node = cmds.createNode('transform',name='test_L')
        cmds.select(node)
        before = cmds.ls()
        with patch.object(cmds,'about',return_value=False):
            result = TOOL.validate(action='create_system',arguments=dict(mirror_axis='x',offset=0,cycled=1))
            self.assertTrue(result.success,result.errors)
            self.assertFalse(TOOL.validate(action='attach_pairs',arguments=dict(type='parent',offset=0)).success)
            self.assertFalse(TOOL.validate(action='delete_system').success)
            cmds.lockNode(node,lock=True)
            self.assertFalse(TOOL.validate(action='create_system',arguments=dict(mirror_axis='x',offset=0,cycled=1)).success)
        self.assertEqual(before,cmds.ls())
        self.assertEqual(cmds.ls(selection=True),[node])


if __name__=='__main__':
    unittest.main()
