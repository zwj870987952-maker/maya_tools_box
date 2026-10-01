import json
import math
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.overslapper import runtime


def keys(plug):
    return (cmds.keyframe(plug, q=True, timeChange=True) or [], cmds.keyframe(plug, q=True, valueChange=True) or [])


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.parent = cmds.createNode('transform', n='driver')
        self.control = cmds.createNode('transform', n='control1', parent=self.parent)
        for frame, value in ((1, 0), (3, 4), (5, 0), (8, 2)):
            cmds.setKeyframe(self.parent, at='tx', t=frame, v=value)
            cmds.setKeyframe(self.parent, at='rz', t=frame, v=value * 10)
        cmds.setKeyframe(self.control, at='tx', t=0, v=2)
        cmds.setKeyframe(self.control, at='tx', t=10, v=2)
        cmds.setAttr(self.control + '.ty', 7)
        cmds.setAttr(self.control + '.tz', 9)
        cmds.currentTime(3)
        cmds.select(self.control)
        cmds.autoKeyframe(state=True)
        cmds.namespace(add='work')
        cmds.namespace(set=':work')

    def ok(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    def snapshot(self):
        return [cmds.currentTime(q=True), cmds.ls(sl=True, long=True), cmds.autoKeyframe(q=True, state=True), cmds.namespaceInfo(currentNamespace=True)]

    def test_translation_additive_axes_zero_cycle_readonly_and_undo(self):
        cmds.cutKey(self.parent, at='rz', clear=True)
        cmds.setAttr(self.parent + '.rz', 0)
        a = dict(mode='translation', targets=[self.control], frame_range=[1, 6], axes='x', animation_type='additive', stiffness=0, frame_lag=1)
        before = self.snapshot()
        k = keys(self.control + '.tx')
        undo = cmds.undoInfo(q=True, undoName=True)
        self.ok(dry_run=True, **a)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(k, keys(self.control + '.tx'))
        self.assertEqual(undo, cmds.undoInfo(q=True, undoName=True))
        # Expected native OS displacement = parent's delayed translation - current translation.
        expected = [2 + cmds.getAttr(self.parent + '.tx', time=f - 1) - cmds.getAttr(self.parent + '.tx', time=f) for f in range(1, 7)]
        self.ok(**a)
        for f, value in enumerate(expected, 1):
            self.assertAlmostEqual(value, cmds.getAttr(self.control + '.tx', time=f), places=5)
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 10], keys(self.control + '.tx')[0])
        self.assertEqual(7, cmds.getAttr(self.control + '.ty'))
        self.assertEqual(9, cmds.getAttr(self.control + '.tz'))
        self.assertEqual(before, self.snapshot())
        cmds.undo()
        self.assertEqual(k, keys(self.control + '.tx'))
        cmds.redo()
        self.assertEqual(8, len(keys(self.control + '.tx')[0]))
        self.ok(**dict(a, animation_type='replacer', strength=0, cycle=True))
        self.assertTrue(all(abs(cmds.getAttr(self.control + '.tx', time=f)) < 1e-7 for f in range(1, 7)))

    def test_rotation_orders_single_transform_group_stiffness(self):
        for order in range(6):
            cmds.setAttr(self.control + '.rotateOrder', order)
            d = self.ok(targets=[self.control], frame_range=[1, 6], axes='z', stiffness_values=[[0.25]], distance=1, distance_only=True)
            self.assertEqual(6, d['sample_count'])
            self.assertEqual([1, 2, 3, 4, 5, 6], keys(self.control + '.rz')[0])
            self.assertTrue(all(math.isfinite(v) for v in keys(self.control + '.rz')[1]))
        # No children uses default distance, not child[0] exception.
        self.ok(targets=[self.control], frame_range=[1, 6], axes='z')
        before = self.snapshot()
        self.assertFalse(TOOL.run(targets=[self.control], frame_range=[1, 6], stiffness_values=[[0.5, 0.5]]).success)
        self.assertEqual(before, self.snapshot())

    def test_wind_paths_nonaliased_namespace_scope_and_enable_undo(self):
        before = self.snapshot()
        n = self.ok(action='create_wind')['created_wind']
        self.assertEqual(before, self.snapshot())
        self.assertEqual(30, cmds.getAttr(cmds.listRelatives(n, shapes=True, fullPath=True)[0] + '.controlPoints', size=True))
        cmds.namespace(set=':')
        cmds.namespace(add='a')
        cmds.namespace(add='a:b')
        cmds.namespace(add='a:b:c')
        n = cmds.rename(n, 'a:b:c:wind')
        full = runtime.node(n)
        d = self.ok(action='inspect')
        self.assertEqual([full], d['winds'])
        from maya_toolkit.tools.overslapper.settings import normalize
        opts = normalize(targets=[self.control], frame_range=[1, 6], wind=True, winds=[full])
        plan = runtime.prepare(opts)
        with runtime.context(plan):
            p = runtime.native()
            for path, inv in (p.create_wind_path(7, 1, 1), p.create_translation_wind_path(6, 1, 1, False), p.create_translation_wind_path(6, 1, 1, True)):
                self.assertIsNot(path[0], inv[0])
                for a, b in zip(path, inv):
                    self.assertTrue(all(abs(a[i] + b[i]) < 1e-8 for i in (12, 13, 14)))
                self.assertGreater(path[0][12], 0)
        self.ok(action='set_winds', winds=[full], enabled=False)
        self.assertFalse(cmds.getAttr(full + '.wind'))
        cmds.undo()
        self.assertTrue(cmds.getAttr(full + '.wind'))
        self.ok(mode='translation', targets=[self.control], frame_range=[1, 6], wind=True, winds=[full], wind_absolute=True, axes='x')
        self.ok(targets=[self.control], frame_range=[1, 6], wind=True, winds=[full], axes='z', cycle=True, remove_parent=self.parent)
        with self.assertRaises(ValueError):
            runtime.native().create_wind_control()

    def test_explicit_layers_preserve_base_other_layer_and_restore_undo(self):
        cmds.namespace(set=':')
        other = cmds.animLayer('foreignLayer')
        cmds.animLayer(other, e=True, attribute=self.control + '.tx')
        cmds.setKeyframe(self.control, at='tx', t=2, v=5, animLayer=other, noResolve=True)
        foreign = runtime.layer_curve(other, self.control + '.tx')
        fk = keys(foreign)
        base = cmds.animLayer(q=True, root=True)
        base_curve = runtime.layer_curve(base, self.control + '.tx')
        bk = keys(base_curve)
        before = self.snapshot()
        flags = {l: [cmds.animLayer(l, q=True, selected=True), cmds.animLayer(l, q=True, preferred=True)] for l in cmds.ls(type='animLayer')}
        self.assertFalse(TOOL.run(mode='translation', targets=[self.control], axes='x', frame_range=[1, 6]).success)
        data = self.ok(mode='translation', targets=[self.control], axes='x', frame_range=[1, 6], new_layer=True, override=True, strength=0.5)
        destination = data['created_layer']
        self.assertFalse(cmds.animLayer(destination, q=True, selected=True))
        self.assertFalse(cmds.animLayer(destination, q=True, preferred=True))
        curve = runtime.layer_curve(destination, self.control + '.tx')
        self.assertEqual([1, 2, 3, 4, 5, 6], keys(curve)[0])
        self.assertEqual(fk, keys(foreign))
        self.assertEqual(bk, keys(base_curve))
        self.assertEqual(before, self.snapshot())
        for l, f in flags.items():
            self.assertEqual(f, [cmds.animLayer(l, q=True, selected=True), cmds.animLayer(l, q=True, preferred=True)])
        self.ok(mode='translation', targets=[self.control], axes='x', frame_range=[2, 5], target_layer=destination, animation_type='deleteall', strength=0)
        self.assertEqual([2, 3, 4, 5], keys(curve)[0])
        self.assertEqual(fk, keys(foreign))
        cmds.undo()
        self.assertEqual([1, 2, 3, 4, 5, 6], keys(curve)[0])

    def test_failure_closes_chunk_restore_and_reject_drivers_shared_curves(self):
        before = self.snapshot()
        original = keys(self.control + '.tx')
        real = runtime.mc.setKeyframe
        count = [0]
        def fail(*args, **kwargs):
            count[0] += 1
            if count[0] == 2:
                raise RuntimeError('injected native write failure')
            return real(*args, **kwargs)
        with patch.object(runtime.mc, 'setKeyframe', fail):
            self.assertFalse(TOOL.run(mode='translation', targets=[self.control], frame_range=[1, 6], axes='x').success)
        self.assertEqual(before, self.snapshot())
        self.assertIsNone(runtime._ACTIVE)
        cmds.undo()
        self.assertEqual(original, keys(self.control + '.tx'))
        constraint = cmds.parentConstraint(self.parent, self.control, mo=True)[0]
        self.assertFalse(TOOL.run(targets=[self.control], frame_range=[1, 6]).success)
        cmds.delete(constraint)
        curve = (cmds.listConnections(self.control + '.tx', s=True, d=False, type='animCurve') or [None])[0]
        cmds.connectAttr(curve + '.output', self.control + '.ty')
        self.assertFalse(TOOL.run(mode='translation', targets=[self.control], frame_range=[1, 6], axes='x').success)
        cmds.disconnectAttr(curve + '.output', self.control + '.ty')
        outside = cmds.createNode('transform', n='outside')
        cmds.connectAttr(curve + '.output', outside + '.tx')
        self.assertFalse(TOOL.run(mode='translation', targets=[self.control], frame_range=[1, 6], axes='x').success)

    def test_presets_protected_and_overshoot(self):
        # Import class definitions only; no QWidget/QApplication is instantiated.
        from maya_toolkit.tools.overslapper.native.overslapper_tool import overslapper_UI
        from types import SimpleNamespace
        class Field:
            def __init__(self, text):
                self.text_value = text
            def text(self):
                return self.text_value
            def setText(self, text):
                self.text_value = text
        class Slider:
            def __init__(self, field):
                self.blocked = False
                self.field = field
            def blockSignals(self, flag):
                old = self.blocked
                self.blocked = flag
                return old
            def setValue(self, value):
                if not self.blocked:
                    self.field.setText('clamped signal changed text')
        field = Field('-1.234')
        slider = Slider(field)
        overslapper_UI.wind_value_changed(SimpleNamespace(wind_strength_value=field, wind_strength_slider=slider))
        self.assertEqual('-1.234', field.text())
        self.assertFalse(slider.blocked)
        default = runtime.read_preset(Path(runtime.__file__).parent / 'native/default.json')
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'preset.json')
            self.ok(dry_run=True, action='write_preset', preset_path=path, preset_data=default)
            self.assertFalse(Path(path).exists())
            self.ok(action='write_preset', preset_path=path, preset_data=default)
            self.assertEqual(default, self.ok(action='read_preset', preset_path=path)['preset_data'])
            self.assertFalse(TOOL.run(action='write_preset', preset_path=path, preset_data=default).success)
            self.ok(action='write_preset', preset_path=path, preset_data=default, overwrite=True)
            self.assertEqual(['preset.json'], sorted(p.name for p in Path(directory).iterdir()))
        self.ok(mode='translation', targets=[self.control], frame_range=[1, 8], axes='x', overshoot=True, overshoot_frequency=3)
        self.assertTrue(all(math.isfinite(v) for v in keys(self.control + '.tx')[1]))
        self.assertFalse(TOOL.run(action='open_ui').success)


if __name__ == '__main__':
    unittest.main(verbosity=2)
