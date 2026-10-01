"""Read full MEL procedure blocks without executing the original auto-open entry."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools_staging_pool/01_animation/physics_tools/PhysicsTools_v1.8.mel'


def tokenize(source):
    return list(re.finditer(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z_0-9]*|\s+|.', source))


def procedures(source):
    tokens = tokenize(source)
    blocks = []
    for i, t in enumerate(tokens):
        if t.group() != 'proc':
            continue
        j = i + 1
        while tokens[j].group().isspace():
            j += 1
        name = tokens[j].group()
        while tokens[j].group() != '{':
            j += 1
        begin, level = j, 0
        while j < len(tokens):
            if tokens[j].group() == '{':
                level += 1
            elif tokens[j].group() == '}':
                level -= 1
                if not level:
                    blocks.append({'name': name, 'line': source.count('\n', 0, t.start()) + 1, 'body_start': tokens[begin].end(), 'body_end': tokens[j].start(), 'body': source[tokens[begin].end():tokens[j].start()]})
                    break
            j += 1
    return blocks


def main():
    source = SOURCE.read_text(encoding='utf-8-sig')
    blocks = procedures(source)
    summary = []
    for row in blocks:
        body = row['body']
        code = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/', '', body)
        entry = {k: v for k, v in row.items() if k != 'body'}
        entry.update(lines=body.count('\n'), embedded_python='python(' in body, deletes=len(re.findall(r'\bdelete\b', code)), cache='diskCache' in code, uses_ui=bool(re.search(r'floatSliderGrp|ConnectionEditor|nodeOutliner|timeControl|channelBox|treeView|graphEditor', code)), external_calls=sorted(set(re.findall(r'\b(?:Rivet|GhostSelected|UnghostSelected|UnghostAll|doJiggle|createHair|doCreateGeometryCache|setupNParticleConnections)\b', code))))
        summary.append(entry)
    result = {'raw_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'source_bytes': SOURCE.stat().st_size, 'total_lines': source.count('\n') + 1, 'procedures': summary, 'top_level_auto_open': 'PhysicsToolsWin();' in source, 'independent_license': None}
    (ROOT / 'plans/staging_run/physics_tools_source_inventory.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'procedures': len(blocks), 'bytes': result['source_bytes'], 'lines': result['total_lines'], 'cache_procs': [r['name'] for r in summary if r['cache']], 'embedded_python': [r['name'] for r in summary if r['embedded_python']]}))


if __name__ == '__main__':
    main()
