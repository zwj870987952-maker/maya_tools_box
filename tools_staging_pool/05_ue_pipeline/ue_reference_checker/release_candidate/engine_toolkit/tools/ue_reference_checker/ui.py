"""Original complete Tk table, pumped without worker threads by UE Slate tick."""
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
    # Package paths are row IDs; duplicate display names never overwrite identity.

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
        bad_count = sum(r["correct"] is False for r in results)
        unknown_count = sum(r["correct"] is None for r in results)

        header = tk.Frame(root, bg="#1e1e1e", pady=7)
        header.pack(fill=tk.X)

        tk.Label(header, text=f"共 {total} 个资产",
                 bg="#1e1e1e", fg="#9cdcfe",
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=(14, 24))
        tk.Label(header, text=f"✔  正确引用   {ok_count}",
                 bg="#1e1e1e", fg="#4ec94e",
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 24))
        tk.Label(header, text=f"✘  未正确引用  {bad_count}    查询未知 {unknown_count}",
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
        for r in sorted(results, key=lambda x: x["correct"] is True):
            if r["correct"] is None:
                tree.insert("", tk.END, iid=r["package_path"],
                    values=("? 查询失败", r["asset_name"], r["error"]), tags=("bad",))
            elif r["correct"]:
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
            # Slate tick unregisters once root is gone, on its own main thread.
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

        return root

    _register_tick()
    try:
        _run()
    except Exception:
        close_ui()
        raise
