"""Preserve the complete SkinMagic source/resources; private Python 3 runtime."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'tools_staging_pool/02_rigging_hierarchy/skin_magic'
RAW = UNIT/'SkinMagic'
RC = UNIT/'release_candidate'
PKG = RC/'maya_toolkit/tools/skin_magic'


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n', encoding='utf8', newline='\n')


def convert():
    fixes = get_fixers_from_package('lib2to3.fixes')
    # Keep pm/Qt names, and do not reinterpret module imports as relative imports.
    fixes = [x for x in fixes if x.rsplit('.',1)[1] not in ('fix_import','fix_imports','fix_imports2')]
    original = (RAW/'skinMagic.py').read_text(encoding='utf-8-sig')
    text = str(RefactoringTool(fixes).refactor_string(original+'\n','skinMagic.py'))
    text = text.replace('str(sWrod, "utf8", errors="ignore")','str(sWrod)')
    return ast.parse(text)


def main():
    tree = convert()
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    original_functions = [n.name for n in functions]
    source = ast.unparse(tree)
    # UI callbacks and disposable working geometry must never undo a caller's history.
    source = source.replace('pm.undo()', 'pass')
    source = source.replace("pass #", "pass #")
    # These replacements are made on AST-normalized text and verified below.
    source = source.replace("        pass\n        pass\n        pass\n        applyVertexData(vtxWeights, vertexInfo)", "        pm.delete(newPoly)\n        applyVertexData(vtxWeights, vertexInfo)")
    source = source.replace("        pm.runtime.GoToBindPose()\n        pm.copySkinWeights", "        _before_mirror = bridge.capture_weights(str(source))\n        pm.runtime.GoToBindPose()\n        pm.copySkinWeights")
    source = source.replace("            pass\n            pass\n            applyVertexData(vtxWeights, vertexInfo)", "            bridge.restore_weights(_before_mirror)\n            applyVertexData(vtxWeights, vertexInfo)", 1)
    source = source.replace("            pm.copySkinWeights(sourceSkin=weightPxyMeshSkinCluster", "            _before_transfer = bridge.capture_weights(str(targetSkinCluster))\n            pm.copySkinWeights(sourceSkin=weightPxyMeshSkinCluster")
    source = source.replace("            pass\n            pass\n            applyVertexData(vtxWeights, vertexInfo)", "            bridge.restore_weights(_before_transfer)\n            applyVertexData(vtxWeights, vertexInfo)", 1)
    source = source.replace("mel.eval('hyperShadePanelMenuCommand(\"hyperShadePanel1\", \"deleteUnusedNodes\");')", "pm.warning('Automatic scene-wide unused shader deletion removed; use a scoped cleanup separately')")
    source = source.replace("meshSkinCluster.setWeightDistribution(1)", "pass  # Selection/UI queries must not change skinCluster settings")
    source = source.replace("command='addBoneGetSelectBone()'", "command=lambda *unused: addBoneGetSelectBone()")
    source = source.replace("command='pm.layoutDialog( dismiss = \"Cancel\")'", "command=lambda *unused: pm.layoutDialog(dismiss='Cancel')")
    source = source.replace("        mel.eval('CreateWrap')", "        _wrap_existing = bridge.scene_uuids()\n        mel.eval('CreateWrap')")
    source = source.replace("            if 'BaseShape' in item.name():", "            if 'BaseShape' in item.name() and bridge.node_uuid(item.getParent()) not in _wrap_existing:")
    source = source.replace("            if pm.ls(bsName):\n                pm.delete(pm.ls(bsName))", "            if pm.ls(bsName):\n                raise ValueError('An unrelated object occupies the blendshape target name: '+bsName)")
    source = source.replace("            boneList = pm.listRelatives(key, allDescendents=1)\n            allChildBoneNum", "            boneList = pm.listRelatives(key, allDescendents=1) or []\n            allChildBoneNum")
    source = source.replace("        childBoneList = pm.listRelatives(key, allDescendents=1)\n        childBoneList.append", "        childBoneList = pm.listRelatives(key, allDescendents=1) or []\n        childBoneList.append")
    source = source.replace("            for cbone in pm.listRelatives(key, allDescendents=1):", "            for cbone in pm.listRelatives(key, allDescendents=1) or []:")
    # A label shape is reparented by the original; delete only its own emptied transform.
    source = source.replace("            meshLabel.setParent(weightMesh)", "            _label_parent = meshLabel.getParent()\n            meshLabel.setParent(weightMesh)\n            if _label_parent and not _label_parent.getChildren():\n                pm.delete(_label_parent)")
    source = source.replace("    for obj in pm.ls('annotation*', type='transform'):\n        pm.delete(obj)", "    pass  # No scene-wide annotation cleanup")
    source = source.replace("    if pm.ls('weightMeshMetal'):\n        proxyMeshMetal = pm.ls('weightMeshMetal')[0]\n    else:\n        proxyMeshMetal = pm.shadingNode('lambert', asShader=True, name='weightMeshMetal')", "    proxyMeshMetal = pm.shadingNode('lambert', asShader=True, name='weightMeshMetal')")
    source = source.replace("    if pm.ls('proxyMeshShader'):\n        proxyMeshShader = pm.ls('proxyMeshShader')[0]\n    else:\n        proxyMeshShader = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='proxyMeshShader')", "    proxyMeshShader = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='proxyMeshShader')")
    tree = ast.parse(source)
    replacements = {
        'applyLanguage': "return bridge.switch_language({1:'chn',2:'eng',3:'jpn'}[lanId])",
        'checkUpdate': "return bridge.update_status()",
        'changeVertPriority': "return bridge.selection_priority(isRevert)",
        'closeUI': "return bridge.close_cleanup()",
        'goShelf': "return bridge.add_shelf_button()",
        'removeUnknowNode': "return bridge.remove_selected_unknown()",
        'exportVtxWeight': "return bridge.vertex_export(isOutputFile)",
        'importVtxWeight': "return bridge.vertex_import(isFromFile)",
        'exportVtxWeight2': "return bridge.xml_export(isOutputFile)",
        'importVtxWeight2': "return bridge.xml_import(isFromFile)",
        'lodSave': "return bridge.lod_export()",
        'lodLoad': "return bridge.lod_import()",
        'paintVertexOff': "return bridge.paint_off()",
        'resetUI': "weight_paintVertexCheckBox.setValue(False)\nrunProgressBar(main_progressBar,0)\nlodReset()",
        'getSelectedVertexInfo': "selectedVertexList = getCurrentSelectVertexs()\nif not selectedVertexList:\n    return None\nmesh = pm.PyNode(selectedVertexList[0].split('.')[0])\nif pm.nodeType(mesh) == 'mesh':\n    mesh = mesh.getParent()\nmeshSkinCluster = getMeshSkinCluster(mesh)\nif not meshSkinCluster:\n    return None\nweight_normalizeLabel.setLabel({0:'OFF',1:'ON',2:'POST'}.get(meshSkinCluster.getNormalizeWeights(),'UNKNOWN'))\nreturn selectedVertexList, mesh, meshSkinCluster",
        'dockScriptEditorCmd': "mel.eval('ScriptEditor;')",
    }
    # The supplied 4.0 distribution has no spring tab or spring implementation.
    # Retain their dead callback names, with a precise error instead of a NameError.
    for f in tree.body:
        if isinstance(f,ast.FunctionDef):
            if f.name in replacements:
                f.body = ast.parse(replacements[f.name]).body
            if f.name.startswith('spring') and f.name not in ('springCopyCmd','springPasteCmd','springWebCmd'):
                f.body = ast.parse("raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')").body
    keep = []
    build = []
    assigned = set()
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.Import,ast.ImportFrom)):
            if isinstance(node,ast.Import) and any(a.name=='pickle' for a in node.names):
                continue
            keep.append(node)
            continue
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant):
            continue
        if isinstance(node,ast.Assign):
            try:
                ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
            else:
                keep.append(node)
                if node.lineno>=979:
                    build.append(node)
                continue
            targets = {n.id for target in node.targets for n in ast.walk(target) if isinstance(n,ast.Name)}
            if targets & {'scriptName','scriptPath','skinMagic_MainUIFile'}:
                keep.append(node)
                continue
        # UI lifecycle belongs only to explicit show_ui; jobs are installed by bridge.
        text = ast.unparse(node)
        if 'pm.scriptJob(' in text or 'pm.deleteUI(' in text or text in ('checkUpdate()','changeVertPriority()','selectionChanged()','pm.showWindow(skinMagic_MainUI)'):
            continue
        if 'pm.loadUI(' in text:
            node.value = ast.parse('bridge.load_ui(language)').body[0].value
        build.append(node)
    for node in build:
        assigned.update(n.id for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store))
    keep.insert(0,ast.parse('from .. import ui_support as bridge').body[0])
    extras = ast.parse('''
def weightToolOn():
    return updateWeightUI()
def loopSelection():
    return pm.runtime.SelectEdgeLoopSp()
def testCmd(ignoreInputs=False):
    return bridge.update_status()
def build_ui(language=''):
    pass
''').body
    extras[-1].body = [ast.Global(names=sorted(assigned))]+build+ast.parse('bridge.bind_controls(skinMagic_MainUI, language)\nreturn skinMagic_MainUI').body
    tree.body = keep+extras
    ast.fix_missing_locations(tree)
    put(PKG/'native/skinMagic.py',ast.unparse(tree))
    put(PKG/'native/__init__.py','"""Complete, private upstream engine. Requires PyMel; no auto-run."""')
    rows=[]
    for src in sorted(RAW.rglob('*')):
        if not src.is_file():
            continue
        rel=src.relative_to(RAW)
        archive=PKG/'upstream'/rel
        if src.suffix=='.py':
            archive=archive.with_suffix('.py.original')
        archive.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,archive)
        rows.append({'path':rel.as_posix(),'archive':archive.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
        if src.suffix!='.py':
            dst=PKG/'native'/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
    controls={}
    for f in RAW.glob('*.ui'):
        callbacks=[]
        for w in ET.parse(f).iter('widget'):
            for prop in w.findall('property'):
                if prop.attrib['name'].startswith('+'):
                    callbacks.append({'widget':w.attrib['name'],'class':w.attrib['class'],'flag':prop.attrib['name'][1:],'function':prop.findtext('string')})
        controls[f.name]=callbacks
    put(PKG/'catalog.json',json.dumps({'source_version':'4.0/40000','author':'Yanbin Bai','files':rows,'functions':original_functions,'ui_controls':controls,'license':'No independent license supplied; local preparation only, no publishing authorization inferred','missing_upstream':['Spring callbacks have no implementation or UI tab','Gore engine supplied without UI controls; companion window provided','weightToolOn/loopSelection/testCmd missing; explicit repairs documented']},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','SkinMagic/** -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','skin_magic').replace('RootMotionBakeTool','SkinMagicTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'skin_magic','registration':{'module':'skin_magic','class_name':'SkinMagicTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[r['path'] for r in rows],'dependencies':['Maya cmds/MEL/API2','Compatible PyMel for complete original GUI/engine; absent in installed Maya2025'],'acceptance_required':True,'change_summary':'Complete 250 upstream functions and all 41 source/resources retained with byte archive; lazy private Python3 port, full four-language UI callback binding, supplemental Gore controls, schema/API/batch weights, safe JSON replacing pickle, exclusive exports/private XML, no internal Undo/global shader/annotation cleanup, scoped ownership/dry-run, docs/tests/promotion.','verification_limitations':['Full PyMel business paths and real Maya GUI not_run because PyMel absent','Spring dead callbacks have no algorithm/UI in upstream; retained explicit failure, separate SpringMagic required','Legacy pickle files rejected; export using original in trusted legacy environment before converting to documented JSON','Complex LoD/Gore/reskin/wrap/deformer/bind-pose/paint helpers require backup-scene manual acceptance','Maya deformerWeights underlying writes are not intrinsically undoable; candidate restores/replays weights for existing skin','No independent redistribution license supplied']},ensure_ascii=False,indent=2))
    print(json.dumps({'source_files':len(rows),'functions':len(original_functions),'controls':{k:len(v) for k,v in controls.items()}}))


if __name__ == '__main__':
    main()
