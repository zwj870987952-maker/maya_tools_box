"""Explicit path-character policy, actual owners and guarded scene-only cleanup."""
import json
from pathlib import Path
import re
from maya_toolkit.framework import BaseMayaTool,ToolResult

PATHS={
 'file':['fileTextureName'],'psdFileTex':['fileTextureName'],'substance':['filename'],'movie':['fileTextureName'],
 'noise':['noiseTextureName'],'mentalrayTexture':['fileTextureName'],'imagePlane':['imageName'],
 'aiImage':['filename'],'aiStandIn':['dso'],'aiPhotometricLight':['aiFilename'],
 'VRayBitmap':['bitmap'],'VRayHDRI':['filepath'],'VRayTexture':['texturePath'],'VRayPtex':['ptexFile'],
 'VRayVolumeGrid':['file'],'VRayLightIES':['iesFile'],'RedshiftSprite':['tex0'],'RedshiftNormalMap':['tex0'],
 'RedshiftBitmap':['tex0'],'RedshiftIESLight':['profile'],'RedshiftDomeLight':['tex0'],'RedshiftProxy':['fileName'],
 'PxrTexture':['filename'],'AlembicNode':['abc_File','cacheFileName'],'gpuCache':['cacheFileName'],
 'cacheFile':['cachePath','cacheName'],'audio':['filename'],'fluidTexture2D':['textureName'],'fluidTexture3D':['textureName'],
 **{n:['imageFileName'] for n in ('envBall','envCube','envChrome','envSky','envSphere')},
}
CONTAINERS={'layeredTexture','VRayMtl'}
EXTRA={'RenderMan_for_Maya':['PxrMultiTexture','PxrLayer','PxrPtexture'], 'mtoa':['aiVolume','aiLightProfile','aiMixTexture'],
       'vrayformaya':['VRayLightDomeShape','VRayEnvironment','VRayVolumetricGrid'],'redshift4maya':['RedshiftEnvironment','RedshiftVolume']}
COMMON=['fileTextureName','filename','imageName','texturePath','bitmap','tex0','fileName','filepath','file','dso','profile','iesFile','cacheFileName','abc_File']

def reasons(path,policy='ascii'):
    if not path: return []
    if policy=='ascii': return ['non_ascii_policy'] if any(ord(c)>127 for c in path) else []
    if policy=='cjk': return ['cjk_policy'] if re.search('[\u4e00-\u9fff]',path) else []
    return ['replacement_character'] if '\ufffd' in path else []

def normalize(values):
    p=dict(action='scan',nodes=None,policy='ascii',allow_reference_removal=False)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('scan','select','delete') or p['policy'] not in ('ascii','cjk','replacement'): raise ValueError('Invalid action/policy')
    if type(p['allow_reference_removal']) is not bool: raise ValueError('Reference removal option must be bool')
    if p['nodes'] is not None and (not isinstance(p['nodes'],list) or not p['nodes'] or len(p['nodes'])>10000 or any(not isinstance(n,str) or not n or any(c in n for c in '*?\n\r') for n in p['nodes']) or len(set(p['nodes']))!=len(p['nodes'])): raise ValueError('Unique exact node/UUID names required')
    return p

def supported_types():
    from maya import cmds
    available=set(cmds.allNodeTypes() or []); result=set(PATHS)|CONTAINERS|{'reference'}
    for plugin,types in EXTRA.items():
        try:
            if cmds.pluginInfo(plugin,query=True,loaded=True): result.update(types)
        except RuntimeError: pass
    return result&available

def get_file_nodes():
    from maya import cmds
    return sorted({n for t in supported_types() for n in cmds.ls(type=t,long=True) or []})

def resolve(name):
    from maya import cmds
    nodes=cmds.ls(name,long=True) or []
    if len(nodes)!=1 or '.' in nodes[0]: raise ValueError('Exact unambiguous scene node required: '+name)
    return nodes[0]

def direct_paths(node):
    from maya import cmds
    kind=cmds.nodeType(node)
    if kind=='reference':
        if node=='sharedReferenceNode': return []
        try: return [('reference_file',cmds.referenceQuery(node,filename=True,withoutCopyNumber=True))]
        except RuntimeError: return []
    rows=[]
    for attr in PATHS.get(kind,COMMON if kind not in CONTAINERS else []):
        if not cmds.attributeQuery(attr,node=node,exists=True): continue
        plug=node+'.'+attr
        try:
            if cmds.getAttr(plug,type=True)!='string': continue
            path=cmds.getAttr(plug)
            if isinstance(path,str) and path: rows.append((attr,path))
        except RuntimeError: continue
    return rows

def scan(p):
    from maya import cmds
    nodes=[resolve(n) for n in p['nodes']] if p['nodes'] is not None else get_file_nodes()
    rows=[]; seen=set(); containers=[]
    for node in nodes:
        if cmds.nodeType(node) in CONTAINERS:
            pending=list(cmds.listConnections(node,source=True,destination=False) or []); visited={node}; owners=set()
            while pending:
                current=resolve(pending.pop())
                if current in visited: continue
                visited.add(current)
                if len(visited)>10000: raise ValueError('Texture graph exceeds bounded scan')
                paths=direct_paths(current)
                if paths:
                    owners.add(current)
                    for attr,path in paths:
                        issue=reasons(path,p['policy']); key=(current,attr)
                        if issue and key not in seen:
                            rows.append(record(current,attr,path,issue)); seen.add(key)
                else: pending.extend(cmds.listConnections(current,source=True,destination=False) or [])
            containers.append({'container':node,'path_owners':sorted(owners),'delete_container':False})
        else:
            for attr,path in direct_paths(node):
                issue=reasons(path,p['policy']); key=(node,attr)
                if issue and key not in seen: rows.append(record(node,attr,path,issue)); seen.add(key)
    return {'issues':rows,'count':len(rows),'containers':containers,'policy':p['policy'],'file_existence_checked':False,'external_files_modified':False}

def record(node,attr,path,issue):
    from maya import cmds
    return {'node':node,'uuid':cmds.ls(node,uuid=True)[0],'type':cmds.nodeType(node),'attribute':attr,'path':path,'reasons':issue}

def plan(p):
    from maya import cmds
    data=scan(p)
    if p['action']!='delete': return data
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Maya Undo before node cleanup')
    nodes=sorted({r['node'] for r in data['issues']})
    if p['nodes'] is not None and any(cmds.nodeType(resolve(n)) in CONTAINERS for n in p['nodes']): raise ValueError('Container deletion refused; explicitly select its actual path owner')
    ordinary=[]; refs=[]
    for node in nodes:
        if cmds.nodeType(node)=='reference':
            if not p['allow_reference_removal']: raise ValueError('Reference path flagged: explicit allow_reference_removal=True required; deletes whole referenced file')
            refs.append(node); continue
        affected=[node]+(cmds.listRelatives(node,allDescendents=True,fullPath=True) or [])
        for affected_node in affected:
            from maya.api import OpenMaya as om
            selection=om.MSelectionList(); selection.add(affected_node); handle=selection.getDependNode(0)
            if handle.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(handle))>1: raise ValueError('Shared DAG instance deletion refused: '+affected_node)
            if cmds.referenceQuery(affected_node,isNodeReferenced=True): raise ValueError('Referenced owner/descendant cannot be deleted as local node: '+affected_node)
            if cmds.lockNode(affected_node,query=True,lock=True)[0] or cmds.ls(affected_node,defaultNodes=True): raise ValueError('Locked/default node cannot be deleted: '+affected_node)
        ordinary.append({'node':node,'uuid':cmds.ls(node,uuid=True)[0],'descendants':affected[1:],'connections':cmds.listConnections(node,connections=True,plugs=True) or []})
    from .reference_ops import references
    data.update(delete_nodes=ordinary,references=references({'reference_nodes':refs}) if refs else [],whole_reference_removal=bool(refs))
    return data

def operation(p):
    from maya import cmds
    path=Path(__file__).with_name('delete_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbCleanPathNodes' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path: raise ValueError('Other package owns cleanup command; restart Maya')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    value=cmds.mtbCleanPathNodes(json.dumps(p)); return json.loads(value[0] if isinstance(value,list) else value)

class CleanInvalidPathsTool(BaseMayaTool):
    tool_id='clean_invalid_paths'; tool_name='路径字符策略检查与清理'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Read-only ASCII/CJK/replacement-character path audit, actual texture/cache/reference owners; explicit guarded scene node deletion with Undo and whole-reference preview.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['scan','select','delete'],'default':'scan'},'nodes':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':10000,'uniqueItems':True},'policy':{'type':'string','enum':['ascii','cjk','replacement'],'default':'ascii'},'allow_reference_removal':{'type':'boolean','default':False}}}
    def validate(self,**values):
        try: return ToolResult.ok(message='Path audit/cleanup preflight complete',data=plan(normalize(values)),warnings=['Non-ASCII is a compatibility policy, not evidence of a broken path; no external files deleted'])
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])
    def execute(self,**values):
        from maya import cmds
        p=normalize(values); data=plan(p)
        if p['action']=='delete': data=operation(p)
        elif p['action']=='select':
            nodes=sorted({r['node'] for r in data['issues']})
            if nodes: cmds.select(nodes,replace=True)
        return ToolResult.ok(message='Path nodes '+p['action']+' completed',data=data)
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import create_ui
        return create_ui()
