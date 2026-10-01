import hashlib
import json
from pathlib import Path
import re
import uuid
import maya.cmds as cmds
import maya.mel as mel
PKG=Path(__file__).resolve().parent
BRAND="sword_anim_polishing_candidate_v1"
OWNER="mtkSwordCandidateSession"
DATA="mtkSwordCandidateData"
MENU="sword_anim_polish_tool"
VENDOR=PKG/"vendor/sword_anim_polish_tool.mel"


def catalog():
    return json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))

def resources():
    for row in catalog()['files']:
        if hashlib.sha256((PKG/'vendor'/row['path']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Vendor resource changed: '+row['path'])

def quote(value):
    return json.dumps(value,ensure_ascii=False)

def array(values):
    return '{'+','.join(quote(v) if isinstance(v,str) else str(v) for v in values)+'}'

def identity(node):
    ids=cmds.ls(node,uuid=True) or []
    if len(ids)!=1:
        raise ValueError('Ambiguous/missing node: '+str(node))
    return ids[0]

def all_uuids():
    # Explicit node arguments are needed for this Maya build's UUID query.
    return {identity(n) for n in cmds.ls(long=True) or []}

def resolve(uid):
    nodes=cmds.ls(uid,long=True) or []
    if len(nodes)!=1:
        raise ValueError('Recorded node no longer resolves: '+uid)
    return nodes[0]

def editable(node,attrs=()):
    if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []):
        raise ValueError('Referenced/locked node: '+node)
    for attr in attrs:
        if cmds.getAttr(node+'.'+attr,lock=True):
            raise ValueError('Locked attribute: '+node+'.'+attr)

def node(value,transform=True):
    if not isinstance(value,str) or not re.fullmatch(r'[|:A-Za-z_\u0080-\uffff][|A-Za-z0-9_:\u0080-\uffff]*',value):
        raise ValueError('Only a whole, unambiguous Maya node name is supported')
    names=cmds.ls(value,long=True) or []
    if len(names)!=1:
        raise ValueError('Missing/ambiguous node: '+value)
    n=names[0]
    if transform and not cmds.objectType(n,isAType='transform'):
        raise ValueError('Select whole transforms, not shapes/components')
    if len(cmds.ls(n,long=True,allPaths=True) or [])!=1:
        raise ValueError('Instanced controls/curves are unsupported')
    editable(n)
    return n

class Ledger:
    def __init__(self,session=None):
        nodes=cmds.ls(session,long=True) if session else [n for n in cmds.ls(type='network') or [] if cmds.attributeQuery(OWNER,node=n,exists=True) and cmds.getAttr(n+'.'+OWNER)==BRAND]
        if not nodes and session:
            raise ValueError('Session not found')
        if len(nodes or [])>1:
            raise ValueError('Multiple sessions; supply session explicitly')
        self.node=nodes[0] if nodes else None
        self.sid=identity(self.node) if self.node else None
        if self.node:
            if cmds.nodeType(self.node)!='network' or not cmds.attributeQuery(OWNER,node=self.node,exists=True) or cmds.getAttr(self.node+'.'+OWNER)!=BRAND:
                raise ValueError('Not a candidate session')
            editable(self.node,(DATA,))
            self.data=json.loads(cmds.getAttr(self.node+'.'+DATA))
            if self.data.get('version')!=1:
                raise ValueError('Invalid session metadata')
        else:
            self.data={'version':1,'owned':[],'inputs':[],'globals':{},'identity_map':{},'pending':None,'layer':None,'objects':[],'failed':None}

    def save(self):
        if not self.node:
            self.node=cmds.createNode('network',name=':mtkSwordSession_'+uuid.uuid4().hex[:12],skipSelect=True)
            cmds.addAttr(self.node,longName=OWNER,dataType='string')
            cmds.setAttr(self.node+'.'+OWNER,BRAND,type='string',lock=True)
            cmds.addAttr(self.node,longName=DATA,dataType='string')
            self.sid=identity(self.node)
        cmds.setAttr(self.node+'.'+DATA,json.dumps(self.data,ensure_ascii=False,allow_nan=False),type='string')

    def state(self):
        return {'session':self.sid,'session_node':self.node,**self.data}

    def restore_globals(self):
        values=dict(self.data['globals'])
        for key in ('eval_mode','my_eval_mode','BARN_eval_mode'):
            values[key]=cmds.evaluationManager(query=True,mode=True)
        values['startTime']=mel.eval('timerX')
        for name,definition in catalog()['globals'].items():
            if name not in values:
                value=[] if definition['array'] else ('' if definition['type']=='string' else 0)
            else:
                value=values[name]
            def remap(v):
                if isinstance(v,str) and v in self.data['identity_map']:
                    return resolve(self.data['identity_map'][v])
                return v
            value=[remap(v) for v in value] if isinstance(value,list) else remap(value)
            literal=array(value) if definition['array'] else (quote(value) if definition['type']=='string' else str(value))
            mel.eval('global '+definition['type']+' $'+name+('[]' if definition['array'] else '')+'; $'+name+'='+literal+';')

    def capture(self,before):
        after=all_uuids()
        self.data['owned']=sorted((set(self.data['owned']) | (after-before))-{self.sid})
        self.data['owned']=[u for u in self.data['owned'] if cmds.ls(u)]
        values={}
        mapping={}
        for name,definition in catalog()['globals'].items():
            declaration='global '+definition['type']+' $'+name+('[]' if definition['array'] else '')+';'
            temporary='$mtkSwordRead_'+name
            value=mel.eval(declaration+' '+definition['type']+' '+temporary+('[]' if definition['array'] else '')+'; '+temporary+'=$'+name+';')
            values[name]=value
            for v in value if isinstance(value,list) else [value]:
                if isinstance(v,str) and v and cmds.objExists(v):
                    mapping[v]=identity(v)
        self.data['globals']=values
        self.data['identity_map']=mapping

def load_vendor():
    resources()
    existing=mel.eval('whatIs '+MENU)
    if existing.startswith('Mel procedure found in:'):
        path=Path(existing.split(':',1)[1].strip())
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=hashlib.sha256(VENDOR.read_bytes()).hexdigest():
            raise ValueError('Another vendor version defines shared MEL procedures; restart Maya rather than overwrite it')
        return
    if existing!='Unknown':
        raise ValueError('Unexpected existing MEL entry: '+existing)
    mel.eval('source '+quote(VENDOR.as_posix())+';')

def snapshot():
    opts={k:cmds.optionVar(query=k) if cmds.optionVar(exists=k) else None for k in ('animBlendingOpt','animBlendBrokenInputOpt','animLayerSelectionKey')}
    value={'time':cmds.currentTime(query=True),'selection':cmds.ls(selection=True,long=True) or [],'namespace':cmds.namespaceInfo(currentNamespace=True),'autokey':cmds.autoKeyframe(query=True,state=True),'linear':cmds.currentUnit(query=True,linear=True),'evaluation':cmds.evaluationManager(query=True,mode=True),'track':cmds.selectPref(query=True,trackSelectionOrder=True),'options':opts,'layers':{identity(l):{k:cmds.animLayer(l,query=True,**{k:True}) for k in ('mute','selected','preferred')} for l in cmds.ls(type='animLayer') or []},'suspended':bool(cmds.refresh(query=True,suspend=True))}
    if not cmds.about(batch=True):
        from maya.plugin.evaluator.cache_preferences import CachePreferenceEnabled
        value['cache']=CachePreferenceEnabled().get_value()
        value['slider']=bool(mel.eval('isTimeSliderVisible()'))
    return value

def restore(value,success,action):
    errors=[]
    def attempt(call):
        try:
            call()
        except Exception as exc:
            errors.append(str(exc))
    attempt(lambda:cmds.namespace(setNamespace=value['namespace']))
    attempt(lambda:cmds.currentUnit(linear=value['linear']))
    attempt(lambda:cmds.autoKeyframe(state=value['autokey']))
    attempt(lambda:cmds.evaluationManager(mode=value['evaluation'][0]))
    attempt(lambda:cmds.selectPref(trackSelectionOrder=value['track']))
    for k,v in value['options'].items():
        attempt(lambda k=k,v=v:cmds.optionVar(remove=k) if v is None else cmds.optionVar(intValue=(k,int(v))))
    if 'cache' in value:
        from maya.plugin.evaluator.cache_preferences import CachePreferenceEnabled
        attempt(lambda:CachePreferenceEnabled().set_value(value['cache']))
    attempt(lambda:cmds.refresh(suspend=False if action=='refresh_viewport' else value['suspended']))
    if 'slider' in value:
        attempt(lambda:mel.eval('setTimeSliderVisible('+str(1 if action=='refresh_viewport' else int(value['slider']))+');'))
    if not success:
        for u,flags in value['layers'].items():
            existing=cmds.ls(u) or []
            if existing:
                for k,v in flags.items():
                    attempt(lambda n=existing[0],k=k,v=v:cmds.animLayer(n,edit=True,**{k:v}))
    attempt(lambda:cmds.currentTime(value['time']))
    # Keep the complete vendor curve/control selection when its next operation
    # needs it; other calls restore the caller's selection.
    if not success or action not in ('create_path','create_circle','curve_controls','arrange_controls','lock_curve','project_curve'):
        nodes=[n for n in value['selection'] if cmds.objExists(n)]
        attempt(lambda:cmds.select(nodes,replace=True) if nodes else cmds.select(clear=True))
    if errors:
        raise RuntimeError('Environment restoration failed: '+'; '.join(errors))
