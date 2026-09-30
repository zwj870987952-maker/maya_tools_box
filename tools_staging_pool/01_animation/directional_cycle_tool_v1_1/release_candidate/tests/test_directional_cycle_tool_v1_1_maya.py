import json
import os
from pathlib import Path
import runpy
import sys
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
from maya_toolkit.tools.directional_cycle_tool_v1_1 import proxy, runtime, algorithms


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.controllers = self.fixture(2)

    def fixture(self, feet):
        master = cmds.createNode('transform', name='master')
        nodes = [master] + [cmds.createNode('transform', name=name, parent=master) for name in ['foot' + str(i) for i in range(feet)] + ['body', 'upper', 'head']]
        nodes = [cmds.ls(n, long=True)[0] for n in nodes]
        for index, foot in enumerate(nodes[1:feet + 1]):
            for time, value in ((1, 0), (3, 4 + index), (5, 8 + index)):
                cmds.setKeyframe(foot, attribute='tx', time=time, value=value)
        cmds.setAttr(nodes[-3] + '.ty', 20)
        cmds.setAttr(nodes[-1] + '.ty', 50)
        cmds.currentTime(1)
        cmds.select(nodes[-2])
        return nodes

    def run_cycle(self, **kwargs):
        result = TOOL.run(action='run', controllers=self.controllers, feet_number=len(self.controllers) - 4, start=1, end=5, **kwargs)
        self.assertTrue(result.success, result.message + str(result.errors) + str(result.data))
        return result

    def test_dry_run_and_guards(self):
        before = set(cmds.ls(uuid=True))
        selection = cmds.ls(selection=True, long=True)
        result = TOOL.run(dry_run=True, action='run', controllers=self.controllers, start=1, end=5)
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, set(cmds.ls(uuid=True)))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        cmds.setAttr(self.controllers[1] + '.tx', lock=True)
        self.assertFalse(TOOL.validate(action='run', controllers=self.controllers, start=1, end=5).success)
        with self.assertRaises(RuntimeError):
            algorithms.run_side()
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_left_right_live_foot_rotation_all_constraints_cleanup(self):
        for direction, sign in (('left', -1), ('right', 1)):
            if proxy.records():
                self.setUp()
            result = self.run_cycle(direction=direction, bake=False, correction_locators=False)
            self.assertTrue(result.data['constraint'])
            cmds.currentTime(5)
            pos = cmds.xform(self.controllers[1], query=True, worldSpace=True, translation=True)
            self.assertAlmostEqual(sign * 8, pos[2], places=3)
            uid = result.data['record_uuid']
            self.assertFalse(TOOL.validate(action='run', controllers=self.controllers, start=1, end=5).success)
            cleaned = TOOL.run(action='cleanup', record_id=uid)
            self.assertTrue(cleaned.success, cleaned.message)
            self.assertFalse(cmds.ls(type='constraint'))
            self.assertFalse([n for n in cmds.ls(type='locator') or [] if proxy.owned(n)])
            self.assertTrue(all(cmds.objExists(n) for n in self.controllers))

    def test_baked_layer_unique_foreign_name_and_undo(self):
        foreign = cmds.animLayer('Left')
        root = cmds.animLayer(query=True, root=True)
        cmds.animLayer(root, edit=True, selected=True)
        before = set(cmds.ls(uuid=True))
        selection = cmds.ls(selection=True, long=True)
        cmds.flushUndo()
        result = self.run_cycle(direction='left', correction_locators=False)
        self.assertTrue(cmds.objExists(foreign))
        self.assertTrue(result.data['layer'])
        self.assertTrue(all(cmds.animLayer(n, query=True, override=True) for n in result.data['layer']))
        self.assertFalse(result.data['helper'])
        self.assertFalse(result.data['constraint'])
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(1, cmds.currentTime(query=True))
        self.assertTrue(cmds.animLayer(root, query=True, selected=True))
        cmds.undo()
        self.assertEqual(before, set(cmds.ls(uuid=True)))

    def test_back_reverses_feet_and_pelvis_layer(self):
        result = self.run_cycle(direction='back', bake=False, correction_locators=False)
        helpers = [n for n in result.data['helper'] if cmds.nodeType(n) == 'transform' and 'Loc_Feet' in n]
        self.assertEqual(2, len(helpers))
        for helper in helpers:
            values = cmds.keyframe(helper, attribute='tx', query=True, valueChange=True)
            self.assertGreater(values[0], values[-1])
        self.assertEqual(1, len(result.data['layer']))
        self.assertIn('Back_Pelvis', result.data['layer'][0])
        cleaned = TOOL.run(action='cleanup', record_id=result.data['record_uuid'], remove_layers=True)
        self.assertTrue(cleaned.success, cleaned.message)
        self.assertFalse(cleaned.data['layers'])

    def test_three_feet_correction_counter_rotation_and_bake(self):
        cmds.file(new=True, force=True)
        self.controllers = self.fixture(3)
        result = self.run_cycle(direction='right', bake=False, correction_locators=True, counter_rotation=True)
        corrections = [n for n in result.data['helper'] if cmds.nodeType(n) == 'transform' and 'CorrectionLoc_' in n.rsplit('|', 1)[-1]]
        self.assertEqual(3, len(corrections))
        self.assertFalse([n for n in result.data['helper'] if 'Temp_' in n or 'Master_CorrectionLoc' in n])
        for node in corrections:
            shape = cmds.listRelatives(node, shapes=True, fullPath=True)[0]
            self.assertEqual(30, cmds.getAttr(shape + '.localScaleX'))
        self.assertTrue(TOOL.run(action='cleanup', record_id=result.data['record_uuid']).success)
        result = self.run_cycle(direction='back', bake=True, correction_locators=True)
        self.assertEqual(2, len(result.data['layer']))
        self.assertFalse(result.data['helper'])
        self.assertFalse(result.data['constraint'])

    def test_uuid_save_reload_and_foreign_child_refusal(self):
        result = self.run_cycle(bake=False, correction_locators=False)
        uid = result.data['record_uuid']
        helper = next(n for n in result.data['helper'] if cmds.nodeType(n) == 'transform')
        helper = cmds.rename(helper, 'renamedCycleHelper')
        foreign = cmds.createNode('transform', name='foreignChild', parent=helper)
        before = set(cmds.ls(uuid=True))
        failed = TOOL.run(action='cleanup', record_id=uid)
        self.assertFalse(failed.success)
        self.assertEqual(before, set(cmds.ls(uuid=True)))
        cmds.parent(foreign, world=True)
        with tempfile.TemporaryDirectory() as scratch:
            path = str(Path(scratch) / 'cycle.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, open=True, force=True)
            cleaned = TOOL.run(action='cleanup', record_id=uid)
            self.assertTrue(cleaned.success, cleaned.message)
            self.assertTrue(cmds.objExists('foreignChild'))

    def test_failure_restores_state_and_is_undoable(self):
        before = set(cmds.ls(uuid=True))
        selection = cmds.ls(selection=True, long=True)
        cmds.flushUndo()
        with patch.object(algorithms, 'run_side', side_effect=RuntimeError('injected')):
            result = TOOL.run(action='run', controllers=self.controllers, start=1, end=5)
        self.assertFalse(result.success)
        self.assertEqual('failed', result.data['state'])
        self.assertFalse(runtime._ACTIVE)
        self.assertIsNone(algorithms.cmds)
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(1, cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual(before, set(cmds.ls(uuid=True)))


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
