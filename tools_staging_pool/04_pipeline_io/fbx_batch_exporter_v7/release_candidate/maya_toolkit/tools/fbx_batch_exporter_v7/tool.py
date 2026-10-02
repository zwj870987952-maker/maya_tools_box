"""Grouped object/range FBX export, scene bake/SSC and portable settings."""
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from maya_toolkit.framework import BaseMayaTool,ToolResult

FLAGS={'input_connections':'FBXExportInputConnections','ascii':'FBXExportInAscii','smoothing_groups':'FBXExportSmoothingGroups','smooth_mesh':'FBXExportSmoothMesh',
       'referenced_assets':'FBXExportReferencedAssetsContent','triangulate':'FBXExportTriangulate','skins':'FBXExportSkins','cameras':'FBXExportCameras','embedded_textures':'FBXExportEmbeddedTextures'}
DEFAULTS=dict(export_animation=True,input_connections=False,ascii=True,smoothing_groups=True,smooth_mesh=True,referenced_assets=True,triangulate=False,skins=True,cameras=True,embedded_textures=True,up_axis='Y',file_version='FBX202000')
VERSIONS=['FBX202000','FBX201900','FBX201800','FBX201600','FBX201400','FBX201300','FBX201200','FBX201100','FBX201000','FBX200900']

def safe_name(value):
    if not isinstance(value,str) or not value or len(value)>150 or any(c in value for c in '/\\<>:"|?*\n\r') or value.endswith((' ','.')) or value in ('.','..'): raise ValueError('Portable filename/prefix required')
    if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',value): raise ValueError('Windows reserved filename')
    return value

def number(value):
    if type(value) not in (int,float) or not math.isfinite(value): raise ValueError('Finite numeric frame required')
    return value

def options(values):
    if not isinstance(values,dict) or set(values)-set(DEFAULTS): raise ValueError('Unknown FBX options')
    result=dict(DEFAULTS,**values)
    for key in set(DEFAULTS)-{'up_axis','file_version'}:
        if type(result[key]) is not bool: raise ValueError('FBX boolean option required')
    if result['up_axis'] not in ('Y','Z') or result['file_version'] not in VERSIONS: raise ValueError('Invalid axis/version')
    return result

def normalize(values):
    p=dict(action='inspect',jobs=None,output_dir=None,prefix='',options={},objects=None,start=None,end=None,settings_path=None,configuration=None)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','export','bake','disable_ssc','save_settings','load_settings'): raise ValueError('Invalid action')
    p['options']=options(p['options'])
    if p['prefix']!='': safe_name(p['prefix'])
    if p['action'] in ('save_settings','load_settings'):
        if not isinstance(p['settings_path'],str) or not Path(p['settings_path']).is_absolute() or Path(p['settings_path']).suffix.lower()!='.json': raise ValueError('Explicit absolute JSON path required')
        if p['action']=='save_settings': p['configuration']=configuration(p['configuration'])
    elif p['action'] in ('bake','disable_ssc'):
        if not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n or any(c in n for c in '*?\n\r') for n in p['objects']): raise ValueError('Exact object list required')
        if p['action']=='bake':
            number(p['start']); number(p['end'])
            if p['start']>p['end'] or p['end']-p['start']>100000: raise ValueError('Ordered bounded bake range required')
    else:
        if not isinstance(p['jobs'],list) or not 1<=len(p['jobs'])<=1000: raise ValueError('1..1000 grouped jobs required')
        for row in p['jobs']:
            if not isinstance(row,dict) or set(row)-{'objects','start','end','filename'} or not {'objects','start','end'}<=set(row): raise ValueError('Each job requires objects/start/end')
            if not isinstance(row['objects'],list) or not row['objects'] or any(not isinstance(n,str) or not n or any(c in n for c in '*?\n\r') for n in row['objects']): raise ValueError('Exact group objects required')
            number(row['start']); number(row['end'])
            if row['start']>row['end'] or row['end']-row['start']>100000: raise ValueError('Ordered bounded frame range required')
            if 'filename' in row and (not safe_name(row['filename']).lower().endswith('.fbx')): raise ValueError('Filename must end .fbx')
        if p['output_dir'] is not None and (not isinstance(p['output_dir'],str) or not Path(p['output_dir']).is_absolute()): raise ValueError('Absolute output directory required')
    return p

def configuration(value):
    if not isinstance(value,dict): raise ValueError('Settings configuration required')
    if 'objects' in value and 'time_ranges' in value:
        # Both supplied original settings versions use these names.
        if not isinstance(value['objects'],list) or not isinstance(value['time_ranges'],list) or len(value['objects'])!=len(value['time_ranges']): raise ValueError('Legacy object/range rows must pair exactly')
        jobs=[]
        for objects,frame_range in zip(value['objects'],value['time_ranges']):
            if not isinstance(objects,str) or not isinstance(frame_range,str): raise ValueError('Invalid legacy row')
            frames=frame_range.split(',')
            if len(frames)!=2: raise ValueError('Invalid legacy range')
            jobs.append({'objects':objects.split(),'start':float(frames[0]),'end':float(frames[1])})
        keys={'inputConnectionsCheckBox':'input_connections','asciiCheckBox':'ascii','smoothingGroupsCheckBox':'smoothing_groups','smoothMeshCheckBox':'smooth_mesh',
              'referencedAssetsContentCheckBox':'referenced_assets','triangulateCheckBox':'triangulate','skinsCheckBox':'skins','camerasCheckBox':'cameras','embeddedTexturesCheckBox':'embedded_textures','upAxisMenu':'up_axis','fileVersionMenu':'file_version','export_animation':'export_animation'}
        value={'version':1,'jobs':jobs,'prefix':value.get('prefix',''),'options':{target:value[key] for key,target in keys.items() if key in value}}
    if set(value)-{'version','jobs','prefix','options'} or value.get('version')!=1: raise ValueError('Unsupported settings schema')
    checked=normalize(dict(jobs=value.get('jobs'),prefix=value.get('prefix',''),options=value.get('options',{})))
    return {'version':1,'jobs':checked['jobs'],'prefix':checked['prefix'],'options':checked['options']}

def resolve(name):
    from maya import cmds
    matches=cmds.ls(name,long=True) or []
    if len(matches)!=1 or '.' in matches[0] or not cmds.objectType(matches[0],isAType='transform'): raise ValueError('Exact transform/joint required: '+name)
    return matches[0]

def plan(p):
    from maya import cmds
    if p['action'] in ('save_settings','load_settings'):
        path=Path(p['settings_path'])
        if p['action']=='save_settings':
            if path.exists() or path.is_symlink() or not path.parent.is_dir(): raise ValueError('Settings require a new JSON in existing directory')
            return {'path':str(path),'configuration':p['configuration']}
        if not path.is_file() or path.stat().st_size>2*1024*1024: raise ValueError('Missing/oversized settings JSON')
        return {'path':str(path),'configuration':configuration(json.loads(path.read_text(encoding='utf-8-sig')))}
    if p['action'] in ('bake','disable_ssc'):
        if not cmds.undoInfo(query=True,state=True): raise ValueError('Maya Undo required')
        targets=sorted({resolve(n) for n in p['objects']})
        if p['action']=='bake':
            targets=sorted(set(targets)|{n for root in targets for n in cmds.listRelatives(root,allDescendents=True,fullPath=True) or []})
            targets=[n for n in targets if not cmds.objectType(n,isAType='constraint')]
        for node in targets:
            if cmds.referenceQuery(node,isNodeReferenced=True) or cmds.lockNode(node,query=True,lock=True)[0]: raise ValueError('Referenced/locked bake or SSC target')
            attrs=['segmentScaleCompensate'] if p['action']=='disable_ssc' else cmds.listAttr(node,keyable=True,multi=True) or []
            if p['action']=='disable_ssc' and cmds.nodeType(node)!='joint': raise ValueError('SSC targets must be joints')
            for attr in attrs:
                plug=node+'.'+attr
                if cmds.getAttr(plug,lock=True): raise ValueError('Locked target attribute: '+plug)
                if p['action']=='disable_ssc' and cmds.listConnections(plug,source=True,destination=False): raise ValueError('Driven SSC attribute')
        return {'targets':targets,'range':[p['start'],p['end']] if p['action']=='bake' else None}
    directory=Path(p['output_dir']) if p['output_dir'] else Path(cmds.file(query=True,sceneName=True)).parent
    if p['output_dir'] is None and not cmds.file(query=True,sceneName=True): raise ValueError('Unsaved scene needs explicit output_dir')
    if not directory.is_dir(): raise ValueError('Existing output directory required')
    tasks=[]; reserved=set()
    for i,row in enumerate(p['jobs']):
        targets=sorted({resolve(n) for n in row['objects']})
        leaf=targets[0].rsplit('|',1)[-1]
        base=leaf.split(':',1)[0]+'_'+str(row['start'])+'_'+str(row['end']) if ':' in leaf else leaf+'_'+str(i)
        base=re.sub(r'[^\w.-]','_',base)
        filename=row.get('filename',(p['prefix']+'_' if p['prefix'] else '')+base+'.fbx'); safe_name(filename)
        output=directory/filename; counter=1
        while output.exists() or output.is_symlink() or str(output.resolve()).casefold() in reserved:
            output=directory/(Path(filename).stem+'_'+str(counter)+'.fbx'); counter+=1
            if counter>10000: raise ValueError('Too many output collisions')
        reserved.add(str(output.resolve()).casefold()); tasks.append({'objects':targets,'start':row['start'],'end':row['end'],'output':str(output)})
    return {'tasks':tasks,'options':p['options'],'count':len(tasks),'external_files_undoable':False}

@contextmanager
def preserve_session():
    from maya import cmds
    enabled=cmds.undoInfo(query=True,state=True); selected=cmds.ls(selection=True,long=True) or []; time=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
    playback={key:cmds.playbackOptions(query=True,**{key:True}) for key in ('animationStartTime','animationEndTime','minTime','maxTime')}
    cmds.undoInfo(stateWithoutFlush=False)
    try: yield
    finally:
        cmds.playbackOptions(**playback)
        if cmds.currentTime(query=True)!=time: cmds.currentTime(time)
        cmds.autoKeyframe(state=auto); valid=[n for n in selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        cmds.undoInfo(stateWithoutFlush=enabled)

def mel_string(value): return json.dumps(str(value).replace('\\','/'),ensure_ascii=False)

@contextmanager
def fbx_settings():
    from maya import mel
    commands=list(FLAGS.values())+['FBXExportBakeComplexAnimation','FBXExportBakeComplexStep','FBXExportBakeComplexStart','FBXExportBakeComplexEnd','FBXExportUpAxis','FBXExportFileVersion']
    state={cmd:mel.eval(cmd+' -q') for cmd in commands}; animation=mel.eval('FBXProperty "Export|IncludeGrp|Animation" -q')
    try: yield
    finally:
        errors=[]
        for command,value in state.items():
            argument=mel_string(value) if command=='FBXExportFileVersion' else str(value).lower() if command=='FBXExportUpAxis' else 'true' if value is True else 'false' if value is False else str(value)
            try: mel.eval(command+(' ' if command in ('FBXExportUpAxis','FBXExportFileVersion') else ' -v ')+argument)
            except RuntimeError as exc: errors.append(str(exc))
        try: mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v '+('true' if animation else 'false'))
        except RuntimeError as exc: errors.append(str(exc))
        if errors: raise RuntimeError('FBX settings restore failed: '+'; '.join(errors))

def export(data):
    from maya import cmds,mel
    if not cmds.pluginInfo('fbxmaya',query=True,loaded=True): cmds.loadPlugin('fbxmaya',quiet=True)
    outputs=[]; opts=data['options']
    with preserve_session(),fbx_settings():
        for task in data['tasks']:
            for key,command in FLAGS.items(): mel.eval(command+' -v '+('true' if opts[key] else 'false'))
            mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v '+('true' if opts['export_animation'] else 'false'))
            mel.eval('FBXExportBakeComplexAnimation -v '+('true' if opts['export_animation'] else 'false'))
            for command,value in (('FBXExportBakeComplexStep',1),('FBXExportBakeComplexStart',task['start']),('FBXExportBakeComplexEnd',task['end'])): mel.eval(command+' -v '+str(value))
            mel.eval('FBXExportUpAxis '+opts['up_axis'].lower()); mel.eval('FBXExportFileVersion '+mel_string(opts['file_version']))
            cmds.playbackOptions(animationStartTime=task['start'],animationEndTime=task['end'],minTime=task['start'],maxTime=task['end']); cmds.select(task['objects'],replace=True,hierarchy=True)
            target=Path(task['output'])
            with tempfile.TemporaryDirectory(prefix='mtb_fbx_',dir=str(target.parent)) as directory:
                generated=Path(directory)/'result.fbx'; mel.eval('FBXExport -f '+mel_string(generated)+' -s')
                if not generated.is_file() or not generated.stat().st_size: raise RuntimeError('FBX exporter produced no file')
                owned=False
                try:
                    with target.open('xb') as writer:
                        owned=True
                        with generated.open('rb') as reader: shutil.copyfileobj(reader,writer)
                        writer.flush(); os.fsync(writer.fileno())
                except Exception:
                    if owned: target.unlink(missing_ok=True)
                    raise
            outputs.append(dict(task,bytes=target.stat().st_size))
    return outputs

class FbxBatchExporterV7Tool(BaseMayaTool):
    tool_id='fbx_batch_exporter_v7'; tool_name='分组分段FBX导出 V7'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Grouped object/range FBX export with native flags/settings restoration, exclusive outputs, hierarchy bake, joint SSC and explicit portable settings.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','export','bake','disable_ssc','save_settings','load_settings'],'default':'inspect'},'jobs':{'type':'array','minItems':1,'maxItems':1000,'items':{'type':'object','additionalProperties':False,'required':['objects','start','end'],'properties':{'objects':{'type':'array','items':{'type':'string'},'minItems':1},'start':{'type':'number'},'end':{'type':'number'},'filename':{'type':'string'}}}},'output_dir':{'type':'string'},'prefix':{'type':'string','default':''},'options':{'type':'object','additionalProperties':False,'properties':{**{k:{'type':'boolean','default':v} for k,v in DEFAULTS.items() if type(v) is bool},'up_axis':{'type':'string','enum':['Y','Z']},'file_version':{'type':'string','enum':VERSIONS}}},'objects':{'type':'array','items':{'type':'string'},'minItems':1},'start':{'type':'number'},'end':{'type':'number'},'settings_path':{'type':'string'},'configuration':{'type':'object'}}}
    def validate(self,**values):
        try: return ToolResult.ok(message='FBX operation preflight passed',data=plan(normalize(values)))
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])
    def execute(self,**values):
        from maya import cmds
        p=normalize(values); data=plan(p)
        if p['action']=='export': data['outputs']=export(data)
        elif p['action']=='save_settings':
            with Path(data['path']).open('x',encoding='utf8') as stream: json.dump(data['configuration'],stream,ensure_ascii=False,indent=2)
        elif p['action']=='disable_ssc':
            for node in data['targets']: cmds.setAttr(node+'.segmentScaleCompensate',False)
        elif p['action']=='bake':
            selected=cmds.ls(selection=True,long=True) or []; time=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
            try:
                cmds.autoKeyframe(state=False)
                cmds.bakeResults(data['targets'],simulation=True,t=(p['start'],p['end']),sampleBy=1,oversamplingRate=1,disableImplicitControl=True,preserveOutsideKeys=True,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,bakeOnOverrideLayer=False,minimizeRotation=False,controlPoints=False,shape=True)
            finally:
                cmds.currentTime(time); cmds.autoKeyframe(state=auto); valid=[n for n in selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        return ToolResult.ok(message='FBX '+p['action']+' completed',data=data)
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui()
