"""Bounded typed history/config, own paths and byte-exact backups before replace."""
from pathlib import Path
import configparser,io,json,math,os,re,tempfile,uuid
NUMBERS={'timer_a_starttime','timer_b_starttime','timer_c_starttime','timer_flash_a_starttime','timer_flash_starttime','timer_flash_b_starttime','timer_flash_freq'}
COLORS={f'timer_{group}_{color}color' for group in ('a','b','c','flash_a','flash_b','pause','default') for color in ('bg','text')}
FLAGS={'timer_automute','timer_autopause'}
def root(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Explicit state directory required')
    p=Path(value)
    if not p.is_absolute() or not p.is_dir() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Existing absolute non-symlink directory required')
    if Path(__file__).parent.resolve() in (p.resolve(),*p.resolve().parents):raise ValueError('Candidate bundle is immutable')
    return p
def history(data):
    if not isinstance(data,dict) or set(data)-{'maya','nuke','desktop'}:raise ValueError('Invalid history hosts')
    for host,files in data.items():
        if not isinstance(files,dict) or len(files)>10000:raise ValueError('History file bound')
        for name,row in files.items():
            if not isinstance(name,str) or not name or len(name)>4096 or not isinstance(row,dict) or set(row)-{'totalTime','lastSave','dirPath','history'}:raise ValueError('Invalid history row')
            for key in ('totalTime',):
                if type(row.get(key)) is not int or not 0<=row[key]<=1000000000:raise ValueError('Nonnegative integer minutes required')
            if not isinstance(row.get('history'),dict) or len(row['history'])>10000:raise ValueError('Invalid version history')
            for key in ('lastSave','dirPath'):
                if row.get(key) is not None and (not isinstance(row[key],str) or len(row[key])>4096):raise ValueError('Invalid history text')
            for version,item in row['history'].items():
                if not isinstance(version,str) or not version.isdigit() or len(version)>12 or not isinstance(item,dict) or set(item)-{'time','date','fileName'}:raise ValueError('Invalid version record')
                if type(item.get('time')) is not int or not 0<=item['time']<=1000000000:raise ValueError('Invalid version minutes')
                for key in ('date','fileName'):
                    if not isinstance(item.get(key),str) or len(item[key])>4096:raise ValueError('Invalid version strings')
    return data
def read_history(path):
    p=Path(path)
    if not p.exists():return {}
    if not p.is_file() or p.is_symlink() or p.stat().st_size>32*1024*1024:raise ValueError('Invalid or oversized history')
    def pairs(rows):
        out={}
        for k,v in rows:
            if k in out:raise ValueError('Duplicate history key')
            out[k]=v
        return out
    return history(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def config_value(section,key,value):
    if section=='general' and key in FLAGS:
        if type(value) is bool:return str(value)
        if value in ('True','False','true','false'):return str(value).title()
        raise ValueError('Strict boolean required')
    if section=='timerOptions' and key in NUMBERS:
        if isinstance(value,str) and value.isdigit():value=int(value)
        if type(value) is not int or not (50 if key=='timer_flash_freq' else 0)<=value<=1000000:raise ValueError('Bounded timer integer required')
        return str(value)
    if section=='timerOptions' and key in COLORS:
        if hasattr(value,'getRgb'):value='rgba'+str(value.getRgb())
        if not isinstance(value,str) or not re.fullmatch(r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',value) or any(int(n)>255 for n in re.findall(r'\d+',value)):raise ValueError('RGBA channels 0-255 required')
        return value
    raise ValueError('Unknown configuration option')
def ini(text):
    if not isinstance(text,str) or len(text)>1024*1024:raise ValueError('Config exceeds 1MiB')
    parser=configparser.ConfigParser(interpolation=None,strict=True);parser.read_string(text)
    if parser.defaults():raise ValueError('INI defaults not allowed')
    for section in parser.sections():
        if section not in ('timerOptions','general'):raise ValueError('Unknown INI section')
        for key,value in parser.items(section):config_value(section,key,value)
    return parser
def read_config(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>1024*1024:raise ValueError('Invalid or oversized INI')
    return ini(p.read_text(encoding='utf8'))
def atomic(path,blob):
    from . import session
    p=Path(path)
    if session.data_root is None or p.parent.resolve()!=session.data_root.resolve() or p.name not in ('ksSaveTimer_config.ini','KSSaveTimer_timeTrackHistory.json') or p.is_symlink():raise ValueError('Only own configured state files writable')
    if p.suffix=='.json':history(json.loads(blob.decode('utf8')))
    else:ini(blob.decode('utf8'))
    backup=None
    if p.exists():
        if not p.is_file():raise ValueError('Existing non-file refused')
        old=p.read_bytes();backup=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
        with backup.open('xb') as f:f.write(old)
        if backup.read_bytes()!=old:raise IOError('Backup mismatch')
        fd,tmp=tempfile.mkstemp(prefix='.mtb_save_timer_',dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(blob)
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    else:
        with p.open('xb') as f:f.write(blob)
    return {'path':str(p),'backup':str(backup) if backup else None}
def write_history(path,data):return atomic(path,(json.dumps(history(data),ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8'))
def write_config(path,parser):
    stream=io.StringIO();parser.write(stream);return atomic(path,stream.getvalue().encode('utf8'))
