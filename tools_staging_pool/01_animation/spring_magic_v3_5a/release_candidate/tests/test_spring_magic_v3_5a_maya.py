"""Actual isolated Maya checks; no QWidget or pretend PyMel engine."""
import importlib
import os
from pathlib import Path
import runpy
import unittest

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Run only through run_mayapy_check.py with temporary Maya preferences')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.spring_magic_v3_5a import runtime


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def test_missing_dependency_is_explicit_and_preflight_does_not_write(self):
        nodes=runtime.snapshot()
        frame=cmds.currentTime(query=True)
        undo=cmds.undoInfo(query=True,undoName=True)
        result=TOOL.run(dry_run=True,action='status')
        self.assertTrue(result.success,result.message)
        self.assertEqual(nodes,runtime.snapshot())
        self.assertEqual(frame,cmds.currentTime(query=True))
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))
        if not runtime.pymel_available():
            result=TOOL.run(dry_run=True,action='compute',pose_match=True)
            self.assertFalse(result.success)
            self.assertIn('PyMel',result.message)
            self.assertEqual(nodes,runtime.snapshot())
            print('FULL_ENGINE_NOT_RUN: compatible PyMel absent; no GUI/collision/bind/bake claim')

    def test_uuid_ownership_survives_rename_and_undo(self):
        with self.assertRaises(ValueError):
            runtime.node_list(['does_not_exist'])
        session,state=runtime.new_session()
        before=runtime.snapshot()
        capsule=cmds.createNode('transform',name='owned_capsule')
        runtime.record_new(state,before)
        uid=runtime.identity(capsule)
        state['capsules']=[uid]
        runtime.save_state(session,state)
        renamed=cmds.rename(capsule,'renamed_owned_capsule')
        self.assertEqual(runtime.identity(renamed),uid)
        self.assertIn(renamed,runtime.resolve(uid))
        foreign=cmds.createNode('transform',name='foreign_child',parent=renamed)
        with self.assertRaisesRegex(ValueError,'Foreign dependent'):
            runtime.deletion_guard([renamed],state)
        cmds.parent(foreign,world=True)
        runtime.deletion_guard([renamed],state)
        cmds.delete(renamed)
        cmds.undo()
        self.assertTrue(runtime.resolve(uid))

    def test_environment_restored_on_exception(self):
        a=cmds.createNode('transform',name='a')
        b=cmds.createNode('transform',name='b')
        cmds.select(a)
        cmds.currentTime(12)
        cmds.autoKeyframe(state=True)
        with self.assertRaisesRegex(RuntimeError,'injected'):
            with runtime.environment([b]):
                cmds.currentTime(23)
                cmds.select(b)
                raise RuntimeError('injected')
        self.assertEqual([a],cmds.ls(selection=True))
        self.assertEqual(12,cmds.currentTime(query=True))
        self.assertTrue(cmds.autoKeyframe(query=True,state=True))

    def test_batch_progress_decorator_returns_and_propagates(self):
        decorators=importlib.import_module('maya_toolkit.tools.spring_magic_v3_5a.native.decorators')
        @decorators.gShowProgress()
        def normal():
            normal.progress(50.5)
            return 17
        self.assertEqual(17,normal())
        self.assertFalse(normal.isInterrupted())
        @decorators.gShowProgress()
        def failing():
            raise RuntimeError('injected progress failure')
        with self.assertRaisesRegex(RuntimeError,'injected progress failure'):
            failing()

    def test_complete_engine_requires_actual_pymel(self):
        if not runtime.pymel_available():
            self.skipTest('Compatible PyMel absent; full spring/collision/binding runtime and GUI not exercised')
        core=importlib.import_module('maya_toolkit.tools.spring_magic_v3_5a.native.core')
        self.assertTrue(callable(core.SpringMagicMaya))
        # Interactive acceptance covers complete physics and UI; import alone
        # is not treated as numerical/rigging validation.


if __name__=='__main__':
    unittest.main(verbosity=2)
