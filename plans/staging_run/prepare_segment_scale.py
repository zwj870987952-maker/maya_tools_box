"""Package the complete two-language operation without automatic execution."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/segment_scale_fix'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/segment_scale_fix'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    files = []
    for source in sorted(UNIT.glob('*')):
        if source.suffix in ('.py', '.mel'):
            target = PKG / 'vendor' / (source.name + '.original')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files.append({'path': target.name, 'original': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    write(PKG / 'catalog.json', json.dumps({'files': files, 'behavior': 'Only selected joints segmentScaleCompensate -> False; empty selection is no-op warning in original, explicit validation failure in candidate', 'author': 'Original attribution not supplied; no license inferred'}, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', '*.py -text\n*.mel -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'segment_scale_fix').replace('RootMotionBakeTool', 'SegmentScaleFixTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'segment_scale_fix', 'registration': {'module': 'segment_scale_fix', 'class_name': 'SegmentScaleFixTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['original'] for r in files], 'dependencies': ['Maya cmds, API2 for instance detection'], 'acceptance_required': True, 'change_summary': 'Complete original selected-joint disable segmentScaleCompensate operation, both original Python/MEL archived by SHA; explicit scope, no-op-aware read-only preflight, locks/references/connections/true DAG instance checks, single Undo chunk and deferred Maya UI.', 'verification_limitations': ['Real Maya GUI, production skin/rig appearance and cross-version acceptance not_run', 'Joint compensation changes can alter visible child proportions; scene backup required for manual comparison']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'assets': len(files)}))


if __name__ == '__main__':
    main()
