"""Read-only plans and native Maya batch weights, independent of PyMel."""
import importlib.util
from pathlib import Path
import re
from . import fileio


def cmds_module():
    from maya import cmds
    return cmds


def pymel_available():
    try:
        return importlib.util.find_spec('pymel.core') is not None
    except (ImportError,ValueError,ModuleNotFoundError):
        return False


def require_pymel():
    if not pymel_available():
        raise RuntimeError('Full SkinMagic GUI/engine requires compatible PyMel, absent on this Maya; no substitute/stub was installed')


def resolve(values):
    cmds=cmds_module()
    values=values if values is not None else (cmds.ls(selection=True,long=True,flatten=True) or [])
    out=[]
    for value in values:
        if any(x in value for x in ('*','?','"',';','\n','\r','\\')):
            raise ValueError('Wildcards/command text are not valid object names')
        nodes=cmds.ls(value,long=True,flatten=True) or []
        if not nodes or ('.' not in value and len(nodes)!=1):
            raise ValueError('Object is missing or ambiguous: '+value)
        for node in nodes:
            base=node.split('.',1)[0]
            from maya.api import OpenMaya as om
            selection=om.MSelectionList()
            selection.add(base)
            obj=selection.getDependNode(0)
            if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))!=1:
                raise ValueError('Instanced DAG targets are unsupported')
            if node in out:
                raise ValueError('Aliased/duplicate targets')
            out.append(node)
    return out


def writable(values):
    cmds=cmds_module()
    for value in set(values):
        node=value.split('.',1)[0]
        if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []):
            raise ValueError('Referenced/locked target: '+node)


def skin_plan(values):
    cmds=cmds_module()
    targets=resolve(values)
    if not targets:
        raise ValueError('Select one skinned mesh or its vertices')
    vertices=[]
    meshes=set()
    for target in targets:
        base=target.split('.',1)[0]
        shape=base if cmds.nodeType(base)=='mesh' else None
        if not shape:
            shapes=cmds.listRelatives(base,shapes=True,noIntermediate=True,fullPath=True,type='mesh') or []
            if len(shapes)!=1:
                raise ValueError('Expected one mesh shape: '+base)
            shape=shapes[0]
        meshes.add(shape)
        if '.' in target:
            if not re.fullmatch(r'.+\.vtx\[[0-9]+\]',target):
                raise ValueError('Only mesh vertex components are accepted')
            if not cmds.objExists(target):
                raise ValueError('Vertex out of range')
            vertices.append(target)
        else:
            vertices.extend(cmds.ls(shape+'.vtx[*]',flatten=True,long=True) or [])
    if len(meshes)!=1 or len(vertices)!=len(set(vertices)) or not vertices:
        raise ValueError('One mesh, with nonoverlapping vertices required')
    shape=next(iter(meshes))
    skins=cmds.ls(cmds.listHistory(shape) or [],type='skinCluster') or []
    if len(skins)!=1:
        raise ValueError('Expected exactly one skinCluster')
    influences=cmds.skinCluster(skins[0],query=True,influence=True) or []
    return {'mesh':shape,'skin':skins[0],'vertices':vertices,'influences':influences}


def influence_pairs(weights, influences):
    cmds=cmds_module()
    known={cmds.ls(n,uuid=True)[0]:n for n in influences}
    pairs=[]
    for name,value in weights.items():
        matches=cmds.ls(name,long=True) or []
        if len(matches)!=1 or cmds.ls(matches[0],uuid=True)[0] not in known:
            raise ValueError('Influence missing/ambiguous/not bound: '+name)
        resolved=known[cmds.ls(matches[0],uuid=True)[0]]
        if any(n==resolved for n,_ in pairs):
            raise ValueError('Duplicate influence aliases')
        if cmds.getAttr(resolved+'.liw'):
            raise ValueError('Influence weights are locked: '+resolved)
        pairs.append((resolved,value))
    return pairs


def import_rows(plan, values):
    cmds=cmds_module()
    by_index={int(v.rsplit('[',1)[1][:-1]):v for v in plan['vertices']}
    rows=[]
    for name,pairs in values.items():
        idx=int(name.rsplit('[',1)[1][:-1])
        if idx not in by_index:
            raise ValueError('File vertex index outside explicitly selected destination: '+str(idx))
        rows.append((by_index[idx],influence_pairs(dict(pairs),plan['influences'])))
    return rows


def preflight(p):
    action=p['action']
    if action=='status':
        from .tool import CATALOG,COMMANDS
        return {'action':action,'pymel_available':pymel_available(),'source_functions':len(CATALOG['functions']),'resources':len(CATALOG['files']),'commands':COMMANDS,'maya_gui_acceptance':'not_run'}
    cmds=cmds_module()
    if action in ('show_ui','show_gore','close_ui','ui_command'):
        require_pymel()
        if cmds.about(batch=True):
            raise RuntimeError('SkinMagic UI requires interactive Maya; standalone GUI construction is forbidden')
        from . import ui_support
        return ui_support.preflight(p)
    plan=skin_plan(p.get('objects'))
    plan['action']=action
    if action in ('set_weights','import_weights'):
        writable([plan['mesh'],plan['skin']]+plan['vertices'])
        if any(cmds.getAttr(j+'.liw') for j in plan['influences']):
            raise ValueError('Import/set refuses a skin with locked influence weights')
        if cmds.getAttr(plan['skin']+'.envelope')==0:
            raise ValueError('Disabled skinCluster')
    if action=='set_weights':
        plan['pairs']=influence_pairs(p['weights'],plan['influences'])
    if action=='export_weights':
        plan['path']=str(fileio.output_path(p['path']))
    if action=='import_weights':
        plan['rows']=import_rows(plan,fileio.read(p['path'],'weights'))
        plan['path']=p['path']
    plan['impacts']={'scene_write':action in ('set_weights','import_weights'),'external_write':action=='export_weights','undo_external_file':False}
    return plan


def capture_weights(skin):
    cmds=cmds_module()
    geometries=cmds.skinCluster(skin,query=True,geometry=True) or []
    influences=cmds.skinCluster(skin,query=True,influence=True) or []
    rows=[]
    for shape in geometries:
        for vertex in cmds.ls(shape+'.vtx[*]',flatten=True,long=True) or []:
            rows.append((vertex,list(zip(influences,cmds.skinPercent(skin,vertex,query=True,value=True)))))
    return {'skin':skin,'rows':rows}


def restore_weights(snapshot):
    cmds=cmds_module()
    for vertex,pairs in snapshot['rows']:
        cmds.skinPercent(snapshot['skin'],vertex,transformValue=pairs,zeroRemainingInfluences=True,normalize=False)


def execute(p):
    plan=preflight(p)
    action=p['action']
    if action=='status':
        return plan
    if action in ('show_ui','show_gore','close_ui','ui_command'):
        from .ui_support import execute as ui_execute
        return ui_execute(p,plan)
    cmds=cmds_module()
    if action=='inspect_skin':
        plan['weights']={v:cmds.skinPercent(plan['skin'],v,query=True,value=True) for v in plan['vertices']}
        return plan
    if action=='export_weights':
        values={v:[[j,w] for j,w in zip(plan['influences'],cmds.skinPercent(plan['skin'],v,query=True,value=True)) if w>0] for v in plan['vertices']}
        return {'path':fileio.write(plan['path'],'weights',values),'vertices':len(values),'external_file_undoable':False}
    rows=plan.get('rows',[(v,plan.get('pairs',[])) for v in plan['vertices']])
    for vertex,pairs in rows:
        cmds.skinPercent(plan['skin'],vertex,transformValue=pairs,zeroRemainingInfluences=True,normalize=False)
    return {'skin':plan['skin'],'vertices':len(rows),'one_framework_undo':True}
