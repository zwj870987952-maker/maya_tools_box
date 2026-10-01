import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()


def animated(name):
    node=cmds.createNode('transform',name=name)
    for t,v in ((-1,8),(0,1),(1,4),(2,2),(3,7)):
        cmds.setKeyframe(node,attribute='tx',time=t,value=v)
    cmds.keyTangent(node,attribute='tx',edit=True,inTangentType='linear',outTangentType='linear')
    return node


def curve(node):
    return cmds.listConnections(node+'.tx',source=True,destination=False,type='animCurve')[0]


def data(node):
    c=curve(node)
    return cmds.keyframe(c,query=True,timeChange=True),cmds.keyframe(c,query=True,valueChange=True)


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def test_dense_batch_negative_fractional_once_and_undo_redo(self):
        for mode,offset in (('batch',1),('batch',-1),('once',0.5)):
            nodes=[animated('obj'+str(i)) for i in range(4)]
            before=[data(n) for n in nodes]
            cmds.select(nodes)
            result=TOOL.run(objects=nodes,mode=mode,offset=offset)
            self.assertTrue(result.success,result.message)
            after=[data(n) for n in nodes]
            for i,(a,b) in enumerate(zip(before,after)):
                delta=0 if i==0 else offset*(i if mode=='batch' else 1)
                self.assertEqual([t+delta for t in a[0]],b[0])
                self.assertEqual(a[1],b[1])
            self.assertEqual(nodes,cmds.ls(selection=True))
            cmds.undo()
            self.assertEqual(before,[data(n) for n in nodes])
            cmds.redo()
            self.assertEqual(after,[data(n) for n in nodes])
            cmds.delete(nodes)

    def test_readonly_selection_and_invalid_second_curve_no_partial_write(self):
        nodes=[animated('a'),animated('b'),animated('c')]
        cmds.select(nodes)
        before=[data(n) for n in nodes]
        undo=cmds.undoInfo(query=True,undoName=True)
        frame=cmds.currentTime(query=True)
        result=TOOL.run(dry_run=True,objects=nodes,offset=2)
        self.assertTrue(result.success,result.message)
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))
        self.assertEqual(before,[data(n) for n in nodes])
        self.assertEqual(frame,cmds.currentTime(query=True))
        self.assertEqual(nodes,cmds.ls(selection=True))
        cmds.setAttr(nodes[-1]+'.tx',lock=True)
        result=TOOL.run(objects=nodes,offset=2)
        self.assertFalse(result.success)
        self.assertEqual(before,[data(n) for n in nodes])

    def test_shared_curve_conflict_or_equal_delta_single_move(self):
        first=animated('first')
        second=animated('second')
        third=cmds.createNode('transform',name='third')
        cmds.connectAttr(curve(second)+'.output',third+'.tx')
        before=data(second)
        self.assertFalse(TOOL.run(objects=[first,second,third],mode='batch',offset=1).success)
        self.assertEqual(before,data(second))
        result=TOOL.run(objects=[first,second,third],mode='once',offset=1)
        self.assertTrue(result.success,result.message)
        self.assertEqual(1,len(result.data['curves']))
        self.assertEqual([t+1 for t in before[0]],data(second)[0])
        self.assertEqual(data(second),data(third))

    def test_gui_selection_semantics_without_window(self):
        nodes=[animated('a'),animated('b'),animated('c')]
        result=TOOL.run(objects=nodes,mode='once',offset=2,update_selection=True)
        self.assertTrue(result.success,result.message)
        self.assertEqual(nodes[1:],cmds.ls(selection=True))
        cmds.select(nodes)
        result=TOOL.run(objects=nodes,mode='batch',offset=2,update_selection=True)
        self.assertTrue(result.success,result.message)
        self.assertEqual(nodes[-1:],cmds.ls(selection=True))
        self.assertTrue(cmds.keyframe(curve(nodes[-1]),query=True,selected=True,timeChange=True))


if __name__=='__main__':
    unittest.main(verbosity=2)
