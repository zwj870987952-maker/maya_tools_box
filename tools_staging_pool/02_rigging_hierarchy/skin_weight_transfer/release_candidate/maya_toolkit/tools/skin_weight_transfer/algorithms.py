"""Pure task grammar and the original merge-plus-normalize operation."""
import math


def task_line(line):
    if not isinstance(line,str) or not line.strip():
        raise ValueError('Task line must be nonempty text')
    parts=[p.strip() for p in line.split('=>')]
    if not 2<=len(parts)<=4 or not parts[0] or not parts[1]:
        raise ValueError('Expected source => target => mesh1,mesh2 => DelSkin')
    if len(parts)==4 and parts[3] and parts[3].lower()!='delskin':
        raise ValueError('Fourth field must be DelSkin or empty')
    meshes=[n.strip() for n in parts[2].split(',')] if len(parts)>=3 and parts[2] else None
    if meshes is not None and (any(not n for n in meshes) or len(meshes)!=len(set(meshes))):
        raise ValueError('Mesh list must have distinct nonempty names')
    return {'source_joint':parts[0],'target_joint':parts[1],'meshes':meshes,'remove_source':len(parts)==4 and parts[3].lower()=='delskin'}


def normalize(kwargs):
    allowed={'action','tasks','task_text'}
    if set(kwargs)-allowed:
        raise ValueError('Unknown arguments')
    action=kwargs.get('action','transfer')
    if action not in ('inspect','transfer'):
        raise ValueError('Unknown action')
    if ('tasks' in kwargs)==('task_text' in kwargs):
        raise ValueError('Provide exactly one of tasks or task_text')
    if 'task_text' in kwargs:
        if not isinstance(kwargs['task_text'],str):
            raise ValueError('task_text must be multiline text')
        tasks=[task_line(line) for line in kwargs['task_text'].splitlines() if line.strip()]
    else:
        tasks=kwargs['tasks']
    if not isinstance(tasks,list) or not 1<=len(tasks)<=1000:
        raise ValueError('Expected 1..1000 ordered tasks')
    out=[]
    for row in tasks:
        if not isinstance(row,dict) or set(row)-{'source_joint','target_joint','meshes','remove_source'}:
            raise ValueError('Invalid task fields')
        for key in ('source_joint','target_joint'):
            if not isinstance(row.get(key),str) or not row[key]:
                raise ValueError('Source/target joint name is required')
        meshes=row.get('meshes')
        if meshes is not None and (not isinstance(meshes,list) or not meshes or any(not isinstance(n,str) or not n for n in meshes) or len(meshes)!=len(set(meshes))):
            raise ValueError('Meshes must be omitted or a nonempty distinct list')
        remove=row.get('remove_source',False)
        if type(remove) is not bool:
            raise ValueError('remove_source must be boolean')
        out.append(dict(source_joint=row['source_joint'],target_joint=row['target_joint'],meshes=meshes,remove_source=remove))
    return {'action':action,'tasks':out}


def merged_rows(weights,count,source,target):
    if type(count) is not int or count<=1 or not 0<=source<count or not 0<=target<count or source==target or len(weights)%count:
        raise ValueError('Invalid influence dimensions/indices')
    rows=[]
    for offset in range(0,len(weights),count):
        values=list(weights[offset:offset+count])
        if any(not math.isfinite(v) or v<0 for v in values):
            raise ValueError('Nonfinite/negative skin weights are unsupported')
        values[target]+=values[source]
        values[source]=0.0
        total=sum(values)
        if total>0:
            values=[v/total for v in values]
        rows.append(values)
    return rows
