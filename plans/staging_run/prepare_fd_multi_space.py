import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/fd_multi_space'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/fd_multi_space'


def main():
    resources = []
    for name in ('FD_Multi_Space_tool_GUI.py', 'FD_Multi_Space_tool_reference.py', 'FD_Multi_Space_tool_no_reference.py', 'Read_Me.rtf'):
        target = PACKAGE / 'upstream' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(UNIT / name, target)
        resources.append({'path': 'upstream/' + name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    (UNIT / '.gitattributes').write_text('FD_Multi_Space_tool_*.py -text\nRead_Me.rtf -text\n', encoding='utf-8', newline='\n')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'tool_id': 'fd_multi_space', 'raw_files': resources, 'source_functions': {'gui': ['launch_script1', 'launch_script2', 'create_main_ui'], 'reference': ['create_ui', 'driven_obj', 'driver_obj', 'connect_objs'], 'local': ['create_ui', 'driven_obj', 'driver_obj', 'connect_objs']}, 'license': 'Copyright 2023 Filippo Dattola; all rights reserved; source commercial use/adaptation/distribution require author permission. Private supplied-copy preparation only, no public publishing.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    value = {'tool_id': 'fd_multi_space', 'registration': {'module': 'fd_multi_space', 'class_name': 'MultiSpaceTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya cmds native GUI for two-mode three-step workflow', 'Existing BaseMayaTool/Undo framework'], 'source': '../FD_Multi_Space_tool_GUI.py', 'change_summary': 'Both complete original local-group/existing-parent algorithms and three-step UI, explicit weight aliases/no force, persistent UUID provenance and guarded multi-target constraints.', 'verification_limitations': ['Real Maya GUI/production rig/reference edits pending', 'Original temporary parenting causes scene hierarchy/constraint edits', 'All-rights-reserved supplied resource; do not publish'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'resources': len(resources), 'payload': len(files)}))


if __name__ == '__main__':
    main()
