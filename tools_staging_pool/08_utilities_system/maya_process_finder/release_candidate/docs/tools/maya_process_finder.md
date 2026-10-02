# Maya进程查找器 Windows独立候选

两个原版本SHA原样归档。完整光标HWND/PID/窗口标题/可执行路径/进程状态/创建时间、Ctrl点击poll与低层hook两模式、Task Manager启动、显式结束与force、console展示/持续监听/退出。按真实Windows程序准备engine_toolkit原生入口，不做无意义Maya Base/UI注册；python -m engine_toolkit.tools.maya_process_finder启动，psutil依赖，Windows ctypes均执行时加载，无import提权/exit/钩子/线程。

原hook版本名为打开任务管理器的函数实为taskkill /f /pid /t，并对任意窗口自动结束。候选把默认click改只读；terminate明确独立action/confirm_terminate=True/查询create_time及exact maya.exe、执行前再次核对PID寿命，不结束child tree、不调用shell、无runas自动提权。Windows terminate也是结束进程，不承诺优雅保存；force使用kill，未保存数据丢失，不可Undo，用户明确选择临时空Maya才直验。Taskmgr普通shell=False启动，不谎称Windows /select flag受支持；按PID手动定位Details。未在整理时启动任务管理器/安装hook/结束任何真实进程。

64位HWND/HHOOK/LRESULT正确restype、WINFUNCTYPE calling convention、MSLL dwExtraInfo指针大小；hook callback只取窗口和排队，过程详情在drain取，始终CallNextHookEx；自有monitor256队列不阻塞click、rising edge防连按、cancel event/PostThreadMessage WM_QUIT、自有Unhook/join，timeout不冒充停止，不杀foreign hook。API validate/execute/run(dict success/data/errors)/Schema，默认dry_run=True不挂钩不launch不kill；未知参数/strict bool/正DWORD PID/非有限ctime拒绝。进程退出或无权限反馈failure，不自动重试管理员。mock完整PID reuse/confirm/dry/noWinAPI/队列测试与独立future layout；真实Windows cursor/globalhook/管理员权限差异和Task Manager交互not_run。
