"""Read only MEL shelf inventory; never execute embedded button commands."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
unit=ROOT/'tools_staging_pool/07_subsystems_suites/malcolm341_mega_pack'
src=next(unit.glob('*/*.mel'))
raw=src.read_bytes(); text=raw.decode('utf8')
def tokens(s):
    out=[]; i=0
    while i<len(s):
        if s[i].isspace(): i+=1;continue
        if s.startswith('//',i):
            end=s.find('\n',i);i=len(s) if end<0 else end+1;continue
        if s.startswith('/*',i):
            end=s.find('*/',i+2)
            if end<0:raise ValueError('Unclosed comment')
            i=end+2;continue
        start=i
        if s[i]=='"':
            i+=1; chars=[]
            while i<len(s) and s[i]!='"':
                if s[i]=='\\':
                    i+=1
                    if i>=len(s):raise ValueError('Invalid escape')
                    chars.append({'n':'\n','r':'\r','t':'\t','"':'"','\\':'\\'}.get(s[i],'\\'+s[i])); i+=1
                else:chars.append(s[i]);i+=1
            if i>=len(s):raise ValueError('Unclosed string')
            i+=1;out.append(('str',''.join(chars),start,i))
        elif s[i] in ';{}()':out.append(('punct',s[i],i,i+1));i+=1
        else:
            while i<len(s) and not s[i].isspace() and s[i] not in '";{}()':i+=1
            if i==start:raise ValueError('Stalled lexer')
            out.append(('word',s[start:i],start,i))
    return out
def attributes(ts):
    out={}
    for i,t in enumerate(ts[:-1]):
        if t[0]=='word' and t[1].startswith('-'):
            out[t[1]]=ts[i+1][1]
    return out
ts=tokens(text); rows=[];menus=[]
for i,t in enumerate(ts):
    if t[:2] not in [('word','shelfButton'),('word','menuItem')]:continue
    j=i+1
    while j<len(ts) and ts[j][1]!=';':j+=1
    if j==len(ts):raise ValueError('Missing semicolon')
    a=attributes(ts[i:j]); command=a.pop('-command',a.pop('-c','')); typ=a.get('-sourceType',a.get('-stp','mel'))
    callbacks=[]
    for k in range(i+1,j):
        flag=ts[k][1]
        if flag in ('-command','-c','-doubleClickCommand','-dcc'):
            value=ts[k+1]; callbacks.append({'event':'primary' if flag in ('-command','-c') else 'double', 'command':value[1],'offset':[value[2],value[3]]})
        elif flag in ('-mi','-menuItem'):
            label,value=ts[k+1],ts[k+2]
            if value[1]=='(':
                value=ts[k+3]
                if value[0]!='str' or ts[k+4][1]!=')':raise ValueError('Unsupported menu expression')
            callbacks.append({'event':f'menu_{sum(c["event"].startswith("menu_") for c in callbacks)+1:03d}',
                              'label':label[1],'command':value[1],'offset':[value[2],value[3]]})
    row={'id':f'button_{len(rows)+1:03d}' if t[1]=='shelfButton' else f'menu_{len(menus)+1:03d}',
         'flags':a,'source_type':typ,'command':command,'command_sha256':hashlib.sha256(command.encode()).hexdigest(),
         'offset':[t[2],ts[j][3]],'command_chars':len(command),'callbacks':callbacks}
    (rows if t[1]=='shelfButton' else menus).append(row)
result={'source':src.relative_to(unit).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
        'top_prefix':text[:600],'top_suffix':text[-900:],'buttons':rows,'menus':menus,
        'top_level_procedures':[ts[i+2][1] for i in range(len(ts)-2) if ts[i][:2]==('word','global') and ts[i+1][:2]==('word','proc')]}
(ROOT/'plans/staging_run/malcolm341_source_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'bytes':len(raw),'buttons':len(rows),'callbacks':sum(len(r['callbacks']) for r in rows),
                  'procedures':result['top_level_procedures'],'inventory':[{ 'id':r['id'],'label':r['flags'].get('-label'),
                  'callbacks':len(r['callbacks']),'chars':r['command_chars'],
                  'effects':[x for x in ('fopen','file -','sysFile','optionVar','savePrefs','userSetup','quit','Quit','system','scriptJob','evalDeferred','undoInfo','loadPlugin') if x in ''.join(c['command'] for c in r['callbacks'])]} for r in rows]},ensure_ascii=False))
