"""Read every BB suite source/header/entry/effect without sourcing it."""
import json
from pathlib import Path
import re
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'tools_staging_pool/02_rigging_hierarchy/bb_tools/bb_Tools'


def main():
    reports = []
    for source in sorted(RAW.rglob('*.mel')):
        try:
            report = audit(source)
            report['file'] = source.relative_to(RAW).as_posix()
        except ValueError as exc:
            report = {'file': source.relative_to(RAW).as_posix(), 'audit_error': str(exc)}
        raw = source.read_bytes()
        decoding = None
        for encoding in ('utf-8-sig', 'gb18030', 'cp1252'):
            try:
                text = raw.decode(encoding)
                decoding = encoding
                break
            except UnicodeDecodeError:
                pass
        if decoding is None:
            text = raw.decode('latin-1')
            decoding = 'latin-1 unverified'
        report['candidate_decoding'] = decoding
        report['header'] = text.splitlines()[:8]
        report['io_lines'] = [str(i + 1) + ':' + line.strip() for i, line in enumerate(text.splitlines()) if re.search(r'\b(?:source|file|fopen|fwrite|sysFile|system|getenv|putenv|optionVar|savePrefs|scriptJob|scriptNode|loadPlugin|python)\b', line) and not line.lstrip().startswith('//')]
        reports.append(report)
        print(json.dumps({'file': report['file'], 'encoding': decoding, 'procedures': len(report.get('procedures', [])), 'top': report.get('top_level_lines', []), 'error': report.get('audit_error')}, ensure_ascii=True))
    path = ROOT / 'plans/staging_run/bb_tools_source_inventory.json'
    path.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
