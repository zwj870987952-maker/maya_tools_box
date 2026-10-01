"""No implicit installation, source, UI or native plugin loading in preflight."""
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile

NATIVE=Path(__file__).with_name('native')


def pymel_available():
    try:
        return importlib.util.find_spec('pymel.core') is not None
    except (ImportError,ModuleNotFoundError,ValueError):
        return False


def plugins():
    from maya import cmds
    loaded={n.lower():n for n in cmds.pluginInfo(query=True,listPlugins=True) or []}
    return {name:loaded.get(name.lower()) for name in ('cvwrap','weightDriver','mgear_solvers')}


def status():
    catalog=json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf8'))
    return {'action':'status','plugins':plugins(),'pymel_available':pymel_available(),'files':len(catalog['files']),'python_modules':len(catalog['definitions']),'definitions':sum(len(v) for v in catalog['definitions'].values()),'versions':catalog['versions'],'compiled_plugins_bundled':False,'gui_acceptance':'not_run','namespace_activation':'Explicit; refuses another imported mgear/cvwrap distribution'}


def namespace_preflight():
    for family in ('mgear','cvwrap'):
        for name,module in list(sys.modules.items()):
            if name!=family and not name.startswith(family+'.'):
                continue
            path=getattr(module,'__file__',None)
            if path and not Path(path).resolve().is_relative_to((NATIVE/family).resolve()):
                raise RuntimeError('Another '+family+' distribution is already imported; use a fresh Maya session for this candidate')


def activate():
    namespace_preflight()
    root=str(NATIVE.resolve())
    if root not in sys.path:
        sys.path.insert(0,root)
    icons=str(NATIVE/'icons')
    existing=os.environ.get('MAYA_ICON_PATH','')
    if icons not in existing.split(os.pathsep):
        os.environ['MAYA_ICON_PATH']=icons+(os.pathsep+existing if existing else '')
    # Standard upstream package namespaces are intentionally retained, so all
    # 363 modules and their string callbacks work. No usersetup/.mod/env writes.


def path_input(value):
    path=Path(value)
    if not path.is_absolute() or not path.is_file() or path.stat().st_size>512*1024*1024:
        raise ValueError('Absolute existing file <=512 MiB required')
    return path


def path_output(value):
    path=Path(value)
    if not path.is_absolute() or not path.parent.is_dir() or path.exists() or path.is_symlink():
        raise ValueError('Absolute nonexistent output under an existing directory required; no overwrite')
    return path


def resolve(values,components=False):
    from maya import cmds
    from maya.api import OpenMaya as om
    values=values if values is not None else cmds.ls(selection=True,long=True,flatten=True) or []
    out=[]
    for name in values:
        if any(c in name for c in ('*','?',';','"','\n','\r','\\')) or (not components and '.' in name):
            raise ValueError('Explicit unique nodes/components required')
        matches=cmds.ls(name,long=True,flatten=True) or []
        if not matches or (not components and len(matches)!=1):
            raise ValueError('Missing/ambiguous target: '+name)
        for match in matches:
            base=match.split('.',1)[0]
            sel=om.MSelectionList()
            sel.add(base)
            obj=sel.getDependNode(0)
            if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))!=1:
                raise ValueError('Instanced targets unsupported')
            if match in out:
                raise ValueError('Duplicate/aliased targets')
            out.append(match)
    return out


def writable(values):
    from maya import cmds
    for name in values:
        base=name.split('.',1)[0]
        if cmds.referenceQuery(base,isNodeReferenced=True) or any(cmds.lockNode(base,query=True,lock=True) or []):
            raise ValueError('Referenced/locked writable scope: '+base)


def wrap_node(name):
    from maya import cmds
    values=resolve([name])
    if len(values)!=1 or cmds.nodeType(values[0])!='cvWrap':
        raise ValueError('An explicit cvWrap node is required')
    writable(values)
    return values[0]


def preflight(p):
    from maya import cmds
    action=p['action']
    if action=='status':
        return status()
    namespace_preflight()
    if action=='load_plugin':
        path=path_input(p['path'])
        if path.suffix.lower()!='.mll' or path.stem.lower()!=p['plugin'].lower():
            raise ValueError('Expected the named Windows native Maya .mll binary')
        return {'action':action,'plugin':p['plugin'],'path':str(path),'impact':'Explicit session plugin load only, no installation or autoload preference; Maya must accept binary/API compatibility'}
    dep='cvwrap' if action in ('create_wrap','rebind','import_binding','export_binding','paint_wrap','cvwrap_options','cvwrap_rebind_ui') else 'weightDriver' if action in ('weightdriver_editor','rbf_manager') else 'mgear_solvers'
    if not plugins()[dep]:
        raise RuntimeError('Required native '+dep+' plugin is not loaded; source bundle supplies no compatible binary. Load a user-supplied matching binary explicitly.')
    if action in ('rbf_manager','mgear_menu') and not pymel_available():
        raise RuntimeError('Bundled mGear 4.0.9 requires compatible PyMel, absent in this Maya')
    gui={'paint_wrap','cvwrap_options','cvwrap_rebind_ui','weightdriver_editor','rbf_manager','mgear_menu'}
    if action in gui and cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required; no QWidget construction in standalone')
    if action=='mgear_menu' and cmds.menu('mGear',exists=True):
        raise RuntimeError('Existing mGear menu must be closed explicitly before candidate activation; no replacement of another menu')
    plan={'action':action,'dependency':dep,'impact':'Native plugin scene operations are wrapped by Base Undo; original third-party editors retain their own scene/file/UI impact. Verify Undo in backup scene.'}
    if action=='create_wrap':
        objects=resolve(p.get('objects'))
        if len(objects)<2:
            raise ValueError('At least one surface and one influence object required in original selection order')
        writable(objects)
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*#?',p['name']) or ('#' not in p['name'] and cmds.objExists(p['name'])):
            raise ValueError('Invalid/existing cvWrap output name')
        for node in objects:
            kind=cmds.nodeType(node)
            shapes=cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True) or [] if kind=='transform' else [node]
            if not any(cmds.nodeType(s) in ('mesh','nurbsCurve','nurbsSurface') for s in shapes):
                raise ValueError('cvWrap surface/influence must have supported geometry')
        plan['objects']=objects
        if 'path' in p:
            plan['path']=str(path_input(p['path']))
    if 'wrap' in p:
        plan['wrap']=wrap_node(p['wrap'])
    if action=='rebind':
        objects=resolve(p.get('objects'),components=True)
        faces=resolve(p.get('faces'),components=True)
        if not objects or not faces:
            raise ValueError('Both driven components and explicit target faces required')
        writable(objects+faces)
        vertices=cmds.ls(cmds.polyListComponentConversion(objects,toVertex=True),flatten=True,long=True) or []
        target_faces=cmds.ls(cmds.polyListComponentConversion(faces,toFace=True),flatten=True,long=True) or []
        if not vertices or not target_faces:
            raise ValueError('Expected mesh vertices and faces')
        plan.update(objects=vertices,faces=target_faces)
    if action in ('import_binding','export_binding'):
        plan['path']=str(path_output(p['path']) if action=='export_binding' else path_input(p['path']))
        plan['external_file_undoable']=False
    return plan


def execute(p):
    from maya import cmds,mel
    action=p['action']
    plan=preflight(p)
    if action=='status':
        return plan
    if action=='load_plugin':
        result=cmds.loadPlugin(plan['path'],quiet=True)
        if not plugins()[p['plugin']]:
            raise RuntimeError('Binary load did not register expected native plugin')
        if p['plugin']=='cvwrap':
            mel.eval('source "'+(NATIVE/'AEcvWrapTemplate.mel').as_posix()+'";')
        return {'plugin':p['plugin'],'loaded':result,'autoload_changed':False}
    if action in ('create_wrap','rebind','import_binding','export_binding'):
        mel.eval('source "'+(NATIVE/'AEcvWrapTemplate.mel').as_posix()+'";')
        selection=cmds.ls(selection=True,long=True,flatten=True) or []
        try:
            if action=='create_wrap':
                cmds.select(plan['objects'],replace=True)
                kwargs={'name':p['name'],'radius':p['radius'],'newBindMesh':p['new_bind_mesh']}
                if 'path' in plan:
                    kwargs['binding']=plan['path']
                result=cmds.cvWrap(**kwargs)
            elif action=='rebind':
                cmds.select(plan['objects']+plan['faces'],replace=True)
                result=cmds.cvWrap(rb=plan['wrap'],radius=p['radius'])
            elif action=='import_binding':
                result=cmds.cvWrap(plan['wrap'],im=plan['path'])
            else:
                with tempfile.TemporaryDirectory(prefix='candidate_cvwrap_') as folder:
                    temp=Path(folder)/'binding.wrap'
                    cmds.cvWrap(plan['wrap'],ex=str(temp))
                    with path_output(plan['path']).open('xb') as target,temp.open('rb') as source:
                        import shutil
                        shutil.copyfileobj(source,target)
                result={'path':plan['path'],'external_file_undoable':False}
            return {'action':action,'result':result,'scope':plan}
        finally:
            cmds.select(selection,replace=True)
    activate()
    if action=='paint_wrap':
        mel.eval('artSetToolAndSelectAttr("artAttrCtx", "cvWrap.'+plan['wrap']+'.weights");')
    elif action=='cvwrap_options':
        importlib.import_module('cvwrap.menu').display_cvwrap_options()
    elif action=='cvwrap_rebind_ui':
        importlib.import_module('cvwrap.bindui').show()
    elif action=='weightdriver_editor':
        # Preserve all complete MEL procedures; global AE/MEL names are native
        # plugin contracts. Their installation is explicit, never a dry-run.
        for name in ('weightDriverUpdateEvaluation.mel','weightDriverEditRBF.mel','AEweightDriverTemplate.mel'):
            path=(NATIVE/name).as_posix()
            mel.eval('source "'+path+'";')
        mel.eval('weightDriverEditRBF;')
    elif action=='rbf_manager':
        importlib.import_module('mgear.rigbits.rbf_manager_ui').show()
    elif action=='mgear_menu':
        name='maya_toolkit.tools.cvwrap_weightdriver.native.explicit_startup'
        spec=importlib.util.spec_from_file_location(name,NATIVE/'userSetup.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.mGear_menu_loader()
    return {'action':action,'full_upstream_entry':True,'gui_acceptance':'not_run'}
