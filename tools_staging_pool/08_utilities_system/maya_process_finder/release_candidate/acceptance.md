# Windows本机直验 not_run

1. python -m engine_toolkit.tools.maya_process_finder，poll/hook分别Ctrl点击临时空Maya窗口，标题/PID/path对应任务管理器；点击普通窗口只查询，绝不自动结束/提权，右/左普通点击不吞。
2. 持续hold只单事件、256队列满正常、Ctrl+C退出线程/hook并保留foreign hooks；启动失败/AccessDenied/进程退出如实报错，不留后台hook。
3. Task Manager仅明确open action，Details手动定位，未宣称/select受支持。结束仅用户主动在无未保存内容的临时Maya用查询PID/create_time/confirm_terminate，dry不会kill；坏PID/寿命变/非Maya拒绝，不杀child tree，不改实际工作Maya。
4. Windows64位hook ABI和不同权限窗口实测，填runtime_version/accepted_by/date/passed=true/candidate_sha256才promotion。
