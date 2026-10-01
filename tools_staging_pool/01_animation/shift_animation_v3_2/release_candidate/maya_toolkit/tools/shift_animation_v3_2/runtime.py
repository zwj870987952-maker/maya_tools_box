"""External adapter only. The full licensed MEL distribution is never rewritten."""
import hashlib
import json
from pathlib import Path
import re
import uuid

import maya.cmds as cmds
import maya.mel as mel

from .tool import LAYER_ACTIONS, PATH_ACTIONS, CURVE_ACTIONS

PKG=Path(__file__).resolve().parent
BRAND='shift_animation_v3_2_candidate_v1'
OWNER='mtkShiftCandidateOwner'
DATA='mtkShiftCandidateData'
MENU='SHIFTING_animation_menue'
VENDOR=PKG/'vendor/barnev_Shift_animation_code.mel'


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
            self.node=cmds.createNode('network',name=':mtkShiftSession_'+uuid.uuid4().hex[:12],skipSelect=True)
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
            temporary='$mtkShiftRead_'+name
            value=mel.eval(declaration+' '+definition['type']+' '+temporary+('[]' if definition['array'] else '')+'; '+temporary+'=$'+name+';')
            values[name]=value
            for v in value if isinstance(value,list) else [value]:
                if isinstance(v,str) and v and cmds.objExists(v):
                    mapping[v]=identity(v)
        self.data['globals']=values
        self.data['identity_map']=mapping


def preflight(options):
    resources()
    ledger=Ledger(options.get('session'))
    action=options['action']
    plan={'action':action,'ledger':ledger,'session':ledger.sid,'scene_write':action not in ('status','analyze_curve','refresh_viewport'),'file_write':False,'layer':None,'objects':[],'attribute_cleanup':{}}
    if action=='status':
        return plan
    if action=='analyze_curve':
        curve=node(options['curve'],transform=False)
        if not cmds.nodeType(curve).startswith('animCurveT') or not cmds.keyframe(curve,query=True,keyframeCount=True):
            raise ValueError('Analysis requires a nonempty time animation curve')
        plan['curve']=curve
        return plan
    if cmds.window('SHIFTING_animation',exists=True):
        raise ValueError('Close original vendor UI; do not run both frontends concurrently')
    if action=='refresh_viewport':
        return plan
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Maya Undo before modifying animation')
    if ledger.data['failed']:
        raise ValueError('Previous vendor call failed; inspect and Undo that call before continuing')
    if ledger.data['pending'] and action in ('auto_path','create_path','create_circle'):
        raise ValueError('Apply the pending path/circle before creating another')
    if action in LAYER_ACTIONS:
        layers=cmds.ls(type='animLayer') or []
        selected=[l for l in layers if cmds.animLayer(l,query=True,selected=True)]
        requested=options.get('layer')
        layer=node(requested,transform=False) if requested else (selected[0] if len(selected)==1 else None)
        if not layer or cmds.nodeType(layer)!='animLayer' or layer==cmds.animLayer(query=True,root=True):
            raise ValueError('Supply a non-base layer or select exactly one non-base layer')
        editable(layer,('mute','weight','selected','preferred'))
        if cmds.animLayer(layer,query=True,lock=True):
            raise ValueError('Input animation layer is locked')
        for l in layers:
            editable(l,('selected','preferred'))
        attrs=cmds.animLayer(layer,query=True,attribute=True) or []
        objects=[]
        for attr in attrs:
            obj=node(attr.rsplit('.',1)[0])
            if obj not in objects:
                objects.append(obj)
        curves=cmds.animLayer(layer,query=True,animCurves=True) or []
        times=cmds.keyframe(curves,query=True,timeChange=True) if curves else []
        if not objects or not times or len(set(times))<2:
            raise ValueError('Layer needs control attributes and at least two keyed frames')
        for curve in curves:
            editable(curve)
        permitted={identity(n) for n in objects+(cmds.animLayer(layer,query=True,blendNodes=True) or [])}
        for curve in curves:
            frontier=cmds.listConnections(curve+'.output',source=False,destination=True) or []
            visited=set()
            while frontier:
                consumer=frontier.pop()
                consumer_id=identity(consumer)
                if consumer_id in visited:
                    continue
                visited.add(consumer_id)
                if consumer_id in permitted:
                    continue
                if cmds.nodeType(consumer) in ('unitConversion','unitToTimeConversion','timeToUnitConversion'):
                    frontier.extend(cmds.listConnections(consumer+'.output',source=False,destination=True) or [])
                else:
                    raise ValueError('Input layer curve has an external/shared consumer: '+consumer)
        if action=='match' and any(t!=int(t) for t in times):
            raise ValueError('Original MATCH casts key intervals to integers; use integer-frame layer keys')
        if action in ('create_path','auto_path') and int(max(times)-min(times)) < options.get('cv_count',5):
            raise ValueError('cv_count is too high for the range; original MEL step would become zero')
        plan.update(layer=layer,objects=objects,frame_range=[min(times),max(times)])
    elif action in PATH_ACTIONS:
        required='circle' if action=='apply_circle' else 'path'
        if ledger.data['pending']!=required:
            raise ValueError('No owned pending '+required+'; create it first')
        plan['layer']=resolve(ledger.data['layer'])
        plan['objects']=[node(resolve(u)) for u in ledger.data['objects']]
        for u in ledger.data['owned']:
            n=resolve(u)
            editable(n)
            if cmds.objectType(n,isAType='dagNode'):
                for child in cmds.listRelatives(n,allDescendents=True,fullPath=True) or []:
                    if identity(child) not in ledger.data['owned']:
                        raise ValueError('Path helper has external children; preserve them and undo the external change')
    if action=='extract' or action in CURVE_ACTIONS or action=='euler_filter':
        names=options.get('objects') or cmds.ls(selection=True,long=True) or []
        if action=='delete_controls' and not names:
            names=[]
        elif not names:
            raise ValueError('Select required whole objects/curves or supply objects')
        plan['objects']=[node(n) for n in names]
        if len({identity(n) for n in plan['objects']})!=len(plan['objects']):
            raise ValueError('Duplicate objects')
    if action in ('lock_curve','unlock_curve','project_curve','curve_controls'):
        expected=2 if action=='project_curve' else 1
        if len(plan['objects'])!=expected:
            raise ValueError('This curve utility requires '+str(expected)+' whole curve(s) in order')
        for obj in plan['objects']:
            children=cmds.listRelatives(obj,shapes=True,fullPath=True) or []
            if not children or any(cmds.nodeType(s)!='nurbsCurve' for s in children):
                raise ValueError('Whole NURBS curves are required')
            for s in children:
                editable(s)
            if len(children)>1 and any(identity(s) not in ledger.data['owned'] for s in children[1:]):
                raise ValueError('Original utility may delete a secondary shape; unowned secondary shapes are refused')
            if action in ('unlock_curve','project_curve'):
                history=cmds.listHistory(obj,pruneDagObjects=True) or []
                if any(identity(n) not in set(ledger.data['owned'])|{identity(obj)}|{identity(s) for s in children} for n in history):
                    raise ValueError('Curve has unowned history that the original command would bake/delete')
        if action=='curve_controls':
            curve=plan['objects'][0]
            connected=cmds.listConnections(curve,type='blindDataTemplate') or []
            if any(n.rsplit('|',1)[-1].startswith('anim_movement_on_curve_tool_sequent_control') for n in connected):
                raise ValueError('This curve already has a control system; use it or delete it first')
            if ledger.data['pending']:
                path_name=ledger.data['globals'].get('AUTOPATH_second_curve')
                path_id=ledger.data['identity_map'].get(path_name)
                if identity(curve)!=path_id:
                    raise ValueError('While a path is pending, create controls only on its own editable path curve')
    if action in ('arrange_controls','delete_controls'):
        metadata=cmds.ls('anim_movement_on_curve_tool_sequent_control*',type='blindDataTemplate') or []
        linked=set()
        for obj in plan['objects']:
            linked.update(n for n in cmds.listConnections(obj,type='blindDataTemplate') or [] if n in metadata)
        if not plan['objects'] and len(metadata)==1:
            linked=set(metadata)
            values=cmds.listConnections(metadata[0]+'.curve',source=True,destination=False) or []
            if len(values)==1:
                plan['objects']=[node(values[0])]
        if len(linked)!=1 or identity(next(iter(linked))) not in ledger.data['owned']:
            raise ValueError('Select a curve/control connected to exactly one owned system; foreign systems are refused')
        metadata=[next(iter(linked))]
        allowed=set(ledger.data['owned'])|set(ledger.data['inputs'])
        for neighbor in cmds.listConnections(metadata[0]) or []:
            if identity(neighbor) not in allowed:
                raise ValueError('Curve-control metadata connects to an external object')
        if action=='arrange_controls' and (len(plan['objects'])!=1 or identity(plan['objects'][0]) not in ledger.data['owned']):
            raise ValueError('Arrange requires one owned curve-control locator')
    if action=='root_motion':
        main=node(options['main']); pelvis=node(options['pelvis'])
        if main==pelvis or main not in plan['objects']:
            raise ValueError('Distinct main/pelvis; main must belong to the input layer')
        plan.update(main=main,pelvis=pelvis)
    if options.get('curve_object'):
        plan['curve_object']=node(options['curve_object'])
    elif action in ('create_path','auto_path','create_circle'):
        plan['curve_object']=''
    if action in LAYER_ACTIONS or action in PATH_ACTIONS or action=='euler_filter':
        for obj in plan['objects']:
            for attr in ('tx','ty','tz','rx','ry','rz'):
                if cmds.attributeQuery(attr,node=obj,exists=True):
                    editable(obj,(attr,))
                    for source in cmds.listConnections(obj+'.'+attr,source=True,destination=False) or []:
                        kind=cmds.nodeType(source)
                        if not (kind.startswith('animCurve') or kind.startswith('animBlend')):
                            raise ValueError('Existing non-animation driver on control channel: '+source)
    if action in ('root_motion','auto_path','apply_path','apply_circle'):
        cleanup={obj:[a for a in cmds.listAttr(obj,userDefined=True) or [] if a!='blendPoint999wb'] for obj in plan['objects']}
        cleanup={n:a for n,a in cleanup.items() if a}
        plan['attribute_cleanup']=cleanup
        if cleanup and not options.get('allow_attribute_cleanup',False):
            raise ValueError('Original algorithm deletes ALL custom control attrs; inspect attribute_cleanup via status/docs and explicitly allow after backup: '+repr(cleanup))
    return plan


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


def command(action,options,plan):
    if action=='match':
        mel.eval('SHIFT3_2_d3d5060e35d6738adc9ec43bc95dfe74();')
        result=mel.eval('SHIFT3_2_36e868f70d3bc857bf7c0d874db1cf86(1);')
        if not result:
            raise RuntimeError('Original MATCH did not return a result layer')
        return result
    if action=='extract':
        return mel.eval('SHIFT3_2_21b7c17e232d97d5c941030f7d497200('+array(plan['objects'])+');')
    if action in ('create_path','auto_path','create_circle'):
        circle=action=='create_circle'
        count=1 if circle else options.get('cv_count',5)
        flat=True if circle else options.get('flat',True)
        mel.eval('SHIFT3_2_8327291d23e32e708ec222974d35f87a('+str(count)+','+quote(plan['curve_object'])+','+str(int(flat))+','+str(int(circle))+');')
        error=mel.eval('global string $AUTOPATH_error; $mtkShiftError=$AUTOPATH_error;')
        curve=mel.eval('global string $AUTOPATH_second_curve; $mtkShiftCurve=$AUTOPATH_second_curve;')
        if error or not curve or not cmds.objExists(curve):
            raise RuntimeError('Original path creation failed or returned no moving path: '+str(error))
        if circle:
            mel.eval('SHIFT3_2_762f049a0ffb16260649a1d60212ee9f();')
        if action=='auto_path':
            mel.eval('SHIFT3_2_d0162d537d4e82bff3de890c7c1b848d('+str(options.get('easing',10))+',0,'+str(int(options.get('vertical_independent',True)))+');')
        return curve
    if action in PATH_ACTIONS:
        circle=action=='apply_circle'
        mel.eval('SHIFT3_2_d0162d537d4e82bff3de890c7c1b848d('+str(0 if circle else options.get('easing',10))+',0,'+str(0 if circle else int(options.get('vertical_independent',True)))+');')
        return None
    if action=='root_motion':
        result=mel.eval('SHIFT3_2_f86532f512c57532bf69080729fb7c0c('+quote(plan['main'])+','+quote(plan['pelvis'])+','+str(int(options.get('rotate',False)))+','+str(int(options.get('flat',True)))+');')
        if not result:
            raise RuntimeError('Original root-motion calculation returned no layer')
        return result
    procedures={'lock_curve':'SHIFT3_2_c0333f01c0305441f7e870d2e8681fb9','unlock_curve':'UnlockCurveLength','project_curve':'SHIFT3_2_9ae282fb1fe972d565d0cedb2f703421','curve_controls':'SHIFT3_2_2948842313131fcddb41ac6ad1efd38c','arrange_controls':'SHIFT3_2_dfd04e9fc8891230ecf4649c050058d5','delete_controls':'SHIFT3_2_4ec8ec2e22058b36b7f19c5b04a2deed','euler_filter':'SHIFT3_2_09f1edc0a69a4931b08e1bcc40e94a55','refresh_viewport':'SHIFT3_2_f4b1a2b52ab1771321003f86cde63160'}
    if action=='project_curve' and not plan['ledger'].data['pending']:
        # The original finishes by selecting AUTOPATH_second_curve. Supply the
        # explicit reference curve as UI context when no path was created yet.
        mel.eval('global string $AUTOPATH_second_curve; $AUTOPATH_second_curve='+quote(plan['objects'][1])+';')
    return mel.eval(procedures[action]+'();')


def execute(options):
    plan=preflight(options)
    ledger=plan['ledger']
    action=options['action']
    if action=='status':
        return ledger.state()
    # Original layer/path/timeline utilities require Maya's real UI procedures.
    # Do not fake getSelectedAnimLayer or fabricate a successful bake in batch.
    if cmds.about(batch=True) and (action in LAYER_ACTIONS or action in PATH_ACTIONS or action=='refresh_viewport'):
        raise RuntimeError('Complete original workflow requires interactive Maya animation-layer/timeline UI; batch execution unavailable')
    load_vendor()
    if action=='analyze_curve':
        before=all_uuids(); oldtime=cmds.currentTime(query=True)
        values=mel.eval('SHIFT3_2_4456cc602c2236c5ece51bee2a5b2ee6('+quote(plan['curve'])+','+array([options.get('start_value',0),options.get('end_value',1)])+','+str(int(options.get('relative',True)))+');')
        if before!=all_uuids() or oldtime!=cmds.currentTime(query=True):
            raise RuntimeError('Read-only analysis unexpectedly changed scene state')
        return {'curve':plan['curve'],'values':values,'scene_write':False}
    snap=snapshot()
    before=all_uuids()
    input_ids={identity(n) for n in plan['objects']}
    success=False
    try:
        ledger.save()
        ledger.restore_globals()
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        if plan['layer']:
            layer=plan['layer']
            for l in cmds.ls(type='animLayer') or []:
                cmds.animLayer(l,edit=True,selected=(l==layer),preferred=(l==layer))
            mel.eval('animLayerEditorOnSelect('+quote(layer)+',1);')
        if plan['objects']:
            cmds.select(plan['objects'],replace=True)
        if action in LAYER_ACTIONS or action in PATH_ACTIONS:
            mel.eval('SHIFT3_2_692e2fda85cadfdf0f28e93323f58c08();')
        result=command(action,options,plan)
        if action in ('match','auto_path','apply_path','apply_circle','root_motion'):
            new_layers=[n for n in cmds.ls(type='animLayer') or [] if identity(n) not in before]
            if not new_layers:
                raise RuntimeError('Original algorithm produced no result animation layer')
        if action in ('create_path','create_circle'):
            ledger.data['pending']='circle' if action=='create_circle' else 'path'
            ledger.data['layer']=identity(plan['layer'])
            ledger.data['objects']=[identity(n) for n in plan['objects']]
        elif action in ('auto_path','apply_path','apply_circle'):
            ledger.data['pending']=None
        ledger.data['inputs']=sorted(u for u in set(ledger.data['inputs'])|input_ids if cmds.ls(u))
        ledger.data['failed']=None
        success=True
        output={'vendor_result':result,'attribute_cleanup':plan['attribute_cleanup']}
    except Exception:
        ledger.data['failed']=action
        raise
    finally:
        try:
            if ledger.node:
                ledger.capture(before)
                ledger.save()
        finally:
            try:
                restore(snap,success,action)
            except Exception:
                if ledger.node:
                    ledger.data['failed']=action+':environment_restoration'
                    ledger.save()
                raise
    output.update(ledger.state())
    return output
