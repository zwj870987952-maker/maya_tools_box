"""Read original MEL declarations and top-level code without sourcing the script."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re


def masked_source(source):
    """Mask comments and quoted text, preserving character offsets and line numbers."""
    result = list(source)
    index = 0
    state = 'code'
    while index < len(source):
        ch = source[index]
        if state == 'code':
            if source.startswith('//', index):
                result[index:index+2] = [' ', ' ']
                index += 2
                state = 'line'
                continue
            if source.startswith('/*', index):
                result[index:index+2] = [' ', ' ']
                index += 2
                state = 'block'
                continue
            if ch == '"':
                result[index] = ' '
                state = 'string'
        elif state == 'line':
            if ch == '\n':
                state = 'code'
            else:
                result[index] = ' '
        elif state == 'block':
            if source.startswith('*/', index):
                result[index:index+2] = [' ', ' ']
                index += 2
                state = 'code'
                continue
            if ch != '\n':
                result[index] = ' '
        elif state == 'string':
            if ch == '\\' and index+1 < len(source):
                result[index] = result[index+1] = ' '
                index += 2
                continue
            if ch == '"':
                state = 'code'
            if ch != '\n':
                result[index] = ' '
        index += 1
    if state in ('block', 'string'):
        raise ValueError('Unclosed MEL comment/string')
    return ''.join(result)


def audit(path):
    raw = path.read_bytes()
    try:
        source = raw.decode('utf-8-sig')
        decoding = 'utf-8-sig'
    except UnicodeDecodeError:
        # Preserve byte offsets for ASCII MEL syntax, without guessing localized text.
        source = raw.decode('latin-1')
        decoding = 'latin-1 for lexical analysis only; actual legacy text encoding unverified'
    masked = masked_source(source)
    signature = re.compile(r'\b(?:(global)\s+)?proc\s+(?:(string|int|float|vector|matrix)\s*(\[\s*\])?\s+)?([A-Za-z_]\w*)\s*\(([^)]*)\)')
    procedures = []
    remainder = list(masked)
    for match in signature.finditer(masked):
        opening = masked.find('{', match.end())
        if opening < 0:
            raise ValueError('Missing body: ' + match.group(4))
        depth, end = 1, opening+1
        while end < len(masked) and depth:
            depth += (masked[end] == '{') - (masked[end] == '}')
            end += 1
        if depth:
            raise ValueError('Unclosed body: ' + match.group(4))
        params = []
        for item in match.group(5).split(','):
            if not item.strip():
                continue
            param = re.fullmatch(r'\s*(string|int|float|vector|matrix)\s+\$([A-Za-z_]\w*)\s*(\[\s*\])?\s*', item)
            if not param:
                raise ValueError('Unsupported declaration: ' + item)
            params.append(dict(name=param.group(2), type=param.group(1) + ('[]' if param.group(3) else '')))
        procedures.append(dict(name=match.group(4), global_scope=bool(match.group(1)),
                               return_type=(match.group(2) or 'void') + ('[]' if match.group(3) else ''),
                               parameters=params, line=source.count('\n', 0, match.start())+1,
                               end_line=source.count('\n', 0, end)+1))
        for index in range(match.start(), end):
            if remainder[index] != '\n':
                remainder[index] = ' '
    original_lines = source.splitlines()
    remaining_lines = ['{}:{}'.format(i+1, original_lines[i]) for i, line in enumerate(''.join(remainder).splitlines()) if line.strip()]
    counts = collections.Counter(p['name'] for p in procedures)
    return dict(file=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), lexical_decoding=decoding,
                procedures=procedures, duplicate_names={n: c for n, c in counts.items() if c > 1},
                top_level_lines=remaining_lines, source_executed=False,
                limitation='Lexical declarations/effect review only; actual Maya source is the syntax authority')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    reports = [audit(Path(p)) for p in args.files]
    Path(args.output).write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for report in reports:
        print(json.dumps({k: report[k] for k in ('file', 'bytes', 'duplicate_names', 'top_level_lines')}, ensure_ascii=True))
        print(json.dumps({'procedures': len(report['procedures']), 'global': sum(p['global_scope'] for p in report['procedures'])}))


if __name__ == '__main__':
    main()
