# 整套 Maya 验收（not_run）

1. 已保存的备份场景和独立临时目录，启动四入口面板，逐个打开完整 SkinInfo1.92/1.7/SuperConnect/Timal，核查 Browse、模式、列表、轴、MO、Go/状态字段。Script Editor 不得有 Fatal/Error；取消对话框正常返回。
2. 两关节简单 mesh，对照 GetInfo/Weighted，XML/JSON 单个及批量导出，重复输出必须拒绝覆盖；dry_run 目录空、节点/选择/Undo 不变。TXT 只含安全关节名，插入 delete/system 等命令必须拒绝且不执行。
3. 修改真实权重，分别导入 XML/JSON，逐点对照原值，一次 Undo 恢复修改前权重。新目标 Timal convention XML、post normalize、已有 skin 选项分别核查；错拓扑拒绝，旧 map 勾选 acknowledgement 后只对确认同编号拓扑导入。
4. 备份生产 skin 验证 transfer/copy、多目标、名称/姿态差异、prune 的预期影响和 Undo；删除目标历史只在临时复制场景勾选授权后测试，源历史保留。liw 锁定和属性连接/引用/多skin保护有效。
5. SuperConnect source/destination prefix+namespace，测试全部 nine direct轴、parent/point/orient/point-orient 和 MO，实际移动 source 核对 destination、单步 Undo 恢复。已有驱动默认拒绝；勾选 direct 替换只影响已预览的目标。重复 stripped 名、自身/层级循环/空匹配拒绝。
6. 不同 Maya 版本、生产 rig、全部原 GUI按钮/批处理和取消路径复验。满意后写真实 passed/tool_id/candidate_sha256/maya_version/accepted_by/date JSON，再运行 plans/staging_run/promote_candidate.py --candidate 本目录 --apply --acceptance 验收记录；当前仍只预览。
