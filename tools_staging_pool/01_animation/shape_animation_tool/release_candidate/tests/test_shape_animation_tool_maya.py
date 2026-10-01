"""Real isolated Maya evaluation, never create or show a Qt window."""
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Use the staging isolated mayapy runner')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.shape_animation_tool import runtime


class Maya(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        self.mesh=cmds.polyPlane(name='sourceMesh',subdivisionsX=1,subdivisionsY=1)[0]
        cmds.delete(self.mesh,constructionHistory=True)
        cmds.currentTime(1)

    def call(self,**kw):
        r=TOOL.run(**kw)
        self.assertTrue(r.success,str(r.message)+' '+str(r.errors))
        return r.data

    def add(self,mesh=None):
        out=self.call(action='add_mesh',mesh=mesh or self.mesh)
        self.sid=out['session']
        self.layer=out['added_layer']
        return out

    def edit(self,**kw):
        return self.call(session=self.sid,layer_id=self.layer,**kw)

    def point(self,mesh=None):
        return cmds.xform((mesh or self.mesh)+'.vtx[0]',query=True,translation=True,objectSpace=True)

    def test_dry_import_and_preflight_have_no_scene_or_undo_changes(self):
        before=set(cmds.ls(uuid=True)); selection=cmds.ls(selection=True,long=True); name=cmds.undoInfo(query=True,undoName=True)
        r=TOOL.run(dry_run=True,action='add_mesh',mesh=self.mesh)
        self.assertTrue(r.success,r.message)
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        self.assertEqual(selection,cmds.ls(selection=True,long=True))
        self.assertEqual(name,cmds.undoInfo(query=True,undoName=True))
        self.assertEqual(1,cmds.currentTime(query=True))
        # Import all retained original UI method definitions, but instantiate none.
        import maya_toolkit.tools.shape_animation_tool.native
        self.assertEqual(before,set(cmds.ls(uuid=True)))

    def test_full_sculpt_pair_geometry_keys_step_and_undo(self):
        original=self.point()
        self.add()
        self.edit(action='set_key',frame=1)
        start=self.edit(action='begin_sculpt',frame=10)
        helper=runtime.resolve(start['editing']['sculpt'])
        cmds.move(0,2,0,helper+'.vtx[0]',relative=True,objectSpace=True)
        self.edit(action='end_sculpt')
        self.assertAlmostEqual(original[1]+2,self.point()[1],places=5)
        self.assertEqual([],cmds.ls('mtkSATTemp_*',type='transform'))
        cmds.currentTime(1)
        self.assertAlmostEqual(original[1],self.point()[1],places=5)
        self.edit(action='step_key',direction='next')
        self.assertEqual(10,cmds.currentTime(query=True))
        self.assertAlmostEqual(original[1]+2,self.point()[1],places=5)
        row=runtime.Engine(self.sid).layer(self.layer)
        self.assertEqual(2,len(row['pairs']))
        self.assertTrue(all(cmds.getAttr(runtime.resolve(p['mult'])+'.input2')==-1 for p in row['pairs']))
        before=self.point()
        self.edit(action='set_enabled',enabled=False)
        self.assertAlmostEqual(original[1],self.point()[1],places=5)
        cmds.undo()
        self.assertAlmostEqual(before[1],self.point()[1],places=5)
        cmds.redo()
        self.assertAlmostEqual(original[1],self.point()[1],places=5)

    def test_reset_delete_key_all_keys_and_remove_preserve_foreign_nodes(self):
        foreign=cmds.createNode('multDoubleLinear',name='shape_1_mult')
        cmds.setAttr(foreign+'.input1',77)
        self.add()
        self.edit(action='set_key',frame=1)
        state=self.edit(action='begin_sculpt',frame=5)
        helper=runtime.resolve(state['editing']['sculpt'])
        base=self.point(helper)
        cmds.move(0,3,0,helper+'.vtx[0]',relative=True,objectSpace=True)
        self.edit(action='reset_shape')
        self.assertAlmostEqual(base[1],self.point(helper)[1],places=5)
        self.edit(action='end_sculpt')
        self.edit(action='delete_key',frame=5)
        self.assertEqual([1], [p['frame'] for p in runtime.Engine(self.sid).layer(self.layer)['pairs']])
        self.edit(action='delete_all_keys')
        self.assertEqual([],runtime.Engine(self.sid).layer(self.layer)['pairs'])
        self.edit(action='set_key',frame=7)
        self.edit(action='remove_mesh')
        self.assertEqual([],runtime.Engine(self.sid).data['layers'])
        self.assertTrue(cmds.objExists(self.mesh))
        self.assertEqual(77,cmds.getAttr(foreign+'.input1'))
        self.assertEqual([],cmds.ls('mtkSATNegative_*'))

    def test_uuid_rename_pending_sculpt_reconstruction_and_shared_driver_guard(self):
        self.add()
        state=self.edit(action='begin_sculpt',frame=1)
        helper=runtime.resolve(state['editing']['sculpt'])
        cmds.rename(helper,'renamedSculpt')
        self.mesh=cmds.rename(self.mesh,'renamedMesh')
        self.assertFalse(TOOL.run(action='set_key',session=self.sid,layer_id=self.layer).success)
        self.edit(action='end_sculpt')
        row=runtime.Engine(self.sid).layer(self.layer)
        mult=runtime.resolve(row['pairs'][0]['mult'])
        other=cmds.createNode('addDoubleLinear')
        cmds.connectAttr(mult+'.output',other+'.input1')
        before=set(cmds.ls(uuid=True))
        r=TOOL.run(action='remove_mesh',session=self.sid,layer_id=self.layer)
        self.assertFalse(r.success)
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        cmds.disconnectAttr(mult+'.output',other+'.input1')
        self.edit(action='remove_mesh')

    def test_key_failure_restores_envelope_time_selection_and_helpers(self):
        self.add()
        self.edit(action='set_key',frame=1)
        bs=runtime.resolve(runtime.Engine(self.sid).layer(self.layer)['bs'])
        old=list(cmds.ls(selection=True,long=True) or []); oldtime=cmds.currentTime(query=True)
        original=runtime.Engine.clone
        calls=[]
        def fail_second(engine,mesh):
            calls.append(mesh)
            if len(calls)==2:
                raise RuntimeError('injected baseline clone failure')
            return original(engine,mesh)
        with patch.object(runtime.Engine,'clone',fail_second):
            result=TOOL.run(action='set_key',frame=8,session=self.sid,layer_id=self.layer)
        self.assertFalse(result.success)
        self.assertEqual(1,cmds.getAttr(bs+'.envelope'))
        self.assertEqual(oldtime,cmds.currentTime(query=True))
        self.assertEqual(old,cmds.ls(selection=True,long=True) or [])
        self.assertEqual([],cmds.ls('mtkSATTemp_*',type='transform'))

    def test_legacy_inspect_adopt_reuses_full_owned_pair_graph(self):
        import pickle
        self.add()
        self.edit(action='set_key',frame=1)
        engine=runtime.Engine(self.sid); row=engine.layer(self.layer)
        bs=runtime.resolve(row['bs'])
        for node in [bs]+[runtime.resolve(p[k]) for p in row['pairs'] for k in ('curve','mult')]:
            for attr in (runtime.OWNER,runtime.ROLE):
                cmds.setAttr(node+'.'+attr,lock=False)
                cmds.deleteAttr(node+'.'+attr)
        cmds.rename(bs,'sourceMesh_LR1_satBS')
        cmds.delete(engine.node)
        old=cmds.createNode('network',name='sat')
        for attr,value in (('meshes',['sourceMesh_LR1']),('sculptMode',False)):
            cmds.addAttr(old,longName=attr,dataType='string')
            cmds.setAttr(old+'.'+attr,str(pickle.dumps(value,protocol=2)),type='string')
        before=set(cmds.ls(uuid=True)); metadata=cmds.getAttr(old+'.meshes')
        self.call(action='inspect_legacy')
        self.assertEqual(before,set(cmds.ls(uuid=True)))
        adopted=self.call(action='adopt_legacy',accept_legacy_ownership=True)
        self.sid=adopted['session']; self.layer=adopted['layers'][0]['id']
        self.edit(action='set_key',frame=4)
        self.assertEqual(metadata,cmds.getAttr(old+'.meshes'))
        self.edit(action='remove_mesh')
        self.assertTrue(cmds.objExists('sat'))

    def test_parented_transformed_mesh_sculpt_and_coherent_curve_retime(self):
        parent=cmds.group(empty=True,name='rigParent')
        cmds.parent(self.mesh,parent)
        cmds.setAttr(parent+'.tx',8)
        cmds.setAttr(parent+'.rotateY',30)
        cmds.setAttr(self.mesh+'.scale',2,2,2)
        cmds.setAttr(self.mesh+'.tz',3)
        before=self.point()
        self.add()
        self.edit(action='set_key',frame=1)
        state=self.edit(action='begin_sculpt',frame=6)
        helper=runtime.resolve(state['editing']['sculpt'])
        # Move the helper in its object coordinates; the finished mesh's local
        # correction must be one unit regardless of parent/world transforms.
        cmds.move(0,1,0,helper+'.vtx[0]',relative=True,objectSpace=True)
        self.edit(action='end_sculpt')
        self.assertAlmostEqual(before[1]+1,self.point()[1],places=5)
        rows=runtime.Engine(self.sid).layer(self.layer)['pairs']
        curves=[runtime.resolve(p['curve']) for p in rows]
        cmds.scaleKey(curves,time=(1,6),timeScale=2,timePivot=1)
        self.edit(action='step_key',direction='next')
        self.assertEqual(11,cmds.currentTime(query=True))
        self.assertAlmostEqual(before[1]+1,self.point()[1],places=5)

    def test_save_reopen_pending_sculpt_and_independent_layers(self):
        import tempfile
        self.add()
        first=self.layer
        self.edit(action='set_key',frame=1)
        second=self.call(action='add_mesh',session=self.sid,mesh=self.mesh)
        self.layer=second['added_layer']
        self.assertNotEqual(first,self.layer)
        state=self.edit(action='begin_sculpt',frame=1)
        helper=runtime.resolve(state['editing']['sculpt'])
        cmds.move(0,2,0,helper+'.vtx[0]',relative=True,objectSpace=True)
        with tempfile.TemporaryDirectory(prefix='mtk_sat_acceptance_') as folder:
            saved=Path(folder)/'pending.ma'
            cmds.file(rename=str(saved))
            cmds.file(save=True,type='mayaAscii',force=True)
            cmds.file(new=True,force=True)
            cmds.file(str(saved),open=True,force=True)
            self.assertTrue(runtime.Engine(self.sid).data['editing'])
            self.edit(action='end_sculpt')
            self.assertAlmostEqual(2,self.point()[1],places=5)
            self.edit(action='remove_mesh')
            self.assertEqual([first],[r['id'] for r in runtime.Engine(self.sid).data['layers']])
            self.assertAlmostEqual(0,self.point()[1],places=5)


if __name__=='__main__':
    unittest.main(verbosity=2)
