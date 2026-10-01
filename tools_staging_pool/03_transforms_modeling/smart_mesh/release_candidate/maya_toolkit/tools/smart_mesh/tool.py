import re
from collections import Counter
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=['combine','separate','extract','duplicate','shelf','hotkey']
OPTIONS=['combine','separate','extract','duplicate','window']
PROPS={'action':{'type':'string','enum':ACTIONS,'default':'combine'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'components':{'type':'array','items':{'type':'string'},'uniqueItems':True},'custom_names':{'type':'boolean','default':True},'option':{'type':'integer','minimum':0,'maximum':4,'default':0},'key':{'type':'string','minLength':1,'maxLength':1},'alt':{'type':'boolean','default':True},'ctrl':{'type':'boolean','default':True},'shelf':{'type':'string'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(action='combine'); p.update(kwargs)
    if p['action'] not in ACTIONS: raise ValueError('Unknown action')
    allowed={'combine':{'objects','custom_names'},'separate':{'objects','custom_names'},'extract':{'components','custom_names'},'duplicate':{'components','custom_names'},'shelf':{'option','shelf'},'hotkey':{'option','key','alt','ctrl'}}[p['action']]
    if set(p)-{'action'}-allowed: raise ValueError('Argument does not apply to action')
    if p['action'] in ('shelf','hotkey'):
        p.setdefault('option',0)
        if type(p['option']) is not int or not 0<=p['option']<=(3 if p['action']=='hotkey' else 4): raise ValueError('Invalid install option')
        if p['action']=='hotkey':
            p.setdefault('alt',True); p.setdefault('ctrl',True)
            if any(type(p[k]) is not bool for k in ('alt','ctrl')) or not isinstance(p.get('key'),str) or not re.fullmatch(r'[A-Za-z0-9]',p['key']): raise ValueError('One letter/digit hotkey with boolean modifiers required')
        if 'shelf' in p and (not isinstance(p['shelf'],str) or not p['shelf']): raise ValueError('Explicit shelf required')
    else:
        p.setdefault('custom_names',True)
        if type(p['custom_names']) is not bool: raise ValueError('Boolean naming option required')
        for key in ('objects','components'):
            if key in p and (not isinstance(p[key],list) or not p[key] or any(not isinstance(v,str) or not v for v in p[key]) or len(p[key])!=len(set(p[key]))): raise ValueError('Nonempty unique explicit selection required')
    return p


def exact(value,readonly=False):
    from maya import cmds
    from maya.api import OpenMaya as om
    if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Exact whole DAG node required')
    values=cmds.ls(value,long=True) or []
    if len(values)!=1: raise ValueError('Missing/ambiguous node')
    n=values[0]; selection=om.MSelectionList(); selection.add(n); obj=selection.getDependNode(0)
    if not obj.hasFn(om.MFn.kDagNode) or not readonly and len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('Non-instanced writable DAG required')
    if not readonly and (cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or [])): raise ValueError('Referenced/locked writable input')
    return n


def mesh(value,readonly=False):
    from maya import cmds
    n=exact(value,readonly)
    if cmds.nodeType(n)=='mesh': n=exact(n.rsplit('|',1)[0],readonly)
    if cmds.nodeType(n)!='transform': raise ValueError('Mesh transform required')
    if not readonly and cmds.listRelatives(n,children=True,fullPath=True,type='transform'): raise ValueError('Writable mesh input with child transforms unsupported')
    shapes=cmds.listRelatives(n,shapes=True,fullPath=True) or []
    if readonly: shapes=[s for s in shapes if cmds.nodeType(s)=='mesh' and not cmds.getAttr(s+'.intermediateObject')]
    if len(shapes)!=1 or cmds.nodeType(shapes[0])!='mesh' or cmds.getAttr(shapes[0]+'.intermediateObject'): raise ValueError('Exactly one visible mesh shape required')
    exact(shapes[0],readonly)
    for attr in ('inMesh','outMesh','worldMesh'):
        if not readonly and cmds.getAttr(shapes[0]+'.'+attr,lock=True): raise ValueError('Locked mesh data')
    matrix=cmds.xform(n,query=True,matrix=True,worldSpace=True)
    from maya.api import OpenMaya as om
    if abs(om.MMatrix(matrix).det3x3())<1e-12: raise ValueError('Degenerate mesh transform')
    return {'node':n,'shape':shapes[0],'uuid':cmds.ls(n,uuid=True)[0],'shape_uuid':cmds.ls(shapes[0],uuid=True)[0],'parent':(cmds.listRelatives(n,parent=True,fullPath=True) or [None])[0],'pivots':cmds.xform(n,query=True,rotatePivot=True,worldSpace=True)+cmds.xform(n,query=True,scalePivot=True,worldSpace=True)}


def history(rows):
    from maya import cmds
    dag={n for row in rows for n in (row['node'],row['shape'])}
    nodes=set()
    for row in rows:
        upstream=cmds.listConnections(row['shape']+'.inMesh',source=True,destination=False) or []
        values=set(upstream)
        for start in upstream: values.update(cmds.listHistory(start,pruneDagObjects=True) or [])
        # Query the geometry input graph, not shape-wide history: the latter
        # can traverse material membership into shared shading engines.
        for value in values:
            resolved=(cmds.ls(value,long=True) or [value])[0]
            if resolved in dag: continue
            if cmds.objectType(resolved,isAType='dagNode') or not (cmds.nodeType(resolved).startswith('poly') or cmds.nodeType(resolved) in ('groupId','groupParts')): raise ValueError('Only static polygon construction history supported: '+resolved+' ('+cmds.nodeType(resolved)+')')
            if cmds.referenceQuery(resolved,isNodeReferenced=True) or any(cmds.lockNode(resolved,query=True,lock=True) or []): raise ValueError('History referenced/locked')
            nodes.add(resolved)
    owned=dag|nodes
    for n in nodes:
        for value in cmds.listConnections(n,source=False,destination=True) or []:
            resolved=(cmds.ls(value,long=True) or [value])[0]
            if resolved not in owned and not (cmds.nodeType(n)=='groupId' and cmds.nodeType(resolved)=='shadingEngine'): raise ValueError('History has consumer outside selected meshes')
    for row in rows:
        for plug in (row['shape']+'.outMesh',row['shape']+'.worldMesh'):
            if cmds.listConnections(plug,source=False,destination=True): raise ValueError('Mesh geometry has external consumer')
    return sorted(nodes)


def component_scope(values,readonly=False):
    from maya import cmds
    if not values: raise ValueError('Select mesh components')
    source=None; selected=[]
    for value in values:
        match=re.fullmatch(r'(.+)\.(f|e|vtx|map)\[(\d+(?::\d+)?)\]',value)
        if not match or not cmds.objExists(value): raise ValueError('Explicit existing mesh face/edge/vertex/UV component required')
        row=mesh(match[1],readonly)
        if source and row['uuid']!=source['uuid']: raise ValueError('One mesh component source required')
        source=row; selected.append(value)
    faces=cmds.ls(cmds.polyListComponentConversion(selected,toFace=True),flatten=True,long=True) or []
    indices=sorted({int(value.rsplit('[',1)[1][:-1]) for value in faces})
    if not indices: raise ValueError('Components converted to no faces')
    count=cmds.polyEvaluate(source['shape'],face=True)
    if any(index>=count for index in indices): raise ValueError('Invalid face index')
    return source,indices,count


def unique_name(base):
    from maya import cmds
    name=base; i=1
    while cmds.objExists(':'+name): name=base+'_'+str(i); i+=1
    return ':'+name


def plan(p):
    from maya import cmds
    if p['action'] in ('shelf','hotkey'):
        from .install import preflight
        return preflight(p)
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    if p['action'] in ('extract','duplicate'):
        row,indices,count=component_scope(p.get('components') or cmds.ls(selection=True,long=True,flatten=True) or [],p['action']=='duplicate')
        owned=[] if p['action']=='duplicate' else history([row])
        if p['action']=='extract' and len(indices)==count: raise ValueError('Extract all faces refused; duplicate or explicitly move whole mesh')
        return {'rows':[row],'history':owned,'face_indices':indices,'face_count':count}
    values=p.get('objects') or cmds.ls(selection=True,long=True) or []
    if not values: raise ValueError('Select mesh objects or combine groups')
    rows=[]; ids=set()
    for value in values:
        n=exact(value)
        candidates=[n]
        if p['action']=='combine' and cmds.nodeType(n)=='transform' and not cmds.listRelatives(n,shapes=True):
            candidates=cmds.listRelatives(n,allDescendents=True,fullPath=True,type='transform') or []
            candidates=[c for c in candidates if cmds.listRelatives(c,shapes=True,type='mesh')]
        for candidate in candidates:
            row=mesh(candidate)
            if row['uuid'] in ids: raise ValueError('Overlapping selection/duplicate mesh alias')
            ids.add(row['uuid']); rows.append(row)
    if p['action']=='combine' and len(rows)<2: raise ValueError('At least two distinct mesh leaves required')
    if p['action']=='separate' and (len(rows)!=1 or cmds.polyEvaluate(rows[0]['shape'],shell=True)<2): raise ValueError('One mesh containing multiple polygon shells required')
    owned=history(rows)
    parent=Counter(row['parent'] for row in rows).most_common(1)[0][0]
    if parent and (cmds.referenceQuery(parent,isNodeReferenced=True) or any(cmds.lockNode(parent,query=True,lock=True) or [])): raise ValueError('Destination parent referenced/locked')
    return {'rows':rows,'history':owned,'destination_parent':parent}


class SmartMeshTool(BaseMayaTool):
    tool_id='smart_mesh'; tool_name='SmartMesh Tools'; category='modeling_surfacing'; version='1.1.0-candidate.1'
    description='完整Smart Combine/Separate/Extract/Duplicate Face，精确静态网格及历史范围，保留无关组/材质/UV/原pivot，完整UI/显式转正后shelf与hotkey安装。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        p=normalize(kwargs); scope=plan(p)
        if p['action'] in ('shelf','hotkey'):
            from .install import execute
            return ToolResult.ok(data=execute(p,scope))
        rows=scope['rows']; action=p['action']; original_uuids=set(cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or [])
        auto=cmds.autoKeyframe(query=True,state=True)
        try:
            cmds.autoKeyframe(state=False)
            if action=='combine':
                result=cmds.polyUnite(*[r['node'] for r in rows],constructionHistory=False,mergeUVSets=1,name=unique_name('SmartCombine_0') if p['custom_names'] else ':polySurface')[0]
                cmds.delete(result,constructionHistory=True); cmds.xform(result,centerPivots=True)
                for row in rows:
                    for n in cmds.ls(row['uuid'],long=True) or []: cmds.delete(n)
                parent=scope['destination_parent']
                if parent: result=cmds.parent(result,parent,absolute=True)[0]
                outputs=[result]
            elif action=='separate':
                row=rows[0]; result=cmds.polySeparate(row['node'],constructionHistory=False)
                outputs=[n for n in result if cmds.objExists(n) and cmds.nodeType(n)=='transform']
                if len(outputs)<2: raise RuntimeError('Maya returned no separate shells')
                for i,n in enumerate(outputs):
                    cmds.delete(n,constructionHistory=True)
                    parent=row['parent']; n=cmds.parent(n,parent,absolute=True)[0] if parent else cmds.parent(n,world=True,absolute=True)[0]
                    if p['custom_names']:
                        base=re.split(r'_(?:Sep|Dup|Ext)_',row['node'].split('|')[-1])[0]
                        n=cmds.rename(n,unique_name(base+'_Sep_'+str(i+1)))
                    cmds.xform(n,worldSpace=True,rotatePivot=row['pivots'][:3],scalePivot=row['pivots'][3:]); outputs[i]=n
                for n in cmds.ls(row['uuid'],long=True) or []: cmds.delete(n)
            else:
                row=rows[0]; base=re.split(r'_(?:Sep|Dup|Ext)_',row['node'].split('|')[-1])[0]
                option={'name':unique_name(base+('_Ext_1' if action=='extract' else '_Dup_1'))} if p['custom_names'] else {}
                result=cmds.duplicate(row['node'],returnRootsOnly=True,upstreamNodes=False,inputConnections=False,**option)[0]
                for n in [result]+(cmds.listRelatives(result,allDescendents=True,fullPath=True) or []):
                    if cmds.ls(n,uuid=True)[0] in original_uuids: raise RuntimeError('Duplicate unexpectedly reused source nodes; refuse cleanup')
                    cmds.lockNode(n,lock=False)
                for n in cmds.listRelatives(result,children=True,fullPath=True,type='transform') or []: cmds.delete(n)
                for n in cmds.listRelatives(result,shapes=True,fullPath=True) or []:
                    if cmds.nodeType(n)!='mesh' or cmds.getAttr(n+'.intermediateObject'): cmds.delete(n)
                    else:
                        for attr in ('inMesh','outMesh','worldMesh'): cmds.setAttr(n+'.'+attr,lock=False)
                cmds.delete(result,constructionHistory=True)
                unwanted=sorted(set(range(scope['face_count']))-set(scope['face_indices']))
                if unwanted: cmds.delete([result+'.f[%d]'%i for i in unwanted])
                if action=='extract': cmds.delete([row['node']+'.f[%d]'%i for i in scope['face_indices']])
                outputs=[result]
            # Delete only validated exclusive polygon history left orphaned by
            # combine/separate. Extract keeps the source construction graph.
            if action in ('combine','separate'):
                for n in scope['history']:
                    if cmds.objExists(n) and not cmds.listConnections(n,source=False,destination=True): cmds.delete(n)
            cmds.select(outputs,replace=True)
            outputs=cmds.ls(outputs,long=True)
            return ToolResult.ok(data={'action':action,'inputs':rows,'outputs':outputs,'output_uuids':[cmds.ls(n,uuid=True)[0] for n in outputs],'created_uuids':[cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or [] if cmds.ls(n,uuid=True)[0] not in original_uuids]})
        finally: cmds.autoKeyframe(state=auto)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show
        return show(self)
