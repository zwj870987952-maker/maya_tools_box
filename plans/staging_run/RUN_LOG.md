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
# 2026-09-30：anim_layer_keyframe_bookmark 完整候选包

- 保留原 Python/README 与四色板 RGB；制作 generate/clear/inspect 框架 API、原生 UI 路由、无写入生成/删除预检、独立层查询、知识说明、目标 tests、真人验收表和晋级清单。正式库/注册表/长期规范未改动。
- 修复基础层跨层混入与历史节点长短名问题；保留四位小数去重及整数显示名，明确短子帧/重复显示名/默认不清空时重复创建行为。clear 与 clear_existing 删除全场景书签，预检展示并拒绝锁定/引用项；空键/数量超限不得删除旧书签。
- 初次隔离检查发现 Maya 删除后重用节点名，异常报告误以为原节点仍存在；改用 UUID 记录删除目标与新节点。针对中途 color 写入失败，报告部分创建/删除并验证单步 Undo 可恢复。
- 8 项离线检查和 8 项 Maya2025 隔离检查最终全通过，涵盖四色板、预检无写入、层隔离/全层、清空/替换 Undo、数量上限、插件未加载、锁定项与部分失败。报告与当前 Python 指纹一致，晋级预览通过；状态 prepared_verified_offline，GUI/引用书签真人检查/其他版本仍待验收。
- 插件加载从预检中移出，生成保留原 writeRequires=true 并注明不能由场景 Undo 保证恢复；创建 skipSelect 保持选择。累计 5/109 完整候选。
# 2026-09-30：Anim Layer v4.0 开始源审计，未计完成

- 全套 6 文件，完整版包含 216 个过程/197 global 和 source 时创建编辑器的顶层代码；NoUI 为 33 global、无顶层执行，但多个过程依赖原生 UI。审计保存源 SHA/签名/顶层行，不执行安装器或原始完整 UI。
- 全版不为 UTF-8，词法审计 byte-preserving Latin-1 仅认 ASCII MEL 结构；不能重编码原资源。自定义商业许可/Autodesk 通知均原样保留，下一轮制作整体运行适配，不改写原脚本。
- 状态仍 working，详见 anim_layer_v4_0_notes.md；累计完成仍 5/109。实际额度本次读取 primary used=5%、weekly used=42%，窗口已自然刷新、4 张卡未兑换，heartbeat 保持 PAUSED。
# 2026-09-30：Anim Layer v4.0 完整套件候选完成

- 完整 6 文件资源原样保留，包括非 UTF-8 全版 MEL、NoUI/安装器、帮助图/许可/readme；没有改写算法或 source 安装器。完整版 197 global/NoUI 33 global 全部签名保留，新增 typed MEL bridge、inventory/load/invoke/open_ui、网关/帮助、BaseMayaTool/Schema/ToolResult/Undo 和导出新路径保护。
- 修复适配器把 BaseAnimation 时间查询 sentinel 误当作必需节点的预检；原时间查询、数组/层选择、source provenance、字面量、单步 Undo 和异常 evaluation 状态恢复经隔离验证。8 项离线/8 项 NoUI Maya2025 检查最终全部通过。
- 整套仍 prepared_unverified：full source 会重建原编辑器/覆写全局 MEL，未在 standalone 强行加载；原菜单/烘焙/抽取/合并/legacy渲染/显示功能未GUI验收。已预制完整业务/签名知识说明、逐项验收、目标 tests 与晋级清单。原 UI 回调不自动进入新增框架，进程 MEL/UI/options/scriptJobs/文件不由场景 Undo 保证，说明已记录。
- mayapy 报告新增 runtime_source_sha256，覆盖 MEL/catalog/UI/图片等运行资源与 Python/tests，防止资源变动仍复用旧报告；本候选 Python/runtime 指纹均匹配。记录器可显式登记未满足的运行证据，本项完整套件 GUI 证据缺失如实保存为 false。
- 累计 6/109 个候选完整；正式库、注册表、长期规则/Obsidian 生成文件未改动。

## 2026-09-30：Anim Mirror Helper 完整候选，累计 7/109

- 保留原商业 MEL、安装器、图标、许可和英俄指南共六文件，所有 90 个 global proc；原英文指南 12 页提取并渲染查看，俄文仅保留资源未进行翻译。
- 增加 typed invoke（含 vector[]）、有明确名称的镜像工作流 action、只读预检、Undo、Evaluation/refresh/timeSlider 的 finally 恢复、原生候选入口与完整原窗口加载；原业务代码及回调不修改。
- 普通 Python 5 项通过；Maya 2025 隔离 standalone 7 项通过，涵盖完整 source/90 过程来源、icon、向量平均、单位、dry-run 不 source、异常恢复。选择保护使用 GUI 标志 shim 验证只读分支，未创建或验收真实 GUI。
- 新增测试适配未来正式目录；临时正式布局下 5 项离线检查通过，正式库没有改变。签名检查已修复 string [] 空格写法；最终 mayapy 报告与 Python/运行素材指纹一致。晋级预览 applied=false。
- candidate_complete=true，prepared_unverified：真实 rig 镜像、连接、循环偏移、烘焙及视口按钮待人工；原 catchQuiet 与非 Undo 影响写入说明。未安装 shelf、未公开发布、未运行 Obsidian 同步。
- 本项收尾读数：5 小时已用 33%、周已用 46%，剩余额度可继续；heartbeat 暂停，未兑换卡。下一项 anim_polish_premium_v1_23。

- 镜像候选提交 553da07；提交后额度复读为 5 小时已用 37%、周已用 47%（可继续），写入下一项检查点。

## 2026-09-30：AnimPolish 完整候选，累计 8/109

- 原 17 Python + README + Word 文档共 19 文件完整保留，160 原函数签名，其中 157 为 JSON API；旧状态脚本/实时文件句柄辅助保留但不作为 JSON invoke。原 Word 内容及五张嵌图用于核对工作流，不对原 Word 改排版。
- 独立 vendor namespace 保留完整算法和原 UI；fix literal_eval/list 默认参数、Python3 exec 局部回写、缓存 New Version 漏调用和 swap 目录。差异单独保存。Settings/属性剪贴板改 JSON、支持字符串/向量，不自动执行旧用户 Python 状态。
- 所有 cache exp/import/swap 自带保护且 reload 后仍有效；禁止覆盖 cameras.ma/geometry.abc。Subdue 仍调用原 doCreateGeometryCache，args[5] 根据本机 Maya2025 stock MEL 定义改为全新 UUID 用户缓存目录；外部 .mcx/.xml 不能 Maya Undo。
- 发现原 sortCB deleteAttr/Undo 与框架 chunk 冲突；保留排序算法但延后 UI idle，UUID 捕获/恢复选择，排序不宣称包含在雕刻原子撤销内。
- 6 项离线检查通过，临时未来正式布局同样 6 项通过；Maya2025 isolated 15 项通过，含 Wrap/Grow/Iron/preview 真节点+Undo、Sculpt start/abort、三个 apply 模式的真实 cluster/keys/Undo、字符串属性 JSON/Undo、相机临时导出及防覆盖、namespace 全模块 import/reload、异常恢复。设置 UI 控件/Subdue MEL 是 stub；Sculpt apply 的 prefix/延后排序是 stub；sort 原算法在 chunk 结束后手动执行排队回调验证，未验收真实 GUI idle。
- candidate_complete=true，prepared_unverified；完整 UI、绘画、Subdue cache、Alembic/Sticky/P2P编辑/缓存附着仍待真人复验。晋级预览 applied=false，长期规范/正式工具库/注册/生成知识库未改。
- 首次收尾额度读取暂时失败，未当作额度为零；提交前后重读，再记录实际检查点。
