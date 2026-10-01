import ast
import os
from pathlib import Path
import runpy
import types
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated temporary Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
PKG=RC/'maya_toolkit/tools/stagger_gui'


def animated(name,constant=False):
    obj=cmds.createNode('transform',name=name)
    for t,value in ((-5,-2),(0,0),(2,8),(6,1),(9,7),(10,6),(15,-1)):
        cmds.setKeyframe(obj,attribute='tx',time=t,value=3 if constant else value)
    cmds.keyTangent(obj,attribute='tx',edit=True,inTangentType='linear',outTangentType='linear')
    return obj


def curve(obj):
    return cmds.listConnections(obj+'.tx',source=True,destination=False,type='animCurve')[0]


def data(obj):
    c=curve(obj)
    return cmds.keyframe(c,query=True,timeChange=True),cmds.keyframe(c,query=True,valueChange=True)


def original_reference(obj,start,end,amount):
    """Run the complete upstream function with only GUI reads fixed.

    All animation commands are actual Maya calls. This harness does not serve
    as the candidate runtime and never instantiates an interactive widget.
    """
    function=next(n for n in ast.parse((PKG/'upstream/ui.py.original').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='stagger_it')
    class SourceCommands:
        def __getattr__(self,name):
            return getattr(cmds,name)
        def intField(self,name,**kwargs):
            return start if name=='sf' else end
        def floatSlider(self,*args,**kwargs):
            return amount
        def window(self,*args,**kwargs):
            return 110
        def progressBar(self,*args,**kwargs):
            return None
    ns={'cmds':SourceCommands(),'Opm':types.SimpleNamespace(MGlobal=types.SimpleNamespace(displayInfo=lambda x:None,displayWarning=lambda x:None))}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'original_stagger_reference','exec'),ns)
    cmds.selectKey(clear=True)
    cmds.select(obj)
    ns['stagger_it']()


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def test_even_odd_and_minimum_range_match_complete_original(self):
        for start,end,amount in ((0,10,3.1),(0,9,2.2),(-3,0,4.0)):
            reference=animated('reference')
            candidate=animated('candidate')
            original_reference(reference,start,end,amount)
            expected=data(reference)
            result=TOOL.run(objects=[candidate],start=start,end=end,amount=amount)
            self.assertTrue(result.success,result.message)
            actual=data(candidate)
            self.assertEqual(expected[0],actual[0])
            for a,b in zip(expected[1],actual[1]):
                self.assertAlmostEqual(a,b,places=6)
            cmds.delete(reference,candidate)

    def test_dry_run_selection_scope_and_undo_redo(self):
        a=animated('a')
        unrelated=animated('unrelated')
        cmds.select(unrelated)
        cmds.selectKey(unrelated,time=(2,2),replace=True)
        before=data(a)
        other=data(unrelated)
        undo=cmds.undoInfo(query=True,undoName=True)
        frame=cmds.currentTime(query=True)
        nodes=cmds.ls(long=True)
        result=TOOL.run(dry_run=True,objects=[a],start=0,end=10)
        self.assertTrue(result.success,result.message)
        self.assertEqual(undo,cmds.undoInfo(query=True,undoName=True))
        self.assertEqual(nodes,cmds.ls(long=True))
        self.assertEqual(before,data(a))
        self.assertEqual(frame,cmds.currentTime(query=True))
        result=TOOL.run(objects=[a],start=0,end=10)
        self.assertTrue(result.success,result.message)
        after=data(a)
        self.assertEqual(other,data(unrelated))
        self.assertEqual([unrelated],cmds.ls(selection=True))
        self.assertEqual(frame,cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual(before,data(a))
        cmds.redo()
        self.assertEqual(after,data(a))

    def test_constant_boundary_and_shared_curve_rejection(self):
        obj=animated('flat',True)
        result=TOOL.run(objects=[obj],start=1,end=8)
        self.assertTrue(result.success,result.message)
        self.assertEqual([],result.data['results'][0]['samples'])
        self.assertIn(1,data(obj)[0])
        self.assertIn(8,data(obj)[0])
        other=cmds.createNode('transform',name='shared_target')
        cmds.connectAttr(curve(obj)+'.output',other+'.tx')
        before=data(obj)
        self.assertFalse(TOOL.run(dry_run=True,objects=[obj],start=0,end=10).success)
        self.assertEqual(before,data(obj))
        cmds.setAttr(other+'.tx',lock=True)
        self.assertFalse(TOOL.run(dry_run=True,objects=[obj,other],start=0,end=10).success)


if __name__=='__main__':
    unittest.main(verbosity=2)
