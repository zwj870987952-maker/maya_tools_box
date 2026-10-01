"""Isolated complete MEL compilation/numeric/curve utility checks; no fake GUI."""
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Use isolated staging mayapy runner')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.shift_animation_v3_2 import runtime


class Maya(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def call(self,**kw):
        r=TOOL.run(**kw)
        self.assertTrue(r.success,str(r.message)+' '+str(r.errors))
        return r.data

    def test_complete_mel_compiles_without_scene_ui_side_effects(self):
        before=set(cmds.ls(uuid=True)); time=cmds.currentTime(query=True)
        runtime.load_vendor()
        for p in runtime.catalog()['unique_procedures']:
            self.assertTrue(mel.eval('whatIs '+p).startswith('Mel procedure found in:'),p)
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        self.assertEqual(time,cmds.currentTime(query=True))
        self.assertFalse(cmds.window('SHIFTING_animation',exists=True))

    def test_original_acceleration_weighting_zero_and_moving_curves_is_readonly(self):
        curve=cmds.createNode('animCurveTU',name='motionCurve')
        for t,v in ((1,0),(2,1),(3,3)):
            cmds.setKeyframe(curve,time=t,value=v)
        before=set(cmds.ls(uuid=True)); undo=cmds.undoInfo(query=True,undoName=True)
        result=self.call(action='analyze_curve',curve=curve,start_value=0,end_value=6,relative=False)
        self.assertEqual([0,2,6],result['values'])
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))
        zero=cmds.createNode('animCurveTU',name='stationaryCurve')
        for t in (1,2,3):
            cmds.setKeyframe(zero,time=t,value=0)
        out=self.call(action='analyze_curve',curve=zero,start_value=0,end_value=6,relative=False)
        # This original fallback advances at the first sample as well.
        self.assertEqual([2,4,6],out['values'])

    def test_dry_layer_and_custom_attribute_cleanup_guard_without_batch_simulation(self):
        main=cmds.spaceLocator(name='mainCtrl')[0]
        pelvis=cmds.spaceLocator(name='pelvisCtrl')[0]
        cmds.setKeyframe(main,attribute='tx',time=1,value=0)
        cmds.setKeyframe(main,attribute='tx',time=10,value=5)
        layer=cmds.animLayer('shiftInput')
        cmds.animLayer(layer,edit=True,attribute=main+'.tx')
        cmds.setKeyframe(main,attribute='tx',time=1,value=0,animLayer=layer)
        cmds.setKeyframe(main,attribute='tx',time=10,value=2,animLayer=layer)
        before=set(cmds.ls(uuid=True)); oldtime=cmds.currentTime(query=True); undo=cmds.undoInfo(query=True,undoName=True)
        dry=TOOL.run(dry_run=True,action='match',layer=layer)
        self.assertTrue(dry.success,dry.message)
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        self.assertEqual(oldtime,cmds.currentTime(query=True))
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))
        outside=cmds.spaceLocator(name='outsideControl')[0]
        curve=(cmds.animLayer(layer,query=True,animCurves=True) or [])[0]
        cmds.connectAttr(curve+'.output',outside+'.tx')
        shared=TOOL.run(dry_run=True,action='match',layer=layer)
        self.assertFalse(shared.success)
        self.assertIn('shared consumer',shared.message)
        cmds.disconnectAttr(curve+'.output',outside+'.tx')
        before=runtime.all_uuids()
        unavailable=TOOL.run(action='match',layer=layer)
        self.assertFalse(unavailable.success)
        self.assertIn('interactive Maya',unavailable.message)
        self.assertEqual(before,runtime.all_uuids())
        cmds.addAttr(main,longName='IK_FK',attributeType='double',keyable=True)
        blocked=TOOL.run(dry_run=True,action='root_motion',layer=layer,main=main,pelvis=pelvis)
        self.assertFalse(blocked.success)
        self.assertIn('IK_FK',blocked.message)
        allowed=TOOL.run(dry_run=True,action='root_motion',layer=layer,main=main,pelvis=pelvis,allow_attribute_cleanup=True)
        self.assertTrue(allowed.success,allowed.message)
        self.assertTrue(cmds.attributeQuery('IK_FK',node=main,exists=True))

    def test_curve_controls_full_vendor_system_delete_and_undo(self):
        curve=cmds.curve(name='manualCurve',degree=3,point=[(0,0,0),(1,0,0),(2,1,0),(3,2,0),(4,2,0)])
        cmds.currentTime(7)
        cmds.autoKeyframe(state=True)
        oldtime=cmds.currentTime(query=True)
        out=self.call(action='curve_controls',objects=[curve])
        sid=out['session']
        self.assertTrue(out['owned'])
        metadata=cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate')
        self.assertEqual(1,len(metadata))
        self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        self.assertEqual(oldtime,cmds.currentTime(query=True))
        other=cmds.curve(name='otherCurve',degree=3,point=[(0,0,0),(1,1,0),(2,2,0),(3,2,0)])
        self.call(action='curve_controls',session=sid,objects=[other])
        self.assertEqual(2,len(cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate')))
        self.call(action='delete_controls',session=sid,objects=[curve])
        self.assertTrue(cmds.objExists(curve))
        self.assertEqual(1,len(cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate')))
        cmds.undo()
        self.assertEqual(2,len(cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate')))
        cmds.redo()
        self.assertTrue(cmds.objExists(curve))
        self.assertEqual(1,len(cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate')))

    def test_wrapper_failure_restores_environment_and_records_undoable_failure(self):
        curve=cmds.curve(name='safeCurve',degree=3,point=[(0,0,0),(1,0,0),(2,1,0),(3,1,0)])
        before=runtime.snapshot()
        def injected(action,options,plan):
            cmds.autoKeyframe(state=not before['autokey'])
            cmds.currentTime(before['time']+6)
            cmds.currentUnit(linear='m')
            cmds.optionVar(intValue=('animBlendBrokenInputOpt',123))
            cmds.createNode('network',name='injectedOwnedTemporary')
            raise RuntimeError('injected vendor failure')
        with patch.object(runtime,'command',injected):
            result=TOOL.run(action='lock_curve',objects=[curve])
        self.assertFalse(result.success)
        after=runtime.snapshot()
        for k in ('time','selection','namespace','autokey','linear','evaluation','track','options','suspended'):
            self.assertEqual(before[k],after[k],k)
        ledger=runtime.Ledger()
        self.assertEqual('lock_curve',ledger.data['failed'])
        self.assertIn(runtime.identity('injectedOwnedTemporary'),ledger.data['owned'])
        self.assertFalse(TOOL.run(action='lock_curve',objects=[curve]).success)
        cmds.undo()
        self.assertFalse(cmds.objExists('injectedOwnedTemporary'))
        self.assertIsNone(runtime.Ledger().node)


if __name__=='__main__':
    unittest.main(verbosity=2)
