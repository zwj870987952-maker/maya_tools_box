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

- AnimPolish 提交 03faa9d；收尾读数恢复成功为 5 小时已用 70%、周已用 52%；heartbeat 继续暂停，无重置卡兑换。下一项 animation_retarget 已标 working。

## 2026-09-30：动画重定向完整候选，累计 9/109

- 原始自有 Python 按字节完整保留；全部 Qt 界面交互保留，业务迁移为 align/numeric_copy/bake/load_scene/restore_pose/save_config/load_config 标准接口，使用现有 core Qt 兼容层与框架 Undo。
- 修复原脚本全局 Constraint_SelectionSet 误删风险：仅删除所选目标的候选约束，校验 UUID、所有权、pair_id 和输出目标；network 姿态记录不占用原 Rematch 组，兼容旧 Rematch/JSON 读取，类型化字符串/向量/矩阵姿态与命名空间/长路径。
- 保留原 maintainOffset、TRS 模式默认值、源对象帧并集和两种 bakeResults 参数；明确记录 bake 不受 none 限制。源/目标姿态提前到约束创建前，数值复合属性拆子通道，配置保存不覆盖，执行 finally 恢复时间与选择。
- 5 项普通 Python 检查通过，12 项 Maya2025 隔离实节点检查通过：约束偏移、数值/小数帧/自定义向量、默认/智能烘焙与 Undo、外部约束集合保持、重命名与同名替身 UUID 防护、类型化 JSON/旧姿态、无副作用预检、文件保护和异常恢复。首次旧姿态 fixture 硬编码 source 失败，Maya 实际创建 source1；修正为实际返回节点名后通过，未把最初失败记成通过。
- 临时正式布局下离线检查及真实 ToolRegistry 注册/面板入口查询通过；正式库没有写入。Python/runtime 指纹与 mayapy 报告匹配，晋级预览 applied=false；candidate_complete=true、prepared_unverified，真实 GUI/复杂绑定/旧分隔符歧义姿态仍待真人。
- 收尾最新读数为 5 小时已用 84%、周已用 54%，继续读取并保存下一项检查点。没有兑换重置卡，没有改长期规则或同步 Obsidian。

- 动画重定向提交 34b9bbe，后续检查点 abfb349。提交后额度已用 88%/55%，继续 AniMirror v2.0。

## 2026-09-30：AniMirror 工作中，额度等待检查点

- AniMirror 原安装器顶层写 Shelf，未执行；唯一嵌入命令完整提取为 9 过程及原布局，原 MEL/PDF 两文件字节保留。两页 PDF 文本和图示均已读取，未修改 PDF。
- 私有 MEL 过程/变量/控件名前缀及无顶层开窗载入已准备；修复 withBake 清理后 ind 增一的顺序。契约改用原 translation_axis，避免把 UI 标签/mirrorJoint 选项误解为最终位移平面。
- 初次编译探针 passed；加入真实隔离场景探针后遇到 floatMath 不可用。确认本机 lookdevKit.mll，并在隔离进程显式加载；随后修正探针对 XY/negX 的错误几何预期。最终所有9过程来源/编译、原算法 X 镜像动态采样和清理检查 passed。UI 查询是固定值 shim，未验收 GUI/其他轴/旋转/中心变换/bake；没有把探索报告当完整候选指纹证据。
- 此项仍 working、candidate_complete=false。API、持久化 UUID 所有权/Undo、标准界面回调、晋级及真人验收资料未完成，不计入9项完成数量。下次先读 animirror_v2_0_notes.md 和 diff 接续。
- 两次额度读失败未按0推断；之后恢复读到 92%、93%、94%、最终95%已用（剩5%），周已用56%。为避免复杂工具中途触达硬限额，保存未完成项并启用同聊天30分钟 heartbeat；工具返回 ACTIVE。自动定时触发/续跑仍未实测，不声称完全无人值守；重置卡未兑换，守护未启动。

## 2026-09-30：同聊天 heartbeat 恢复成功

- 最后一批 Git add/commit 上次因自动审批遇到额度上限而未执行，原始部分暂存及工作文件均保留；这属于审批服务无法完成而非安全风险判定。没有绕过审批。
- 30分钟同聊天 heartbeat 消息实际到达；本次先读额度失败，重试恢复为 5小时已用2%（剩98%）、周已用57%（剩43%）。满足条件后工具暂停 heartbeat 为 PAUSED，恢复 AniMirror 工作；未消费任何重置卡。
- 补完成本地检查点提交 4d83d47。已观察到同聊天定时触发→读取恢复额度→暂停自身→恢复工作整个路径；手机推送和卡守护仍未验证/未启动，不声称其他机器或全额度彻底耗尽时同样可靠。

## 2026-09-30：AniMirror 完整候选，累计 10/109

- 全部九个原 MEL 过程和原窗口保留，另加两个 typed option/cache reader；业务 UI 查询改显式参数，原 UI enable/disable 保留，四按钮走 BaseMayaTool/ToolResult/Undo。位移用原 X/Y/Z 选择，不凭原平面标签重写算法。加载仅定义过程，不执行安装器或 Shelf。
- UUID 所有权 network 随保存/Undo 恢复，执行前从场景重建 MEL 列表；清理拒绝外部后代/消费连接，仅允许 floatMath 的 defaultRenderUtilityList 系统登记。显式 UUID baseline 修正多镜像所有权捕获；删除前缓存 UUID 和脱离目标下候选约束，修复 Maya 清理 helper 时连带删除空 transform。内部写场景 MEL 受标准入口保护。
- 普通 Python 五项及 Maya2025 隔离十四项通过，涵盖真实三轴/旋转、累计 bake/filterCurve、单次 Undo、失败保护、重命名同名替身、组件选择及保存重载。没有创建 GUI；复杂中心/绑定、实际高亮范围、其他版本与原指南的生产骨架支持待真人。
- 完整专项知识说明、资源/Schema/注册晋级清单与真人验收已预制；本项原资源和 upstream 加 -text Git 属性，防止自动换行转换破坏字节归档哈希。原资源内容未编辑。早期探索探针历史保留，当前编译探针不再绕过标准 API。
- 修正 record_candidate 不覆盖已观察到的 heartbeat 验证事实；本轮 heartbeat 已实际恢复且保持 PAUSED。正式库/长期规范/生成知识库未改，不运行同步，不消费卡或购买额度。

- AniMirror 候选提交 e109a1a，检查点0ddbb18；收尾实时额度33%/62%已用，继续 Back2Origin。

## 2026-09-30：Back2Origin 完整候选，累计 11/109

- 原文件36函数完整归档，原八个核心算法AST一致，完整反向循环独立参数化；原生界面/帮助/发现/namespace保留，移除导入复制/开窗，安装函数明确禁用。独立UI名称、callable回调及标准ToolResult/Undo，不写正式库。
- 原世界root→局部global数值、反向覆盖root、absolute frame modulus 和 cutKey全部translate行为保留且写入说明；帧步长>1检查所有可能被删键的轴，拒绝引用/锁定/非animCurve驱动、重复角色和不明确对象。执行finally恢复eval/refresh/time/selection/四个播放范围。
- 5项普通Python及10项Maya2025隔离实节点通过，涵盖真实正向/反向、世界位置、键与Undo、未选轴删键、范围外键、缺省范围/缺global、引用/驱动预检、发现和失败恢复；原生GUI/生产rig/引擎结果待真人。首次Undo fixture用currentTime采样在工具之上增加动作而失败，改为worldMatrix/time只读采样后通过。
- 当前候选包含完整知识说明、两测试、验收及注册晋级清单；Git属性防止换行转换破坏原件/candidate哈希。继续保持heartbeat暂停，不兑换卡、不购买、不运行Obsidian同步。

- Back2Origin候选提交95c457a，收尾实时额度43%/64%已用，下一项bh_aim_tools_v1_1。

## 2026-09-30：bh_aimTools 完整候选，累计12/109

- 购买工具ReadMe明确不要分享，四原资源完整本地保留，未发布；完整16原过程/原生UI，另加typed参数读取，共17过程。创建/附着/Aim/两种烘焙均标准API，唯一顶层窗口移除。
- UUID/Owner/token与ctrl message防护，不接管旧工具定位器；只删除自己临时约束，清理前脱离控制器下候选约束，保护空控制器；临时root返回实际唯一名及DAG叶名，避免碰撞误删。旧全时段旋转键删除改显式参数，UI仍给Yes/No且默认No。
- 原轴启发式、maintainOffset、SetKeyRotate、pairBlend与filterCurve保留；Maya混合节点/属性可能保留，明确返回survivors，不自动删除承载旧动画的节点。执行finally恢复cache/eval/refresh/time/range/selection，create/bake成功选择结果。
- 4普通Python及9隔离Maya2025检查通过：真实流程/键/朝向/烘焙/Undo、UUID/重载/批量同叶名、外部约束/后代/改接、失败恢复和来源保护。首次Aim后新增控制器键生成外部pairBlend被正确拒绝；改为Aim前旧键。批量fixture歧义短名改确定长路径。GUI、生产rig、动画层和复杂blend仍待真人。
- 专项说明、两测试、晋级注册与验收齐备；Git属性保存原资源实际字节。正式工具库、长期规则及knowledge未改，heartbeat继续暂停，卡未消费。

- bh_aimTools候选提交a67f18a，收尾实时额度53%/65%已用；下一项bh_local_nudge。

## 2026-09-30：bh_localNudge完整候选，累计13/109

- 五原MEL过程和完整原生窗口/12按钮保留，三原资源按字节归档；无顶层开窗，私有过程/控件，场景按钮标准API。参数amount/ctrl/alt替代业务UI依赖，保持属性加减、CTRL半值/ALT四分之一、Right负X/Left正X。
- 只读通道预检与Undo，实际after查询，恢复组件选择；不改原动画/autoKey行为。原算法不显式打键：隔离autoKey关闭时已有动画通道微调不改变键，时间切换后按原曲线恢复，写入说明与真人步骤。
- 四普通Python及七隔离Maya2025检查通过，含真正MEL数值/旋转/四modifier组合/多对象/父级局部语义、Undo、预检/组件、动画/故障恢复。GUI、真实按键/autoKey/非默认单位/其他平台待真人。
- 完整说明、两测试、资源、Schema/注册晋级清单和验收已预制，仅待整理池有业务代码变动；heartbeat保持暂停，无卡消费或知识同步。

## 2026-10-01：bh_speedLines 完整候选，累计14/109

- 八原资源完整按字节归档；21原过程/原窗口保留，加typed option reader共22，移除顶层开窗/偏好修改。原loft/转换、polyReduce/rebuild/SmoothHairCurves/polyNormal、整数时间visibility、Pencil/EP/深度流程保留，按钮走标准API。默认消耗曲线与可选保留、原16转换偏好finally恢复写明，不自动赋纹理/安装。
- owned plane/shapes/live/context UUID记录，外部同名/子对象/消费者拒绝；只按已保存ID清理自身parented EP ToolChanged和Undo job，关闭窗口/Undo deferred路径预制。平面重命名仍可stop，深度固定名操作拒绝。Undo/Redo不宣称自动复原GUI上下文和任务。
- 4普通Python及9 Maya2025隔离检查通过，实际几何/曲线/法线/可见性键/偏好/Undo/层、guard/故障恢复与headless owned-plane fixture；正式布局及注册预览通过，指纹匹配。headless没有currentCtx，清理跳过GUI上下文命令；转换偏好恢复异常仍尝试恢复时间/选择并关闭guard。
- 实际polyReduce显示已有历史导致ch=0被忽略，说明中保留此限制。鼠标绘画/start_draw、滑条、EP/Pencil、ToolChanged/关闭/deferred Undo均未运行真实GUI，仍prepared_unverified；完整人工步骤和知识说明齐备，正式库未改。

- bh_speedLines完整候选提交ef1268f，收尾实际额度70%/68%已用，进入bh_wave_it。

## 2026-10-01：bh_waveIt 完整候选，累计15/109

- 原十过程/完整compact-advanced窗口和三资源保留，移除两次顶层开窗；四typed参数reader/setter，无业务窗口查询。原6.28/rad_to_deg公式、S/C/invert、首对象base offset覆盖语义保留；显式有序数组确保选择顺序不被排序，UI滑条/预设走标准API。
- 无副作用标量通道预检，引用/锁/外部驱动/缺失属性/歧义拒绝，Undo分组/finally时间与组件选择/guard恢复。不显式打键，实际autoKey关闭旧键不变，切时间恢复原曲线。位移/custom使用同一角度数值，当前单位/整数强制转换/拖动Undo数量均写明。
- 普通Python四项、Maya2025隔离八项、临时正式布局注册通过且指纹匹配；真实多轴/custom/有序/预设/首对象/Undo/reference/故障/动画检查。早期角度内部浮点3.0000000000000004/6.000000000000001导致fixture严格相等失败，改近似比较，原算法未改。
- GUI/Interactive/Channel Box、autoKey开启/非默认单位/制作rig仍not_run，完整知识/人工验收/晋级清单已预制，只保留待整理候选；heartbeat暂停，无卡消费/正式库改动/Obsidian同步。

- bh_waveIt完整候选提交83ecf29，实际收尾额度74%/68%已用，进入brs_loc_transfer。

## 2026-10-01：BRS Locator Transfer完整候选，累计16/109

- 单原文件字节归档，17原函数均有候选对应，18函数含build_ui；六helper AST除guard外一致，创建/回写/guide完整循环保留。移除导入GUI/下载exec/关cycleCheck，原四按钮/布局标准API，显式选项替代业务控件和全局进度条依赖。
- UUID+message持久目标对应、Owner/Role定位器/组/guide/约束/annotation/shapes，重命名parent实际路径更新、安全所有权清理；约束先脱离目标再删保护空控制器。外部同名/子对象/约束/改接拒绝；None breakdown修复，原静默失败改明确错误。保留原bake/round/keep/snapKey边界，额外动画属性回写拒绝以免原全通道操作误改。
- 普通Python3项、Maya2025隔离8项、临时正式布局注册检查与哈希匹配通过；涵盖真实创建/回写/编辑/annotation/密度/timeline/breakdown/Undo/重命名/保存重载/故障与保护。
- guide路径实际完成但简单平移观测group.tx=10、locator第1帧worldX仍0，原先缓存世界动画→移组→回写流程保留，不能当作整体动画重定向通过。输出警告/知识/人工清单均明确，此项prepared_unverified，制作意图待真人确认后再修/转正。
- 完整两测试/专项说明/资源/Schema/注册晋级资料齐备；正式库未改，heartbeat暂停，无卡消费/同步。多次额度读暂时失败未按0猜测，收尾成功实际80%/69%已用。

- BRS Locator Transfer候选提交c277557，进入brs_smooth_mocap。

## 2026-10-01：BRS Smooth Mocap完整候选，累计17/109

- 原单文件完整字节归档，valueAverage AST除guard外一致；原三邻点快照/端点保持/strength-1循环及locator→六TR bake保留。完整固定BRS locator后端含原来源随包，独立Owner/辅助名，不依赖另一个待整理包或scripts目录；移除scripts exec/导入确认执行/关别的窗口。
- 标准smooth_keys与smooth_mocap参数/Schema/只读计划/Undo，新参数UI显式确认。修复叶joint None、非joint后代/单时间键定位器缺失，明确跳过；Mocap明确约束启用，回烘后仅owned约束/locator安全清理，blend旧动画载体可能保留。
- 普通Python3项及Maya2025隔离6项通过，真实原平均值/快照/端点/键选择与Undo，两轮locator平滑将中值6回烘为2/3、成功清理/Undo、静态后代/strength1、只读/锁/故障双guard恢复。正式布局注册预览和全部证据哈希匹配。
- 真正Graph Editor/动捕资产/jointOrient/大角度旋转/复杂层和视觉质量未验收，prepared_unverified；完整依赖/知识/两测试/注册晋级和人工清单齐备。保持heartbeat暂停、待整理池、不消费卡/不改正式库/不跑同步。

- Smooth Mocap候选提交f39c54b，收尾实际83%/70%已用，进入cg_shake_py3。

## 2026-10-01：CgShake完整候选，累计18/109

- 原14方法对应完整Qt布局/原生gradient/四图/预设/Cache/Restore/Overwrite/Use cache，七原文件字节保留。复用core.ui_base绑定PySide2/6，延迟主窗口，Frame最低1，缺预设目录开窗不崩，原样式漏PNG后缀修复；不自动载插件。
- 原仅第一选择、两循环快照、六次正向uniform及六TR setAttr/非零amount打键保留；GUI原gradient求值，API显式每帧权重，无伪造插值。全对象清键/层作用域明确，标准Undo包住原chunk外overwrite/restore，finally时间/选择/四播放范围与guard。
- UUID缓存路径/Owner场景记录/SHA+sidecar校验，清键前验明目标/文件；临时文件后替换、已有文件覆盖需显式允许，旧cache属性不接管。文件/目录/clipboard不能由场景Undo撤销，真实说明/人工步骤齐备。
- 普通Python3项、Maya2025隔离6项通过，真实随机/首选/范围/zero通道/Undo/预检/故障、预设文件覆盖及animImportExport .anim导出导入/SHA修改拒绝；正式布局注册和报告指纹匹配。未创建Qt，实际渐变/层/Use cache GUI不算通过。
- 收尾真实额度5小时已用1%、周71%，窗口resetsAt从1790791927变1790810074，自然刷新；四卡仍available，无消费/购买。上一窗口从2%/57%到至少83%/70%，未观测完整0→100窗口，不能据此声称精确满额周消耗。工作继续、heartbeat暂停、正式库/长期规范/生成知识库未改。

- CgShake候选提交bfd16ec，进入copy_animation。

## 2026-10-01：动画复制完整候选，累计19/109

- 原优化文件完整字节归档，六采样/帧门控/match/numeric算法AST只加guard，其余一致；完整五Qt类/列表delegate/圆点/右键/拖拽/录入编辑/配置保留，场景/文件按钮标准API。修复列表clear删除C++item后复用旧wrapper，先缓存modes再新建条目。
- 每pair Owner/token network与source/target message+UUID、helper/follow/target constraint UUID持久记录。私有组/四集合，只删自己的资源，后代/输出/改接/外部固定名保护；约束先脱离目标保护空transform，临时失败资源及时记UUID，blend可能保留。cleanup独立标准动作，列表清空不改场景。
- 普通Python3项、Maya2025隔离9项通过：真实frame整数键/初始偏移/Undo，numeric逐整数/custom标量，持续constraint/repeat/cleanup，frame→constraint→numeric，持久重命名/保存重载、同叶名两pair批量、只读/外部对象、配置覆盖与错误返回失败/guard/Undo。正式布局注册/报告指纹匹配。
- 未实例化Qt，圆点/右键/拖拽/编辑/文件对话框和nonuniform scale/层/制作rig/旧Python待真人；完整知识/两测试/验收/注册晋级预制，prepared_unverified。实际收尾5小时8%/周72%已用，heartbeat暂停，无卡/正式库/同步变更。

## 2026-10-01：Directional Cycle完整候选，累计20/109

- 原五文件字节/CC BY-SA 4.0署名保留，八函数及完整Dockable原窗口，复用core Qt绑定；左右±angle/脚±90、后退timeScale=-1/骨盆层、校正/反旋转原流程保留。原仅删第一组临时约束修复为全部嵌套列表，校正真实shape路径、足数1..999/当前角色计数检查。
- per-cycle Owner/token network/UUID/message、唯一owned方向/骨盆层和helper，原Left/Right/Back不覆盖；清理先脱离目标约束防空控制器误删，外部子节点/输出/层成员保护。默认保留输出层/network/旧动画载体，remove_layers显式，失败含record UUID/Undo，finally时间/选择/旧层标记/guard恢复。全对象bake作用域、固定世界head aim、原pelvis层公式、back角色/参数差异均明确。
- 普通Python3项、Maya2025隔离7项、临时正式布局注册/面板/Schema检查及指纹通过。实际左右脚轨迹/后退键反转/三足correction-counter路径与back双层/完整cleanup/命名隔离/重命名保存重载/故障Undo；捕获节点UUID改显式逐节点ls查询，层root内部连接允许，未创建Qt。
- 真正GUI/制作循环rig/脚滑移/固定瞄准点/复杂层/非均匀缩放和其他版本待人工，prepared_unverified；完整候选/知识/两测试/注册晋级/验收齐备。收尾真实5小时19%、周74%已用，heartbeat仍暂停，无卡消费/正式库/同步。

- Directional Cycle完整候选提交115d41a，进入dof_control_v1_0。

## 2026-10-01：DOF Control完整候选，累计21/109

- 原MEL与XPM字节保留/Dirk Bialluch自由分发声明，完整polyCube/addDoubleLinear/reverse/隐式unitConversion图与负XY缩放保留，真实shape渲染flags，私有guard过程/明确camera数组/唯一辅助名/无force覆盖。原无UI，新增标准create/template/cleanup/记录列表入口。
- camera UUID/message、Owner/token network记录原focusDistance/fStop、cube与全资源真实UUID、实际相机源plug。全批只读预检拒绝原动画/驱动/锁/引用/实例/重复记录；清理仅自己的图且恢复创建前数值，外部后代/输入/输出/改接/缺失保护，材质集合membership自动断开但不删除集合。时间/选择/guard恢复，故障record可追溯/Undo。
- 普通Python2项、Maya2025隔离6项、临时正式布局注册/面板/Schema及报告指纹通过：厘米focus=-tz/fStop=sz/四renderflag/DepthOfField保持、真实值编辑/cleanup原值恢复/Undo-redo、双相机namespace/模板Undo、原动画拒绝/外部保护、重命名保存重载和部分失败Undo。
- 原ScaleZ实际fStop而非物理焦深范围明确；真实GUI/Viewport/template/renderer/非厘米单位/相机缩放待验收，prepared_unverified。完整知识/两测试/晋级/验收齐备，收尾真实5小时23%/周74%已用，工作继续、heartbeat暂停、无卡/正式库/同步。

- DOF提交01b2566；生成MEL继承原注释的一处尾空白随后修正为5c4dc6b，Maya/布局/指纹刷新通过，后续提交只在检查exit0后执行。正式库未改。

## 2026-10-01：EB Labs ScreenSpace完整候选，累计22/109

- 148原文件/版权/原许可管理/数据/prefs完整字节归档，不运行安装器/Hub/prefs/许可/网络；原Python hybrid版本模块缺失，候选直接使用完整独立native MEL，不依赖临时路径。21原过程对应，全原窗口/投影归一化/aim-depth/orientation/Smart Bake循环保留，Full Bake原逐步1采样后同Smart流程。
- 私有procedure/control名，按钮标准API，明确camera/target/orientation；只读验证，owned network UUID/message/source/control/rig映射、唯一helper名、外部后代/输入/输出/锁保护，清理仅owned约束/helper且保护空target，必要pairBlend/target曲线/buffer与来源record保留。去除全Maya窗口/pane隐藏，finally时间/选择/namespace/guard。零距离明确错误；已有焦距/许可逻辑不改。
- 普通Python2项、Maya2025隔离6项、临时正式布局注册/面板/Schema与全指纹通过，实际0.4/-1归一化/屏幕编辑后的目标移动/nearClip、TR稀疏Smart及逐帧Full Bake/Undo、namespace、改名保存重载和后代保护、部分失败Undo。曾因测试在动作后额外currentTime导致只Undo切帧，改为只读带time取值后整组Undo通过，不当作算法缺陷。
- 真正GUI/生产camera/非均匀父级scale/镜头穿越/复杂rig/层与视觉效果待人工，prepared_unverified；clip/buffer/key时序切线影响、原Hub缺模块仅归档/版权私用、完整验收/晋级齐备。manifest原子替换一次WinError5，立即重试scan成功再记录，并非持续权限障碍。收尾实际5小时31%/周75%已用，继续工作、heartbeat暂停，无卡/正式库/同步/公开发布。

## 2026-10-01：EB Labs Whiskey完整候选，累计23/109

- 完整4930行原WhiskeyPro源码22类/272方法及133原资源逐字节归档，完整原生widget/slider/profile/固定选择/倍率，私有窗口/独立JSON元数据；不运行缺失hybrid Hub安装器/版本模块、原许可管理器不改，私有版权资源不公开。
- 保留全部原补间/世界矩阵/快照/InOut/PosePusher/Multiply/清理/Smash/切线业务；15直接写入方法标准回调ticket/Tool.run，Undo保持开启、取消隐藏面板/隔离、每回调chunk替代跨事件长chunk。只读/UUID写范围/引用锁/共享曲线保护，finally时间(未变不强制求值)/选择/namespace/AutoKey/层flags；API原AutoKey开时显式补键，偏好会话保存+显式JSON导入导出，独占创建/覆盖授权，无全局prefs自动写入。
- 修复源包围盒缺cls、Multiply不存在层方法→合成值标准分支、无曲线层通道索引、Maya2025曲线keyValue禁止setAttr→等值keyframe；采集吞错进ToolResult，拒绝Smash上游删除兜底。文档说明Smash全通道/断输入、match-last全对象删键、子帧shape遍历/负数取整、全局切线无法保证Undo、每拖拽回调独立撤销。
- 普通Python2项、Maya2025隔离7项、临时正式布局注册/面板/Schema与全指纹通过。真实原native tween/world/PosePusher/multiply/Hotkeys/层曲线、真正animLayer与AutoKey补键Undo、快照/明确camera InOut、共享输出/锁/文件引用拒绝、子帧/常量/彩key/rekey、Smash采样/Undo、原回调/注入故障finally、会话profiles/JSON/切线。没有构造真实GUI；界面/生产rig/复杂图 prepared_unverified，完整验收/晋级齐备。
- 收尾额度接口连续两次暂不可读，第三次实际5小时44%/周77%已用，未推测错误为额度耗尽；保存并继续下一项，heartbeat暂停，未用卡/购买/同步/转正。

## 2026-10-01：FD Multi Space完整候选，累计24/109

- 3原Python/RTF 4资源字节保留，Filippo Dattola All Rights Reserved/商业与修改再分发许可说明，私有本地不发布；实际local插组centerPivot与reference既有父级算法，没有文件打开/导出行为。完整两种模式/三步UI与标准create全部步骤/阶段API。
- 显式属性名/driver UUID→weightAlias替代listAttr[-1]/force，同driven的不同driver复用自有多target constraint，保持mo；Owner network/helper标签/message与阶段1/2/3，半成品保存重载/重命名可续跑。引用节点UUID可能与原场景节点重复，增加referenceNode UUID上下文；local拒绝引用重父级，reference默认拒绝引用编辑，明确allow才接受addAttr/约束/reference edits。
- 只读参数/层级/循环/锁/外部驱动/target/权重/来源预检，拒绝重复attr/driver、外部同名图或改接；create整组Undo/Redo、三步各chunk，finally选择按身份/时间/namespace/AutoKey恢复。失败不自动回滚，保留Undo；不添加冒险图删除/自动清理，文档说明插组/整个父级子树/权重归一化与非无跳变算法影响。
- 普通Python2项、Maya2025隔离5项、临时正式布局注册/面板/Schema及全指纹通过：真实值0/1、双target同组同约束/Undo回退、只读/循环/锁/已有驱动、真实引用与共享原UUID场景编辑/Undo、三步改名后加attr保存重载准确alias/外部target拒绝、部分失败finally/Undo。真实GUI/生产rig/scale/复杂引用待人工prepared_unverified，验收/晋级齐备；收尾真实5小时50%/周78%已用，继续下一项，heartbeat暂停、无卡/同步/转正。

## 2026-10-01：Gimbal Lock Fix完整候选，累计25/109

- 原单Python字节保留，完整8方法/原生UI/Quaternion SLERP/角速度区间/采样规则/全曲线spline保留，UI桥标准API与Undo。检测不是奇异性证明、修复不是保证消除万向锁/长转圈，原preserve/create-new/smooth/frame_rate未实现，UI原未连线checkbox禁用，原播放/动画范围标签按实际行为准确说明。
- 修复非XYZ从quat后仅赋order→reorderIt，六种顺序key矩阵保持；Maya API1不存在原angleShortestPath调用，等价归一化绝对点积2acos/clamp最短夹角；SLERP先复制第二quat避免缓存符号污染；getAttr(time)替代切帧，角曲线fallback TA但安全准入已有三轴才允许。
- 只读有限参数/三轴TA/固定order/degree/样本量/锁引用共享曲线保护，层约束与缺轴拒绝；原private写入仅活跃scope，修复finallyAutoKey/时间/选择、局部失败Undo。说明范围外切线也变spline/增加键不保证保留Euler圈数。
- 普通Python2项、Maya2025隔离5项、临时正式布局注册/面板/Schema及指纹通过，六顺序真实key矩阵/Undo、read-only detection/dry/真实区间、子帧密度范围/原UI业务桥、quat缓存/共享锁/order单位拒绝、第二笔写失败Undo-finally；未打开GUI/生产动画视觉待验prepared_unverified，完整文档/验收/晋级齐备。真实收尾5小时54%/周79%已用，继续下一项，无卡/同步/转正。

## 2026-10-01：Universal IK FK Pro完整候选，累计26/109

- Monika Gelbmann Pro3.0/旧版1.10/安装说明3原资源完整字节归档，Pro13全局函数19UI方法/完整窗口/临时RP链/复制控制器/约束/PV投影/offset/左右arm-leg六bend-axis/逐帧AllKeys原业务源码齐备，不发布。原PyMel在本机Maya2025 find_spec为None，不安装外部依赖，不将其算法/GUI标为通过。
- 标准Schema/API、原6个写UI回调/根私有活跃guard、私有helper前缀/UUID范围/只删本次helper后代外部使用者保护/约束detach/shared solver保留，finally时间/选择/namespace/AutoKey；只读scope/reference-edit/锁/曲线共享/有限offset/范围/依赖检查。修复is比较/rotateY空白/multiplyer/IK→FK range硬码/None key列表/Bake取消AutoKey初始化/AllKeys范围，eval变literal_eval。
- Owner transform Store保留原字符串形态并加JSON/message/UUID，更新必须自有+overwrite_store，引用message本次明确允许，改名重载可解析，不删外部同名节点。原.ma/.mb场景Store导入强制删除改为显式自有JSON进出，旧格式不直接互读须备份重定义，记录为明确格式变化而不承诺兼容。文件独占创建/明确覆盖原子写、不得MayaUndo；坏offset不执行代码。
- 普通Python2项、静态全原资源/函数/UI、临时正式布局注册/面板/Schema/指纹通过；Maya2025隔离6项中5项实际通过（metadata/key/switch），完整原匹配1项因PyMel absent明确skip。真实0/1/10切换/key/Undo、Store只读/改名保存重载/更新Undo/外部子保护、JSON覆盖/更新导入/坏数据、消息失败finally/Undo、真实引用metadata明确编辑及同文件UUID上下文通过；不是原匹配或烘焙通过。
- 缺PyMel+真实GUI+制作rig/临时IK链/双向match/bake待验prepared_unverified，完整知识/验收/晋级已备。收尾实际5小时63%/周80%已用，继续下一项；heartbeat暂停，无卡/购买/同步/转正。
## 2026-10-01：JOP Retarget Anim完整候选，累计27/109

- Jesse ONG PHO v09全14函数/3UI方法/6原资源字节保留；许可允许自用商业修改但禁止第三方分享，原安装器不执行。保留稀疏/逐整数帧采样、mult/decompose/quatToEuler目标rotateOrder/减pivot/六轴key/整曲线Euler filter，不键scale、不承诺长圈/复杂scale插值。
- 原空选择mySelec错误修复；去掉import插件加载；冻结分支原DG创建删除改只读API2世界pivot与旋转重构（单位scale），实际与原point/decompose/compose图对照通过。UUID+referenceNode UUID快照支持JSON/改名重载/明确映射，完整UI保存会话cache/回放标准API桥；degree/cm/非实例transform/静态pivot、目标rotateAxis-pivotTranslate零/offsetParentMatrix identity、锁/引用曲线/外部输入/共享/奇异矩阵/范围保护。
- 标准Undo与私有助手身份/外部输出保护，finally清理助手和恢复AutoKey/选择/时间/namespace，插件按需加载可卸载才清理且不属场景Undo。失败不自动局部回滚。动态pivot子通道漏检在首轮测试发现后修复；引用fixture原工作文件自引用未加载改为另名工作场景，真实同UUID/reference上下文检查通过。
- 普通Python2项、隔离Maya2025五组、临时正式布局注册/面板/Schema及指纹通过：六顺序父级变换回放+Undo、只读dry/capture、多控制器dense/frozen原DG等价、JSON/改名保存重载/原UI业务桥/新目标、真实引用保护/明确本地映射、共享/锁/动画pivot/单位/额外旋转/奇异矩阵和第二键故障cleanup-finally/Undo。真人GUI/复杂父级scale/生产rig待验prepared_unverified；完整验收/晋级备齐。
- 实际收尾5小时71%/周82%已用，继续下一项；heartbeat暂停，无卡/购买/Obsidian同步/转正。
## 2026-10-01：Keyframe Overlap完整候选，累计28/109

- DEX3D原6资源/4类31方法完整字节与UI/算法保留，原用户机器检查及placeholder逻辑保留、无独立license私有不发布。隔离原support/安装器下载exec；cfg/APPDATA/presets自动写改完整会话preset流程，持久化变化明确记录。
- 六rotation/position模式、classic particle goal延迟、红editable locator、四组/跟随/结果约束/端点键、回烘焙与线性误差选点优化完整；原变量at未定义查询修复，optimizer按实际帧而非0索引删键，position offset属性修为tx/ty/tz，低fps sampleBy最小1。范围外键与子帧/圈数/质量不承诺。
- 随机私有前缀+owner network/controls-members消息/成员owner，不删外部原前缀/同名图/已有约束；标准API/Undo/privateguard、曲线共享/复合输入/引用锁/外部后代和输出检查，手工编辑helper仅直接本地不共享curve，半成品需Undo。Maya listConnections默认把shape返回transform导致成员漏检，已显式shapes=True；带shape控制器listHistory遗漏TR曲线，补直接曲线连接检查。
- 普通Python2项、Maya2025隔离四组、正式临时布局注册/面板/Schema和匹配指纹全通过；真实六模式粒子/constraint/bake、红locator编辑、10..16优化严格10/13/16、Create Undo/Redo+BakeUndo、同kfo用户物体保留、rename/saveReload、只读dry、锁/共享/外部约束/后代拒绝、注入bake失败AutoKey/evaluation/refresh恢复。非真人GUI、复杂制作rig/动力学视觉和缓存待验prepared_unverified。
- 实际收尾5小时78%/周83%已用，继续下一项；heartbeat暂停，无重置卡/购买/同步/转正。
## 2026-10-01：KF AnimRig IK/FK完整候选，累计29/109

- Kiel Figgins 3.02完整七MEL过程/原匹配与说明UI/4原资源保留，手臂/普通腿/狗腿/高级样条算法与stretch/Pole/右手rotateAxis补偿全分支备齐，未附独立license私有不发布。过程/窗口私有名，错误Ten(0)菜单改无参数，MEL定义延迟至执行，dry/inspect只读。
- Schema/明确引用编辑/同reference node依赖/准确KF命名/degree-cm/Undo/停止播放/锁曲线共享保护，真实MEL写节点与setAttr属性范围guard、delete仅此次新节点及新后代/外部输出保护；暂关AutoKey，finally清新助手、恢复时间/选择/namespace/AutoKey。源rig未提供，不将同名临时fixture当完整原资产验收。
- 原timeline改标准Python范围循环调用完整原match，每帧显式键预检目标，补原AutoKey未键通道；这是行为变化，仍不切pinner/IKFK。新目标动画曲线/自动blend不冒险当垃圾删除，复杂狗腿/样条残留需真人核验。
- 普通Python2项+完整MEL编译与引用手臂2组mayapy+临时正式布局注册/面板/Schema/指纹通过：实际Hand位置/旋转/Pole、单帧/逐帧1/2/3和Undo、dry/引用默认拒绝、AutoKey/时间/选择/助手清理、注入helper属性失败finally/Undo。真实GUI、原rig、反向FK stretch/腿狗腿样条尚未运行，prepared_unverified。
- 顺带按第28项发现的Maya带shape listHistory遗漏TR曲线，补第27项JOP直接曲线连接和compound驱动检查，fixture增加实际curve shape，五组重新通过并刷新全部匹配报告。JOP计数不重复。
- 实际收尾5小时83%/周83%已用，继续下一项；heartbeat暂停，无卡/购买/同步/转正。
## 2026-10-01：Lock to World完整候选，累计30/109

- Jesse ONG PHO v09全部13函数/4UI方法/2原资源完整保留。完整起始世界矩阵/逐整数帧父逆补偿/quat目标order/冻结pivot减法/通道掩码与Start-End-Lock窗口；未附独立license私有不发布。矩阵/identity/plugin/助手支持从审阅JOP候选复制进本payload，无其他staging运行依赖，不提前下沉正式core。
- import插件加载去掉，冻结采样用只读API2；整数范围/degree-cm/唯一transform/静态pivot/额外变换限制/选中通道锁引用共享与compound驱动/奇异矩阵/总量预检。APIattributes与channelBox显式互斥，原UI长名短名正规化，子帧按钮值明确拒绝不截断。原吞异常并误报rotateOrder改真实异常，finally清自有助手/AutoKey/时间/选择/namespace；标准Undo，插件不归sceneUndo，无文件写。
- 普通Python2项、Maya2025隔离3组、临时正式布局注册/面板/Schema/全部指纹通过：六order+动画父级worldMatrix逐帧保持、冻结worldpivot、多控制器无键新目标、只读dry、仅tx时未选ry锁与旋转曲线保持、共享/动态pivot/GUI batch/privatewrite保护、第二键失败真实错误cleanup/finally/Undo。初测锁通道被Maya对象keyframe查询排除，改直接曲线查询避免测试误判。
- 真人GUI/channelBox/引用业务/真实脚底IK接触和复杂scale仍待验prepared_unverified；完整文档/验收/晋级备齐。实际收尾5小时88%/周84%已用，继续下一项，无卡/购买/同步/转正，heartbeat暂停。
## 2026-10-01：Keyframe Reduction完整候选，累计31/109

- Robert Joosten MIT 0.0.1整仓60资源字节归档（Python2原件.py.original而非可执行Py3），MIT/Paper.js归属保留。全12类68方法/完整MVector二维、least-squares/Bezier递归/weighted Wu-Barsky fallback/Newton重参数/三拆分/Qt筛选设置和callback转换Py3，未执行安装器、不写shelf/userSetup。PySide6/2延迟GUI与包内图标、回调清理/空选提示/标准API桥。
- 原全曲线floor(first)..ceil(last)+1 exclusive采样和关键帧/切线写回算法保留；2D几何容差不是最终Maya间帧最大值误差，子帧端点/Infinity可变，明确记录。Auto空/常量/等角log除零修复；cutKey原0.01偏移可能漏近首键改index1..last clear不改clipboard。error严格正，TL/TA/TU本地单输出/普通时间/非step、引用锁共享/层/驱动拒绝，采样预算及curve UUID写scope；Undo+AutoKey finally，失败需Undo。
- 普通Python2项、Maya2025隔离3组、临时正式布局注册/面板/Schema与指纹通过：直线/常量20→2且1..20半帧值保持/Undo、Auto常量、只读dry/inspect、原类标准桥、共享/step/private写拒绝、weighted Existing/threshold波形流程与不减键分支、第二fit-key故障Auto/Undo恢复。首测误把原首帧前constant Infinity当线性外推，测试修为原键范围，未改业务算法。
- 未创建真实Qt GUI、制作曲线插值质量未验，prepared_unverified，完整知识/验收/晋级备齐；现有正式库/core未发现同类Bezier完整拟合，不提前下沉。实际收尾5小时93%/周85%已用；无卡/购买/同步/转正，heartbeat仍暂停，提交后重读额度决定续跑。

## 2026-10-01：31项后额度等待检查点

- Keyframe Reduction候选完整提交8f61c8df89c4dd274d9af4d5430d3834e5e780df；提交后一次读数5小时94%已用，后续实际读数96%已用/周86%已用（5小时剩余4%）。已低于6%阈值，保存31/109完整候选后结束整理回合。
- 下一项maya_timeline_marker仅阅读原源码，未写候选、未运行原UI、不计完成，保留working供恢复。进入waiting_for_quota，启用同聊天30分钟heartbeat；续跑必须重新扫描/核验额度与单写者。
- 不消费重置卡、不购买额度，未同步Obsidian、未迁入正式库；真人Maya验收仍待进行。

## 2026-10-01：自然刷新续跑与Timeline Marker完整候选，累计32/109

- 续跑检查初读5小时98%已用/周86%已用，核验同聊天ACTIVE heartbeat等待。刷新时间后一次额度接口读取失败，重试实际5小时0%已用/周86%已用、ordinaryUsageAllowed=true，未推测刷新；无其他写入、工作树干净，暂停同一heartbeat后恢复，未用卡。
- Robert Joosten 2.0.2整仓49资源与GPL-3.0-or-later Copyright(C)2015/GPLv3全文字节保留；两类26方法/13原函数全Python3转换，完整原生覆层/右键菜单/RGB/注释/tooltip/选区移动/原命令和hotkey，GUI延迟PySide6/2。原Python2归档.py.original，不执行MEL安装器/userSetup，也不安装hotkeys。
- Maya2025隔离探针确认fileInfo不入Undo；候选保留timelineMarkers三数组JSON格式，私有MPxCommand保存精确原值或缺失状态、真实Undo/Redo；插件只在正式写时加载且不autoload、不在有Undo记录时卸载。修MEL转义串完整解码、读/paint/update不写、set长度严格、范围移动冻结源数据避免目标碰撞删待移动源，保留int向零截断/后源覆盖目标语义。API数据写入不要求GUI已装，这是原行为变化。
- 标准Schema/只读预检/Undo、恶劣原metadata保留拒绝、整数/颜色/数据量保护。保存并链旧MEL press/release，清理只恢复仍属自身的hook并保留后来外部handler；自有菜单/4API callbacks包含Undo/Redo只读刷新，原版仍运行拒绝重叠；会话GUI/插件不属场景Undo。
- 普通Python3项、Maya2025隔离4组、临时正式布局注册/面板/Schema、静态与全部指纹匹配通过：真实fileInfo/精确Undo/Redo、中文引号路径换行、原格式、ma/mb临时保存重开、全部命令桥、dry/inspect无副作用、坏数据/Undo关闭拒绝、命令后注入故障Undo恢复。hook所有权测试timeControl是shim、API callbacks是真实注册/Undo事件；未构造Qt GUI，绝不当时间轴验收。
- 首轮自有API2插件误用MArgList.length，修为len后全部四组通过；不是原算法通过证明。真人Qt覆层/tooltip/拖动/高DPI/声音/其他插件共存仍待验prepared_unverified，完整知识/验收/晋级已备；正式库/core/同步未动。本项实际收尾5小时6%/周87%已用，继续下一项mov_playblast_v11，heartbeat保持暂停。

## 2026-10-01：多相机MOV拍屏完整候选，累计33/109

- 原v11.1全43类方法/7函数、主UTF8/alt GB18030两个原Python与bat共3资源字节保留；原始自动开UI/拖放安装器不执行，私有窗口/设置窗口、完整单多相机/当前view/正交/音频/缩放/增序/覆盖/MP4/GIF/几拍一UI。未附独立license，只本地不发布。
- 参数化API保持高JPG→MOV/低QT-H264两路径与原libx264/yuv420p/MP4 crf23-AAC/GIF-lanczos；负帧排序，hold取每组首帧、末尾补齐原语义；源图片只读复制，自有完整序列修原hold残留图像导致帧数计算混乱。QT明确不支持hold，音频显式有效性检查、节点offset-start+手工偏移，高低均送FFmpeg（低手工偏移原未生效，记录行为改变）；奇数尺寸pad、相机UUID清洗后缀也明确记录。
- 全输出组MOV/MP4/GIF预检覆盖/增序，临时目录解析父级验证/所有权登记、同卷hardlink原子无覆盖创建或显式覆盖并核对签名再replace；FFmpeg shell=False/隐藏窗口/超时/返回码/error完整，坏图像转码不会误认旧目标为成功。finally逐项尝试恢复panel camera/时间/选择/AutoKey、清自有临时目录；已发布前相机遇后续失败不会删，ToolResult.fail.data列出部分文件，文件不能MayaUndo。
- 原Documents自动settings读写改会话+明确JSON进出，UI保存提示本次会话、导出/导入按钮，刷新不reload旧v9；打开输出仅已有目录。内部原capture/rename/cleanup helpers保留但仅标准事务自有目录允许，不能通过kwargs访问外部目录；标准capture用参数化完整流水线。未写Documents/shelf/userSetup/正式库、未装依赖。
- 本机真实FFmpeg6.1可用。普通Python3项、Maya2025隔离4组、临时正式布局注册/面板/Schema及全部指纹通过：真实JPEG/音频生成、MOV逐帧PNG验证hold首帧重复与尾补齐、MP4/GIF/audio输出、坏JPEG真实FFmpeg非零保持旧目标、JSON覆盖/进出、dry无文件/scene写入、真实camera/audio/time/selection配合高/低拍屏shim、第二相机失败部分文件报告与finally。modelPanel/playblast是明确shim，不宣称viewport/Qt图像或声音同步实测。
- 真实GUI/viewport/本机QuickTime codec/生产相机和音画品质仍待验prepared_unverified；完整知识/验收/晋级齐备。实际收尾5小时14%/周88%已用，继续下一项overslapper_v1_03；heartbeat暂停，无用卡/购买/同步/转正。

## 2026-10-01：Overslapper完整候选，累计34/109

- Philippe Ratté 1.0.3完整9原资源字节归档、原20页PDF与EULA/图标/default JSON保留。完整28业务函数、2 QObject worker、原UI56方法+部分导入4方法，私有相对导入/懒GUI，无shelf/userScripts安装。限制性EULA包括不得复制/修改/再分发，明确保留，不推定授权、不发布。
- 原旋转24主上轴/六order/距离/忽略自身位移、平移frame lag、分组1-stiffness/strength、cycle/移除父级、layer、过冲stable zone/峰谷decay、风曲线/路径完整保留。修平移add拼写误删所有键、无关move清未选轴、风正逆matrix别名、上轴norm误用target、zero strength未缩放、单个无child索引、过冲int/string末区/零间距/end绝对帧重复加start。
- 标准Schema/read-only preflight/Undo/UUID写scope，本地transform/所选channel/driver/锁/共享/引用边界，显式layer/noResolve原始层值与findCurveForPlug cut/scale，其他层/base保持，新增chosen attrs仅、finally恢复时间/选择/AutoKey/namespace及原layer旗标。异常不自动回滚，标准一次Undo恢复。深namespace风查询去重/明确winds、fresh曲线私有名和接线，不覆盖已有对象。
- 原完整JSON八组/部分导入保留，先整体验证，补frame_lag/wind strength往返；JSON覆盖/取消/原子临时文件保护与文件不能Undo说明。原pratte_custom_var改私有会话gradient，关闭清理，仍明示Maya偏好保存可能写私有var；slider同步blockSignals避免负数/小数文字被范围回写。原UI不再关闭别人的chunk/cursor，Maya BaseMixin.show真实本地签名核对用无参show，未冒充Qt验收。
- 普通Python3组、Maya2025隔离6组、临时正式布局注册/面板/Schema/全指纹通过：纯父平移解析预期/additive外键/未选轴/zero/cycle/UndoRedo、六旋转order与无child、30点风/三级namespace/正逆分离/开关Undo/两模式wind/移除父级、layer保护与deleteall/scale/flag恢复、第二键故障finally/Undo/constraint/共享未选轴拒绝、临时JSON与真实过冲。UI负数同步用假控件运行原回调，只导入类不构造Qt，未当GUI实测。首轮纯平移断言fixture带父旋转，隔离掉旋转后按解析结果通过，未为测试改业务算法。
- PDF原文提取与相关页6..20渲染核对功能，临时PNG已在验证workspace绝对路径后清理。真人GUI/渐变/部分预设/生产rig/layer合成/运动品质仍待验prepared_unverified；完整知识/验收/晋级齐备。实际收尾5小时32%/周91%已用，继续physics_tools；heartbeat暂停，无卡/购买/Obsidian同步/转正。

## 2026-10-01：Physics Tools完整候选，累计35/109

- IURI MONTEIRO / modified by k31，PhysicsTools_v1.8.mel完整307004bytes/7314行原资源字节归档；109个完整原MEL过程、319行原生主UI与五段内嵌Python保留，无独立许可，只本地不发布。源码索引和全改动diff、完整知识、验收及晋级payload已备，不执行原自动入口。
- 标准Schema/BaseMayaTool/只读预检/Undo/private MEL wrapper+Native guard、私有助手namespace/UUID+network metadata归属、受控删除/缓存；显式reference edits复选；目标命名UUIDleaf、绝对API DAG/namespace/layer旗标恢复、多选择越界保护、空集合访问修复。取消冗余Connection Editor/Goal UI镜像保留真实particle/goal算法；Jiggle用实际同类原生node，避开项目规则/隐藏cache路径修改。原createHair/follicle等完整保留待真人检查。
- 隔离运行发现legacy particle删除会连带删控制器，补自有约束先清/临时目标lock恢复/单节点删除；完整bulk-delete曾90秒卡住，修改DAG根优先、跳过已删除节点后全部通过。未以失败假装通过，最终报告匹配当前所有Python/资源指纹。删除拒绝外部child/外部输出（默认shading membership例外），cleanup也删除本会话烘焙层/曲线，文档明确不能用来保留结果。
- CacheMe只在明确已有父目录建立owner子目录/.mcj，运行全局diskCache时暂禁可写外部enable并finally恢复；Clear只删登记自有文件，未改项目规则/他人cache；文件不可Undo。原噪声/循环全函数通过私有dict和范围代理运行，不污染__main__，噪声显式通道/自有新层/恢复random state。finally恢复原时间/选择/AutoKey/ns/playback/refresh/layer flags，原交互editor/tool/selectMode效果另列。
- 普通Python2组、Maya2025隔离6组、临时正式布局注册/面板/Schema/全指纹通过：109定义编译、private guard、dry/inspect零改动；locator/ns/UndoRedo；真实particle预览/烘焙/完整cleanup/Undo且原控制器存活锁恢复；原循环和noise；真实jiggle+diskCache+.mcj创建删除及注入故障finally；外部child/driver/lock拒绝。没有构造主UI，没有实测全部hair/advanced/multi/localspace/runtime-command/生产rig或运动品质，prepared_unverified。
- 实际收尾5小时55%/周94%已用、ordinaryUsageAllowed=true，继续pose_matcher；同heartbeat暂停，不用卡/购买/同步/转正。

## 2026-10-01：Pose Matcher完整候选，累计36/109

- 原55函数/49691bytes/PoseMatcher.py字节归档、完整骨架对齐与NumPy网格合并/拆分两套业务和原cmds UI保留；无独立作者/license声明，只本地整理不发布。源码索引/full AST差异、完整知识/验收/晋级payload齐备。
- 骨架原JO/RA/parent delta/rot order矩阵和同父去重/twist逻辑保留；补零向量/acos范围/缺joint与parent先查/重复basename/有效写父scope、实例/ref/lock/driver/scale/shear拒绝，reorder使用Euler自身；部分错误ToolResult如实反馈。UI私有名、双表按row删除/sync finally、reset回调参数、deep namespace、Save Map显式保存，对齐不再隐式写map。
- 网格修vertex-normal数组和face-normal index错配、face偏移用face数、UV先copy且U平移修V上界/相同起点漏处理；保持round/intersect1d首匹配/原顶点/UV/normal/face流程。新Info format2+merged_faces，split核对拓扑再用map_v位置和当前face-corner normals，原UV恢复；旧无证明Info拒绝，未当成法线能猜对的格式。
- private MPxCommand/MFnMeshData+MDagModifier/cachedInMesh实现真实mesh Undo/Redo。初版inMesh在无history mesh再求值后无几何，改cachedInMesh后通过；官方MeshData/polyPrimitiveCmd文档只作primary参考，无复制其实现/代码。几何保留.ma保存重开；返回单名规范化；only真实写时plugin加载，不autoload/不卸带Undo插件，正式路径加载需重启Maya。
- 输出OBJ/JSON同父临时目录→hardlink不覆盖或明确replace+旧SHA保护，部分发布实际written_files列出；finally选择/time/AutoKey/refresh/ns恢复、自有progress cleanup，取消不返回半数组。创建独立Lambert/SG、源mesh/材质/skin不迁移，位置/法线+保拓扑编辑可split，UV/skin/history/材质不在往返契约。
- 普通Python2组、Maya2025隔离4组、临时正式布局注册/面板/Schema/全指纹通过：readonly/dry/overlaps、原向量和UV/输入不变；六order实际对齐/Undo/lock；硬边cube merge/.ma保存重开/split点UVface法线完全匹配/UndoRedo；新旧mapJSON/覆盖拒绝、before-publication及after-geometry注入失败原文件保持/finally/Undo。未造GUI、未用生产JO/RA/twist/skin或复杂模型；prepared_unverified。
- 实际收尾5小时66%/周96%已用、ordinaryUsageAllowed=true，继续pose_transfer_remote；heartbeat保持暂停，不用卡/购买/Obsidian同步/转正。

## 2026-10-01：Pose Transfer完整候选，累计37/109

- 原9方法/完整自动手动1..5步+cleanup UI，两原资源字节保留，无独立license声明，只本地不发布。实际原行为是locator world matrix/ROOT平移offset写回原controllers；Readme称跨模型但源码不含重映射，知识/Schema明确不自动跨模型或处理ROOT旋转scale差异。
- 标准API/Schema/readonly/Undo，scene network保存ROOT/controllers/locator/shape UUID和orig path/上次ROOT position/完整flag，每次操作重读，不依赖Python缓存；deep namespace与leaf特征/ROOT范围ControlSet/filter，明确手选范围可在ROOT树外，父先子后应用；全T/R/S/shear可写要求，ref edit显式API/GUI复选。
- 保留完整原matrix/locator方法，修helper带DAG非法名、重复shift累计offset（成功后更新上次ROOTpos）、创建后立即tracking及partial flag、marker skipSelect、rename后UUID校对路径、控制器删除仍可cleanup。只删自有helper/shape，外部child/output和锁/driver/tamper/metadata异常拒绝；finally时间/选择/AutoKey/ns恢复，UI关闭不删scene session，窗口高550容纳按钮。
- 普通Python2组、Maya2025隔离5组、临时正式布局注册/面板/Schema/全指纹通过：dry/detect set范围/private guard/Undo无改动；capture/shift重复delta0/apply世界位置旋转/UndoRedo/ma保存重开/cleanup Undo后shift；外部child/locked scale/目标attr被改拒绝；第二helper xform注入失败partial flag/finally/Undo；UUID rename后apply和目标被删后的cleanup。原UI/production pivots/scale/shear/OPM/ref edits未实测prepared_unverified，文档/验收/晋级齐备。
- 实际收尾5小时73%/周97%已用、ordinaryUsageAllowed=true，继续下一个pending单元；heartbeat暂停，不用卡/购买/Obsidian同步/转正。检查点helper去掉已过时的Timeline Marker resume_note，实际current_tool/source_commit/log才是恢复依据。

## 2026-10-01：Retime Tools完整候选，累计38/109

- 原28文件/32类211方法/38历史MEL过程完整携带。raw Python归档.py.original，完整native.py原UI与方法保留；Core/Shuffle/Lookup/State/Color全类提取headless engine。所有原图、7z、空Plugin.py、安装/Qt/license资源字节校验；未安装Shelf或第三方依赖。主文件只依赖Qt，原可选LicenseManager版本模块/UXFramework缺失如实列出，原许可代码/trial flag不改不模拟，未给独立再分发许可只本地整理。
- 标准Schema/API/readonly validate/dry/ToolResult/Undo、finally selection/time/ns/autokey；原Qt写回调同API，创建原全部多shape控制器、连接、启停/offline/reset/invert、bake、shuffle/clean、rename、明确单个旧controller升级与ASCII/JSON IO。拒ref/lock/其他warp/shared warp animation curve/外部输出与子项/层及约束输出；子集只connect/disconnect/clean，bake/shuffle/state整controller预检。
- 完整原逆查找辅助方法保留，API用原分段样本相邻插值去重和warp斜率，修错误同端点/邻接方向/零帧被跳过；shuffle merge避免insert移动已粘贴时间，Infinity属性直接读取恢复（原query在实际Maya返回None）、失败不装通过、临时curve finally清理；负帧floor(t+.5)取整、invert包含末帧、bake单curve输出查询；断开和delete先恢复time.outTime避免冻结。逆操作拒hold/nonmonotonic无唯一逆，原bake preserveOutsideKeys=False影响明确。
- 原导入/导出菜单是禁用占位，保留事实而API提供完整显式文件数据流程/元数据，不依赖缺失MEL全局。现有目录temp→hardlink不覆盖/明确overwrite原子replace，外部文件不Undo。key clipboard改变同原算法不等于scene Undo可还原。
- 历史MEL完整私有过程/UI/全局变量，不自动呼出；修缺失animscratch Python桥。保留calculator/velocity/旧迭代连接/字符集/旧shuffle/bake/进度完整算法，历史回调单独人工Maya验收，不能等同受Python预检API或无人值守场景写入口。
- 普通Python2组、隔离Maya2025五组与临时正式布局注册/面板/Schema/全指纹通过：dry undo/time/selection不变、原完整create/connect/enable/disable/Undo；正负零帧shuffle/时间恢复/临时清理/deleteUndo；锁/外部child/hold拒绝/私有writer guard；ASCII/JSON预检不写/不覆盖/导入导出/bake及Qt类import不造Widget；38 MEL定义编译无scene变动。真实Qt按钮/旧MEL回调/生产rig/加权非线性/跨版本仍not_run，prepared_unverified。未晋级/Obsidian同步/用卡/购买。

### 本轮等待额度检查点

- 第38项提交 cf5328047aa667e7a422fd35b45fc80cfc9f3fe2；实际额度接口5小时87%已用/周100%已用（ordinaryUsageAllowed仍true，周百分比已到100则停止新工具）。不使用任何重置卡，不购买额度。
- 下一项01_animation/root_motion_bake仅已阅读原完整脚本，尚无第39项候选变更；恢复先读manifest/Git/usage。原相对位置是世界位置/Euler相减，并非矩阵相对变换；存在默认删除同名offset layer/烘焙全部keyable属性/框选实际用了animation range/同名namespace首匹配等边界，下一轮需保留全算法并补安全检查。
- 保存状态waiting_for_quota，恢复同聊天30分钟heartbeat；只有周额度允许、5小时剩余高于95%、无其他运行回合时续跑。不消费卡、不转正、不同步Obsidian。

## 2026-10-01：额度恢复续跑与Root Motion完整候选，累计39/109

- 开工实际额度5小时1%已用/周0%已用，ordinaryUsageAllowed=true；卡片可用数3而此前4，仅观察账号外部变化，不归因本聊天（本聊天没有consume调用/购买）。App thread list当前checkout只有本聊天active，另一额度问询systemError无整理writer。已暂停同聊天heartbeat并核验TOML PAUSED，动态重扫109/109入口/34路径修复，恢复working；新resume_run.py只接受实际>95%剩余/周允许/已暂停heartbeat，不启动第二writer。
- Root Motion原13方法/UI全部保留，raw字节SHA归档。完整center point/orient skip+maintainOffset→原全keyable bakeResults参数→ring偏移层；相对语义明确是世界平移/Euler分量，不改成matrix算法或跳过层。
- 默认全部center先world采样为独立自有locator，避免center在Root下约束循环；snapshot_center=False保留独立源直接约束。私有窗口，无顶层自动启动；GUI原扫描/执行/范围定义可追溯，bridge用整批API/真实框选/可无ring，fullnamespace和歧义不首匹配/RootX_M不误作Root。
- 全组readonly preflight/ref/lock/noneditable drivers/shared animCurve输出/Root重复祖先交叠/后代ring和direct后代center检查；原bake全部keyable与preserveOutsideKeys=False影响明确。层unique UUID不覆盖旧层、临时约束/locator/parentOnly副本UUID追踪，仅自有清理，外部DAG后代拒删；finally旧layers flags/time/select/ns/autokey恢复，会话总释放，失败已写场景按一Undo恢复。
- actual ring实测源两xform后动画求值回到base，末帧偏移没保存；在无驱动parentOnly副本上执行原完整world/Euler相对方法，Maya求相同parent/pivot/RO局部值后显式在新animLayer写T/R，原起止整Rootkey保留。真实末帧tx3/tz2及Undo通过，无层源bake和rotation/已有Rootkeys/UndoRedo也通过，未用删掉偏移层的缩减代替。
- 普通Python2组/隔离Maya2025六组/临时正式布局注册面板及全部指纹通过；干跑scene/time/Undo无变、全约束+bake+层保存、原同名层/flags不动、dependent snapshot、第二坏组前置拒绝、注入bake失败清理、深ns歧义/范围/batchUI拒绝。原GUI、生产pivot/JO/RA/RO/非均匀scale/层输入/时间滑块交互仍not_run，prepared_unverified，真人验收资料与晋级清单完整。不转正、不Obsidian同步、不用卡。

## 2026-10-01：Shape Animation与Shift Animation完整候选，累计41/109

- 补录已提交候选的恢复记录：Shape Animation提交68307035724f860c50a1525814d1d37f1d396794；Shift Animation提交4c0ae1edb394d980d15f2b727d3da914e2e9191b。manifest、各项检查报告与Git实际内容为依据。Shape原39文件/六版本/34方法完整携带；完整成对blendShape正负目标、关键帧曲线、原雕刻/Reset算法、UUID会话和显式安全旧会话采纳；普通Python2组、隔离Maya8组及临时正式布局通过，GUI与生产场景仍not_run。
- Shift原六个文件、130声明/129唯一MEL过程及20全局完整未改字节保留。附带许可要求商业购买、禁止分发或修改原代码；未购买/发布。独立Python/UI适配保留MATCH/路径/圆形/root-motion/曲线控制完整MEL，原自定义属性清除有明确allow_attribute_cleanup。实际Maya批处理缺交互层/时间滑块功能如实拒绝，没有模拟该功能。普通Python2组、隔离Maya5组、临时布局通过，曲线双系统独立删除/UndoRedo/失败恢复已测，完整交互功能待验收。
- Shape单元.gitattributes加入后改变源树指纹，第一次scan重置其完成状态；在Shift提交中已重新scan→record并修正Shape实际提交号。后续按先scan再record顺序维护完整性。当前活动回合收尾实际额度5小时38%/周6%已用，heartbeat保持PAUSED，继续Spring Magic；不重复套用新回合95%启动门槛。

## 2026-10-01：Spring Magic 3.5a完整候选，累计42/109

- 完整46源文件保留原字节SHA，四份UI、全部icons与history/操作说明均携带；原Python2入口/开发reload助手留档.py.original。native保留core37、springMath17、utility6、UI39、decorator10函数；数值碰撞math AST完全不变，原inertia/wind/twist/tension/extend/aim/bake/capsule/controlBind主要算法AST逐项对比通过。
- 本机Maya2025缺PyMel，完整SpringMagic引擎、几何/绑定/GUI未执行，明确prepared_unverified；没有安装依赖或提供伪造PyMel替代。Python3相对import/next/urllib/unicode，完整引擎按需加载；状态可在缺依赖时读取。Base/Schema/readonly validate/dry/ToolResult/Undo、正X无分支链和范围/写权限/共享驱动检查齐备。
- 所有持久碰撞资源与代理采用session UUID网络；计算临时helper确定性仅清理本次新建UUID，不做全场景SpringNull通配符清理或GC隐式删除。完整原控制器绑定，Bake控制器按UUID找源而非名字拆分。取消/异常部分key需整组Undo，failed状态阻止未Undo的后续写入；finally恢复时间/选择/namespace/autokey、等待光标及progressbar。
- 原普通模式cutKey所有keyable通道影响明确，API默认拒绝，allow_key_cleanup=True或GUI确认才执行；原GoToBindPose连接层级影响显式allow。原Floor/Subs无引擎实现，保留但禁用；Straight源缺失函数明确补为joint.rotate置零待实测。UI语言直接XML读取，不覆盖资源；图标本包绝对路径；打开不再自动访问旧版本站，明确网站按钮保留，Shelf仅用户点击才改UI偏好。
- 普通Python4组通过；实际隔离Maya5组中4组通过、完整引擎1组因PyMel缺失skip，分别验证依赖拒绝/无节点时间Undo写入、UUID改名及外部child拒删/Undo、失败环境恢复、batch进度finally/返回值；真实GUI=false。临时正式布局4组及注册/面板通过。全物理动态范围仍109；本项非Maya/缺依赖结果不能当真实求解通过，不转正/不同步Obsidian/不用卡不购买。

## 2026-10-01：Stagger GUI完整候选，累计43/109

- 原12文件全部字节SHA归档，八SVG/原Demo GIF/三页安装PDF完整携带；PDF技能只读提取说明（PDF解析有wrong-pointing-object警告但三页文本可读），实际原入口import stagger.ui; stagger.ui.win()与头部stagger.ui()不符，框架入口已补齐。Animation Creation/2022署名保留，无独立许可仅本地整理。
- 完整原边界插键/首键值比较/每2帧偏移与正常值交替采样/奇数end-.5/末端ease与整数帧写入，不切掉旧内部键、不缩减原算法、不误当物体错时。原五GUI函数、原图形高度随slider和start/end时间滑块按钮完整保留，私有控件名，执行API桥，finally恢复进度/窗口高度；真实GUI与SVG未验收。
- 原无对象参数query容易受全局键选择影响，候选直接从指定对象图查curve，拒锁/引用/范围外共享/timeWarp/animBlend等不支持图。Maya2025实际拒keyframe(query,animation='objects')，已改直接listConnections；普通时间curve有隐式time输入无connection，保留支持并拒真正warp。
- 普通Python2组/隔离Maya3组通过：完整原函数仅固定GUI数值读取而全部实际动画命令Maya执行，偶/奇/最小/负帧结果逐键等同；dry node/key/undo/time/select无变，无关selected key隔离，UndoRedo；常量仍只边界插键，共享/锁target拒绝。临时正式布局注册/面板/Schema通过；非线性加权生产曲线/真实UI另需验收，prepared_unverified，不转正/同步/用卡/购买。

## 2026-10-01：减选关键帧偏移完整候选，累计44/109

- 单次/批量两个原入口字节SHA完整留档，原自动窗口只archive，正式候选同时提供两工作方式；once=0/offset/offset，batch=0/offset/2offset/...，不丢减选循环语义。原ls(dag=True)隐式后代展开现明确只用ordered whole nodes，省略objects时ls selection列表并注明tracking未启用不能保证点击顺序。
- 原逐时间写入可能dense key碰撞、重复时间多次移动，改整curve relative timeChange/option over一次平移，保留全部键值/数量；共享同delta去重，不同delta/影响首个不动或外部对象拒绝。拒引用/锁/驱动键/timeWarp/层与不支持图；整批预检无节点/键/时间/选择/Undo写入，run整Undo组；API默认保持选择，GUI显式update_selection保留原减选与选键输出。
- 原字段范围/精度/step和两按钮完整私有UI，无外部依赖/文件写入。普通Python2组、隔离Maya4组、临时晋级布局注册面板全部通过：密集邻帧batch正/负与once小数的每键时间/值/数量及UndoRedo；dry/后项锁整批无先写；共享curve冲突或同delta仅一次；once余对象和batch末对象/keys选择。真实UI/生产加权切线/跨版本仍not_run，prepared_unverified。不转正/同步/用卡/购买。

## 2026-10-01：Sword Anim Polishing完整候选，累计45/109

- 原9文件57MEL声明/56唯一过程/21非内建全局及四帮助/installer/BMP/许可完整原字节保留。Barnev Pavel商业内部使用/不可修改分发约束明确，独立Python适配不改原引擎，不购买发布。独立接口覆盖Parent In/Aim/Sword/Reverse/Arc/Bake/Layer/Euler、全部快捷选择/帮助/删除/MT Update/VP/原约束权重；原完整UI仍可显式备份对照，不与候选同时运行，原UI会设置matrixNodes autoload本次未调用。
- begin原SomethingSelected scriptJob仅取消本次新建的SW回调，改明确finish_setup执行原完整结束过程，Top/Side非共线+UUID预检；不修改原回调或用假camera/timeline。所有原代理joint/约束/bake/path/cluster/nearestPoint/uValue完整算法保留。普通预检不sourceMEL/不建节点，拒锁/引用/实例/短名歧义/共享driver，bake后的本系统删前拒外部child/输出；保留baked animation graph，pairBlend baked input1接回后删helper，完整交互清理须实测。
- Parent In在真实mayapy报MEL运行错，probe分步定位原SW_6de locator屏幕尺寸函数依赖模型panel；Parent In/setup/完整Arc明确要求交互环境，不删函数来绕过。原Euler前10帧临时零键/全旋转winding影响明确，非Arc全局键选择临时清除并恢复，sourceBake内catch不能当生产正确性证明。
- 原SW_7 native motionPath打开Undo却不关闭；Maya实际query chunkName只返最外层不适合猜深度。实际MCommandMessage命令callback可见原MEL内部undoInfo，适配记录本同步调用未配对open、finally只闭其自身，保持Base外层Undo；原源码未改。native完整逐帧uValue/temporary nearPoint+decompose清理、成功及真实missing_curve失败后的外层一次Undo通过。
- finally恢复range/time/select/keyselect/ns/autokey/units/eval/track/optionVars/cache/Move/refresh/timeline；Arc旧motionTrail.nodeState按UUID恢复，MT Update外部trail拒绝。MELglobals存网络+UUID映射避免Undo/reopen/rename陈旧缓存，failed须Undo后续才写。自身元数据网络和新helper加owner。
- 普通Python2组/隔离Maya5组/临时正式布局注册面板通过：56完整过程source零scene/UI/Undo写入；原完整Bake/Euler+UndoRedo；原逆距/零距weights；锁/interactive拒绝与rename-global恢复；native motionPath完整抽样/Undo平衡成功及失败。真实UI/完整Arc/Parent/Aim/Sword/Reverse/cleanup/layers/productionrig仍not_run，prepared_unverified，不转正/Obsidian同步/用卡/购买。

## 2026-10-01：TB Anim Tools 完整候选，累计46/109

- 原安装器与四帮助GIF五原文件SHA完整留档；原安装器仅下载main、没有主体。已从原引用上游固定到eb8ede026c61f3cf5e38bafbc709d3bbed4d90c1，完整286ZIP条目/2759177bytes、SHA256 290cc3ff67d81347037b3b6d011547b76bd2bdf158e5c27c93c3f74b2a2758d9原样携带，包含所有apps/Icons/plugins/appData/proApps/样式/LICENSE，不裁减或解锁付费内容。
- 原11类方法、style/圆角/拖动/Escape/路径字段完整UI移植，修Qt6/Py3.12/distutils/不依赖PyMel/父窗口懒求值、窗口flag/QColor/globalPosition。原自动下载并覆盖启动改为离线固定ZIP安装、显式模块注册、显式原版整套启动三个按钮；版本写入改独立精确commit收据，不覆盖upstream版本文件。原LGPL版权完整留在UI及原件；上游GPL LICENSE完整保留，不对不同组件擅改许可。
- SHA与每文件完整性、ZIP越界/链接/ADS/设备名/大小写别名/路径冲突/压缩炸弹防护；绝对新目录/已有parent/拒junction与symlink/任何已有安装拒覆盖，Windows临时同级解包后rename发布，失败只清理本次临时目录。validate/dry_run不建目录/注册/导入vendor/联网。register仅新建模块、明确外部影响确认、tbUpdateType=2禁用自动上游更新；launch仅交互Maya和本候选完整资源/模块，拒同名已载入模块，调用完整原版installer，无真实用户profile安装或原套件启动。
- 普通Python4组与实际隔离Maya2025两组通过，验证全部文件一致、异常发布清理/已有目录保护、只读scene/optionVars、临时module注册与foreign保护、batch native启动拒绝。临时正式布局注册/面板通过，生产库未改；GUI/原版延迟启动/各项动画功能/可选插件仍not_run，prepared_unverified。无Obsidian同步/用卡/购买。

## 2026-10-01：时间轴方块基础/增强版完整候选，累计47/109

- 三原文件完整SHA保留，完整basic15/enhanced46类方法、两个布局、原中文说明携带；源说明引用缺失example/hotkey文件未伪造。明确方块是规划数据，不是场景key；原源未有场景动画重定时，不错误承诺。
- 全纯document API覆盖六色类型、添加/属性/选中/拖拽移动/复制粘贴/范围/删除/清空/JSON，返回新state不原地改输入。完整嵌套Schema与独立validate，深复制clipboard、相对时距和超显示范围裁剪保留；拒已有block覆盖、move同帧安全、selected移动映射/隐藏方块保留。文件4MiB/重复键/帧/色范围预检，绝对路径且拒junction/symlink，新建不覆盖，显式替换先完整旧字节backup再临时替换/并发哈希保护；没有package配置自动读取或源目录写入。
- 全原UI经Bridge接API，修rowLayout columnWidth8/实际9控件、属性margin、refresh parent、私有属性窗名；原模式/fit/reset仅提示，现在实现，并保留默认拖拽。窗口内Qt5/6 shortcuts与100份document UndoRedo，不注册全局Maya热键；scene Undo不代替内存历史/外部文件/播放状态。sync整数负帧range只读，显式setCurrentFrame/play/stop，batch播放拒绝。
- 普通Python4组、实际隔离Maya2025三组、临时正式布局注册面板全部通过；直接提取原完整copy/paste方法只固定UI frame读取，与candidate相对时距/裁剪结果一致；全61方法AST存在，原件SHA一致。实际scene key/selection/时间/Undo dry不变、临时文件backup/坏load保护、negative sync/小数拒绝、native全类导入和纯构造零窗口、batch show/play拒绝验证；全部GUI/焦点/滚动/播放not_run，prepared_unverified。不转正/同步/用卡/购买。

## 2026-10-01：Tweener 1.0.2完整候选，累计48/109

- 全27原文件/SHA/GPL LICENSE/14图标/135套件类函数声明完整携带，Py3私有相对包/Qt5/6移植，不裁减五模式/原层选择/Bézier切线/键数据/MPx Undo/UI/dragger/keyhammer。原installer会网络下载/删旧安装/覆盖module/autoload/Shelf，仅完整archive不运行；框架直接完整自有privateplugin，不需要安装用户目录。
- 七个完整数值函数AST只把iteritems换items，与原一致。原BaseUndoChunk不能记录API2，保留完整MPxCommand/MAnimCurveChange undoIt/redoIt，把private stagingTweener等四命令纳入Basechunk。readonly validate不prepare/插键/注册plugin/UI；显式curve/objects/time_range/indices、wholeDag/锁引用/唯一输出/共享外部/层lock/timeWarp预检，源层best-layer/default真实API单位保留，帧在键范围外不安全插入拒绝。
- 原live先关闭Undo命令创建cache现改原引擎直接preview、release登记同一cache一次；取消/关闭/换模式/异常/finalize回滚未登记cache、busy finally/仅移本窗口idlecallback，UUID输出/锁guard；外部API不能打断preview。原拖拽150px/overshoot与idle节流完整保留，修press拖动位置沿用旧值。GUI构造/实际idle/mouse未执行，不冒充通过。
- 原keyhammer完整逐curve预计算evaluate后add，修range endIndex漏末帧、selected时间仅来自scope，取消API change回滚、progress finally，batch不建UI。tick原颜色不保证Undo明确；原UI完整toolbar/presets/饼图/dock/偏好/Qt资源，修Py3/Qt6绘制及重复父layout；预设label更新但callback旧值不一致，改当前fraction且仅Between映射，signed模式不二次变换；Shelf显式函数指向完整候选，不自动建Shelf/热键/autoload。
- 普通Python2组、实际隔离Maya2025六组、临时正式布局注册面板通过。五模式实际value/UndoRedo、未有键插入/撤销、range/连续选键组、keyhammer并集闭区间/外部选键不借用、锁/共享/whole对象解析、actual MAnimCurveChange preview多步取消/提交与UndoRedo、注入keyhammer真实取消rollback均通过。真实简单选中animationLayer解析与Base键不变/Undo、旋转默认插值degree/API单位也通过。两次测试自身错误（Maya实际创建shared1，animLayer curve query返回list）已修为实际返回值，最终报告6passed。
- 全GUI/idle/window close/mouse/weighted/nonlinear/production层仍not_run，prepared_unverified；现候选完整可晋级，不转正/Obsidian同步/用卡/购买。
