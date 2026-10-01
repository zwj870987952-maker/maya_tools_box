"""Complete paired-target corrective animation engine, independent of the original UI."""
import copy
import hashlib
import json
import math
import re
import uuid

import maya.cmds as cmds

OWNER = 'mtkSATOwner'
ROLE = 'mtkSATRole'
BRAND = 'shape_animation_tool_candidate_v1'
DATA = 'mtkSATData'


def uid(node):
    names = cmds.ls(node, uuid=True) or []
    if len(names) != 1:
        raise ValueError('Node must be unambiguous: '+str(node))
    return names[0]


def resolve(identity):
    nodes = cmds.ls(identity, long=True) or []
    if len(nodes) != 1:
        raise ValueError('Missing or ambiguous UUID: '+str(identity))
    return nodes[0]


def canonical_plug(name):
    import maya.api.OpenMaya as om
    selection=om.MSelectionList()
    selection.add(name)
    plug=selection.getPlug(0)
    return (om.MFnDependencyNode(plug.node()).uuid().asString(),plug.partialName(False,True,True,False,True,True))


def same_connections(actual,expected):
    return sorted(canonical_plug(p) for p in (actual or []))==sorted(canonical_plug(p) for p in expected)


def time_curve(curve):
    inputs=cmds.listConnections(curve+'.input',source=True,destination=False,plugs=True) or []
    # Maya-created animCurveT* normally evaluates context time implicitly with
    # no input connection. Explicit ordinary time1 outputs are valid too.
    return not inputs or same_connections(inputs,['time1.outTime']) or same_connections(inputs,['time1.unwarpedTime'])


def editable(node, attrs=()):
    if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []):
        raise ValueError('Referenced/locked node: '+node)
    for a in attrs:
        if cmds.getAttr(node+'.'+a,lock=True):
            raise ValueError('Locked attribute: '+node+'.'+a)


def mesh_node(node):
    names = cmds.ls(node, long=True) or []
    if len(names)!=1 or '.' in names[0]:
        raise ValueError('Select one whole mesh or its transform')
    node = names[0]
    if cmds.nodeType(node)=='mesh':
        parents = cmds.listRelatives(node,parent=True,fullPath=True) or []
        if len(parents)!=1:
            raise ValueError('Instanced mesh is unsupported')
        node = parents[0]
    if cmds.nodeType(node)!='transform':
        raise ValueError('Expected a mesh transform')
    shapes = cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True,type='mesh') or []
    children = cmds.listRelatives(node,children=True,fullPath=True) or []
    if len(shapes)!=1 or any(cmds.nodeType(p)!='mesh' for p in children):
        raise ValueError('Exactly one visible mesh and no child transforms are required')
    if len(cmds.ls(shapes[0],allPaths=True,long=True) or [])!=1:
        raise ValueError('Instanced mesh is unsupported')
    editable(node,('lodVisibility',))
    editable(shapes[0],('inMesh',))
    return node,shapes[0]


def shape(node):
    values = cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True,type='mesh') or []
    if len(values)!=1:
        raise ValueError('Expected one owned mesh shape: '+node)
    return values[0]


def topology(node):
    import maya.api.OpenMaya as om
    selection=om.MSelectionList()
    selection.add(node)
    fn=om.MFnMesh(selection.getDagPath(0))
    counts,vertices=fn.getVertices()
    return hashlib.sha256(json.dumps([fn.numVertices,list(counts),list(vertices)],separators=(',',':')).encode()).hexdigest()


def owned(node, session, role=None):
    if not cmds.attributeQuery(OWNER,node=node,exists=True) or cmds.getAttr(node+'.'+OWNER)!=session:
        raise ValueError('Refuse to modify an unowned node: '+node)
    if role and (not cmds.attributeQuery(ROLE,node=node,exists=True) or cmds.getAttr(node+'.'+ROLE)!=role):
        raise ValueError('Wrong owned node role: '+node)
    editable(node)
    return node


def mark(node, session, role):
    if cmds.attributeQuery(OWNER,node=node,exists=True):
        raise ValueError('Node already has an owner')
    for attr,value in ((OWNER,session),(ROLE,role)):
        cmds.addAttr(node,longName=attr,dataType='string')
        cmds.setAttr(node+'.'+attr,value,type='string',lock=True)


def snapshot_scene():
    return {'selection':cmds.ls(selection=True,long=True) or [],'time':cmds.currentTime(query=True),'namespace':cmds.namespaceInfo(currentNamespace=True),'autokey':cmds.autoKeyframe(query=True,state=True)}


def restore_scene(snap, time=True, selection=True):
    cmds.namespace(setNamespace=snap['namespace'])
    cmds.autoKeyframe(state=snap['autokey'])
    if time:
        cmds.currentTime(snap['time'])
    if selection:
        nodes = [n for n in snap['selection'] if cmds.objExists(n)]
        cmds.select(nodes,replace=True) if nodes else cmds.select(clear=True)


class Engine:
    def __init__(self, session=None):
        if session:
            nodes = cmds.ls(session,long=True) or []
        else:
            nodes = [n for n in cmds.ls(type='network') or [] if cmds.attributeQuery(OWNER,node=n,exists=True) and cmds.getAttr(n+'.'+OWNER)==BRAND]
        if len(nodes)>1:
            raise ValueError('Multiple sessions; supply session UUID/name')
        self.node = nodes[0] if nodes else None
        if session and not self.node:
            raise ValueError('Session not found')
        if self.node:
            owned(self.node,BRAND,'session')
            self.sid = uid(self.node)
            self.data = json.loads(cmds.getAttr(self.node+'.'+DATA))
            if self.data.get('version')!=1 or not isinstance(self.data.get('layers'),list):
                raise ValueError('Invalid candidate session data')
        else:
            self.sid = None
            self.data = {'version':1,'layers':[],'current':None,'editing':None}
        self.temporary = []

    def save(self):
        if not self.node:
            self.node = cmds.createNode('network',name=':mtkSATSession_'+uuid.uuid4().hex[:12],skipSelect=True)
            mark(self.node,BRAND,'session')
            cmds.addAttr(self.node,longName=DATA,dataType='string')
            self.sid = uid(self.node)
        owned(self.node,BRAND,'session')
        cmds.setAttr(self.node+'.'+DATA,json.dumps(self.data,ensure_ascii=False,allow_nan=False),type='string')

    def layer(self, identity=None):
        ident = identity or self.data.get('current')
        records = [r for r in self.data['layers'] if r['id']==ident]
        if len(records)!=1:
            raise ValueError('Layer not found; add a mesh first or supply layer_id')
        return records[0]

    def state(self):
        return {'session':self.sid,'session_node':self.node,'layers':copy.deepcopy(self.data['layers']),'editing':copy.deepcopy(self.data['editing'])}

    def graph(self,r):
        mesh,msh = mesh_node(resolve(r['mesh']))
        if int(cmds.polyEvaluate(msh,vertex=True))!=r['vertices'] or topology(msh)!=r['topology']:
            raise ValueError('Mesh topology changed; restore the original topology')
        if not r.get('bs'):
            return mesh,msh,None
        bs = owned(resolve(r['bs']),self.sid,'deformer')
        if cmds.nodeType(bs)!='blendShape' or not cmds.blendShape(bs,query=True,geometry=True):
            raise ValueError('Invalid owned blendShape')
        outputs = cmds.blendShape(bs,query=True,geometry=True) or []
        if len(outputs)!=1 or uid(outputs[0])!=uid(msh):
            raise ValueError('Deformer geometry was reassigned or shared')
        editable(bs,('envelope',))
        if not cmds.getAttr(bs+'.supportNegativeWeights'):
            raise ValueError('Enable supportNegativeWeights on the owned corrective blendShape')
        allowed = {uid(mesh),uid(msh),self.sid,r['bs']}
        for p in r['pairs']:
            mult = owned(resolve(p['mult']),self.sid,'negative_weight')
            allowed.add(uid(mult))
            curve = owned(resolve(p['curve']),self.sid,'weight_curve')
            allowed.add(uid(curve))
            if cmds.nodeType(curve)!='animCurveTU' or cmds.nodeType(mult)!='multDoubleLinear':
                raise ValueError('Invalid paired target driver')
            if not time_curve(curve):
                raise ValueError('Weight curve has a non-time driver')
            if not same_connections(cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True),[bs+'.weight[%s]'%p['positive']]):
                raise ValueError('Weight curve is shared/reconnected')
            if not same_connections(cmds.listConnections(mult+'.input1',source=True,destination=False,plugs=True),[bs+'.weight[%s]'%p['positive']]) or not same_connections(cmds.listConnections(mult+'.output',source=False,destination=True,plugs=True),[bs+'.weight[%s]'%p['negative']]):
                raise ValueError('Paired target weight graph changed')
            if cmds.getAttr(mult+'.input2')!=-1 or cmds.listConnections(mult+'.input2',source=True,destination=False):
                raise ValueError('Negative weight multiplier changed')
            for index in (p['negative'],p['positive']):
                plug = bs+'.weight[%s]'%index
                if cmds.getAttr(plug,lock=True):
                    raise ValueError('Locked target weight')
                expected = [mult+'.input1'] if index==p['positive'] else []
                if not same_connections(cmds.listConnections(plug,source=False,destination=True,plugs=True),expected):
                    raise ValueError('Target weight is used outside its own negative pair')
            for node in (mult,curve):
                for consumer in cmds.listConnections(node,source=False,destination=True) or []:
                    if uid(consumer) not in allowed:
                        raise ValueError('Owned driver is used outside this layer')
        indices = set(cmds.getAttr(bs+'.weight',multiIndices=True) or [])
        expected = {p[k] for p in r['pairs'] for k in ('negative','positive')}
        if indices!=expected:
            raise ValueError('Untracked blendShape targets; refuse destructive modification')
        for connection in cmds.listConnections(bs+'.envelope',source=True,destination=False) or []:
            raise ValueError('Envelope has an external driver: '+connection)
        if cmds.listConnections(bs+'.envelope',source=False,destination=True):
            raise ValueError('Envelope is shared with another node')
        # Support a coherent retime of the full weight curves without relying on
        # stale Python/cache metadata. Read-only preflight updates only its copy.
        frame_sets=[]
        for p in r['pairs']:
            curve=resolve(p['curve'])
            times=cmds.keyframe(curve,query=True,timeChange=True) or []
            values=cmds.keyframe(curve,query=True,valueChange=True) or []
            active=[t for t,v in zip(times,values) if abs(v-1)<1e-7]
            if len(active)!=1 or any(min(abs(v),abs(v-1))>1e-7 for v in values):
                raise ValueError('Corrective weight keys must contain one unit key and zero keys at the other target frames')
            p['frame']=active[0]
            frame_sets.append(set(times))
        frames={p['frame'] for p in r['pairs']}
        if len(frames)!=len(r['pairs']) or any(s!=frames for s in frame_sets):
            raise ValueError('Weight curve key times disagree; retime all layer weight curves together')
        r['pairs'].sort(key=lambda p:p['frame'])
        for p in r['pairs']:
            for index in (p['negative'],p['positive']):
                incoming = cmds.listConnections(self.target_plug(bs,index),source=True,destination=False,shapes=True) or []
                edit = self.data['editing']
                if incoming and not (edit and edit['layer']==r['id'] and index==edit['positive'] and len(incoming)==1 and uid(cmds.listRelatives(incoming[0],parent=True,fullPath=True)[0])==edit['sculpt']):
                    raise ValueError('Target geometry has an external connection')
        return mesh,msh,bs

    @staticmethod
    def target_plug(bs,index):
        return bs+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget'%index

    def clone(self,mesh):
        name = cmds.duplicate(mesh,name=':mtkSATTemp_'+uuid.uuid4().hex[:12],returnRootsOnly=True)[0]
        identity = uid(name)
        self.temporary.append(identity)
        mark(name,self.sid,'temporary_mesh')
        for attr in ('tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility','lodVisibility'):
            cmds.setAttr(name+'.'+attr,lock=False)
        cmds.delete(name,constructionHistory=True)
        for child in cmds.listRelatives(name,shapes=True,fullPath=True,type='mesh') or []:
            if cmds.getAttr(child+'.intermediateObject'):
                cmds.delete(child)
        if cmds.listRelatives(name,parent=True):
            cmds.parent(name,world=True)
        name = resolve(identity)
        cmds.setAttr(name+'.visibility',1)
        cmds.setAttr(name+'.lodVisibility',1)
        return name

    def delete_owned(self,node,role=None):
        owned(node,self.sid,role)
        if cmds.objectType(node,isAType='dagNode'):
            descendants = cmds.listRelatives(node,allDescendents=True,fullPath=True) or []
            if len(descendants)!=1 or any(cmds.nodeType(n)!='mesh' for n in descendants):
                raise ValueError('Owned temporary has unexpected added children; preserve it')
            for msh in descendants:
                editable(msh)
                inputs = cmds.listConnections(msh+'.inMesh',source=True,destination=False) or []
                if inputs:
                    raise ValueError('Owned temporary has user-added history; preserve it')
        cmds.delete(node)

    def cleanup(self):
        errors = []
        for identity in list(self.temporary):
            try:
                nodes = cmds.ls(identity,long=True) or []
                if nodes:
                    self.delete_owned(nodes[0],'temporary_mesh')
                self.temporary.remove(identity)
            except Exception as exc:
                errors.append(str(exc))
        if errors:
            raise RuntimeError('Temporary cleanup failed: '+'; '.join(errors))

    def add(self,mesh):
        transform,msh = mesh_node(mesh)
        if not self.node:
            self.save()
        label = transform.rsplit('|',1)[-1]+'_LR'
        i = 1
        while any(r['label']==label+str(i) for r in self.data['layers']):
            i += 1
        row = {'id':uuid.uuid4().hex,'mesh':uid(transform),'label':label+str(i),'bs':None,'pairs':[],'vertices':int(cmds.polyEvaluate(msh,vertex=True)),'topology':topology(msh)}
        self.data['layers'].append(row)
        self.data['current'] = row['id']
        self.save()
        return row

    def create_bs(self,r,mesh):
        bs = cmds.blendShape(mesh,name=':mtkSATBS_'+r['id'][:12],origin='local')[0]
        mark(bs,self.sid,'deformer')
        # Negative baseline target must actually subtract from the positive target.
        cmds.setAttr(bs+'.supportNegativeWeights',True)
        r['bs'] = uid(bs)
        return bs

    def set_key(self,r):
        mesh,_,bs = self.graph(r)
        frame = float(cmds.currentTime(query=True))
        if any(p['frame']==frame for p in r['pairs']):
            return
        used = {p[k] for p in r['pairs'] for k in ('negative','positive')}
        negative = next(i for i in range(len(used)+1) if i not in used)
        positive = next(i for i in range(negative+1,len(used)+2) if i not in used)
        current = self.clone(mesh)
        envelope = cmds.getAttr(bs+'.envelope') if bs else None
        try:
            if bs:
                cmds.setAttr(bs+'.envelope',0)
            baseline = self.clone(mesh)
        finally:
            if bs:
                cmds.setAttr(bs+'.envelope',envelope)
        if not bs:
            bs = self.create_bs(r,mesh)
        cmds.blendShape(bs,edit=True,target=(mesh,negative,baseline,1.0))
        cmds.blendShape(bs,edit=True,target=(mesh,positive,current,1.0))
        for index in (negative,positive):
            cmds.aliasAttr('shape_'+str(index),bs+'.weight[%s]'%index)
        self.cleanup()
        for p in r['pairs']:
            curve = resolve(p['curve'])
            cmds.setKeyframe(curve,time=frame,value=0)
            cmds.keyTangent(curve,edit=True,weightedTangents=True)
            cmds.keyTangent(curve,edit=True,weightedTangents=False)
        plug = bs+'.weight[%s]'%positive
        for p in r['pairs']:
            cmds.setKeyframe(plug,time=p['frame'],value=0)
        cmds.setKeyframe(plug,time=frame,value=1)
        curve = cmds.listConnections(plug,source=True,destination=False,type='animCurve')[0]
        mark(curve,self.sid,'weight_curve')
        mult = cmds.createNode('multDoubleLinear',name=':mtkSATNegative_'+uuid.uuid4().hex[:12],skipSelect=True)
        mark(mult,self.sid,'negative_weight')
        cmds.setAttr(mult+'.input2',-1)
        cmds.connectAttr(plug,mult+'.input1')
        cmds.connectAttr(mult+'.output',bs+'.weight[%s]'%negative)
        r['pairs'].append({'frame':frame,'negative':negative,'positive':positive,'curve':uid(curve),'mult':uid(mult)})
        r['pairs'].sort(key=lambda p:p['frame'])
        self.save()

    def remove_pairs(self,r,pairs):
        mesh,_,bs = self.graph(r)
        if not bs:
            return
        for p in list(pairs):
            # Full original remove-target sequence: reconnect a owned duplicate,
            # remove the actual target item, then delete its own weight drivers.
            for index in (p['negative'],p['positive']):
                temporary = self.clone(mesh)
                cmds.connectAttr(shape(temporary)+'.worldMesh[0]',self.target_plug(bs,index))
                cmds.blendShape(bs,edit=True,remove=True,target=(mesh,index,temporary,1.0))
                self.cleanup()
            self.delete_owned(resolve(p['mult']),'negative_weight')
            self.delete_owned(resolve(p['curve']),'weight_curve')
            r['pairs'].remove(p)
            for index in (p['negative'],p['positive']):
                cmds.removeMultiInstance(bs+'.weight[%s]'%index,b=True)
            for other in r['pairs']:
                cmds.cutKey(resolve(other['curve']),time=(p['frame'],p['frame']),clear=True)
        self.save()

    def begin(self,r):
        snap = snapshot_scene()
        self.set_key(r)
        mesh,_,bs = self.graph(r)
        if not cmds.getAttr(bs+'.envelope'):
            raise ValueError('Cannot sculpt a disabled layer')
        frame = float(cmds.currentTime(query=True))
        pair = next(p for p in r['pairs'] if p['frame']==frame)
        helper = self.clone(mesh)
        identity = uid(helper)
        old_visibility = cmds.getAttr(mesh+'.lodVisibility')
        plug = self.target_plug(bs,pair['positive'])
        try:
            cmds.connectAttr(shape(helper)+'.worldMesh[0]',plug)
            cmds.setAttr(mesh+'.lodVisibility',False)
            self.data['editing'] = {'layer':r['id'],'sculpt':identity,'frame':frame,'positive':pair['positive'],'old_visibility':old_visibility,'selection':snap['selection'],'context':cmds.currentCtx(),'component':bool(cmds.selectMode(query=True,component=True))}
            self.save()
            self.temporary.remove(identity)  # Persistent across sculpt calls and scene saves.
            cmds.select(helper,replace=True)
            return helper
        except Exception:
            if cmds.isConnected(shape(helper)+'.worldMesh[0]',plug):
                cmds.disconnectAttr(shape(helper)+'.worldMesh[0]',plug)
            cmds.setAttr(mesh+'.lodVisibility',old_visibility)
            self.data['editing'] = None
            raise

    def finish(self,r):
        edit = self.data['editing']
        helper = owned(resolve(edit['sculpt']),self.sid,'temporary_mesh')
        mesh,_,bs = self.graph(r)
        # Maya stores the connected target's geometry when its own source is deleted,
        # exactly as in the complete original sculpt-off implementation.
        self.delete_owned(helper,'temporary_mesh')
        cmds.setAttr(mesh+'.lodVisibility',edit['old_visibility'])
        cmds.selectMode(component=edit['component']) if edit['component'] else cmds.selectMode(object=True)
        try:
            cmds.setToolTo(edit['context'])
        except RuntimeError:
            cmds.setToolTo('selectSuperContext')
        nodes = [n for n in edit['selection'] if cmds.objExists(n)]
        cmds.select(nodes,replace=True) if nodes else cmds.select(clear=True)
        self.data['editing'] = None
        self.save()

    def reset(self,r):
        edit = self.data['editing']
        helper = owned(resolve(edit['sculpt']),self.sid,'temporary_mesh')
        mesh,_,bs = self.graph(r)
        old_time = cmds.currentTime(query=True)
        envelope = cmds.getAttr(bs+'.envelope')
        try:
            cmds.currentTime(edit['frame'])
            cmds.setAttr(bs+'.envelope',0)
            baseline = self.clone(mesh)
        finally:
            cmds.setAttr(bs+'.envelope',envelope)
            cmds.currentTime(old_time)
        if cmds.listConnections(shape(helper)+'.inMesh',source=True,destination=False):
            raise ValueError('Temporary sculpt mesh has added history; undo it before reset')
        # Full original reset: baseline -> temporary sculpt blendShape, bake only
        # this owned helper's history, remove the owned baseline afterward.
        reset = cmds.blendShape(baseline,helper,topologyCheck=True,name=':mtkSATReset_'+uuid.uuid4().hex[:12])[0]
        cmds.setAttr(reset+'.weight[0]',1)
        cmds.delete(helper,constructionHistory=True)
        self.cleanup()

    def remove(self,r):
        self.graph(r)
        if r.get('bs'):
            self.delete_owned(resolve(r['bs']),'deformer')
        for p in r['pairs']:
            for k,role in (('mult','negative_weight'),('curve','weight_curve')):
                values = cmds.ls(p[k],long=True) or []
                if values:
                    self.delete_owned(values[0],role)
        self.data['layers'].remove(r)
        self.data['current'] = self.data['layers'][-1]['id'] if self.data['layers'] else None
        self.save()


def inspect_legacy(node='sat'):
    from .utils import attrToPy
    if not cmds.objExists(node) or cmds.nodeType(node)!='network':
        raise ValueError('Legacy SAT network not found')
    layers = attrToPy(node+'.meshes')
    if not isinstance(layers,list) or any(not isinstance(n,str) for n in layers):
        raise ValueError('Invalid legacy mesh list')
    editing = attrToPy(node+'.sculptMode') if cmds.objExists(node+'.sculptMode') else False
    if editing:
        raise ValueError('Finish editing in original SAT first, save a backup, then adopt')
    records = []
    for label in layers:
        name = re.sub(r'_LR\d+$','',label)
        mesh,msh = mesh_node(name)
        bs_values = cmds.ls(label+'_satBS') or []
        if len(bs_values)>1:
            raise ValueError('Ambiguous legacy deformer')
        bs = bs_values[0] if bs_values else None
        pairs = []
        if bs:
            editable(bs,('envelope','supportNegativeWeights'))
            if cmds.attributeQuery(OWNER,node=bs,exists=True):
                raise ValueError('Legacy layer already adopted')
            geometry = cmds.blendShape(bs,query=True,geometry=True) or []
            if len(geometry)!=1 or uid(geometry[0])!=uid(msh):
                raise ValueError('Legacy blendShape geometry mismatch')
            aliases = cmds.aliasAttr(bs,query=True) or []
            names = dict(zip(aliases[::2],aliases[1::2]))
            for alias,plug in names.items():
                if not re.fullmatch(r'shape_\d+',alias):
                    raise ValueError('Unexpected legacy target alias')
            used = set()
            for alias,plug in names.items():
                inputs = cmds.listConnections(bs+'.'+plug,source=True,destination=False) or []
                if len(inputs)==1 and cmds.nodeType(inputs[0])=='animCurveTU':
                    curve = inputs[0]
                    editable(curve)
                    if cmds.attributeQuery(OWNER,node=curve,exists=True):
                        raise ValueError('Already owned legacy curve')
                    positive = int(alias.split('_')[-1])
                    mults = cmds.listConnections(bs+'.'+plug,source=False,destination=True,type='multDoubleLinear') or []
                    if len(mults)!=1:
                        raise ValueError('Missing legacy negative weight multiplier')
                    mult = mults[0]
                    editable(mult)
                    if cmds.attributeQuery(OWNER,node=mult,exists=True) or cmds.getAttr(mult+'.input2')!=-1 or cmds.listConnections(mult+'.input2',source=True,destination=False):
                        raise ValueError('Invalid legacy multiplier')
                    output = cmds.listConnections(mult+'.output',source=False,destination=True,plugs=True) or []
                    canonical=canonical_plug(output[0]) if len(output)==1 else None
                    if not canonical or canonical[0]!=uid(bs) or not re.fullmatch(r'weight\[\d+\]',canonical[1]):
                        raise ValueError('Shared or invalid legacy multiplier')
                    negative = int(canonical[1].split('[')[-1].split(']')[0])
                    if not same_connections(cmds.listConnections(mult+'.input1',source=True,destination=False,plugs=True),[bs+'.weight[%s]'%positive]):
                        raise ValueError('Legacy multiplier has a different weight driver')
                    if not time_curve(curve) or not same_connections(cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True),[bs+'.weight[%s]'%positive]):
                        raise ValueError('Shared or non-time legacy curve')
                    if not same_connections(cmds.listConnections(bs+'.weight[%s]'%positive,source=False,destination=True,plugs=True),[mult+'.input1']) or cmds.listConnections(bs+'.weight[%s]'%negative,source=False,destination=True):
                        raise ValueError('Shared legacy target weight')
                    times = cmds.keyframe(curve,query=True,timeChange=True) or []
                    values = cmds.keyframe(curve,query=True,valueChange=True) or []
                    active = [t for t,v in zip(times,values) if abs(v-1)<1e-7]
                    if len(active)!=1 or used.intersection((negative,positive)):
                        raise ValueError('Unrecognized legacy key pair')
                    used.update((negative,positive))
                    pairs.append({'frame':active[0],'negative':negative,'positive':positive,'curve':uid(curve),'mult':uid(mult)})
            if used != set(cmds.getAttr(bs+'.weight',multiIndices=True) or []):
                raise ValueError('Untracked legacy targets')
            frames={p['frame'] for p in pairs}
            if len(frames)!=len(pairs):
                raise ValueError('Duplicate legacy corrective key frames')
            for p in pairs:
                curve=resolve(p['curve'])
                times=cmds.keyframe(curve,query=True,timeChange=True) or []
                values=cmds.keyframe(curve,query=True,valueChange=True) or []
                if set(times)!=frames or any(min(abs(v),abs(v-1))>1e-7 for v in values):
                    raise ValueError('Legacy weight keys are not coherent zero/unit target pairs')
            if cmds.listConnections(bs+'.envelope',source=True,destination=False) or cmds.listConnections(bs+'.envelope',source=False,destination=True):
                raise ValueError('Driven legacy envelope')
            for i in used:
                if cmds.getAttr(bs+'.weight[%s]'%i,lock=True) or cmds.listConnections(Engine.target_plug(bs,i),source=True,destination=False):
                    raise ValueError('Locked weight or connected legacy target')
        records.append({'id':uuid.uuid4().hex,'mesh':uid(mesh),'label':label,'bs':uid(bs) if bs else None,'pairs':sorted(pairs,key=lambda p:p['frame']),'vertices':int(cmds.polyEvaluate(msh,vertex=True)),'topology':topology(msh)})
    return records


def preflight(options):
    engine = Engine(options.get('session'))
    action = options['action']
    if engine.node:
        editable(engine.node,(DATA,))
    if action=='status':
        return engine,None
    if action=='inspect_legacy':
        return engine,inspect_legacy(options.get('legacy_node','sat'))
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Maya Undo before modifying the scene')
    if action=='adopt_legacy':
        if engine.data['editing'] or engine.data['layers']:
            raise ValueError('Adopt legacy data into an empty session only')
        return engine,inspect_legacy(options.get('legacy_node','sat'))
    editing = engine.data['editing']
    if editing and action not in ('end_sculpt','reset_shape'):
        raise ValueError('Finish the pending sculpt before another scene operation')
    if action in ('end_sculpt','reset_shape'):
        if not editing:
            raise ValueError('No pending sculpt')
        r = engine.layer(options.get('layer_id') or editing['layer'])
        if r['id']!=editing['layer']:
            raise ValueError('Wrong editing layer')
        helper = owned(resolve(editing['sculpt']),engine.sid,'temporary_mesh')
        if topology(shape(helper))!=r['topology']:
            raise ValueError('Sculpt mesh topology changed; undo topology edits before finishing')
        if cmds.listConnections(shape(helper)+'.inMesh',source=True,destination=False):
            raise ValueError('Remove user-added sculpt history before finishing/resetting')
        descendants=cmds.listRelatives(helper,allDescendents=True,fullPath=True) or []
        if len(descendants)!=1 or any(cmds.nodeType(n)!='mesh' for n in descendants):
            raise ValueError('Remove user-added helper children before finishing/resetting')
    elif action=='add_mesh':
        selected = cmds.ls(selection=True,long=True) or []
        value = options.get('mesh')
        if value is None:
            if len(selected)!=1:
                raise ValueError('Supply mesh or select exactly one mesh')
            value = selected[0]
        return engine,mesh_node(value)[0]
    elif action=='remove_all':
        for r in engine.data['layers']:
            engine.graph(r)
        return engine,None
    else:
        r = engine.layer(options.get('layer_id'))
    mesh,_,bs = engine.graph(r)
    if action=='begin_sculpt':
        if cmds.listConnections(mesh+'.lodVisibility',source=True,destination=False):
            raise ValueError('Driven mesh LOD visibility cannot be temporarily changed')
        if bs and cmds.getAttr(bs+'.envelope')!=1:
            raise ValueError('Enable layer envelope fully before sculpting')
    return engine,r


def execute(options):
    engine,value = preflight(options)
    action = options['action']
    if action in ('status','inspect_legacy'):
        return engine.state() if action=='status' else {'legacy_layers':value}
    snap = snapshot_scene()
    succeeded = False
    try:
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        if 'frame' in options:
            cmds.currentTime(options['frame'])
        if action=='add_mesh':
            added = engine.add(value)
            out = {'added_layer':added['id']}
        elif action=='adopt_legacy':
            engine.save()
            for r in value:
                if r['bs']:
                    mark(resolve(r['bs']),engine.sid,'deformer')
                    cmds.setAttr(resolve(r['bs'])+'.supportNegativeWeights',True)
                    for p in r['pairs']:
                        mark(resolve(p['curve']),engine.sid,'weight_curve')
                        mark(resolve(p['mult']),engine.sid,'negative_weight')
            engine.data['layers']=value
            engine.data['current']=value[-1]['id'] if value else None
            engine.save()
            out = {'adopted_layers':len(value),'legacy_network_unchanged':options.get('legacy_node','sat')}
        elif action=='remove_all':
            for r in list(engine.data['layers']):
                engine.remove(r)
            out = {}
        else:
            r = value
            if action=='set_key':
                engine.set_key(r)
            elif action=='delete_key':
                frame = float(cmds.currentTime(query=True))
                engine.remove_pairs(r,[p for p in r['pairs'] if p['frame']==frame])
            elif action=='delete_all_keys':
                engine.remove_pairs(r,list(r['pairs']))
            elif action=='remove_mesh':
                engine.remove(r)
            elif action=='set_enabled':
                if r['bs']:
                    cmds.setAttr(resolve(r['bs'])+'.envelope',options['enabled'])
            elif action=='begin_sculpt':
                engine.begin(r)
            elif action=='end_sculpt':
                engine.finish(r)
            elif action=='reset_shape':
                engine.reset(r)
            elif action=='step_key':
                frames = sorted(p['frame'] for p in r['pairs'])
                if not frames:
                    raise ValueError('No corrective keys to step through')
                now = cmds.currentTime(query=True)
                if options['direction']=='prev':
                    cmds.currentTime(max((t for t in frames if t<now),default=frames[0]))
                else:
                    cmds.currentTime(min((t for t in frames if t>now),default=frames[-1]))
            if action!='remove_mesh':
                engine.data['current']=r['id']
                engine.save()
            out = {}
        succeeded = True
        out.update(engine.state())
        return out
    finally:
        try:
            engine.cleanup()
        finally:
            restore_scene(snap,time=not (succeeded and action in ('begin_sculpt','step_key')),selection=not (succeeded and action in ('begin_sculpt','end_sculpt')))
