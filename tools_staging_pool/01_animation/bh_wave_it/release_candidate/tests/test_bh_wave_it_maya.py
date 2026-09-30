import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy harness may execute this disposable-scene test')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel

RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.bh_wave_it import runtime
from maya_toolkit.tools.bh_wave_it.contracts import normalize, values


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.nodes = [cmds.createNode('transform', name=name) for name in ['zLast', 'aFirst', 'mid']]
        cmds.select(clear=True)

    def test_full_source_guard_and_gui_refusal(self):
        info = runtime.load_suite()
        self.assertEqual(14, len(info['procedures']))
        self.assertFalse(TOOL.run(action='open_ui').success)
        self.assertFalse(cmds.window('mtbWI_waveItUI', exists=True))
        with self.assertRaises(RuntimeError):
            mel.eval('mtbWI_bh_waveVal();')
        self.assertFalse(runtime._ACTIVE)

    def test_ordered_wave_multiple_axes_custom_and_undo(self):
        for node in self.nodes:
            cmds.addAttr(node, longName='waveAmount', attributeType='double', keyable=True)
        saved = cmds.polyCube(name='selectionMesh')[0] + '.vtx[0]'
        cmds.select(saved)
        args = dict(action='wave', objects=self.nodes, rotate_axes=['X', 'Y', 'Z'], translate_axes=['Y'], custom_attributes=['waveAmount'], amplitude=.3, frequency=.7, phase=1, base_offset=2)
        cmds.flushUndo()
        result = TOOL.run(**args)
        self.assertTrue(result.success, result.message)
        expected = values(normalize(**args), 3)
        for i, node in enumerate(self.nodes):
            for attr in ['rotateX', 'rotateY', 'rotateZ', 'translateY', 'waveAmount']:
                self.assertAlmostEqual(expected[i], cmds.getAttr(node + '.' + attr), places=4)
        self.assertEqual(cmds.ls(saved, long=True), cmds.ls(selection=True, long=True))
        self.assertEqual(15, len(result.data['operations']))
        cmds.undo()
        for node in self.nodes:
            self.assertEqual(0, cmds.getAttr(node + '.rotateX'))
            self.assertEqual(0, cmds.getAttr(node + '.waveAmount'))

    def test_presets_and_invert(self):
        for action, freq in [('basic_s', 1), ('inverse_s', -1), ('basic_c', .5), ('inverse_c', -.5), ('invert', -.3)]:
            args = dict(action=action, objects=self.nodes, frequency=.3, phase=2)
            result = TOOL.run(**args)
            self.assertTrue(result.success, result.message)
            self.assertEqual(freq, result.data['effective_frequency'])
            for node, expected in zip(self.nodes, values(normalize(**args), 3)):
                self.assertAlmostEqual(expected, cmds.getAttr(node + '.rotateX'), places=4)

    def test_base_offset_only_first_rotation(self):
        for node in self.nodes:
            cmds.setAttr(node + '.translateY', 7)
            cmds.setAttr(node + '.rotateX', 3)
        result = TOOL.run(action='base_offset', objects=self.nodes, base_offset=20, translate_axes=['Y'])
        self.assertTrue(result.success, result.message)
        self.assertEqual(-20, cmds.getAttr(self.nodes[0] + '.rotateX'))
        self.assertAlmostEqual(3, cmds.getAttr(self.nodes[1] + '.rotateX'))
        self.assertEqual(7, cmds.getAttr(self.nodes[0] + '.translateY'))
        self.assertEqual(1, len(result.data['operations']))

    def test_readonly_dryrun_preflight_lock_driver_components(self):
        before = cmds.ls(long=True)
        cmds.select(self.nodes)
        selection = cmds.ls(selection=True, long=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        result = TOOL.run(dry_run=True, action='wave', objects=self.nodes)
        self.assertTrue(result.success)
        self.assertEqual(before, cmds.ls(long=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        cmds.setAttr(self.nodes[1] + '.rotateX', lock=True)
        self.assertFalse(TOOL.run(action='wave', objects=self.nodes).success)
        self.assertEqual(0, cmds.getAttr(self.nodes[0] + '.rotateX'))
        cmds.setAttr(self.nodes[1] + '.rotateX', lock=False)
        driver = cmds.createNode('multiplyDivide')
        cmds.connectAttr(driver + '.outputX', self.nodes[1] + '.rotateX')
        self.assertFalse(TOOL.run(action='wave', objects=self.nodes).success)
        self.assertFalse(TOOL.run(action='wave', objects=self.nodes, custom_attributes=['missing']).success)

    def test_failure_restores_selection_time_and_guard(self):
        runtime.load_suite()
        cmds.currentTime(9)
        cmds.select(self.nodes[1])
        selection = cmds.ls(selection=True, long=True)
        original = mel.eval
        def fail(code):
            if code == 'mtbWI_bh_waveVal();':
                cmds.select(clear=True)
                cmds.currentTime(12)
                raise RuntimeError('injected MEL failure')
            return original(code)
        with patch('maya.mel.eval', side_effect=fail):
            result = TOOL.run(action='wave', objects=self.nodes)
        self.assertFalse(result.success)
        self.assertEqual(9, cmds.currentTime(query=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertFalse(runtime._ACTIVE)

    def test_animation_no_explicit_keys(self):
        node = self.nodes[0]
        cmds.setKeyframe(node, attribute='rotateX', time=1, value=3)
        cmds.setKeyframe(node, attribute='rotateX', time=10, value=6)
        cmds.autoKeyframe(state=False)
        cmds.currentTime(1)
        before = cmds.keyframe(node, attribute='rotateX', query=True, valueChange=True)
        result = TOOL.run(action='wave', objects=self.nodes, amplitude=0, base_offset=7)
        self.assertTrue(result.success, result.message)
        self.assertEqual(-7, result.data['operations'][0]['after'])
        self.assertEqual(before, cmds.keyframe(node, attribute='rotateX', query=True, valueChange=True))
        cmds.currentTime(10)
        self.assertAlmostEqual(6, cmds.getAttr(node + '.rotateX'))

    def test_duplicate_leaf_and_reference_are_refused(self):
        parent1 = cmds.createNode('transform', name='parentA')
        parent2 = cmds.createNode('transform', name='parentB')
        node1 = cmds.createNode('transform', name='same', parent=parent1)
        cmds.createNode('transform', name='same', parent=parent2)
        self.assertFalse(TOOL.run(action='wave', objects=['same']).success)
        self.assertTrue(TOOL.run(action='wave', objects=[cmds.ls(node1, long=True)[0]]).success)
        import tempfile
        with tempfile.TemporaryDirectory() as scratch:
            file = str(Path(scratch) / 'reference.ma')
            cmds.select(self.nodes[0])
            cmds.file(file, exportSelected=True, type='mayaAscii', force=True)
            cmds.file(file, reference=True, namespace='WIref')
            self.assertFalse(TOOL.run(action='wave', objects=['WIref:zLast']).success)


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
