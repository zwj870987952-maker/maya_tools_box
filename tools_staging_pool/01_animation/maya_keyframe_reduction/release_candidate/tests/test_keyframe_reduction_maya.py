import math
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.keyframe_reduction import runtime
from maya_toolkit.tools.keyframe_reduction.native.classes.keyframeReduction import KeyframeReduction


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        self.node = cmds.circle(name='control', constructionHistory=False)[0]
        for frame in range(1, 21):
            cmds.setKeyframe(self.node, attribute='tx', time=frame, value=frame * 2)
            cmds.setKeyframe(self.node, attribute='ty', time=frame, value=0)
        cmds.keyTangent(self.node, inTangentType='linear', outTangentType='linear')
        self.curve = cmds.listConnections(self.node + '.tx', source=True, destination=False)[0]
        self.constant = cmds.listConnections(self.node + '.ty', source=True, destination=False)[0]
        cmds.currentTime(3)
        cmds.select(self.node)

    def test_linear_constant_auto_and_undo(self):
        before = cmds.keyframe(self.curve, query=True, valueChange=True)
        result = TOOL.run(curves=[self.curve, self.constant], error=.01, tangentSplitAuto=True)
        self.assertTrue(result.success, str((result.message, result.errors)))
        for curve, multiplier in ((self.curve, 2), (self.constant, 0)):
            self.assertEqual(2, cmds.keyframe(curve, query=True, keyframeCount=True))
            for i in range(2, 41):
                time = i / 2
                self.assertAlmostEqual(time * multiplier, cmds.keyframe(curve, query=True, eval=True, time=(time,))[0], places=5)
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(self.curve, query=True, valueChange=True))

    def test_readonly_scope_and_source_bridge(self):
        before = (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True))
        self.assertTrue(TOOL.run(dry_run=True, curves=[self.curve]).success)
        self.assertTrue(TOOL.run(action='inspect', curves=[self.curve]).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True)))
        self.assertGreater(KeyframeReduction(self.curve).reduce(error=.01), 0)
        cmds.undo()
        other = cmds.createNode('transform', name='foreign')
        cmds.connectAttr(self.curve + '.output', other + '.tx')
        self.assertFalse(TOOL.validate(curves=[self.curve]).success)
        cmds.disconnectAttr(self.curve + '.output', other + '.tx')
        cmds.keyTangent(self.curve, outTangentType='step')
        self.assertFalse(TOOL.validate(curves=[self.curve]).success)
        self.assertFalse(TOOL.validate(action='open_ui').success)
        with self.assertRaises(RuntimeError):
            KeyframeReduction(self.constant)._removeKeys([1, 20], 1)

    def test_weighted_split_waveform_and_partial_failure(self):
        for frame in range(1, 21):
            cmds.setKeyframe(self.curve, time=frame, value=math.sin(frame / 5.0))
        result = TOOL.run(curves=[self.curve], error=.05, weightedTangents=True, tangentSplitExisting=True, tangentSplitAngleThreshold=True)
        self.assertTrue(result.success, str((result.message, result.errors)))
        self.assertLessEqual(cmds.keyframe(self.curve, query=True, keyframeCount=True), 20)
        cmds.undo()
        before = cmds.keyframe(self.curve, query=True, valueChange=True)
        real = cmds.setKeyframe
        writes = []
        def fail(*args, **kwargs):
            writes.append(args)
            if len(writes) == 2:
                raise RuntimeError('injected second fitted-key failure')
            return real(*args, **kwargs)
        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'setKeyframe', side_effect=fail):
            result = TOOL.run(curves=[self.curve], error=1)
        self.assertFalse(result.success)
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertFalse(runtime._ACTIVE)
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(self.curve, query=True, valueChange=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
