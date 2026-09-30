import importlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Only run through isolated mayapy runner, never a user scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
RC = Path(__file__).resolve().parents[1]
if (RC/'maya_toolkit/framework/base_tool.py').exists():
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.anim_polish_premium_v1_23 import AnimPolishTool
    TOOL = AnimPolishTool()
else:
    spec = importlib.util.spec_from_file_location('polish_loader',RC/'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    TOOL = loader.load_tool()
package = TOOL.__class__.__module__.rsplit('.',1)[0]
contracts = sys.modules[package+'.contracts']
runtime = sys.modules[package+'.runtime']
state = sys.modules[package+'.state']


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def invoke(self,function,arguments):
        result = TOOL.run(action='invoke',function=function,arguments=arguments)
        self.assertTrue(result.success,result.errors)
        result.to_json()
        return result

    def test_01_read_only_dry_run(self):
        mesh = cmds.polyCube(name='dryMesh')[0]
        before = set(sys.modules)
        nodes = cmds.ls()
        result = TOOL.run(action='invoke',function='wrap.wrapToWorld',arguments={'drvn':mesh},dry_run=True)
        self.assertTrue(result.success,result.errors)
        self.assertEqual(nodes,cmds.ls())
        self.assertEqual(before,set(sys.modules))
        self.assertFalse(state.data_directory().exists())

    def test_02_wrap_to_world_and_undo(self):
        mesh = cmds.polyCube(name='wrapMesh')[0]
        before = set(cmds.ls())
        self.invoke('wrap.wrapToWorld',{'drvn':mesh})
        self.assertTrue(cmds.ls(type='blendShape'))
        self.assertTrue(cmds.objExists(mesh+'.fr1_1_wrap'))
        cmds.undo()
        self.assertEqual(before,set(cmds.ls()))
        self.assertFalse(cmds.objExists(mesh+'.fr1_1_wrap'))

    def test_03_grow_shrink_json_list_default(self):
        mesh = cmds.polyCube(name='growMesh')[0]
        before = set(cmds.ls())
        result = self.invoke('growShrink.run',{'geo':mesh})
        self.assertEqual(result.data['outcome']['return_value'],1)
        self.assertTrue(cmds.objExists(mesh+'.growShrink_1'))
        cmds.undo()
        self.assertEqual(before,set(cmds.ls()))

    def test_04_iron_json_list_default(self):
        mesh = cmds.polyPlane(name='ironMesh',subdivisionsX=2,subdivisionsY=2)[0]
        before = set(cmds.ls())
        result = self.invoke('iron.run',{'geo':mesh,'its':1})
        self.assertEqual(result.data['outcome']['return_value'],1)
        self.assertTrue(cmds.objExists(mesh+'.iron_1'))
        cmds.undo()
        self.assertEqual(before,set(cmds.ls()))

    def test_05_sculpt_and_abort(self):
        mesh = cmds.polyCube(name='sculptMesh')[0]
        result = self.invoke('sculptPose.sculpt',{'geo':mesh,'shade':0})
        sculpt = result.data['outcome']['return_value']
        self.assertEqual(cmds.getAttr(sculpt+'.origGeo'),mesh)
        self.assertEqual(cmds.getAttr(mesh+'Shape.visibility'),False)
        cmds.select(sculpt)
        self.invoke('sculptPose.abortSculpt',{})
        self.assertFalse(cmds.objExists(sculpt))
        self.assertEqual(cmds.getAttr(mesh+'Shape.visibility'),True)

    def test_06_json_attribute_clipboard_and_undo(self):
        source = cmds.createNode('transform',name='copySource')
        target = cmds.createNode('transform',name='pasteTarget')
        for node in (source,target):
            cmds.addAttr(node,longName='messageText',dataType='string')
        text = 'quoted "text" and literal source; no Python execution'
        cmds.setAttr(source+'.translateX',4)
        cmds.setAttr(source+'.messageText',text,type='string')
        with tempfile.TemporaryDirectory(prefix='polish_state_') as directory:
            cmds.select(source)
            self.invoke('copyPasteAttrs.copy',{'path':Path(directory).as_posix()})
            self.assertTrue((Path(directory)/'attributes.json').is_file())
            self.assertFalse((Path(directory)/'user_copyPasteAttrs.py').exists())
            cmds.select(target)
            self.invoke('copyPasteAttrs.paste',{'path':Path(directory).as_posix()})
            self.assertEqual(cmds.getAttr(target+'.translateX'),4)
            self.assertEqual(cmds.getAttr(target+'.messageText'),text)
            cmds.undo()
            self.assertEqual(cmds.getAttr(target+'.translateX'),0)
            self.assertEqual(cmds.getAttr(target+'.messageText'),None)

    def test_07_isolated_camera_export_and_collision(self):
        camera = cmds.camera(name='exportCamera')[0]
        with tempfile.TemporaryDirectory(prefix='polish_camera_') as directory:
            args = dict(path=Path(directory).as_posix(),cams=[camera])
            self.invoke('caching.exp_cams',args)
            target = Path(directory)/'cameras.ma'
            self.assertTrue(target.is_file())
            old = target.read_bytes()
            result = TOOL.run(action='invoke',function='caching.exp_cams',arguments=args,dry_run=True)
            self.assertFalse(result.success)
            self.assertIn('overwrite',str(result.errors))
            self.assertEqual(old,target.read_bytes())

    def test_08_quick_bake_error_restores_refresh(self):
        target = cmds.createNode('transform',name='bakeErrorTarget')
        before = cmds.refresh(query=True,suspend=True)
        with patch.object(cmds,'bakeResults',side_effect=RuntimeError('intentional isolated bake failure')):
            result = TOOL.run(action='invoke',function='quickBake.run',arguments={'objs':[target]})
        self.assertFalse(result.success)
        self.assertIn('intentional',str(result.errors))
        self.assertEqual(before,cmds.refresh(query=True,suspend=True))

    def test_09_all_business_modules_import_and_reload(self):
        before = cmds.ls()
        for module in sorted({f['module'] for f in contracts.CATALOG['functions'].values() if f['callable_by_api']}):
            imported = runtime.load(module)
            imported = importlib.reload(imported)
            for fn in contracts.CATALOG['functions'].values():
                if fn['module']==module and fn['callable_by_api']:
                    self.assertEqual(list(inspect.signature(getattr(imported,fn['name'])).parameters),[p['name'] for p in fn['parameters']])
        self.assertEqual(before,cmds.ls())
        self.assertNotIn('animPolish',sys.modules)
        self.assertFalse(state.data_directory().exists())

    def test_10_material_rgb_and_python3_print(self):
        self.invoke('assignColors.createMat',{'name':'demo','color':[0.1,0.2,0.3]})
        self.invoke('assignColors.printColor',{'mat':'jsap_demo_blinn_MAT'})
        color = cmds.getAttr('jsap_demo_blinn_MAT.color')[0]
        for actual,expected in zip(color,[0.1,0.2,0.3]):
            self.assertAlmostEqual(actual,expected,places=5)

    def test_11_settings_json_with_control_stubs(self):
        # Stub UI controls only; this proves JSON fields without claiming a real window test.
        values = {name:('selectionToken' if typ=='radioCollection' else 1) for typ,name,flag in contracts.CATALOG['settings_fields']}
        calls = []
        def control(name,query=False,edit=False,**kwargs):
            if query:
                return values[name]
            calls.append((name,kwargs))
        with tempfile.TemporaryDirectory(prefix='polish_settings_') as directory:
            with patch.object(state,'data_directory',return_value=Path(directory)):
                patches = [patch.object(cmds,typ,side_effect=control) for typ in {r[0] for r in contracts.CATALOG['settings_fields']}]
                for handle in patches:
                    handle.start()
                try:
                    saved = state.save_settings()
                    payload = json.loads((Path(directory)/'settings.json').read_text(encoding='utf-8'))
                    self.assertEqual(saved['saved'],len(contracts.CATALOG['settings_fields']))
                    self.assertFalse((Path(directory)/'user_settings.py').exists())
                    loaded = state.load_settings()
                    self.assertEqual(loaded['loaded'],len(calls))
                    self.assertEqual(len(payload['fields']),len(calls))
                finally:
                    for handle in reversed(patches):
                        handle.stop()

    def test_12_smooth_preview_and_undo(self):
        mesh = cmds.polyCube(name='previewMesh')[0]
        cmds.select(mesh)
        shape = cmds.listRelatives(mesh,shapes=True)[0]
        before = cmds.getAttr(shape+'.displaySmoothMesh')
        self.invoke('smoothPreview.run',{'div':1})
        self.assertEqual(cmds.getAttr(shape+'.displaySmoothMesh'),2)
        self.assertEqual(cmds.getAttr(shape+'.smoothLevel'),1)
        cmds.undo()
        self.assertEqual(cmds.getAttr(shape+'.displaySmoothMesh'),before)

    def test_13_sculpt_apply_modes_with_ui_stubs(self):
        module = runtime.load('sculptPose')
        for function,extras in [('sculptPose.apply',{'mode':'standard'}),('sculptPose.apply_1f',{}),('sculptPose.apply_p2p',{})]:
            with self.subTest(function=function):
                cmds.file(new=True,force=True)
                cmds.currentTime(5)
                mesh = cmds.polyCube(name='applyMesh')[0]
                sculpt = self.invoke('sculptPose.sculpt',{'geo':mesh,'shade':0}).data['outcome']['return_value']
                cmds.move(0,.25,0,sculpt+'.vtx[0]',relative=True)
                expected = cmds.pointPosition(sculpt+'.vtx[0]',world=True)
                before = set(cmds.ls())
                # Only textField lookup and deferred UI ordering are stubbed; Maya cluster/key algorithms are real.
                with patch.object(cmds,'about',return_value=False),patch.object(cmds,'textField',return_value='Sculpt'),patch.object(state,'defer_sort',return_value={'deferred':True}):
                    result = self.invoke(function,dict(scu=sculpt,**extras))
                self.assertFalse(cmds.objExists(sculpt))
                actual = cmds.pointPosition(mesh+'.vtx[0]',world=True)
                for a,b in zip(actual,expected):
                    self.assertAlmostEqual(a,b,places=4)
                if function=='sculptPose.apply_1f':
                    attr = result.data['outcome']['return_value']
                    self.assertEqual(cmds.keyframe(mesh+'.'+attr,query=True,valueChange=True),[0.0,1.0,0.0])
                cmds.undo()
                self.assertEqual(before,set(cmds.ls()))

    def test_14_subdue_new_directory_with_mel_stub(self):
        import maya.mel as mel
        commands = []
        with tempfile.TemporaryDirectory(prefix='polish_subdue_') as directory:
            with patch.object(state,'data_directory',return_value=Path(directory)),patch.object(mel,'eval',side_effect=lambda cmd:commands.append(cmd)):
                state.create_subdue_cache()
                state.create_subdue_cache()
            children = list((Path(directory)/'subdue_cache').iterdir())
            self.assertEqual(len(children),2)
            self.assertNotEqual(children[0],children[1])
            self.assertEqual(len(commands),2)
            self.assertTrue(all('doCreateGeometryCache 6' in c and directory.replace('\\','/') in c for c in commands))

    def test_15_sort_after_chunk_and_uuid_target(self):
        module = runtime.load('sculptPose')
        node = cmds.createNode('transform',name='sortTarget')
        for attr in ('fr2_1_scu','fr1_1_scu'):
            cmds.addAttr(node,longName=attr,attributeType='float',keyable=True)
            cmds.setAttr(node+'.'+attr,.5)
        cmds.select(node)
        queued = []
        with patch.object(cmds,'about',return_value=False),patch.object(cmds,'evalDeferred',side_effect=lambda callback,**kwargs:queued.append(callback)):
            result = self.invoke('sculptPose.sortCB',{})
        self.assertTrue(result.data['outcome']['return_value']['deferred'])
        other = cmds.createNode('transform',name='sortOther')
        cmds.select(other)
        queued.pop()()  # Execute real sort only after BaseMayaTool's chunk has closed.
        self.assertEqual(cmds.ls(selection=True),[other])
        self.assertEqual(cmds.getAttr(node+'.fr1_1_scu'),.5)
        self.assertEqual(cmds.getAttr(node+'.fr2_1_scu'),.5)
        with patch.object(cmds,'evalDeferred',side_effect=lambda callback,**kwargs:queued.append(callback)):
            cmds.select(node)
            state.defer_sort(lambda:self.fail('Deleted UUID must never target a same-name replacement'))
        cmds.delete(node)
        cmds.createNode('transform',name='sortTarget')
        queued.pop()()


if __name__=='__main__':
    unittest.main()
