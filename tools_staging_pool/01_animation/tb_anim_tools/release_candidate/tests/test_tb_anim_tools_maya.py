import os
from pathlib import Path
import runpy
import tempfile
import unittest

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya profile')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.tb_anim_tools import files


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_inspect_install_and_dry_run_do_not_change_scene_or_preferences(self):
        node = cmds.createNode('transform', name='foreign')
        cmds.setKeyframe(node, attribute='tx', time=1, value=3)
        cmds.select(node)
        before = (cmds.ls(long=True), cmds.ls(selection=True), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True), sorted(cmds.optionVar(list=True)))
        with tempfile.TemporaryDirectory() as folder:
            destination = str(Path(folder) / 'suite')
            dry = TOOL.run(dry_run=True, action='install_files', destination=destination)
            self.assertTrue(dry.success, dry.message)
            self.assertFalse(Path(destination).exists())
            self.assertTrue(TOOL.run().success)
            result = TOOL.run(action='install_files', destination=destination)
            self.assertTrue(result.success, result.message)
            self.assertEqual(files.SHA256, result.data['archive_sha256'])
            self.assertFalse(TOOL.run(action='install_files', destination=destination).success)
            self.assertEqual(before[:3], (cmds.ls(long=True), cmds.ls(selection=True), cmds.currentTime(query=True)))
            self.assertEqual(before[4], sorted(cmds.optionVar(list=True)))
            # File install is outside Undo, explicitly not a scene algorithm.
            self.assertEqual(3, cmds.getAttr(node + '.tx'))

    def test_registration_scoped_to_temp_module_directory_no_overwrite(self):
        exists = cmds.optionVar(exists='tbUpdateType')
        old = cmds.optionVar(query='tbUpdateType') if exists else None
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                dest = root / 'suite'
                mods = root / 'modules'
                mods.mkdir()
                self.assertTrue(TOOL.run(action='install_files', destination=str(dest)).success)
                args = dict(action='register_module', destination=str(dest), module_dir=str(mods))
                self.assertFalse(TOOL.run(**args).success)
                args['acknowledge_external_effects'] = True
                result = TOOL.run(dry_run=True, **args)
                self.assertTrue(result.success, result.message)
                self.assertEqual([], list(mods.iterdir()))
                self.assertEqual(old, cmds.optionVar(query='tbUpdateType') if exists else None)
                result = TOOL.run(**args)
                self.assertTrue(result.success, result.message)
                self.assertEqual(2, cmds.optionVar(query='tbUpdateType'))
                text = (mods / 'tbAnimTools.mod').read_text(encoding='utf-8')
                self.assertIn(str(dest), text)
                self.assertIn('MAYAVERSION:2025', text)
                self.assertFalse(TOOL.run(**args).success)
                self.assertEqual(text, (mods / 'tbAnimTools.mod').read_text(encoding='utf-8'))
                self.assertFalse(TOOL.run(action='launch_native', destination=str(dest), acknowledge_external_effects=True).success)
                self.assertNotIn('tbtoolsInstaller', __import__('sys').modules)
        finally:
            if exists:
                cmds.optionVar(intValue=('tbUpdateType', old))
            elif cmds.optionVar(exists='tbUpdateType'):
                cmds.optionVar(remove='tbUpdateType')


if __name__ == '__main__':
    unittest.main(verbosity=2)
