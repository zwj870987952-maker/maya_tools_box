import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Use disposable Maya runner')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.root_motion_bake import runtime


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        cmds.playbackOptions(minTime=1,maxTime=4,animationStartTime=-2,animationEndTime=8)

    def call(self,**kwargs):
        r=TOOL.run(**kwargs)
        self.assertTrue(r.success,str(r.errors))
        return r.data

    def scene(self,ring=False,dependent=False):
        root=cmds.createNode('transform',name='root')
        center=cmds.createNode('transform',name='RootX_M',parent=root if dependent else None)
        for t,v in ((1,2),(4,8)):
            cmds.setKeyframe(center+'.tz',time=t,value=v,inTangentType='linear',outTangentType='linear')
        g={'root':root,'center':center}
        if ring:
            main=cmds.createNode('transform',name='main')
            for t,v in ((1,0),(4,3)):
                cmds.setKeyframe(main+'.tx',time=t,value=v,inTangentType='linear',outTangentType='linear')
            g['ring']=main
        return g

    def test_full_bake_no_ring_and_undo_cleanup(self):
        g=self.scene()
        cmds.currentTime(3)
        cmds.select(g['center'])
        cmds.autoKeyframe(state=True)
        before=(set(cmds.ls()),cmds.ls(sl=True,long=True),cmds.currentTime(q=True),cmds.undoInfo(q=True,undoName=True))
        args=dict(action='bake',groups=[g],maintain_offset=False)
        self.assertTrue(TOOL.run(dry_run=True,**args).success)
        self.assertEqual(before,(set(cmds.ls()),cmds.ls(sl=True,long=True),cmds.currentTime(q=True),cmds.undoInfo(q=True,undoName=True)))
        data=self.call(**args)
        self.assertEqual([],data['layers'])
        self.assertAlmostEqual(8,cmds.getAttr(g['root']+'.tz',time=4),places=5)
        self.assertFalse(cmds.ls('mtkRootMotion_center_*'))
        self.assertFalse(cmds.ls(type='pointConstraint'))
        self.assertTrue(cmds.autoKeyframe(q=True,state=True))
        self.assertEqual(3,cmds.currentTime(q=True))
        cmds.undo()
        self.assertEqual(set(before[0]),set(cmds.ls()))
        self.assertEqual(0,cmds.getAttr(g['root']+'.tz',time=4))

    def test_full_ring_layer_unique_preserves_existing_layer(self):
        g=self.scene(ring=True)
        existing=cmds.animLayer('root_offsetLayer')
        cmds.animLayer(existing,e=True,selected=True,preferred=True)
        data=self.call(action='bake',groups=[g],maintain_offset=False)
        self.assertEqual(1,len(data['layers']))
        self.assertNotEqual(existing,data['layers'][0])
        self.assertTrue(cmds.objExists(existing))
        self.assertTrue(cmds.animLayer(existing,q=True,selected=True))
        self.assertTrue(cmds.animLayer(existing,q=True,preferred=True))
        self.assertAlmostEqual(3,cmds.getAttr(g['root']+'.tx',time=4),places=5)
        self.assertAlmostEqual(2,cmds.getAttr(g['root']+'.tz',time=4),places=5)
        cmds.undo()
        self.assertTrue(cmds.objExists(existing))
        self.assertFalse(cmds.objExists(data['layers'][0]))

    def test_original_rotation_constraints_and_animated_root_redo(self):
        g=self.scene()
        for t,v in ((1,0),(4,30)):
            cmds.setKeyframe(g['center']+'.rz',time=t,value=v,inTangentType='linear',outTangentType='linear')
            cmds.setKeyframe(g['root']+'.tz',time=t,value=1,inTangentType='linear',outTangentType='linear')
        old=cmds.keyframe(g['root']+'.tz',q=True,valueChange=True)
        self.call(action='bake',groups=[g],maintain_offset=False,rotate_axes=['z'])
        self.assertAlmostEqual(8,cmds.getAttr(g['root']+'.tz',time=4),places=5)
        self.assertAlmostEqual(30,cmds.getAttr(g['root']+'.rz',time=4),places=4)
        cmds.undo()
        self.assertEqual(old,cmds.keyframe(g['root']+'.tz',q=True,valueChange=True))
        cmds.redo()
        self.assertAlmostEqual(30,cmds.getAttr(g['root']+'.rz',time=4),places=4)

    def test_dependent_center_snapshot_and_strict_batch_preflight(self):
        g=self.scene(dependent=True)
        self.assertFalse(TOOL.run(action='bake',groups=[g],snapshot_center=False).success)
        data=self.call(action='bake',groups=[g],maintain_offset=False)
        self.assertAlmostEqual(8,cmds.getAttr(g['root']+'.tz',time=4),places=5)
        self.assertFalse(cmds.ls(type='pointConstraint'))
        cmds.undo()
        bad=cmds.createNode('transform',name='badRoot')
        cmds.setAttr(bad+'.tz',lock=True)
        before=set(cmds.ls())
        self.assertFalse(TOOL.run(action='bake',groups=[g,{'root':bad,'center':g['center']}]).success)
        self.assertEqual(before,set(cmds.ls()))

    def test_failure_finally_and_unowned_deletion(self):
        g=self.scene()
        cmds.currentTime(2)
        foreign=cmds.createNode('transform',name='foreign')
        original=cmds.bakeResults
        with patch.object(cmds,'bakeResults',side_effect=RuntimeError('injected failure')):
            r=TOOL.run(action='bake',groups=[g])
            self.assertFalse(r.success)
        self.assertFalse(cmds.ls(type='pointConstraint'))
        self.assertFalse(cmds.ls('mtkRootMotion_center_*'))
        self.assertEqual(2,cmds.currentTime(q=True))
        self.assertIsNone(runtime._session)
        self.assertTrue(cmds.objExists(foreign))
        with self.assertRaises(RuntimeError):
            runtime.native_cmds.delete(foreign)
        cmds.undo()
        self.assertTrue(cmds.objExists(foreign))

    def test_discovery_namespace_ambiguity_ranges_and_no_ui(self):
        cmds.namespace(add='a')
        cmds.namespace(add='a:b')
        g=self.scene()
        for k,n in g.items():
            g[k]=cmds.rename(n,'a:b:'+n)
        found=self.call(action='discover')
        self.assertEqual(1,len(found['groups']))
        self.assertEqual('a:b:root',found['groups'][0]['root'].split('|')[-1])
        cmds.createNode('transform',name='a:b:root_extra')
        self.assertTrue(self.call(action='discover')['ambiguous'])
        self.assertFalse(TOOL.run(action='bake').success)
        self.assertFalse(TOOL.run(action='bake',groups=[g],time_range='selected').success)
        self.assertEqual([-2,8],TOOL.validate(action='bake',groups=[g],time_range='animation').data['range'])
        self.assertFalse(TOOL.run(action='open_ui').success)


if __name__=='__main__':
    unittest.main(verbosity=2)
