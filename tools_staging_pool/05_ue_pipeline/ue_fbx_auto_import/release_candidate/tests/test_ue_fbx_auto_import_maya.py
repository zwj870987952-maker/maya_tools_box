from pathlib import Path
import json
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
candidate = Path(__file__).resolve().parents[1]
# Staging launch must supply the independent engine package path itself.
import importlib.util
spec = importlib.util.spec_from_file_location('candidate_launcher', candidate / 'launch_candidate.py')
launcher = importlib.util.module_from_spec(spec); spec.loader.exec_module(launcher)
tool_instance = launcher.load_tool()
class Tests(unittest.TestCase):
    def test_config_only_preserves_dirty_scene_and_dryrun(self):
        with tempfile.TemporaryDirectory() as d:
            cmds.file(new=True, force=True); cube = cmds.polyCube()[0]; cmds.setAttr(cube + '.tx', 7)
            before = (cmds.ls(uuid=True), cmds.file(q=True, modified=True), cmds.file(q=True, sceneName=True), cmds.undoInfo(q=True, undoName=True))
            fbx = Path(d) / 'Walk.fbx'; fbx.write_bytes(b'fbx')
            config = {'fbx_files':[str(fbx)], 'destination_content_path':'/Game/Anim', 'skeleton_path':'/Game/Hero_Skeleton'}
            out = Path(d) / 'Configs'; tool = tool_instance
            self.assertTrue(tool.run(dry_run=True, action='generate_config', config=config, output_dir=str(out)).success)
            self.assertFalse(out.exists())
            result = tool.run(action='generate_config', config=config, output_dir=str(out))
            self.assertTrue(result.success, result); self.assertEqual(json.loads(Path(result.data['output']).read_text()), config)
            self.assertEqual((cmds.ls(uuid=True), cmds.file(q=True, modified=True), cmds.file(q=True, sceneName=True), cmds.undoInfo(q=True, undoName=True)), before)
            self.assertFalse(tool.run(dry_run=True, action='show_ui').success)
if __name__ == '__main__': unittest.main()
