"""Pure preset IO for structured API, independent of Maya UI and Undo."""
import ast
import hashlib
from pathlib import Path

def preset_plan(action,path,values=None):
    if not isinstance(path,str) or not path:raise ValueError('preset_path required')
    target=Path(path)
    if not target.is_absolute() or target.suffix.lower()!='.txt':raise ValueError('Absolute .txt path required')
    if action=='read_preset':
        if not target.is_file() or target.stat().st_size>1024*1024:raise ValueError('Existing preset <=1 MiB required')
        return {'preset_path':str(target),'source_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    if target.exists() or not target.parent.is_dir():raise ValueError('Fresh file and existing parent required')
    if not isinstance(values,dict) or not values or len(values)>1000:raise ValueError('Nonempty bounded preset_values required')
    for key,value in values.items():
        if not isinstance(key,str) or not key.isidentifier():raise ValueError('Invalid key')
        ast.literal_eval(repr(value))
    text='\n'.join(key+' = '+repr(value) for key,value in values.items())+'\n'
    if len(text.encode('utf-8'))>1024*1024:raise ValueError('Preset too large')
    return {'preset_path':str(target),'text':text}

def execute_preset(action,path,values):
    plan=preset_plan(action,path,values);target=Path(path)
    if action=='save_preset':
        with target.open('x',encoding='utf-8',newline='\n') as output:output.write(plan['text'])
        return {'preset_path':str(target),'saved':True}
    result={}
    for line in target.read_text(encoding='utf-8-sig').splitlines():
        if ' = ' not in line:continue
        key,value=line.strip().split(' = ',1)
        if not key.isidentifier() or key in result:raise ValueError('Invalid/duplicate key')
        result[key]=ast.literal_eval(value)
    return {'preset_path':str(target),'values':result,'source_sha256':plan['source_sha256']}
