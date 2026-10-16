"""Production API contracts; real Maya evidence retains environment limits."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
from maya_toolkit.tools import advanced_skeleton_animation as module
from maya_toolkit.tools.advanced_skeleton_animation import engine, mocapx_contract


class TestAdvancedSkeletonAnimation(unittest.TestCase):
    def test_catalog_distinguishes_interactive_entrypoints(self):
        self.assertEqual(len(engine.OPERATIONS),46)
        self.assertEqual(engine.OPERATIONS['mocap_matcher']['execution_mode'],'interactive_ui')
        self.assertEqual(engine.OPERATIONS['dynamics_bake']['execution_mode'],'interactive_dialog')

    def test_unknown_operation_and_kwargs_rejected_before_maya(self):
        with patch.object(engine.mirror,'maya') as maya:
            for args in ({'operation':'arbitrary MEL'}, {'unknown':True}):
                with self.assertRaises(ValueError):
                    engine.preflight(**args)
            maya.assert_not_called()

    def test_anim_rescue_conflict_blocks_scene_operations(self):
        cmds=Mock()
        cmds.about.return_value=False
        cmds.play.return_value=False
        cmds.undoInfo.return_value=True
        cmds.getModifiers.return_value=0
        cmds.objExists.return_value=True
        cmds.sets.return_value=['char:Main']
        cmds.pluginInfo.return_value=['animRescue_2024x64']
        with patch.object(engine,'inspect_source',return_value=('file.mel','6.640')), \
             patch.object(engine.discovery,'resolve'), \
             patch.object(engine.mirror,'resolve_namespace',return_value='char:'), \
             patch.object(engine.mirror,'maya',return_value=(cmds,Mock())):
            with self.assertRaisesRegex(ValueError,'animRescue'):
                engine.preflight(operation='pose_reset')
            cmds.setAttr.assert_not_called()

    def test_registered_as_production(self):
        from maya_toolkit.framework import ToolRegistry
        self.assertIsInstance(ToolRegistry.get('advanced_skeleton_animation'),module.AdvancedSkeletonAnimationTool)

    def test_mocapx_rejects_namespace_before_mutation(self):
        cmds=Mock()
        with self.assertRaisesRegex(ValueError,'命名空间'):
            mocapx_contract.validate(cmds,'character:')
        cmds.assert_not_called()
        self.assertEqual(cmds.mock_calls,[])

    def test_mocapx_missing_plugs_rejected_before_native_call(self):
        cmds=Mock()
        cmds.objExists.return_value=False
        with self.assertRaisesRegex(ValueError,'缺少属性'):
            mocapx_contract.validate(cmds,'')
        cmds.setAttr.assert_not_called()

    def test_catalog_has_maya_evidence_for_every_entry(self):
        self.assertTrue(all(v['verification'].startswith('maya_') for v in engine.OPERATIONS.values()))
        self.assertIn('fixture',engine.OPERATIONS['connect_mocapx']['verification'])

    def test_dry_run_does_not_execute(self):
        from maya_toolkit.core import maya_utils
        with patch.object(maya_utils,'ensure_maya_initialized'), \
             patch.object(engine,'preflight',return_value={'operation':'pose_reset'}), \
             patch.object(engine,'execute') as execute:
            self.assertTrue(module.AdvancedSkeletonAnimationTool().run(dry_run=True).success)
            execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
