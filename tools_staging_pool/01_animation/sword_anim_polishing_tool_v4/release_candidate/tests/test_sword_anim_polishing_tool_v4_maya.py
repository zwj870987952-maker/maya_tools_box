import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.sword_anim_polishing_tool_v4 import runtime
v=runtime.v


def animated(name):
    node=cmds.createNode('transform',name=name)
    for attr in ('tx','ty','tz','rx','ry','rz'):
        cmds.setKeyframe(node,attribute=attr,time=1,value=0)
        cmds.setKeyframe(node,attribute=attr,time=5,value=10 if attr=='tx' else 0)
    return node


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def test_complete_vendor_compile_no_scene_or_ui_write(self):
        before=v.all_uuids()
        undo=cmds.undoInfo(query=True,undoName=True)
        v.load_vendor()
        for proc in v.catalog()['unique_procedures']:
            self.assertTrue(mel.eval('exists '+v.quote(proc)))
        self.assertEqual(before,v.all_uuids())
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))

    def test_native_constraint_weights_and_pivot(self):
        a=cmds.createNode('transform',name='a')
        b=cmds.createNode('transform',name='b')
        target=cmds.createNode('transform',name='target')
        cmds.setAttr(b+'.tx',3)
        cmds.setAttr(target+'.tx',1)
        before=v.all_uuids()
        result=TOOL.run(action='constraint_weights',objects=[a,b,target])
        self.assertTrue(result.success,result.message)
        self.assertAlmostEqual(2/3,result.data['weights'][0],places=6)
        self.assertAlmostEqual(1/3,result.data['weights'][1],places=6)
        cmds.setAttr(target+'.tx',0)
        result=TOOL.run(action='constraint_weights',objects=[a,b,target])
        self.assertEqual([1,0],result.data['weights'])
        self.assertEqual(before,v.all_uuids())

    def test_full_native_bake_and_undo(self):
        obj=animated('weapon')
        before=v.all_uuids()
        cmds.select(obj)
        frame=cmds.currentTime(query=True)
        evaluation=cmds.evaluationManager(query=True,mode=True)
        result=TOOL.run(dry_run=True,action='bake',objects=[obj],start=1,end=5)
        self.assertTrue(result.success,result.message)
        self.assertEqual(before,v.all_uuids())
        result=TOOL.run(action='bake',objects=[obj],start=1,end=5)
        self.assertTrue(result.success,result.message)
        self.assertEqual([1,2,3,4,5],cmds.keyframe(obj+'.tx',query=True,timeChange=True))
        self.assertEqual(frame,cmds.currentTime(query=True))
        self.assertEqual(evaluation,cmds.evaluationManager(query=True,mode=True))
        cmds.undo()
        self.assertEqual(before,v.all_uuids())
        self.assertEqual([1,5],cmds.keyframe(obj+'.tx',query=True,timeChange=True))
        cmds.redo()
        self.assertEqual([1,2,3,4,5],cmds.keyframe(obj+'.tx',query=True,timeChange=True))

    def test_locked_and_interactive_preflights_and_metadata_restore(self):
        obj=animated('weapon')
        before=v.all_uuids()
        cmds.setAttr(obj+'.rx',lock=True)
        result=TOOL.run(action='parent_in',objects=[obj],start=1,end=5)
        self.assertFalse(result.success)
        self.assertEqual(before,v.all_uuids())
        cmds.setAttr(obj+'.rx',lock=False)
        for action in ('parent_in','begin_aim','begin_sword','begin_reverse','arc_polish'):
            result=TOOL.run(dry_run=True,action=action,objects=[obj])
            self.assertFalse(result.success)
            self.assertIn('interactive',result.message)
        ledger=v.Ledger()
        ledger.save()
        ledger.data['globals']['BARN_curve_sword_remember_SOURCE']=[obj]
        ledger.data['identity_map'][obj]=v.identity(obj)
        ledger.save()
        renamed=cmds.rename(obj,'renamed_weapon')
        ledger=v.Ledger(ledger.sid)
        self.assertEqual([v.resolve(v.identity(renamed))],runtime.live_group(ledger,'source'))
        v.load_vendor()
        ledger.restore_globals()
        self.assertIn(renamed,mel.eval('global string $BARN_curve_sword_remember_SOURCE[]; $mtkTestNames=$BARN_curve_sword_remember_SOURCE;')[0])

    def test_native_motion_path_full_sampling_balances_nested_undo(self):
        v.load_vendor()
        obj=animated('weapon')
        path=cmds.curve(degree=1,point=[(0,0,0),(5,0,0),(10,0,0)])
        loc=cmds.spaceLocator()[0]
        before=v.all_uuids()
        cmds.undoInfo(openChunk=True,chunkName='outerNativePath')
        try:
            motion_path=runtime.native_call('SW_7b95c992be7b036735f7298f89ab9556('+v.quote(obj)+','+v.quote(path)+',{1,6},'+v.quote(loc)+',1);')
        finally:
            cmds.undoInfo(closeChunk=True)
        self.assertEqual('motionPath',cmds.nodeType(motion_path))
        self.assertEqual([1,2,3,4,5],cmds.keyframe(motion_path+'.uValue',query=True,timeChange=True))
        self.assertFalse(cmds.ls(type='nearestPointOnCurve'))
        self.assertFalse(cmds.ls(type='decomposeMatrix'))
        cmds.undo()
        self.assertEqual(before,v.all_uuids())
        cmds.redo()
        self.assertTrue(cmds.ls(type='motionPath'))
        cmds.undoInfo(openChunk=True,chunkName='outerFailedNativePath')
        try:
            cmds.setAttr(obj+'.ty',3)
            with self.assertRaises(RuntimeError):
                runtime.native_call('SW_7b95c992be7b036735f7298f89ab9556('+v.quote(obj)+',"missing_curve",{1,6},'+v.quote(loc)+',1);')
        finally:
            cmds.undoInfo(closeChunk=True)
        cmds.undo()
        self.assertAlmostEqual(0,cmds.getAttr(obj+'.ty'))


if __name__=='__main__':
    unittest.main(verbosity=2)
