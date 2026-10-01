"""Owned complete original UI; callable callbacks, data bridges and cleanup."""
from contextlib import contextmanager
import functools
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from . import fileio, runtime

_window=None
_gore=None
_busy=False
_priorities={}
_proxy_uuid=None
_display={}
_temporary_xml=None
_jobs=[]
_language=''
_controls={}


def engine():
    runtime.require_pymel()
    from .native import skinMagic
    return skinMagic


def ui_text(language=''):
    if language not in ('','chn','eng','jpn'):
        raise ValueError('Invalid language')
    root_path=Path(__file__).with_name('native')
    root=ET.parse(root_path/('skinMagic'+('_'+language if language else '')+'.ui')).getroot()
    root.find('widget').set('name','skinMagicCandidate')
    for parent in root.iter():
        for prop in list(parent.findall('property')):
            if prop.attrib.get('name','').startswith('+'):
                parent.remove(prop)  # Bind actual Python callables after loadUI.
    for element in root.iter():
        for attr in ('text','tail'):
            value=getattr(element,attr)
            if value and ('icons/' in value.replace('\\','/') or element.tag in ('normaloff','normalon')):
                relative=value.strip().replace('\\','/').rsplit('icons/',1)[-1]
                path=root_path/'icons'/relative
                if not path.is_file():
                    raise FileNotFoundError(path)
                setattr(element,attr,path.as_posix())
    return ET.tostring(root,encoding='unicode')


def load_ui(language=''):
    import pymel.core as pm
    global _window,_language
    name=pm.loadUI(uiString=ui_text(language))
    _window=str(name)
    _language=language
    return str(name)


def bind_controls(window,language):
    import pymel.core as pm
    global _controls
    from .tool import CATALOG
    root=ET.fromstring(ui_text(language))
    paths={}
    def walk(w,path):
        paths[w.attrib['name']]=path
        for child in w.findall('widget'):
            walk(child,path+'|'+child.attrib['name'])
    walk(root.find('widget'),str(window))
    commands={'QPushButton':pm.button,'QCheckBox':pm.checkBox,'QRadioButton':pm.radioButton,'QLineEdit':pm.textField,'QListWidget':pm.textScrollList,'QSlider':pm.intSlider}
    _controls=paths
    for row in CATALOG['ui_controls']['skinMagic'+('_'+language if language else '')+'.ui']:
        if row['class'] not in commands or row['widget'] not in paths:
            raise ValueError('Unsupported/missing original callback control: '+str(row))
        callback_fn=functools.partial(callback,row['function'])
        commands[row['class']](paths[row['widget']],edit=True,**{row['flag']:callback_fn})
    # The source checkbox requests global shader cleanup. Keep its visible
    # meaning honest while retaining the surrounding complete LoD algorithm.
    e=engine()
    e.lodDeleteShader_CheckBox.setValue(False)
    e.lodDeleteShader_CheckBox.setEnable(False)
    pm.checkBox(str(e.lodDeleteShader_CheckBox),edit=True,annotation='Scene-wide unused shader deletion removed to protect unrelated assets')
    e.miscUpdate_button.setVisible(False)


def show_ui(language=''):
    global _busy
    runtime.require_pymel()
    cmds=runtime.cmds_module()
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required; never construct Qt in standalone')
    close_ui()
    _busy=True
    try:
        e=engine()
        name=e.build_ui(language)
        selection_priority(False)
        _jobs.append(cmds.scriptJob(uiDeleted=[name,close_cleanup],runOnce=True))
        _jobs.append(cmds.scriptJob(event=['SelectionChanged',selection_changed],parent=name))
        _jobs.append(cmds.scriptJob(event=['SceneOpened',scene_opened],parent=name))
        cmds.showWindow(name)
        update_status()
        return str(name)
    except Exception:
        close_ui()
        raise
    finally:
        _busy=False


def selection_changed(*unused):
    if _busy or not _window:
        return
    e=engine()
    try:
        # Weight UI queries no longer set skinCluster.weightDistribution.
        # Avoid the original event-driven scene paint/delete path.
        if not e.weight_paintVertexCheckBox.getValue():
            e.selectionChanged()
    except Exception as exc:
        runtime.cmds_module().warning('SkinMagic selection update: '+str(exc))


def scene_opened(*unused):
    global _proxy_uuid,_display
    _proxy_uuid=None
    _display={}
    engine().resetUI()


def update_status():
    e=engine()
    if _window:
        e.printTextLable(e.main_processLable,'SkinMagic 4.0 candidate — real Maya acceptance pending')
    return {'source_version':'4.0','auto_update':False}


def selection_priority(revert=False):
    cmds=runtime.cmds_module()
    if revert:
        for flag,value in _priorities.items():
            cmds.selectPriority(**{flag:value})
        _priorities.clear()
    else:
        if not _priorities:
            for flag in ('polymeshVertex','joint','polymesh'):
                _priorities[flag]=cmds.selectPriority(query=True,**{flag:True})
        cmds.selectPriority(polymeshVertex=10,polymesh=1,joint=9)


def close_cleanup(*unused):
    global _window,_gore,_proxy_uuid,_display
    cmds=runtime.cmds_module()
    for job in list(_jobs):
        if cmds.scriptJob(exists=job):
            cmds.scriptJob(kill=job,force=True)
    _jobs.clear()
    selection_priority(True)
    # Deletion of helpers/display restore is undoable, never a wildcard match.
    if _proxy_uuid or _display:
        from maya_toolkit.core.context import UndoChunkContext
        with UndoChunkContext(chunk_name='SkinMagic owned UI cleanup'):
            paint_off()
    _window=None
    if _gore and cmds.window(_gore,exists=True):
        cmds.deleteUI(_gore)
    _gore=None


def close_ui():
    cmds=runtime.cmds_module()
    if _window and cmds.window(_window,exists=True):
        cmds.deleteUI(_window)
    close_cleanup()


def switch_language(language):
    return show_ui(language)


def preflight(p):
    cmds=runtime.cmds_module()
    action=p['action']
    if action!='ui_command':
        return {'action':action,'interactive':True,'language':p.get('language',''),'ui':_window,'impacts':'Owned UI lifecycle; close restores exact selection priorities and deletes only owned proxy'}
    if not _window or not cmds.window(_window,exists=True):
        raise RuntimeError('Open this candidate UI before calling its original business commands')
    e=engine()
    command=p['command']
    objects=runtime.resolve(p.get('objects'))
    scope=set(n.split('.',1)[0] for n in objects)
    if command=='renameMakeCmd':
        if e.renameAll_radioButton.getSelect():
            if not p.get('allow_scene_scope',False):
                raise ValueError('All-scene rename requires allow_scene_scope=True after inspecting the dry-run scope')
            scope.update(cmds.ls(type='transform',long=True) or [])
        elif e.renameHierarchy_radioButton.getSelect():
            for obj in list(scope):
                scope.update(cmds.listRelatives(obj,allDescendents=True,fullPath=True,type='transform') or [])
    # Include cached original engine inputs (LoD source/target/receivers, Gore,
    # reskin bones, blendshape controls, proxy and vertex skin).
    for name in ('lodSourceMesh','lodTargetMesh','goreSourceMesh'):
        value=getattr(e,name,None)
        if value and cmds.objExists(str(value)):
            scope.add(str(value))
    for name in ('reSkinBone','goreTargetMeshList'):
        scope.update(str(x) for x in getattr(e,name,[]) if cmds.objExists(str(x)))
    scope.update(str(x) for pair in e.lodBoneDict.items() for x in pair if cmds.objExists(str(x)))
    for field in ('bsTransSrcMesh_lineEdit','bsTransTgtMesh_lineEdit'):
        name=getattr(e,field).getText()
        if name and cmds.objExists(name):
            scope.add(name)
    if command not in ('languageCmd','languageSelectedCmd','goShelfCmd','bilibiliCmd','youtubeCmd','donatePayPal_buttonCmd','linkinCmd','updatePageCmd','deformerWebCmd','renameUpdatePreview','renameUpdatePreviewCmd','renameStartChangeCmd','testCmd'):
        if not scope and command not in ('paintVertexOffCmd',):
            raise ValueError('Select explicit targets or load original UI inputs first')
        runtime.writable(list(scope))
    expanded=set(scope)
    for node in scope:
        expanded.update(cmds.listHistory(node) or [])
    skins=cmds.ls(list(expanded),type='skinCluster') or []
    for skin in skins:
        expanded.update(cmds.skinCluster(skin,query=True,influence=True) or [])
    if command=='lodMakeButtonCmd':
        for bone in e.lodBoneDict:
            expanded.update(cmds.listRelatives(str(bone),allDescendents=True,fullPath=True) or [])
            if e.lodDeleteBone_CheckBox.getValue():
                for connected in cmds.listConnections(str(bone),type='skinCluster') or []:
                    expanded.add(connected)
                    expanded.update(cmds.skinCluster(connected,query=True,geometry=True) or [])
    if command in ('reSkinCmd','mirrorWeightCmd','buildWeightMapCmd','paintVertexOnCmd','bindSkinPlusButtonCmd'):
        # Original bind-pose/bind-plus paths can traverse connected joint trees.
        for node in list(expanded):
            if cmds.nodeType(node)=='joint':
                parents=cmds.listRelatives(node,allParents=True,fullPath=True) or []
                expanded.update(parents)
                expanded.update(cmds.listRelatives(node,allDescendents=True,fullPath=True) or [])
    if command=='paintVertexOnCmd' and e.vertexInfo:
        proxy=str(e.vertexInfo[1])+'_colorProxy'
        existing=cmds.ls(proxy,long=True) or []
        if existing and (not _proxy_uuid or cmds.ls(existing[0],uuid=True)[0]!=_proxy_uuid):
            raise ValueError('An unrelated color proxy occupies the original output name')
    if command=='buildWeightMapCmd' and objects:
        mesh=objects[0].split('.',1)[0]
        leaf=mesh.rsplit('|',1)[-1]
        outputs=[leaf+'_colorProxy',leaf+'_WeightMap']
        for skin in skins:
            outputs.extend(leaf+'_'+j.rsplit('|',1)[-1]+'_WeightMap' for j in cmds.skinCluster(skin,query=True,influence=True) or [])
        if any(cmds.objExists(name) for name in outputs):
            raise ValueError('An existing object occupies a weight-map output name')
    if command=='bsTransDoButtonCmd':
        blend=str(e.bsTransSrcBs_List.getValue())
        if not cmds.objExists(blend) or cmds.nodeType(blend)!='blendShape':
            raise ValueError('Load a valid source blendShape')
        aliases=cmds.aliasAttr(blend,query=True) or []
        for name in aliases[::2]:
            if cmds.objExists(name):
                raise ValueError('An existing object occupies a blendshape target name: '+name)
        for index in cmds.getAttr(blend+'.weight',multiIndices=True) or []:
            if cmds.listConnections(blend+'.weight['+str(index)+']',source=True,destination=False,plugs=True):
                raise ValueError('Source blendShape weights must be undriven in this backup scene')
    modifying={'setWeight0Cmd','setWeight01Cmd','setWeight025Cmd','setWeight05Cmd','setWeight075Cmd','setWeight09Cmd','setWeight1Cmd','setWeightFromValueCmd','plusWeightCmd','minusWeightCmd','pasteWeightCmd','relaxWeightCmd','reSkinCmd','mirrorWeightCmd','transferWeightCmd','pruneWeightCmd','normalizeWeightCmd','swapWeightCmd','swapMergeWeightCmd','lodMakeButtonCmd','goreMakeCmd','bsTransDoButtonCmd','deformerOKCmd','meshDelNonSkinHistoryCmd','meshCleanUpButtonCmd','buildWeightMapCmd','paintVertexOnCmd','bindSkinPlusButtonCmd','renameMakeCmd','scaleJointButtonCmd','cleanAttrButtonCmd','removeUnknowNodeButtonCmd','removeBoneCmd','addBoneCmd','boneLabelDoButtonCmd','importVtxWeightCmd'}
    if command in modifying:
        runtime.writable(list(expanded))
    return {'action':action,'command':command,'objects':objects,'affected_nodes':sorted(expanded),'scene_scope_acknowledged':bool(p.get('allow_scene_scope',False)),'impacts':'Original selected/cached business inputs, connected skin/rig hierarchy. Bind-pose/history removal/deletion/rename may be destructive; backup scene required. File-dialog exports exclusive; files and shelf/UI preferences are not Maya Undo.'}


@contextmanager
def operation_scope():
    global _busy,_temporary_xml,_proxy_uuid
    cmds=runtime.cmds_module()
    previous_busy=_busy
    _busy=True
    auto=cmds.autoKeyframe(query=True,state=True)
    current=cmds.currentTime(query=True)
    old_nodes={cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or []}
    # Preserve joint influence locks and visible model panel isolate settings.
    locks={n:cmds.getAttr(n+'.liw') for n in cmds.ls(type='joint',long=True) or [] if cmds.attributeQuery('liw',node=n,exists=True)}
    panels={n:cmds.isolateSelect(n,query=True,state=True) for n in cmds.getPanel(type='modelPanel') or []}
    blend_values={n+'.weight['+str(i)+']':cmds.getAttr(n+'.weight['+str(i)+']') for n in cmds.ls(type='blendShape') or [] for i in cmds.getAttr(n+'.weight',multiIndices=True) or []}
    with tempfile.TemporaryDirectory(prefix='skin_magic_') as folder:
        _temporary_xml=Path(folder)/'weights.xml'
        cmds.autoKeyframe(state=False)
        try:
            yield
        finally:
            _temporary_xml=None
            for n,value in locks.items():
                if cmds.objExists(n) and not cmds.referenceQuery(n,isNodeReferenced=True) and cmds.getAttr(n+'.liw')!=value:
                    cmds.setAttr(n+'.liw',value)
            for n,value in panels.items():
                if n in (cmds.getPanel(type='modelPanel') or []):
                    cmds.isolateSelect(n,state=value)
            for plug,value in blend_values.items():
                if cmds.objExists(plug) and cmds.getAttr(plug)!=value and not cmds.listConnections(plug,source=True,destination=False,plugs=True):
                    cmds.setAttr(plug,value)
            cmds.currentTime(current,update=True)
            cmds.autoKeyframe(state=auto)
            e=engine()
            proxy=getattr(e,'proxyMesh',None)
            if proxy and cmds.objExists(str(proxy)):
                uid=cmds.ls(str(proxy),uuid=True)[0]
                if uid not in old_nodes:
                    _proxy_uuid=uid
            _busy=previous_busy


def execute(p,plan=None):
    action=p['action']
    if action=='show_ui':
        return {'window':show_ui(p.get('language',''))}
    if action=='show_gore':
        return {'window':show_gore()}
    if action=='close_ui':
        close_ui()
        return {'closed':True}
    e=engine()
    cmds=runtime.cmds_module()
    command=p['command']
    plan=plan or preflight(p)
    with operation_scope():
        if 'objects' in p:
            cmds.select(plan['objects'],replace=True)
        if command=='paintVertexOnCmd' and e.vertexInfo:
            shape=str(e.vertexInfo[1].getShape())
            for attr in ('overrideEnabled','overrideShading','overrideDisplayType'):
                _display.setdefault(shape+'.'+attr,cmds.getAttr(shape+'.'+attr))
        if command=='renameUpdatePreview':
            e.renameUpdatePreview()
        elif command=='renameStartChangeCmd':
            e.renameStartChangeCmd(False)
        else:
            getattr(e,command)(False)
    return {'command':command,'selection':cmds.ls(selection=True,long=True,flatten=True) or [],'affected_nodes':plan['affected_nodes']}


def callback(command,*unused):
    if _busy:
        return
    from .tool import SkinMagicTool
    cmds=runtime.cmds_module()
    arguments={'action':'ui_command','command':command}
    if command=='renameMakeCmd' and engine().renameAll_radioButton.getSelect():
        arguments['allow_scene_scope']=True
        preview=SkinMagicTool().validate(**arguments)
        if not preview.success:
            cmds.warning(preview.message)
            return
        count=len(preview.data['affected_nodes'])
        if cmds.confirmDialog(title='SkinMagic — rename all',message='Rename across the scene: '+str(count)+' previewed nodes. Continue in this backup scene?',button=['Cancel','Rename'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')!='Rename':
            return
    result=SkinMagicTool().run(**arguments)
    if not result.success:
        cmds.warning(result.message+'; check Script Editor and Undo the failed operation before continuing')
    return result


def paint_off():
    global _proxy_uuid
    cmds=runtime.cmds_module()
    if _proxy_uuid:
        nodes=cmds.ls(_proxy_uuid,long=True) or []
        if nodes:
            cmds.delete(nodes)
    _proxy_uuid=None
    for plug,value in list(_display.items()):
        if cmds.objExists(plug):
            cmds.setAttr(plug,value)
    _display.clear()
    if _window:
        engine().proxyMesh=None
        engine().weight_paintVertexCheckBox.setValue(False)


def remove_selected_unknown():
    cmds=runtime.cmds_module()
    nodes=runtime.resolve(None)
    if not nodes or any(cmds.nodeType(n)!='unknown' for n in nodes):
        raise ValueError('Explicitly select only the unknown nodes to remove')
    runtime.writable(nodes)
    cmds.delete(nodes)
    return nodes


def add_shelf_button():
    cmds=runtime.cmds_module()
    from maya import mel
    parent=mel.eval('global string $gShelfTopLevel; string $skinMagicShelf=`tabLayout -q -selectTab $gShelfTopLevel`; $skinMagicShelf;')
    # Works in both this candidate and promoted layout without execfile or global
    # module pollution. The package root is resolved by its own __file__.
    from . import tool
    pkgroot=Path(tool.__file__).resolve().parents[3]
    command="import sys; from pathlib import Path; p="+repr(str(pkgroot))+"; sys.path.insert(0,p) if p not in sys.path else None; from maya_toolkit.tools.skin_magic.tool import SkinMagicTool; SkinMagicTool().show_ui()"
    return cmds.shelfButton(parent=parent,label='SkinMagic 4.0',image=str(Path(__file__).with_name('native')/'icons/Title.png'),sourceType='python',command=command)


def choose(kind,save):
    cmds=runtime.cmds_module()
    suffix={'weights':'*.VertexWeight','lod':'*.BoneList','xml':'*.xml'}[kind]
    result=cmds.fileDialog2(fileMode=0 if save else 1,caption='SkinMagic '+('export ' if save else 'import ')+kind,fileFilter=suffix,dialogStyle=2)
    if not result:
        return None
    if save:
        return fileio.output_path(result[0])
    fileio.read_bytes(result[0])
    return Path(result[0])


def vertex_info():
    e=engine()
    if e.vertexInfo:
        return e.vertexInfo
    plan=runtime.skin_plan(None)
    import pymel.core as pm
    return [plan['vertices'],pm.PyNode(plan['mesh']).getParent(),pm.PyNode(plan['skin'])]


def vertex_export(is_output=True):
    e=engine()
    info=vertex_info()
    data=e.prepareExprotVertexData(info)
    e.exprotVertexWeightData={str(v):list(pairs) for v,pairs in data.items()}
    if is_output:
        path=choose('weights',True)
        if path:
            return fileio.write(path,'weights',{str(v):[[str(j),w] for j,w in pairs] for v,pairs in data.items()})
    return {'vertices':len(data)}


def vertex_import(is_from=True):
    e=engine()
    if is_from:
        path=choose('weights',False)
        if not path:
            return
        data=fileio.read(path,'weights')
    else:
        data=e.exprotVertexWeightData
    if not data:
        raise ValueError('No vertex weight buffer')
    info=vertex_info()
    plan=runtime.skin_plan([str(v) for v in info[0]])
    rows=runtime.import_rows(plan,{str(v):[[str(j),w] for j,w in pairs] for v,pairs in data.items()})
    cmds=runtime.cmds_module()
    runtime.writable([plan['mesh'],plan['skin']])
    for vertex,pairs in rows:
        cmds.skinPercent(plan['skin'],vertex,transformValue=pairs,zeroRemainingInfluences=True)
    e.exprotVertexWeightData=None
    e.updateSkinClusterCache(info[2])
    return {'vertices':len(rows)}


def lod_export():
    e=engine()
    if not e.lodBoneDict:
        raise ValueError('Load a LoD bone mapping before export')
    path=choose('lod',True)
    if path:
        return fileio.write(path,'lod',{str(k):str(v) for k,v in e.lodBoneDict.items()})


def lod_import():
    e=engine()
    path=choose('lod',False)
    if not path:
        return
    data=fileio.read(path,'lod')
    cmds=runtime.cmds_module()
    for name in list(data)+list(data.values()):
        nodes=cmds.ls(name,long=True,type='joint') or []
        if len(nodes)!=1:
            raise ValueError('LoD joint missing or ambiguous: '+name)
    e.lodBoneDict={e.toJoint(k):e.toJoint(v) for k,v in data.items()}
    e.lodUpdateBoneListUI(e.lodBoneDict)
    return {'mapping_count':len(data)}


def xml_export(is_output=True):
    info=vertex_info()
    path=choose('xml',True) if is_output else _temporary_xml
    if not path:
        return
    if not is_output:
        fileio.output_path(str(path))
    cmds=runtime.cmds_module()
    with tempfile.TemporaryDirectory(prefix='skin_magic_xml_export_') as folder:
        cmds.deformerWeights('weights.xml',path=folder,export=True,deformer=str(info[2]),defaultValue=0.0)
        data=Path(folder,'weights.xml').read_bytes()
        with path.open('xb') as stream:
            stream.write(data)
    return str(path)


def api_weights(skin,shape):
    from maya.api import OpenMaya as om,OpenMayaAnim as oma
    selection=om.MSelectionList()
    selection.add(skin)
    fn=oma.MFnSkinCluster(selection.getDependNode(0))
    selection2=om.MSelectionList()
    selection2.add(shape)
    dag=selection2.getDagPath(0)
    component_fn=om.MFnSingleIndexedComponent()
    component=component_fn.create(om.MFn.kMeshVertComponent)
    component_fn.addElements(range(om.MFnMesh(dag).numVertices))
    weights,count=fn.getWeights(dag,component)
    return fn,dag,component,weights,count


def import_xml_weights(skin,shape,path):
    """Undo-safe native index XML import; only existing compatible influences."""
    from maya.api import OpenMaya as om
    cmds=runtime.cmds_module()
    tree=fileio.xml_tree(str(path))
    known=cmds.skinCluster(skin,query=True,influence=True) or []
    if not list(tree.iter('weights')):
        raise ValueError('XML contains no deformer weight data')
    for row in tree.iter('weights'):
        source=row.get('source')
        if source not in known and not any(n.rsplit('|',1)[-1]==source for n in known):
            raise ValueError('XML influence not bound to destination: '+str(source))
        if int(row.get('size','0'))!=cmds.polyEvaluate(shape,vertex=True):
            raise ValueError('XML vertex count differs from target')
        for point in row.findall('point'):
            index=int(point.get('index','-1'))
            value=float(point.get('value','nan'))
            if not 0<=index<int(row.get('size','0')) or not fileio.finite(value) or not 0<=value<=1:
                raise ValueError('XML point index/weight invalid')
    saved=api_weights(skin,shape)
    # Native deformerWeights does not reliably create Undo entries. Restore the
    # saved values through API, then replay imported values through skinPercent.
    try:
        cmds.deformerWeights(path.name,path=str(path.parent),im=True,deformer=skin,method='index',defaultValue=0.0)
        imported=runtime.capture_weights(skin)
    finally:
        saved[0].setWeights(saved[1],saved[2],om.MIntArray(range(saved[4])),saved[3],False)
    runtime.restore_weights(imported)
    return {'vertices':len(imported['rows'])}


def xml_import(is_from=True):
    info=vertex_info()
    path=choose('xml',False) if is_from else _temporary_xml
    if not path:
        return
    shape=str(info[1].getShape())
    skin=str(info[2])
    runtime.writable([shape,skin])
    if any(runtime.cmds_module().getAttr(j+'.liw') for j in runtime.cmds_module().skinCluster(skin,query=True,influence=True)):
        raise ValueError('Unlock destination influence weights before XML import')
    result=import_xml_weights(skin,shape,path)
    if not is_from:
        path.unlink()  # Always operation-owned temporary XML.
    return result


def show_gore():
    global _gore
    cmds=runtime.cmds_module()
    if not _window:
        show_ui()
    if _gore and cmds.window(_gore,exists=True):
        cmds.showWindow(_gore)
        return _gore
    import pymel.core as pm
    e=engine()
    _gore=str(pm.window(title='SkinMagic — Gore',widthHeight=(420,360)))
    pm.columnLayout(adjustableColumn=True)
    e.goreBaseMesh_lineEdit=pm.textField(text='Pick Skinned Base Mesh',editable=False)
    pm.button(label='Load selected base',command=functools.partial(callback,'goreGetBaseMeshCmd'))
    e.goreMesh_ListBox=pm.textScrollList(allowMultiSelection=True,height=170)
    for label,command in [('Add selected targets','goreAddCmd'),('Remove selected list items','goreRemoveCmd'),('Clear','goreClearCmd')]:
        pm.button(label=label,command=functools.partial(callback,command))
    e.goreDeleteBase_CheckBox=pm.checkBox(label='Delete original base mesh after binding',value=False)
    e.goreDeleteShader_CheckBox=pm.checkBox(label='Scene-wide shader cleanup removed',value=False,enable=False)
    pm.button(label='Build Gore (removes target history)',command=functools.partial(callback,'goreMakeCmd'))
    # Original complete Gore business is retained; source supplied no controls.
    for name,target in {'goreGetBaseMeshCmd':'goreGetBaseMesh','goreAddCmd':'goreAdd','goreRemoveCmd':'goreRemove','goreClearCmd':'goreClear','goreMakeCmd':'goreMake'}.items():
        setattr(e,name,lambda unused=False,target=target: getattr(e,target)())
    cmds.showWindow(_gore)
    return _gore


capture_weights=runtime.capture_weights
restore_weights=runtime.restore_weights


def node_uuid(node):
    return runtime.cmds_module().ls(str(node),uuid=True)[0]


def scene_uuids():
    cmds=runtime.cmds_module()
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or []}
