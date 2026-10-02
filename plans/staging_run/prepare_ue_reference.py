import ast
from prepare_external_candidate import ROOT, put, prepare
UNIT = ROOT / 'tools_staging_pool/05_ue_pipeline/ue_reference_checker'
RC = UNIT / 'release_candidate'
PKG = RC / 'engine_toolkit/tools/ue_reference_checker'
put(PKG / '__init__.py', r'''"""UE direct hard/soft package referencers; explicit GUI and browser actions."""
import re
import threading

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'show_ui', 'locate', 'close_ui'], 'default': 'inspect'},
    'pattern': {'type': 'string', 'default': '_zoo', 'maxLength': 256},
    'package_name': {'type': 'string'}}}

def _unreal():
    import unreal
    return unreal

def _main_thread():
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError('Invoke on the UE Editor main thread; no Unreal API on workers')

def _package(name):
    if not isinstance(name, str) or not re.fullmatch(r'/[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)+', name):
        raise ValueError('Exact UE package path required, not object path')
    return name

def collect_results(pattern='_zoo'):
    _main_thread()
    if not isinstance(pattern, str) or not pattern or len(pattern) > 256: raise ValueError('Nonempty regex up to 256 characters required')
    compiled = re.compile(pattern, re.IGNORECASE)
    u = _unreal(); registry = u.AssetRegistryHelpers.get_asset_registry()
    if registry.is_loading_assets(): raise RuntimeError('Asset Registry is still loading; wait until it finishes before judging references')
    selected = list(u.EditorUtilityLibrary.get_selected_asset_data())
    if len(selected) > 10000: raise ValueError('Selection exceeds 10000 assets')
    options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True,
        include_searchable_names=False, include_soft_management_references=False, include_hard_management_references=False)
    rows, seen = [], set()
    for ad in selected:
        package = str(ad.package_name)
        if package in seen: continue
        seen.add(package)
        row = {'asset_name': str(ad.asset_name), 'package_path': package, 'correct': None, 'correct_refs': [], 'all_refs': [], 'all_ref_count': None, 'error': None}
        try:
            refs = registry.get_referencers(_package(package), options)
            if refs is None: raise RuntimeError('Registry query returned None; not a confirmed empty reference list')
            refs = sorted(set(str(p) for p in refs))
            matching = [p for p in refs if compiled.search(p)]
            row.update(correct=bool(matching), correct_refs=matching, all_refs=refs, all_ref_count=len(refs))
        except Exception as error: row['error'] = str(error)
        rows.append(row)
    return rows

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    _main_thread()
    action = kwargs.get('action', 'inspect')
    if action not in parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
    if action == 'locate':
        name = _package(kwargs.get('package_name'))
        u = _unreal(); registry = u.AssetRegistryHelpers.get_asset_registry()
        assets = list(registry.get_assets(u.ARFilter(package_names=[name])) or [])
        paths = []
        for asset in assets:
            obj = asset.get_asset()
            if obj is not None: paths.append(str(obj.get_path_name()))
        if not paths: raise ValueError('No loadable asset in exact package: ' + name)
        return {'action': action, 'package_name': name, 'object_paths': paths, 'asset_mutations': []}
    if action == 'close_ui': return {'action': action, 'asset_mutations': []}
    return {'action': action, 'pattern': kwargs.get('pattern', '_zoo'), 'rows': collect_results(kwargs.get('pattern', '_zoo')), 'asset_mutations': [], 'files_written': [],
            'scope': 'Direct on-disk package hard and soft referencers; regex case-insensitive. Not recursive/live-scene dependency validation'}

def execute(**kwargs):
    plan = validate(**kwargs)
    action = plan['action']
    if action == 'locate': _unreal().EditorAssetLibrary.sync_browser_to_objects(plan['object_paths'])
    elif action == 'show_ui':
        from .ui import show_result_window
        show_result_window(plan['rows'])
    elif action == 'close_ui':
        from .ui import close_ui
        close_ui()
    return plan

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        errors = [row['package_path'] + ': ' + row['error'] for row in data.get('rows', []) if row['error']]
        return {'success': not errors, 'tool_id': 'ue_reference_checker', 'dry_run': dry_run, 'data': data, 'errors': errors}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_reference_checker', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui(pattern='_zoo'): return run(dry_run=False, action='show_ui', pattern=pattern)
''')

original = (UNIT / 'UE资产引用检查器.py').read_text(encoding='utf-8')
tree = ast.parse(original)
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'show_result_window')
ui = '\n'.join(original.splitlines()[node.lineno-1:node.end_lineno])
ui = ui.replace('    path_index: dict[str, str] = {r["asset_name"]: r["package_path"] for r in results}', '    # Package paths are row IDs; duplicate display names never overwrite identity.')
ui = ui.replace('        bad_count = total - ok_count', '        bad_count = sum(r["correct"] is False for r in results)\n        unknown_count = sum(r["correct"] is None for r in results)')
ui = ui.replace('text=f"✘  未正确引用  {bad_count}"', 'text=f"✘  未正确引用  {bad_count}    查询未知 {unknown_count}"')
ui = ui.replace('key=lambda x: x["correct"]', 'key=lambda x: x["correct"] is True')
ui = ui.replace('            if r["correct"]:', '''            if r["correct"] is None:
                tree.insert("", tk.END, iid=r["package_path"],
                    values=("? 查询失败", r["asset_name"], r["error"]), tags=("bad",))
            elif r["correct"]:''')
ui = ui.replace('            _main_thread_queue.put(_unregister_tick)', '            # Slate tick unregisters once root is gone, on its own main thread.')
ui = ui.replace('        root.mainloop()', '        return root')
ui = ui.replace('    threading.Thread(target=_run, daemon=True).start()', '''    try:
        _run()
    except Exception:
        close_ui()
        raise''')
put(PKG / 'ui.py', r'''"""Original complete Tk table, pumped without worker threads by UE Slate tick."""
import tkinter as tk
from tkinter import ttk
import queue
from . import _unreal, _main_thread, run
unreal = _unreal()
WINDOW_WIDTH, WINDOW_HEIGHT = 880, 460
_active_root = None
_main_thread_queue = queue.Queue()
_tick_handle = None

def _process_main_thread_queue(delta_seconds):
    _main_thread()
    for _ in range(100):
        try: task = _main_thread_queue.get_nowait()
        except queue.Empty: break
        try: task()
        except Exception as error: unreal.log_error('[AssetChecker] ' + str(error))
    root = _active_root
    if root is None:
        _unregister_tick()
        return
    try:
        root.update_idletasks(); root.update()
    except tk.TclError:
        close_ui()

def _register_tick():
    global _tick_handle
    _main_thread()
    if _tick_handle is None: _tick_handle = unreal.register_slate_post_tick_callback(_process_main_thread_queue)

def _unregister_tick():
    global _tick_handle
    _main_thread()
    if _tick_handle is not None:
        unreal.unregister_slate_post_tick_callback(_tick_handle); _tick_handle = None

def _sync_browser(package_name):
    result = run(dry_run=False, action='locate', package_name=package_name)
    if not result['success']: unreal.log_warning('[AssetChecker] ' + '; '.join(result['errors']))

def close_ui():
    global _active_root
    _main_thread()
    root, _active_root = _active_root, None
    if root is not None:
        try: root.destroy()
        except tk.TclError: pass
    _unregister_tick()
    while True:
        try: _main_thread_queue.get_nowait()
        except queue.Empty: break

''' + ui)

put(RC / 'tests/test_ue_reference_checker.py', r'''from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_reference_checker as t
class Tests(unittest.TestCase):
    def fake(self, rows, refs, loading=False):
        self.synced = []
        def query(name, options):
            self.assertTrue(options.include_hard_package_references); self.assertTrue(options.include_soft_package_references)
            self.assertFalse(options.include_searchable_names)
            value = refs[name]
            if isinstance(value, Exception): raise value
            return value
        obj = types.SimpleNamespace(get_path_name=lambda: '/Game/A/Hero.Hero')
        registry = types.SimpleNamespace(is_loading_assets=lambda: loading, get_referencers=query, get_assets=lambda f:[types.SimpleNamespace(get_asset=lambda: obj)])
        return types.SimpleNamespace(EditorUtilityLibrary=types.SimpleNamespace(get_selected_asset_data=lambda: rows),
            AssetRegistryHelpers=types.SimpleNamespace(get_asset_registry=lambda: registry),
            AssetRegistryDependencyOptions=lambda **kw:types.SimpleNamespace(**kw), ARFilter=lambda **kw:kw,
            EditorAssetLibrary=types.SimpleNamespace(sync_browser_to_objects=self.synced.append))
    def test_distinct_packages_regex_and_unknown(self):
        rows = [types.SimpleNamespace(package_name='/Game/A/Hero', asset_name='Hero'), types.SimpleNamespace(package_name='/Game/B/Hero', asset_name='Hero'), types.SimpleNamespace(package_name='/Game/C/Bad', asset_name='Bad')]
        refs = {'/Game/A/Hero':['/Game/ZOO/Map_ZOO','/Game/Other','/Game/Other'], '/Game/B/Hero':[], '/Game/C/Bad':RuntimeError('Registry error')}
        with patch.object(t, '_unreal', return_value=self.fake(rows, refs)):
            result = t.run(); self.assertFalse(result['success'])
            found = result['data']['rows']; self.assertEqual(len(found), 3)
            self.assertTrue(found[0]['correct']); self.assertEqual(found[0]['all_ref_count'], 2)
            self.assertFalse(found[1]['correct']); self.assertIsNone(found[2]['correct']); self.assertIsNone(found[2]['all_ref_count'])
    def test_loading_and_invalid_regex_fail_without_false_empty(self):
        with patch.object(t, '_unreal', return_value=self.fake([], {}, loading=True)):
            self.assertFalse(t.run()['success'])
        with patch.object(t, '_unreal') as unreal:
            self.assertFalse(t.run(pattern='[')['success']); unreal.assert_not_called()
    def test_browser_paths_and_dryrun_and_worker_rejection(self):
        with patch.object(t, '_unreal', return_value=self.fake([], {})):
            self.assertTrue(t.run(action='locate', package_name='/Game/A/Hero')['success']); self.assertEqual(self.synced, [])
            self.assertTrue(t.run(dry_run=False, action='locate', package_name='/Game/A/Hero')['success'])
            self.assertEqual(self.synced, [['/Game/A/Hero.Hero']])
        with patch.object(t.threading, 'current_thread', return_value=object()), patch.object(t, '_unreal') as unreal:
            self.assertFalse(t.run()['success']); unreal.assert_not_called()
if __name__ == '__main__': unittest.main()
''')
put(RC / 'docs/tools/ue_reference_checker.md', '''# UE 资产引用检查器候选

原资产选择→AssetRegistry direct hard/soft package referencers→忽略大小写_zoo正则→完整880x460深色Tk结果表/统计/异常优先/双滚动/右键定位/关闭保留，原单文件SHA归档，不自动main。纯UE模块，无Maya继承/注册；validate/execute/run和Schema、结构化success/data/errors。inspect默认只读、pattern默认_zoo可配置、locate exact package_name、show_ui打开结果、close_ui移除自己窗口和Slate callback。dry_run不打开/关闭UI、不改变Content Browser选区，不保存资产或写外部文件。

查询在UE主线程，不启动worker或强制扫描。AssetRegistry正在加载时拒绝判定，get_referencers异常或None记unknown并overall success=False，保留其他结果，不把失败当无引用。空列表才是确认零directrefs；按package去重，两个同名资产路径独立。pattern是路径文本匹配，correct意味着至少一个directreferencer符合约定，不等于UE资产技术正确、无循环、场景已加载或资产可以安全删除；不递归，不包含management/searchable-name。unsaved编辑可能未进入on-disk registry。

```python
from engine_toolkit.tools import ue_reference_checker as t
result = t.run(pattern='_zoo')
t.show_ui(pattern='_zoo')
t.run(dry_run=False, action='locate', package_name='/Game/Props/Hero')
t.run(dry_run=False, action='close_ui')
```

UI沿用原全部widget/交互，改为UE Slate tick在同一个主线程pump Tk update，不使用Tk.mainloop堵塞UE，不从其他线程quit/destroy Tk；根窗口关闭下一tick卸载，显式close立即卸载并清队列；不改变其它应用窗口。每tick任务至多100，逐任务异常记录，单例重开UI替换旧Tk root。定位使用ARFilter exact包→object path strings，修复原sync_browser_to_objects传Object而不是Array[str]。locate会加载资产与更改浏览器选区，非场景或文件写入；不宣称GUI体验已通过。Tk/Tcl在目标UE Python可能缺失，需要本地环境验证，代码不会安装依赖。

所有UI/API资源在engine_toolkit/tools/ue_reference_checker，自包含docs/tests/promotion。只预览晋级，真实UE验收后runtime_version/current SHA/人名日期才允许apply；无Maya面板伪入口。引用结果可指导人工检查/定位，不能作为自动杀毒、删除或修复依据。离线3mock/临时最终布局通过不等于UE结果/窗口/Slate实际验证。

参考：[AssetRegistry](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetRegistry?application_version=5.5)、[EditorAssetLibrary sync_browser_to_objects](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary?application_version=5.5)。
''')
put(RC / 'acceptance.md', '''# UE 引用检查人工验收 not_run

备份UE项目、启用Python Editor Script/EditorScriptingUtilities、核对Tk/Tcl可用。import无窗口；registry扫描完成后选中same-name distinct-package资产、有hard/soft _zoo匹配/无匹配/无refs，用Reference Viewer核对direct引用；query error/None/正在加载显示失败或unknown，不能假无refs。invalidregex/dry show_ui不改UI/资产/文件。实际show_ui深色表格统计、未知/异常优先/滚动、右键正确package定位（Array[str] path）、单例反复重开与关闭；UE继续响应，关闭后Slate callback无残留，不从worker调用API/Tk。检查asset/uasset不保存不dirty，locate只改变浏览器选区与加载缓存。目标Python缺Tk说明条件缺失，不能mock当实测。满意后记录UE runtime_version/current candidate SHA/tool_id=ue_reference_checker/passed=true/accepted_by/date，人工验收前仍待整理池。
''')
prepare('05_ue_pipeline/ue_reference_checker', 'Complete UE referencer regex checker and original dark Tk table/browser navigation with unknown/error states and single-main-thread Slate lifecycle', ['Unreal Editor PythonScriptPlugin/EditorScriptingUtilities/AssetRegistry', 'Target UE Python tkinter/Tcl'], ['Real Unreal registry/Reference Viewer/Tk GUI/Slate lifecycle not_run'], 'Original UE dark Tk reference results table with right-click browser navigation')
