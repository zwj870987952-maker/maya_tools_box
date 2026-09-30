"""Copy the intact local licensed mirror suite and generate provenance/catalog."""
import hashlib
import json
from pathlib import Path
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/anim_mirror_helper_v1_1'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/anim_mirror_helper_v1_1'


def main():
    original = UNIT / 'Anim_Mirror_Helper_v1_1_studio_lic'
    for source in original.rglob('*'):
        if source.is_file():
            target = PACKAGE / 'upstream' / source.relative_to(original)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    report = audit(PACKAGE / 'upstream/mirror_walk_tool_code.mel')
    resources = {p.relative_to(PACKAGE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((PACKAGE / 'upstream').rglob('*')) if p.is_file()}
    catalog = dict(entry='upstream/mirror_walk_tool_code.mel', resources=resources,
                   procedures={p['name']: p for p in report['procedures'] if p['global_scope']},
                   top_level_lines=report['top_level_lines'], lexical_decoding=report['lexical_decoding'])
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    rows = ['# Anim Mirror Helper 原始过程目录', '',
            '签名从未修改的 MEL 提取；行号用于追溯，不表示算法或 GUI 已验收。invoke 的 arguments 键须与参数名完全一致。', '',
            '| 过程 | 参数 | 返回 | 原文件行 |', '| --- | --- | --- | --- |']
    for name, proc in catalog['procedures'].items():
        params = ', '.join(p['type']+' '+p['name'] for p in proc['parameters']) or '无'
        rows.append('| `{}` | `{}` | `{}` | {} |'.format(name, params, proc['return_type'], proc['line']))
    (docs / 'anim_mirror_helper_v1_1_procedures.md').write_text('\n'.join(rows)+'\n', encoding='utf-8')
    files = sorted(p for folder in (RC/'maya_toolkit', RC/'docs', RC/'tests')
                   for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    promotion = dict(tool_id='anim_mirror_helper_v1_1',
                     registration=dict(module='anim_mirror_helper_v1_1', class_name='AnimMirrorHelperTool'),
                     files=[dict(source=p.relative_to(RC).as_posix(), target=p.relative_to(RC).as_posix()) for p in files],
                     resources=list(resources), source='../Anim_Mirror_Helper_v1_1_studio_lic',
                     dependencies=['Interactive Maya MEL/cmds, buttonManip, stock timeSlider procedures', 'existing maya_toolkit framework/core', 'Python 3'],
                     license='Custom Barnev Pavel Studio license; intact local copies; redistribution permission not established',
                     change_summary='All six original files and 90 global procedures preserved; typed calls, semantic workflow actions, read-only validation, Undo and runtime restoration, native gateway and promotion metadata.',
                     verification_limitations=['Actual rig mirroring/constraints/attributes/baking and viewport button pending GUI acceptance', 'Original catchQuiet may conceal failures', 'MEL globals, UI, tool context and clipboard cannot be undone as scene edits', 'No public redistribution authorized'],
                     acceptance_required=True)
    (RC/'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(procedures=len(catalog['procedures']), resources=len(resources))))


if __name__ == '__main__':
    main()
