"""Read-only candidate audit; write the consolidated human acceptance handoff."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import scan_pool
from promote_candidate import fingerprint, payload, registry_change


def main():
    root, run = scan_pool.ROOT, scan_pool.RUN
    manifest = json.loads((run / 'manifest.json').read_text(encoding='utf8'))
    errors, targets, classes, rows = [], {}, {}, []
    for key in ('catalog_missing_folders', 'unlisted_folders', 'duplicate_catalog_folders'):
        if manifest[key]:
            errors.append({key: manifest[key]})
    for item in manifest['tools']:
        name = item['source_path']
        candidate = root / item['candidate_path']
        try:
            assert item['status'] in ('prepared_verified_offline', 'prepared_unverified')
            assert item['candidate_complete'] and item['entry_exists']
            assert (root / item['acceptance_instructions']).is_file()
            assert item.get('source_commit')
            description = json.loads((candidate / 'promotion.json').read_text(encoding='utf8'))
            digest = fingerprint(candidate, description)
            assert digest == item['promotion']['candidate_sha256'], 'Stale checked fingerprint'
            pairs = payload(candidate, description)
            assert any(target.suffix == '.md' and 'docs' in target.parts for _, target in pairs)
            assert any(target.name.startswith('test_') for _, target in pairs)
            if description.get('registration'):
                registry_change(description)
                cls = description['registration']['class_name']
                assert cls not in classes, 'Duplicate registration class: ' + cls
                classes[cls] = name
            for _, target in pairs:
                key = str(target).casefold()
                assert key not in targets, 'Cross-candidate target collision: ' + str(target)
                targets[key] = name
            checks = [c for c in item['offline_checks'] if c.get('kind') != 'required_runtime_evidence']
            failures = [c for c in checks if not c.get('passed')]
            rows.append({'source_path': name, 'tool_id': description['tool_id'],
                         'runtime': description.get('runtime', 'maya'),
                         'candidate_sha256': digest, 'payload_files': len(pairs),
                         'source_commit': item['source_commit'],
                         'offline_checks_passed': sum(bool(c.get('passed')) for c in checks),
                         'offline_checks_total': len(checks),
                         'failed_checks': [{'kind': c.get('kind'), 'reason': c.get('reason'),
                                            'output': c.get('output', '')} for c in failures]})
        except (AssertionError, ValueError, OSError, KeyError) as error:
            errors.append({'source_path': name, 'error': str(error)})
    # These paths must have no changes across the entire preparation branch.
    forbidden = subprocess.check_output(
        ['git', 'diff', 'main', '--name-only', '--', 'maya_toolkit', 'engine_toolkit',
         'knowledge/_generated', 'AGENTS.md', 'DEVELOPMENT_SPEC.md'], cwd=root, text=True).splitlines()
    if forbidden:
        errors.append({'protected_paths_changed': forbidden})
    commits = sorted({item['source_commit'] for item in manifest['tools'] if item.get('source_commit')})
    commit_check = subprocess.run(['git', 'cat-file', '--batch-check=%(objecttype)'], cwd=root,
                                  input='\n'.join(commits) + '\n', text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if any(kind != 'commit' for kind in commit_check.stdout.splitlines()):
        errors.append({'invalid_checkpoint_commits': commit_check.stdout})
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    report = {'kind': 'final_candidate_handoff_audit', 'passed': not errors, 'audited_at': now,
              'physical_candidates': len(manifest['tools']), 'audited_candidates': len(rows),
              'payload_files': len(targets), 'status_counts': dict(collections.Counter(
                  item['status'] for item in manifest['tools'])),
              'runtime_counts': dict(collections.Counter(row['runtime'] for row in rows)),
              'maya_acceptance_counts': dict(collections.Counter(
                  item['maya_acceptance']['status'] for item in manifest['tools'])),
              'offline_failures': [{'source_path': row['source_path'], 'checks': row['failed_checks']}
                                   for row in rows if row['failed_checks']],
              'protected_paths_changed': forbidden, 'errors': errors, 'candidates': rows}
    scan_pool.dump(run / 'FINAL_AUDIT.json', report)
    if errors:
        print(json.dumps({'passed': False, 'errors': errors}, ensure_ascii=True))
        raise SystemExit(1)
    lines = ['# 待整理工具池逐项验收总表', '', '生成时间：' + now, '',
             f"动态范围共 {len(rows)} 项，全部候选完整且晋级预检有效；正式库未迁入。",
             f"状态：{report['status_counts'].get('prepared_verified_offline', 0)} 项 prepared_verified_offline，"
             f"{report['status_counts'].get('prepared_unverified', 0)} 项 prepared_unverified。两种状态均须用户实际验收。",
             f"运行环境：{report['runtime_counts'].get('maya', 0)} 项 Maya、"
             f"{report['runtime_counts'].get('maya_unreal', 0)} 项 Maya + Unreal、"
             f"{report['runtime_counts'].get('unreal_editor', 0)} 项 Unreal Editor、"
             f"{report['runtime_counts'].get('windows_standalone', 0)} 项独立 Windows。",
             '真实 Maya GUI / Unreal / Windows 人工验收均未完成；isolated mayapy、Qt 离屏和 mock 结果不代替验收。',
             'heartbeat 已停用（PAUSED），本次没有消费重置卡、购买额度或运行 Obsidian 同步。', '',
             '## 如何逐项验收', '',
             '按每行「验收步骤」在对应真实宿主中使用备份场景和临时目录执行；记录版本、用户、日期和结果。',
             '每包的 launch_candidate.py 是候选入口，promotion.json 列出未来正式路径和注册信息；当前包全部保留在 tools_staging_pool。',
             '通过后写入 passed=true、tool_id、candidate_sha256、accepted_by、date，以及 maya_version / runtime_version；',
             '用 promote_candidate.py 先预览，再使用 --acceptance 和 --apply 按单项晋级。',
             'Maya + Unreal 项同时需要两个宿主版本。版本、授权或功能不符合预期时先修改候选并重新验收；不得复用旧指纹。', '',
             '## 需先处理的已知失败', '',
             'Anim Filters：当前 Maya 2025 解释器缺少 SciPy，科学计算依赖测试失败；Butterworth / Median 需要兼容的 SciPy 安装后复验。',
             '其 Qt 测试因 standalone 创建 widgets 曾崩溃而跳过；不得算作 UI 通过。详情保留在 manifest.json 和对应验收说明。',
             '其他候选的许可、版本限制、外部插件/素材和行为变化见各自文档与验收步骤；离线通过不代表这些条件已满足。', '',
             '## 验收清单', '',
             '| 序号 | 分类 | 工具 | 真实宿主 | 离线检查 | 验收步骤 | 晋级清单 |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    labels = {'maya': 'Maya', 'maya_unreal': 'Maya + Unreal',
              'unreal_editor': 'Unreal Editor', 'windows_standalone': 'Windows'}
    for index, (item, row) in enumerate(zip(manifest['tools'], rows), 1):
        candidate = root / item['candidate_path']
        description = json.loads((candidate / 'promotion.json').read_text(encoding='utf8'))
        docs = next(candidate / pair['source'] for pair in description['files']
                    if pair['target'].replace('\\', '/').startswith('docs/tools/')
                    and pair['target'].endswith('.md'))
        checks = f"{row['offline_checks_passed']}/{row['offline_checks_total']}"
        if row['failed_checks']:
            checks += '（有失败，见上文）'
        lines.append(f"| {index} | {item['source_path'].split('/')[0]} | "
                     f"[{row['tool_id']}](<{docs.as_posix()}>) | {labels[row['runtime']]} | {checks} | "
                     f"[待验收](<{(root / item['acceptance_instructions']).as_posix()}>) | "
                     f"[promotion.json](<{(candidate / 'promotion.json').as_posix()}>) |")
    lines += ['', '## 对账与恢复', '',
              '[manifest.json](manifest.json) 保存逐项状态、检查证据、候选指纹和实际源提交。',
              '[FINAL_AUDIT.json](FINAL_AUDIT.json) 保存候选完整性、目标冲突、指纹和受保护路径对账结果。',
              '[RUN_LOG.md](RUN_LOG.md) 保存实际整理记录和额度检查。',
              '晋级预检和最终对账为只读检查，未执行任何 --apply。']
    (run / 'MAYA_ACCEPTANCE.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
    manifest['execution'].update({'state': 'completed', 'current_tool': None,
                                  'heartbeat_status': 'PAUSED', 'heartbeat_verified': True,
                                  'completed_at': now, 'completion_audit': 'plans/staging_run/FINAL_AUDIT.json',
                                  'acceptance_summary': 'plans/staging_run/MAYA_ACCEPTANCE.md'})
    scan_pool.dump(run / 'manifest.json', manifest)
    print(json.dumps({key: report[key] for key in ('passed', 'audited_candidates',
                                                 'payload_files', 'status_counts', 'runtime_counts')},
                     ensure_ascii=True))


if __name__ == '__main__':
    main()
