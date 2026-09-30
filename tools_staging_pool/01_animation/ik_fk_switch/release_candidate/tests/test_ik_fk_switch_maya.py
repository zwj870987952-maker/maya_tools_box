import importlib.util
import json
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
from maya_toolkit.tools.ik_fk_switch import runtime
from maya_toolkit.tools.ik_fk_switch.tool import CONTROLS


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        self.fields = {name: cmds.createNode('transform', name=name) for name in CONTROLS}
        cmds.addAttr(self.fields['switchCtrl'], longName='ikfk', attributeType='double', minValue=0, maxValue=10, keyable=True)
        cmds.select(self.fields['fkwrist'])

    def store(self, **kwargs):
        result = TOOL.run(action='store', **dict(self.fields, **kwargs))
        self.assertTrue(result.success, result.message + str(result.errors))
        return result.data

    def test_store_readonly_rename_save_reload_undo_and_protection(self):
        before = (cmds.ls(long=True), cmds.undoInfo(query=True, undoName=True), cmds.ls(selection=True))
        self.assertTrue(TOOL.run(dry_run=True, action='store', **self.fields).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.undoInfo(query=True, undoName=True), cmds.ls(selection=True)))
        data = self.store(rotOffset=[0, 90, 180])
        self.assertFalse(TOOL.validate(action='store', **self.fields).success)
        cmds.undo()
        self.assertFalse(runtime.records())
        cmds.redo()
        renamed = cmds.rename(self.fields['fkwrist'], 'renamedWrist')
        self.fields['fkwrist'] = renamed
        result = TOOL.run(action='load', record_id=data['record_id'])
        self.assertTrue(result.success, result.message)
        self.assertTrue(result.data['fields']['fkwrist'].endswith('renamedWrist'))
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'saved.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(path, open=True, force=True)
            self.assertTrue(TOOL.run(action='load', record_id=data['record_id']).success)
            self.store(overwrite_store=True, rotOffset=[0, 1, 2])
            cmds.undo()
            self.assertEqual([0, 90, 180], TOOL.run(action='load', record_id=data['record_id']).data['fields']['rotOffset'])
        child = cmds.createNode('transform', name='foreignChild', parent=data['node'])
        self.assertFalse(TOOL.validate(action='store', **self.fields, overwrite_store=True).success)

    def test_json_overwrite_import_update_and_bad_file_no_scene_import(self):
        row = self.store()
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'store.json')
            self.assertTrue(TOOL.run(action='export_store', file_path=path).success)
            self.assertFalse(TOOL.run(action='export_store', file_path=path).success)
            value = json.loads(Path(path).read_text(encoding='utf-8'))
            value['stores'][0]['rotOffset'] = [1, 2, 3]
            Path(path).write_text(json.dumps(value), encoding='utf-8')
            self.assertFalse(TOOL.run(action='import_store', file_path=path).success)
            self.assertTrue(TOOL.run(action='import_store', file_path=path, overwrite_store=True).success)
            self.assertEqual([1, 2, 3], runtime.load_record(row['record_id'])['fields']['rotOffset'])
            cmds.undo()
            self.assertEqual([0, 0, 0], runtime.load_record(row['record_id'])['fields']['rotOffset'])
            value['stores'][0]['rotOffset'] = '__import__("os").system("bad")'
            Path(path).write_text(json.dumps(value), encoding='utf-8')
            self.assertFalse(TOOL.validate(action='import_store', file_path=path, overwrite_store=True).success)

    def test_switch_range_one_ten_keying_undo_and_shared_curve(self):
        for maximum in (1, 10):
            result = TOOL.run(action='switch', direction='to_ik', switchAttrRange=maximum, **self.fields)
            self.assertTrue(result.success, result.message)
            self.assertEqual(maximum, cmds.getAttr(self.fields['switchCtrl'] + '.ikfk'))
            cmds.undo()
            self.assertEqual(0, cmds.getAttr(self.fields['switchCtrl'] + '.ikfk'))
        cmds.currentTime(3)
        result = TOOL.run(action='key', direction='to_fk', **self.fields)
        self.assertTrue(result.success, result.message)
        self.assertEqual([3], cmds.keyframe(self.fields['fkwrist'], attribute='rx', query=True))
        cmds.undo()
        cmds.setKeyframe(self.fields['fkwrist'], attribute='rx', time=1, value=0)
        curve = cmds.listConnections(self.fields['fkwrist'] + '.rx', source=True, destination=False)[0]
        foreign = cmds.createNode('transform', name='foreign')
        cmds.connectAttr(curve + '.output', foreign + '.rx')
        self.assertFalse(TOOL.validate(action='key', **self.fields).success)

    def test_metadata_partial_failure_finally_and_dependency_report(self):
        real = cmds.connectAttr
        calls = []

        def failure(*args, **kwargs):
            calls.append(args)
            if len(calls) == 2:
                raise RuntimeError('injected metadata message failure')
            return real(*args, **kwargs)

        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'connectAttr', side_effect=failure):
            result = TOOL.run(action='store', **self.fields)
        self.assertFalse(result.success)
        self.assertFalse(runtime._ACTIVE)
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        cmds.undo()
        self.assertFalse(runtime.records())
        if not importlib.util.find_spec('pymel'):
            result = TOOL.run(action='match', **self.fields)
            self.assertFalse(result.success)
            self.assertIn('pymel', result.message)
        self.assertFalse(TOOL.validate(action='open_ui').success)

    def test_real_reference_metadata_requires_explicit_edits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'controls.ma')
            cmds.select(list(self.fields.values()))
            cmds.file(path, force=True, type='mayaAscii', exportSelected=True)
            cmds.file(path, reference=True, namespace='ref')
            self.fields = {name: 'ref:' + value for name, value in self.fields.items()}
            self.assertFalse(TOOL.validate(action='store', **self.fields).success)
            row = self.store(allow_reference_edits=True)
            self.assertTrue(all(value.startswith('|ref:') for name, value in runtime.load_record(row['record_id'])['fields'].items() if name in CONTROLS))
            cmds.undo()
            self.assertFalse(runtime.records())

    @unittest.skipUnless(importlib.util.find_spec('pymel'), 'PyMel absent: full original matching/baking/GUI NOT verified')
    def test_original_fk_to_ik_matching_when_pymel_present(self):
        # Offset groups emulate the original zero-pose control assumptions.
        positions = [(0, 0, 0), (4, 1, 0), (8, 0, 0)]
        for name, position in zip(CONTROLS[:3], positions):
            offset = cmds.group(empty=True, name=name + 'Offset')
            cmds.xform(offset, worldSpace=True, translation=position)
            cmds.parent(self.fields[name], offset, relative=True)
        cmds.setAttr(self.fields['ikwrist'] + '.tx', 8)
        result = TOOL.run(action='match', direction='to_ik', **self.fields)
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual([8, 0, 0], cmds.xform(self.fields['ikwrist'], query=True, worldSpace=True, translation=True))
        self.assertEqual(1, cmds.getAttr(self.fields['switchCtrl'] + '.ikfk'))
        cmds.undo()
        self.assertEqual(0, cmds.getAttr(self.fields['switchCtrl'] + '.ikfk'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
