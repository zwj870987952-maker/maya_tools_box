import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/eblabs_screenspace'
SOURCE = UNIT / 'ScreenSpace'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/eblabs_screenspace'


def replace_body(text, name, body):
    mask = masked_source(text)
    match = re.search(r'global proc\s+(?:int\s+)?' + re.escape(name) + r'\([^)]*\)', mask)
    if not match:
        raise ValueError(name)
    start = mask.index('{', match.end())
    end, depth = start + 1, 1
    while depth:
        depth += (mask[end] == '{') - (mask[end] == '}')
        end += 1
    return text[:start + 1] + '\n' + body + '\n' + text[end - 1:]


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for file in sorted(p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        target = PACKAGE / 'upstream' / file.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    for path, value in ((UNIT / '.gitattributes', 'ScreenSpace/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(value, encoding='utf-8', newline='\n')
    entry = SOURCE / 'eblabs_hub/ScreenSpace/scripts/eblabs_screenSpace.mel'
    original = entry.read_text(encoding='utf-8-sig')
    names = [row['name'] for row in audit(entry)['procedures']]
    text = original
    # Private names cover declarations, callbacks, controls, and preferences, not upstream modules.
    for name in sorted(set(re.findall(r'\b(?:ebLabs\w*|eb_labs\w*)\b', text)), key=len, reverse=True):
        text = re.sub(r'\b' + re.escape(name) + r'\b', 'mtbSS_' + name, text)
    text = text.replace('namespace -set ":";', '// Preserve current namespace; runtime uses an isolated private namespace.')
    actions = {'ebLabs_animTools_screenSpaceRigMulti': 'create', 'ebLabs_animTools_screenSpaceSmartBakeMulti': 'smart_bake', 'ebLabs_animTools_screenSpaceFullBakeMulti': 'full_bake', 'ebLabs_screenSpace_deleteRig': 'cleanup'}
    for name, action in actions.items():
        text = replace_body(text, 'mtbSS_' + name, 'python(' + json.dumps("import maya_toolkit.tools.eblabs_screenspace.ui as _u; _u.dispatch('" + action + "')") + ');')
    text = replace_body(text, 'mtbSS_ebLabs_screenSpace_enableMayaUI', '// No global Maya windows/panes are hidden or restored.')
    text = replace_body(text, 'mtbSS_ebLabs_screenSpace_updateProgress', '// Progress is deliberately independent of window existence.')
    text = replace_body(text, 'mtbSS_ebLabs_screenSpace_errorDialogue', 'error (stringArrayToString($msgs, "\\n"));')
    text = replace_body(text, 'mtbSS_ebLabs_screenSpace_quickUndo', 'if($action=="undo") python("import maya_toolkit.tools.eblabs_screenspace.ui as _u; _u.quick_undo(\'undo\')"); else if($action=="redo") python("import maya_toolkit.tools.eblabs_screenspace.ui as _u; _u.quick_undo(\'redo\')");')
    text = replace_body(text, 'mtbSS_ebLabs_screenSpace_updateRigList', 'python("import maya_toolkit.tools.eblabs_screenspace.ui as _u; _u.refresh_rigs()");')
    text = text.replace('if(!(`objExists $selectedCam[0]`))', 'if(size($selectedCam)==0 || !(`objExists $selectedCam[0]`))')
    text = text.replace('if($shapeChk[0]!="")', 'if(size($shapeChk)>0 && $shapeChk[0]!="")')
    # Full original rig sampling/normalization/orientation graph; explicit options and private helper names.
    text = text.replace('mtbSS_ebLabs_animTools_screenSpaceRig(string $inputCam, string $inputObj)', 'mtbSS_ebLabs_animTools_screenSpaceRig(string $inputCam, string $inputObj, string $prefix, int $orientationChkBox)')
    text = text.replace('int $orientationChkBox = `checkBox -q -v mtbSS_ebLabs_sc_orientationChkBox`;', '// Explicit orientation argument.')
    text = text.replace('$object + "_', '$prefix + "_')
    # Smart bake uses persistent UUIDs, never reconstructs source identity from helper names.
    text = text.replace('string $object = substituteAllString($control, "_screenSpaceControl", "");', 'string $object = python("__import__(\'maya_toolkit.tools.eblabs_screenspace.runtime\', fromlist=[\'current_target\']).current_target()");')
    text = text.replace('string $rig = ($prefix + "_screenSpaceRig");', 'string $rig = python("__import__(\'maya_toolkit.tools.eblabs_screenspace.runtime\', fromlist=[\'current_rig\']).current_rig()");', 1)
    text = text.replace('delete ($rig);', 'python("import maya_toolkit.tools.eblabs_screenspace.runtime as _r; _r.clean_active()");')
    # Zero-distance target cannot be normalized; report rather than NaN/error in division.
    text = text.replace('//key control and depth locator', 'if($normalizer < 0.000000001) error "Target coincides with camera at sampled key";\n//key control and depth locator')
    # Core construction and smart bake can only be called through standard guarded runtime.
    for name in ('ebLabs_animTools_screenSpaceRig', 'ebLabs_animTools_screenSpaceSmartBake', 'ebLabs_screenSpace_makeCurveCube', 'ebLabs_screenSpace_setRandoColor'):
        mask = masked_source(text)
        match = re.search(r'global proc mtbSS_' + name + r'\([^)]*\)', mask)
        point = mask.index('{', match.end()) + 1
        text = text[:point] + '\npython("import maya_toolkit.tools.eblabs_screenspace.runtime as _r; _r.require_active()");\n' + text[point:]
    text = '\n'.join(line.expandtabs(4).rstrip() for line in text.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'eblabs_screenspace_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/eblabs_screenSpace.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'eblabs_screenspace', 'original_procedures': names, 'runtime_procedures': ['mtbSS_' + n for n in names], 'raw_files': resources, 'runtime_audit': audit(PACKAGE / 'runtime.mel'), 'license': 'Copyright Eric Bates / EB Labs. No independent redistribution grant found; private local preparation only. Bundled license managers/data remain unchanged and unused by direct MEL adapter.', 'changes': ['All original MEL rig sampling/normalization/aim/depth/orientation and sparse bake loops retained', 'No installer shelf/prefs/network/license alteration', 'Private native UI names and standard dispatch', 'Owned persistent UUID source/control/rig and safe cleanup', 'No global Maya window/pane hiding; time/selection/namespace restored', 'Version-specific PackageData launcher not used; direct bundled native MEL']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'eblabs_screenspace', 'registration': {'module': 'eblabs_screenspace', 'class_name': 'ScreenSpaceTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['runtime.mel', 'catalog.json'], 'dependencies': ['Maya native MEL/constraints/key clipboard', 'Existing framework/core Undo', 'Actual Maya UI required for original full window'], 'source': '../ScreenSpace/eblabs_hub/ScreenSpace/scripts/eblabs_screenSpace.mel', 'change_summary': 'Complete bundled ScreenSpace MEL/UI/graph/Smart-Full Bake and all resources, direct self-contained native runtime, explicit inputs and owned UUID-safe cleanup.', 'verification_limitations': ['Native GUI/actual camera projection/rig production animation pending', 'Legacy smart bake overwrites target key timing/tangents and animation clipboard', 'Auxiliary pairBlend/target curves and buffers may remain after cleanup', 'Bundled hybrid EB Hub Python helpers require absent version-specific modules and are archival only; full direct MEL does not depend on them', 'Private licensed resources, no public publication'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'procedures': len(names), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
