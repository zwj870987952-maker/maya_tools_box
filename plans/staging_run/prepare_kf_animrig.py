import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/kf_animrig_ikfk'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/kf_animrig_ikfk'
PROCS = ['kfAnimRig_IKFK', 'matchTimeline', 'matchIKtoFK', 'matchFKtoIK', 'matchIKtoFKTen', 'matchFKtoIKTen', 'kfARI_Instruct']

HEADER = r'''
global proc mtbKF_checkNodes(string $nodes[])
{ python("from maya_toolkit.tools.kf_animrig_ikfk import runtime as r; r.check_nodes('" + stringArrayToString($nodes, ",") + "')"); }
global proc mtbKF_checkSelection()
{ string $nodes[] = `ls -sl`; mtbKF_checkNodes($nodes); }
global proc mtbKF_checkAttr(string $plug)
{ python("from maya_toolkit.tools.kf_animrig_ikfk import runtime as r; r.check_attr('" + $plug + "')"); }
global proc mtbKF_delete(string $nodes[])
{ python("from maya_toolkit.tools.kf_animrig_ikfk import runtime as r; r.delete_helpers('" + stringArrayToString($nodes, ",") + "')"); }
'''


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for source in sorted(UNIT.iterdir()):
        if not source.is_file() or source.name.startswith('.'):
            continue
        target = PACKAGE / 'upstream' / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, text in ((UNIT / '.gitattributes', '*.mel -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(text, encoding='utf-8', newline='\n')
    original = (UNIT / 'kfAnimRig_IKFK.mel').read_text(encoding='utf-8-sig')
    text = original
    for proc in sorted(PROCS, key=len, reverse=True):
        text = re.sub(r'\b' + proc + r'\b', 'mtbKF_' + proc, text)
    text = text.replace('kfAnimRig_IKFKWin', 'mtbKF_RigMatchWin').replace('kfARI_InstructWin', 'mtbKF_InstructionsWin')
    text = text.replace('btnARI_', 'mtbKF_btnARI_').replace('mainSaveForm', 'mtbKF_mainSaveForm').replace('scrollMT_Instruct', 'mtbKF_scrollInstructions')
    text = text.replace('mtbKF_matchIKtoFKTen(0)', 'mtbKF_matchIKtoFKTen()').replace('mtbKF_matchFKtoIKTen(0)', 'mtbKF_matchFKtoIKTen()')
    # Native timeline is routed to Python's explicit range/AutoKey/Undo loop.
    pattern = r'(global proc mtbKF_matchTimeline\(int \$which\)\s*\{)'
    text = re.sub(pattern, lambda m: m[1] + '\npython("from maya_toolkit.tools.kf_animrig_ikfk import runtime as r; r.invoke_timeline(" + $which + ")"); return;\n', text)
    for proc, action in [('matchIKtoFK', 'match_ik_to_fk'), ('matchFKtoIK', 'match_fk_to_ik'), ('matchIKtoFKTen', 'spline_ik_to_fk'), ('matchFKtoIKTen', 'spline_fk_to_ik')]:
        pattern = r'(global proc mtbKF_' + proc + r'\(\)\s*\{)'
        code = '\nif(!python("from maya_toolkit.tools.kf_animrig_ikfk import runtime as r; r.is_active()")){python("r.invoke(\\\"' + action + '\\\")"); return;}\n'
        text = re.sub(pattern, lambda m: m[1] + code, text)
    # All original delete operands are string arrays. Route each individually.
    text = re.sub(r'\bdelete\s+((?:\$\w+\s*)+);', lambda m: ' '.join('mtbKF_delete(%s);' % v for v in re.findall(r'\$\w+', m[1])), text)
    text = re.sub(r'\bsetAttr\s+(\([^()]+\))', lambda m: 'mtbKF_checkAttr(%s); setAttr %s' % (m[1], m[1]), text)
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('//'):
            # Source write xform/move/rotate use explicit array operand or current selection.
            for command in ('xform', 'move', 'rotate'):
                if re.search(r'(?<![\w`])\b' + command + r'\s+-', stripped) and not re.search(r'\b' + command + r'\s+-q\b', stripped):
                    match = re.search(r'\$(\w+)\s*;', stripped)
                    guard = 'mtbKF_checkNodes($%s); ' % match[1] if match else 'mtbKF_checkSelection(); '
                    line = re.sub(r'\b' + command + r'\s+-', guard + command + ' -', line)
            if 'eval ("parentConstraint ' in stripped:
                line = 'mtbKF_checkNodes($alignObjKF);\n' + line
            if re.search(r'parentConstraint \$\w+ \$\w+', stripped):
                destination = re.search(r'parentConstraint \$\w+ (\$\w+)', stripped)[1]
                line = 'mtbKF_checkNodes(%s);\n' % destination + line
        lines.append(line.expandtabs(4).rstrip())
    text = HEADER.strip() + '\n' + '\n'.join(lines).rstrip() + '\n'
    (PACKAGE / 'native.mel').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'kf_animrig_ikfk_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/kfAnimRig_IKFK.mel', tofile='native.mel')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': resources, 'source_procs': PROCS, 'license': 'Kiel Figgins, original author and instructions retained; no independent license supplied, private local candidate.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/jop_retarget_anim_v09/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('jop_retarget_anim', 'kf_animrig_ikfk').replace('JopRetargetTool', 'KFAnimRigTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'kf_animrig_ikfk', 'registration': {'module': 'kf_animrig_ikfk', 'class_name': 'KFAnimRigTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json', 'native.mel'], 'dependencies': ['Maya MEL/cmds', 'Kiel Figgins referenced KF Auto Rig exact nodes/attributes; original rigs not supplied', 'BaseMayaTool/Undo'], 'source': '../kfAnimRig_IKFK.mel', 'change_summary': 'Complete seven original MEL procedures and native UI, private procedure names, guarded target writes/helper deletes, explicit reference consent, Python timeline with finally state restoration.', 'verification_limitations': ['Real original KF rigs and GUI acceptance absent', 'Hand/leg/dog/advanced spline exact production behavior pending', 'Does not switch pinner IKFK automatically; native matching only', 'Original bake requires keyed channels for AutoKey; explicit candidate keys written destination scope'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'procs': len(PROCS), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
