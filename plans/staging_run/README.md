# 本轮工具池整理运行资料

本轮依据 `plans/2026-09-staging-pool-unattended.md`。候选不等于真实 Maya 验收；正式库只在用户验收后晋级。

- `manifest.json`：109 项动态任务与状态，恢复时先读此文件，再看 Git diff。
- `INDEX.md`：生成的进度总表；用 scan_pool.py 更新，不手改。
- `scan_pool.py`：只读扫描源码、不 import 原工具；`--repair-paths` 仅修正单元内唯一同名文件路径，仍需源码复核其调用方式。
- `promote_candidate.py`：晋级预检与人工验收后执行；默认不写正式文件，目标冲突、陈旧候选指纹、缺少验收记录时拒绝晋级。
- `run_mayapy_check.py`：在独立进程、临时 Maya 偏好目录和限时条件下跑 standalone 测试，不接管用户 GUI 场景。
- `tests/test_promotion.py`：只在临时迷你仓库测试晋级安全行为。

运行时使用本机已发现的 Python 3；目标测试运行时与 GUI 验收版本分别记录，不声称所有版本兼容。

本轮保持单聊天写入。不启动其他聊天或 worktree。已创建初始暂停的 30 分钟 heartbeat（返回 ID `automation`），尚未完成实际定时触发/续跑核验。后台额度读取失败不按 0% 或 100%推断；保留日志并重试。没有启动重置卡消费守护，内置用卡工具要求每次用户明确确认。

每项完成后更新 manifest、生成总表、提交对应文件并读取额度。5 小时剩余低于 6% 时才启用 heartbeat 并结束回合；续跑要求剩余高于 95%、周额度可用且没有其他运行回合。周期内读数无变化时保持安静。整个目标完成后停止自动化。

本轮不主动运行 Obsidian 同步，不编辑 knowledge/_generated/，不修改长期规范。转正后如何同步按当时用户指令和项目规范处理。
