"""Offline Maya ASCII filtering with exact original backup and entirely new outputs."""
from pathlib import Path
import hashlib
import json
import os
from maya_toolkit.framework import BaseMayaTool,ToolResult
from .ascii_filter import clean_bytes,KNOWN

def normalize(kwargs):
    allowed={'action','files','directories','output_dir','script_policy','script_names','remove_plugin_requires','confirm_broad_removal'}
    if set(kwargs)-allowed:raise ValueError('Unknown parameters')
    p=dict(action='scan',files=[],directories=[],output_dir=None,script_policy='known',script_names=list(KNOWN),remove_plugin_requires=False,confirm_broad_removal=False);p.update(kwargs)
    if p['action'] not in ('scan','clean') or p['script_policy'] not in ('known','all_scripts','none'):raise ValueError('Invalid action/script_policy')
    for key in ('remove_plugin_requires','confirm_broad_removal'):
        if not isinstance(p[key],bool):raise ValueError('Boolean required')
    for key in ('files','directories','script_names'):
        if not isinstance(p[key],list) or len(p[key])>10000 or any(not isinstance(v,str) or not v for v in p[key]):raise ValueError('String list required: '+key)
    if (p['script_policy']=='all_scripts' or p['remove_plugin_requires']) and not p['confirm_broad_removal']:
        raise ValueError('Broad removal can break legitimate scripts/plugins: confirm_broad_removal=True required')
    return p

def plan(p):
    paths=set(); roots=[]
    for value in p['files']:
        path=Path(value).resolve()
        if not path.is_file() or path.suffix.lower()!='.ma':raise ValueError('Existing .ma file required: '+value)
        paths.add(path)
    for value in p['directories']:
        root=Path(value).resolve()
        if not root.is_dir():raise ValueError('Input directory missing: '+value)
        roots.append(root)
        for directory,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=sorted(n for n in dirs if n.casefold() not in ('history','release_candidate','__pycache__','.git') and not (Path(directory)/n).is_symlink())
            for name in files:
                if Path(name).suffix.lower()=='.ma':paths.add((Path(directory)/name).resolve())
            if len(paths)>10000:raise ValueError('More than 10000 input files')
    if not paths:raise ValueError('No .ma files found')
    out=None
    if p['action']=='clean':
        if not isinstance(p['output_dir'],str) or not p['output_dir']:raise ValueError('clean requires explicit new output_dir')
        out=Path(p['output_dir']).resolve()
        if out.exists() or not out.parent.is_dir():raise ValueError('output_dir must be new, with an existing parent')
        for root in roots:
            if out==root or root in out.parents:raise ValueError('Output must be outside recursively scanned input directories')
    rows=[]
    for path in sorted(paths):
        if path.stat().st_size>128*1024*1024:raise ValueError('Source exceeds bounded 128 MB lexer input: '+str(path))
        data=path.read_bytes(); cleaned,changes=clean_bytes(data,p['script_policy'],p['script_names'],p['remove_plugin_requires'])
        key=hashlib.sha256(str(path).encode()).hexdigest()[:12];filename=path.stem+'_'+key+'.ma'
        rows.append({'source':str(path),'source_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(cleaned).hexdigest(),
            'size':len(data),'output_size':len(cleaned),'changes':changes,
            'output':str(out/filename) if out else None,'backup':str(out/'history'/filename) if out else None})
    return {'rows':rows,'count':len(rows),'output_dir':str(out) if out else None,'options':p,
        'impact':'New filtered .ma and byte-exact original backups + report only. Original files/current scene untouched. External writes cannot Maya Undo. Does not guarantee virus-free.'}

def clean_files(p,progress=None,cancel=None):
    report=plan(p);root=Path(report['output_dir']);root.mkdir();(root/'history').mkdir()
    result=dict(report,completed=[],failures=[],cancelled=False)
    for index,row in enumerate(report['rows']):
        if cancel and cancel():result['cancelled']=True;break
        backup,output=Path(row['backup']),Path(row['output']);owned_output=False;owned_backup=False;backup_complete=False
        try:
            data=Path(row['source']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=row['source_sha256']:raise ValueError('Source changed after preflight')
            filtered,changes=clean_bytes(data,p['script_policy'],p['script_names'],p['remove_plugin_requires'])
            if hashlib.sha256(filtered).hexdigest()!=row['output_sha256']:raise ValueError('Filter changed after preflight')
            with backup.open('xb') as stream:owned_backup=True;stream.write(data)
            backup_complete=hashlib.sha256(backup.read_bytes()).hexdigest()==row['source_sha256']
            if not backup_complete:raise ValueError('Backup SHA mismatch')
            with output.open('xb') as stream:owned_output=True;stream.write(filtered)
            result['completed'].append(row)
        except Exception as error:
            if owned_output:output.unlink(missing_ok=True)
            if owned_backup and not backup_complete:backup.unlink(missing_ok=True)
            result['failures'].append({'source':row['source'],'error':str(error),'backup_retained':backup_complete})
            break
        if progress:progress(index+1,len(report['rows']))
    try:
        with (root/'report.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=True,indent=2)
    except Exception as error:result['failures'].append({'source':'report.json','error':str(error),'backup_retained':False})
    return result

class SceneVirusCleanerTool(BaseMayaTool):
    tool_id='scene_virus_cleaner';tool_name='Maya ASCII 脚本与声明清理';category='scene_hygiene'
    description='离线字节保留.ma策略过滤与新文件/原备份；不是完整杀毒，不执行待检查脚本'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['scan','clean'],'default':'scan'},'files':{'type':'array','items':{'type':'string'},'maxItems':10000},
        'directories':{'type':'array','items':{'type':'string'},'maxItems':10000},'output_dir':{'type':'string'},
        'script_policy':{'type':'string','enum':['known','all_scripts','none'],'default':'known'},
        'script_names':{'type':'array','items':{'type':'string'},'default':list(KNOWN)},
        'remove_plugin_requires':{'type':'boolean','default':False},'confirm_broad_removal':{'type':'boolean','default':False}}}
    def validate(self,**kwargs):
        try:return ToolResult.ok(message='离线文件/清理策略预检通过，未执行MEL/未写文件',data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        p=normalize(kwargs);data=clean_files(p) if p['action']=='clean' else plan(p)
        if data.get('failures'):return ToolResult.fail(message='部分文件处理失败，原文件未改，查看新输出报告',data=data,errors=[r['error'] for r in data['failures']])
        return ToolResult.ok(message='策略过滤完成，不宣称病毒已全部清除',data=data)
    def show_ui(self):
        from .ui import show_ui
        return show_ui()
