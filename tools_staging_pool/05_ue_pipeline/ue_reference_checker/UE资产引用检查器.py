import unreal
import re
import tkinter as tk
from tkinter import ttk
import threading
import queue

# ============================================================
# 配置区 — 按需修改
# ============================================================

CORRECT_REF_PATTERN = r"_zoo"  # 正确引用的模式，忽略大小写
WINDOW_WIDTH  = 880
WINDOW_HEIGHT = 460

# 单例：保证同时只有一个结果窗口
_active_root: tk.Tk | None = None

# 主线程任务队列：tkinter 子线程 → Unreal 主线程
_main_thread_queue: queue.Queue = queue.Queue()
_tick_handle = None

# ============================================================
# 主线程 Tick 队列（仅用于右键定位，其余 UI 操作不触碰 Unreal API）
# ============================================================

def _process_main_thread_queue(delta_seconds: float) -> None:
    try:
        while True:
            _main_thread_queue.get_nowait()()
    except queue.Empty:
        pass


def _register_tick() -> None:
    global _tick_handle
    if _tick_handle is None:
        _tick_handle = unreal.register_slate_post_tick_callback(_process_main_thread_queue)


def _unregister_tick() -> None:
    global _tick_handle
    if _tick_handle is not None:
        unreal.unregister_slate_post_tick_callback(_tick_handle)
        _tick_handle = None


def _sync_browser(package_name: str) -> None:
    """在 Unreal 主线程执行，将资产定位到内容浏览器。"""
    try:
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        # 用 ARFilter 按包名精确查询，不依赖路径格式拼接
        ar_filter = unreal.ARFilter(package_names=[package_name])
        asset_data_list = ar.get_assets(ar_filter)

        if not asset_data_list:
            unreal.log_warning(f"[AssetChecker] 注册表中未找到资产: {package_name}")
            return

        objects = [ad.get_asset() for ad in asset_data_list]
        objects = [o for o in objects if o is not None]

        if objects:
            unreal.EditorAssetLibrary.sync_browser_to_objects(objects)
            unreal.log(f"[AssetChecker] 已定位: {package_name}")
        else:
            unreal.log_warning(f"[AssetChecker] 资产对象加载失败: {package_name}")
    except Exception as e:
        unreal.log_error(f"[AssetChecker] 定位资产失败: {e}")


# ============================================================
# 引用检查逻辑
# ============================================================

def is_correct_reference(ref_path: str) -> bool:
    return bool(re.search(CORRECT_REF_PATTERN, ref_path, re.IGNORECASE))


def get_all_referencers(asset_registry: unreal.AssetRegistry, package_name: str) -> list[str]:
    try:
        dep_options = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True,
            include_hard_package_references=True,
            include_searchable_names=False,
            include_soft_management_references=False,
            include_hard_management_references=False,
        )
        refs = asset_registry.get_referencers(package_name, dep_options)
        return [str(r) for r in refs]
    except Exception as e:
        unreal.log_error(f"[AssetChecker] get_referencers 失败 '{package_name}': {e}")
        return []


def collect_results() -> list[dict] | None:
    selected = unreal.EditorUtilityLibrary.get_selected_asset_data()
    if not selected:
        return None

    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    results = []

    for ad in selected:
        pkg  = str(ad.package_name)
        name = str(ad.asset_name)

        all_refs     = get_all_referencers(ar, pkg)
        correct_refs = [r for r in all_refs if is_correct_reference(r)]

        results.append({
            "asset_name":    name,
            "package_path":  pkg,
            "correct":       len(correct_refs) > 0,
            "correct_refs":  correct_refs,
            "all_ref_count": len(all_refs),
        })

    return results


# ============================================================
# 表格 UI
# ============================================================

def show_result_window(results: list[dict]) -> None:
    global _active_root

    # 如已有窗口则先关闭旧窗口
    if _active_root is not None:
        try:
            _active_root.quit()
            _active_root.destroy()
        except Exception:
            pass
        _active_root = None

    # 建立 package_path 索引，供右键菜单查询
    path_index: dict[str, str] = {r["asset_name"]: r["package_path"] for r in results}

    def _run() -> None:
        global _active_root

        root = tk.Tk()
        _active_root = root
        root.title("资产引用检查结果")
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root.configure(bg="#252526")
        root.resizable(True, True)

        # ── 顶部统计栏 ──────────────────────────────────────
        total     = len(results)
        ok_count  = sum(1 for r in results if r["correct"])
        bad_count = total - ok_count

        header = tk.Frame(root, bg="#1e1e1e", pady=7)
        header.pack(fill=tk.X)

        tk.Label(header, text=f"共 {total} 个资产",
                 bg="#1e1e1e", fg="#9cdcfe",
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=(14, 24))
        tk.Label(header, text=f"✔  正确引用   {ok_count}",
                 bg="#1e1e1e", fg="#4ec94e",
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 24))
        tk.Label(header, text=f"✘  未正确引用  {bad_count}",
                 bg="#1e1e1e", fg="#f0c040",
                 font=("Consolas", 10)).pack(side=tk.LEFT)

        # ── 表格区域 ────────────────────────────────────────
        tree_frame = tk.Frame(root, bg="#252526")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 0))

        vsb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL,   bg="#3c3c3c")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, bg="#3c3c3c")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Chk.Treeview",
            background="#1e1e1e",
            foreground="#d4d4d4",
            fieldbackground="#1e1e1e",
            rowheight=26,
            font=("Consolas", 10),
        )
        style.configure(
            "Chk.Treeview.Heading",
            background="#2d2d2d",
            foreground="#bbbbbb",
            font=("Consolas", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Chk.Treeview",
            background=[("selected", "#094771")],
            foreground=[("selected", "#ffffff")],
        )

        cols = ("status", "asset", "refs")
        tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            style="Chk.Treeview",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )

        tree.heading("status", text="状态")
        tree.heading("asset",  text="资产名称")
        tree.heading("refs",   text="引用路径")

        tree.column("status", width=130, minwidth=100, anchor=tk.CENTER, stretch=False)
        tree.column("asset",  width=220, minwidth=140, anchor=tk.W,      stretch=False)
        tree.column("refs",   width=490, minwidth=200, anchor=tk.W,      stretch=True)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        tree.tag_configure("ok",  foreground="#4ec94e")
        tree.tag_configure("bad", foreground="#f0c040")

        # 先插入异常条目（置顶），再插入正确条目
        for r in sorted(results, key=lambda x: x["correct"]):
            if r["correct"]:
                refs_str = "  |  ".join(r["correct_refs"])
                tree.insert("", tk.END,
                            iid=r["package_path"],
                            values=("✔  正确引用", r["asset_name"], refs_str),
                            tags=("ok",))
            else:
                if r["all_ref_count"]:
                    refs_str = f"共 {r['all_ref_count']} 个引用者，均不符合规则"
                else:
                    refs_str = "无任何引用者"
                tree.insert("", tk.END,
                            iid=r["package_path"],
                            values=("✘  未正确引用", r["asset_name"], refs_str),
                            tags=("bad",))

        # ── 右键菜单 ────────────────────────────────────────
        ctx_menu = tk.Menu(
            root, tearoff=0,
            bg="#2d2d2d", fg="#d4d4d4",
            activebackground="#094771", activeforeground="#ffffff",
            font=("Consolas", 10),
        )

        def on_locate() -> None:
            iid = tree.focus()
            if iid:
                # iid 即 package_path，投递到 Unreal 主线程执行
                _main_thread_queue.put(lambda p=iid: _sync_browser(p))

        ctx_menu.add_command(label="在内容浏览器中选中此资产", command=on_locate)

        def on_right_click(event) -> None:
            row = tree.identify_row(event.y)
            if row:
                tree.focus(row)
                tree.selection_set(row)
                ctx_menu.post(event.x_root, event.y_root)

        tree.bind("<Button-3>", on_right_click)

        # ── 底部关闭按钮 ────────────────────────────────────
        def on_close() -> None:
            global _active_root
            _active_root = None
            # 通过队列在主线程注销 Tick，避免跨线程调用 Unreal API
            _main_thread_queue.put(_unregister_tick)
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)

        btn_bar = tk.Frame(root, bg="#252526")
        btn_bar.pack(fill=tk.X, pady=6)

        tk.Button(
            btn_bar, text="关闭", command=on_close,
            bg="#3c3c3c", fg="#d4d4d4",
            activebackground="#505050", activeforeground="#ffffff",
            relief=tk.FLAT, font=("Consolas", 10),
            padx=28, pady=4, cursor="hand2",
        ).pack()

        root.mainloop()

    _register_tick()
    threading.Thread(target=_run, daemon=True).start()


# ============================================================
# 入口
# ============================================================

def main() -> None:
    results = collect_results()
    if not results:
        unreal.log_warning("[AssetChecker] 未选择任何资产。")
        return

    unreal.log("[AssetChecker] ========== 检查结果 ==========")
    for r in results:
        if r["correct"]:
            unreal.log(f"[AssetChecker] [OK]  {r['asset_name']}  ->  {', '.join(r['correct_refs'])}")
        else:
            unreal.log_warning(f"[AssetChecker] [!!]  {r['asset_name']}  ->  未正确引用")
    unreal.log("[AssetChecker] ================================")

    show_result_window(results)


main()
