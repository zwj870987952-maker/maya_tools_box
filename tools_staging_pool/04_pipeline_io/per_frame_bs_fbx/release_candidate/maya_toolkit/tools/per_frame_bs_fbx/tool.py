"""World-space mesh snapshots into frame-pulsed blendShapes and rigid skin."""
import math
from pathlib import Path
import re
from maya_toolkit.framework import BaseMayaTool,ToolResult

def normalize(values):
    p=dict(action='inspect',root=None,start=None,end=None,step=1.0,output_group=None,output=None,ascii=False,copy_materials=True)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','build','build_export'): raise ValueError('Invalid action')
    for key in ('start','end','step'):
        if p[key] is not None and (type(p[key]) not in (int,float) or not math.isfinite(p[key])): raise ValueError('Finite frames/step required')
    if p['step'] is None or p['step']<=0: raise ValueError('Positive step required')
    for key in ('ascii','copy_materials'):
        if type(p[key]) is not bool: raise ValueError('Boolean options required')
    if p['root'] is not None and (not isinstance(p['root'],str) or not p['root'] or any(c in p['root'] for c in '*?\n\r')): raise ValueError('Exact root required')
    if p['output_group'] is not None and (not isinstance(p['output_group'],str) or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',p['output_group'])): raise ValueError('Simple output group name required')
    if p['output'] is not None and (not isinstance(p['output'],str) or not Path(p['output']).is_absolute() or Path(p['output']).suffix.lower()!='.fbx'): raise ValueError('Absolute .fbx output required')
    if p['action']=='build_export' and p['output'] is None: raise ValueError('Build export requires explicit output')
    return p

def dag_path(node):
    from maya.api import OpenMaya as om
    selected=om.MSelectionList(); selected.add(node); return selected.getDagPath(0)

def topology(mesh):
    from maya.api import OpenMaya as om
    fn=om.MFnMesh(dag_path(mesh)); counts,ids=fn.getVertices()
    return {'vertices':fn.numVertices,'polygons':fn.numPolygons,'counts':list(counts),'ids':list(ids)}

def plan(p):
    from maya import cmds
    from maya.api import OpenMaya as om
    roots=cmds.ls(p['root'],long=True) if p['root'] else cmds.ls(selection=True,long=True)
    if not roots or len(roots)!=1 or '.' in roots[0] or not cmds.objectType(roots[0],isAType='transform'): raise ValueError('Select/provide exactly one mesh transform/group')
    root=roots[0]
    meshes=(cmds.listRelatives(root,allDescendents=True,fullPath=True,type='mesh') or [])+(cmds.listRelatives(root,shapes=True,fullPath=True,type='mesh') or [])
    meshes=sorted({m for m in meshes if not cmds.getAttr(m+'.intermediateObject')})
    if not meshes: raise ValueError('Root contains no non-intermediate polygon mesh')
    for mesh in meshes:
        if len(om.MDagPath.getAllPathsTo(dag_path(mesh).node()))!=1: raise ValueError('Shared DAG mesh instance unsupported')
    start=p['start'] if p['start'] is not None else cmds.playbackOptions(query=True,minTime=True)
    end=p['end'] if p['end'] is not None else cmds.playbackOptions(query=True,maxTime=True)
    if end<start or not math.isclose((end-start)/p['step'],round((end-start)/p['step']),abs_tol=1e-7): raise ValueError('Range must end on the step grid')
    count=round((end-start)/p['step'])+1
    if not 1<=count<=2000: raise ValueError('1..2000 samples required; one target per sample and mesh')
    name=p['output_group'] or re.sub('[^A-Za-z0-9_]','_',root.rsplit('|',1)[-1].split(':')[-1])+'_FbxExpGrp'
    if name[0].isdigit(): name='export_'+name
    if cmds.objExists(':'+name): raise ValueError('Output group already exists; original group will never be reused/overwritten')
    rows=[{'source':m,'uuid':cmds.ls(m,uuid=True)[0],'topology':topology(m)} for m in meshes]
    if sum(r['topology']['vertices'] for r in rows)*count>10000000: raise ValueError('Sample exceeds 10 million stored vertex snapshots')
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Maya Undo')
    if p['output'] is not None:
        path=Path(p['output'])
        if path.exists() or path.is_symlink() or not path.parent.is_dir(): raise ValueError('Explicit FBX must be a new file in existing directory')
    return {'root':root,'meshes':rows,'frames':[start+i*p['step'] for i in range(count)],'output_group':name,'targets':count*len(meshes),'stored_vertices':sum(r['topology']['vertices'] for r in rows)*count,'output':p['output']}

def identities():
    from maya import cmds
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or []}

def copy_mesh(source,parent,name,world_points=True):
    from maya import cmds
    from maya.api import OpenMaya as om
    transform=cmds.createNode('transform',name=name,parent=parent) if parent else cmds.createNode('transform',name=name)
    selection=om.MSelectionList(); selection.add(transform)
    src=om.MFnMesh(dag_path(source)); node=om.MFnMesh().copy(src.object(),selection.getDependNode(0))
    shape=om.MFnDagNode(node).fullPathName()
    if world_points: om.MFnMesh(node).setPoints(src.getPoints(om.MSpace.kWorld),om.MSpace.kObject)
    return cmds.ls(transform,long=True)[0],shape

def copy_materials(source,shape):
    from maya import cmds
    from maya.api import OpenMaya as om
    path=dag_path(source); sets,indices=om.MFnMesh(path).getConnectedShaders(path.instanceNumber())
    for index,shader in enumerate(sets):
        sg=om.MFnDependencyNode(shader).name(); faces=[i for i,value in enumerate(indices) if value==index]
        if faces: cmds.sets([shape+'.f['+str(i)+']' for i in faces],edit=True,forceElement=sg)

def build(p,data):
    from maya import cmds
    from maya.api import OpenMaya as om
    before=identities(); selected=cmds.ls(selection=True,long=True) or []; time=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
    namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True); rows=[]
    try:
        cmds.namespace(set=':'); cmds.autoKeyframe(state=False); cmds.currentTime(data['frames'][0])
        group=cmds.createNode('transform',name=data['output_group']); group=cmds.ls(group,long=True)[0]
        joint=cmds.createNode('joint',name=data['output_group']+'_RootJoint',parent=group); joint=cmds.ls(joint,long=True)[0]
        for index,row in enumerate(data['meshes']):
            matches=cmds.ls(row['uuid'],long=True) or []
            if len(matches)!=1 or topology(matches[0])!=row['topology']: raise RuntimeError('Source topology/identity changed at first sample')
            source=matches[0]; base,shape=copy_mesh(source,group,'mesh_'+str(index)+'_exp')
            if p['copy_materials']: copy_materials(source,shape)
            else: cmds.sets(shape,edit=True,forceElement='initialShadingGroup')
            bs=cmds.blendShape(base,origin='local',name=data['output_group']+'_mesh'+str(index)+'_ani_bs')[0]
            skin=cmds.skinCluster(joint,base,toSelectedBones=True,maximumInfluences=1,normalizeWeights=1,name=data['output_group']+'_mesh'+str(index)+'_skin')[0]
            rows.append(dict(row,source=source,base=base,blend_shape=bs,skin_cluster=skin))
        for target_index,frame in enumerate(data['frames']):
            cmds.currentTime(frame)
            cmds.setKeyframe(joint,attribute=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ'],time=frame)
            for index,row in enumerate(rows):
                if topology(row['source'])!=row['topology']: raise RuntimeError('Animated topology changed at frame '+str(frame))
                target,shape=copy_mesh(row['source'],None,data['output_group']+'_target_'+str(index)+'_'+str(target_index))
                cmds.blendShape(row['blend_shape'],edit=True,target=(row['base'],target_index,target,1.0),topologyCheck=True)
                plug=row['blend_shape']+'.weight['+str(target_index)+']'
                for when,value in ((frame-p['step'],0),(frame,1),(frame+p['step'],0)):
                    cmds.setKeyframe(plug,time=when,value=value,inTangentType='linear',outTangentType='linear')
                cmds.delete(target)
        return {'group':group,'joint':joint,'meshes':rows,'frames':data['frames'],'targets':data['targets'],'source_modified':False,'space':'world vertices baked into identity output meshes'}
    except Exception:
        # Only this operation's new UUIDs, including bind poses/curves/deformers.
        for identity in identities()-before:
            names=cmds.ls(identity,long=True) or []
            if names:
                try: cmds.delete(names)
                except RuntimeError: pass
        raise
    finally:
        cmds.namespace(set=namespace if cmds.namespace(exists=namespace) else ':')
        cmds.currentTime(time); cmds.autoKeyframe(state=auto); valid=[n for n in selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)

class PerFrameBsFbxTool(BaseMayaTool):
    tool_id='per_frame_bs_fbx'; tool_name='模型逐帧转BS与FBX'; category='pipeline_io'; version='1.0.0-candidate1'
    description='World-space per-frame mesh snapshots as pulse-keyed blendShapes and one rigid root joint; complete independent output group, optional guarded FBX export.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','build','build_export'],'default':'inspect'},'root':{'type':'string'},'start':{'type':'number'},'end':{'type':'number'},'step':{'type':'number','exclusiveMinimum':0,'default':1},'output_group':{'type':'string','pattern':'^[A-Za-z_][A-Za-z0-9_]*$'},'output':{'type':'string'},'ascii':{'type':'boolean','default':False},'copy_materials':{'type':'boolean','default':True}}}
    def validate(self,**values):
        try: return ToolResult.ok(message='Per-frame BS preflight passed',data=plan(normalize(values)),warnings=['One target per sample/mesh; topology-changing meshes refused during build; FBX/file logs are not Undoable'])
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])
    def execute(self,**values):
        p=normalize(values); data=plan(p)
        if p['action']=='inspect': return ToolResult.ok(message='Per-frame snapshot inspected',data=data)
        result=build(p,data)
        if p['action']=='build_export':
            from .fbx_io import export,DEFAULTS
            try:
                result['outputs']=export({'tasks':[{'objects':[result['group']],'start':data['frames'][0],'end':data['frames'][-1],'output':p['output']}],'options':dict(DEFAULTS,ascii=p['ascii'],embedded_textures=False,blend_shapes=True)})
            except Exception as exc: return ToolResult.fail(message='BS group created, FBX export failed: '+str(exc),data=result,errors=[str(exc)])
        return ToolResult.ok(message='Per-frame BS group generated'+(' and FBX saved' if p['action']=='build_export' else '; select group for manual FBX export'),data=result)
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui()
