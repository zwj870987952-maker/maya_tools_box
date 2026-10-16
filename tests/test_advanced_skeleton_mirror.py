"""Contract regression; live Maya evidence is recorded in the tool documentation."""
import unittest
from unittest.mock import patch, Mock

from maya_toolkit.tools.advanced_skeleton_mirror import AdvancedSkeletonMirrorTool
from maya_toolkit.tools.advanced_skeleton_mirror import runtime
from maya_toolkit.framework import ToolRegistry


class TestAdvancedSkeletonMirror(unittest.TestCase):
    def test_registered(self):
        self.assertIn('advanced_skeleton_mirror', [t['tool_id'] for t in ToolRegistry.list_tools()])

    def test_invalid_parameters_return_failure_without_native_call(self):
        for args in ({'side': {}}, {'space': []}, {'source_path': 42}, {'typo': True}):
            with self.subTest(args=args), patch.object(runtime, 'maya', return_value=(Mock(), Mock())) as api:
                self.assertFalse(AdvancedSkeletonMirrorTool().validate(**args).success)
                if api.called:
                    self.assertFalse(api.return_value[1].eval.called)
                    self.assertEqual(api.return_value[0].mock_calls, [])

    def test_dry_run_does_not_execute_or_open_undo(self):
        from maya_toolkit.core import maya_utils
        with patch.object(maya_utils, 'ensure_maya_initialized'), \
                patch.object(runtime, 'preflight', return_value={'action': 'mirror'}), \
                patch.object(runtime, 'execute') as execute, \
                patch('maya_toolkit.framework.base_tool.UndoChunkContext') as undo:
            result = AdvancedSkeletonMirrorTool().run(dry_run=True)
            self.assertTrue(result.success)
            self.assertTrue(result.dry_run)
            execute.assert_not_called()
            undo.assert_not_called()


if __name__ == '__main__':
    unittest.main()
