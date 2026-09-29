# 临时计划：Codex 无人值守整理 Maya 待整理工具池

> 执行地点：另一台机器的本地 Codex 项目聊天。本文只服务本次集中整理，不修改 `AGENTS.md`、`DEVELOPMENT_SPEC.md` 或项目长期做法；本轮不运行 Obsidian 同步，也不编辑 `knowledge/_generated/`。启动时重新读取账号、目录和工具版本，不能把 2026-09-29 的快照当实时数据。

## 1. 本轮要完成什么

**范围在启动时确定。** 启动时扫描 `tools_staging_pool/` 下所有分类和工具单元，和 `staging_catalog.json` 双向对账；新增、缺项、入口不一致都要列出并处理。启动后又新增的单元，在后续续跑时自动纳入。2026-09-29 的参考快照是 57 个物理单元、57 条清单记录、57 个可找到的入口；README 的“54 项”已经过时，不能作为任务上限。

**交付是最终版候选包。** 每个工具在待整理池内准备好将来正式目录所需的完整代码、资源、参数 Schema、`validate(**kwargs)` / `execute(**kwargs)`、无副作用 `dry_run`、`ToolResult`、撤销和外部文件影响说明、正式知识文档、目标测试文件及面板/注册所需信息。可适用的 Maya 工具遵循 `DEVELOPMENT_SPEC.md` 的真实契约；独立 Windows 程序、UE 工具和第三方套件按其真实运行方式准备适配，不作无意义的 `BaseMayaTool` 继承。候选包不能依赖仍留在待整理池的临时路径或缺失素材。

当前 `maya_toolkit/tools/__init__.py` 使用 `ALL_TOOL_CLASSES` 注册，面板从注册表列工具，所以**只搬一个代码目录还不足以挂载面板**。为达到“用户验收后不再开发”的要求，每项须同时准备目标路径清单和注册/面板变更；可以制作经过静态检查的单次晋级脚本，验收后执行它完成文件搬迁、文档与测试安放、注册和面板接入。正式库与注册表在 Maya 验收前不发生变动。该晋级动作不应再需要重构业务代码。

**本轮跳过人工和环境验收阻塞。** 对每项尽力进行静态解析、隔离单测、mock 或可用的 `mayapy` 检查；遇到真实 Maya/UE 运行不可用、Python 版本不兼容、测试失败或验证卡住时，先尝试修复确定的代码问题，再如实记下失败、缺失条件和人工复验步骤，转到下一项。不得以“未实测”阻断整批整理；也不得把失败写成通过。`prepared_unverified` 计入本轮已处理，`prepared_verified_offline` 表示仅非 Maya 检查通过；两者都仍需用户最终逐项验收。用户实测通过后，才按长期项目规范转正。

## 2. 工作机器的一次性预检

1. 用同一个 Plus 账号登录该机器的桌面版 Codex、Codex CLI 和手机 ChatGPT Remote。更新本仓库，确认分支、远端和工作树；保留已有用户改动。选择一个固定的本地工作目录，只允许一个聊天写入。
2. 保持机器开机、桌面版运行、网络可用，并启用手机上该聊天的“需要回复/任务完成”通知。做一次短时间的真实测试：让聊天提出无副作用问题，确认手机收到推送、打开 Remote、能答复。无需预设卡片闹钟。
3. 工作目录应可写；用最小权限预先验证 Git、本地运行时，并执行 `node plans/codex_app_server_probe.mjs` 验证 Codex App Server **只读**接口。先在 CLI 账号界面核对与桌面版是同一账号；探针应显示 ChatGPT 认证、Plus、周窗口和卡片详情。若提示 `Account auth: none`，先在该机器的 Codex CLI 登录同一账号再重试。后台定时任务可能按 `approval_policy = "never"` 运行；任何必须授权的命令在无人值守阶段会失败，因此预检时解决具体权限，不应笼统打开全盘访问。
4. 在同一聊天创建清晰的 `/goal` 和每 5 分钟一次的 **heartbeat** 定时续跑。心跳只在上一轮已结束时开启下一项；不同时写同一批文件。先看第一轮 Scheduled 日志，再让任务持续。与项目文件相关的本地定时运行要求电脑保持开机、桌面版运行。

## 3. 工具整理的可恢复循环

在本次临时目录 `plans/staging_run/` 建立 `manifest.json`、总索引和日志。清单由实时目录生成，每轮重新比较，记录每项的源路径、入口、资源、外部依赖/许可、目标正式路径、状态、改动摘要、非 Maya 验证结果、跳过原因、待用户 Maya 测试步骤、晋级动作和提交号。状态可为 `pending`、`working`、`prepared_verified_offline`、`prepared_unverified`。重启后从清单及 Git diff 恢复，不凭聊天记忆猜进度。

每项工作按下列流程执行，并在有用量时立即进入下一项：

1. 阅读原脚本、资源、相关 README、现有 `maya_toolkit.core` 和正式工具，找重复能力和行为边界。第三方套件保留来源与许可，避免大范围重写；复杂套件可分多轮，但最终作为一个单元交付。
2. 在该工具单元内制作 `release_candidate/`，其内部镜像将来的目标目录结构；备齐运行代码、素材、正式文档草案、测试和晋级清单。保持原始入口可追溯。设计的复用点能安全下沉到 `core` 时才下沉；任何改变行为的优化都在逐项说明中列明。
3. 分离 UI 与业务逻辑，补输入检查、无副作用预检、撤销分组及文件覆盖保护。记录参数、数据输出、场景和文件影响、与其他工具的可组合关系、Maya 版本待测项。批处理、导出、清理、杀毒与引用替换的人工验收步骤只使用备份场景或临时目录。
4. 做与代码改动相关的最小自动检查。检查失败先修复明确缺陷；仍因 Maya/UE、旧 Python、缺少资产或未知运行环境而卡住时记录具体错误和复验方法，标为 `prepared_unverified`，立即继续下一项。不得执行可能直接修改真实场景或真实外部文件的原始入口。所有离线检查均不得冒充真实 Maya 实测。
5. 检查 candidate 可在**不再重构代码**的条件下晋级，更新 manifest 和总索引，按工具小批提交。不要改长期规范，不运行 `scripts/sync_obsidian_knowledge.py`，不手改 `knowledge/_generated/`。

当动态范围内每项都处于 `prepared_verified_offline` 或 `prepared_unverified`，并且各有最终版候选包、目标路径/晋级清单、逐项 Maya 验收说明，才停止自动续跑并通知用户集中验收。最终实测可能暴露新缺陷；届时修复对应候选再晋级。

## 4. 5 小时与周额度：实时决策和计算

2026-09-29 的账号快照是 Plus，5 小时已用 19%、周已用 25%；当时还有 3 张 Full reset 卡，其中本轮指定的两张分别在 **10 月 4 日 09:20:18**、**10 月 5 日 07:11:20**（北京时间）到期，第三张在 10 月 23 日到期。所有值启动时重读。`usedPercent` 是已用比例，`resetsAt` 是 Unix 秒；重置卡会同时刷新 5 小时和周窗口，并改变周重置时间。每轮开工、每项收尾、遇到限流及使用卡后都重新读取，而非从某个时间连续加 5 小时。

用户问“满额使用几次 5 小时会耗尽周额度”：**目前无法准确给出固定次数**。官方不公布可用于相除的该账号周/5 小时绝对额度，现有接口只返回两个 `usedPercent`；模型、上下文、工具和任务复杂度使实际消耗变化。启动后记录一个从 5 小时窗口接近 0% 到 100% 的完整工作窗口中，周已用百分比增加的百分点 `ΔW`。若开始时周已用 `W`，相似负载下估计还需 `ceil((100 - W) / ΔW)` 个满额窗口。例如 `W=25`、完整一轮使周用量增加 20 个百分点，则约还需 **4 轮**；这里的 20 只是算式示例，不是该账号实测值。每完成一轮更新 `ΔW` 和估计，周额度可能在最后一轮尚未耗尽 5 小时时先到上限。

工作规则：有额度就做真正的整理；仅 5 小时额度耗尽时，保存进度，按实时 `primary.resetsAt` 等待下一轮，heartbeat 自动继续。**只要周额度实际耗尽，立即使用最早到期的本轮卡，不等 5 小时窗口结束，也不等预设日期。** 第一张成功后重读额度并继续，周额度再次耗尽就用第二张。此前用户也明确要求优先避免卡片过期：如果直到到期前约 12 小时周额度仍未耗尽，守护逻辑可提前使用对应卡，以免过期；这会放弃剩余周额度，并须在日志中写明。不要使用 10 月 23 日到期的第三张，也不要购买额度。

### 自动使用卡和 App 实时通知

首次启动时，在**另一台机器**验证官方 `codex app-server` 的 `account/rateLimits/read` 只读调用能返回同一账号的 `rateLimitsByLimitId.codex` 和卡片详情。之后建立一个独立于定时聊天运行的轻量本机守护任务，按分钟级间隔读取用量。周窗口 `secondary.usedPercent` 达 100% 或服务明确报告周限流时，按 `expiresAt` 选择最早到期且属于本轮的卡，调用官方 `account/rateLimitResetCredit/consume`，传该卡的 `creditId` 和**持久化的** UUID `idempotencyKey`；重试同一次操作复用 UUID。若接口只返回卡片数量、不返回可核对的卡片 ID 与到期时间，则不盲选，以免误用第三张。立即再次读取限额与可用卡，只有 `reset` / `alreadyRedeemed` 且卡数和额度核验相符才记为成功。`nothingToReset`、`noCredit`、认证错误或接口不兼容时不猜测成功、不尝试第三张。到期前约 12 小时的兜底也用同一核验流程。所有调用使用已登录的本机 Codex 账号，禁止抓取/打印 token 或调用未公开网页接口。

守护任务将“已触发、成功、失败、需要手机操作”写入 `plans/staging_run/` 的运行日志；同聊天 heartbeat 发现新事件后**在下一次运行时通过 App 聊天报告**，失败时提出需要答复的问题，触发手机 Remote 通知。通知内容包含周/5 小时用量、卡片到期时间、尝试结果和手机端 `Settings → Usage` 手动操作入口。手机端仅作为失败兜底；它已在预检中验证可收通知。如果后台聊天因限额也无法启动，则 App 推送无法保证实时送达，因此自动 App Server 守护是主路径。不要把固定时间闹钟当主提醒。

## 5. 在另一台机器上粘贴的启动指令

在该仓库的本地 Codex 桌面聊天中发送：

```text
请执行 plans/2026-09-staging-pool-unattended.md 这份临时计划。先重读 AGENTS.md、DEVELOPMENT_SPEC.md，再以启动时 tools_staging_pool/ 的实际目录和 staging_catalog.json 双向对账确定全部任务，之后每轮纳入新增单元。本轮要把每项整理到可直接晋级的最终版候选包：完整代码/资源、框架接口、Schema、正式文档候选、测试、面板和注册的晋级动作都预制在待整理池，不提前迁入正式库。Maya、mayapy、Python 或 UE 验证失败或卡住时，记录原因与复验步骤，标 prepared_unverified 并继续下一项；我最后集中人工验收。

请在此本地聊天设立可验证的长期目标、每 5 分钟 heartbeat，并先完成手机 Remote 通知测试。准备 plans/staging_run/ 的动态 manifest 与可恢复进度。按实时用量持续工作；5 小时限流后等最新重置时间继续。请在本机预检并实现官方 Codex App Server 的只读额度检查和指定两张临期卡的自动使用守护：周额度一耗尽就用最早到期卡并复核，卡临期时按计划兜底；失败则立即通过本聊天在 App 通知我手机处理。不得使用第三张卡或购买额度。不要修改长期项目规范，也不要运行 Obsidian 同步。全部动态范围完成后停用续跑并交付逐项 Maya 验收总表。
```

定时任务必须是**同聊天 heartbeat**，保持上下文；不要创建每次一个新聊天、每次一个 worktree 的独立 cron 任务。首次实际运行和守护脚本的只读预检结果应在 Scheduled 中核验。若该机器没有可用的 `codex app-server`、无法使用 ChatGPT 账号认证或守护进程不能稳定运行，先继续整理工具，同时立刻在已测试的 App 聊天向用户报告“自动用卡不可用”，要求手机端在周额度耗尽时用 `Settings → Usage`；不要声称已经实现全自动用卡。

## 依据

- [OpenAI Docs：Scheduled tasks](https://learn.chatgpt.com/docs/automations)：本地定时任务、同聊天 heartbeat、后台权限。
- [OpenAI Docs：Codex App Server](https://learn.chatgpt.com/docs/app-server)：`account/rateLimits/read`、`account/rateLimitResetCredit/consume`、`creditId`、幂等与结果核验。
- [OpenAI Docs：Pricing](https://learn.chatgpt.com/docs/pricing)：Plus 用量随模型和任务变化，周上限未给固定比例。
- [OpenAI Docs：Remote connections](https://learn.chatgpt.com/docs/remote-connections) 与 [Notifications](https://learn.chatgpt.com/docs/notifications)：手机端接收和处理需要关注的聊天。
- [OpenAI Help：Banked resets](https://help.openai.com/en/articles/20001498)：卡片到期、双窗口刷新与手动兜底。
