import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/bh_speedlines'
SOURCE = UNIT / 'bh_speedLines(速度线)'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/bh_speedlines'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for file in sorted(p for p in SOURCE.rglob('*') if p.is_file()):
        target = PACKAGE / 'upstream' / file.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': 'upstream/' + file.relative_to(SOURCE).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    entry = SOURCE / 'bh_speedLines.mel'
    original = entry.read_text(encoding='utf-8-sig')
    info = audit(entry)
    calls = [int(row.split(':', 1)[0]) for row in info['top_level_lines'] if row.split(':', 1)[1].strip() == 'bh_speedLines;']
    if len(calls) != 1:
        raise ValueError('Unexpected entry calls')
    adapted = ''.join('\n' if i + 1 in calls else line for i, line in enumerate(original.splitlines(True)))
    if adapted.rstrip().endswith('};'):
        adapted = adapted.rstrip()[:-1] + '\n'
    names = [row['name'] for row in info['procedures']]
    controls = ['bhSpeedLinesOptionsMenu', 'bhsl_vis2s', 'bhsl_layerSwitch', 'bhsl_detailSwitch', 'bhsl_toolMode', 'bhslaboutMenu5', 'aboutlabe500', 'MainTools',
                'bhSL_depthField', 'bhSL_drawDepthSlider', 'bh_SL_cameraField', 'bhScrollList', 'SL_Draw_Plane', 'bh_DrawnGeoL'] + ['but' + str(i) for i in range(2, 10)]
    for name in names + controls:
        adapted = re.sub(r'\b' + re.escape(name) + r'\b', 'mtbSL_' + name, adapted)
    mapping = {'bh_geoFrom2Curves': 'geometry', 'bh_reverseNormals': 'flip', 'bh_simplify': 'simplify', 'bh_keyVisibility': 'key_visibility',
               'bh_smoothCurves': 'smooth', 'bh_toggleDrawMode': 'toggle_draw'}
    for name, action in mapping.items():
        callback = 'python(' + json.dumps("import maya_toolkit.tools.bh_speedlines.ui as _u; _u.dispatch('" + action + "')") + ');'
        adapted = adapted.replace('-command mtbSL_' + name + ' ', '-command ' + json.dumps(callback) + ' ')
    for name, action in (('bhSL_drawDepth', 'draw_depth'), ('bhSL_drawDepthReset', 'reset_depth')):
        callback = 'python(' + json.dumps("import maya_toolkit.tools.bh_speedlines.ui as _u; _u.dispatch('" + action + "')") + ');'
        adapted = adapted.replace(json.dumps('mtbSL_' + name + '();'), json.dumps(callback))
    for widget, option in (('bhsl_detailSwitch', 'detail'), ('bhsl_layerSwitch', 'layer'), ('bhsl_vis2s', 'hold_two')):
        adapted = re.sub(r'`menuItem\s+-query\s+-cb\s+mtbSL_' + widget + r'`', '`mtbSL_read_option "' + option + '"`', adapted)
    # Business geometry uses an explicit camera, independent of the window.
    start = adapted.index('global proc mtbSL_bh_geoFrom2Curves()')
    end = adapted.index('global proc mtbSL_bh_reverseNormals()', start)
    body = adapted[start:end]
    body = body.replace('`textField -q -text mtbSL_bh_SL_cameraField`', '$mtbSL_camera')
    body = body.replace('{\n', '{\nglobal string $mtbSL_camera;\nglobal int $mtbSL_consumeCurves;\n', 1)
    body = body.replace('delete $sel;', 'if ($mtbSL_consumeCurves) delete $sel;')
    adapted = adapted[:start] + body + adapted[end:]
    # Python owns the async job and plane cleanup, never a fixed-name delete.
    adapted = adapted.replace('delete "mtbSL_SL_Draw_Plane";', 'python("import maya_toolkit.tools.bh_speedlines.runtime as _r; _r.remove_plane_only()");')
    adapted = re.sub(r'int \$scriptNum=`scriptJob[^;]+;', '// The adapter registers a parented, owned ToolChanged job after setup.', adapted)
    ui_only = {'bh_speedLinesUI', 'bhUpdateWin', 'bh_scrollWinUpdateSel', 'bh_camList_SL_UI', 'bhSLcutDecimals', 'goToG9Site'}
    masked = masked_source(adapted)
    points = []
    pattern = r'global proc\s+(?:(?:string|float|int)\s*(?:\[\s*\])?\s+)?(mtbSL_\w+)\([^)]*\)'
    for match in re.finditer(pattern, masked):
        if match.group(1)[len('mtbSL_'):] not in ui_only:
            points.append(masked.index('{', match.end()) + 1)
    guard = '\npython("import maya_toolkit.tools.bh_speedlines.runtime as _r; _r.require_active()");\n'
    for point in reversed(points):
        adapted = adapted[:point] + guard + adapted[point:]
    adapted += '\nglobal proc int mtbSL_read_option(string $name) { global int $mtbSL_options[]; if ($name == "detail") return $mtbSL_options[0]; if ($name == "layer") return $mtbSL_options[1]; if ($name == "hold_two") return $mtbSL_options[2]; error "Unknown speedlines option"; return 0; }\n'
    # Native close uses the standard stop action while the controls still exist.
    close = 'python(' + json.dumps('import maya_toolkit.tools.bh_speedlines.ui as _u; _u.on_close()') + ');'
    adapted = adapted.replace('-menuBar 1 mtbSL_bh_speedLinesUI;', '-menuBar 1 -closeCommand ' + json.dumps(close) + ' mtbSL_bh_speedLinesUI;')
    adapted = '\n'.join(line.expandtabs(4).rstrip() for line in adapted.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'bh_speedlines_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/bh_speedLines.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'bh_speedlines', 'raw_files': resources, 'original_procedures': names, 'runtime_procedures': ['mtbSL_' + name for name in names] + ['mtbSL_read_option'],
               'original_audit': info, 'runtime_audit': audit(PACKAGE / 'runtime.mel'),
               'source_license': 'Purchased/provided toolkit; no independent redistribution license found; private preparation',
               'guide_reviewed': 'Complete ReadMe.txt; referenced video not included or fetched',
               'changes': ['No import-time GUI/preferences', 'Private procedure/control/helper/layer names', 'Full original geometry/curve/normal/visibility algorithms', 'Arguments replace geometry/menu option queries', 'Owned draw plane/job lifecycle and close handling', 'Conversion preferences restored and curve consumption explicit'],
               'localized_variant': 'Original Chinese MEL and all sample textures preserved; runtime uses original English suite'}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'bh_speedlines', 'registration': {'module': 'bh_speedlines', 'class_name': 'SpeedLinesTool'},
                   'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)],
                   'resources': [row['path'] for row in resources] + ['runtime.mel', 'catalog.json'], 'dependencies': ['Maya Python3/native MEL runtime commands', 'Actual GUI/model panel for interactive drawing', 'Existing maya_toolkit framework/core Undo'],
                   'source': '../bh_speedLines(速度线)/bh_speedLines.mel', 'change_summary': 'Complete original speedline geometry/curve/visibility/drawing suite and resources; explicit arguments, standard API, preference restoration and owned live-plane/scriptJob cleanup.',
                   'verification_limitations': ['Real GUI drawing, mouse/EP/Pencil contexts and close/scriptJob callbacks pending', 'Original key visibility truncates fractional current time and writes surrounding frames', 'Geometry consumes selected curves by default; simplify modifies topology/pivots', 'Texture samples are resources, not automatically assigned materials', 'Legacy SmoothHairCurves and drawing contexts need actual Maya acceptance'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'procedures': len(names), 'runtime_procedures': len(names) + 1, 'resources': len(resources), 'top_level': catalog['runtime_audit']['top_level_lines']}))


if __name__ == '__main__':
    main()
