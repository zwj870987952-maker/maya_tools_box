import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.asset_it_v1_2.tool import PKG,BUNDLE


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); self.alive=cmds.polyCube(name='existing')[0]; cmds.select(self.alive); cmds.currentTime(7); cmds.autoKeyframe(state=True)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.undoInfo(query=True,undoName=True))

    def test_inventory_metadata_import_one_model_and_namespace_guards(self):
        before=self.state(); inventory=self.call(dry_run=True).data; self.assertEqual(290,inventory['count']); self.assertEqual(before,self.state())
        relative=inventory['assets'][0]['relative']; self.call(action='metadata',asset=relative); self.assertEqual(before,self.state())
        self.call(action='import_asset',asset=relative,namespace='candidateAsset',scale=2,dry_run=True); self.assertEqual(before,self.state()); self.assertFalse(cmds.namespace(exists='candidateAsset'))
        cmds.namespace(add='userScope'); cmds.namespace(setNamespace='userScope')
        r=self.call(action='import_asset',asset=relative,namespace='candidateAsset',scale=2)
        self.assertTrue(cmds.objExists(r.data['group'])); self.assertEqual([(2.,2.,2.)],cmds.getAttr(r.data['group']+'.scale')); self.assertGreater(len(cmds.ls('candidateAsset:*',type='mesh')),0)
        self.assertEqual(before[1:4],self.state()[1:4]); self.assertFalse(TOOL.run(action='import_asset',asset=relative,namespace='candidateAsset').success)
        self.assertEqual(':userScope',cmds.namespaceInfo(currentNamespace=True,absoluteName=True))
        imported=self.state()[0]; cmds.undo(); self.assertEqual(before[0],self.state()[0]); self.assertEqual(before[1:4],self.state()[1:4]); self.assertTrue(cmds.namespace(exists=':candidateAsset'))
        cmds.redo(); self.assertEqual(imported,self.state()[0]); self.assertTrue(cmds.objExists(r.data['group']),str({'group':r.data['group'],'roots':cmds.ls(assemblies=True,long=True),'namespace':cmds.namespaceInfo(currentNamespace=True,absoluteName=True),'relative':cmds.namespace(query=True,relativeNames=True)})); cmds.undo(); self.assertEqual(before[0],self.state()[0])
        self.assertEqual(':userScope',cmds.namespaceInfo(currentNamespace=True,absoluteName=True)); cmds.namespace(setNamespace=':')
        with tempfile.TemporaryDirectory(prefix='assetit_redo_fixture_') as directory:
            fixture=Path(directory)/'model.ma'; shutil.copyfile(Path(inventory['library'])/relative,fixture)
            r=self.call(action='import_asset',library=directory,asset='model.ma',namespace='redoAsset')
            created=self.state()[0]; cmds.undo(); fixture.rename(fixture.with_suffix('.ma.bak')); cmds.redo(); self.assertEqual(created,self.state()[0]); self.assertTrue(cmds.objExists(r.data['group'])); cmds.undo()
        self.assertFalse(TOOL.run(action='launch_native').success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()

    def test_fresh_private_install_never_overwrites_and_preserves_sources(self):
        before=self.state()
        with tempfile.TemporaryDirectory(prefix='assetit_private_install_') as folder:
            target=Path(folder)/'AssetIt'; self.call(action='install',target_dir=str(target),dry_run=True); self.assertFalse(target.exists()); self.assertEqual(before,self.state())
            result=self.call(action='install',target_dir=str(target)); self.assertFalse(result.data['native_ui_path_matches'])
            for file in (BUNDLE/'AssetIt').rglob('*.py'):
                self.assertEqual(file.read_bytes(),(target/file.relative_to(BUNDLE/'AssetIt')).read_bytes())
            config=json.loads((target/'Preferences/UserLibPath.json').read_text(encoding='utf8')); self.assertEqual(str(target/'AssetIt_LIBRARY'),config['USER_LIB_PATH']); self.assertTrue(Path(config['USER_LIB_PATH']).is_dir())
            self.assertFalse(TOOL.run(action='install',target_dir=str(target)).success); self.assertFalse(TOOL.run(action='launch_native',target_dir=str(target)).success); self.assertEqual(before,self.state())
        self.assertFalse(TOOL.run(action='metadata',asset='../outside.ma').success)


if __name__=='__main__': unittest.main()
