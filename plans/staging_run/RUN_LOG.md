# 本轮执行日志

## 2026-09-30：启动与首个候选

- 用户确认流程表后开始执行；只在本聊天写入固定目录 `E:\GitHub\maya_tools_box`。
- 实时范围：8 分类、109 工具单元、109 清单记录。修正 34 个入口路径：13 个唯一同名文件路径修正，21 个依据源码/说明核准实际文件。入口存在不表示可直接安全启动。
- 已更新工具池 README 的对应链接。安装器、导入即打开 UI、版本分支等差异写入 entry_audit.json 与清单 entry_notes。
- 全池只读 Python3 源码语法审计：1125 个 Python 文件、103 个 MEL 文件；8 个工具单元含 Python3 解析错误。具体错误见 source_audit.json，不能把旧 Python2 语法直接等同于工具损坏。
- reset_pivot 原始脚本未改；完整候选含 7 个动作、UI、无副作用预检、结构化结果、UUID 路径修复、finally 父级恢复、安全拒绝、说明、目标测试、验收步骤和晋级清单。
- reset_pivot：10 项隔离单测通过；Maya2025 mayapy 的 4 项隔离场景测试通过，测试覆盖 7 个 action 的预检与执行/Undo 路径；没有 GUI 验收，其他版本未实测。
- 晋级预检通过，applied=false；通用晋级脚本在临时迷你仓库的 6 项安全测试通过。正式目录、正式注册和面板文件未变动。
- 同聊天 30 分钟 heartbeat 已创建；PAUSED→ACTIVE→PAUSED 状态切换成功，并读回确认线程绑定与暂停状态。实际定时触发、恢复整理和手机推送仍未核验；不声称完全自动续跑已通过。
- 一次额度读取失败，后续重试成功：5 小时已用45%、周已用37%（当时快照）；未将读取失败解释为无额度。没有使用任何重置卡或启动兑换守护。
- 本轮没有运行 Obsidian 同步，没有修改长期规范或生成知识库。

后续从 manifest.json 读取未完成项，动态重扫目录，并继续制作候选。记录 source_commit 时使用真实已产生的 Git SHA；不预写尚不存在的提交号。

## 2026-09-30：anim_filters 候选完成，验证不足继续推进

- 本轮恢复时核对 Git 工作树和清单；首个候选仍为 reset_pivot，下一项为 anim_filters。
- 保留全部 5 个上游文件及原 GPL 声明，并附 GNU GPL v2 正文；候选运行路径不依赖待整理池中的原始资源。
- 保留 Adaptive/Butterworth/Median 三种数学操作与原 UI，提供统一 API、无副作用计算预检、实时预览、buffer、参数刷新、取消/应用/关闭恢复及注册晋级资料。
- 修复确定缺陷：零阈值线性段递归、递归深度、linspace float 样本数、padlen 相等边界、Nyquist 无效值；改变范围及依据写入专项文档。
- 用命令写入及唯一 Undo Chunk 替代原预览关闭全局 Undo、直接 API 写入和 clipboard 恢复。预览若不在 Undo 栈顶则拒绝自动撤销其他操作。
- 原脚本端点覆盖行为用隔离 translateX/rotateX 曲线直接对照；候选一致，区间外键保持。
- 隔离 Python 测试：10 项通过、1 项科学数值测试因 SciPy 缺失跳过。Maya2025 mayapy：5 项场景/预览测试通过、1 项依赖检查失败、1 项 Qt 测试跳过。
- 先前 Qt widget 尝试以 Windows 状态 3221226505 退出；保存原报告 anim_filters_qt_failure.json，未继续在主 standalone 测试进程中重复触发。真实 GUI 待用户实测，不将这个失败写成通过。
- candidate_complete=true；status=prepared_unverified。依赖缺口、错误输出和复验命令均已记录；正式库未晋级。
- 恢复扫描增加原单元全部文件/资源的指纹和候选交付指纹检查，源码或候选变化时撤销陈旧的完成状态，避免仅入口没变便沿用旧证据。
# 2026-09-30：anim_layer_bookmark_trimmer 完整候选包

- 保留原脚本/README 的完整归档，拆分业务算法与原生 UI，四个按钮经 BaseMayaTool 调用。预制运行包、Schema、知识说明、目标测试、真人验收表和晋级清单；正式库/注册表保持原状。
- 修复单曲线字符串返回、其他浮点通道漏选、缺少端点时的预检索引异常；插件加载从查询移到显式 UI 启动，端点插入失败不再吞掉。优化拒绝重叠和退化书签，补有限值/锁定/引用/单输出等预检。
- 明确原行为：局部范围使用相交的整段书签；修剪覆盖首尾范围和中间空隙；selected 无命中使用最近书签；端点是本层曲线值，切线/整曲线 weightedTangents 可能影响范围外插值，力度 0 并非绝对无操作。
- 普通 Python 8 项检查通过；Maya 2025 隔离场景 10 项检查通过，包括六优化模式、缺端点、修剪补键、通道排除、双向层隔离和单步 Undo。最终 mayapy 报告与候选 Python 指纹一致，晋级只读预览通过。状态 prepared_verified_offline；真实窗口/时间滑块/Channel Box 交互及其他版本仍待验收。
- 动态清单仍为 109 单元/109 清单/109 有效入口；累计 3 个候选完整，后续从 anim_layer_key_runner 开始。
# 2026-09-30：anim_layer_key_runner 完整候选包

- 完整保留 Python/MEL/README 原始存档；原 MEL 的 source 自动执行不用于候选启动，新增只定义启动过程的 MEL 桥。拆出原生 UI，调度统一使用 BaseMayaTool/Schema/ToolResult，正式库与注册表未改动。
- 层查询规范单字符串返回，基础层禁止跨层兜底，全层按确切对象属性合并；保留四位小数/0.001 容差，补帧数上限、未知参数/语法/类型/非有限数值预检。dry_run 从不 eval/exec 命令；Python 只编译语法。
- 命令调度恢复原时间和存活的原选择，UUID 解析支持对象改名；逐帧结构化失败并可选择首错停止。命令写入层取决于命令本身，任意命令/外部文件影响不由预检或 Maya Undo 保证，文档与 Schema 已写清。
- 8 项离线检查及 9 项 Maya2025 隔离检查全部通过：MEL/Python、预检无写入、帧失败、层隔离/全层、播放/上限/空动画、删除/改名和单步 Undo。mayapy Python 指纹一致，晋级预览通过；状态 prepared_verified_offline，真实 UI/Advanced Skeleton/其他版本待验收。
- 累计 4/109 个完整候选；范围仍实时扫描。工具小批提交后继续下一 pending 单元，不提前转正，不运行 Obsidian 同步。
