"""Mirror the intact licensed suite and derive callable metadata, not source edits."""
import hashlib
import json
import re
from pathlib import Path
import shutil

from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/anim_layer_v4_0'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/anim_layer_v4_0'


def main():
    upstream = PACKAGE / 'upstream'
    upstream.mkdir(parents=True, exist_ok=True)
    original = UNIT / 'anim_layer_v4_0'
    for source in original.rglob('*'):
        if source.is_file():
            target = upstream / source.relative_to(original)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    editions = {}
    for edition, entry in [('full', 'layerEditor.mel'), ('no_ui', 'no_UI_version/layerEditor_no_UI.mel')]:
        report = audit(upstream / entry)
        procedures = {p['name']: p for p in report['procedures'] if p['global_scope']}
        editions[edition] = dict(entry='upstream/' + entry, sha256=report['sha256'],
                                 procedures=procedures, top_level_lines=report['top_level_lines'],
                                 duplicate_names=report['duplicate_names'], lexical_decoding=report['lexical_decoding'])
    resources = {p.relative_to(PACKAGE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(upstream.rglob('*')) if p.is_file()}
    (PACKAGE / 'catalog.json').write_text(json.dumps({'editions': editions, 'resources': resources}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    rows = ['# Anim Layer v4.0 过程签名目录', '',
            '从完整原始文件声明生成；静态标签不覆盖调用链，不表示 Maya 验证或最终效果。',
            'API 先 inventory 查选定版本/过程，再用 arguments 的同名键调用；原文件行号与返回类型保留在 catalog.json。', '']
    patterns = [(r'(?<![$\w])file\s+-', '文件命令'), (r'\bdelete\s', '删除'),
                (r'\b(?:bakeResults|bakeSimulation|filterCurve|cutKey|setKeyframe)\b', '动画写入'),
                (r'\b(?:setAttr|connectAttr|disconnectAttr|editDisplayLayerMembers|editRenderLayerMembers)\b', '属性/连接写入'),
                (r'\b(?:window|menuItem|treeView|scriptJob|optionVar|createLayerEditor)\b', 'UI/设置/回调'),
                (r'\b(?:evaluationManager|refresh|setTimeSliderVisible)\b', '运行状态'),
                (r'\bselect(?:Key)?\s', '选择')]
    for edition, entry in editions.items():
        text_lines = (PACKAGE / entry['entry']).read_bytes().decode('latin-1').splitlines()
        rows.extend(['## ' + edition, '', '| 过程 | parameters | 返回 | 原文件行 | 直接文本中出现的影响 |', '| --- | --- | --- | --- | --- |'])
        for name, proc in entry['procedures'].items():
            body = '\n'.join(text_lines[proc['line']-1:proc['end_line']])
            effects = [label for pattern, label in patterns if re.search(pattern, body)]
            params = ', '.join(p['type'] + ' ' + p['name'] for p in proc['parameters']) or '无'
            rows.append('| `{}` | `{}` | `{}` | {} | {} |'.format(name, params, proc['return_type'], proc['line'], '、'.join(effects) or '未标记；仍须检查依赖过程'))
        rows.append('')
    (docs / 'anim_layer_v4_0_procedures.md').write_text('\n'.join(rows).rstrip() + '\n', encoding='utf-8')
    files = sorted(p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests')
                   for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    description = {
        'tool_id': 'anim_layer_v4_0',
        'registration': {'module': 'anim_layer_v4_0', 'class_name': 'AnimLayerSuiteTool'},
        'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in files],
        'resources': list(resources),
        'dependencies': ['Maya MEL/cmds and original animation/render/display layerEditor support', 'Interactive Maya for full edition and most UI-dependent procedures', 'existing maya_toolkit framework/core', 'Python 3'],
        'source': '../anim_layer_v4_0',
        'license': 'Custom Barnev Pavel agreement plus Autodesk notices; intact sources/resources retained locally; no redistribution or relicensing claim',
        'change_summary': 'Intact six-file suite and all global signatures retained; self-contained full/NoUI loaders, typed MEL calls, inventory/dry-run, framework result/Undo, export collision guard and UI gateway; original source and callbacks unchanged.',
        'verification_limitations': ['Full editor GUI and all menu operations pending', 'NoUI is not universally headless: many procedures need stock Maya UI', 'MEL global definitions/UI/options/scriptJobs are not reverted by scene Undo', 'Legacy source encoding and other Maya versions unverified', 'License does not establish public redistribution permission'],
        'acceptance_required': True,
    }
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'global_procedures': {e: len(c['procedures']) for e, c in editions.items()}, 'resources': len(resources)}))


if __name__ == '__main__':
    main()
