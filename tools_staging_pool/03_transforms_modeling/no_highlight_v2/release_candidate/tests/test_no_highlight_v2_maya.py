import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.no_highlight_v2 import tool,view
NATIVE_CHOOSE=view.choose


class Checks(unittest.TestCase):
    def setUp(self):
        if tool.SESSION:
            tool.SESSION.remove_callbacks(); tool.SESSION=None
        tool.RECOVERY=None
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.autoKeyframe(state=False)
        cmds.selectMode(object=True); cmds.selectType(facet=False)
        self.a=cmds.polyCube(name='first')[0]; self.b=cmds.polyCube(name='second')[0]
        cmds.setAttr('firstShape.overrideEnabled',1); cmds.setAttr('firstShape.overrideShading',1)
        cmds.setAttr('secondShape.overrideEnabled',0); cmds.setAttr('secondShape.overrideShading',0)
        self.panel={'sel':True,'object':True,'component':False,'facet':False}
        view.choose=lambda panel=None: panel or 'fixturePanel'
        view.state=lambda panel:self.panel['sel']
        view.apply=lambda panel,value:self.panel.update(sel=value)
        view.exists=lambda panel:True
        view.selection_state=lambda:{key:self.panel[key] for key in ('object','component','facet')}
        view.selection_apply=lambda object_mode,facet:self.panel.update(object=object_mode,component=not object_mode,facet=facet)
        cmds.select(self.a)

    def tearDown(self):
        if tool.SESSION:
            tool.SESSION.remove_callbacks(); tool.SESSION=None

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def values(self,n): return tuple(bool(cmds.getAttr(n+'.'+a)) for a in tool.ATTRS)
    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),self.values('firstShape'),self.values('secondShape'),dict(self.panel),cmds.selectMode(query=True,object=True),cmds.selectType(query=True,facet=True))

    def test_start_refresh_same_object_rename_stop_real_override_and_callbacks(self):
        before=self.state(); self.call(action='start',dry_run=True); self.assertEqual(before,self.state()); self.assertIsNone(tool.SESSION)
        self.call(action='start'); session=tool.SESSION
        self.assertEqual(6,len(session.callbacks)); self.assertFalse(self.panel['sel'])
        self.assertTrue(self.panel['component']); self.assertTrue(self.panel['facet'])
        self.assertEqual((True,False),self.values('firstShape'))
        # Dispatch invokes the same real callback method; native modelPanel and
        # GUI event delivery are not claimed as standalone acceptance.
        session.selection_changed(); session.selection_changed()
        self.assertEqual((True,False),self.values('firstShape'))
        cmds.select(self.b); session.selection_changed()
        self.assertEqual(before[4],self.values('firstShape')); self.assertEqual((True,False),self.values('secondShape'))
        renamed=cmds.rename('secondShape','renamedShape')
        self.call(action='stop',dry_run=True); self.assertIs(tool.SESSION,session)
        self.call(action='stop'); self.assertIsNone(tool.SESSION); self.assertEqual([],session.callbacks)
        self.assertEqual(before[4],self.values('firstShape')); self.assertEqual(before[5],self.values(renamed))
        self.assertTrue(self.panel['sel']); self.assertTrue(self.panel['object']); self.assertFalse(self.panel['facet'])
        cmds.undo(); self.assertEqual((True,False),self.values(renamed)); self.assertIsNone(tool.SESSION)
        self.call(action='recover'); self.assertEqual(before[5],self.values(renamed))

    def test_undo_fault_guard_scene_change_cleanup_and_unchanged_bad_start(self):
        cmds.setAttr('firstShape.overrideShading',lock=True); before=self.state()
        self.assertFalse(TOOL.run(action='start').success); self.assertEqual(before,self.state()); self.assertIsNone(tool.SESSION)
        cmds.setAttr('firstShape.overrideShading',lock=False)
        self.call(action='start'); session=tool.SESSION
        cmds.undo(); self.assertTrue(session.faulted)
        before=self.state(); self.assertFalse(TOOL.run(action='refresh').success); self.assertEqual(before,self.state())
        self.call(action='stop'); self.assertEqual([],session.callbacks)
        self.call(action='start'); session=tool.SESSION
        cmds.file(new=True,force=True)
        self.assertIsNone(tool.SESSION); self.assertEqual([],session.callbacks)
        self.assertTrue(self.panel['sel'])
        with self.assertRaises(RuntimeError): NATIVE_CHOOSE()
        with self.assertRaises(RuntimeError): TOOL.show_ui()

    def test_foreign_edits_locked_restore_instance_and_deleted_shapes(self):
        self.call(action='start'); session=tool.SESSION
        cmds.setAttr('firstShape.overrideEnabled',0); before=self.state()
        self.assertFalse(TOOL.run(action='stop').success); self.assertEqual(before,self.state()); self.assertEqual(6,len(session.callbacks))
        cmds.setAttr('firstShape.overrideEnabled',1); cmds.setAttr('firstShape.overrideShading',lock=True); before=self.state()
        self.assertFalse(TOOL.run(action='stop').success); self.assertEqual(before,self.state())
        cmds.setAttr('firstShape.overrideShading',lock=False); self.call(action='stop')
        cmds.parent('firstShape',self.b,add=True,shape=True)
        self.assertFalse(TOOL.run(action='start').success)
        cmds.select(clear=True); self.call(action='start'); self.call(action='stop')


if __name__=='__main__': unittest.main()
