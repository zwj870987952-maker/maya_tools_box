"""Bounded data-only serialization. No pickle/eval; exclusive external writes."""
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

MAX_BYTES = 64*1024*1024


def finite(value):
    return type(value) in (int,float) and math.isfinite(value)


def output_path(value):
    if not isinstance(value,str) or not value or not Path(value).is_absolute():
        raise ValueError('An absolute output path is required')
    path=Path(value)
    if path.exists() or path.is_symlink():
        raise FileExistsError('Export refuses an existing path: '+value)
    if not path.parent.is_dir():
        raise ValueError('Output parent directory must exist')
    return path


def read_bytes(value):
    path=Path(value)
    if not path.is_absolute() or not path.is_file() or path.stat().st_size>MAX_BYTES:
        raise ValueError('Input must be an absolute regular file <=64 MiB')
    with path.open('rb') as stream:
        data=stream.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise ValueError('Input exceeds 64 MiB')
    return data


def validate_data(data, kind):
    if not isinstance(data,dict) or set(data)!={'format','kind','data'} or data['format']!='skin_magic/1' or data['kind']!=kind:
        raise ValueError('Expected SkinMagic safe JSON '+kind+'; legacy pickle is unsupported')
    values=data['data']
    if not isinstance(values,dict) or not values or len(values)>1000000:
        raise ValueError('Data must be a nonempty bounded mapping')
    if any(not isinstance(k,str) or not k or len(k)>4096 for k in values):
        raise ValueError('Invalid data name')
    if kind=='lod':
        if any(not isinstance(v,str) or not v or len(v)>4096 for v in values.values()):
            raise ValueError('LoD values must be joint names')
    elif kind=='weights':
        for vertex, pairs in values.items():
            if not re.fullmatch(r'.+\.vtx\[[0-9]+\]',vertex) or not isinstance(pairs,list) or not pairs:
                raise ValueError('Expected vertex and influence-weight pairs')
            seen=set()
            for pair in pairs:
                if not isinstance(pair,list) or len(pair)!=2 or not isinstance(pair[0],str) or not pair[0] or pair[0] in seen or not finite(pair[1]) or not 0<=pair[1]<=1:
                    raise ValueError('Invalid/duplicate influence or nonfinite/out-of-range weight')
                seen.add(pair[0])
            if sum(p[1] for p in pairs)>1.05 or sum(p[1] for p in pairs)<=0:
                raise ValueError('Weight sum must be positive and <=1.05 (original rounds to 2 decimals)')
        source_meshes={v.rsplit('.vtx[',1)[0] for v in values}
        if len(source_meshes)!=1:
            raise ValueError('One source mesh per weight file')
    else:
        raise ValueError('Unknown data kind')
    return values


def read(value, kind):
    try:
        data=json.loads(read_bytes(value).decode('utf8'),parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise ValueError('Only safe JSON is supported; do not open legacy pickle files') from exc
    return validate_data(data,kind)


def write(value, kind, values):
    data={'format':'skin_magic/1','kind':kind,'data':values}
    validate_data(data,kind)
    path=output_path(str(value))
    encoded=(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8')
    if len(encoded)>MAX_BYTES:
        raise ValueError('Output exceeds 64 MiB')
    with path.open('xb') as stream:
        stream.write(encoded)
    return str(path)


def xml_tree(value):
    data=read_bytes(value)
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('XML entity declarations are forbidden')
    return ET.fromstring(data)
