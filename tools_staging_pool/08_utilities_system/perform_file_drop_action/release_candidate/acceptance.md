# 文件拖拽 Maya真实直验 not_run

1. 备份scene下show_ui或显式enable_drop，拖单本机ma/mb到当前modelPanel，Import/Open/Reference/Cancel完整，无inline执行未知源scriptNodes；其他URL/多文件/非ma/mb不吞，未改内置performFileDropAction/安装路径/global mode。
2. namespace空/重名/非法拒绝不改scene；Import/Reference/Open均不可保证Undo（隔离2025已证实import无Undo队列），仅备份scene使用。Open modified Save/Discard/Cancel，当前无名保存cancel保留scene，现存输出先backup。
3. 多次enable/drop/disable/close后不叠自有filter、不移foreign hook，新modelPanel重新enable。独立MEL mtb_performFileDropAction编译与路径含引号/Unicode核验。
4. accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
