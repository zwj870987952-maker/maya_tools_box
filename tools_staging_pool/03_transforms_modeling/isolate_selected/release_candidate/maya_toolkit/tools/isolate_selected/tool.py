import json
import uuid
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

OWNER='mtbIsolateOwner'
DATA='mtbIsolateSnapshot'
PROPS={'action':{'type':'string','enum':['isolate','restore','inspect'],'default':'isolate'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'panel':{'type':'string'},'receipt':{'type':'string'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(kwargs); p.setdefault('action','isolate')
    if p['action'] not in PROPS['action']['enum']: raise ValueError('Unknown action')
    for key,value in p.items():
        if key=='objects':
            if not isinstance(value,list) or not value or any(not isinstance(n,str) or not n for n in value) or len(value)!=len(set(value)): raise ValueError('Unique explicit nodes required')
        elif not isinstance(value,str) or not value: raise ValueError('Nonempty string required')
    if p['action']=='restore' and 'objects' in p or p['action']!='restore' and 'receipt' in p: raise ValueError('Arguments do not apply to action')
    return p


def node(value,write=False):
    from maya import cmds
    from maya.api import OpenMaya as om
    if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Explicit whole node required')
    matches=cmds.ls(value,long=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous node: '+value)
    result=matches[0]; sel=om.MSelectionList(); sel.add(result); obj=sel.getDependNode(0)
    if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('Instanced DAG unsupported')
    if write:
        if cmds.referenceQuery(result,isNodeReferenced=True) or any(cmds.lockNode(result,query=True,lock=True) or []): raise ValueError('Referenced/locked writable node')
        plug=result+'.visibility'
        if cmds.getAttr(plug,lock=True) or cmds.listConnections(plug,source=True,destination=False): raise ValueError('Locked/driven visibility')
    return result,cmds.ls(result,uuid=True)[0]


def scene_scope(values):
    from maya import cmds
    if not values: raise ValueError('Select at least one whole transform/shape')
    selected=[]; ids=set()
    for value in values:
        n,uid=node(value)
        if not cmds.objectType(n,isAType='dagNode'): raise ValueError('DAG transforms/shapes required')
        if uid in ids: raise ValueError('Aliased duplicate targets')
        ids.add(uid); selected.append(n)
        for shape in cmds.listRelatives(n,shapes=True,fullPath=True) or []: node(shape)
    # Keep every ancestor needed to display a selected descendant. Hide only
    # child transforms, never the direct shapes of the selected parent itself.
    keep=set(selected)
    for n in selected:
        parent=cmds.listRelatives(n,parent=True,fullPath=True) or []
        while parent:
            keep.add(parent[0]); parent=cmds.listRelatives(parent[0],parent=True,fullPath=True) or []
    descendants=set()
    for n in selected:
        descendants.update(cmds.listRelatives(n,allDescendents=True,fullPath=True) or [])
    changes=[]
    for n in sorted(descendants-keep):
        if not cmds.objectType(n,isAType='transform'): continue
        n,uid=node(n,True); before=cmds.getAttr(n+'.visibility')
        if before: changes.append({'uuid':uid,'name':n,'before':bool(before),'during':False})
    return {'objects':selected,'selected_uuids':sorted(ids),'hide':changes,'direct_selected_shapes_preserved':True}


def reference(value):
    from maya import cmds
    base,suffix=(value.split('.',1)+[''])[:2] if '.' in value else (value,'')
    n,uid=node(base)
    return {'uuid':uid,'suffix':'.'+suffix if suffix else ''}


def ref_name(ref):
    from maya import cmds
    values=cmds.ls(ref['uuid'],long=True) or []
    if len(values)!=1: raise ValueError('Snapshot member missing or ambiguous UUID')
    node(values[0])
    result=values[0]+ref['suffix']
    if not cmds.objExists(result): raise ValueError('Snapshot component no longer exists')
    return result


def validate_snapshot(data):
    if not isinstance(data,dict) or set(data)!={'format','panel','hide','prior_view','view_members'} or data['format']!='mtbIsolate-1': raise ValueError('Unsupported/corrupt snapshot')
    if not isinstance(data['panel'],str) or not data['panel']: raise ValueError('Invalid snapshot panel')
    prior=data['prior_view']
    if not isinstance(prior,dict) or set(prior)!={'enabled','members'} or type(prior['enabled']) is not bool or not isinstance(prior['members'],list) or any(not isinstance(n,str) for n in prior['members']): raise ValueError('Invalid prior panel state')
    if not isinstance(data['hide'],list) or not isinstance(data['view_members'],list): raise ValueError('Invalid snapshot rows')
    ids=set()
    for row in data['hide']:
        if not isinstance(row,dict) or set(row)!={'uuid','name','before','during'} or type(row['before']) is not bool or row['before'] is not True or row['during'] is not False or not isinstance(row['name'],str): raise ValueError('Invalid visibility snapshot row')
        uuid.UUID(row['uuid'])
        if row['uuid'] in ids: raise ValueError('Duplicate snapshot UUID')
        ids.add(row['uuid'])
    for row in data['view_members']:
        if not isinstance(row,dict) or set(row)!={'uuid','suffix'} or not isinstance(row['suffix'],str): raise ValueError('Invalid panel member reference')
        uuid.UUID(row['uuid'])
        if row['suffix'] and (not row['suffix'].startswith('.') or any(c in row['suffix'] for c in (';','"','\n','\r','\\'))): raise ValueError('Invalid component suffix')
    if len(prior['members'])!=len(data['view_members']): raise ValueError('Incomplete panel membership snapshot')
    return data


def receipts():
    from maya import cmds
    return [n for n in cmds.ls(type='network') or [] if cmds.objExists(n+'.'+OWNER) and cmds.getAttr(n+'.'+OWNER)=='isolate_selected']


def read_receipt(value):
    from maya import cmds
    values=cmds.ls(value,long=True) or []
    if len(values)!=1 or values[0] not in receipts(): raise ValueError('Exact candidate-owned snapshot network required')
    n=values[0]
    if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Snapshot referenced/locked')
    if cmds.listConnections(n,source=False,destination=True): raise ValueError('Snapshot has external consumer; refuse deletion')
    if not cmds.objExists(n+'.'+DATA) or cmds.listConnections(n,source=True,destination=False): raise ValueError('Snapshot missing data or externally driven')
    data=validate_snapshot(json.loads(cmds.getAttr(n+'.'+DATA)))
    return n,data


def plan(p):
    from maya import cmds
    from . import view
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    if p['action']=='restore':
        if 'receipt' in p:
            receipt,snapshot=read_receipt(p['receipt'])
            panel=view.choose(p.get('panel') or snapshot['panel'])
        else:
            panel=view.choose(p.get('panel'))
            matching=[n for n in receipts() if read_receipt(n)[1]['panel']==panel]
            if len(matching)!=1: raise ValueError('One owned snapshot for panel required; specify receipt for moved scene')
            receipt,snapshot=read_receipt(matching[0])
        for row in snapshot['hide']:
            value=ref_name({'uuid':row['uuid'],'suffix':''}); node(value,True)
            if bool(cmds.getAttr(value+'.visibility'))!=row['during']: raise ValueError('Visibility changed since isolate; restore refused before writes')
        members=[ref_name(r) for r in snapshot['view_members']]
        return dict(p,panel=panel,receipt=receipt,snapshot=snapshot,restore_members=members)
    panel=view.choose(p.get('panel'))
    if any(read_receipt(n)[1]['panel']==panel for n in receipts()): raise ValueError('Restore this panel snapshot before applying a new isolate')
    scope=scene_scope(p.get('objects') or cmds.ls(selection=True,long=True) or [])
    before=view.state(panel)
    refs=[reference(n) for n in before['members']]
    return dict(p,panel=panel,scope=scope,prior_view=before,prior_members=refs,gui_acceptance='not_run')


class IsolateSelectedTool(BaseMayaTool):
    tool_id='isolate_selected'; tool_name='隔离选中物体并保留恢复记录'
    category='modeling_surfacing'; version='1.0-candidate.1'
    description='只显示所选DAG对象，隐藏未选子transform并保留直接shape/选中后代路径；逐UUID持久snapshot仅恢复本次visibility和原modelPanel隔离集合。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        from . import view
        p=normalize(kwargs); scope=plan(p)
        if p['action']=='inspect': return ToolResult.ok(data=scope)
        selection=cmds.ls(selection=True,long=True) or []
        auto=cmds.autoKeyframe(query=True,state=True)
        try:
            cmds.autoKeyframe(state=False)
            if p['action']=='restore':
                snapshot=scope['snapshot']
                for row in snapshot['hide']:
                    n=ref_name({'uuid':row['uuid'],'suffix':''}); cmds.setAttr(n+'.visibility',row['before'])
                view.restore(scope['panel'],snapshot['prior_view'],scope['restore_members'])
                cmds.delete(scope['receipt'])
                return ToolResult.ok(data={'restored':snapshot['hide'],'panel':scope['panel'],'gui_acceptance':'not_run'})
            snapshot={'format':'mtbIsolate-1','panel':scope['panel'],'hide':scope['scope']['hide'],'prior_view':scope['prior_view'],'view_members':scope['prior_members']}
            receipt=cmds.createNode('network',name='mtbIsolateReceipt_'+uuid.uuid4().hex[:12])
            cmds.addAttr(receipt,longName=OWNER,dataType='string'); cmds.setAttr(receipt+'.'+OWNER,'isolate_selected',type='string')
            cmds.addAttr(receipt,longName=DATA,dataType='string'); cmds.setAttr(receipt+'.'+DATA,json.dumps(snapshot),type='string')
            for row in snapshot['hide']: cmds.setAttr(row['name']+'.visibility',0)
            view.apply(scope['panel'],scope['scope']['objects'])
            return ToolResult.ok(data={'receipt':receipt,'panel':scope['panel'],'hidden':snapshot['hide'],'gui_acceptance':'not_run'})
        finally:
            cmds.autoKeyframe(state=auto)
            valid=[n for n in selection if cmds.objExists(n)]
            cmds.select(valid,replace=True) if valid else cmds.select(clear=True)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        win='mtbIsolateSelectedOnly'
        if cmds.window(win,exists=True): cmds.deleteUI(win)
        cmds.window(win,title=self.tool_name,widthHeight=(370,180)); cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='只隐藏未选子transform；恢复本次快照及原隔离集合')
        panel=cmds.textField(placeholderText='modelPanel（留空使用当前视图）')
        def call(action,dry=False):
            name=cmds.textField(panel,query=True,text=True).strip()
            result=self.run(action=action,dry_run=dry,**({'panel':name} if name else {})); print(result.to_dict())
            if not result.success: cmds.warning(result.message)
        cmds.button(label='预检当前选择',command=lambda *_:call('isolate',True))
        cmds.button(label='只显示选中物体',command=lambda *_:call('isolate'))
        cmds.button(label='恢复本次隔离记录',command=lambda *_:call('restore')); cmds.showWindow(win)
        return win


def isolate_selected_only(**kwargs): return IsolateSelectedTool().run(action='isolate',**kwargs)
def restore_visibility(**kwargs): return IsolateSelectedTool().run(action='restore',**kwargs)
def create_isolate_ui(): return IsolateSelectedTool().show_ui()
def main(): return create_isolate_ui()
