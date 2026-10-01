import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Isolated temporary Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, mel
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.skin_info_and_super_connect import operations as op


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def call(self, **p):
        result = TOOL.run(**p)
        self.assertTrue(result.success, result.message)
        return result

    def skin(self):
        cmds.select(clear=True)
        a = cmds.joint(name='jointA')
        b = cmds.joint(name='jointB', position=(2,0,0))
        mesh = cmds.polyPlane(name='skinMesh', subdivisionsX=1, subdivisionsY=1)[0]
        skin = cmds.skinCluster([a,b], mesh, toSelectedBones=True)[0]
        cmds.skinPercent(skin, mesh+'.vtx[*]', transformValue=[(a,1),(b,0)])
        return mesh, skin, a, b

    def test_complete_native_definitions_compile_without_execution(self):
        before = cmds.ls(long=True)
        for suite in op.catalog()['suites']:
            mel.eval((op.PKG/(suite+'_legacy.mel')).read_text(encoding='utf8'))
            mel.eval((op.PKG/(suite+'_ui.mel')).read_text(encoding='utf8'))
        self.assertEqual(before, cmds.ls(long=True))

    def test_all_formats_roundtrip_exclusive_export_and_timal_bind(self):
        mesh, skin, a, b = self.skin()
        with tempfile.TemporaryDirectory(prefix='skin_suite_') as folder:
            selection = cmds.ls(selection=True, long=True)
            before = cmds.undoInfo(query=True, undoName=True)
            self.call(dry_run=True, action='export', objects=[mesh], directory=folder, formats=['xml','json'])
            self.assertEqual(before, cmds.undoInfo(query=True, undoName=True))
            self.assertEqual([], list(Path(folder).iterdir()))
            self.call(action='export', objects=[mesh], directory=folder, formats=['xml','json'])
            self.assertFalse(TOOL.run(action='export',objects=[mesh],directory=folder).success)
            for fmt in ('xml','json'):
                cmds.skinPercent(skin,mesh+'.vtx[*]',transformValue=[(a,0),(b,1)])
                self.call(action='import', objects=[mesh], directory=folder, formats=[fmt])
                self.assertAlmostEqual(1, cmds.skinPercent(skin,mesh+'.vtx[0]',query=True,transform=a))
                cmds.undo()
                self.assertAlmostEqual(1, cmds.skinPercent(skin,mesh+'.vtx[0]',query=True,transform=b))
                self.call(action='import', objects=[mesh], directory=folder, formats=[fmt])
            self.call(action='export', objects=[mesh], directory=folder, basename='timalMap', convention='timal')
            copy = cmds.polyPlane(name='newUnbound',subdivisionsX=1,subdivisionsY=1)[0]
            selection = cmds.ls(selection=True,long=True)
            self.call(action='import',objects=[copy],directory=folder,basename='timalMap',convention='timal',post_normalize=True)
            self.assertTrue(op.mesh(copy)['skin'])
            self.assertEqual(selection, cmds.ls(selection=True,long=True))

    def test_txt_no_eval_topology_and_joint_weight_locks(self):
        mesh, skin, a, b = self.skin()
        with tempfile.TemporaryDirectory() as folder:
            self.call(action='export',objects=[mesh],directory=folder)
            path = Path(folder)/'skinMesh.txt'
            path.write_text('delete "skinMesh";',encoding='utf8')
            self.assertFalse(TOOL.run(action='import',objects=[mesh],directory=folder).success)
            self.assertTrue(cmds.objExists(mesh))
            path.write_text('select -add "jointA";\n',encoding='utf8')
            wrong = cmds.polyPlane(name='differentTopology', subdivisionsX=2, subdivisionsY=1)[0]
            self.assertFalse(TOOL.run(action='import',objects=[wrong],basename='skinMesh',directory=folder).success)
            self.call(action='lock_weights',objects=[a])
            self.assertTrue(cmds.getAttr(a+'.liw'))
            self.assertFalse(TOOL.run(action='import',objects=[mesh],directory=folder).success)
            cmds.undo()
            self.assertFalse(cmds.getAttr(a+'.liw'))

    def test_transfer_copy_weighted_info_and_undo(self):
        mesh, skin, a, b = self.skin()
        target = cmds.polyPlane(name='targetMesh',subdivisionsX=1,subdivisionsY=1)[0]
        self.call(action='transfer',objects=[mesh,target])
        cluster = op.mesh(target)['skin']
        self.assertAlmostEqual(1,cmds.skinPercent(cluster,target+'.vtx[0]',query=True,transform=a))
        cmds.undo()
        self.assertFalse(op.mesh(target)['skin'])
        self.call(action='transfer',objects=[mesh,target])
        self.call(action='copy',objects=[mesh,target])
        info = self.call(action='info',objects=[mesh])
        self.assertEqual(2,len(info.data['meshes'][0]['influences']))
        self.call(action='select_weighted',objects=[mesh])
        self.assertEqual([a],cmds.ls(selection=True))

    def test_direct_all_axes_prefix_and_constraints_motion_undo(self):
        cmds.namespace(add='src')
        cmds.namespace(add='dst')
        src = cmds.createNode('transform', name='src:S_hand')
        dst = cmds.createNode('transform', name='dst:D_hand')
        p = {'action':'connect','sources':[src],'destinations':[dst],'source_prefix':'S_','destination_prefix':'D_'}
        state = cmds.ls(long=True)
        self.call(dry_run=True, **p)
        self.assertEqual(state,cmds.ls(long=True))
        self.call(**p)
        cmds.setAttr(src+'.tx',5)
        self.assertEqual(5,cmds.getAttr(dst+'.tx'))
        cmds.undo()
        cmds.undo()
        self.assertFalse(cmds.listConnections(dst+'.tx',source=True,destination=False))
        for mode in ('parent','point','orient','point_orient'):
            self.call(**dict(p,mode=mode,channels=['tx','ty','tz','rx','ry','rz'],maintain_offset=False))
            self.assertAlmostEqual(cmds.getAttr(src+'.tx'),cmds.getAttr(dst+'.tx') if mode!='orient' else cmds.getAttr(src+'.tx'))
            cmds.undo()
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
