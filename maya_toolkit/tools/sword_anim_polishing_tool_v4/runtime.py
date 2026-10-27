"""Independent guarded execution of complete, unchanged licensed MEL."""
import json
import math
from pathlib import Path
from . import vendor_adapter as v

GROUPS={'source':'BARN_curve_sword_remember_SOURCE','aim_top':'BARN_curve_sword_remember_AIM_TOP','aim_side':'BARN_curve_sword_remember_AIM_SIDE','base':'BARN_curve_sword_remember_BASE_SYSTEM','all':'BARN_curve_sword_remember_DELETE_AFTER_BAKE','path_source':'BARN_curve_motion_path_remember1','path_locator':'BARN_curve_motion_path_remember2','path_system':'BARN_curve_motion_path_remember3'}
STARTS={'begin_aim':'SW_6cbceab3c5b6c616d252d08ce5624f3b','begin_sword':'SW_51ef5f996bc4f51959ade4cf9878f9b3','begin_reverse':'SW_0f6b87b682f999b1ba225892b54147c2'}
NODE_OWNER='mtkSwordOwnedBy'


def native_call(command):
    from maya.api import OpenMaya as om
    import re
    errors=[]
    depth=[0]
    def track_undo(text,*_):
        if text.lstrip().startswith('undoInfo '):
            flags=set(re.findall(r'-[A-Za-z]+',text))
            if flags&{'-ock','-openChunk'}:
                depth[0]+=1
            if flags&{'-cck','-closeChunk'}:
                depth[0]-=1
    callback=om.MCommandMessage.addCommandOutputCallback(lambda message,kind,*_:errors.append(message) if kind==om.MCommandMessage.kError else None)
    command_callback=om.MCommandMessage.addCommandCallback(track_undo)
    try:
        return v.mel.eval(command)
    except Exception as exc:
        raise RuntimeError(str(exc)+'; native MEL: '+' | '.join(errors[-4:])) from exc
    finally:
        om.MMessage.removeCallback(callback)
        om.MMessage.removeCallback(command_callback)
        # Actual command callbacks include undoInfo inside compiled native MEL.
        # Close only unmatched opens observed during this synchronous call;
        # the surrounding BaseMayaTool chunk is outside the observed scope.
        if depth[0]<0 or depth[0]>32:
            raise RuntimeError('Unexpected native Undo balance: '+str(depth[0]))
        for _ in range(depth[0]):
            v.cmds.undoInfo(closeChunk=True)


def live_group(ledger,name):
    output=[]
    for value in ledger.data['globals'].get(GROUPS[name],[]) or []:
        uid=ledger.data['identity_map'].get(value)
        if uid and v.cmds.ls(uid):
            output.append(v.resolve(uid))
    return output


def owned(ledger):
    output=[]
    for uid in ledger.data['owned']:
        if v.cmds.ls(uid):
            node=v.resolve(uid)
            if not v.cmds.attributeQuery(NODE_OWNER,node=node,exists=True) or v.cmds.getAttr(node+'.'+NODE_OWNER)!=ledger.sid:
                raise ValueError('Lost ownership marker: '+node)
            output.append(node)
    return output


def guard_delete(ledger,nodes):
    permitted=set(ledger.data['owned'])
    all_nodes=[]
    for n in nodes:
        if v.identity(n) not in permitted:
            raise ValueError('Only candidate-owned helpers may be deleted')
        all_nodes.append(n)
        all_nodes.extend(v.cmds.listRelatives(n,allDescendents=True,fullPath=True) or [])
    for n in all_nodes:
        v.editable(n)
        if v.identity(n) not in permitted:
            raise ValueError('Foreign child blocks deletion: '+n)
        for target in v.cmds.listConnections(n,source=False,destination=True) or []:
            uid=v.identity(target)
            if uid not in permitted and uid not in ledger.data['inputs'] and v.cmds.nodeType(target)!='shadingEngine':
                raise ValueError('Foreign output blocks deletion: '+target)
    return all_nodes


def channel_guards(nodes,ledger,allow_owned=False):
    allowed=set(ledger.data['owned']) if allow_owned else set()
    input_ids={v.identity(n) for n in nodes}|set(ledger.data['inputs'])
    for n in nodes:
        v.editable(n)
        for attr in ('tx','ty','tz','rx','ry','rz'):
            if v.cmds.getAttr(n+'.'+attr,lock=True):
                raise ValueError('Locked transform channel: '+n+'.'+attr)
            for driver in v.cmds.listConnections(n+'.'+attr,source=True,destination=False) or []:
                kind=v.cmds.nodeType(driver)
                if v.identity(driver) in allowed:
                    continue
                if not kind.startswith('animCurve'):
                    raise ValueError('Existing foreign/non-animation driver: '+driver)
                v.editable(driver)
                if kind not in ('animCurveTA','animCurveTL','animCurveTT','animCurveTU'):
                    raise ValueError('Driven-key curve unsupported')
                for destination in v.cmds.listConnections(driver,source=False,destination=True) or []:
                    if v.identity(destination) not in input_ids|allowed:
                        raise ValueError('Shared animation input affects outside scope')


def preflight(p):
    v.resources()
    ledger=v.Ledger(p.get('session'))
    action=p['action']
    plan={'action':action,'session':ledger.sid,'pending':ledger.data.get('pending'),'owned':owned(ledger),'gui_acceptance':'not_run'}
    if action=='status':
        plan.update(failed=ledger.data.get('failed'),groups={g:live_group(ledger,g) for g in GROUPS},source_procedures=len(v.catalog()['unique_procedures']))
        return plan
    if not v.cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Maya Undo')
    if ledger.data.get('failed'):
        raise ValueError('Previous operation failed; Undo before continuing')
    if action in ('parent_in',*STARTS,'arc_polish','finish_setup') and v.cmds.about(batch=True):
        raise ValueError('Complete native Parent In/setup/Arc Polish requires interactive Maya/model panel; no fabricated camera/timeline/scriptJob replacement')
    names=p.get('objects',v.cmds.ls(selection=True,long=True) or [])
    nodes=[v.node(n) for n in names]
    if len(nodes)!=len(set(nodes)):
        raise ValueError('Duplicate aliases identify same transform')
    if any(len(v.cmds.ls(n.rsplit('|',1)[-1],long=True) or [])!=1 for n in nodes):
        raise ValueError('Original vendor globals require unique short control names')
    plan['objects']=nodes
    if action in ('help','refresh_viewport'):
        return plan
    if ledger.data.get('pending') and action not in ('finish_setup','select_group','status','delete_system','help','constraint_weights'):
        raise ValueError('Finish the current locator setup before creating another system')
    if action in ('parent_in',*STARTS,'bake','bake_layer','euler_filter','arc_polish','constraint_weights') and not nodes:
        raise ValueError('Select or supply whole transforms')
    if action=='constraint_weights' and len(nodes)<2:
        raise ValueError('Supply targets followed by constrained transform')
    if action in ('begin_sword','begin_reverse') and len(nodes) not in (2,3):
        raise ValueError('Select sword, optional wrist, and hand in this order')
    if action in ('parent_in',*STARTS,'bake','bake_layer'):
        start=p.get('start',int(v.cmds.playbackOptions(query=True,animationStartTime=True)))
        end=p.get('end',int(v.cmds.playbackOptions(query=True,animationEndTime=True)))
        if end<=start or end-start>200000:
            raise ValueError('Invalid animation range')
        plan['range']=[start,end]
    if action in ('parent_in',*STARTS,'bake','bake_layer','euler_filter','arc_polish'):
        channel_guards(nodes,ledger,allow_owned=action in ('bake','bake_layer','euler_filter'))
    if action=='bake_layer' and v.cmds.objExists('BakedAnim'):
        raise ValueError('Original layer bake names BakedAnim; existing node blocks creation rather than risking reuse')
    if action=='euler_filter':
        curves=v.cmds.listConnections(nodes,source=True,destination=False,type='animCurve') or []
        if not curves:
            raise ValueError('Euler filter requires existing rotation animation')
        first=min((v.cmds.keyframe(c,query=True,timeChange=True) or [0])[0] for c in curves)
        plan['temporary_zero_key']=first-10
        for node in nodes:
            for attr in ('rx','ry','rz'):
                if v.cmds.keyframe(node+'.'+attr,query=True,time=(first-10,first-10),keyframeCount=True):
                    raise ValueError('Original temporary zero-key time already contains animation')
    if action=='finish_setup':
        if not ledger.data.get('pending'):
            raise ValueError('No pending setup')
        inputs=[v.resolve(u) for u in ledger.data['objects']]
        channel_guards(inputs,ledger)
        top=live_group(ledger,'aim_top')
        side=live_group(ledger,'aim_side')
        if not top or not side:
            raise ValueError('Recorded aim locators disappeared')
        for a,b in zip(top,side):
            pos_a=v.cmds.xform(a,query=True,worldSpace=True,translation=True)
            pos_b=v.cmds.xform(b,query=True,worldSpace=True,translation=True)
            source=inputs[0] if ledger.data['pending']!='begin_aim' else inputs[top.index(a)]
            origin=v.cmds.xform(source,query=True,worldSpace=True,rotatePivot=True)
            va=[x-y for x,y in zip(pos_a,origin)]
            vb=[x-y for x,y in zip(pos_b,origin)]
            cross=[va[1]*vb[2]-va[2]*vb[1],va[2]*vb[0]-va[0]*vb[2],va[0]*vb[1]-va[1]*vb[0]]
            if sum(x*x for x in cross)<1e-10:
                raise ValueError('Move Top/Side away from pivot into non-collinear directions')
        plan['range']=ledger.data['range']
    if action=='arc_polish':
        if len(nodes)!=1:
            raise ValueError('Arc Polish accepts one animated object')
        if 'decomposeMatrix' not in v.cmds.allNodeTypes():
            raise ValueError('Original Arc requires decomposeMatrix/matrixNodes; load the installed Maya plugin before validation')
        slider=v.mel.eval('$mtkSwordSlider=$gPlayBackSlider')
        timeline=v.cmds.timeControl(slider,query=True,rangeArray=True)
        selected=v.cmds.keyframe(query=True,selected=True,timeChange=True) or []
        selected_curves=v.cmds.keyframe(query=True,selected=True,name=True) or []
        object_curves=v.cmds.listConnections(nodes[0],source=True,destination=False,type='animCurve') or []
        if selected_curves and not set(selected_curves)<=set(object_curves):
            raise ValueError('Selected graph keys include outside objects')
        if timeline[1]-timeline[0]<=1 and (not selected or max(selected)<=min(selected)):
            raise ValueError('Select actual timeline range or at least two object key times')
        plan['range']=timeline if timeline[1]-timeline[0]>1 else [min(selected),math.ceil(max(selected)+1)]
        plan['trails']=[{'uuid':v.identity(t),'nodeState':v.cmds.getAttr(t+'.nodeState')} for t in v.cmds.ls(type='motionTrail') or []]
    if action=='select_group':
        plan['selection']=live_group(ledger,p['group'])
    if action=='delete_system':
        # All recorded helpers include constraints, pairBlends, paths/history.
        # Require baked source first rather than deleting only DAG locators.
        if not ledger.node or not ledger.data.get('baked'):
            raise ValueError('Bake source animation successfully before deleting its system')
        plan['delete']=[n for n in owned(ledger) if not v.cmds.nodeType(n).startswith(('animCurve','animBlend')) and v.cmds.nodeType(n)!='animLayer']
        guard_delete(ledger,plan['delete'])
        plan['reconnect']=[]
        for target in [v.resolve(u) for u in ledger.data['inputs'] if v.cmds.ls(u)]:
            for channel in ('tx','ty','tz','rx','ry','rz'):
                destination=target+'.'+channel
                sources=v.cmds.listConnections(destination,source=True,destination=False,plugs=True) or []
                for source in sources:
                    driver=source.split('.')[0]
                    if v.identity(driver) not in ledger.data['owned']:
                        continue
                    kind=v.cmds.nodeType(driver)
                    if kind=='pairBlend':
                        attr=('inTranslate' if channel[0]=='t' else 'inRotate')+channel[-1].upper()+'1'
                        baked=v.cmds.listConnections(driver+'.'+attr,source=True,destination=False,plugs=True) or []
                        if len(baked)!=1 or not v.cmds.nodeType(baked[0].split('.')[0]).startswith(('animCurve','animBlend')):
                            raise ValueError('Baked pairBlend input1 has no independent animation; keep system for manual acceptance')
                        v.editable(target,(channel,))
                        plan['reconnect'].append([baked[0],destination])
                    elif not kind.startswith(('animCurve','animBlend')):
                        raise ValueError('Source still depends on a non-baked helper; bake before cleanup')
    if action=='update_motion_trails':
        trails=v.cmds.ls(type='motionTrail') or []
        if any(v.identity(t) not in ledger.data['owned'] for t in trails):
            raise ValueError('Original update touches all motion trails; foreign trails block this action')
    return plan


def jobs():
    return {int(x.split(':',1)[0]):x for x in v.cmds.scriptJob(listJobs=True) or []}


def kill_new_vendor_jobs(before):
    for uid,text in jobs().items():
        if uid not in before and 'SW_' in text:
            v.cmds.scriptJob(kill=uid,force=True)


def tag_new(ledger,before):
    for uid in v.all_uuids()-before-{ledger.sid}:
        node=v.resolve(uid)
        if not v.cmds.attributeQuery(NODE_OWNER,node=node,exists=True):
            v.cmds.addAttr(node,longName=NODE_OWNER,dataType='string')
        v.cmds.setAttr(node+'.'+NODE_OWNER,ledger.sid,type='string')


def execute(p):
    plan=preflight(p)
    action=p['action']
    if action=='status':
        return plan
    if action=='help':
        filename={'base':'help_parent_make_aim_tools.mel','reverse':'help_sword_reverse_tools.mel','path':'help_path_polish.mel','bake':'help_bake.mel'}[p['topic']]
        return {'text':(v.PKG/'vendor/misc'/filename).read_text(encoding='utf-8-sig'),'topic':p['topic']}
    v.load_vendor()
    ledger=v.Ledger(p.get('session'))
    if action=='constraint_weights':
        values=v.mel.eval('SW_9de233870ac6b9c5087a491c3b4ca38a('+v.array(plan['objects'])+');')
        return {'weights':values,'objects':plan['objects']}
    if action=='select_group':
        v.cmds.select(plan['selection'],replace=True) if plan['selection'] else v.cmds.select(clear=True)
        return {'selection':plan['selection']}
    ledger.save()
    before=v.all_uuids()
    previous_jobs=jobs()
    env=v.snapshot()
    env['context']=v.cmds.currentCtx()
    if not v.cmds.about(batch=True):
        env['move_mode']=v.cmds.manipMoveContext('Move',query=True,mode=True)
    env['animation_range']=[v.cmds.playbackOptions(query=True,**{name:True}) for name in ('animationStartTime','animationEndTime')]
    env['key_selection']=[(v.identity(c),v.cmds.keyframe(c,query=True,selected=True,timeChange=True) or []) for c in v.cmds.keyframe(query=True,selected=True,name=True) or []]
    success=False
    result=None
    try:
        ledger.restore_globals()
        v.cmds.autoKeyframe(state=False)
        v.cmds.selectPref(trackSelectionOrder=True)
        if action!='arc_polish':
            v.cmds.selectKey(clear=True)
        if plan.get('range') and action!='arc_polish':
            v.cmds.playbackOptions(animationStartTime=plan['range'][0],animationEndTime=plan['range'][1])
        if plan['objects']:
            v.cmds.select(plan['objects'],replace=True)
        if action=='parent_in':
            result=native_call('SW_cf01bdffb1989adef0d5abffde9c5a33('+str(p['size'])+');')
            native_call('SW_09f1edc0a69a4931b08e1bcc40e94a55();')
        elif action in STARTS:
            command=STARTS[action]+'('+('' if action=='begin_sword' else str(p['size']))+');'
            v.mel.eval(command)
            kill_new_vendor_jobs(previous_jobs)
            ledger.data['pending']=action
            ledger.data['objects']=[v.identity(n) for n in plan['objects']]
            ledger.data['range']=plan['range']
        elif action=='finish_setup':
            pending=ledger.data['pending']
            if pending=='begin_aim':
                result=v.mel.eval('SW_10df34add5a583f84d24608e860c1b4b();')
            elif pending=='begin_sword':
                selection=live_group(ledger,'aim_top')+live_group(ledger,'aim_side')+[v.resolve(u) for u in ledger.data['objects']]
                v.cmds.select(selection,replace=True)
                v.mel.eval('SW_f97932bf0a9a89d861a2c21323a52981(1,0.5);')
            else:
                helpers=live_group(ledger,'all')
                inputs=[v.resolve(u) for u in ledger.data['objects']]
                v.mel.eval('SW_45974e786e3602ef878571e324a928e9(0.5,'+v.array(helpers)+','+v.array(inputs)+');')
            ledger.data['pending']=None
        elif action=='arc_polish':
            # The original consumes real timeline/graph selection; no global
            # procedure replacement is installed to fake this range.
            native_call('SW_216cd5229394f893f58516bc1517892a('+str(p['knots'])+','+str(int(p['show_source']))+');')
        elif action in ('bake','bake_layer'):
            if action=='bake_layer':
                result=v.mel.eval('SW_c830bbb3bb6041f72a5fb76403fcabe8();')
            else:
                v.mel.eval('SW_de88efca2929f0080ae1d45ff5db42d4();')
            native_call('SW_09f1edc0a69a4931b08e1bcc40e94a55();')
            # The source catches bake errors: independently require keys across
            # range instead of treating a void MEL return as success.
            for node in plan['objects']:
                curves=v.cmds.keyframe(node,query=True,name=True) or []
                times=[t for c in curves for t in v.cmds.keyframe(c,query=True,timeChange=True) or []]
                if not times or min(times)>plan['range'][0] or max(times)<plan['range'][1]:
                    raise RuntimeError('Original bake did not produce expected range on '+node)
            if set(v.identity(n) for n in plan['objects'])>=set(ledger.data['inputs']):
                ledger.data['baked']=True
        elif action=='euler_filter':
            v.mel.eval('SW_09f1edc0a69a4931b08e1bcc40e94a55();')
        elif action=='delete_system':
            # Preserve independent animation created by the source bake. New
            # output animCurves created while baking must not be deleted.
            for source,destination in plan['reconnect']:
                v.cmds.connectAttr(source,destination,force=True)
            deletions=plan['delete']
            guard_delete(ledger,deletions)
            constraints=[n for n in deletions if v.cmds.objectType(n,isAType='constraint')]
            if constraints:
                v.cmds.delete(constraints)
            remaining=[n for n in deletions if v.cmds.objExists(n)]
            if remaining:
                v.cmds.delete(remaining)
            ledger.data['pending']=None
        elif action=='update_motion_trails':
            v.mel.eval('SW_9b29b86e5de4ada4b19840df4e8973d5();')
        elif action=='refresh_viewport':
            v.cmds.refresh(suspend=False)
            if not v.cmds.about(batch=True):
                v.mel.eval('setTimeSliderVisible(1);')
        if action in ('parent_in',*STARTS,'arc_polish'):
            ledger.data['inputs']=sorted(set(ledger.data['inputs'])|{v.identity(n) for n in plan['objects']})
            ledger.data['baked']=False
        ledger.capture(before)
        tag_new(ledger,before)
        ledger.save()
        success=True
    except Exception as exc:
        ledger.capture(before)
        tag_new(ledger,before)
        ledger.data['failed']=str(exc)
        ledger.save()
        raise
    finally:
        try:
            kill_new_vendor_jobs(previous_jobs)
            for row in plan.get('trails',[]):
                if v.cmds.ls(row['uuid']):
                    v.cmds.setAttr(v.resolve(row['uuid'])+'.nodeState',row['nodeState'])
            v.cmds.playbackOptions(animationStartTime=env['animation_range'][0],animationEndTime=env['animation_range'][1])
            v.cmds.setToolTo(env['context'])
            if 'move_mode' in env:
                v.cmds.manipMoveContext('Move',edit=True,mode=env['move_mode'])
            v.restore(env,success,'refresh_viewport' if action=='refresh_viewport' else action)
            v.cmds.selectKey(clear=True)
            for uid,times in env['key_selection']:
                if v.cmds.ls(uid):
                    for time in times:
                        v.cmds.selectKey(v.resolve(uid),add=True,time=(time,time))
        except Exception as exc:
            ledger.data['failed']='Environment restoration failed: '+str(exc)
            ledger.save()
            raise
    # Metadata after environment restoration agrees with actual scene UUIDs.
    return {'action':action,'session':ledger.sid,'pending':ledger.data.get('pending'),'owned':owned(ledger),'groups':{g:live_group(ledger,g) for g in GROUPS},'native_result':result,'gui_acceptance':'not_run'}


def show_original_ui():
    if v.cmds.about(batch=True):
        raise RuntimeError('Interactive Maya only')
    if v.cmds.window('mayaToolkitSwordPolish',exists=True):
        raise RuntimeError('Close candidate UI before opening original shared-global UI')
    v.load_vendor()
    # Original behavior includes matrixNodes autoload preference; explicit
    # original-UI invocation only, never part of candidate import/preflight.
    return v.mel.eval('sword_anim_polish_tool('+v.quote((v.PKG/'vendor').as_posix())+');')
