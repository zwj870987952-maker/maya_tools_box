"""Keep every original byte; prepare the complete native suite with explicit entry points."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/bb_tools'
RAW = UNIT / 'bb_Tools'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/bb_tools'
PREFIX = 'bbstg_'
ENTRIES = {
    'bb_Tools.mel': 'bb_Tools',
    'Script/wp_rename.mel': 'wp_RenameWindow',
    'Script/bb_listTool.mel': 'bb_listTool',
    'Script/bb_ctrlTool.mel': 'bb_ctrlTool',
    'Script/bb_attributeTool.mel': 'bb_attributeTool',
    'Script/bb_curveTool.mel': 'bb_curveTool',
    'Script/bb_blendShapeTool.mel': 'bb_blendShapeTool',
    'Script/bb_QCTool.mel': 'bb_QCTool',
    'Script/bb_advFixTool/bb_advFixTool.mel': 'bb_advFixTool',
    'Script/bb_FBXExportTool.mel': 'bb_FBXExportTool',
    'Script/cgTkShapeBuilder.mel': 'cgTkShapeBuilder',
    'Script/Mirror&Flip.mel': 'abSymMesh',
    'Script/bb_skin2Deform.mel': 'bb_skin2Deform',
    'Script/bb_createFolliceTool.mel': 'bb_createFolliceTool',
    'Script/cdkMakeDynamicChain.mel': 'cdkMakeDynamicChainUI',
    'Script/bb_softModTool.mel': 'bb_softModTool',
    'Script/bb_selectTool.mel': 'bb_selectTool',
    'Script/bb_history.mel': 'bb_history',
    'Script/bb_skinList.mel': 'bb_skinList',
    'Script/FileTextureManager.mel': 'FileTextureManager',
    'Script/LxxBSRePlace.mel': 'LxxBSReplace',
    'Script/bb_FixError.mel': 'bb_FixError',
    'Script/bb_autoSkirt.mel': 'bb_autoSkirt',
    'Script/bb_masterCreate.mel': 'bb_masterCreate',
    'Script/aboutJBPerVert.mel': 'JBPerVertWindow',
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [re.sub(r'^[ \t]+', lambda m: m[0].expandtabs(4), x.rstrip()) for x in text.rstrip().splitlines()]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')


def replace_body(text, report, name, body):
    masked = masked_source(text)
    start = re.search(r'\b(?:global\s+)?proc\s+(?:(?:string|int|float|vector|matrix)\s*(?:\[\s*\])?\s+)?'+re.escape(name)+r'\s*\([^)]*\)', masked)
    opening = masked.index('{', start.end())
    depth, end = 1, opening+1
    while depth:
        depth += (masked[end] == '{')-(masked[end] == '}')
        end += 1
    return text[:opening]+'{\n'+body+'\n}'+text[end:]


def main():
    inventory = json.loads((ROOT / 'plans/staging_run/bb_tools_source_inventory.json').read_text(encoding='utf-8'))
    active = [f for f in inventory if f['file'] == 'bb_Tools.mel' or f['file'].startswith('Script/') and f['file'] not in ('Script/DelDJJ.mel', 'Script/OutlineError.mel')]
    names = {p['name'] for f in active for p in f['procedures']}
    substitutions = re.compile(r'\b(' + '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r')\b')
    files = []
    for source in sorted(RAW.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(RAW)
        target = PKG / 'vendor' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        files.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size})
        if source.suffix.lower() != '.mel':
            target = PKG / 'native' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    procedures, native_files = {}, []
    effects = ('delete', 'deleteAttr', 'cutKey', 'bakeResults', 'connectAttr', 'parent', 'scriptJob', 'scriptNode', 'optionVar', 'file', 'fopen', 'deformerWeights', 'system', 'python', 'window', 'textField', 'checkBox', 'radioCollection', 'textScrollList')
    for report in active:
        relative = report['file']
        text = (RAW / relative).read_bytes().decode(report['candidate_decoding'])
        original_lines = text.splitlines()
        for p in report['procedures']:
            if p['name'] in procedures:
                raise ValueError('Ambiguous active declaration ' + p['name'])
            body = '\n'.join(original_lines[p['line'] - 1:p['end_line']])
            procedures[p['name']] = dict(p, file=relative, native_name=PREFIX+p['name'], direct_effects=[x for x in effects if re.search(r'\b' + x + r'\b', body)])
        entry = ENTRIES.get(relative)
        if relative == 'Script/aboutJBPerVert.mel':
            # This original has an entire top-level UI rather than one auto-run call.
            lines = text.splitlines(keepends=True)
            text = ''.join(lines[:14]) + 'global proc JBPerVertWindow(){\n' + ''.join(lines[14:75]) + '}\n' + ''.join(lines[75:])
            names.add('JBPerVertWindow')
            text = text.replace('global proc JBPerVertWindow()', 'global proc bbstg_JBPerVertWindow()')
        elif entry:
            text, count = re.subn(r'(?m)^\s*' + re.escape(entry) + r'\s*;\s*$', '// Candidate: explicit native UI entry only.', text)
            if count > 1:
                raise ValueError('Unexpected repeated entry ' + relative)
        if relative == 'bb_Tools.mel':
            text = replace_body(text, report, 'bb_Tools_FilePath', '    global string $bbstg_bundleRoot; return $bbstg_bundleRoot;')
            def button_command(match):
                try:
                    value = json.loads(match[0])
                except ValueError:
                    return match[0]
                for member, target in ENTRIES.items():
                    if value.startswith(member+'";'):
                        return json.dumps(target+';', ensure_ascii=False)
                return match[0]
            text = re.sub(r'"(?:\\.|[^"\\])*"', button_command, text)
            text = text.replace('("source \\"" + $bb_Tools_Path + $buttonArray[$i+1])', '$buttonArray[$i+1]')
        elif relative == 'Script/bb_QCTool.mel':
            text = replace_body(text, report, 'bb_QC_setFilePath', '    global string $bbstg_bundleRoot; return ($bbstg_bundleRoot + "Script");')
            text = re.sub(r'(?m)^.*eval \("source .*$', '    // Definitions already loaded through the UTF-8 Python loader.', text)
        elif relative == 'Script/bb_advFixTool/bb_advFixTool.mel':
            text = replace_body(text, report, 'bb_advFix_setFilePath', '    global string $bbstg_bundleRoot; return ($bbstg_bundleRoot + "Script/bb_advFixTool");')
            text = re.sub(r'(?m)^.*eval \("source .*$', '    // Definitions already loaded through the UTF-8 Python loader.', text)
        elif relative == 'Script/bb_skin2Deform.mel':
            block = '\n'.join(original_lines[162:168])
            text = text.replace(block, '    string $filePath = staging_bb_scratch();')
            text = text.replace('`fopen $fileNew "w"`', '`staging_bb_open $fileNew "w"`')
            text = text.replace('sysFile -delete (', 'staging_bb_delete (')
        elif relative == 'Script/bb_QC_set.mel':
            text = text.replace('`bb_QC_setFilePath` + "/QC_sets"', '`staging_bb_qc_dir`')
            text = text.replace('`fopen $fileName "w"`', '`staging_bb_open $fileName "w"`')
            text = text.replace('sysFile -copy ($path + "/" + $fileName + ".bb") $loadFile[0];', 'staging_bb_copy($loadFile[0], ($path + "/" + $fileName + ".bb"));')
            text = text.replace('eval ($nextWord);', 'staging_bb_qc_line($nextWord);')
            for variable in ('modleSuffix', 'cam', 'smooth', 'ctrlSuffix'):
                text = text.replace('+ $'+variable+' + "\\\"', '+ encodeString($'+variable+') + "\\\"')
            text = text.replace('+ $allItem[$i] + "\\\"', '+ encodeString($allItem[$i]) + "\\\"')
        elif relative == 'Script/FileTextureManager.mel':
            text = re.sub(r'\bsystem\s*\(', 'staging_bb_system (', text)
        elif relative == 'Script/bb_FixError.mel':
            # Remove the unavailable PyMel dependency; preserve callback repair behavior.
            text = text.replace('import pymel.core as pm', 'import maya.cmds as pm')
            text = replace_body(text, report, 'DelDJJ', '    python("import builtins; builtins._bb_staging_cleanup_ui()");')
            text = text.replace('报错清除完成！', '界面回调清理已执行；病毒文件按清单单独隔离。')
        text = substitutions.sub(lambda m: PREFIX+m[0], text)
        # Procedure identifiers in callback strings are prefixed, resource filenames are not.
        for filename in {part for f in active for part in Path(f['file']).parts}:
            token = filename if filename.endswith('.mel') else filename+'/'
            text = text.replace(PREFIX+token, token)
            if not filename.endswith('.mel'):
                text = text.replace('/'+PREFIX+filename, '/'+filename)
        write(PKG / 'native' / relative, text)
        native = audit(PKG / 'native' / relative)
        native_files.append({'path': relative, 'sha256': hashlib.sha256((PKG / 'native' / relative).read_bytes()).hexdigest(), 'source_encoding': report['candidate_decoding'], 'original_procedures': len(report['procedures']), 'native_procedures': len(native['procedures']), 'top_level_lines': native['top_level_lines']})
    support = PKG / 'native/bridge.mel'
    support_files = [{'path': 'bridge.mel', 'sha256': hashlib.sha256(support.read_bytes()).hexdigest()}] if support.is_file() else []
    data = {'files': files, 'native_files': native_files, 'support_files': support_files, 'procedures': procedures, 'entries': ENTRIES, 'original_declarations': sum(len(x['procedures']) for x in inventory), 'active_declarations': len(procedures), 'original_modified': False, 'prefix': PREFIX, 'archive_only': [x['file'] for x in inventory if x not in active], 'license': 'Original author notices retained, including LiuBen, Nilesh Jadhav, CGTOOLKIT, Brendan Ross, Crow Yeh and Highend3D metadata. No standalone suite license found; no new distribution rights asserted.'}
    write(PKG / 'catalog.json', json.dumps(data, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', 'bb_Tools/** -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'bb_tools').replace('RootMotionBakeTool', 'BBToolsTool')
    write(RC / 'launch_candidate.py', launch+'\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'bb_tools', 'registration': {'module': 'bb_tools', 'class_name': 'BBToolsTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in files], 'dependencies': ['Maya cmds/MEL/native UI, skin/follicle/nHair/blendShape', 'ADV helpers target original AdvancedSkeleton 5.74 rig conventions; other rigs require manual verification', 'FBX conversion requires installed fbxmaya and external user-selected FBX; no plugin installation performed'], 'acceptance_required': True, 'change_summary': 'Complete BB distribution retained byte-for-byte. Full active native suite with namespaced declarations, explicit UI startup and bundled paths; typed procedure API/read-only inventory, caller environment restoration, scratch weight XML, restricted QC settings, no-overwrite texture IO, explicit virus-file quarantine rather than userSetup deletion. Original installer and obsolete duplicate versions archived only.', 'verification_limitations': ['Real Maya GUI and production rigs not_run', 'Full suite native UI callbacks retain original broad scene scope; batch/API safe subset is documented, native workflows require backup scenes', 'Original third-party algorithms and legacy workflow assumptions retained; isolated declarations/selected algorithms do not validate every button', 'File copies/moves/config exports/quarantine and UI/scriptJob/optionVar changes are not covered by Maya Undo', 'Multi-file actions can partially succeed before a later failure; no claim of atomic rollback', 'No public redistribution license inferred from bundled author metadata']}
    write(RC / 'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(files), 'native_files': len(native_files), 'active_declarations': len(procedures)}))


if __name__ == '__main__':
    main()
