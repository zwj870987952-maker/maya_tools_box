"""Precise read-only ordered task planning and undoable original weight merge."""
from .algorithms import merged_rows


def environment():
    from maya import cmds
    from maya.api import OpenMaya as om,OpenMayaAnim as oma
    return cmds,om,oma


def resolve(name,kind=None):
    cmds,om,_=environment()
    if any(c in name for c in ('*','?',';','"','\n','\r','.')):
        raise ValueError('Expected a whole node name without wildcards/code: '+name)
    nodes=cmds.ls(name,long=True) or []
    if len(nodes)!=1 or (kind and cmds.nodeType(nodes[0])!=kind):
        raise ValueError('Missing, ambiguous or wrong node type: '+name)
    node=nodes[0]
    selection=om.MSelectionList()
    selection.add(node)
    obj=selection.getDependNode(0)
    if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))!=1:
        raise ValueError('Instanced DAG nodes are unsupported: '+node)
    return node


def uuid(name):
    return environment()[0].ls(name,uuid=True)[0]


def mesh_shape(name):
    cmds,_,_=environment()
    node=resolve(name)
    if cmds.nodeType(node)=='mesh':
        if cmds.getAttr(node+'.intermediateObject'):
            raise ValueError('Intermediate mesh is not a target')
        return node
    shapes=cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True,type='mesh') or []
    if len(shapes)!=1:
        raise ValueError('Expected one visible mesh: '+node)
    return resolve(shapes[0],'mesh')


def writable(names):
    cmds,_,_=environment()
    for node in names:
        if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []):
            raise ValueError('Referenced/locked writable scope: '+node)


def discover(source):
    cmds,_,_=environment()
    skins=cmds.listConnections(source+'.worldMatrix',source=False,destination=True,type='skinCluster') or []
    shapes=[]
    for skin in skins:
        for shape in cmds.skinCluster(skin,query=True,geometry=True) or []:
            full=mesh_shape(shape)
            if full not in shapes:
                shapes.append(full)
    return shapes


def read_weights(skin,shape):
    cmds,om,oma=environment()
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
    influences=[path.fullPathName() for path in fn.influenceObjects()]
    return list(weights),count,influences


def scope(shape):
    cmds,_,_=environment()
    skins=cmds.ls(cmds.listHistory(shape,pruneDagObjects=True) or [],type='skinCluster') or []
    if len(skins)!=1:
        raise ValueError('Expected exactly one skinCluster: '+shape)
    skin=skins[0]
    geometries=[mesh_shape(n) for n in cmds.skinCluster(skin,query=True,geometry=True) or []]
    if geometries!=[shape]:
        raise ValueError('Multi-geometry skinClusters are unsupported')
    writable([shape,skin]+(cmds.listRelatives(shape,parent=True,fullPath=True) or []))
    if cmds.getAttr(skin+'.skinningMethod')!=0:
        raise ValueError('Only classic linear skin supported; DQ/blended weight redistribution needs separate acceptance')
    if cmds.listConnections(skin+'.weightList',source=True,destination=False,plugs=True):
        raise ValueError('Skin weight inputs are connected/driven')
    if cmds.getAttr(skin+'.maintainMaxInfluences'):
        raise ValueError('Disable maintainMaxInfluences before exact full weight merge')
    weights,count,influences=read_weights(skin,shape)
    if not weights:
        raise ValueError('Mesh has no vertices')
    for joint in influences:
        if cmds.getAttr(joint+'.liw'):
            raise ValueError('Influence weights locked: '+joint)
    return {'shape':shape,'skin':skin,'influences':influences,'weights':weights,'count':count,'vertex_count':len(weights)//count}


def preflight(p):
    cmds,_,_=environment()
    tasks=[]
    virtual={}
    for task in p['tasks']:
        source=resolve(task['source_joint'],'joint')
        target=resolve(task['target_joint'],'joint')
        if uuid(source)==uuid(target):
            raise ValueError('Source and target must differ')
        meshes=[mesh_shape(n) for n in task['meshes']] if task['meshes'] else discover(source)
        if not meshes or len({uuid(n) for n in meshes})!=len(meshes):
            raise ValueError('No source-linked meshes, or aliased/duplicate mesh targets')
        rows=[]
        for shape in meshes:
            info=scope(shape)
            skin=info['skin']
            current=virtual.setdefault(uuid(skin),set(uuid(n) for n in info['influences']))
            if uuid(source) not in current or uuid(target) not in current:
                raise ValueError('Source/target influence absent (or removed by earlier task): '+shape)
            indices={uuid(n):idx for idx,n in enumerate(info['influences'])}
            merged_rows(info['weights'],info['count'],indices[uuid(source)],indices[uuid(target)])
            if task['remove_source']:
                writable([source])
                current.remove(uuid(source))
            rows.append({k:v for k,v in info.items() if k not in ('weights','count')})
        tasks.append({'source_joint':source,'target_joint':target,'remove_source':task['remove_source'],'meshes':rows})
    return {'action':p['action'],'tasks':tasks,'impact':'All vertices: target += source, source=0, normalize all influences; optional source influence removal. No joint deletion/files. One outer Undo.','gui_acceptance':'not_run'}


def execute(p):
    plan=preflight(p)
    if p['action']=='inspect':
        return plan
    cmds,_,_=environment()
    done=[]
    for task in plan['tasks']:
        for row in task['meshes']:
            # Re-read after each earlier task: A->B then B->C must carry A too.
            weights,count,influences=read_weights(row['skin'],row['shape'])
            indices={uuid(n):i for i,n in enumerate(influences)}
            values=merged_rows(weights,count,indices[uuid(task['source_joint'])],indices[uuid(task['target_joint'])])
            for index,weights_row in enumerate(values):
                cmds.skinPercent(row['skin'],row['shape']+'.vtx['+str(index)+']',transformValue=list(zip(influences,weights_row)),zeroRemainingInfluences=True,normalize=False)
            if task['remove_source']:
                cmds.skinCluster(row['skin'],edit=True,removeInfluence=task['source_joint'])
            done.append({'shape':row['shape'],'skin':row['skin'],'source_joint':task['source_joint'],'target_joint':task['target_joint'],'vertices':len(values),'source_removed':task['remove_source']})
    return {'tasks_completed':len(plan['tasks']),'meshes_processed':done}
