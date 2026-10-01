import importlib
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Temporary isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.rdm_tools_v2 import runtime
M = 'RdMToolsV2.RiggingTools.'


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_deferred_box_import_then_real_creation_and_undo_redo(self):
        before = runtime.uuids()
        state = runtime.snapshot()
        module = importlib.import_module(runtime.PREFIX + M + 'Curves.BoxCurve')
        self.assertEqual(before, runtime.uuids())
        self.assertEqual(state, runtime.snapshot())
        result = TOOL.run(action='script', module=M + 'Curves.BoxCurve')
        self.assertTrue(result.success, result.message)
        self.assertEqual(1, len(cmds.ls(type='nurbsCurve')))
        self.assertEqual(16, cmds.getAttr('BoxCurve.overrideColor'))
        cmds.undo()
        self.assertEqual(before, runtime.uuids())
        cmds.redo()
        self.assertTrue(cmds.objExists('BoxCurve'))
        self.assertFalse(TOOL.run(action='script', module=M + 'Curves.BoxCurve').success)

    def test_complete_nondependent_module_imports_never_run_scene_or_ui(self):
        before = runtime.uuids()
        state = runtime.snapshot()
        imported, deferred = [], []
        for name, info in runtime.catalog()['modules'].items():
            if info['pymel_required'] or name.endswith('UItoPY'):
                deferred.append(name)
                continue
            try:
                importlib.import_module(runtime.PREFIX + name)
                imported.append(name)
            except ModuleNotFoundError as exc:
                if exc.name != 'pymel' and not exc.name.startswith('pymel.'):
                    raise
                deferred.append(name)
            self.assertEqual(before, runtime.uuids(), name)
            self.assertEqual(state, runtime.snapshot(), name)
        self.assertGreater(len(imported), 45)
        print('Original module imports without execution:', len(imported), 'dependency-deferred:', len(deferred))

    def test_color_axis_dry_fullscope_and_single_undo(self):
        joint = cmds.createNode('joint', name='jointA')
        other = cmds.createNode('joint', name='outsideScope')
        cmds.select(joint)
        cmds.currentTime(12)
        cmds.autoKeyframe(state=True)
        state = runtime.snapshot()
        for mod, func, arguments, attr, value in ((M + 'Curves.CurveColors', 'colorShape', {'Color': 17}, 'overrideColor', 17), (M + 'ShowHide.RdMToggleAxis', 'setAxisDisplay', {'display': True}, 'displayLocalAxis', True)):
            params = dict(action='call', module=mod, function=func, arguments=arguments, objects=[joint])
            previous = cmds.getAttr(joint + '.' + attr)
            untouched = cmds.getAttr(other + '.' + attr)
            undo = cmds.undoInfo(query=True, undoName=True)
            dry = TOOL.run(dry_run=True, **params)
            self.assertTrue(dry.success, dry.message)
            self.assertEqual(state, runtime.snapshot())
            self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
            result = TOOL.run(**params)
            self.assertTrue(result.success, result.message)
            self.assertEqual(value, cmds.getAttr(joint + '.' + attr))
            self.assertEqual(untouched, cmds.getAttr(other + '.' + attr))
            self.assertEqual(state, runtime.snapshot())
            cmds.undo()
            self.assertEqual(previous, cmds.getAttr(joint + '.' + attr))

    def test_real_cube_curve_matched_pose_and_nested_groups_undo(self):
        obj = cmds.createNode('transform', name='source')
        cmds.setAttr(obj + '.tx', 4)
        cmds.select(obj)
        before = runtime.uuids()
        state = runtime.snapshot()
        result = TOOL.run(action='call', module=M + 'Curves.curveOnSelection', function='curveOnSelectionFunc', arguments={'mode': 'Cube', 'offset': True}, objects=[obj])
        self.assertTrue(result.success, result.message)
        self.assertTrue(result.data['created_node_uuids'])
        self.assertAlmostEqual(4, cmds.xform(obj + '_CC', query=True, translation=True, worldSpace=True)[0])
        self.assertTrue(cmds.objExists(obj + '_CC_Root'))
        self.assertEqual(state, runtime.snapshot())
        cmds.undo()
        self.assertEqual(before, runtime.uuids())
        result = TOOL.run(action='call', module=M + 'Curves.RootAuto', function='offsetGrp', objects=[obj])
        self.assertTrue(result.success, result.message)
        self.assertTrue(cmds.objExists(obj + '_Offset_Grp'))
        cmds.undo()
        self.assertEqual(before, runtime.uuids())

    def test_original_curve_export_exclusive_repeat_readonly(self):
        cmds.circle(name='exportCurve')
        before = runtime.uuids()
        with tempfile.TemporaryDirectory() as folder:
            for i in range(2):
                path = Path(folder) / ('curves%s.json' % i)
                p = dict(action='script', module=M + 'Curves.CurveToJson', output_path=str(path))
                result = TOOL.run(**p)
                self.assertTrue(result.success, result.message)
                rows = json.loads(path.read_text())
                self.assertEqual(1, len(rows))
                self.assertTrue(rows[0]['points'])
                self.assertEqual(before, runtime.uuids())
                self.assertFalse(TOOL.run(**p).success)

    def test_all11_original_control_modes_actual_shapes_and_undo(self):
        for mode in ('Joint', 'Locator', 'CircleX', 'CircleY', 'CircleZ', 'Sphere', 'Cube', 'Hand', 'Foot', 'EyeVisor', 'Pringle'):
            with self.subTest(mode=mode):
                cmds.file(new=True, force=True)
                obj = cmds.createNode('transform', name='controlSource')
                cmds.setAttr(obj + '.tx', 7)
                cmds.select(obj)
                before = runtime.uuids()
                state = runtime.snapshot()
                result = TOOL.run(action='call', module=M + 'Curves.curveOnSelection', function='curveOnSelectionFunc', arguments={'mode': mode}, objects=[obj])
                self.assertTrue(result.success, result.message)
                created = result.data['created_node_uuids']
                self.assertTrue(created, mode)
                targets = [n for identifier in created for n in cmds.ls(identifier, long=True) or [] if cmds.objectType(n, isAType='transform')]
                self.assertTrue(targets)
                self.assertTrue(any(abs(cmds.xform(n, query=True, translation=True, worldSpace=True)[0] - 7) < 1e-6 for n in targets), mode)
                self.assertEqual(state, runtime.snapshot())
                cmds.undo()
                self.assertEqual(before, runtime.uuids())

    def test_instances_empty_joint_scope_lock_legacy_scope_and_missing_pymel(self):
        cmds.select(clear=True)
        self.assertFalse(TOOL.run(action='call', module=M + 'ShowHide.RdMToggleAxis', function='setAxisDisplay').success)
        joint = cmds.createNode('joint')
        cmds.setAttr(joint + '.overrideColor', lock=True)
        self.assertFalse(TOOL.run(action='call', module=M + 'Curves.CurveColors', function='colorShape', objects=[joint]).success)
        a = cmds.createNode('transform', name='parentA')
        b = cmds.createNode('transform', name='parentB')
        child = cmds.createNode('transform', name='multi', parent=a)
        cmds.parent(child, b, add=True)
        rejected = TOOL.run(action='call', module=M + 'Curves.RootAuto', function='rootAuto', objects=['|parentA|multi'])
        self.assertFalse(rejected.success)
        self.assertIn('Instanced', rejected.message)
        result = TOOL.run(action='script', module=M + 'Tools.BendyRibbons', allow_native_scope=True, objects=[joint])
        self.assertFalse(result.success)
        self.assertIn('PyMel', result.message)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
