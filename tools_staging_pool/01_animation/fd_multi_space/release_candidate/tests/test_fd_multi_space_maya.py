import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy may run disposable scenes')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.fd_multi_space import scene


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        self.root = cmds.createNode('transform', name='rigRoot')
        self.driven = cmds.createNode('transform', name='control', parent=self.root)
        self.driver = cmds.createNode('transform', name='driverA')
        cmds.setAttr(self.driven + '.tx', 2)
        cmds.select(self.driven)

    def create(self, mode='local', attribute='space', **kwargs):
        result = TOOL.run(action='create', mode=mode, driven=self.driven, driver=self.driver, attribute=attribute, **kwargs)
        self.assertTrue(result.success, result.message + str(result.errors))
        self.driven = result.data['driven']
        return result.data

    def test_local_values_multitarget_and_atomic_undo(self):
        data = self.create()
        self.assertEqual(3, data['phase'])
        self.assertEqual([data['parent']], cmds.listRelatives(self.driven, parent=True, fullPath=True))
        cmds.setAttr(self.driven + '.space', 1)
        cmds.setAttr(self.driver + '.tx', 5)
        self.assertAlmostEqual(7, cmds.xform(self.driven, query=True, worldSpace=True, translation=True)[0])
        cmds.setAttr(self.driven + '.space', 0)
        self.assertAlmostEqual(2, cmds.xform(self.driven, query=True, worldSpace=True, translation=True)[0])
        driver2 = cmds.createNode('transform', name='driverB')
        result = TOOL.run(action='create', driven=self.driven, driver=driver2, attribute='worldSpace')
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual(data['group'], result.data['group'])
        self.assertEqual(data['constraint'], result.data['constraint'])
        self.assertEqual(2, len(cmds.parentConstraint(data['constraint'], query=True, targetList=True)))
        cmds.undo()
        self.assertFalse(cmds.objExists(self.driven + '.worldSpace'))
        self.assertEqual(1, len(cmds.parentConstraint(data['constraint'], query=True, targetList=True)))

    def test_dry_preflight_cycle_foreign_and_full_undo(self):
        before = (cmds.ls(long=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True))
        args = {'action': 'create', 'driven': self.driven, 'driver': self.driver}
        self.assertTrue(TOOL.run(dry_run=True, **args).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True)))
        self.assertFalse(TOOL.validate(**dict(args, driver=self.driven)).success)
        cmds.setAttr(self.driven + '.tx', lock=True)
        self.assertFalse(TOOL.validate(**args).success)
        cmds.setAttr(self.driven + '.tx', lock=False)
        self.create()
        cmds.undo()
        self.assertFalse(cmds.objExists('control.space'))
        self.assertEqual(['rigRoot'], cmds.listRelatives('control', parent=True))
        self.assertFalse(scene.records())
        cmds.redo()
        self.assertEqual(1, len(scene.records()))
        self.assertFalse(TOOL.validate(action='create', driven='control', driver=self.driver, attribute='space2').success)
        self.assertFalse(TOOL.validate(action='open_ui').success)

    def test_reference_existing_parent_and_real_edits(self):
        data = self.create(mode='reference')
        self.assertFalse(data['group'])
        self.assertEqual('|rigRoot', data['parent'])
        cmds.undo()
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'rig.ma')
            cmds.select(self.root)
            cmds.file(path, force=True, type='mayaAscii', exportSelected=True)
            cmds.file(path, reference=True, namespace='referenced')
            self.driven = 'referenced:control'
            self.assertFalse(TOOL.validate(action='create', mode='reference', driven=self.driven, driver=self.driver).success)
            self.assertFalse(TOOL.validate(action='create', mode='local', driven=self.driven, driver=self.driver, allow_reference_edits=True).success)
            data = self.create(mode='reference', allow_reference_edits=True)
            self.assertTrue(cmds.referenceQuery(self.driven, isNodeReferenced=True))
            self.assertTrue(cmds.objExists(self.driven + '.space'))
            self.assertTrue(cmds.referenceQuery(self.driven, editStrings=True))
            cmds.undo()
            self.assertFalse(cmds.objExists('referenced:control.space'))

    def test_staged_uuid_rename_save_reload_and_foreign_target(self):
        result = TOOL.run(action='prepare', driven=self.driven, attribute='space')
        self.assertTrue(result.success, result.message)
        identity = result.data['record_id']
        node = scene.record(identity)['driven']
        cmds.rename(node, 'renamedControl')
        result = TOOL.run(action='add_driver', record_id=identity, driver=self.driver)
        self.assertTrue(result.success, result.message)
        data = scene.record(identity)
        cmds.addAttr(data['driven'], longName='extraLaterAttribute', attributeType='double', keyable=True)
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'saved.ma')
            cmds.file(rename=path)
            cmds.file(save=True, force=True, type='mayaAscii')
            cmds.file(path, open=True, force=True)
            result = TOOL.run(action='connect', record_id=identity)
            self.assertTrue(result.success, result.message + str(result.errors))
            data = scene.record(identity)
            targets = cmds.parentConstraint(data['constraint'], query=True, targetList=True)
            alias = cmds.parentConstraint(data['constraint'], query=True, weightAliasList=True)[0]
            source = cmds.listConnections(data['constraint'] + '.' + alias, source=True, destination=False, plugs=True)[0]
            self.assertTrue(source.endswith('.space'))
            foreign = cmds.createNode('transform', name='foreign')
            cmds.parentConstraint(foreign, data['parent'], edit=True, maintainOffset=True)
            self.assertFalse(TOOL.validate(action='create', driven=data['driven'], driver='driverA', attribute='thirdSpace').success)

    def test_existing_parent_foreign_driver_and_failure_finally(self):
        curve = cmds.createNode('animCurveTL', name='foreignCurve')
        cmds.connectAttr(curve + '.output', self.root + '.tx')
        self.assertFalse(TOOL.validate(action='create', mode='reference', driven=self.driven, driver=self.driver).success)
        cmds.disconnectAttr(curve + '.output', self.root + '.tx')
        cmds.select(self.driven)
        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'connectAttr', side_effect=RuntimeError('injected connect failure')):
            result = TOOL.run(action='create', driven=self.driven, driver=self.driver)
        self.assertFalse(result.success)
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertTrue(cmds.undoInfo(query=True, state=True))
        self.assertEqual(['control'], cmds.ls(selection=True))
        cmds.undo()
        self.assertFalse(cmds.objExists('control.space'))
        self.assertFalse(scene.records())


if __name__ == '__main__':
    unittest.main(verbosity=2)
