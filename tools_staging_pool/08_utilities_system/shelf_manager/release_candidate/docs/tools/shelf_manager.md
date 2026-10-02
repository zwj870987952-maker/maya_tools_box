# 跨版本工具架管理器完整候选

原源码SHA精确归档，完整cmds窗口/中英文双列表/2018-2026自动版本/默认工具架toggle/refresh/选择/加载/迁移/删除交互保留。Base/API/Schema/无副作用预检/未来注册面板预制，默认inspect不native/MEL/UI。扫描明确1-32现有non-symlink Maya prefs roots，仅root/2018..2026/{zh_CN/}prefs/shelves/文件名shelf_*.mel，max10000/16MiB；GUI可建议HOME/MAYA_APP_DIR标准已存目录，移除原C/D盘recursive全盘fallback。多root同版本同名按完整路径显示/选中，不再被name_version映射覆盖；默认shelf数据全部收集后toggle显示而不是初扫永久遗漏。

迁移实际是复制，源保留；先整批预检碰撞/坏末项/范围/同src-target/PNG伙伴，再hash核对与exclusive新输出，overwrite=True明确先exact备份现有目标、临时copy hash核验并atomic替换；目标并发改动拒绝覆盖。相邻同名PNG可include_icons；不会查找/迁移任意全局图片依赖，跨版本MEL实际兼容和外部图标路径待直验。运行中IO失败可能有前项已完成，不能声称事务all-or-none，成功返回receipt/data列出目标/备份；运行中异常的失败结果不含完整已完成列表，应按目标目录和.mtb_backup_*材料逐项核对恢复；普通碰撞在写任何项前拒绝。

原删除硬盘文件和按同名annotation删任意shelf UI，改明确Quarantine把源mel/同名png移入对应root独立.mtb_shelf_trash_UUID，receipt记录原路径/SHA/隔离文件，可手动精确恢复，不rmtree/unlink原文件。明确roots/选择/确认后才移，不清foreign已载shelf UI、共用图标或注册startup；文件复制/覆盖/移动和Maya shelf UI不可scene Undo。若恢复时原路径已存在，先比较SHA/备份，不盲覆盖。

加载MEL可执行用户脚本，API confirm_execute_mel/GUI明确Load按钮确认，不在scan/dry/migrate/delete执行。源路径MEL json quoting，已有目标同名shelf UI预检保留；实际MEL可任意改UI/scene/files，不声称静态检查证明其安全，候选只对信任临时shelf直验。own manager窗口MQt pointer跟踪/foreign重名拒绝删除，关闭只manager不删用户loaded shelf。完整原UI的本机临时mock构造/双语言/完整路径选择和后台文件扫描/冲突/backup/坏末项/可恢复隔离/future注册离线检查；真实Maya shelf加载/UI版本和外部图标/生产MELnot_run。
