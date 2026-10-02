# 本轮工具池整理运行资料

本轮依据 `plans/2026-09-staging-pool-unattended.md`。候选不等于真实 Maya 验收；正式库只在用户验收后晋级。

- `manifest.json`：109 项动态任务与状态，恢复时先读此文件，再看 Git diff。
- `INDEX.md`：生成的进度总表；用 scan_pool.py 更新，不手改。
- `MAYA_ACCEPTANCE.md`：全部 109 项的逐项真实宿主验收总表，链接候选说明、验收步骤及晋级清单。
- `FINAL_AUDIT.json`：最终对账结果，涵盖候选指纹、目标文件冲突、晋级预检和原提交有效性。
- `final_audit.py`：读取当前 manifest 并复核完整交付；只有全部候选准备完成时生成验收总表并写入 completed 状态。
- `scan_pool.py`：只读扫描源码、不 import 原工具；`--repair-paths` 仅修正单元内唯一同名文件路径，仍需源码复核其调用方式。
- `promote_candidate.py`：晋级预检与人工验收后执行；默认不写正式文件，目标冲突、陈旧候选指纹、缺少验收记录时拒绝晋级。
- `run_mayapy_check.py`：在独立进程、临时 Maya 偏好目录和限时条件下跑 standalone 测试，不接管用户 GUI 场景。
- `tests/test_promotion.py`：只在临时迷你仓库测试晋级安全行为。

运行时使用本机已发现的 Python 3；目标测试运行时与 GUI 验收版本分别记录，不声称所有版本兼容。

本轮保持单聊天写入。不启动其他聊天或 worktree。初始阶段创建了暂停的 30 分钟 heartbeat（ID `automation`）；当时实际定时触发/续跑尚待核验，后续操作与结果以运行日志为准。后台额度读取失败不按 0% 或 100%推断；保留日志并重试。遵循用户后续明确指令，不启动用卡守护、不消费重置卡、不购买额度。

每项完成后更新 manifest、生成总表、提交对应文件并读取额度。5 小时剩余低于 6% 时才启用 heartbeat 并结束回合；续跑要求剩余高于 95%、周额度可用且没有其他运行回合。周期内读数无变化时保持安静。整个目标完成后停止自动化。

本轮不主动运行 Obsidian 同步，不编辑 knowledge/_generated/，不修改长期规范。转正后如何同步按当时用户指令和项目规范处理。

2026-10-02 最终交付：实时对账为 109 个物理单元、109 条目录记录、109 个存在的入口，109 个完整候选；4 项 prepared_verified_offline、105 项 prepared_unverified，全部仍待用户实测。最终对账通过，heartbeat 已停用（PAUSED），执行状态 completed。Anim Filters 的 SciPy 依赖缺失检查失败如实保留，见验收总表。正式库、长期规范和生成知识库没有本分支改动。
