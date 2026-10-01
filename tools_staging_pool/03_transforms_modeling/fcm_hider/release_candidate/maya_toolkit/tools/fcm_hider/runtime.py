import ast
import importlib
import json
from pathlib import Path
import re
import sys
import uuid
from .tool import SETS

ALL='All_Sets_Hider'
SETTINGS='FCM_Hider_Settings'
OWNER='mtbFCMOwner'
_ACTIVE=False
_PLAN={}
_SYSTEM='mtbFCM'
_ALLOWED=set()
_ERRORS=[]
_TICKETS={}


def current_system(): return _SYSTEM


def names(system): return {name:system+':'+name for name in [ALL]+SETS+[SETTINGS]}


def bind_globals(env):
    env.update(names(_SYSTEM)); env['namespaceHider']=_SYSTEM+':'
    env['namespaceHiderForWindow']=_SYSTEM


def resolve(value):
    from maya import cmds
    from maya.api import OpenMaya as om
    if not isinstance(value,str) or any(c in value for c in ('*','?',';','"','\n','\r','\\')):
        raise ValueError('Explicit node/component required')
    matches=cmds.ls(value,long=True,flatten=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous target: '+value)
    match=matches[0]; node=match.split('.',1)[0]
    sel=om.MSelectionList(); sel.add(node); obj=sel.getDependNode(0)
    if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('Instances unsupported')
    if '.' in match and not re.search(r'\.f\[\d+\]$',match): raise ValueError('Only mesh faces or whole objects supported')
    if '.f[' in match:
        index=int(match.rsplit('[',1)[1][:-1])
        if index>=cmds.polyEvaluate(node,face=True): raise ValueError('Face index exceeds current topology')
    return match,node,cmds.ls(node,uuid=True)[0]


def writable(node,system_node=False):
    from maya import cmds
    if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []): raise ValueError('Referenced/locked writable member: '+node)
    for attr in () if system_node else ('visibility','lodVisibility','template','overrideDisplayType','displayType'):
        if cmds.objExists(node+'.'+attr) and (cmds.getAttr(node+'.'+attr,lock=True) or cmds.listConnections(node+'.'+attr,source=True,destination=False)):
            raise ValueError('Locked/driven display channel: '+node+'.'+attr)


def members(system):
    from maya import cmds
    result=[]
    for key in SETS:
        name=names(system)[key]
        if cmds.objExists(name): result.extend(cmds.sets(name,query=True) or [])
    return sorted(set(result))


def path_check(path,write=False):
    path=Path(path)
    if not path.is_absolute() or path.suffix.lower()!='.json' or path.is_symlink(): raise ValueError('Absolute .json path required; legacy executable .py unsupported')
    if write:
        if path.exists() or not path.parent.is_dir(): raise ValueError('Output must not exist and parent must exist')
    elif not path.is_file() or path.stat().st_size>16*1024*1024: raise ValueError('Existing JSON <=16 MiB required')
    return path


def read_sets(path):
    value=json.loads(path_check(path).read_text(encoding='utf-8-sig'))
    if not isinstance(value,dict) or set(value)!={'format','sets'} or value['format']!='mtbFCM-1' or not isinstance(value['sets'],dict) or set(value['sets'])!=set(SETS): raise ValueError('Complete mtbFCM-1 nine-set JSON required')
    for content in value['sets'].values():
        if not isinstance(content,list) or len(content)>100000 or any(not isinstance(n,str) or not n for n in content) or len(content)!=len(set(content)): raise ValueError('Unique finite set members required')
    return value


def mirror_plan(tolerance,system):
    from maya import cmds
    from maya.api import OpenMaya as om
    from math import dist
    pairs=[('R_','L_'),('_R_','_L_'),('_R','_L'),('r_','l_'),('_r_','_l_'),('_r','_l'),('Right','Left'),('right','left'),('rt','lf'),('Rt','Lf'),('RGT','LFT'),('Rgt','Lft')]
    output={}
    for source,target in (('Arm_R_Hider','Arm_L_Hider'),('Leg_R_Hider','Leg_L_Hider')):
        values=[]
        for member in cmds.sets(names(system)[source],query=True) or []:
            member,node,uid=resolve(member)
            if '.f[' in member:
                sel=om.MSelectionList(); sel.add(node); dag=sel.getDagPath(0)
                if dag.node().hasFn(om.MFn.kTransform): dag.extendToShape()
                fn=om.MFnMesh(dag); pts=fn.getPoints(om.MSpace.kObject)
                index=int(member.rsplit('[',1)[1][:-1]); vertices=fn.getPolygonVertices(index)
                mapped=[]
                for vertex in vertices:
                    p=pts[vertex]; reflected=(-p.x,p.y,p.z)
                    hits=[i for i,q in enumerate(pts) if dist(reflected,(q.x,q.y,q.z))<=tolerance]
                    if len(hits)!=1: raise ValueError('Mesh is not uniquely symmetric within tolerance')
                    mapped.append(hits[0])
                hits=[i for i in range(fn.numPolygons) if set(fn.getPolygonVertices(i))==set(mapped)]
                if len(hits)!=1: raise ValueError('No unique mirrored face topology')
                values.append(node+'.f['+str(hits[0])+']')
            else:
                leaf=node.rsplit('|',1)[-1]
                matches=[]
                for old,new in pairs:
                    if old in leaf:
                        candidate=leaf.replace(old,new)
                        if candidate!=leaf and cmds.objExists(candidate): matches.append(resolve(candidate)[0])
                matches=sorted(set(matches))
                if len(matches)!=1: raise ValueError('Mirror counterpart missing or ambiguous: '+member)
                values.append(matches[0])
        output[target]=sorted(set(values))
    return output


def preflight(p):
    from maya import cmds
    action=p['action']; system=p['system']
    if not re.fullmatch(r'mtbFCM[A-Za-z0-9_]*',system): raise ValueError('Private root namespace must start mtbFCM and contain identifiers only')
    mapping=names(system); owned=[]
    for key,name in mapping.items():
        if cmds.objExists(name):
            _,node,uid=resolve(name)
            expected='transform' if key==SETTINGS else 'objectSet'
            if cmds.nodeType(node)!=expected or not cmds.objExists(node+'.'+OWNER) or cmds.getAttr(node+'.'+OWNER)!=system: raise ValueError('Foreign collision at system node: '+name)
            writable(node,True); owned.append(uid)
    if action not in ('inspect','initialize','open_ui') and len(owned)!=len(mapping): raise ValueError('Initialize complete owned system before this action')
    if cmds.objExists(mapping[ALL]):
        content=cmds.sets(mapping[ALL],query=True) or []
        actual={cmds.ls(n,uuid=True)[0] for n in content}
        expected={cmds.ls(mapping[k],uuid=True)[0] for k in SETS if cmds.objExists(mapping[k])}
        if actual!=expected: raise ValueError('Aggregate set membership changed or contains foreign sets')
    if action=='open_ui' and cmds.about(batch=True): raise ValueError('Full native UI requires interactive Maya')
    if action=='native_callback' and p['callback_ticket'] not in _TICKETS: raise ValueError('Invalid native callback ticket')
    values=members(system)
    if action in ('add','remove','lock_selection','native_callback'):
        values+=p.get('objects') or cmds.ls(selection=True,long=True,flatten=True) or []
    if action in ('add','remove','lock_selection') and not (p.get('objects') or cmds.ls(selection=True)):
        raise ValueError('Explicit member selection required')
    if action=='import_sets':
        data=read_sets(p['path']); values += [n for v in data['sets'].values() for n in v]
    if action=='export_sets': path_check(p['path'],True)
    mirrored=None
    if action=='mirror':
        mirrored=mirror_plan(p['mirror_tolerance'],system)
        values+=[n for v in mirrored.values() for n in v]
    if action=='native_callback':
        source=_TICKETS[p['callback_ticket']]
        if 'mirrorHider' in source:
            mirrored=mirror_plan(0.0001,system); values+=[n for v in mirrored.values() for n in v]
    allowed=set(owned); explicit=[]
    for value in sorted(set(values)):
        # Face ranges are expanded explicitly first; no glob strings admitted.
        expanded=cmds.ls(value,long=True,flatten=True) or []
        if not expanded: raise ValueError('Stale set membership: '+value)
        for item in expanded:
            match,node,uid=resolve(item); writable(node); allowed.add(uid); explicit.append(match)
            if cmds.nodeType(node) not in ('transform','joint','mesh','nurbsCurve','nurbsSurface','annotationShape'): raise ValueError('Members must be geometry/control objects or faces, no nested arbitrary sets')
            for shape in cmds.listRelatives(node,shapes=True,fullPath=True) or []:
                _,shape,sid=resolve(shape); writable(shape); allowed.add(sid)
    # Layer unlock is permitted only if every layer member lies in this scope.
    layers=[]
    if action in ('unlock_visible','unlock_meshes','native_callback'):
        for uid in list(allowed):
            node=(cmds.ls(uid,long=True) or [None])[0]
            for layer in cmds.listConnections(node,type='displayLayer') or []:
                if layer=='defaultLayer': continue
                content=cmds.editDisplayLayerMembers(layer,query=True,fullNames=True) or []
                if all(cmds.ls(n,uuid=True)[0] in allowed for n in content):
                    writable(layer); allowed.add(cmds.ls(layer,uuid=True)[0]); layers.append(layer)
    callback_cleanup=action=='native_callback' and any(t in _TICKETS[p['callback_ticket']] for t in ('removeAllHider','confirmRemoveAllHider'))
    if action=='cleanup' or callback_cleanup:
        settings=mapping[SETTINGS]
        if cmds.listRelatives(settings,allDescendents=True,fullPath=True): raise ValueError('Settings contains foreign children; refuse deletion')
        for name in mapping.values():
            for dest in cmds.listConnections(name,source=False,destination=True) or []:
                if cmds.ls(dest,uuid=True)[0] not in set(owned): raise ValueError('System node has foreign consumer; refuse deletion')
    if action=='lock_selection' or action=='native_callback' and 'lockSelection' in _TICKETS[p['callback_ticket']]:
        for value in p.get('objects') or cmds.ls(selection=True,long=True) or []:
            node=value.split('.',1)[0]
            for child in cmds.listRelatives(node,children=True,fullPath=True) or []:
                if cmds.ls(child,uuid=True)[0] not in allowed: raise ValueError('Lock pickWalk would affect unselected child')
    return dict(p,allowed_ids=sorted(allowed),owned_ids=owned,members=sorted(set(explicit)),layers=sorted(set(layers)),mirrored=mirrored,gui_acceptance='not_run',external_file_undoable=False)


def require_active():
    if not _ACTIVE: raise RuntimeError('FCM scene writes require standard validated run')


def query_members(env):
    from maya import cmds
    content=cmds.sets(env['setHider'],query=True) or []
    env['allSet']=content
    env['polys']=cmds.filterExpand(content,selectionMask=34,fullPath=True) or []
    env['transformAndShapeSet']=[n for n in content if '.' not in n and cmds.nodeType(n) in ('transform','joint','mesh','nurbsCurve','nurbsSurface','annotationShape')]
    shapes=[]
    for face in env['polys']:
        node=face.split('.',1)[0]
        shape=cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True) or [node]
        for s in shape:
            if cmds.nodeType(s)=='mesh' and [s] not in shapes: shapes.append([s])
    env['shapes']=shapes


def clear_current_set():
    from .proxy import cmds
    native=importlib.import_module(__package__+'.native')
    canonical=names(_SYSTEM)[native.setHider.rsplit(':',1)[-1]]
    native.setHider=canonical; native.showSet()
    content=cmds.sets(canonical,query=True) or []
    if content: cmds.sets(content,edit=True,remove=canonical)
    native.setHider=canonical; native.checkStateIcon()


def show_member_faces():
    from .proxy import cmds
    faces=[n for n in _PLAN['members'] if '.f[' in n]
    if faces: cmds.showHidden(faces)
    for f in faces: cmds.polyHole(f,assignHole=0)


def hide_member_polys(faces):
    from .proxy import cmds
    if faces: cmds.hide(faces)


def show_member_polys(faces):
    from .proxy import cmds
    if faces: cmds.showHidden(faces)


def unlock_members(mesh_only=False):
    from .proxy import cmds
    for member in _PLAN['members']:
        node=member.split('.',1)[0]
        shapes=cmds.listRelatives(node,shapes=True,fullPath=True) or []
        if mesh_only and not (cmds.nodeType(node)=='mesh' or any(cmds.nodeType(s)=='mesh' for s in shapes)): continue
        for target in [node]+shapes:
            for attr,value in (('overrideDisplayType',0),('template',0)):
                if cmds.objExists(target+'.'+attr): cmds.setAttr(target+'.'+attr,value)
    for layer in _PLAN['layers']: cmds.setAttr(layer+'.displayType',0)


def mirror_sets():
    from .proxy import cmds
    require_active()
    mirrored=_PLAN['mirrored']
    if mirrored is None: raise ValueError('Mirrored counterparts must be completely preflighted')
    for key,content in mirrored.items():
        if content: cmds.sets(content,edit=True,forceElement=names(_SYSTEM)[key])
    return mirrored


def mirror_faces_into(values,target):
    # Original UI calls full mirrorHider; lower helper retains an explicit,
    # validated topology path instead of modifying global reflection mode.
    return mirror_sets()


def file_dialog(action):
    from maya import cmds
    paths=cmds.fileDialog2(fileMode=0 if action=='export_sets' else 1,fileFilter='Hider JSON (*.json)') or []
    if not paths: return None
    from .tool import FcmHiderTool
    result=FcmHiderTool().run(action=action,system=_SYSTEM,path=paths[0])
    if not result.success: raise RuntimeError(result.message)
    return result.data


def help_window():
    from maya import cmds
    if cmds.window('mtbFCMHelp',exists=True): cmds.deleteUI('mtbFCMHelp')
    window=cmds.window('mtbFCMHelp',title='FCM Hider usage and source gaps',widthHeight=(540,380))
    cmds.columnLayout(adjustableColumn=True)
    cmds.scrollField(editable=False,wordWrap=True,text='Body sets store objects; Extra sets may store shapes and faces. Right click Add / Remove / Select / Clear. Toggle visibility, show all or mirror right arm/leg to left. Unlock and show-hidden now affect only Hider members. Export/import safe JSON to new temporary files. Scene writes use Undo; files and Maya selection masks do not. Original three help images were not supplied. See acceptance.md before production use.',height=310)
    cmds.showWindow(window)
    return window


def callback(source):
    source=source.rstrip(',')
    if source not in _TICKETS.values():
        # Only exact original bundled callback literals (or the fixed dynamic
        # focus command) are accepted, never user file/text execution.
        c=json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf8'))
        if source not in c['callbacks'] and source!='ShowOrHideAllSetsButton()' and source not in ('setHider = Head_Hider; showOrHideButton()','setHider = Torso_Hider; showOrHideButton()','setHider = Arm_R_Hider; showOrHideButton()','setHider = Arm_L_Hider; showOrHideButton()','setHider = Leg_R_Hider; showOrHideButton()','setHider = Leg_L_Hider; showOrHideButton()','setHider = Extra_One_Hider; showOrHideButton()','setHider = Extra_Two_Hider; showOrHideButton()','setHider = Extra_Three_Hider; showOrHideButton()','setHider = Head_Hider','setHider = Torso_Hider','setHider = Arm_R_Hider','setHider = Arm_L_Hider','setHider = Leg_R_Hider','setHider = Leg_L_Hider','setHider = Extra_One_Hider','setHider = Extra_Two_Hider','setHider = Extra_Three_Hider'):
            raise ValueError('Unrecognized native callback text')
    ast.parse(source)
    def invoke(*unused):
        if source in ('saveSetsHider()','LoadSetsHider()'):
            return file_dialog('export_sets' if source=='saveSetsHider()' else 'import_sets')
        from .tool import FcmHiderTool
        ticket=uuid.uuid4().hex; _TICKETS[ticket]=source
        try:
            result=FcmHiderTool().run(action='native_callback',system=_SYSTEM,callback_ticket=ticket)
            if not result.success: raise RuntimeError(result.message)
            return result.data
        finally: _TICKETS.pop(ticket,None)
    return invoke


def execute(p):
    global _ACTIVE,_PLAN,_SYSTEM,_ALLOWED,_ERRORS
    from maya import cmds
    plan=preflight(p); action=p['action']; system=p['system']
    if action=='inspect': return plan
    if action=='export_sets':
        data={'format':'mtbFCM-1','sets':{k:cmds.sets(names(system)[k],query=True) or [] for k in SETS}}
        with path_check(p['path'],True).open('x',encoding='utf8') as stream: json.dump(data,stream,ensure_ascii=False,indent=2)
        return {'path':p['path'],'external_file_undoable':False}
    native=importlib.import_module(__package__+'.native')
    selection=cmds.ls(selection=True,long=True,flatten=True) or []; ns=cmds.namespaceInfo(currentNamespace=True)
    auto=cmds.autoKeyframe(query=True,state=True)
    _ACTIVE=True; _PLAN=plan; _SYSTEM=system; _ALLOWED=set(plan['allowed_ids']); _ERRORS=[]
    try:
        cmds.autoKeyframe(state=False); cmds.namespace(setNamespace=':')
        if not cmds.namespace(exists=system): cmds.namespace(add=system)
        bind_globals(native.__dict__)
        if action in ('initialize','open_ui'):
            native.createHiderInTheScene()
            if action=='open_ui': native.HiderUI()
        elif action=='import_sets':
            from .proxy import cmds as protected
            data=read_sets(p['path'])
            for key,content in data['sets'].items():
                native.setHider=names(system)[key]; native.removeSet()
                if content: protected.sets(content,edit=True,forceElement=names(system)[key])
            native.checkAllIconSets()
        else:
            native.setHider=names(system)[p.get('set','Head_Hider')]
            if 'objects' in p: cmds.select(p['objects'],replace=True)
            if action=='add': native.shapeMode='On' if p['shape_mode'] else 'Off'; native.addSelectionToSet()
            elif action=='remove': native.removeSelection()
            elif action=='clear': native.removeSet()
            elif action=='hide': native.hideSet()
            elif action=='show': native.showSet()
            elif action=='toggle': native.showOrHideButton()
            elif action in ('show_all','hide_all'): native.choise='show' if action=='show_all' else 'hide'; native.ShowOrHideAllSets()
            elif action=='clear_body': native.removeAllBodySets()
            elif action=='clear_extra': native.removeAllExtraSets()
            elif action=='cleanup': native.removeAllHider()
            elif action=='mirror': mirror_sets()
            elif action=='unlock_visible': unlock_members(False)
            elif action=='unlock_meshes': unlock_members(True)
            elif action=='lock_selection': native.lockSelection()
            elif action=='show_faces': show_member_faces()
            elif action=='native_callback':
                # The source is an exact internally registered original UI
                # callback, never loaded from a file or accepted as API code.
                source=_TICKETS[p['callback_ticket']]
                exec(compile(source,'<trusted bundled FCM callback>','exec'),native.__dict__)
            else: raise ValueError('Unimplemented action')
        if _ERRORS: raise RuntimeError('; '.join(dict.fromkeys(_ERRORS)))
        return {'action':action,'system':system,'members':members(system),'gui_acceptance':'not_run'}
    finally:
        cmds.namespace(setNamespace=ns); cmds.autoKeyframe(state=auto)
        valid=[n for n in selection if cmds.objExists(n)]
        keep_selection=action=='native_callback' and any(t in _TICKETS[p['callback_ticket']] for t in ('selectSet','cmds.select','polySelectConstraint','growSelection','filterOnlyCurves'))
        if not keep_selection:
            cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        _ACTIVE=False; _PLAN={}; _ALLOWED=set()
