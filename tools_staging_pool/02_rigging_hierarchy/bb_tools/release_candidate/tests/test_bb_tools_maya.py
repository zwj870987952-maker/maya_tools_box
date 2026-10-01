import os
from pathlib import Path
import runpy
import sys
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
mod = sys.modules[TOOL.__class__.__module__]
runtime = __import__(mod.__package__+'.runtime', fromlist=['runtime'])


def state():
    return (sorted(cmds.ls(long=True)), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), cmds.autoKeyframe(query=True, state=True), cmds.namespaceInfo(currentNamespace=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)

    def test_full_definitions_no_original_auto_ui_or_scene_writes(self):
        before = state()
        self.assertTrue(TOOL.run(dry_run=True).success)
        self.assertEqual(before, state())

        runtime.load_native()
        self.assertEqual(before, state())
        for name, item in mod.catalog()['procedures'].items():
            if item['global_scope']:
                self.assertTrue(mel.eval('whatIs '+item['native_name']).startswith('Mel procedure'), name+': '+mel.eval('whatIs '+item['native_name']))
        self.assertTrue(mel.eval('whatIs bbstg_JBPerVertWindow').startswith('Mel procedure'))
        for member, entry in mod.catalog()['entries'].items():
            self.assertTrue(mel.eval('whatIs bbstg_'+entry).startswith('Mel procedure'), member)
        self.assertEqual((runtime.PKG/'native').as_posix()+'/', mel.eval('bbstg_bb_Tools_FilePath()'))
        self.assertEqual((runtime.PKG/'native/Script/bb_advFixTool').as_posix(), mel.eval('bbstg_bb_advFix_setFilePath()'))

    def test_all_16_original_controller_shapes_and_single_undo_redo(self):
        for index, style in enumerate(mod.SHAPES):
            before = state()
            dry = TOOL.run(dry_run=True, action='call', procedure='bb_CtrlTool_createShape', arguments=[style, 'ctrl_'+str(index)])
            self.assertTrue(dry.success, dry.message)
            self.assertEqual(before, state())
            result = TOOL.run(action='call', procedure='bb_CtrlTool_createShape', arguments=[style, 'ctrl_'+str(index)])
            self.assertTrue(result.success, result.message)
            shapes = cmds.listRelatives('ctrl_'+str(index), shapes=True) or []
            self.assertEqual(1, len(shapes))
            self.assertEqual('nurbsCurve', cmds.nodeType(shapes[0]))
            cmds.undo()
            self.assertFalse(cmds.objExists('ctrl_'+str(index)))
            cmds.redo()
            self.assertTrue(cmds.objExists('ctrl_'+str(index)))

    def test_original_color_attribute_hash_and_skin_query(self):
        mesh = cmds.polyCube(name='body')[0]
        cmds.select(mesh)
        args = dict(action='call', procedure='bb_CtrlTool_changeColorApply', arguments=[mesh, 13], objects=[mesh])
        before = state()
        self.assertTrue(TOOL.run(dry_run=True, **args).success)
        self.assertEqual(before, state())
        result = TOOL.run(**args)
        self.assertTrue(result.success, result.message)
        shape = cmds.listRelatives(mesh, shapes=True)[0]
        self.assertEqual(13, cmds.getAttr(shape+'.overrideColor'))
        cmds.undo()
        self.assertEqual(0, cmds.getAttr(shape+'.overrideEnabled'))
        attr = TOOL.run(action='call', procedure='bb_attr_addAttr', arguments=[mesh, ['travel', 'Float', '-2', '5', '1', '1']], objects=[mesh])
        self.assertTrue(attr.success, attr.message)
        self.assertEqual([-2.], cmds.attributeQuery('travel', node=mesh, minimum=True))
        self.assertEqual([5.], cmds.attributeQuery('travel', node=mesh, maximum=True))
        cmds.undo()
        self.assertFalse(cmds.attributeQuery('travel', node=mesh, exists=True))
        out = TOOL.run(action='call', procedure='wpRename_js_replaceHash', arguments=['joint_###', 7])
        self.assertTrue(out.success, out.message)
        self.assertEqual('joint_007', out.data['native_result'])
        cmds.select(clear=True)
        joint = cmds.joint(name='rootInfluence')
        cmds.skinCluster(joint, mesh, toSelectedBones=True)
        before = state()
        query = TOOL.run(action='call', procedure='bb_returnSkinList', arguments=[mesh], objects=[mesh])
        self.assertTrue(query.success, query.message)
        self.assertEqual([joint], query.data['native_result'])
        self.assertEqual(before[:5], state()[:5])

    def test_locked_scope_existing_names_and_interactive_preflight_reject(self):
        node = cmds.polyCube(name='protected')[0]
        shape = cmds.listRelatives(node, shapes=True)[0]
        cmds.setAttr(shape+'.overrideColor', lock=True)
        before = state()
        self.assertFalse(TOOL.run(action='call', procedure='bb_CtrlTool_changeColorApply', arguments=[node, 13], objects=[node]).success)
        self.assertFalse(TOOL.run(action='call', procedure='bb_CtrlTool_createShape', arguments=['CtrlShape_cube', node]).success)
        self.assertFalse(TOOL.run(action='call', procedure='bb_QC_unusedFix', allow_scene_scope=True).success)
        self.assertFalse(TOOL.run(action='call', procedure='DelDJJ').success)
        self.assertEqual(before, state())
        instance_parent = cmds.createNode('transform', name='actualInstanceParent')
        cmds.parent(node, instance_parent, add=True)
        with self.assertRaises(ValueError):
            runtime.nodes([node])


if __name__ == '__main__':
    unittest.main()
