from pathlib import Path
import ast,base64,json
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def rows(value):
    if not isinstance(value,list) or len(value)>256:raise ValueError('At most 256 button records')
    result=[]
    for row in value:
        if not isinstance(row,dict) or set(row)-{'command','source_element','text','source_type','icon','icon_png'}:raise ValueError('Unknown button fields')
        item={'command':row.get('command') or '', 'source_element':row.get('source_element') or '', 'text':row.get('text') or '', 'source_type':row.get('source_type') or ('mel' if (row.get('command') or '').rstrip().endswith(';') else 'python')}
        for k in ('command','source_element','text'):
            if not isinstance(item[k],str) or len(item[k])>(65536 if k=='command' else 1024):raise ValueError('Invalid button '+k)
        if item['source_type'] not in ('mel','python'):raise ValueError('Explicit mel/python source_type required')
        if item['source_type']=='python' and item['command']:
            try:ast.parse(item['command'])
            except SyntaxError as e:raise ValueError('Invalid Python syntax: '+str(e)) from e
        if row.get('icon_png'):
            if not isinstance(row['icon_png'],str) or len(row['icon_png'])>512*1024:raise ValueError('Icon limit')
            blob=base64.b64decode(row['icon_png'],validate=True)
            if not blob.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG icon required')
            item['icon_png']=row['icon_png']
        elif row.get('icon'):
            p=path(row['icon']);item['icon']=str(p)
        result.append(item)
    return result
def read(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>16*1024*1024:raise ValueError('Config missing or exceeds 16MiB')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate config key')
            result[k]=v
        return result
    return rows(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def new_path(value):
    p=path(value)
    if p.suffix.lower()!='.json' or p.exists() or not p.parent.is_dir():raise ValueError('New JSON file and existing parent required')
    return p
def write(value,data):
    p=new_path(value);data=rows(data)
    with p.open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,allow_nan=False,indent=2)
    return str(p)
