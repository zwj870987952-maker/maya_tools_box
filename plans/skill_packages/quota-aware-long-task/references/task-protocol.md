# 运行协议与恢复状态

路径、阈值、线程、停止条件和卡策略从本次用户答案取得；不得直接执行旧 Maya 整理任务。

## 文件与状态

- PLAN.md：目标、范围、停止条件、额度策略、卡授权、验收标准和自动化限制。
- state.json：事实及已确认策略；临时文件 + 同目录 atomic replace 更新，单写入者，不覆盖其他执行者的更新。
- HANDOFF.md：无需聊天记忆即可继续的交接；参考 assets/handoff-template.md。
- events.jsonl：实际事件/读数/状态切换/验证/用卡结果，按事件 ID 去重通知。
- 成果/证据索引：只引用实际存在的文件和 Git SHA，不保存 token、Cookie、密钥或完整账户隐私。

状态：preparing、running、checkpointing、waiting_for_quota、paused_by_user、needs_input、completed、stopped。额度等待不等于任务完成。

以下为结构示例，实际创建时填写本次路径与线程、已确认策略；不能照例值启动任务。

```json
{
  "schema_version": 1,
  "task_id": "user-chosen-task-id",
  "state": "preparing",
  "completion_verified": false,
  "work_items": [{"id": "first-unit", "status": "pending", "evidence": []}],
  "quota_policy": {
    "bucket_id": "codex",
    "pause_five_hour_remaining_pct": 6,
    "resume_five_hour_remaining_pct": 95,
    "weekly_reserve_pct": 1,
    "snapshot_max_age_seconds": 300,
    "heartbeat_interval_minutes": 30,
    "in_unit_check_minutes": 10
  },
  "stop_policy": {
    "operator": "any",
    "deadline": null,
    "max_rounds": null,
    "five_hour_remaining_floor_pct": null,
    "weekly_remaining_floor_pct": null,
    "other_conditions": []
  },
  "rounds_started": 0,
  "writer": null,
  "next_unit_estimated_cost_pct": null,
  "reset_policy": {
    "mode": "never",
    "trigger": "before_expiry_or_exhaustion",
    "expiry_lead_hours": null,
    "max_cards": 0,
    "allowed_card_ids": [],
    "excluded_card_ids": [],
    "actual_capability": "not_verified",
    "redemption_attempts": []
  },
  "automation": {
    "id": null,
    "thread_id": null,
    "status": "PAUSED",
    "binding_verified": false,
    "transitions_verified": false,
    "scheduled_resume_verified": false,
    "notifications_verified": false
  },
  "checkpoint": {
    "last_completed_unit": null,
    "current_unit": null,
    "next_step": null,
    "files": [],
    "source_commit": null,
    "uncommitted_diff": null,
    "active_processes": []
  }
}
```

writer 非空时记录 owner_thread、host、round_id、started_at、last_seen、活跃进程线索。新触发核验执行者；超时仅是线索，不能直接清他人锁。无人活跃时核对半成品/进程并记录依据后才能释放陈旧标记。存在竞争时用独占文件创建或正式协调能力，不能以「先读后写 JSON」冒充互斥。

最终步骤设置 completion_verified，前提是所有工作项及证据符合本次完成定义。文件生成、测试通过、真人验收和发布分开记录；失败可否延期算完成由本次用户定义，不一律套 prepared_unverified。

## 额度决策脚本

`scripts/quota_decision.py` 只读建议器支持五小时/周额度、截止时间、最大回合数、永久额度下限、预计下一单元消耗、持有者和终止状态。其他业务停止条件由执行者检查并记录。它不检测业务完成、抢锁、发卡提醒或修改自动化。

把成功读取的正式工具 JSON 包在以下快照中；先解析 MCP text 包装，不把错误文本当 data。不存在窗口/许可保留 null，按 retry_usage 处理，不能填零或假定通过。

```json
{
  "observed_at": "2026-10-04T12:00:00+08:00",
  "data": {
    "ordinaryUsageAllowed": true,
    "rateLimitsByLimitId": {
      "codex": {
        "primary": {"usedPercent": 94, "windowDurationMins": 300},
        "secondary": {"usedPercent": 70, "windowDurationMins": 10080}
      }
    }
  }
}
```

脚本检查 300/10080 分钟窗口；不同账户窗口不同时报告无法判断，先按实际契约适配计划。`--now` 只供离线复演，实际默认带时区当前时间。

```text
python scripts/quota_decision.py --state /absolute/run/state.json --usage /absolute/run/usage.json
python scripts/quota_decision.py --state /absolute/run/state.json --usage /absolute/run/usage.json --owner-round CURRENT_ROUND_ID
```

当前写入者传实际 owner-round，heartbeat 不传；不能从 state 复制他人 round_id 假冒持有者。action：continue=当前回合推进；start_round=已确认方案的首轮可以启动（不要求等待一次完整刷新）；prepare_resume=先暂停 heartbeat/核验锁再开工；save_and_wait=保存后启用 heartbeat；wait=安静等待；retry_usage=未知/过期读数，运行中先保存再重读；retry_state=状态异常，核对半成品与进程；busy=不启动重复回合，pending_stop_reason 告知现持有者应收尾；finish/stop=最终交接并暂停自动化；remain_stopped/remain_paused=不恢复。suggested_heartbeat 只是目标，不代表实际状态。首条命令为唤醒检查，第二条为当前回合的检查。

本轮剩余**低于** pause/周预留线才等额度，恢复须**高于** resume/周预留线；预计下一单元使剩余达到或低于预留时提前交接。永久下限在剩余**达到或低于**下限时终止整个任务。最大轮次限制新回合，不强行终止最后允许回合。截止优先停止新业务，仍保存交接。

脚本只实现 any（任一成立）组合；用户要求 all（同时满足）时，由执行者按该任务具体语义实现组合判定，不能将本脚本的 any 建议套用过去。脚本遇到 all 会明确拒绝，不静默提前终止。

## heartbeat 提示词生成

创建前替换下文所有说明占位为具体目标、绝对路径、阈值、截止时区、卡策略和自动化 ID，保存最终 prompt。不能直接创建泛泛的「继续工作」。

> 继续本聊天已授权的【目标】。先读【绝对 PLAN/state/HANDOFF/日志路径】和实际产物/Git diff，从检查点恢复，不重复已完成外部动作。先查【停止条件】、人工暂停和其他活跃回合；任务结束时暂停本 heartbeat、保存最终交接并通知。每次触发读取实时五小时/周额度和【用卡/临期提醒策略】，未知不猜测，临期事件不被等待分支跳过。只有五小时剩余高于【恢复阈值】、周剩余高于【预留线】且无其他回合时暂停自身并读回核验，登记单写入者，继续下一安全步骤。工作时 heartbeat 保持 PAUSED，步骤前后和长步骤【检查间隔】重读停止条件/额度；低于【暂停阈值】、预计步骤会穿过预留或读数未知时，先保存交接/实际证据/未提交改动，再启用 heartbeat并核验，释放持有者，结束回合。失败/未验收如实记录，完成标准为【明确证据】，允许范围为【范围/权限边界】。不购买额度、不另建聊天或执行未授权外部动作。无变化或不能恢复时安静等待；仅重要变化、完成、失败、临期卡需操作或必需答复时通知，并去重同一事件。

用户选用卡时，写入数量/允许范围/临期提前量/确认模式及「遵守当前兑换工具的逐次确认与资格限制；不支持则提醒人工，不绕过」。不能同时写「不使用」与「自动使用」。

用 automation_update 创建/更新 heartbeat，不手写 automation.toml，不换 cron 新聊天；保存真实返回的 ID。更新保留其他字段和通知设置，同任务不重复创建。状态确认失败记录未落实。

## 用卡能力与通知限制

模式：never、confirm_each、auto_if_supported。只有正式工具允许提前授权自动兑换时才能落实 auto；否则实际为 confirm_each，在启用业务前告知用户差异。

2026-10-04 本环境 consume_usage_reset 要求每次明确确认、至少一窗口剩余不高于 10%，且不能指定 creditId。此为当前能力记录而非永久规则，使用时重读工具契约。只允许指定卡而工具不能选卡时，不兑换。官方 App Server 的指定卡接口不是绕过已有确认/资格要求的途径，不自行另建兑换守护。

卡事件记录数量、允许范围内候选 ID、expiresAt（未知不推算）、已提醒事件及幂等 key/outcome。成功后读回额度与卡，延迟刷新时不再兑另一张。任务停止后不为用卡继续消耗业务额度。临期但不满足资格时提醒 Settings → Usage，注明实际到期时区、需用户操作及不确定性。

本地循环依赖机器/App/登录/网络；定时消息、审批、恢复和手机通知分别验证。硬限额/审批不可用或设备离线时不保证唤醒推送或精确兑换。购买额度、发邮件、创建系统守护需另行授权。

## 本次经验的边界

- 6%/95%/30 分钟是可调整起点；大单元未完成也可交接，部分文件和失败证据准确保留。
- Git 审批也受额度影响，先落盘，下一轮补提交，不预写 SHA。
- 重复唤醒通过持有者核验、单写入者和事件去重处理，无变化安静等待。
- mayapy/离屏 Qt/mock 不等于 GUI 通过；其他任务同样区分测试、验收和发布。
- 交接保留已有用户改动、失败报告及下一具体命令，不能只写「继续下一个」。
- 动态新增可能导致永不结束，启动时约定截止或封存范围。

## 官方资料（实际使用重读工具）

- [Scheduled tasks](https://learn.chatgpt.com/docs/automations)：当前定时能力；本机 heartbeat 类型/绑定以 automation_update 为准。
- [Codex App Server](https://learn.chatgpt.com/docs/app-server)：额度桶、usedPercent、卡详情与幂等；兑换后重新读取。
- [Banked resets](https://help.openai.com/en/articles/20001498-how-banked-codex-resets-work)：重置影响五小时/周窗口并改变周刷新日期，资格/到期以账户为准。
