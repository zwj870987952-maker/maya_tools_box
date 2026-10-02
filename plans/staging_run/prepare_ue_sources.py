import ast
from prepare_external_candidate import ROOT, put, prepare
UNIT = ROOT / 'tools_staging_pool/05_ue_pipeline/ue_source_finder'
RC = UNIT / 'release_candidate'
PKG = RC / 'engine_toolkit/tools/ue_source_finder'
# Reuse the reviewed import metadata reader, copied self-contained for independent promotion.
source = (ROOT / 'tools_staging_pool/05_ue_pipeline/ue_context_menu/release_candidate/engine_toolkit/tools/ue_context_menu/__init__.py').read_text(encoding='utf-8')
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'read_source_paths')
put(PKG / 'source_paths.py', '\n'.join(source.splitlines()[node.lineno-1:node.end_lineno]))
put(PKG / '__init__.py', r'''"""Explicit source collection/copy with owned fresh session output and reports."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from .source_paths import read_source_paths

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'copy_sources'], 'default': 'inspect'},
    'output_dir': {'type': 'string', 'description': 'Existing parent directory; empty defaults Desktop'},
    'session_name': {'type': 'string', 'description': 'Optional new directory basename, default unique timestamp/UUID'},
    'source_mode': {'type': 'string', 'enum': ['first', 'all'], 'default': 'first'},
    'open_folders': {'type': 'boolean', 'default': False}}}

def _unreal():
    import unreal
    return unreal

def _safe_name(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 or ord(c) == 92 or c in '<>:"/|?*' for c in name) or name.endswith(('.', ' ')) or name in ('.', '..'):
        raise ValueError('Unsafe filesystem component: ' + str(name))
    if name.split('.')[0].casefold() in {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1,10)), *(f'lpt{i}' for i in range(1,10))}:
        raise ValueError('Reserved Windows name: ' + name)
    return name

def _hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    action, mode = kwargs.get('action', 'inspect'), kwargs.get('source_mode', 'first')
    if action not in ('inspect', 'copy_sources') or mode not in ('first', 'all'): raise ValueError('Invalid action/source_mode')
    if not isinstance(kwargs.get('open_folders', False), bool): raise ValueError('open_folders must be boolean')
    raw = kwargs.get('output_dir') or str(Path.home() / 'Desktop')
    if not isinstance(raw, str): raise ValueError('output_dir must be string')
    parent = Path(raw).resolve()
    if not parent.is_dir(): raise ValueError('Output parent must already exist')
    session = _safe_name(kwargs.get('session_name') or ('UE_Sources_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]))
    target = parent / session
    if target.exists(): raise ValueError('Session directory already exists; no overwrite: ' + str(target))
    assets = list(_unreal().EditorUtilityLibrary.get_selected_assets())
    if not assets or len(assets) > 10000: raise ValueError('Select 1..10000 UE assets')
    rows, seen, targets = [], set(), set()
    for asset in assets:
        record = read_source_paths(asset); asset_path = record['asset']
        if asset_path in seen: continue
        seen.add(asset_path)
        package = asset_path.split('.', 1)[0]
        parts = PurePosixPath(package).parts
        if len(parts) < 3 or parts[0] != '/': raise ValueError('Invalid UE package path: ' + package)
        folder = target.joinpath(*(_safe_name(part) for part in parts[1:-1]))
        folder.resolve().relative_to(target.resolve())
        name = _safe_name(record['name'])
        record.update(folder=str(folder), copies=[], missing=[], failed=[])
        paths = record['paths'][:1] if mode == 'first' else record['paths']
        if not paths: record['missing'].append({'source': None, 'reason': record['status']})
        for index, raw_source in enumerate(paths):
            source = Path(raw_source)
            if record['status'] == 'raw_relative' or not source.is_absolute():
                record['missing'].append({'source': raw_source, 'reason': 'Unresolved relative import source; not joined against current working directory'}); continue
            if not source.is_file():
                record['missing'].append({'source': raw_source, 'reason': 'Source file missing'}); continue
            source = source.resolve()
            extension = source.suffix
            filename = _safe_name(name + (('_src' + str(index+1)) if index else '') + extension)
            destination = folder / filename; key = str(destination).casefold()
            if key in targets: raise ValueError('Selected assets collide at: ' + str(destination))
            targets.add(key)
            record['copies'].append({'asset_name': name, 'asset_path': asset_path, 'source_path': str(source),
                'target_path': str(destination), 'target_filename': filename, 'renamed': filename != source.name,
                'sha256': _hash(source), 'size': source.stat().st_size})
        rows.append(record)
    return {'action': action, 'source_mode': mode, 'session': str(target), 'rows': rows,
            'open_folders': kwargs.get('open_folders', False), 'asset_mutations': [],
            'file_impact': 'Copies source files into a new session tree; TXT/JSON reports. Sources and import metadata unchanged; filesystem output is outside UE Undo'}

def _write(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f: f.write(text)

def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect': return plan
    session = Path(plan['session'])
    session.mkdir()  # Exclusive ownership; no merge with existing output.
    groups, copied, warnings = {}, [], []
    for row in plan['rows']:
        folder = Path(row['folder'])
        report = groups.setdefault(str(folder), {'success': [], 'missing_source': [], 'failed': []})
        report['missing_source'].extend({'asset_name': row['name'], 'asset_path': row['asset'], **m} for m in row['missing'])
        try: folder.mkdir(parents=True, exist_ok=True)
        except Exception as error:
            report['failed'].append({'asset_name': row['name'], 'asset_path': row['asset'], 'error': 'Output folder creation failed: ' + str(error)})
            continue
        for item in row['copies']:
            path = Path(item['source_path']); dest = Path(item['target_path']); owned = False
            try:
                if path.stat().st_size != item['size'] or _hash(path) != item['sha256']: raise ValueError('Source changed after preflight')
                with path.open('rb') as f, dest.open('xb') as out:
                    owned = True; shutil.copyfileobj(f, out, 1024 * 1024)
                if _hash(dest) != item['sha256']: raise ValueError('Copied content differs from preflight SHA')
                shutil.copystat(path, dest)
                report['success'].append(item); copied.append(str(dest))
            except Exception as error:
                if owned: dest.unlink(missing_ok=True)
                report['failed'].append({**item, 'error': str(error)})
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    logs = []
    for raw_folder, report in sorted(groups.items()):
        folder = Path(raw_folder)
        try:
            for key, label in [('success', '成功复制'), ('missing_source', '源文件缺失'), ('failed', '处理失败')]:
                if report[key]:
                    path = folder / (folder.name + '_' + label + '_' + stamp + '.txt')
                    _write(path, '===== UE资产' + label + '日志 =====\n' + json.dumps(report[key], ensure_ascii=False, indent=2) + '\n')
                    logs.append(str(path))
            if report['success']:
                path = folder / (folder.name + '_名单_' + stamp + '.txt')
                _write(path, '===== 成功复制文件名单 =====\n' + '\n'.join(item['target_path'] for item in report['success']) + '\n'); logs.append(str(path))
        except Exception as error: warnings.append('Report write failed ' + str(folder) + ': ' + str(error))
    summary = {'session': str(session), 'total_assets': len(plan['rows']), 'total_folders': len(groups),
        'total_success': sum(len(g['success']) for g in groups.values()),
        'total_missing': sum(len(g['missing_source']) for g in groups.values()),
        'total_failed': sum(len(g['failed']) for g in groups.values()), 'folder_logs': groups, 'copied': copied, 'logs': logs, 'warnings': warnings}
    try: _write(session / 'summary.json', json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    except Exception as error: summary['warnings'].append('summary.json failed: ' + str(error))
    if plan['open_folders']:
        if os.name != 'nt': summary['warnings'].append('Explorer opening supported on Windows only')
        else:
            for folder in sorted(groups):
                try: subprocess.Popen(['explorer.exe', folder], shell=False)
                except Exception as error: summary['warnings'].append('Explorer failed: ' + str(error))
    _unreal().log('UE source copy summary: ' + str({k:v for k,v in summary.items() if k.startswith('total_')}))
    return summary

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        success = not data.get('total_failed', 0) and not data.get('warnings')
        return {'success': success, 'tool_id': 'ue_source_finder', 'dry_run': dry_run, 'data': data,
                'errors': [] if success else ['Partial copy/report failure; see session summary and retained output']}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_source_finder', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui():
    result = run()
    _unreal().log(str(result))
    return result
''')
put(RC / 'tests/test_ue_source_finder.py', r'''from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_source_finder as t
class Asset:
    def __init__(self, folder, name, sources): self.folder, self.name, self.sources = folder, name, sources
    def get_name(self): return self.name
    def get_path_name(self): return self.folder + '/' + self.name + '.' + self.name
    def get_editor_property(self, name): return types.SimpleNamespace(extract_filenames=lambda: self.sources)
class Tests(unittest.TestCase):
    def fake(self, assets): return types.SimpleNamespace(EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda:assets), log=lambda s:None)
    def test_distinct_folder_copy_and_all_reports_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); src=root/'old.fbx'; src.write_bytes(b'FBX original bytes'); src2=root/'extra.fbx'; src2.write_bytes(b'second source')
            assets = [Asset('/Game/A/Hero', 'Body', [str(src),str(src2)]), Asset('/Game/B/Hero','Body',[str(src)]), Asset('/Game/A/Hero','Missing',[str(root/'missing.fbx')])]
            with patch.object(t, '_unreal', return_value=self.fake(assets)):
                args = dict(action='copy_sources', output_dir=d, session_name='Batch', source_mode='all')
                before = sorted(p.name for p in root.iterdir()); self.assertTrue(t.run(**args)['success']); self.assertEqual(sorted(p.name for p in root.iterdir()), before)
                result = t.run(dry_run=False, **args); self.assertTrue(result['success'], result)
                data = result['data']; self.assertEqual(data['total_success'], 3); self.assertEqual(data['total_missing'], 1)
                self.assertEqual((root/'Batch/Game/A/Hero/Body.fbx').read_bytes(), src.read_bytes())
                self.assertEqual((root/'Batch/Game/B/Hero/Body.fbx').read_bytes(), src.read_bytes())
                self.assertEqual((root/'Batch/Game/A/Hero/Body_src2.fbx').read_bytes(), b'second source')
                self.assertTrue((root/'Batch/summary.json').is_file()); self.assertTrue(any('名单' in p for p in data['logs']))
                self.assertTrue(any('源文件缺失' in p for p in data['logs']))
                self.assertFalse(t.run(dry_run=False, **args)['success'])
            self.assertEqual(src.read_bytes(), b'FBX original bytes')
    def test_failed_copy_report_and_first_source_default(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'raw.fbx'; src.write_bytes(b'bytes')
            with patch.object(t, '_unreal', return_value=self.fake([Asset('/Game/X','Hero',[str(src),str(src)])])):
                args=dict(action='copy_sources',output_dir=d,session_name='Batch')
                preview=t.run(**args); self.assertEqual(len(preview['data']['rows'][0]['copies']),1)
                with patch.object(t.shutil, 'copyfileobj', side_effect=OSError('copy failed')):
                    result=t.run(dry_run=False, **args); self.assertFalse(result['success']); self.assertEqual(result['data']['total_failed'],1)
                self.assertFalse((Path(d)/'Batch/Game/X/Hero.fbx').exists()); self.assertEqual(src.read_bytes(),b'bytes')
    def test_no_relative_guess_and_path_escape_refusal(self):
        with tempfile.TemporaryDirectory() as d, patch.object(t, '_unreal', return_value=self.fake([Asset('/Game/X','Hero',['../raw.fbx'])])):
            result=t.run(output_dir=d,session_name='Batch'); self.assertTrue(result['success']); self.assertEqual(result['data']['rows'][0]['copies'],[])
            self.assertFalse(t.run(output_dir=d,session_name='../escape')['success'])
if __name__ == '__main__': unittest.main()
''')
put(RC / 'docs/tools/ue_source_finder.md', '''# UE 源文件追溯复制候选

完整保留原选中资产→import_data源文件→按UE文件夹分类→复制并以资产名重命名→成功/缺失/失败日志与名单→汇总→打开目录功能。原无UI单文件SHA归档，import取消桌面打印与立即复制。native UE独立包，无Maya继承/注册，Schema/validate/execute/run结构化success/data/errors。dry_run默认True/action默认inspect，读选区/importmetadata/源SHA但不mkdir/复制/log/Explorer。

```python
from engine_toolkit.tools import ue_source_finder as t
preview = t.run(action='copy_sources', output_dir=r'D:/SourceCollect', session_name='Review01')
result = t.run(dry_run=False, action='copy_sources', output_dir=r'D:/SourceCollect', session_name='Review01')
```

output_dir必须现存，默认桌面；session_name缺省时间+随机后缀，预检显示自己的会话路径，下次执行可能分配新路径，需传相同session_name复核路径。新会话目录必须不存在，独占mkdir，不复用桌面旧目录；保存Game/Plugin mount完整父文件夹层级，防原仅末级目录分类合并不同UE路径。原第一源filename行为default source_mode=first保留，all额外源按_src2/3后缀，文件basename为asset_name+原extension，不改变UE资产名或importdata。source metadata读取复用第89项reviewed reader，代码独立复制source_paths.py，自包含，不依赖别候选。raw/相对路径绝不按cwd猜，missing记录；missing可有完整成功查询结果，不表示复制了全部资产，应检查total_missing。

整批碰撞/路径遍历/Windows保留名/selection<=10000预检；每源SHA/size执行前再核对，独占xb分块copy、目标SHA核对、copystat；失败只删除自己创建的部分文件，保留成功outputs与失败日志；进程中断/目录或日志异常可留下partial session。既有源不修改/删除，UE资产元数据不写，外部输出不受UE Undo。读大源计算SHA有IO成本，远程路径/源在copy时变化可能导致该项失败，不能保证生产者同时改写的snapshot。

每文件夹按需保存原4种TXT（成功复制/名单/源文件缺失/处理失败），多字段保留asset path/source/target/renamed/error，并summary.json结构化计数/完整folder_logs/生成路径。open_folders默认False（原自动弹资源管理器改显式True），Windows以参数数组explorer.exe调用，无shell命令拼接；仅打开本次组路径，非Windows或失败warnings如实记录。show_ui仅Output Log预检（原无窗口）；复制后log简短汇总，不开UE事务。原覆盖copy2改独占的新会话输出，明确行为变化与路径层级调整。

可衔接PrintSourcePaths查询、人工定位缺失源或重新生成FBX配置；只复制导入源文件不复制uasset、不修改reimport绑定，不承诺重新导入配置就正确。真实UE资产类型/multi-source/TXT/Explorer/跨版本均not_run；离线真实临时文件复制测试不替代UE验收。promotion.json仅engine/docs/tests预制路径，runtime_version/current SHA/人工验收后晋级，依旧不改Maya正式库。
''')
put(RC / 'acceptance.md', '''# UE 源文件追溯复制验收 not_run

备份UE项目，准备存在/缺失/无importdata/同名不同文件夹/多源资产、临时output_dir。import和dry_run不得建目录或开Explorer；核对路径清单和full Game父级分类；source_mode=first/all与_srcN命名、原asset名改名规则、Unicode/Windows保留名/同target碰撞/相对路径明确拒绝或missing。实际copy验证SHA/时间元数据/原源不变/UE importdata不变，新会话fourTXT+summary统计准确；existing session拒绝不覆盖，失败copy保留成功文件并删除自己partial、失败日志真实；纯missing生成missing日志不假计success。open_folders=True只打开自己的路径，无shell拼接。真实UE/Explorer/跨版本未验收，临时离线复制不算UE通过；通过后记录current candidate SHA/runtime_version/tool_id=ue_source_finder/accepted_by/date/passed=true，文件输出不能UE Undo撤回。
''')
prepare('05_ue_pipeline/ue_source_finder', 'Complete UE source file tracing/copy/rename, per-folder success/missing/failure/list reports, summary and explicit Explorer opening; new exclusive session tree and first/all modes', ['Unreal Editor PythonScriptPlugin/EditorScriptingUtilities', 'Windows Explorer only for optional open_folders'], ['Real UE source metadata/types and Explorer invocation/target versions not_run'], 'Original no-window source-copy workflow; explicit API and Output Log preview')
