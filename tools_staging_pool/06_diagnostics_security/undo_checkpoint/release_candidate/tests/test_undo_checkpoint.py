from pathlib import Path
import importlib.util
import sys
import unittest
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    sys.path.insert(0,str(rc));from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool;tool=UndoCheckpointTool()
from maya_toolkit.tools.undo_checkpoint import manager
from maya_toolkit.tools.undo_checkpoint.shelf import BUTTONS,command
class Tests(unittest.TestCase):
    def test_queue_format_has_unnamed_entries_and_order_guard(self):
        rows=manager.parse_queue(['0: ','1: mtbCheckpoint_cp_A','2: ']);self.assertEqual([r['name'] for r in rows],['','mtbCheckpoint_cp_A',''])
        with self.assertRaises(RuntimeError):manager.parse_queue(['0: a','3: b'])
    def test_shelf_commands_real_newlines_compile_without_path_dependency(self):
        for identifier,label,image,expression in BUTTONS:
            value=command(expression);compile(value,'Shelf '+identifier,'exec');self.assertIn('\n',value);self.assertNotIn('sys.path',value)
if __name__=='__main__':unittest.main()
