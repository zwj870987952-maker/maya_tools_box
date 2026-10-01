import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Disposable Maya runner required')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.retime_tools.runtime import engine_cmds


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.currentUnit(time='film')
        cmds.undoInfo(state=True)
        cmds.playbackOptions(animationStartTime=-4,animationEndTime=10,minTime=-4,maxTime=10)

    def call(self,**kwargs):
        r=TOOL.run(**kwargs)
        self.assertTrue(r.success,str(r.errors))
        return r.data

    def scene(self):
        obj=cmds.createNode('transform',name='actor')
        for t,v in ((-2,-4),(0,0),(2,4),(6,12)):
            cmds.setKeyframe(obj+'.tx',time=t,value=v,inTangentType='linear',outTangentType='linear')
        curve=cmds.listConnections(obj+'.tx',s=True,d=False)[0]
        cmds.select(obj)
        c=self.call(action='create',name='warp')['controller']
        self.call(action='connect',controller=c,nodes=[obj])
        return obj,curve,c

    def test_dry_create_connections_restore_and_state_undo(self):
        obj,curve,c=self.scene()
        cmds.currentTime(3)
        cmds.select(obj)
        before=(set(cmds.ls()),cmds.ls(sl=True,long=True),cmds.currentTime(q=True),cmds.undoInfo(q=True,undoName=True))
        self.assertTrue(TOOL.run(dry_run=True,action='state',controller=c,state='Disable').success)
        self.assertEqual(before,(set(cmds.ls()),cmds.ls(sl=True,long=True),cmds.currentTime(q=True),cmds.undoInfo(q=True,undoName=True)))
        self.call(action='state',controller=c,state='Disable')
        self.assertEqual(2,cmds.getAttr(c+'.retimeState'))
        self.assertTrue(cmds.isConnected('time1.outTime',c+'.timeWarp'))
        self.call(action='state',controller=c,state='Enable')
        self.assertEqual(1,cmds.getAttr(c+'.retimeState'))
        self.assertAlmostEqual(6,cmds.getAttr(obj+'.tx',time=3),places=5)
        cmds.undo()
        self.assertEqual(2,cmds.getAttr(c+'.retimeState'))
        self.assertEqual([obj],cmds.ls(sl=True))
        self.assertEqual(3,cmds.currentTime(q=True))

    def test_shuffle_zero_negative_times_and_delete_disconnect(self):
        obj,curve,c=self.scene()
        cmds.cutKey(c+'.timeWarp',clear=True)
        for t,v in ((-4,-8),(10,20)):
            cmds.setKeyframe(c+'.timeWarp',time=t,value=v,inTangentType='linear',outTangentType='linear')
        self.call(action='shuffle',controller=c)
        self.assertEqual([-1,0,1,3],cmds.keyframe(curve,q=True,timeChange=True))
        self.assertTrue(cmds.isConnected('time1.outTime',curve+'.input'))
        self.assertEqual([-4,0,4,12],cmds.keyframe(curve,q=True,valueChange=True))
        self.assertFalse([n for n in cmds.ls(type='animCurve') if '_tempCurve' in n])
        cmds.undo()
        self.assertTrue(cmds.isConnected(c+'.timeWarp',curve+'.input'))
        self.call(action='state',controller=c,state='Delete')
        self.assertFalse(cmds.objExists(c))
        self.assertTrue(cmds.objExists(obj))
        self.assertTrue(cmds.isConnected('time1.outTime',curve+'.input'))
        cmds.undo()
        self.assertTrue(cmds.objExists(c))

    def test_driver_locks_foreign_children_and_flat_inverse_refused(self):
        obj,curve,c=self.scene()
        cmds.setAttr(obj+'.tx',lock=True)
        self.assertFalse(TOOL.run(dry_run=True,action='bake',controller=c).success)
        cmds.setAttr(obj+'.tx',lock=False)
        child=cmds.createNode('transform',parent=c)
        self.assertFalse(TOOL.run(action='state',controller=c,state='Delete').success)
        self.assertTrue(cmds.objExists(child))
        cmds.cutKey(c+'.timeWarp',clear=True)
        for t in (-4,10):
            cmds.setKeyframe(c+'.timeWarp',time=t,value=2,inTangentType='linear',outTangentType='linear')
        old=cmds.keyframe(curve,q=True,timeChange=True)
        self.assertFalse(TOOL.run(action='shuffle',controller=c).success)
        self.assertEqual(old,cmds.keyframe(curve,q=True,timeChange=True))
        with self.assertRaises(RuntimeError):
            engine_cmds.delete(obj)

    def test_curve_files_bake_roundtrip_and_ui_import_only(self):
        obj,curve,c=self.scene()
        from maya_toolkit.tools.retime_tools import native
        self.assertIsNotNone(native.Window)
        self.assertFalse(TOOL.run(action='open_ui').success)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'warp.json'
            before=set(cmds.ls())
            self.assertTrue(TOOL.run(dry_run=True,action='export_curve',controller=c,file=str(p)).success)
            self.assertFalse(p.exists())
            self.assertEqual(before,set(cmds.ls()))
            self.call(action='export_curve',controller=c,file=str(p))
            self.assertFalse(TOOL.run(action='export_curve',controller=c,file=str(p)).success)
            imported=self.call(action='import_curve',name='restoredWarp',file=str(p))['controller']
            self.assertEqual(cmds.keyframe(c+'.timeWarp',q=True,timeChange=True),cmds.keyframe(imported+'.timeWarp',q=True,timeChange=True))
            self.call(action='bake',controller=c)
            self.assertAlmostEqual(8,cmds.getAttr(obj+'.tx',time=4))
            self.assertTrue(cmds.objExists(curve))

    def test_complete_legacy_mel_compiles_without_scene_writes(self):
        from maya_toolkit.tools.retime_tools.legacy_mel import load_definitions
        from maya import mel
        before=set(cmds.ls())
        load_definitions()
        self.assertTrue(mel.eval('exists mtkRTlegacy_timeWarp'))
        self.assertTrue(mel.eval('exists mtkRTlegacy_tw_velocityTimeWarp'))
        self.assertEqual(before,set(cmds.ls()))


if __name__=='__main__':
    unittest.main(verbosity=2)
