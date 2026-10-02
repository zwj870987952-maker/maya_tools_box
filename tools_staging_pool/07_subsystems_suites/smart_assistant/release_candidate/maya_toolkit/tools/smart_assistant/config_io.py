"""Five supplied optionVar keys; literal config and deterministic sequence parsing."""
from pathlib import Path
import json,math,re
KEYS={'workingUnitLinear':str,'workingUnitTime':str,'gridSize':float,'gridSpacing':float,'gridDivisions':int}
FILES={'.ma','.mb','.fbx','.obj','.abc'}
IMAGES={'.png','.jpg','.jpeg','.bmp'}
def prefs(values):
    if not isinstance(values,dict) or set(values)-set(KEYS):raise ValueError('Only original five preference keys accepted')
    result={}
    for key,value in values.items():
        typ=KEYS[key]
        if typ is str:
            if not isinstance(value,str) or not value or len(value)>128:raise ValueError('Unit optionVar must be a nonempty string')
        elif typ is int:
            if type(value) not in (int,float) or not math.isfinite(value) or value!=int(value) or not 1<=value<=10000:raise ValueError('Grid divisions must be a positive integral number (Maya may store float)')
        elif type(value) not in (int,float) or not math.isfinite(value) or value<=0 or value>1000000:raise ValueError('Positive finite grid value required')
        result[key]=value
    return result
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or p.is_symlink():raise ValueError('Absolute non-symlink path required')
    return p
def read_prefs(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>1024*1024:raise ValueError('Config absent or exceeds 1 MiB')
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise ValueError('Duplicate config key')
            d[k]=v
        return d
    return prefs(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def output_path(value):
    p=path(value)
    if not p.parent.is_dir() or p.exists() or p.suffix.lower()!='.json':raise ValueError('New JSON file with existing parent required')
    return p
def write_prefs(value,values):
    p=output_path(value);values=prefs(values)
    with p.open('x',encoding='utf8') as f:json.dump(values,f,ensure_ascii=False,allow_nan=False,indent=2)
    return str(p)
def sequence(folder):
    p=path(folder)
    if not p.is_dir():raise ValueError('Sequence folder absent')
    groups={}
    for child in sorted(p.iterdir()):
        if not child.is_file() or child.suffix.lower() not in IMAGES:continue
        match=re.fullmatch(r'(.*?)(\d+)',child.stem)
        if match:groups.setdefault((match[1],len(match[2]),child.suffix.lower()),[]).append((int(match[2]),child))
    groups={k:sorted(v) for k,v in groups.items() if len(v)>=2}
    if len(groups)!=1:raise ValueError('Exactly one numbered image sequence (at least two frames) required')
    key,values=next(iter(groups.items()));frames=[i for i,p in values]
    if len(frames)>10000 or len(set(frames))!=len(frames) or frames!=list(range(frames[0],frames[-1]+1)):raise ValueError('Sequence must have unique contiguous frames, maximum 10000')
    return {'folder':str(p),'first_image':str(values[0][1]),'first_frame':frames[0],'last_frame':frames[-1],'count':len(frames),'prefix':key[0],'padding':key[1]}
