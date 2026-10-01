import os
import json
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.isolate_selected import tool,view
NATIVE_CHOOSE=view.choose


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.root=cmds.polyCube(name='root')[0]
        self.mid=cmds.createNode('transform',name='middle',parent=self.root)
        self.chosen=cmds.polyCube(name='chosen')[0]; cmds.parent(self.chosen,self.mid)
        self.other=cmds.polyCube(name='other')[0]; cmds.parent(self.other,self.root)
        self.hidden=cmds.polyCube(name='alreadyHidden')[0]; cmds.parent(self.hidden,self.root); cmds.setAttr(self.hidden+'.v',0)
        self.unrelated=cmds.polyCube(name='unrelated')[0]; cmds.setAttr(self.unrelated+'.v',0)
        self.panel={'enabled':True,'members':[self.root+'.f[0]']}
        # Only the native viewport adapter is substituted. All scene operations,
        # UUIDs, receipts, visibility, node ownership and Undo are actual Maya.
        view.choose=lambda panel=None: panel or 'fixturePanel'
        view.state=lambda panel: dict(enabled=self.panel['enabled'],members=list(self.panel['members']))
        def apply(panel,objects): self.panel.update(enabled=True,members=list(objects))
        def restore(panel,snapshot,members): self.panel.update(enabled=snapshot['enabled'],members=list(members))
        view.apply=apply; view.restore=restore
        cmds.select(self.root); cmds.autoKeyframe(state=True)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),{n:cmds.getAttr(n+'.v') for n in (self.root,self.mid,self.chosen,self.other,self.hidden,self.unrelated)},dict(self.panel),cmds.autoKeyframe(query=True,state=True))

    def test_real_visibility_receipt_uuid_restore_and_single_undo(self):
        before=self.state(); self.call(dry_run=True); self.assertEqual(before,self.state())
        r=self.call(); receipt=r.data['receipt']
        self.assertTrue(cmds.getAttr('rootShape.v'))
        self.assertFalse(cmds.getAttr(self.mid+'.v')); self.assertFalse(cmds.getAttr(self.other+'.v'))
        self.assertFalse(cmds.getAttr(self.hidden+'.v')); self.assertFalse(cmds.getAttr(self.unrelated+'.v'))
        self.assertEqual(before[1],cmds.ls(selection=True,long=True)); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        cmds.undo()
        self.assertFalse(cmds.objExists(receipt)); self.assertEqual(before[4],self.state()[4])
        cmds.redo(); self.assertTrue(cmds.objExists(receipt))
        # Rename while isolated: receipt resolves actual UUID, not stale names.
        self.other=cmds.rename(self.other,'renamedOther')
        self.call(action='restore',receipt=receipt)
        self.assertTrue(cmds.getAttr(self.other+'.v')); self.assertTrue(cmds.getAttr(self.mid+'.v'))
        self.assertFalse(cmds.getAttr(self.hidden+'.v')); self.assertFalse(cmds.getAttr(self.unrelated+'.v'))
        self.assertEqual(['|root.f[0]'],self.panel['members']); self.assertTrue(self.panel['enabled'])
        self.assertFalse(cmds.objExists(receipt))
        cmds.undo(); self.assertTrue(cmds.objExists(receipt)); self.assertFalse(cmds.getAttr(self.other+'.v'))
        cmds.redo(); self.assertFalse(cmds.objExists(receipt)); self.assertTrue(cmds.getAttr(self.other+'.v'))

    def test_selected_descendant_path_and_previously_disabled_panel(self):
        self.panel.update(enabled=False,members=[])
        r=self.call(objects=[self.root,self.chosen])
        self.assertTrue(cmds.getAttr(self.mid+'.v')); self.assertTrue(cmds.getAttr(self.chosen+'.v'))
        self.assertFalse(cmds.getAttr(self.other+'.v'))
        self.call(action='restore',receipt=r.data['receipt']); self.assertFalse(self.panel['enabled'])

    def test_all_preflight_refusals_and_corrupt_or_changed_receipt(self):
        before=self.state()
        for p in ({'objects':[self.root+'.f[0]']},{'objects':[self.root,'|root']},{'objects':['missing']}):
            self.assertFalse(TOOL.run(**p).success)
        self.assertEqual(before,self.state())
        cmds.setAttr(self.other+'.v',lock=True); before=self.state()
        self.assertFalse(TOOL.run().success); self.assertEqual(before,self.state())
        cmds.setAttr(self.other+'.v',lock=False)
        r=self.call(); receipt=r.data['receipt']; before=self.state()
        self.assertFalse(TOOL.run().success); self.assertEqual(before,self.state())
        text=cmds.getAttr(receipt+'.'+tool.DATA)
        corrupt=json.loads(text); corrupt['hide'][-1]['before']='true'
        cmds.setAttr(receipt+'.'+tool.DATA,json.dumps(corrupt),type='string'); before=self.state()
        self.assertFalse(TOOL.run(action='restore',receipt=receipt).success); self.assertEqual(before,self.state())
        cmds.setAttr(receipt+'.'+tool.DATA,text,type='string')
        cmds.setAttr(self.other+'.v',1); before=self.state()
        self.assertFalse(TOOL.run(action='restore',receipt=receipt).success); self.assertEqual(before,self.state())
        cmds.setAttr(self.other+'.v',0); cmds.setAttr(self.mid+'.v',lock=True); before=self.state()
        self.assertFalse(TOOL.run(action='restore',receipt=receipt).success); self.assertEqual(before,self.state())
        cmds.setAttr(self.mid+'.v',lock=False); self.call(action='restore',receipt=receipt)
        cmds.parent(self.other,world=True); cmds.parent(self.other,self.root,add=True)
        self.assertFalse(TOOL.run().success)
        with self.assertRaises(RuntimeError): NATIVE_CHOOSE()
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
