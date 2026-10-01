"""Preserve all seven resources and every original procedure/class method."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/skin_info_and_super_connect'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/skin_info_and_super_connect'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(line.rstrip() for line in value.splitlines()).rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    files = []
    for source in sorted(UNIT.rglob('*')):
        if source.is_file() and 'release_candidate' not in source.parts and source.name != '.gitattributes':
            relative = source.relative_to(UNIT)
            target = PKG / 'vendor' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    suites = {}
    for suite, relative in (('skin192', 'Export - Import SkinCluster/skinInfo_V1.92.mel'), ('skin17', 'Export - Import SkinCluster/skinInfo_V1.7.mel'), ('connect', 'Super Connect/Super_Connect/Super_Connect.mel')):
        source = UNIT / relative
        report = audit(source)
        lines = source.read_text(encoding='utf-8-sig').splitlines()
        covered = {i for row in report['procedures'] for i in range(row['line'] - 1, row['end_line'])}
        body = '\n'.join(line for i, line in enumerate(lines) if i in covered)
        ui = '\n'.join(line for i, line in enumerate(lines) if i not in covered)
        # Keep all original algorithms under explicit archival identifiers, with
        # independent globals. Runtime/UI never execute the unsafe legacy bodies.
        for row in sorted(report['procedures'], key=lambda row: -len(row['name'])):
            body = re.sub(r'\b' + row['name'] + r'\b', 'scpstg_' + suite + '_legacy_' + row['name'], body)
            ui = re.sub(r'\b' + row['name'] + r'\b', 'scpstg_' + suite + '_' + row['name'], ui)
        # All named UI controls use suite prefixes, preserving complete layouts.
        controls = set(re.findall(r'(?m)^\s*(?:window|textFieldGrp|textFieldButtonGrp|textField|textScrollList|checkBox|checkBoxGrp|radioButton|progressBar)\b[^;]*?\s([A-Za-z_]\w*)\s*;', ui))
        controls.update({'SkinInfo', 'Super_Connect', 'Result', 'ResultLamb', 'TextF_TotalInfluences', 'TextF_WeightedInfluences', 'TextF_FileName', 'tFButton_export', 'tFButton_import', 'CHB_JSON', 'CHB_XML', 'CHB_JSON2', 'CHB_XML2', 'DeleteHistoryChBox', 'SourceTXF', 'DestinationTXF', 'ChangeControlsTSL_01', 'ChangeControlsTSL_02', 'RB1', 'RB2', 'RB3', 'Direct_T_CHB', 'Direct_R_CHB', 'Direct_S_CHB', 'Parent_constraints_CHB', 'Point_Orient_constraints_CHB', 'CBSprogressBar'})
        for name in sorted(controls, key=len, reverse=True):
            ui = re.sub(r'\b' + name + r'\b', 'scpstg_' + suite + '_' + name, ui)
        ui = re.sub(r'eval\s*`(scpstg_\w+_SelectInfluences)`', r'\1()', ui)
        # Replace all UI callback procedures with safe dispatch wrappers.
        wrappers = []
        for row in report['procedures']:
            if row['parameters']:
                continue  # Pure Remove_nameSpace helper remains in complete legacy body.
            name = 'scpstg_' + suite + '_' + row['name']
            ret = 'string ' if row['return_type'] == 'string' else ''
            statement = 'string $unused = ' if ret else ''
            command = 'python("__import__(\'maya_toolkit.tools.skin_info_and_super_connect.ui\',fromlist=[\'dispatch\']).dispatch(\'' + suite + '\',\'' + row['name'] + '\')")'
            wrappers.append('global proc ' + ret + name + '() {' + statement + command + ';' + (' return "";' if ret else '') + '}')
        body = re.sub(r'(?m)^proc ', 'global proc ', body)
        write(PKG / (suite + '_legacy.mel'), body)
        write(PKG / (suite + '_ui.mel'), '\n'.join(wrappers) + '\nglobal proc scpstg_' + suite + '_showUI() {\n' + ui + '\n}\n')
        suites[suite] = {'source': relative, 'procedures': report['procedures'], 'ui_controls': sorted(controls)}
    source = UNIT / 'Export & Import Skin Weights Script/Export-Import JointsWeights v1.3 UI Class.txt'
    tree = ast.parse(source.read_bytes())
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    methods = [n.name for n in klass.body if isinstance(n, ast.FunctionDef)]
    tree.body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef))]
    write(PKG / 'timal_original.py', ast.unparse(tree))
    write(PKG / 'catalog.json', json.dumps({'files': files, 'suites': suites, 'timal_methods': methods, 'copyright': 'SkinInfo/SuperConnect Khaled Hussein; Timal attribution from source; no license file supplied'}, ensure_ascii=False, indent=2))
    write(RC / '.gitattributes', '* -text')
    write(UNIT / '.gitattributes', '*/*.mel -text\n*/*/*.mel -text\n*/*.txt -text\n*/*/*.txt -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'skin_info_and_super_connect').replace('RootMotionBakeTool', 'SkinInfoSuperConnectTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'skin_info_and_super_connect', 'registration': {'module': 'skin_info_and_super_connect', 'class_name': 'SkinInfoSuperConnectTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in files], 'dependencies': ['Maya cmds/MEL/deformerWeights; original full GUI in interactive Maya'], 'acceptance_required': True, 'change_summary': 'Whole SkinInfo 1.92/1.7, SuperConnect, Timal 1.3, installer/icon/source provenance preserved. Full info/weighted influences/JSON/XML/batch import-export/bind/transfer/copy/weight locks plus prefix pairing direct/parent/point/orient channels and complete UI routes, explicit no-overwrite files and non-executable TXT influence parser, dry scope and Undo.', 'verification_limitations': ['Real Maya GUI, production skin/rig/topology compatibility and other versions not_run', 'External export files are not Maya Undo; old unverified topology requires explicit acknowledgement', 'Original unsafe MEL text evaluation and overwrite paths replaced; legacy procedures retained for audit, not called by public API/UI', 'Original installer never executed; no license inferred or publishing performed']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(files), 'procedures': {k: len(v['procedures']) for k, v in suites.items()}, 'timal_methods': methods}))


if __name__ == '__main__':
    main()
