# 工具架管理器真实Maya验收 not_run

1. 仅复制好的临时prefs root，在真实Maya打开完整版本选择、中英文双列、默认shelf toggle/refresh、多root同名完整路径区分；不扫C/D全盘、不自动loadMEL。
2. 仅信任临时shelf，Load提示会执行MEL，取消无执行；同名现有shelf UI拒绝覆盖，旧代码/外部icon路径实际兼容2018-2026分别核验。
3. 迁移=复制源保留，整批同名/坏最后拒绝无首项写；已有API overwrite明确backup，PNG伙伴/hash一致，IO失败可能留有前项已完成的目标和备份；失败结果不提供完整已完成列表，按目标目录和.mtb_backup_*材料逐项核对恢复。文件写不可scene Undo。
4. Quarantine确认后mel/png到source root独立目录，receipt包含原路径/SHA，手动恢复准确，不删foreign shelf UI；manager close/reopen只自己的MQt窗口，不删shelf资源。
5. accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
