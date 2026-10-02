"""Scene/script batch processor with explicit outputs and isolated default."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tokenize
import traceback
from maya_toolkit.framework import BaseMayaTool,ToolResult


def digest(path):
    sha=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): sha.update(chunk)
    return sha.hexdigest()


def normalize(values):
    p=dict(action='inspect',files=None,scripts=[],base_dir=None,save_backup=False,save_after=False,overwrite=False,
           remove_unknown=False,execution_mode='isolated',error_policy='skip_file',timeout=180,output=None)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','process','save_current'): raise ValueError('Invalid action')
    if p['execution_mode'] not in ('isolated','interactive') or p['error_policy'] not in ('skip_file','stop_batch'): raise ValueError('Invalid execution mode/policy')
    for key in ('save_backup','save_after','overwrite','remove_unknown'):
        if type(p[key]) is not bool: raise ValueError('Options must be bool')
    if type(p['timeout']) is not int or not 10<=p['timeout']<=3600: raise ValueError('Timeout 10..3600 seconds')
    for key in ('base_dir','output'):
        if p[key] is not None and (not isinstance(p[key],str) or not Path(p[key]).is_absolute()): raise ValueError('Absolute output paths required')
    if p['overwrite']: p['save_backup']=True
    if p['action']=='save_current':
        if p['files'] is not None or p['scripts']: raise ValueError('Save current does not process file/script lists')
        if p['output'] is not None and Path(p['output']).suffix.lower() not in ('.ma','.mb'): raise ValueError('Current save supports exact .ma/.mb format')
    else:
        if p['output'] is not None: raise ValueError('Current-save output only')
        if not isinstance(p['files'],list) or not 1<=len(p['files'])<=1000: raise ValueError('1..1000 unique source files required')
        for value in p['files']:
            if not isinstance(value,str) or not Path(value).is_absolute() or Path(value).suffix.lower() not in ('.ma','.mb','.fbx'): raise ValueError('Absolute .ma/.mb/.fbx scene paths required')
        if len({str(Path(v).resolve()).casefold() for v in p['files']})!=len(p['files']): raise ValueError('Duplicate source file')
        if not isinstance(p['scripts'],list) or len(p['scripts'])>1000: raise ValueError('Unique ordered script files required')
        for value in p['scripts']:
            if not isinstance(value,str) or not Path(value).is_absolute() or Path(value).suffix.lower() not in ('.py','.mel'): raise ValueError('Absolute Python/MEL script paths required')
        if len({str(Path(v).resolve()).casefold() for v in p['scripts']})!=len(p['scripts']): raise ValueError('Duplicate script file')
    return p


def exclusive_copy(source,target):
    target=Path(target); target.parent.mkdir(parents=True,exist_ok=True)
    owned=False
    try:
        with target.open('xb') as writer:
            owned=True
            with Path(source).open('rb') as reader: shutil.copyfileobj(reader,writer)
            writer.flush(); os.fsync(writer.fileno())
    except Exception:
        if owned: target.unlink(missing_ok=True)
        raise


def unused(path):
    path=Path(path)
    if path.exists() or path.is_symlink(): raise ValueError('Output/backup already exists: '+str(path))
    parent=path.parent
    while not parent.exists(): parent=parent.parent
    if not parent.is_dir(): raise ValueError('Output parent is not a directory')
    return path


def mayapy_path():
    from maya import cmds
    location=os.environ.get('MAYA_LOCATION')
    path=Path(location)/'bin'/('mayapy.exe' if os.name=='nt' else 'mayapy') if location else Path(sys.executable).with_name('mayapy.exe' if os.name=='nt' else 'mayapy')
    if not path.is_file(): raise ValueError('Matching mayapy unavailable')
    return str(path)


def output_plan(p):
    rows=[]; seen=set()
    if p['base_dir'] is not None and not Path(p['base_dir']).is_dir(): raise ValueError('Output base directory must exist')
    for value in p['files']:
        path=Path(value).resolve()
        if not path.is_file(): raise ValueError('Missing source file: '+str(path))
        if p['overwrite'] and path.suffix.lower()=='.fbx': raise ValueError('FBX overwrite is not Maya scene save; use Save After .ma instead')
        key=hashlib.sha256(str(path).casefold().encode('utf8')).hexdigest()[:8]
        base=Path(p['base_dir']) if p['base_dir'] is not None else path.parent
        stem=path.stem+'__'+key
        row={'source':str(path),'source_sha256':digest(path),'backup':str(base/'BF_Backup'/(stem+path.suffix)) if p['save_backup'] else None,
             'after':str(base/'backup'/(stem+'.ma')) if p['save_after'] else None,'overwrite':p['overwrite']}
        for output in (row['backup'],row['after']):
            if output is not None:
                unused(output); canonical=str(Path(output).resolve()).casefold()
                if canonical in seen: raise ValueError('Output collision')
                seen.add(canonical)
        rows.append(row)
    scripts=[]
    for value in p['scripts']:
        path=Path(value).resolve()
        if not path.is_file(): raise ValueError('Missing script file')
        scripts.append({'path':str(path),'sha256':digest(path)})
    sources={str(Path(row['source']).resolve()).casefold() for row in rows}
    if seen & sources: raise ValueError('Backup/after would replace another input')
    return {'tasks':rows,'scripts':scripts,'count':len(rows),'script_effects_unrestricted':True}


def plan(p):
    from maya import cmds
    if p['action']=='save_current':
        current=cmds.file(query=True,sceneName=True)
        if not current or not Path(current).is_file(): raise ValueError('Current scene must have an existing source path')
        output=Path(p['output']) if p['output'] is not None else Path(current)
        if output.suffix.lower() not in ('.ma','.mb'): raise ValueError('Save requires .ma/.mb; FBX is an export workflow')
        if output.resolve()==Path(current).resolve():
            if not p['overwrite']: raise ValueError('Current file save requires explicit overwrite=True and mandatory backup')
            tasks=output_plan(dict(p,files=[current],scripts=[],save_after=False))
            return {'current_scene':current,'output':str(output),'backup':tasks['tasks'][0]['backup'],'source_sha256':tasks['tasks'][0]['source_sha256']}
        unused(output)
        if not output.parent.is_dir(): raise ValueError('Current save directory must already exist')
        return {'current_scene':current,'output':str(output),'backup':None,'source_sha256':digest(current)}
    data=output_plan(p)
    if p['execution_mode']=='isolated': data['mayapy']=mayapy_path()
    else:
        name=cmds.file(query=True,sceneName=True)
        if cmds.about(batch=True): raise ValueError('Interactive mode requires real GUI Maya')
        if not name or not Path(name).is_file() or cmds.file(query=True,modified=True): raise ValueError('Interactive batch requires a clean saved caller scene; dirty/untitled scene cannot be replaced safely')
        data['caller_scene']=name
    return data


def execute_script(row):
    from maya import mel,cmds
    path=Path(row['path'])
    if digest(path)!=row['sha256']: raise RuntimeError('Selected script changed since preflight')
    if path.suffix.lower()=='.py':
        try:
            with tokenize.open(path) as stream: source=stream.read()
        except UnicodeDecodeError: source=path.read_bytes().decode('gb18030')
        namespace={'__name__':'__main__','__file__':str(path),'cmds':cmds}
        original=list(sys.path); sys.path.insert(0,str(path.parent))
        try: exec(compile(source,str(path),'exec'),namespace)
        finally: sys.path[:]=original
    else:
        try: source=path.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError: source=path.read_bytes().decode('gb18030')
        mel.eval(source)


def save_scene(target,overwrite=False,expected_sha=None):
    from maya import cmds
    target=Path(target); suffix=target.suffix.lower(); file_type='mayaBinary' if suffix=='.mb' else 'mayaAscii'
    target.parent.mkdir(parents=True,exist_ok=True); source_name=cmds.file(query=True,sceneName=True)
    try:
        with tempfile.TemporaryDirectory(prefix='mtb_processed_',dir=str(target.parent)) as directory:
            generated=Path(directory)/('result'+suffix); cmds.file(rename=str(generated)); cmds.file(save=True,type=file_type,force=True)
            if overwrite:
                if not target.is_file() or digest(target)!=expected_sha: raise RuntimeError('Original changed since backup; overwrite refused')
                os.replace(generated,target)  # Same-directory atomic replace after mandatory backup.
            else: exclusive_copy(generated,target)
    finally: cmds.file(rename=source_name)
    return {'path':str(target),'bytes':target.stat().st_size,'type':file_type}


def process_one(p,task,scripts,emit=None):
    from maya import cmds
    result={'source':task['source'],'success':False,'scripts':[],'outputs':[]}
    try:
        if digest(task['source'])!=task['source_sha256']: raise RuntimeError('Source changed since preflight')
        if task['backup']:
            exclusive_copy(task['source'],task['backup']); result['backup']=task['backup']
        if Path(task['source']).suffix.lower()=='.fbx' and not cmds.pluginInfo('fbxmaya',query=True,loaded=True): cmds.loadPlugin('fbxmaya',quiet=True)
        cmds.file(task['source'],open=True,force=True,executeScriptNodes=False,prompt=False)
        original=Path(cmds.file(query=True,sceneName=True)).resolve()
        for row in scripts:
            started=time.monotonic()
            try:
                execute_script(row); result['scripts'].append({'path':row['path'],'success':True,'seconds':round(time.monotonic()-started,3)})
            except Exception as exc:
                result['scripts'].append({'path':row['path'],'success':False,'message':str(exc),'traceback':traceback.format_exc()}); raise
            if emit: emit('Script completed: '+row['path'])
        if Path(cmds.file(query=True,sceneName=True)).resolve()!=original: raise RuntimeError('Script switched or renamed the scene; automatic save refused')
        if p['remove_unknown']:
            unknown=cmds.ls(type='unknown') or []
            if unknown: cmds.delete(unknown)
            result['unknown_removed']=unknown
        if task['after']: result['outputs'].append(save_scene(task['after']))
        if task['overwrite']: result['outputs'].append(save_scene(task['source'],overwrite=True,expected_sha=task['source_sha256']))
        result.update(success=True,message='Scene scripts completed'+(' without saving' if not task['after'] and not task['overwrite'] else ' and requested outputs saved'))
    except Exception as exc: result.update(message=str(exc),traceback=traceback.format_exc())
    return result


class BatchProcessorV3Tool(BaseMayaTool):
    tool_id='batch_processor_v3'; tool_name='文件脚本批量执行 V3'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Ordered Python/MEL scripts over scenes, exact pre-backups/after saves or explicit guarded overwrite; isolated mayapy default and clean-scene interactive compatibility.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','process','save_current'],'default':'inspect'},
        'files':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':1000,'uniqueItems':True},
        'scripts':{'type':'array','items':{'type':'string'},'uniqueItems':True,'default':[]},'base_dir':{'type':'string'},'output':{'type':'string'},
        'save_backup':{'type':'boolean','default':False},'save_after':{'type':'boolean','default':False},'overwrite':{'type':'boolean','default':False},'remove_unknown':{'type':'boolean','default':False},
        'execution_mode':{'type':'string','enum':['isolated','interactive'],'default':'isolated'},'error_policy':{'type':'string','enum':['skip_file','stop_batch'],'default':'skip_file'},
        'timeout':{'type':'integer','minimum':10,'maximum':3600,'default':180}}}

    def __init__(self): self.progress=None; self.cancelled=None

    def validate(self,**values):
        try:
            p=normalize(values); data=plan(p)
            warnings=['Selected scripts are executable user code with unrestricted external effects; child process protects caller scene, not the filesystem']
            if p['overwrite']: warnings.append('Overwrite forces exact pre-backup; external source files are not Maya Undoable')
            if p['execution_mode']=='interactive': warnings.append('Interactive scene switching flushes Undo history; reopening restores scene path and valid selection/time only')
            return ToolResult.ok(message='Batch process preflight passed',data=data,warnings=warnings)
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def run(self,dry_run=False,**values):
        # Scene-open file workflows deliberately do not enter a Maya scene Undo
        # chunk: opening files clears that queue. The protocol remains identical.
        from maya_toolkit.core.maya_utils import ensure_maya_initialized
        ensure_maya_initialized(); started=time.monotonic(); checked=self.validate(**values)
        if dry_run or not checked.success:
            checked.tool_id=self.tool_id; checked.dry_run=bool(dry_run); checked.execution_time=round(time.monotonic()-started,4); return checked
        try: result=self.execute(**values)
        except Exception as exc: result=ToolResult.fail(message=str(exc),errors=[traceback.format_exc()])
        result.warnings.extend(w for w in checked.warnings if w not in result.warnings)
        result.tool_id=self.tool_id; result.dry_run=False; result.execution_time=round(time.monotonic()-started,4); return result

    def execute(self,**values):
        from maya import cmds
        import maya_toolkit
        p=normalize(values); planned=plan(p)
        if p['action']=='inspect': return ToolResult.ok(message='Scene/script output plan inspected',data=planned)
        if p['action']=='save_current':
            if planned['backup']: exclusive_copy(planned['current_scene'],planned['backup'])
            if p['remove_unknown']:
                unknown=cmds.ls(type='unknown') or []
                if unknown:
                    from maya_toolkit.core.context import UndoChunkContext
                    with UndoChunkContext(chunk_name='BatchProcessorV3_remove_unknown'): cmds.delete(unknown)
            output=save_scene(planned['output'],overwrite=p['overwrite'] and Path(planned['output']).resolve()==Path(planned['current_scene']).resolve(),expected_sha=planned['source_sha256'])
            return ToolResult.ok(message='Current scene output saved; file writes not Undoable',data={'output':output,'backup':planned['backup']})
        results=[]; cancelled=False; selected=cmds.ls(selection=True,long=True) or []; current=cmds.currentTime(query=True)
        autokey=cmds.autoKeyframe(query=True,state=True); namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
        try:
            with tempfile.TemporaryDirectory(prefix='mtb_script_batch_') as directory:
                for index,task in enumerate(planned['tasks']):
                    if self.cancelled and self.cancelled(): cancelled=True; break
                    if self.progress: self.progress(index,len(planned['tasks']),task['source'])
                    if p['execution_mode']=='interactive': result=process_one(p,task,planned['scripts'])
                    else:
                        config=Path(directory)/('config'+str(index)+'.json'); output=Path(directory)/('result'+str(index)+'.json')
                        config.write_text(json.dumps({'parameters':p,'task':task,'scripts':planned['scripts'],'result':str(output),'runtime_root':str(Path(maya_toolkit.__file__).resolve().parent.parent)}),encoding='utf8')
                        process=subprocess.Popen([planned['mayapy'],str(Path(__file__).with_name('worker.py')),str(config)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONIOENCODING='utf-8'),creationflags=0x08000000 if os.name=='nt' else 0)
                        deadline=time.monotonic()+p['timeout']; reason=None
                        while True:
                            try: stdout=process.communicate(timeout=.1)[0]; break
                            except subprocess.TimeoutExpired:
                                if self.progress: self.progress(index,len(planned['tasks']),task['source'])
                                if self.cancelled and self.cancelled(): reason='Cancelled'; cancelled=True
                                elif time.monotonic()>deadline: reason='Worker timed out'
                                if reason:
                                    process.kill(); stdout=process.communicate()[0]; break
                        if reason: result={'source':task['source'],'success':False,'message':reason+'; script/output external effects may remain'}
                        elif output.is_file(): result=json.loads(output.read_text(encoding='utf8')); result['success']=bool(result.get('success')) and process.returncode==0
                        else: result={'source':task['source'],'success':False,'message':'Worker returned no result','output':stdout.decode('utf8',errors='replace')[-3000:]}
                        result['returncode']=process.returncode
                    results.append(result)
                    if self.progress: self.progress(index+1,len(planned['tasks']),result['message'])
                    if not result['success'] and p['error_policy']=='stop_batch': break
        finally:
            if p['execution_mode']=='interactive':
                cmds.file(planned['caller_scene'],open=True,force=True,executeScriptNodes=False,prompt=False)
                cmds.autoKeyframe(state=autokey)
                cmds.namespace(set=namespace if cmds.namespace(exists=namespace) else ':')
                valid=[n for n in selected if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True); cmds.currentTime(current)
        failed=[r['source'] for r in results if not r['success']]; data={'scenes':results,'cancelled':cancelled,'processed':len(results),'failed':len(failed),'caller_scene_preserved':p['execution_mode']=='isolated'}
        if failed or cancelled: return ToolResult.fail(message='Batch has failed/cancelled scenes; completed external outputs retained',data=data,errors=failed or ['CANCELLED'])
        return ToolResult.ok(message='Batch scripts and requested saves completed',data=data)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_maya_file_manager
        return show_maya_file_manager()
