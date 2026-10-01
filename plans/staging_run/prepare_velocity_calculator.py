"""Bundle complete original velocity tool and ready future layout."""
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/velocity_calculator'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/velocity_calculator'


def main():
    source = UNIT / 'maya_velocity_calculator.py'
    archive = PKG / 'upstream/maya_velocity_calculator.py.original'
    archive.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, archive)
    (PKG / 'catalog.json').write_text(json.dumps({'files': [{'path': source.name, 'archive': archive.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}], 'license': 'User prototype, no separate license supplied'}, indent=2) + '\n', encoding='utf-8', newline='\n')
    (UNIT / '.gitattributes').write_text('*.py -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'velocity_calculator').replace('RootMotionBakeTool', 'VelocityCalculatorTool')
    (RC / 'launch_candidate.py').write_text(launch, encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'velocity_calculator', 'registration': {'module': 'velocity_calculator', 'class_name': 'VelocityCalculatorTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [source.name], 'dependencies': ['Maya cmds/API2, no external resources/dependencies'], 'acceptance_required': True, 'change_summary': 'Complete original two-button velocity tool archived and adapted. Correct actual start/end samples with read-only MDGContext world matrices, general Maya time and linear unit conversion, explicit bounded inputs/structured results and lazy UI. Does not change timeline, preserves endpoint-distance and backward-difference semantics.', 'verification_limitations': ['Real Maya GUI/viewport message and production constraints/simulation sampling not_run', 'Average is endpoint displacement magnitude divided by duration, not traveled path length', 'Instant is a backward finite difference, not an analytic derivative', 'Referenced/locked nodes may be queried but scene dynamics with history/cache need manual validation', 'Positive duration required; original zero-duration 0 result deliberately rejected']}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'original_files': 1}))


if __name__ == '__main__':
    main()
