"""Byte-preserving MEL command lexer for generated .ma; never executes source."""
import re
PROTECTED={'sceneConfigurationScriptNode','uiConfigurationScriptNode'}
KNOWN=('vaccine_gene','breed_gene')

def commands(data):
    chunks=[]; start=0; i=0; quoted=False; escaped=False; comment=None
    while i<len(data):
        char=data[i]; nxt=data[i:i+2]
        if comment=='line':
            if char in (10,13):comment=None
        elif comment=='block':
            if nxt==b'*/':comment=None;i+=1
        elif quoted:
            if escaped:escaped=False
            elif char==92:escaped=True
            elif char==34:quoted=False
        elif nxt==b'//':comment='line';i+=1
        elif nxt==b'/*':comment='block';i+=1
        elif char==34:quoted=True
        elif char==59:
            chunks.append(data[start:i+1]);start=i+1
        i+=1
    if quoted or comment=='block':raise ValueError('Unterminated quoted string or block comment; refuse to rewrite')
    if data[start:].strip():
        tail=tokens(data[start:])
        if tail:raise ValueError('Non-comment command missing final semicolon')
    if start<len(data):chunks.append(data[start:])
    return chunks

def tokens(data):
    out=[]; i=0
    while i<len(data):
        if data[i] in b' \t\r\n;':i+=1;continue
        if data[i:i+2]==b'//':
            end=data.find(b'\n',i+2);i=len(data) if end<0 else end+1;continue
        if data[i:i+2]==b'/*':
            end=data.find(b'*/',i+2)
            if end<0:raise ValueError('Unterminated comment')
            i=end+2;continue
        if data[i]==34:
            i+=1;value=bytearray()
            while i<len(data):
                if data[i]==34:i+=1;break
                if data[i]==92 and i+1<len(data):
                    # Decode only identifier quote/backslash escapes. Script bodies remain data.
                    if data[i+1] in (34,92):value.append(data[i+1]);i+=2;continue
                value.append(data[i]);i+=1
            out.append(bytes(value).decode('utf-8',errors='surrogateescape'))
        else:
            start=i
            while i<len(data) and data[i] not in b' \t\r\n;':i+=1
            out.append(data[start:i].decode('utf-8',errors='surrogateescape'))
    return out

def clean_bytes(data, script_policy='known', script_names=None, remove_plugin_requires=False):
    if not data.lstrip().startswith(b'//Maya ASCII'):raise ValueError('Expected Maya ASCII header; binary/unknown formats refused')
    if script_policy not in ('known','all_scripts','none'):raise ValueError('Invalid script policy')
    names=set(KNOWN if script_names is None else script_names)
    chunks=commands(data); parsed=[tokens(c) for c in chunks]
    removed=set(); kept_scripts=[]; warnings=[]
    for t in parsed:
        if len(t)>=2 and t[:2]==['createNode','script']:
            if '-n' not in t:raise ValueError('Unnamed script node; ambiguous scope')
            name=t[t.index('-n')+1]
            if name in PROTECTED or script_policy=='none' or (script_policy=='known' and name not in names):kept_scripts.append(name)
            else:removed.add(name)
    def ref(name):return name.split('.',1)[0].lstrip(':') in removed
    result=[]; active=None; discarded=[]; plugin_rows=[]
    for chunk,t in zip(chunks,parsed):
        drop=False
        if not t:result.append(chunk);continue
        command=t[0]
        if command=='createNode':
            active=t[t.index('-n')+1] if '-n' in t else None
            drop=active in removed
        elif command=='select':
            selected=[v for v in t[1:] if not v.startswith('-')]
            active=selected[-1].lstrip(':') if len(selected)==1 else None
            if any(ref(v) for v in selected):
                if len(selected)>1:raise ValueError('Mixed select containing removed and kept nodes; refuse ambiguous edit')
                drop=True
        elif command in ('setAttr','addAttr','rename','lockNode') and active in removed:
            if command=='setAttr':
                attributes=[v for v in t[1:] if v.startswith('.') or ('.' in v and not v.startswith('-') and not any(c.isspace() for c in v))]
                target=attributes[0] if attributes else None
                if target is None:raise ValueError('Cannot determine removed-node setAttr target')
                drop=target.startswith('.') or ref(target)
            else:drop=True
        elif command in ('connectAttr','disconnectAttr'):
            drop=any(ref(v) for v in t[1:] if not v.startswith('-'))
        elif command=='requires' and remove_plugin_requires:
            if len(t)<3:raise ValueError('Malformed requires command')
            plugin=t[-2]
            if plugin!='maya':drop=True;plugin_rows.append({'plugin':plugin,'version':t[-1]})
        elif command=='setAttr':
            attributes=[v for v in t[1:] if v.startswith('.') or ('.' in v and not v.startswith('-') and not any(c.isspace() for c in v))]
            # Only the actual first attribute argument, never a string payload value.
            drop=bool(attributes and ref(attributes[0]))
        elif active in removed:
            # Do not discard arbitrary unrelated commands after a script block.
            active=None
        if drop:discarded.append(command)
        else:result.append(chunk)
    output=b''.join(result)
    commands(output)  # Final string/comment boundaries still valid; no MEL evaluation.
    return output,{'removed_script_nodes':sorted(removed),'retained_script_nodes':kept_scripts,
        'removed_requires':plugin_rows,'removed_command_count':len(discarded),'warnings':warnings,
        'security_claim':'Policy-driven structural filtering only; not signature-complete malware detection. Other expressions/jobs/plugins remain.'}
