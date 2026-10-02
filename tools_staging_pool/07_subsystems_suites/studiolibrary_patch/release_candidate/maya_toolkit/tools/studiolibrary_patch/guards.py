"""Pure preflight plus Maya transform validation; no eager vendor imports."""
from pathlib import Path
import json,math,os,tempfile
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def finite(value):
    if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>1e9:raise ValueError('Finite bounded number required')
    return float(value)
def frames(start,end,step=1):
    start,end,step=map(finite,(start,end,step))
    if step<=0 or end<start or (end-start)/step>9998:raise ValueError('Ordered range, positive step and at most 10000 samples required')
    values=[round(start+i*step,6) for i in range(int((end-start)/step+0.0001)+1)]
    if values[-1]<end-step*0.0001:values.append(end)
    if len(set(values))!=len(values):raise ValueError('Sample step is below supported precision')
    return values
def read(value):
    p=path(str(value))
    if not p.is_file() or p.stat().st_size>64*1024*1024:raise ValueError('JSON missing or exceeds 64 MiB')
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise ValueError('Duplicate JSON key')
            d[k]=v
        return d
    return json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def data(value,animation=False):
    if not isinstance(value,dict) or value.get('schemaVersion')!=1:raise ValueError('World schemaVersion 1 required')
    objects=value.get('objects')
    if not isinstance(objects,dict) or not 1<=len(objects)<=4096:raise ValueError('1-4096 world objects required')
    count=0
    if animation:frames(value.get('startFrame'),value.get('endFrame'),value.get('sampleBy',1))
    for name,item in objects.items():
        if not isinstance(name,str) or not name or not isinstance(item,dict):raise ValueError('Invalid world object')
        samples=item.get('frames') if animation else [item]
        if not isinstance(samples,list) or not samples or len(samples)>10000:raise ValueError('Invalid world samples')
        times=[]
        for sample in samples:
            if not isinstance(sample,dict):raise ValueError('Invalid sample')
            if animation:
                time=finite(sample.get('time'));times.append(time)
                if not value['startFrame']-0.0001<=time<=value['endFrame']+0.0001:raise ValueError('Sample outside source range')
            for field,size in (('position',3),('rotation',3))+( () if animation else (('matrix',16),)):
                vector=sample.get(field)
                if not isinstance(vector,list) or len(vector)!=size:raise ValueError('Invalid '+field)
                for n in vector:finite(n)
            count+=1
            if count>1000000:raise ValueError('Total sample limit exceeded')
        if animation and times!=sorted(set(times)):raise ValueError('Sample times must be sorted and unique')
    return value
def save_json(value,payload):
    p=path(str(value));blob=(json.dumps(payload,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8')
    if not p.parent.is_dir():raise ValueError('Existing parent required')
    # Existing world metadata may only be changed through asset/history save.
    if p.exists():raise FileExistsError('World metadata overwrite refused')
    with p.open('xb') as f:f.write(blob)
def targets(objects,writable=False,attributes=None):
    from maya import cmds
    if not isinstance(objects,(list,tuple)) or not 1<=len(objects)<=4096:raise ValueError('Explicit transform objects required')
    result=[]
    for name in objects:
        if not isinstance(name,str) or not name or any(c in name for c in '*?[]'):raise ValueError('Exact transform name required')
        found=cmds.ls(name,long=True) or []
        if len(found)!=1 or not cmds.objectType(found[0],isAType='transform'):raise ValueError('Missing, ambiguous or non-transform: '+name)
        node=found[0]
        if node in result:raise ValueError('Duplicate transform')
        if writable:
            for attr in attributes or ('translateX','translateY','translateZ','rotateX','rotateY','rotateZ'):
                plug=node+'.'+attr
                if cmds.getAttr(plug,lock=True):raise ValueError('Locked destination: '+plug)
                incoming=cmds.listConnections(plug,s=True,d=False) or []
                if any(not cmds.nodeType(n).startswith('animCurve') for n in incoming):raise ValueError('Driven destination: '+plug)
        result.append(node)
    return result
def matches(rows,attributes=None):
    if not rows:raise ValueError('No matched targets')
    return targets([dst for src,dst in rows],True,attributes)
def asset(value,animation=False,new=False):
    p=path(value);suffix='.wanim' if animation else '.wpose'
    if p.suffix.lower()!=suffix:raise ValueError('Expected '+suffix+' asset directory')
    if new:
        if p.exists() or not p.parent.is_dir():raise ValueError('New asset directory and existing parent required')
    else:
        if not p.is_dir():raise ValueError('Asset directory missing')
        filename='world_transform.json' if animation else 'world_pose.json';data(read(p/filename),animation)
        pose=read(p/'pose.json')
        if not isinstance(pose,dict):raise ValueError('Standard pose metadata absent')
    return p
