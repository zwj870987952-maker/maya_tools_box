import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya.api import OpenMaya as om
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.a=cmds.polyCube(name='first')[0]; self.b=cmds.polyCube(name='second')[0]
        cmds.polyUVSet(self.a,create=True,uvSet='detail'); cmds.polyCopyUV(self.a,uvSetNameInput='map1',uvSetName='detail',constructionHistory=False)
        cmds.polyUVSet(self.a,currentUVSet=True,uvSet='detail'); cmds.polyEditUV(self.a+'.map[*]',uValue=.25,vValue=.5)
        cmds.select(self.a,self.b); cmds.autoKeyframe(state=True)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def data(self,node):
        shape=cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True)[0]; selected=om.MSelectionList(); selected.add(shape); fn=om.MFnMesh(selected.getDagPath(0))
        result={}
        for name in cmds.polyUVSet(shape,query=True,allUVSets=True):
            uv=fn.getUVs(name); assignment=fn.getAssignedUVs(name)
            result[name]=[list(v) for v in (uv[0],uv[1],assignment[0],assignment[1])]
        return result

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),self.data(self.a),self.data(self.b),cmds.polyUVSet(self.a,query=True,currentUVSet=True),cmds.autoKeyframe(query=True,state=True))

    def test_union_multi_mesh_rename_geometry_current_and_single_undo(self):
        before=self.state(); self.assertEqual(['detail','map1'],self.call().data['uv_sets'])
        self.assertEqual(before,self.state()); self.call(action='rename',renames={'map1':'base','detail':'lightmap'},dry_run=True); self.assertEqual(before,self.state())
        self.call(action='rename',renames={'map1':'base','detail':'lightmap'})
        self.assertEqual(before[4]['map1'],self.data(self.a)['base']); self.assertEqual(before[4]['detail'],self.data(self.a)['lightmap']); self.assertEqual(before[5]['map1'],self.data(self.b)['base'])
        self.assertEqual(['lightmap'],cmds.polyUVSet(self.a,query=True,currentUVSet=True)); self.assertEqual(before[1:3],self.state()[1:3]); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        cmds.undo(); self.assertEqual(before,self.state())

    def test_two_phase_swap_current_index_and_undo_with_holes(self):
        cmds.select(self.a); before=self.state(); indices=cmds.polyUVSet(self.a,query=True,allUVSetsIndices=True)
        self.call(action='rename',renames={'map1':'detail','detail':'map1'})
        self.assertEqual(before[4]['map1'],self.data(self.a)['detail']); self.assertEqual(before[4]['detail'],self.data(self.a)['map1'])
        self.assertEqual(indices,cmds.polyUVSet(self.a,query=True,allUVSetsIndices=True)); self.assertEqual(['map1'],cmds.polyUVSet(self.a,query=True,currentUVSet=True))
        cmds.undo(); self.assertEqual(before,self.state())
        cmds.polyUVSet(self.a,create=True,uvSet='unused'); cmds.polyUVSet(self.a,create=True,uvSet='third'); cmds.polyUVSet(self.a,delete=True,uvSet='unused')
        indices=cmds.polyUVSet(self.a,query=True,allUVSetsIndices=True)
        self.call(action='rename',renames={'third':'last'}); self.assertEqual(indices,cmds.polyUVSet(self.a,query=True,allUVSetsIndices=True))

    def test_all_table_conflicts_locked_names_alias_components_and_instances(self):
        before=self.state()
        for mapping in ({'map1':'detail'},{'missing':'new'},{'map1':'same','detail':'same'}): self.assertFalse(TOOL.run(action='rename',renames=mapping).success)
        self.assertEqual(before,self.state())
        shape=cmds.listRelatives(self.b,shapes=True,fullPath=True)[0]; cmds.setAttr(shape+'.uvSet[0].uvSetName',lock=True); before=self.state()
        self.assertFalse(TOOL.run(action='rename',renames={'map1':'base'}).success); self.assertEqual(before,self.state()); cmds.setAttr(shape+'.uvSet[0].uvSetName',lock=False)
        self.assertFalse(TOOL.run(objects=[self.a,'firstShape']).success); self.assertFalse(TOOL.run(objects=[self.a+'.f[0]']).success)
        parent=cmds.createNode('transform',name='otherParent'); cmds.parent('firstShape',parent,add=True,shape=True)
        self.assertFalse(TOOL.run(objects=[self.a]).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
