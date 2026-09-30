import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/bh_wave_it'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/bh_wave_it'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for file in sorted(UNIT.rglob('*')):
        if not file.is_file() or 'release_candidate' in file.parts or file.name == '.gitattributes':
            continue
        rel = file.relative_to(UNIT)
        target = PACKAGE / 'upstream' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': 'upstream/' + rel.as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    (UNIT / '.gitattributes').write_text('bh_waveIt/** -text\n*.txt -text\n', encoding='utf-8', newline='\n')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    entry = UNIT / 'bh_waveIt/bh_waveIt.mel'
    original = entry.read_text(encoding='utf-8-sig')
    info = audit(entry)
    top = {int(row.split(':', 1)[0]) for row in info['top_level_lines']}
    if len(top) != 2 or any('bh_waveIt;' not in row for row in info['top_level_lines']):
        raise ValueError('Unexpected top-level source')
    text = ''.join('\n' if i + 1 in top else line for i, line in enumerate(original.splitlines(True)))
    names = [row['name'] for row in info['procedures']]
    controls = ['waveItUI', 'mainCol', 'Size', 'Freq', 'RotOffset', 'WaveIt', 'rotXBox', 'rotYBox', 'rotZBox', 'traXBox', 'traYBox', 'traZBox', 'chBox', 'intBox']
    for name in names + controls:
        text = re.sub(r'\b' + name + r'\b', 'mtbWI_' + name, text)
    text = text.replace('-title "mtbWI_bh_waveIt"', '-title "bh_waveIt"').replace('-l "mtbWI_Size"', '-l "Size"')
    # Keep the native layout, route scene callbacks through run/validate/Undo.
    for name, action in [('bh_basicS', 'basic_s'), ('bh_inverseS', 'inverse_s'), ('bh_basicC', 'basic_c'), ('bh_inverseC', 'inverse_c'), ('bh_intCheck', 'interactive'), ('bh_baseOffset', 'base_offset')]:
        callback = 'python(' + json.dumps("import maya_toolkit.tools.bh_wave_it.ui as _u; _u.dispatch('" + action + "')") + ');'
        text = re.sub(r'(-(?:c|cc|dc)\s+)(?:"mtbWI_' + name + r'"|mtbWI_' + name + r')\s*;', lambda m: m.group(1) + json.dumps(callback) + ';', text)
        # Slider callbacks are followed by more flags, not a semicolon.
        text = re.sub(r'(-(?:cc|dc)\s+)"mtbWI_' + name + '"', lambda m: m.group(1) + json.dumps(callback), text)
    # Business queries use typed globals, never a fabricated window.
    signature = 'global proc mtbWI_bh_waveVal()'
    start, end = text.index(signature), text.index('global proc mtbWI_bh_invertFields()')
    body = text[start:end]
    body = body.replace('string $sel[]=`ls -sl`;', 'global string $mtbWI_objects[]; string $sel[]=$mtbWI_objects;')
    text = text[:start] + body + text[end:]
    start, end = text.index('global proc mtbWI_bh_baseOffset()'), text.index('global proc mtbWI_bhResizeWaveUIToggle()')
    body = text[start:end].replace('string $sel[]=`ls -sl`;', 'global string $mtbWI_objects[]; string $sel[]=$mtbWI_objects;')
    text = text[:start] + body + text[end:]
    for widget, key in [('Size', 'amplitude'), ('Freq', 'frequency'), ('WaveIt', 'phase'), ('RotOffset', 'base_offset')]:
        text = re.sub(r'`\s*floatSliderGrp\s+-q\s+-(?:value|v)\s+"mtbWI_' + widget + r'"\s*`', '`mtbWI_read_float "' + key + '"`', text)
        text = re.sub(r'floatSliderGrp\s+-e\s+-v\s+([^;]+?)\s+"mtbWI_' + widget + r'"\s*;', lambda m: 'mtbWI_set_float "' + key + '" ' + m.group(1).strip() + ';', text)
    for widget in controls[6:13]:
        text = re.sub(r'`checkBox\s+-q\s+-v\s+mtbWI_' + widget + '`', '`mtbWI_read_flag "' + widget + '"`', text)
    text = text.replace('`channelBox -q  -sma "mainChannelBox"`', '`mtbWI_read_attrs`')
    # intCheck remains a legacy UI dispatcher, guarded before any scene work.
    protected = set(names) - {'bh_waveIt', 'bhResizeWaveUIToggle'}
    masked = masked_source(text)
    points = [masked.index('{', m.end()) + 1 for m in re.finditer(r'global proc\s+(mtbWI_\w+)\([^)]*\)', masked) if m.group(1)[6:] in protected]
    for point in reversed(points):
        text = text[:point] + '\npython("import maya_toolkit.tools.bh_wave_it.runtime as _r; _r.require_active()");\n' + text[point:]
    keys = ['amplitude', 'frequency', 'phase', 'base_offset']
    floats = ' '.join('if ($name == "' + key + '") return $mtbWI_values[' + str(i) + '];' for i, key in enumerate(keys))
    setters = ' '.join('if ($name == "' + key + '") { $mtbWI_values[' + str(i) + ']=$value; return; }' for i, key in enumerate(keys))
    flags = ' '.join('if ($name == "' + key + '") return $mtbWI_flags[' + str(i) + '];' for i, key in enumerate(controls[6:13]))
    text += '\nglobal proc float mtbWI_read_float(string $name) { global float $mtbWI_values[]; ' + floats + ' error "Unknown float"; return 0; }\n'
    text += 'global proc mtbWI_set_float(string $name, float $value) { python("import maya_toolkit.tools.bh_wave_it.runtime as _r; _r.require_active()"); global float $mtbWI_values[]; ' + setters + ' error "Unknown float"; }\n'
    text += 'global proc int mtbWI_read_flag(string $name) { global int $mtbWI_flags[]; ' + flags + ' error "Unknown flag"; return 0; }\n'
    text += 'global proc string[] mtbWI_read_attrs() { global string $mtbWI_attrs[]; return $mtbWI_attrs; }\n'
    text = '\n'.join(line.expandtabs(4).rstrip() for line in text.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'bh_wave_it_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/bh_waveIt.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'bh_wave_it', 'original_procedures': names, 'runtime_procedures': ['mtbWI_' + name for name in names] + ['mtbWI_read_float', 'mtbWI_set_float', 'mtbWI_read_flag', 'mtbWI_read_attrs'], 'raw_files': resources, 'runtime_audit': audit(PACKAGE / 'runtime.mel'), 'source_license': 'Provided toolkit; independent redistribution authorization absent, private preparation', 'changes': ['Remove both import-time windows', 'Private procedures/widgets', 'Typed explicit ordered objects, axes and custom attributes', 'Native sliders/presets use standard API', 'Original 6.28/rad_to_deg arithmetic and first-object base offset preserved']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'bh_wave_it', 'registration': {'module': 'bh_wave_it', 'class_name': 'WaveItTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['runtime.mel', 'catalog.json'], 'dependencies': ['Maya Python3/native MEL', 'Actual Maya GUI for native controls/channel box', 'Existing maya_toolkit framework/core Undo'], 'source': '../bh_waveIt/bh_waveIt.mel', 'change_summary': 'Full ten-procedure wave/preset/base-offset/interactive native suite, strict ordered explicit API, read-only scalar channel preflight, ToolResult and Undo.', 'verification_limitations': ['Native GUI/interactive sliders/channel box pending', 'Original overwrite values do not explicitly create animation keys', 'Degrees numeric result also applied to translations/custom attrs in current Maya units', 'Selection order determines wave and first-object offset'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'original_procedures': len(names), 'runtime_procedures': len(catalog['runtime_procedures']), 'resources': len(resources), 'top_level': catalog['runtime_audit']['top_level_lines']}))


if __name__ == '__main__':
    main()
