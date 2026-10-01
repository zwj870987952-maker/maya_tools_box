import ast
import copy
from functools import wraps
import importlib
import json
from pathlib import Path
import sys
import uuid

_ACTIVE=False
_API=False
_PLAN={}
_ALLOWED=set()
_NEW=set()
_ERRORS=[]
_TICKETS={}
_SESSION={}
OWNER='mtbWsOwner'
TR=['tx','ty','tz','rx','ry','rz']


def catalog():
    return json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf8'))


def preference_load(group):
    return copy.deepcopy(_SESSION.get(group,{'activeProfile':'default','data':{'default':{}}}))


def preference_save(group,value):
    _SESSION[group]=copy.deepcopy(value)


def scene_preference(group,key,default):
    from maya import cmds
    values=cmds.fileInfo(group+'.'+key,query=True)
    if not values:
        return default
    try:
        return ast.literal_eval(values[0])
    except (ValueError,SyntaxError):
        return values[0]


def helper_name(node,suffix):
    from maya import cmds
    short=node.rsplit('|',1)[-1].replace(':','_')
    uid=cmds.ls(node,uuid=True)[0].replace('-','')[:8]
    return 'mtbWS_'+short+'_'+uid+'_'+suffix


def identity(node):
    from maya import cmds
    values=cmds.ls(node.split('.',1)[0],long=True) or []
    if len(values)!=1:
        raise ValueError('Missing/ambiguous explicit node: '+node)
    return values[0],cmds.ls(values[0],uuid=True)[0]


def writable(node):
    from maya import cmds
    from maya.api import OpenMaya as om
    node,uid=identity(node)
    if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []):
        raise ValueError('Referenced/locked node: '+node)
    sel=om.MSelectionList(); sel.add(node); obj=sel.getDependNode(0)
    if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))>1:
        raise ValueError('Instanced node unsupported')
    return node,uid


def owner(node):
    from maya import cmds
    plug=node+'.'+OWNER
    return cmds.getAttr(plug) if cmds.objExists(plug) else None


def set_property(node,key,value):
    from .proxy import cmds
    if not cmds.objExists(node+'.'+key):
        cmds.addAttr(node,ln=key,dt='string')
    cmds.setAttr(node+'.'+key,str(value),type='string')
    if key in ('ebLabs_mayaControl','ebLabs_parentGroup','ebLabs_hook') and value:
        from maya import cmds as real
        uid=real.ls(value,uuid=True)[0]
        extra=key+'_uuid'
        if not cmds.objExists(node+'.'+extra):
            cmds.addAttr(node,ln=extra,dt='string')
        cmds.setAttr(node+'.'+extra,uid,type='string')


def get_property(node,key,default):
    from maya import cmds
    uidplug=node+'.'+key+'_uuid'
    if cmds.objExists(uidplug):
        uid=cmds.getAttr(uidplug)
        matches=cmds.ls(uid,long=True) or []
        if len(matches)!=1:
            raise ValueError('Metadata UUID target missing: '+key)
        return matches[0]
    plug=node+'.'+key
    return cmds.getAttr(plug) if cmds.objExists(plug) else default


def preflight(p):
    from maya import cmds
    action=p['action']
    if action=='inventory':
        c=catalog()
        return {'files':len(c['files']),'python_modules':len(c['definitions']),'definitions':sum(map(len,c['definitions'].values())),'missing_beta_modules':c['missing_version_modules'],'gui_acceptance':'not_run'}
    if action in ('import_preferences','export_preferences'):
        path=Path(p['path'])
        if not path.is_absolute() or path.suffix.lower()!='.json' or path.is_symlink():
            raise ValueError('Absolute .json path required')
        if action=='export_preferences' and (path.exists() or not path.parent.is_dir()):
            raise ValueError('Existing parent and nonexistent output required; no overwrite')
        if action=='import_preferences':
            if not path.is_file() or path.stat().st_size>8*1024*1024:
                raise ValueError('Existing preferences <=8 MiB required')
            value=json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(value,dict) or any(not isinstance(v,dict) or not isinstance(v.get('data'),dict) for v in value.values()):
                raise ValueError('Preference group objects with data profiles required')
        return dict(p)
    if action=='open_beta':
        c=catalog()
        tag=str(sys.version_info.major)+str(sys.version_info.minor)
        root=Path(p['beta_root']) if 'beta_root' in p else Path(__file__).with_name('bundle')
        if not root.is_absolute() or not (root/'eblabs_hub/WorldSpaceTools/scripts/Spaces.py').is_file():
            raise ValueError('beta_root must be an absolute original licensed distribution root containing eblabs_hub')
        if tag not in ('310','39','37','27'):
            raise RuntimeError('Supplied Beta Hub supports Python2.7/3.7/3.9/3.10 hybrid modules, current Python '+sys.version.split()[0]+' unsupported')
        missing=[r for r in c['missing_version_modules'] if r.endswith('_'+tag+'.py') and not (root/r).is_file()]
        if missing:
            raise RuntimeError('Supplied Beta Hub lacks proprietary version modules; obtain matching licensed original distribution. Missing examples: '+', '.join(missing[:5]))
        if cmds.about(batch=True):
            raise ValueError('Beta requires interactive Maya and original licensed Hub/Qt environment')
        for name,module in list(sys.modules.items()):
            if name=='eblabs_hub' or name.startswith('eblabs_hub.'):
                filename=getattr(module,'__file__',None)
                if filename and not Path(filename).resolve().is_relative_to(root.resolve()):
                    raise ValueError('Other EB Hub already imported; use fresh Maya session')
        return dict(p,beta_root=str(root.resolve()))
    if action=='open_ui':
        if cmds.about(batch=True):
            raise ValueError('Interactive Maya required')
        return dict(p)
    if action=='gimbal' and cmds.about(batch=True):
        raise ValueError('Full gimbal report window requires interactive Maya')
    if _ACTIVE:
        raise RuntimeError('Source-suite action already running')
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Undo must be enabled')
    objects=p.get('objects') or cmds.ls(selection=True,long=True) or []
    if action=='native_callback' and p['callback_ticket'] not in _TICKETS:
        raise ValueError('No valid UI callback ticket')
    if not objects:
        raise ValueError('Explicit selection required')
    targets=[]; ids=set(); original_owned=set()
    for value in objects:
        if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')):
            raise ValueError('Unique whole transforms required')
        node,uid=writable(value)
        if not cmds.objectType(node,isAType='transform') or uid in ids:
            raise ValueError('Unique transform/joint required')
        targets.append(node); ids.add(uid)
    # Existing helper nodes are admitted only through persistent candidate
    # ownership, never arbitrary name suffixes or EB Labs string metadata alone.
    for node in targets:
        token=owner(node)
        if token:
            matches=[n for n in cmds.ls(long=True) if cmds.objExists(n+'.'+OWNER)]
            owned=[n for n in matches if owner(n)==token]
            for n in owned:
                _,uid=writable(n); ids.add(uid); original_owned.add(uid)
            source=get_property(node,'ebLabs_mayaControl',None)
            if source:
                src,sid=writable(source); ids.add(sid)
                for a in TR:
                    if cmds.getAttr(src+'.'+a,lock=True):
                        raise ValueError('Source channels locked')
                    for driver in cmds.listConnections(src+'.'+a,source=True,destination=False) or []:
                        if not cmds.nodeType(driver).startswith('animCurve') and not owner(driver):
                            raise ValueError('Source acquired unsupported external driver')
                        _,did=writable(driver); ids.add(did)
        elif action=='to_local':
            raise ValueError('Only candidate-owned world controls can bake and clean safely')
        for shape in cmds.listRelatives(node,shapes=True,fullPath=True) or []:
            _,sid=writable(shape); ids.add(sid)
        for a in p.get('attributes',TR):
            if not cmds.objExists(node+'.'+a) or cmds.getAttr(node+'.'+a,lock=True):
                if not token:
                    raise ValueError('Missing/locked TR channel: '+node+'.'+a)
        for a in TR:
            for source in cmds.listConnections(node+'.'+a,source=True,destination=False) or []:
                kind=cmds.nodeType(source)
                if not kind.startswith('animCurve') and not owner(source):
                    raise ValueError('Unsupported external driver/layer: '+source)
                if kind.startswith('animCurve'):
                    _,sid=writable(source); ids.add(sid)
    # A shared animation curve may not modify an unrelated object.
    for uid in list(ids):
        matches=cmds.ls(uid,long=True) or []
        if not matches:
            continue
        n=matches[0]
        if cmds.nodeType(n).startswith('animCurve'):
            for dest in cmds.listConnections(n,source=False,destination=True) or []:
                if cmds.ls(dest,uuid=True)[0] not in ids:
                    raise ValueError('Shared animation curve has external user')
    if action in ('to_parent','copy','snap','path_locator') and len(targets)<2:
        raise ValueError('Ordered source/target selection required')
    if action=='to_local':
        for node in targets:
            root=get_property(node,'ebLabs_parentGroup',None) or node
            for child in [root]+(cmds.listRelatives(root,allDescendents=True,fullPath=True) or []):
                if cmds.ls(child,uuid=True)[0] not in original_owned:
                    raise ValueError('Helper cleanup contains foreign child; no writes permitted')
        for uid in original_owned:
            names=cmds.ls(uid,long=True) or []
            for dest in cmds.listConnections(names[0],source=False,destination=True) or []:
                if cmds.ls(dest,uuid=True)[0] not in ids:
                    raise ValueError('Owned helper has external user; cleanup refused')
    if action=='snap' and len(targets)!=2:
        raise ValueError('Snap requires exactly two nodes')
    if action in ('to_world','to_parent','ik_chain'):
        for n in targets[:-1] if action=='to_parent' else targets:
            if cmds.objExists(helper_name(n,'WorldSpaceControl')) or owner(n):
                raise ValueError('Candidate world helper already exists')
    if action=='rebuild_path' and any(not cmds.listRelatives(n,shapes=True,type='nurbsCurve') for n in targets):
        raise ValueError('Curve transforms required')
    if action=='path_locator' and not cmds.listRelatives(targets[0],shapes=True,type='nurbsCurve'):
        raise ValueError('First selected object must be curve')
    for n in targets:
        first=cmds.findKeyframe(n,which='first'); last=cmds.findKeyframe(n,which='last')
        if last-first>10000:
            raise ValueError('Original native sampling range exceeds 10000 frames')
    return dict(p,objects=targets,allowed_ids=sorted(ids),owned_ids=sorted(original_owned),file_undoable=False,gui_acceptance='not_run')


def capture_error(required=False):
    # Original optional query fallbacks are retained. Write failures are captured
    # by the proxy and become failed ToolResult even if original code catches.
    if required and _ACTIVE:
        _ERRORS.append(str(sys.exc_info()[1]))


def require_active():
    if not _ACTIVE:
        raise RuntimeError('Native scene write requires validated standard run')


def native_operation(name):
    def decorate(function):
        @wraps(function)
        def wrapped(*args,**kwargs):
            if _ACTIVE:
                return function(*args,**kwargs)
            from .tool import WorldSpaceToolsTool
            ticket=uuid.uuid4().hex
            _TICKETS[ticket]=(function,args,kwargs)
            try:
                result=WorldSpaceToolsTool().run(action='native_callback',callback_ticket=ticket)
                if not result.success:
                    raise RuntimeError(name+': '+result.message)
                return result.data.get('native_result')
            finally:
                _TICKETS.pop(ticket,None)
        return wrapped
    return decorate


def all_ids():
    from maya import cmds
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True)}


def register_created(before):
    from maya import cmds
    created=all_ids()-before
    _NEW.update(created); _ALLOWED.update(created)
    for uid in created:
        node=(cmds.ls(uid,long=True) or [None])[0]
        if node and not cmds.objExists(node+'.'+OWNER):
            cmds.addAttr(node,ln=OWNER,dt='string')
            cmds.setAttr(node+'.'+OWNER,_PLAN['owner_token'],type='string')


def flatten(values):
    for value in values:
        if isinstance(value,(list,tuple,set)):
            yield from flatten(value)
        elif isinstance(value,str):
            yield value


def check_write(command,args,kwargs):
    from maya import cmds
    require_active()
    names=list(flatten(args))
    if command in ('setAttr','addAttr','deleteAttr','setKeyframe','cutKey','pasteKey','copyKey','bufferCurve','keyframe','keyTangent','filterCurve','rebuildCurve'):
        names=list(flatten(args[:1]))
    if command in ('circle','curve','group','spaceLocator','createNode','ikHandle'):
        names=[] if kwargs.get('empty') or kwargs.get('em') or command!='group' else cmds.ls(selection=True,long=True) or []
    if command=='createNode':
        names=[]
    if command=='rename':
        names=names[:1]
    if command=='connectAttr':
        names=names[-1:]
    if command=='pathAnimation':
        names=names[-1:]
    # Every actual writable argument must resolve within validated objects or
    # actual newly created UUIDs, not glob patterns/prefix/name reconstruction.
    for value in names:
        node,uid=identity(value)
        if uid not in _ALLOWED:
            raise ValueError('Write exceeds validated scope: '+value)
        writable(node)
        if command=='delete':
            is_curve=cmds.nodeType(node).startswith('animCurve')
            if uid not in _NEW and uid not in _PLAN['owned_ids'] and not is_curve:
                raise ValueError('Only owned helpers or validated target animation curves may be deleted: '+node)
            for dest in cmds.listConnections(node,source=False,destination=True) or []:
                if cmds.ls(dest,uuid=True)[0] not in _ALLOWED:
                    raise ValueError('Delete would affect external connection: '+dest)
            for child in cmds.listRelatives(node,allDescendents=True,fullPath=True) or []:
                if cmds.ls(child,uuid=True)[0] not in _NEW|set(_PLAN['owned_ids']):
                    raise ValueError('Helper contains foreign child; cleanup refused')
    if command=='delete' and not names:
        raise ValueError('No implicit delete scope')


def execute(p):
    global _ACTIVE,_API,_PLAN,_ALLOWED,_NEW,_ERRORS
    from maya import cmds
    plan=preflight(p)
    action=p['action']
    if action=='inventory':
        return plan
    if action=='export_preferences':
        with Path(p['path']).open('x',encoding='utf8') as stream:
            json.dump(_SESSION,stream,ensure_ascii=False,indent=2)
        return {'path':p['path'],'external_file_undoable':False}
    if action=='import_preferences':
        _SESSION.clear(); _SESSION.update(json.loads(Path(p['path']).read_text(encoding='utf-8-sig')))
        return {'groups':list(_SESSION),'session_only':True}
    if action=='open_beta':
        root=plan['beta_root']
        if root not in sys.path:
            sys.path.insert(0,root)
        result=importlib.import_module('eblabs_hub.WorldSpaceTools.scripts.Spaces').launch()
        return {'beta_root':root,'native_result':str(result),'original_license_checks':'unchanged','gui_acceptance':'not_run'}
    native=importlib.import_module(__package__+'.native')
    if action=='open_ui':
        native.window.load()
        return {'window':'mtbWS2','full_native_ui':True}
    selection=cmds.ls(selection=True,long=True) or []
    time=cmds.currentTime(query=True)
    auto=cmds.autoKeyframe(query=True,state=True)
    ns=cmds.namespaceInfo(currentNamespace=True)
    blend=cmds.optionVar(query='animBlendingOpt') if cmds.optionVar(exists='animBlendingOpt') else None
    _ACTIVE=True; _API=action!='native_callback'; _PLAN=dict(plan,owner_token=uuid.uuid4().hex)
    _ALLOWED=set(plan['allowed_ids']); _NEW=set(); _ERRORS=[]
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        cmds.select(plan['objects'],replace=True)
        native.SuspendUI.setBatchMode(True); native.ProgressBar.setBatchMode(True)
        interval=(p['start'],p['end']) if 'start' in p and not p.get('on_keys',True) else False
        attrs=p.get('attributes',TR)
        if action in ('to_world','to_parent','ik_chain'):
            values=plan['objects'][:-1] if action=='to_parent' else plan['objects']
            parent=plan['objects'][-1] if action=='to_parent' else False
            if action=='ik_chain':
                result=native.WorldSpaceFunctions.toIKChainSpaceExec(values,attributes=attrs,bakeTimeRange=interval,fastMode=True)
            else:
                result=native.WorldSpaceFunctions.toWorldSpaceExec(values,parentSpaceObject=parent,attributes=attrs,bakeTimeRange=interval,fastMode=True)
        elif action=='to_local':
            result=native.WorldSpaceFunctions.toLocalSpaceExec(plan['objects'],bakeTimeRange=interval,fastMode=True)
        elif action=='create_paths':
            result=native.PathSpaces.createPathsForSelection()
        elif action=='path_locator':
            result=native.PathSpaces.createAnimatedLocatorOnPath()
        elif action=='rebuild_path':
            result=native.PathSpaces.rebuildCurve(p['spans'],plan['objects'])
        elif action=='copy':
            result=native.CopyAtoB.copyAtoB(plan['objects'][1:],plan['objects'][0],bakeTimeRange=interval,maintainOffset=p['maintain_offset'])
        elif action=='snap':
            result=native.CopyAtoB.snapAtoB_button()
        elif action in ('child_cog','parent_cog'):
            result=native.Functions.addCog(cogType=action.split('_')[0])
        elif action=='gimbal':
            result=native.Functions.plotGimbalInfo()
        elif action=='native_callback':
            function,args,kwargs=_TICKETS[p['callback_ticket']]
            result=function(*args,**kwargs)
        else:
            raise ValueError('Action has no implementation')
        if _ERRORS:
            raise RuntimeError('; '.join(dict.fromkeys(_ERRORS)))
        return {'action':action,'native_result':result,'created_uuids':sorted(_NEW),'gui_acceptance':'not_run'}
    finally:
        cmds.autoKeyframe(state=auto)
        if blend is not None:
            cmds.optionVar(intValue=('animBlendingOpt',blend))
        elif cmds.optionVar(exists='animBlendingOpt'):
            cmds.optionVar(remove='animBlendingOpt')
        cmds.currentTime(time,edit=True)
        cmds.namespace(setNamespace=ns)
        valid=[n for n in selection if cmds.objExists(n)]
        cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        _ACTIVE=False; _API=False; _PLAN={}; _ALLOWED=set(); _NEW=set()
