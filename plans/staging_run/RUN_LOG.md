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

## 2026-10-01：速度计算器完整候选，累计49/109

- 原单文件四功能/两按钮与完整距离表达式SHA/AST保留；修原average读current当start/start当end并留时间在end的实际错误，使用MDGContext直接求真start/end worldMatrix。不改timeline、scene keys/selection/Undo，无helper/文件写入；按MDagPath.instanceNumber正确查询实例，引用/锁仅可读不解锁。
- 完整average endpoint距离/秒及instant backward sample_step差分，结构化单/多对象world位置/向量/标量/units/duration/quantity，默认选择首项和两按钮源语义保留。MTime所有Maya time单位到秒、MDistance内部cm到UI距离单位，不只支持原四fps。正时长/finite/wholetransform/歧义/别名/范围/showResult-batch预检；往返位移0不误称沿路径平均速率。
- 普通Python2组、实际隔离Maya2025三组和临时正式布局注册panel通过：current9测真1..5结果24cm/s、半帧instant24、不动scene/Undo；父动画film24/ntscf60/120fps与m转换1.2m/s/秒单位、实例另一父分支48cm/s；往返0、零时长/属性/batch消息/GUI拒绝。Maya2025 asMObject(context)发DeprecationWarning，实测读取正确，兼容/未来API复验限制如实记录；GUI/production模拟与缓存未验收，prepared_unverified。无转正/同步/用卡/购买。

## 2026-10-01：额度断点，完整候选仍为49/109

- 恢复后实际账号读数：5小时已用96%（剩余4%）、周已用15%（剩余85%）；ordinaryUsageAllowed=true。额度低于停工阈值，未消费任何重置卡，未购买额度。
- 当前第50项01_animation/w_retarget_tool仅有四个初步候选模块，engine/UI/文档/测试/晋级包仍未完成。保存release_candidate/RESUME.md及全部现有文件，不计入candidate_complete，不声称通过Maya或候选验证；原始入口未改动。
- 已通过App工具把同聊天heartbeat恢复为ACTIVE，并由enter_quota_wait.py读取本机TOML确认，manifest.execution进入waiting_for_quota。下一轮满足5小时剩余>95%、周额度允许且无其他整理回合后，暂停heartbeat，从该部分候选继续。
- 修复等待记录脚本：部分候选断点不再误写成完成工具边界，额度备注不再固定声称周用量100%。

## 2026-10-01 20:33：修复 heartbeat 中文指令编码

- 本次触发实时读数：5小时已用97%、周已用15%；manifest仍waiting_for_quota，49/109完整候选，W Retarget Tool断点未变，不开启整理回合。
- 上次读取automation.toml时通过终端输出未转义中文，输出编码造成name/prompt乱码并被写回自动化。本次使用用户原始中文指令通过App工具恢复同一automation的名称及完整prompt，保留ACTIVE、30分钟周期和原target_thread_id。
- 修复后读取本机UTF-8 TOML，以ensure_ascii=True输出JSON并解析，对完整prompt、名称与ACTIVE状态作精确比对通过。后续终端转交中文配置均使用ASCII转义JSON或显式UTF-8，不再把乱码写回。
- 未修改候选或正式库、未使用重置卡、未购买额度；继续等待既定开工条件。

## 2026-10-01 21:03：自动续跑及 W Retarget Tool 完整候选，累计50/109

- heartbeat读取实际5小时已用0%、周已用15%，manifest等待且线程列表无其他本仓库运行回合；暂停同一heartbeat并验证本机配置，恢复第50项。实时重扫109物理/目录记录/有效入口，路径修复34项，无新增漏项。不用卡、不购买、不执行Obsidian同步。
- 全Walter Delgado原始单文件字节归档/SHA/作者保留，全部18类方法、帮助/关于和四行UI完整保留。业务提取完整五组/父层约束/multMatrix/decomposeMatrix/九通道逐帧算法，保留pose-offset、exclusive end、代理scale通常1。已有目标曲线采用显式key值，原静默异常改明确失败；长DAG名字用UUID辅助名，逐帧矩阵泄漏修为只清理本次UUID节点。
- 全批目标锁/引用/通道/共享/timewarp/层/实例/源目标依赖先读预检；独立目标单Undo，恢复time/selection/autokey，失败可能留部分键可Undo，不冒充自动事务回滚。GUI完整按钮通过run，修方法被control覆盖、空选择/取消dialog/无效区间/CopyAll半行；Clear按原行为只清八字段。FBX显式新文件、namespace去重、明确节点、独占输出及临时文件，七项设置和selection恢复，不自动装插件/覆盖旧文件。
- 普通Python两组、隔离Maya2025五组、临时正式布局/注册panel全部通过。真姿态10/12/14、九通道/结束不采样、parent长路径已有键保留、整批锁预检无部分写、真实注入写入失败清理/恢复/Undo、共享/timewarp拒绝、实际临时FBX导出/七设置恢复/不覆盖通过。全GUI/复杂生产绑定/FBX重导入未实测，prepared_unverified，完整包在staging，不提前转正。

## 2026-10-01：Base OverRig 9.0完整候选，累计51/109

- 原Barnev Pavel许可禁止修改/再分发且商业用途需购买；全部10文件原字节SHA保留，包括368204字节MEL、安装脚本、两个PDF手册、两个图标、热键说明及Jiggle_Bone_New.mb。不修改或抽取改写原引擎，不安装Shelf/userSetup/热键、不购买或发布。
- 词法审查原源码仅过程声明，308声明/307独立过程/一个重复声明保留，完整原主/子窗口和所有业务保留。外围57公共过程typed API及完整schema/catalog，不允许任意MEL或直接内部过程；inspect/validate/dry只读资源/签名/输入/锁/引用/源冲突预检，明确有序scope，尺寸周期/模式/布尔/IK数目与source/knots集合删除范围保护。
- 原source/MEL名保持不变，所有同名过程已有来源检查，资源misc路径随候选/正式位置自动绑定。统一UndoChunk、原生嵌套跟踪，恢复调用者time/selection/namespace/autokey/unit/evaluation/refresh/选择偏好/options/autoload/cache/slider；有目的的时间/选择保留。原GUI及callback仍按原逻辑，不夸大普通Undo对scriptJobs/scriptNodes/插件/prefs/disable-Undo motionTrail的范围，也不把catch吞错当成功。
- 普通Python2组、真实隔离Maya2025五组通过：完整307过程加载不创建scene/UI，不动timeline/selection/Undo；原locator scale1.5/UndoRedo与环境恢复、原姿态loc位置4/旋转30/Undo、真正blendParent清理/其他对象和userNote保留/Undo、dry/锁/真实GUI依赖batch拒绝。初次自有wrapper timerX赋值遗漏反引号已修复后重跑通过，未改原源。
- 临时正式布局检查先因探针硬编码animation拒绝rigging；已修探针按真实domain检查注册/筛选/Schema/panel，后续类别同用。原GUI zxy radio写6可疑行为如实待验收，不改受限源。完整交付prepared_unverified，GUI/生产绑定/IK/烘焙/物理/overlap pending，不提前转正/同步。

## 2026-10-01：批量绑骨头/生成代理完整候选，累计52/109

- 两份完整用户原型SHA/原始三代理函数/三UI方法保留。旧PyMel脚本同一selected两次无法配对，改明确joint/mesh pairs与两次UI独立列表捕获；Maya cmds一骨骼一mesh，不需缺失PyMel，不替代weights_copy，复用core只读mesh/skin查询与框架Undo。
- 原joint/locator/cube无offset跟随和ISS/GOS集保留；原skinning按base名误找已有骨骼改记录实际创建后缀。完整原三函数移植：真bake含末帧、删本次代理constraint、在start冻结源并删除ALL source keys、显式新skinCluster。source删除需要明确allow_source_key_removal，未绑定polygon/静态unit scale+zero shear/无驱动父层/无共享或锁timecurve/无目标父子，全批预检，不强断驱动或覆写现skin。
- 普通Python两组、真隔离Maya2025四组、临时正式布局/domain/schema/panel通过：两mesh各唯一influence/weight1/UndoRedo；三模式actual suffix/pose/既有set成员不改/constraint跟随/Undo；真skinning实际后缀joint键0/2/4/6、末帧、constraint已移、原keys全删、world vertex末帧位置等于原动画、Undo完整场景/区间外及custom键恢复；全批已有skin拒绝/父子拒绝/scale key拒绝。恢复selection/time/autokey/namespace，没有文件/偏好安装写入；异常仍须Undo部分修改。
- 完整候选prepared_unverified，GUI/生产动画/pivot/模拟/版本待真实验收，不转正/Obsidian同步/用卡/购买。

- 追加区间外/custom键回归时，首次Undo节点列表对比因Maya恢复节点的枚举顺序变化失败；报告及manifest如实保存failed，随后将节点集合对比排序（选择次序仍严格比较）再跑。业务未丢节点，键恢复仍独立逐值验证，最终报告四组通过；原失败提交可追溯。

## 2026-10-01：BB Tools 完整候选，累计53/109

- 原81文件/9,349,220字节完整SHA归档，31活动MEL的297原过程全部保留、顶层JB PerVert界面另包入口；重复根目录旧版本/Installer/独立重复FixError helpers归档，不安装Shelf/userSetup。完整图标/QC docx/ADV三ma/XML资源齐备；保留各作者与CGTOOLKIT版权，无公开再分发许可推断。
- 完整原主面板与全部子界面/业务保留。过程/回调前缀避免同名覆盖，明确活动版本与UTF-8 Unicode loader、随包路径。隔离Maya source曾因本机代码页损坏UTF8字符串失败，改Python mel.eval传Unicode，全套编译后通过；加载不启动原UI。typed全部global过程API、无副作用inspect/dry、六项隔离验证batch子集、其他交互原过程需明确全场景范围且拒绝batch假跑。
- XML转权重临时文件改每次owned子目录，不写随包文件；QC配置只准固定UI数据，拒绝任意MEL/Python、不覆盖/全文件导入前检查；FTM完整Copy/Move/Set算法保留，限定解析复制搬移/mkdir无shell、独占创建/校验后移除源；原FixError无条件删userSetup改明确所选文件隔离恢复副本，场景感染节点另可Undo按钮、Outliner去PyMel依赖。
- 五组普通Python与四组真实隔离Maya2025通过：完整81资源/31活动定义/所有原过程入口、原16种真实曲线/UndoRedo、真实颜色/属性限制/编号/蒙皮influence查询、锁/名称保护/交互拒绝；文件复制移动/拒绝覆盖/拒绝shell/删除范围、QC数据注入拒绝。临时正式布局/真实rigging domain/注册/Schema/panel通过，fingerprint匹配。
- API恢复time/selection UUID/namespace/autokey，外部文件/GUI callback/optionVars不宣称Undo覆盖，原全场景连接/删除/引用逻辑须备份场景验收。完整交付prepared_unverified，GUI/QC往返/ADV/FBX/动态链/权重/纹理/感染样本/原全部按钮not_run。未触真实Maya GUI、正式库、Obsidian、用卡或购买。

## 2026-10-01：约束管理v6/重建约束完整候选，累计54/109

- 两份原型完整SHA归档，原4UI类/所有方法和辅助8函数保留；明确Qt6/Qt5、去自动启动。完整原列表/模式/颜色/tooltip/选择/右键/静止位置/修改轴/重建辅助界面由API桥接所有写回调。实际alias+targetMatrix+物理index匹配、保持targets顺序，不按W拆名字/误认userDefined浮点为权重。
- 原已有动画setAttr后隐式打键改显式value、全批锁/驱动/共享timecurve预检。原删除式断开只存权重改实际输出边UUID保存/断开/恢复，原节点、动画、offset/skip/custom全留；新driver不强覆盖，原pairBlend仍流向原child同通道才能恢复；快照JSON不执行代码/任意接线/按名字删除。逆向节点有本次ownerUUID标记。
- 原所谓反向两分支实际仍同方向已纠正：原child驱动每个原target，先断原输出防双向环，拒绝DAG相关/已有驱动/矩阵/上游child依赖；恢复只删本次inverse并接回原边，不宣称把原动画自动bake到逆向。重建duplicate(inputConnections)再接全部原outputs/delete旧，所有属性/输入曲线/target offset/interp保留、actual名UUID更新、一次Undo回原。
- 列表notes改JSON保护长DAG分隔符/颜色，可读旧格式，新名拒绝覆写；辅助完整四动作callable回调+显式snapshot新文件读写，原固定TEMP JSON不自动调用。真实本机Autodesk菜单脚本阅读后纠正原axis把maintainOffset当version、连driver也处理的问题，限定child且所有同child约束显式包括，rest/axis只交互Maya待验收。
- 普通Python2组、真隔离Maya2025六组、临时正式布局/domain/schema/panel通过：namespaced含W目标/alias顺序；三mode与custom实值/现curve显式key/Undo/全批锁拒绝/空UI scope不误删scene selection；原UUID/动画/偏移/输出恢复、新driver保护；真正两目标inverse及运动/owner/恢复/Undo；真实rebuild完整custom/interp/offset/inputcurve与Undo；移除exacttarget保持偏移/scene JSON颜色/导出导入拒绝覆写/伪造destination拒绝无scene/session变化；真实pairBlend原动画仍保留。
- 完整交付prepared_unverified，原所有GUI/右键/颜色/列表往返/native rest-axis/更多约束类型/生产复杂图待真实Maya。无正式库/Obsidian写入，无用卡或购买。

## 2026-10-01：层级/约束影响分析完整候选，累计55/109

- 完整原七函数、结果窗口与source SHA归档，保留六分析函数入口；输入与graph统一long DAG/UUID、实际constraint parent/targetMatrix、source->child方向，geometry补入，原不正确的“约束覆盖全部DAG parent”假定移除，保守保留父边/零weight潜在边。
- 选择间接影响穿过未选中介，稳定输入顺序Kahn分层、严格所有边层级验证、迭代SCC/1500链不递归，cycles及下游blocked单独unresolved，不把环剩余节点伪排成正常层。全局闭包与直接/投影边都有预算、未知约束警告不冒充完整验证；明确structural potential graph不是Maya DG/evaluation证明。
- 普通Python4组、真实隔离Maya2025四组、临时正式布局/domain/schema/panel通过：namespace与真重复leaf长路径/原始state零变化；真point constraints正确方向/未选hidden中介/保留父边、严格verify；geometry driver+joint祖先；真双point结构环valid=false/no fake layers，budget/alias/instance拒绝。初次重复leaf夹具误拿ambiguous列表第一项和shape-instance误当transform-instance的断言已改为准确夹具后复验。
- 实例检查发现对精确fullPath调用cmds.ls(allPaths)仍可能只返该路径；改用API2 MDagPath.getAllPathsTo，新增真实多parent transform实例回归。同样纠正53 BB/54约束管理的输入实例guard，原其他检查和正式布局完整重跑均通过，manifest fingerprint更新。未改原prototype或正式库。
- 完整交付prepared_unverified，真实结果GUI/生产复杂图/十种native constraint更多情形/多版本待集中验收。只读分析不写scene/time/select/Undo/namespace/UI/file，只有显式show_ui开原结果窗；不提前转正/同步/用卡/购买。
# 2026-10-01：Joint Optimal Pro 4.1完整候选，累计56/109

- 六份原资源/MEL/PDF/License/图标/安装器逐字节SHA保留；144声明、143独立原过程、142原签名typed API与完整原GUI，system find仅归档不调用，不安装/购买/发布。
- 独立适配全类型/vector/matrix、有序whole输入/锁引用/真实多父DAG保护、半径/颜色RGB/驱动/strict limit语义预检；其他原scope须显式同意与interactive Maya。API恢复time/UUID选择/namespace/autokey/选择偏好/mirror optionVars，框架Undo+nested chunk保护；原GUI/runtime globals/catchQuiet边界明确。
- 初次Windows source在321行唯一CP1251字母被本机CP936误读，Unterminated string失败报告保留；完整原字节在内存decode CP1251→Unicode mel.eval后全部143过程编译，无修改源码。第二次仅fixture残留实例选择失败，修正fixture明确选择后四组真实Maya2025+两组普通Python+临时正式布局全部通过，候选fingerprint匹配；不冒充GUI实测。
- 同步修正第51项OverRig原allPaths(fullPath)实例误判，改API2 MDagPath.getAllPathsTo，新增真实多父DAG检查；其五组隔离Maya/两组普通Python/晋级布局及重记录均通过。
- GUI、组件、链增删/朝向/镜像/烘焙/生产rig与其他版本not_run，prepared_unverified。实际额度已用5h59%、周25%，继续第57项；heartbeat保持暂停，未迁正式库/同步Obsidian/用卡或购买。
# 2026-10-01：RdM Tools v2完整候选，累计57/109

- 原164文件/86 Python模块/126函数/3界面类与全部方法完整SHA归档，native全Python3/Qt6→Qt5兼容，全部主UI/Picker/图标/MEL/PDF/docx资源随包。EULA源链接本轮不可访问，保留出处无公开许可推断，不运行installer/不写用户RmdTools_Path。
- 将原import-time创建/删除/场景查询/示例完整保留为显式run_script，保留原常量重置/顺序与显式main界面动作；GUI reload改定义加载后显式原动作。私有namespace import/随包paths/defaultparent构造时读取，原AddRemoveJoints语法+漏mel修正留原件；完整普通函数/脚本API、JSON签名/明确scope/真实DAG实例/锁驱动/命名/空选择防全场景、原mode名字删除保护。
- 74原模块在真实隔离Maya2025import不改scene/环境，12模块因PyMel或pyside2uic延后；PyMel缺失明确失败，无stub/GUI模拟。两组普通Python+七组真实Maya通过：全部11原曲线模式位置/Undo、Box显式创建/UndoRedo、原颜色/骨骼轴/dry/scope、RootAuto/Offset真实分组/Undo、全场景曲线JSON重复不累积/不覆盖、实例/锁/空scope。初次fixture source→实际source1修正，完整import曾发现scene变量表达式误判常量，改仅字面量/Qt别名后所有复跑通过。
- 原CurveToJson/UItoPY硬编码输出改明确绝对独占新文件/明确.ui输入，保留原算法、文件不受Undo，Maya权重GUI对话框留待临时目录验收；原未随包提供RdMTools Legacy/旧Picker图片/开发模板列明，不假造补齐资产。临时正式布局/注册/rigging域/Schema/panel与fingerprint匹配。
- 完整Qt/PyMel/AutoRig/Facial/skin/IKFK/生产及跨版本not_run，prepared_unverified。实际额度5h已用69%、周26%，继续第58项；heartbeat暂停，不迁正式库/Obsidian/用卡/购买。
# 2026-10-02：Relationship Tools v19完整候选，累计58/109

- 原50方法/完整布局/源码历史SHA保留，去自动窗口；全部原mark/foot/ani/world pose/one-more/align/layer流程有完整API与GUI路由，不做假的batch UI。
- 原全场景suffix删除改ownership/role/message来源，完整mark形状/约束/动画曲线一并owned；外来名称/子节点/外部驱动/锁引用保护，UUID缓存取代共用系统temp，独占显式JSON导出/限大小/有限三坐标/原UUID整体预检导入。
- 统一[start,end)，MarkAni不多一帧；先step采样、保留end-1，不cut旧对象键/禁用TR/scale/custom/范围外键，key-only空范围no-op；保留原六次世界pose/层级算法并检查收敛。避免写入者移动自己的mark driver或Align下面目标，真实实例/普通独立time动画输入/锁引用检查。新override层只加入所选TR、不异常重复执行，旧preferred/selected恢复。
- 两组普通Python+五组真实隔离Maya2025通过：父移动mark/step/Undo与owned删除/Undo/外来suffix保留、Foot/MarkAni真实curve exclusive键、UUID改名世界pose/采样/未选属性与外键保留/JSON独占NaN拒绝、Align空key-only/单帧/多帧新layer真实数值+Undo、外来节点/锁/实例/GUI拒绝。锁定mark的transform keyframe查询返回None，改查询其真实连接animCurve证实实际键，未伪造通过。临时正式布局/rigging/注册/Schema/panel与fingerprint通过。
- API最终恢复time/UUID selection/namespace/autokey/evaluation/refresh原暂停状态；GUI成功step保留+1，失败不advance。文件与Python缓存不承诺Undo，真实GUI/生产rig/复杂layer/跨版本not_run，prepared_unverified。实际5h已用77%、周27%，继续第59项，heartbeat暂停；不迁正式库/同步/用卡/购买。

# 2026-10-02：ReParent Pro 1.5.1 完整候选，累计59/109

- 完整原13 MEL过程、完整原UI、图标原SHA归档；候选隔离过程/全局变量/UI/临时名/动态辅助suffix，全部default/Pin/manual start-go-cancel/relative/freeze/IK/local/locator-size与最终bake-delete API及按钮路由、Schema、文档、验收、注册晋级备齐。
- 修正全部反向bake时间字符串；保留原清全部六TR键行为（包括范围外），强制明确allow_clear_animation。foreign reserved名称、原有约束/锁/引用/真DAG实例/共享或非time动画保护，IK首控缺父/共线零长拒绝；原layer菜单业务从未读取，候选只给最终bake实现override层，明确标注。
- 自有owner/会话控制UUID记录，清理前复核set成员/外部后代/下游连接；最终bake替换原全场景suffix通配符删除，只清自有辅助、保留控制器烘焙结果曲线及pairBlend上游动画网络并解除辅助归属。原TempLocator等保留。Pin临时约束不存在导致原delete报错已修正。
- 两组Python、六组Maya2025隔离测试、临时正式布局注册/rigging域/Schema/panel/fingerprint全部通过：全13过程无副作用编译、default实际逐帧运动/首尾bake/清键ack/dry/两次Undo还原外键、Pin/manualGo偏移/Cancel/relative实际运动、IK弯曲三控制器真实handle/最终bake后旋转一致、外来成员/子节点拒绝、最终override层保留/Undo。Maya2025 implicit-time animCurve无input连接，改允许隐式time但仍拒绝非time驱动。
- 真实GUI/生产manual pivot/freeze/IK/local/高级动画层/其它版本not_run，prepared_unverified。实际额度5h已用88%、周29%，继续第60项；heartbeat暂停，不同步/迁正式/用卡/购买。

# 2026-10-02：Segment Scale Fix完整候选，累计60/109

- 原Python/MEL两个同功能脚本完整SHA归档；完整所选joint segmentScaleCompensate关闭操作、explicit scope/只读预检/Schema/Undo/真实Maya小UI/文档/验收/注册晋级齐备。省略objects沿用原所选joint筛选，不递归；已关闭节点no-op，输出UUID/前后值/未变计数。
- 两组Python、三组Maya2025隔离检查、临时正式布局注册/rigging域/panel/fingerprint全部通过：父缩放2时子joint真实世界矩阵scale变化、scope不影响祖孙、单步Undo恢复；锁属性/驱动/别名重复/真DAG实例/空范围拒绝；混选只joint/显式transform拒绝/重复预检no-op、GUI batch拒绝。
- core当前仅context/maya_utils/logger/string/ui，没有等价joint属性scope业务；使用框架现有Undo，不新改core。真实GUI/生产skin rig外观/其它版本not_run，prepared_unverified。实际5h已用90%、周29%，继续第61项，heartbeat暂停，不同步/迁正式/用卡/购买。

# 2026-10-02：Skin Info / Super Connect / Timal完整候选，累计61/109

- 原7文件完整SHA归档；SkinInfo1.92/1.7全26过程、SuperConnect全7过程、Timal全4类方法/原布局/图标/installer均保留，installer不执行。原完整四GUI入口与所有业务按钮路由安全API，原unsafe legacy算法审计保留但公开接口不调用，去顶层UI/文件写入。
- 完整info/weighted/select-influences/lock/unlock、XML/JSON/批量export-import/Timal后normalize与新旧skin、transfer/copy/prune及全9direct轴/parent/point/orient/point-orient/prefix/MO。TXT只解析安全joint名，不执行原eval；绝对既有目录、安全basename、独占批量预留输出/no覆盖/出错只清新文件，含meta拓扑指纹，旧图显式allow_unchecked_topology。已有锁/驱动/真实DAG实例/重复匹配/自身和层级依赖scope保护，delete history和direct换连接显式ack。
- 两组Python+五组Maya2025隔离+临时正式布局注册/rigging域/panel/fingerprint全部通过：全部33原MEL/全UI定义无副作用编译、XML/JSON实权重往返及导入Undo恢复、Timal新skin/XML后normalize、transfer新skin真实weights及Undo/copy/info/weighted选择、liw/恶意TXT拒绝/错拓扑、direct全轴namespace/prefix真实motion与四约束/Undo。fixture中创建新mesh改变选择，改比较import调用前真实selection，未改业务掩盖失败。
- 原deformerWeights不依赖其跨版本Undo保证，现有skin捕获原/导入权重后API复原再经skinPercent回放，单Undo实际测试通过；导出文件不属于MayaUndo。无许可文件，不推断发布权限。真实GUI/生产skin/拓扑姿态/历史删除/跨版本not_run，prepared_unverified。
- 收尾实际5h已用96%（剩4%）、周30%，低于6%阈值；保存提交和检查点后启用同聊天30分钟heartbeat并结束本轮。动态清单第一未完成项为skeleton_generator（不是按聊天记忆猜测的skin_magic），下轮先处理该项。所有候选留池、不同步/迁正式/用卡/购买。

- 额度等待转换已验证：App heartbeat ACTIVE，manifest waiting_for_quota，61/109，下一项02_rigging_hierarchy/skeleton_generator；第61项提交8f9b7fd49478045c825a1cbe5e6890b314c81ed3，真实GUI仍not_run。只有实时5小时剩余>95%、周额度允许、没有其它整理回合时才能暂停heartbeat恢复工作。

# 2026-10-02：新额度回合恢复，Skeleton Generator 完整候选，累计62/109

- heartbeat首次额度读失败，重读成功：5h已用1%、周31%、ordinaryUsageAllowed true。App线程列表显示当前checkout无其它active writer；同聊天heartbeat暂停已验证，resume_run进入working，实时目录109项双向对账无新增或缺项，不用卡/不购买。
- 原选区生成骨骼链完整函数/原SHA保留，去自动执行。完整joint/locator所选森林，原joint-first/direct-selected-parent边界、world TR不复制scale、joint radius/drawStyle、选择新骨架保留；改迭代深树、目标namespace/后缀名碰撞整体预检、UUID映射、select_result可恢复选择，原namespace/autokey恢复。
- 两组Python+三组Maya2025隔离+临时正式布局/rigging域/注册/Schema/panel/fingerprint通过：混选三节点实际世界位置/quaternion/层级/radius/drawStyle/单位scale、未选tip不创建、dry全scene/selection/time/undo不变、单Undo删除全部新骨架；缺选中中间父生成两个世界根/有namespace源/调用者autokey与namespace及selection恢复、冲突/别名/真DAG实例/空scope拒绝。namespaceInfo当前返回caller而非:caller，fixture改比较调用前实际值，不伪造业务变化。
- 真实GUI/生产混合缩放rig/跨版本not_run，prepared_unverified。实际5h已用4%、周31%，继续skin_magic，heartbeat保持暂停；不迁正式/同步/用卡/购买。

# 2026-10-02：SkinMagic 4.0 完整候选，累计63/109

- 250原函数定义、完整41文件（4语言UI/原图标/安装说明）逐字节SHA归档，原目录不变；私有Python3完整业务运行时无自动UI/场景/网络。101控件回调逐语言改callable绑定，不污染__main__，资源绝对作者路径改候选路径；完整原权重/LoD/Rename/Misc/BS/BBF算法、Gore补充窗口，缺失Spring算法/控件明确保留报错，不虚构实现。
- Base/ToolResult/Schema全部UI业务命令和cmds批量inspect/set/export/import；只读scope包含选区/缓存/历史/skin/LoD删除相关连接，已有引用/锁/实例/影响/alias冲突拒绝。原连续Undo改目标权重快照恢复/明确临时网格删除；去全场景annotation/unusedshader/未知后缀代理和别名目标删除；PyMel缺失不装stub，真实GUI待验收。使用框架Undo、不改core/正式库。
- 权重与LoD pickle改64MiB安全JSON、独占输出，旧pickle明确拒绝；XML私有临时目录、实体/影响/顶点数/点值保护，原deformerWeights后API复原再skinPercent回放实现可撤销；保留原GUI导出2位精度，cmds批量完整精度。恢复选优先级/影响锁/AutoKey/time/isolate/源BS，原颜色代理按UUID清理/显示复原。
- 5组Python+4组Maya2025隔离+临时正式布局注册/rigging域/panel/fingerprint通过：完整原字节/函数/UI/图标闭包，安全数据/恶意pickle与XML实体拒绝，真实skin指定顶点/未选顶点/no-write dry/单Undo；JSON导出不覆盖/导入Undo、XML实际weight与Undo/无holdernode，锁/错范围/实例/GUI依赖拒绝。完整PyMel、真实GUI、生产LoD/Gore/Wrap/代理及跨版本not_run；prepared_unverified，非假通过。
- 收尾实时5h已用18%（剩82%）、周33%（剩67%），立即继续skin_weight_transfer；heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：骨骼权重转移完整候选，累计64/109

- 原15函数与单文件SHA完整归档，原字节不改。完整源->目标->多mesh->DelSkin有序行、源关节已连skin自动发现、merge/normalize/remove-influence、载入选择/多行列表/UI执行+预检、Base/ToolResult/Schema/知识/测试/晋级全部备齐。
- 精确UUID/DAG匹配拒绝歧义shortname、自身、重复shape/transform别名、缺影响、锁/引用/实例、多skin/多geometry/驱动数据/maintainMaxInfluences/DQ。全部任务预检模拟删除影响，坏后行不让前行偷偷写。API批量读保留，不可Undo的API写改逐顶点cmds写完整归一化与原removeInfluence，顺序读实际前行权重，完整单Undo。
- 3组离线+4组Maya2025隔离+临时正式布局/注册/rigging/panel/fingerprint全部通过：真实全顶点0/.5/.5/dry场景选择时间Undo不变/oneUndo；源连接自动发现、A->B移除A后B->C最终C=1、Undo恢复影响与原权重；非归一化.8/.4/.8->0/.6/.4及Undo原值；全表错误/已删除影响/自身/alias/锁/实例/GUIbatch拒绝。发现误用了命令flag名skinMethod作属性，修正真实skinningMethod后全部通过，未掩盖错误。
- core get_skin_cluster/正式weights_copy是不同作用域，复用框架Undo、不改core。GUI/生产大网格性能/其它版本not_run；prepared_unverified。实际5h22%已用、周34%，继续camera_f_fix，heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：按F相机重置完整候选，累计65/109

- 原完整MEL/SHA字节归档，不自动source。完整默认persp/ResetTransformations/局部T=(1,1,1)保留；读取本机Maya2025已安装performResetTransformations.mel确认底层makeIdentity -apply false及偏好参数，仅查看、不复制Autodesk脚本。默认R/S使用原Maya偏好，API可显式override，偏好不写入；原选相机默认保持，preserve_selection扩展可选。
- 完整Base/Schema/Undo/只读preflight/相机字段+预检+执行UI/文档/验收/晋级。拒绝非perspective、锁/引用/驱动/关键帧/歧义/真DAG实例/child-transform rig，恢复AutoKey，只改相机本地变换，不宣称修复shape/焦距/裁切或实际F视口异常。
- 2组Python+3组Maya2025隔离+临时正式布局/注册/modeling_surfacing域/panel/fingerprint全部通过：真实执行原MEL与候选TRS/selection一致、dry所有状态不变/oneUndo原姿态与selection；偏好全部关闭R/S保持与显式override、shape参数/AutoKey/偏好保持；错误目标/orthographic/锁/keyframe/rigchild/实例/GUIbatch拒绝。fixture 15度实际浮点为14.999999999999998，改比较操作前真实值，不改业务伪造通过。
- 真实F framing/GUI/生产父级camera/其它版本not_run，prepared_unverified。实际5h26%已用、周35%，继续cvwrap_weightdriver；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：cvWrap / weightDriver / mGear完整套件，累计66/109

- 全部532文件、363 Python模块、4614函数/类、80UI和全部模板/图片字节SHA归档；保留完整上游业务，转换两个Py2 cvWrap模块、Qt6/2兼容、SDK reload、QInputDialog取消处理、明确29菜单SVG占位补图。源缺三原生插件二进制与本机PyMel，如实记录，不虚构变形器。
- 统一Base/Schema/read-only预检，完整cvWrap创建/rebind/paint/绑定IO、weightDriver全MEL编辑器/AE、mGear RBF与全部family菜单；显式受保护命名空间/插件加载/AE模板，去startup自动defer，已有mGear菜单不替换。绑定独占输出，RBF preset不覆盖，gSkin禁止任意pickle对象执行；上游其它GUI按钮影响逐项说明，真实场景/文件使用备份验收。
- 4离线+2Maya2025隔离+临时完整晋级布局/注册/modeling_surfacing/panel/fingerprint全通过；MEL四脚本真实source、只读依赖预检场景/选区/时间/Undo/插件/path不变。原生算法/完整PyMel和GUI not_run，prepared_unverified。额度首次读取失败，重读实际5h39%已用、周37%，立即继续WorldSpaceTools；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：WorldSpaceTools完整源码套件，累计67/109

- 全174文件/114模块/336定义原字节SHA归档；完整legacy source原类/方法/四页UI与world/parent/local/IK/path/COG/gimbal/copy保留，全provided Hub/source/字体/图像/preset保留。Beta多个Python分支共缺370专用模块、本机Python3.11不支持，原许可模块不更改，不伪造Core或算法，开放准确beta_root合法环境入口并记录not_run。
- Base/Schema/read-only scope/Undo及44原写方法和业务入口经标准回调；真实UUID新建节点owner，helper/source metadata存UUID，重命名继续，foreign child/外部连接拒绝清理，不靠suffix全局删除。原多目标复制只采样最后目标修正，字符串special tick遍历修正，fullpath basename/skipRotate变量修正；原空copy占位不当真实实现。
- 用户AppDir自动prefs改session+显式JSON独占输出，eval改literal_eval；去全局pane/isolate/长期chunks，finally恢复time/selection/AutoKey/namespace/animBlendingOpt。原clipboard/buffer/tangent影响明确，不假称全局可Undo。
- 2离线+4隔离Maya2025+临时正式布局/注册/animation/panel/fingerprint通过。实际world/parent/local动画值/keytime/dry与Undo、原对象重命名UUID回烘；多目标copy/paths/逐帧1..5，共享curve/foreign child/实例/锁/错scope/Beta和GUIbatch拒绝。修正Maya属性通配漏owned DAG导致清理拒绝，按实际UUID节点查owner后通过，不伪造fixture。
- GUI/生产IK/pathLocator/COG/gimbal/Beta与跨版本not_run，prepared_unverified。实际5h47%已用、周38%，立即继续FCM Hider；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：FCM Hider完整候选，累计68/109

- shelf TXT完整1309行Py2业务转私有Py3，原57文件/54PNG/58定义SHA归档；完整9成员集合、All/settings、紧凑UI及所有右键/shape/面/visibility/镜像/选择/锁/检查/帮助/联系保留。三帮助图片原缺，提供文字帮助、不伪造原图；原安装器不执行，不写shelf/usericons。
- Base/Schema/只读scope/Undo；私有mtbFCM namespace与逐节点owner，异源collision/失效成员/引用/锁/驱动/真实例拒绝。全部UI固定源回调callable/private、不污染__main__。任意外部Pythonexec集合改严格JSON独占输出，legacy .py拒绝。全scene unlock/show/delete改成员/全覆盖layer/确切owned系统范围，foreignchild/aggregateforeign/consumer拒绝清理。
- 原All WIP接现有完整全部显示；namespace非幂等/clear短名查询、r_左模式、空ls(None)全场景风险修复。面hide只指定原成员，去修改最后面fallback；face镜像改局部X唯一顶点/拓扑映射，全表预检；原UI选择mask/color/clipboard外部状态及partial失败Undo说明明确。
- 2离线+4隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint通过，真实membership/visibility/隐藏face/dry/单Undo、mirror命名/JSON往返/不覆盖、无关网格unlock保持、collision/foreignchild/锁/GUIbatch拒绝。实际面镜像/完整GUI/生产rig和跨版本not_run，prepared_unverified。
- 实际5h55%已用、周39%，立即继续GPU Cache to Mesh；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：GPU缓存转实体完整候选，累计69/109

- 原完整单文件SHA归档，完整每cache文件AbcImport/reparent/hide行为，全部路径/父级/shapeUUID/引用/锁/真DAG实例/overlap预检，自包含私有namespace与holder，不筛cacheGeomPath、不删原cache，不写输入文件。完整API/Schema/UI/文档/验收/注册晋级。
- 实际发现Maya2025原AbcImport Undo留下AlembicNode；复制/直接删除临时DG方案导致隔离进程3221225477，撤回该方案。最终自包含MPxCommand拥有native导入生命周期，临时child记录关闭且保留Undo队列，MDagModifier撤销全部新增DAG/DG与原visibility，Redo同一节点及动画连接。dry不注册插件；执行只载自己的候选command，不安装/autoload，不改core。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint通过；真实临时AbcExport/AbcImport/gpuCache、cube8vertices/frame1=2/frame3=6/原父ty10局部挂载、dry无变、一次Undo无AlembicNode残留与原Undo历史、重复Undo/Redo和动画、bad后行全表拒绝/hideFalse/overlap/锁/batchGUI拒绝。隔离fixture卸载reader释放Windows临时handle，仅测试进程，候选不卸载插件。
- GUI/GPU视口/复杂生产Alembic/跨版本not_run，prepared_unverified。Undo可能留空namespace与会话注册command，相关队列存在时不能卸载候选，验收路径变换用新session。实际5h61%已用、周40%，立即继续isolate_selected；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：隔离选中物体完整候选，累计70/109

- 原两文件SHA归档，完整四入口/API/Schema/原生小UI/知识/验收/晋级备齐；修正原隐藏直接shape与全场景强制恢复，保留选中后代祖先，只还原本次visibility。UUID持久network receipt与原视图集合可随场景保存/重命名/显式panel恢复，锁/引用/驱动/真实例/别名/腐坏记录/手改visibility全表拒绝。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全部通过。实际DAG/shape/visibility/UUID/receipt/单Undo与Redo、重命名、无关/原隐藏保持、选中后代祖先、锁/坏行/改值/实例拒绝。仅替换viewport adapter，不冒充原生视口验收；native batch/GUI拒绝正确。真实modelPanel/GUI/视图Undo/生产场景/跨版本not_run，prepared_unverified；意外视口失败人工Undo本调用。
- 实际5h66%已用（剩34%）、周41%，立即继续mirror_tool；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：镜像变换完整候选，累计71/109

- 原单文件SHA与所有类/方法/完整三平面三模式层级UI保留，UI两写入口转Base API，预制Schema/只读preflight/知识/验收/晋级。原Euler公式保留，不声称任意矩阵几何对称；精确basename/namespace路径匹配、歧义/缺侧对象拒绝、shape排除、实际目标DAG深度排序、全部源提前采样修复双侧污染。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全部通过：九组合与完整原mirror_transform实际世界矩阵一致、dry/单Undo/选区时间保持、两侧交换、父子顺序、namespace、全表锁/动画/真DAG实例/歧义拒绝。目标普通transform/正scale/无shear/identity OPM/正均匀父链及计划祖先scale严格条件；GUI/生产rig/pivot/旋转顺序/跨版本not_run，prepared_unverified。
- 实际5h68%已用（剩32%）、周41%，立即继续no_highlight_v2；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：取消高亮完整候选，累计72/109

- 原单文件SHA归档；完整Start/Stop、第一对象/shape组件选择跟随、原生小UI及旧方法名、Base/Schema/预检/知识/验收/晋级。修正同一对象连续选择清override不再应用，UUID记录两属性原值，恢复原视图/选择模式/facet，不强制0/1；锁/引用/驱动/实例/外部值冲突拒绝。六API回调有显式清理，UI close/delete拆回调，Undo/Redo及其选择递送禁止写，最近Stop Undo用recover，不假称Python生命周期可Undo。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全通过：真实override/UUID重命名/Undo Stop+recover、同选重用、锁/坏值/实例、六真实callback注册/移除、真实Undo与BeforeNew清理。初始失败发现standalone selectMode object/component均False；整个viewport/selection-mode adapter显式替换，不伪造原生模式通过。真实modelEditor/mask/GUI SelectionChanged递送/UI删除/生产跨版本not_run，prepared_unverified。
- 额度首次读取失败后重读实际5h72%已用（剩28%）、周42%，立即继续quaternion_tool；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：四元数完整候选，累计73/109

- 原SHA/全部数学类方法与完整创建/向量/Euler/应用/帮助UI保留，全部按钮走Base API，十一action/严格数值/Schema/只读preflight/知识/验收/晋级备齐。原乘法/RotateDirection/XYZ约定不改；浮点dot边界clamp，MVector输入复制避免normalize副作用，原零模identity和Slerp clamp保留。应用明确deg修正rad单位，不写单位/keys，严格普通XYZ/无rotateAxis/identity OPM及全表锁引用驱动实例拒绝。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全通过：十个纯计算无场景变化，实际MEulerRotation quaternion/90度向量/FromTo同向反向/Slerp半角与反号/逆积/normalize/零fallback、MVector不改；实际原cmds.rotate姿态一致、dry/oneUndo/AutoKey、rad单位姿态一致、坏后行/旋转顺序/keys/别名/组件/实例拒绝。GUI/生产复杂父级pivot及跨版本not_run，prepared_unverified。
- 实际5h75%已用（剩25%）、周42%，立即继续rotation_aligner；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：旋转对齐完整候选，累计74/109

- 原两文件SHA归档；原角度显示说明与旋转对齐源码不匹配明确记录，不宣称AngleDisplayContainer存在。完整原1132行全部函数/矩阵/JO/RA/order/单轴搜索/两步完全对齐与六轴/限制/多对列表/范围烘焙/迭代右键UI保留，去模块开窗，高层入口受Base/Schema/scope/只读预检/晋级保护。
- 明确source被旋转、target只读；原烘焙无setKeyframe修正范围真实写keys，非烘焙保留参考小数key，单帧小数/可选成功跳帧；统一Undo/AutoKey/time/degree单位转换。原6选up参数算法未用，拒绝不伪造。源锁轴按原跳过，JO/RA/order原算法；驱动/引用/共享curve/OPM/实例/shear/反射/退化检查，未来帧动态失败可Undo本调用。
- 2离线+4隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint通过：真实原单轴矩阵、完整XYZ、JO+非XYZ+旋转父、锁轴单轴、dry/单Undo/AutoKey/time、实际range键/小数参考key/曲线外键保留/rad度制/共享curve拒绝。新建键fixture缓存未求值导致一次Undo姿态比较失败，先显式时间求值后核对原曲线值/矩阵，全部通过，不改算法掩盖错误。GUI/生产长动画/复杂骨架/跨版本not_run，prepared_unverified。
- 实际5h80%已用（剩20%）、周43%，立即继续smart_mesh；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：SmartMesh完整候选，累计75/109

- Dennis Bartalon Porter原1.1.0两文件SHA/所有MEL业务与安装/About归档；完整四几何业务/原生四row图标文字fallback/逐操作命名/预检/Shelf/Hotkey/窗口Shelf/About/标准Base/Schema/知识验收晋级。合并精确mesh叶/多数完整父组，不临时重命名整个层级或删原组/无关child，静态history独占消费者保护；拆分两pivot分别保持；extract指定面/全face拒绝，duplicate完整rig源只读/新副本清理检查UUID，不碰源skin/children/history，全face无空delete。
- 2离线+4隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全通过：真实combine数量/父组/无关对象/材质/AutoKey/单Undo原全部节点；separate壳/父组/不同两pivot/Undo；rigged源duplicate保持skin与mesh/全face/真实extract；锁/共享poly历史/错scope/写实例/GUI与安装batch拒绝。原shape-wide listHistory走入groupId/共享SG导致误拒绝，改几何inMesh图；实际combined pivots查询顺序与假设相反，改两属性独立读，修复后全部通过。
- Shelf/Hotkey完整实现但只验收晋级注册后显式安装，静态正式包命令不留staging路径，不覆盖任何既有press/release绑定或foreigncommand；持久UI/偏好不由sceneUndo回滚，整理时未写。GUI/复杂UV材质/生产rig/引用实例只读duplicate/持久安装及跨版本not_run，prepared_unverified。
- 实际5h87%已用（剩13%）、周44%，立即继续unlock_freeze；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：解锁冻结完整候选，累计76/109

- 原单文件SHA归档；完整九TRS解锁/原makeIdentity apply全TRS/原选择恢复，移除channelBox隐含其它属性与MEL拼接，精确TRS及compound解锁，可选restore_locks；标准Base/Schema/预检小UI/知识/验收/晋级。全部受影响后代/几何输入独占construction预检，锁后代/引用/实例/动画/JO/OPM/共享历史/geometry consumer/相机灯/变形器拒绝，不仅检查输入根。joint原生T骨长/旋转转JO边界说明明确。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint通过：真实mesh世界points保持/TRS归零/锁解除、oneUndo原points/锁/选区/历史、v锁保持/AutoKey与restore_locks；nurbs circle/controllerCV、组后代mesh及joint骨段位置；坏后行/动画/alias/overlap/实例/GUIbatch拒绝。一次测试因新建polyCube改变fixture当前选择，改显式选择被设key的源再拒绝验证，不改业务掩盖。GUI/生产复杂pivot法线/模型骨架/跨版本not_run，prepared_unverified。
- 实际5h90%已用（剩10%）、周45%，立即继续uv_set_renamer；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：UV集改名完整候选，累计77/109

- 原单文件SHA归档；完整跨模型UV名称联合列表/白色输入/红色改名/Zwj水印UI、两兼容函数、Base/Schema/inspect只读默认/知识验收晋级。全表最终名称冲突预检，两阶段临时名称支持交换循环；每mesh缺old按原跳过，但全部不存在拒绝；UUID跟随、真实DAG实例/引用写/锁/名称及current驱动检查，当前UV集跟随原集身份，统一Undo，选区时间AutoKey不改。
- 2离线+3隔离Maya2025+临时正式布局/注册/modeling_surfacing/panel/fingerprint全通过：两mesh缺不同UV集、dry不改状态、原MFnMesh坐标/分配索引/native set index保持、current正确跟随/oneUndo；交换与稀疏index保持；冲突/缺old/重复final/后行锁/alias/组件/实例/GUIbatch拒绝。GUI/按UV名称关联材质UVChooser与导出器/生产rig-history/跨版本not_run，prepared_unverified。
- 实际5h95%已用（剩5%）、周45%；按每项收尾阈值保存后进入额度等待，下项world_transform_v4。候选均留在池内，不迁正式/同步/用卡/购买。

- UV候选提交5ad20dd08dcdd643e7aeeeb9badadc3a659531a6；App heartbeat已启用并由本机配置复核，状态waiting_for_quota，下项world_transform_v4未开始，等待5h剩余>95%且周允许再续跑。本轮新增16项（62至77），累计77/109。

# 2026-10-02：额度刷新续跑，世界坐标V4完整候选，累计78/109

- 实际5h0%已用、周46%、ordinaryUsageAllowed=true；本聊天为当前checkout唯一active writer，App heartbeat暂停并本机配置复核，rescan动态109无新增缺项后从第78项恢复。遵循用户最新不用卡/购买、不迁正式、不同步约束。
- 原单文件SHA归档、完整原生UI/两滑条/只key/ChannelBox组识别/真实高亮范围/进度保留；标准Base/Schema/只读inspect/UUID单位快照/父子排序重试/真实逐帧key/Undo/时间AutoKey恢复/显式独占JSON/知识验收晋级。修正原自动覆盖共享temp、±180角差、失败仍key且报成功、未高亮误取范围；不把snapshot当动画曲线，所选组小数keys保留。
- 2离线+5隔离Maya2025+临时正式布局/注册/panel/fingerprint全通过：真实父子姿态/重命名UUID/单Undo/key/time/AutoKey；已有小数key/范围外key值/只位移；JO+nonXYZ joint/native xform、不同pivot/rad/m单位；临时JSON exclusive/dry/非法load/内存dry不改；坏后行锁/共享curve/真实实例/batchUI拒绝。发现原生setKeyframe生成直接time曲线可能无显式input连线，允许Maya隐式time或time1两标准输出，仍拒绝自定义time驱动，修复后全通过。
- GUI/ChannelBox/高亮/取消/生产复杂骨架及跨版本not_run，prepared_unverified。实际5h4%已用（剩96%）、周46%，立即继续abc_batch_exporter，heartbeat工作时暂停。

# 2026-10-02：ABC两版完整候选，累计79/109

- 两Python2原稿逐字节SHA归档；完整两原生UI全部控件与随机Lambert/SG按钮保留Python3函数回调，模型列表/选择集/quoted AbcExport全部flags/Schema/只读预检/知识验收晋级齐备。修正原动态exec/boolean值塞flag/不quoted文件路径/缺集沿用旧选区/强制丢弃当前scene/覆盖输出。batch真实逐scene独立mayapy，scriptNodes禁用，当前scene不打开/关闭/保存。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint全部通过：实际带空格ABC写出并AbcImport回读两mesh/UV/动画最后帧6单位、选区时间AutoKey/node/modified不改、dry不加载exporter/创建file、既有cache bytes不覆盖；缺空set/stripNamespace冲突/随机材质真实分配与oneUndo；真实childmayapy分别导出good.ma及missing.mb失败且保留成功文件，dirty liveUnsaved scene完整，输出已存在及同stem冲突全批前拒绝。
- GUI双窗/颜色faceSets全部语义/生产引用资产/跨版本not_run，prepared_unverified。文件/plugin加载非sceneUndo，worker超时可能遗留独有临时或partial文件明确说明。实际5h8%已用（剩92%）、周47%，立即继续asset_it_v1_2，heartbeat保持暂停。

# 2026-10-02：AssetIt完整原套件候选，累计80/109

- 978原文件159310854 bytes、18 Python/225函数、290图库模型+3缩略图模板scene、354PNG/309JSON/HDR/TX/JPG完整字节保留。许可限制原软件修改/第三方分发，不改任何原套件代码；原危险Drag安装器仅.py.original归档。完整所有原UI/浏览/搜索收藏/标签/metadata/放置drag/replace/import/ref/场景文件多资产/渲染/设置业务和资源齐备；单独Base/Schema/只读库存metadata/独占namespace导入/新目录复制安装/原版完整UI启动预检/知识验收晋级。
- 2离线+2隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：全部978 SHA/18语法/225defs/290 metadata-thumbnail；真实原Bolt模型导入/new group/scale/current namespace/selection/time/AutoKey、已有NS全表前拒绝、真实全部DAG/DG一次Undo+Redo及临时原文件移走仍Redo；159MB新临时目录独占copy/codebytes/安装副本UserLibPath指向自身独立库/旧目录不覆盖/dry不写file。Arnold原生requires实际autoload，PyMel缺；完整GUI/render等未运行，prepared_unverified。
- 修复真实file import不能由外层Undo回滚，独占MPxCommand以新UUID控制MDagModifier lifetime，既有Undo队列保留。发现删除空NS后API Redo ls能列出但objExists解析失败，改Undo保留占用空NS、Redo无文件读取；明确限制新导入换NS，手工删保留NS后Redo拒绝。current namespace使用absoluteName，验证已有NS不能因当前userScope而绕过。最初293总MA误等同图库数量，精确改290+3模板。所有问题修复后检查通过，无伪造GUI验收。
- 原完整UI后续native callbacks仍有原rmtree/rename/偏好/renderSetup/固定名cleanup等不可自动Undo行为，按许可保持原状，如实列备份库集中验收边界；adapter launch前依赖/安装代码SHA/库路径/固定名冲突检查。实际5h19%已用（剩81%）、周49%，立即继续batch_importer_v3，heartbeat保持暂停；不迁正式/同步/用卡/购买。

# 2026-10-02：批量导入V3完整候选，累计81/109

- 原单文件SHA归档；全部Qt主窗/文件与递归folder/count/name/References/Import/DeleteList/DelRef/ZWJ水印保留，Python2 long→int，Qt6/Qt5 lazy，cancel空folder防错、namespace可编辑。标准Base/Schema/全表路径/实例数/namespace不碰scene预检、独占nativefile lifetime、知识验收晋级。
- 2离线+4隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：真实MA/MB三份导入/oneUndo所有DAG-DG/原源file移走仍Redo/name lookup；OBJ真实triangle导入/UndoRedo；两同源RN独占UndoRedo及选同份多个object/shape后whole-reference preview/删除仅1份/Undo恢复选区/Redo不碰另一份；unloaded且custom RN重建原名/元数据锁/load状态，nested子与包含nested父/edited reference/非引用/坏后行/NS碰撞全部前拒绝。禁止scriptNodes和NS共享自动fallback，保持time/AutoKey/currentnamespace/有效selection。
- Maya默认RN metadata locked，原先锁判断误拒绝正常file removal；不手动解锁既有RN，改用原生removeReference；restore仅解锁本次新RN完成原名重建并还原lock。严格无edit/顶层无nested/SHA可读范围，reference Undo/Redo读原文件且节点UUID可变；普通import保留空NS且Redo不重读file。GUI全部控件/FBX与ABC/all translator reference模式/生产跨版本not_run，prepared_unverified。
- 实际5h25%已用（剩75%）、周50%，立即继续batch_processor_v3；heartbeat工作时暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：文件批量执行V3完整候选，累计82/109

- 原单文件SHA归档，完整Qt列表/drag/自然名称日期大小排序/全部所选/三个保存模式/Save/log保留；Base/Schema/readonly预检，默认逐文件隔离mayapy、真实ordered Python/MEL执行，强制覆盖前原始字节备份、全表路径/SHA/冲突预检，正确MA/MB保存，FBX覆盖拒绝，知识验收晋级齐备。脚本为任意用户代码，isolated保护调用者scene但不是OS文件沙箱；交互只允许真实GUI干净已保存scene，结束重开来源恢复有效选区/time/AutoKey/namespace，Undo清空和外部影响明确说明。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：实际两child场景/Python-MEL顺序/原字节备份/SaveAfter/dirty调用者及Undo不变；MB覆盖实际Binary、脚本失败/换scene不自动保存；save_current freshMB/原MA mandatorybackup、batchGUI模式/FBX覆盖前拒绝、取消前不启动worker。初测MEL utf8-sig非有效codec名，修正utf-8-sig后全通过；原QPlainTextEdit.appendHtml错用改QTextEdit.append+HTML转义。
- 默认不删除unknown，显式选项保留；保存外部文件不Undo，覆盖先SHA验证但不承诺并发比较交换，cancel/timeout不回滚脚本外部影响。GUI/实际FBX/interactive/MGTools/途中取消/跨版本not_run，prepared_unverified。实际5h32%已用（剩68%）、周51%，继续clean_invalid_paths；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：字符策略路径清理完整候选，累计83/109

- 原Python/README两件SHA归档，完整双窗/路径明细/选择刷新/单全删除/作者保留，补ascii/cjk/replacement策略与整引用显式选项。所有原renderer类型/动态已加载扩展、全部现存path attrs、Alembic真实abc_File/cacheName、容器循环有界全部上游实际owner，非ASCII不假称文件损坏，默认scan/readonly dry，无外部文件写入删除。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：实际file混合Unicode、ASCII缺失不报、layered第二条上游实际owner且容器拒删；纹理DG原UUID/连接oneUndoRedo；gpuCache/imagePlane shape删后父transform保留/Undo；锁后行全表拒绝；中文源顶层完整reference native removal/Undo恢复selection/load/RN/name-lock/Redo，仅显式允许，edited拒绝。MDagModifier.deleteNode默认includeParents=True实测仍删空父，改False后通过，不以API封装假设父保留。
- 标准Base/Schema、专用MPx local-node snapshot+整引用恢复、self-contained reference helper（不依赖其他待池）、函数绑定UI/UUID行删除/预检确认、知识验收晋级齐备。Maya reference Undo仍须同SHA源文件/空namespace且UUID可能改变；嵌套/edits/源不可读拒绝。GUI/全部renderer schema/生产plugin副作用/源变化Undo/跨版本not_run，prepared_unverified。实际5h36%已用（剩64%）、周51%，继续fbx_batch_exporter_v7，heartbeat暂停；不迁正式/同步/用卡/购买。

# 2026-10-02：分组分段FBX V7完整候选，累计84/109

- 原主窗/配套预设两件SHA归档；完整native form/两组列表与计数/高亮范围/前缀/全部FBX flags、axis、十版本/配置窗/SSC/层级bake/ZWJ水印保留。Base/Schema/readonly inspect/全表配对预检/小数范围、独占输出自动序号保prefix、显式新JSON/原两预设schema加载、知识验收晋级齐备。未保存scene明确选择输出目录，配置不自动覆盖共享JSON。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：实际ASCII FBX写两文件/序号保prefix/原生FBX再导入模型与第3帧tx=6；所有所用FBX flag及animation property恢复、selection/time/AutoKey/四独立播放范围/dirty flag/Undo队列不变；真实SSC UndoRedo与约束对象bake 1,2,3 keys/tx/oneUndo恢复驱动；JSON新写/dry/读回/已有文件byte不覆盖/坏后行不写FBX。
- 本机FBXPushSettings尝试写settings file Permission denied，改全部使用query逐项finally还原，不Push/Pop/ResetExport。初测bake层级含constraint伪keyable多属性，排除constraint作为烘焙目标并multi=True列真实属性后通过；FBX导入namespace不是预期测试范围，按实际mesh回读而非误判导出缺mesh。全部原范围和层级业务保留，不把export文件影响包装为可Undo。
- GUI/highlight/全部flags组合及旧FBX版本/生产动画层/UE实际导入/跨版本not_run，prepared_unverified。实际5h41%已用（剩59%）、周52%，继续per_frame_bs_fbx；heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：逐帧BS与FBX完整候选，累计85/109

- 原单文件SHA归档；无原UI脚本完整生成流程替换为cmds/API2、Base/Schema/只读inspect和轻量候选UI，免缺失PyMel。多non-intermediate mesh分别按世界空间快照复制基模/UV/face SG、每mesh每frame原生BS target/linear 0-1-0脉冲、single rootJoint rigid skin/逐帧key，支持父级运动与source deformer、明确采样网格及内存预算、existing group拒绝不reuse。自包含全FBX helper / shape-skin flags+设置恢复/独占output、知识验收晋级齐备。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：实际两mesh/source BS形变+父tx运动、1/2/3逐世界顶点吻合、六target+rigid skin/源scene图Undo退回/Redo仍几何正确、选区timeAutoKey/absolute userScope不改；真实ASCII FBX导出/生成组oneUndo后FBX仍存在/已有output前拒绝，再导入两个skin输出mesh+2 BS/skin，1/3帧顶点回读吻合；共享真实DAG实例/坏步长网格/GUIbatch拒绝。
- FBX重导入额外具化六BS辅助目标meshes，不用全部mesh数量误判模型，按skin.outputGeometry shapes=True与source→生成base映射逐点验证，保留完整严格几何断言；第一轮测试把排序后第二mesh误当sourceCube（offset 4），修正测试身份映射后通过，未掩盖或降级顶点正确性。源材质copy可增加SG membership（引用SG可能record edits）明确说明，visibility/material-animation不转换；拓扑改变runtime拒绝/清理owned新UUID，动态求值副作用待验。
- GUI/长序列/动态模拟/引用SG/拓扑变化/UE真实消费/跨版本not_run，prepared_unverified。实际5h47%已用（剩53%）、周53%，继续replace_references，heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：引用替换三版完整候选，累计86/109

- 三原入口SHA归档；EN多选并改NS/MEL式单选保NS/Python batch文件列表+增删rule三套全部nativeUI保留、imports不打开UI。Base/Schema/readonly inspect，真实native loadReference+带copy-number的准确file edit namespace、自动规范basename/suffix去碰撞，不从RN字符串猜namespace，不以旧扩展强制新格式。专用MPx Undo/Redo重载原/目标SHA、load状态/namespace、真实RN UUID守护、reference无edit/无nested/简单NS/源可读准入和知识验收晋级齐备。
- 2离线+3隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：多RN含同份多object/shape去重，真实MA→MB/两namespace/oneUndo恢复旧资产及selection/Redo目标；unloaded depth none保持load状态、保NS/Undo旧path；edited后行全表不写；真实child batch原始SHA/caller dirtyscene/time/AutoKey/Undo不改，新MA打开确为两新sphere；多rule命中拒绝且不生成结果。batch原稿不保存改为独占全新同格式output，保源scene，不force切换caller。
- file edit namespace必须给reference文件（含copy-number）而非只传RN；Autodesk明确会同搬namespace中local nodes，新增所有成员均属本RN的检查后才改NS，避免扩大影响。Windowsnative query路径slash形式用Path归一比对；原生MA→MB惰性增默认sharedReferenceNode，Undo仅保留该Maya共享元数据（不删默认），测试严格检查其他所有原节点恢复/无其他新增，不声明元数据集合逐字节Undo。
- GUI/复杂生产refs/损坏file rollback/plugin副作用/跨版本not_run，prepared_unverified。实际5h53%已用（剩47%）、周54%，继续vessel_fbx_exporter；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：舰船自动FBX完整候选，累计87/109

- 原单文件SHA归档，完整All_joints烘焙/Reset_Trans全部keys删除+原9TRS值/全场references import/导出集合与成员NS merge/AAA关键词/原全部FBXflags/每次export后root_NNN rename/可选引用FBX/原备用export-set bake(default False)保留。Base/Schema/readonly inspect/全集preview、候选简UI、self-contained FBX/MA IO、知识验收晋级齐备；原无UI导入自动执行取消，整体仅作用exportAll复制dirty/untitled当前scene的真正独立mayapy snapshot，workspace保持/scene scriptNodes禁用/私有Maya app日志，不改变caller。
- 2离线+2隔离Maya2025+临时正式布局/注册/panel/fingerprint通过：原dirtycaller全部节点/references/keys/Customkey/selection/time/AutoKey/Undo/modified原样，真实snapshotchild import reference/namespace去除/All_joints keys1,2,3/Reset TRS rx=-90并custom全部keys清后首帧1/root_001；全新prepared MA实际读回这些状态、真实ASCII FBX再导入1mesh；已存在output/锁后行/空全部exportset前拒绝不写。原Reset_Trans cuts所有attrs明确preview，不假称只TRS。
- 原烘焙reset在reference import之前，候选private import先行避免副本reference edits生成后import丢失，明确记录顺序行为改变；NS merge有副本全namespace扩大搬迁/重名影响，原caller完全保持。文件/日志不Undo，worker失败/timeout可能保留完成outputs。GUI/嵌套引用/动态模拟/备用bake-export-set分支/全部flags/UE与跨版本not_run，prepared_unverified。实际5h57%已用（剩43%）、周55%，继续ue_bone_exporter，heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：UE骨骼表完整原生候选，累计88/109

- 原5文件SHA归档，完整UE Python SkeletalMesh名称TXT与C++ Editor原生右键/保存窗口/成功消息两条实现保留。明确Python网格骨骼与原C++共享Skeleton差异，C++提供mesh/shared两菜单；补Context/MessageDialog/Paths/FileManager显式include和ToolMenu owner生命周期，移除未用EditorStyle补AssetRegistry，exclusive文件保护，无自动执行/无asset commit/save。
- 3离线mock和临时最终布局/源码fingerprint通过：UTF8中文骨名/只读dry-run/已有目标整表拒绝/不同路径同名collision/竞争写入保留竞争者并撤自己的文件。UE package在缺Maya/Unreal时可导入。临时晋级助手增加明确external runtime分支，仅engine/docs/tests ownnamespace，无Maya Base/registry/panel伪适配；2实际temp-repo测试验证未验收/旧SHA拒绝、验收后复制/重复目标拒绝、Maya注册字节不变及external禁止写正式Maya路径。只改本轮临时助手，不修改正式框架。
- 本机Program Files/Epic Games未找到安装。真实UE资产/SkeletonModifier读取副作用/UBT C++编译/保存窗口/热重载/跨UE版本均not_run，不把源文本检查称为编译通过；prepared_unverified，UE runtime_acceptance单独not_run，Maya GUI仍未伪通过。实际5h63%已用（剩37%）、周56%，继续ue_context_menu；heartbeat暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：UE源路径右键完整候选，累计89/109

- 原单文件SHA归档，完整Print Source Paths/多路径Output Log保留；取消import即注册，显式owned menu register/unregister/dry-run无菜单与日志变化；通用ContentBrowser.AssetContextMenu+自有section，callback正式完整模块名。去除不可靠has_editor_property，保留4级获取方法fallback、错误与raw_relative provenance，不把未解析源误报绝对路径。
- 2离线mock+临时最终布局/fingerprint通过，真实模拟多源去重/方法错误回退/无property/raw路径/只读注册dry-run/重复注册单entry/注销/空选区log。正式Maya registry byte不变，真实UE菜单和资产类型/版本均not_run，prepared_unverified。实际5h65%已用（剩35%）、周56%，继续ue_fbx_auto_import；heartbeat保持暂停。

# 2026-10-02：Maya配置+UE动画导入双端完整候选，累计90/109

- 原2文件SHA归档；完整Maya Qt5/6配置生成UI（检测Anim/Skeleton、两可编辑combo、FBX拖放/文本、Load/Generate/桌面编号JSON）和UE实际FbxImportUI/AssetImportTask/FbxFactory批量动画导入保留。Maya仅配置生成继承Base/category engine_bridge/Schema/ToolResult，UE independent engine package提供原生结构化API，共享自包含纯config，无虚假UE Maya执行。
- 源绝对FBX/SHA/三键旧JSON/Content正确relative_to/仅Skeleton uasset/重复basename/坏最后cfg/重叠目标/真实Skeleton类型/全新Game目录预检；dry不创建tasks/options或文件。UE按stem新子目录隔离多take、明确confirm_import、mandatory animation-only flags/no mesh-material-texture、EXPORTED_TIME/replace=False/save原True，原静态mesh对象错误选项取消；native失败停止并保留partial路径；共享Skeleton曲线metadata可能变，不承诺import/save Undo。Maya文件独占创建不覆盖、初测loader缺正式framework修复使用候选launcher；GUI检测异常显示warning。
- 3离线mock+1隔离Maya2025+临时最终布局/正式注册/domain/panel/fingerprint通过，配置实际JSON/编号旧bytes保持/wholebadcfg不import、native成功/空返回失败；Maya真实dirty scene/节点/场景名/Undo dry/写文件均不改。临时晋级新增双端必须runtime_version，3temp repo测试含只有Maya验收不得晋级。真实Maya配置UI/UE导入与Skeleton/Interchange多take/跨版本not_run，prepared_unverified。实际5h68%已用（剩32%）、周56%，继续ue_reference_checker；heartbeat保持暂停，不用卡/不转正。

# 2026-10-02：UE引用检查器完整原生候选，累计91/109

- 原单文件SHA归档，完整direct hard/soft包引用+_zoo忽略大小写pattern、原深色Tk表格/统计/滚动/异常优先/右键定位/关闭保留。显式Schema/API/dry-run、无自动窗口；query异常/None为unknown并success false，registry loading拒绝提前判定，不返回假空引用；package身份去重，同名显示不混淆。
- UI改UE Slate主线程pump Tk，不worker destroy/quit，不mainloop堵塞；单例/callback close与queue bounded100生命周期齐备。locate ARFilter exact包，按Epic文档修正sync_browser_to_objects为object path strings而非Object，加载缓存与浏览器选择影响明确，资产/文件不保存。
- 3离线mock+临时最终布局/fingerprint通过，重复同名不同包/regex/真实errorunknown/空refs/directoptions/loading与invalidregex拒绝、dry locate不sync/实际path数组sync/mainthreadguard；真实UE registry/ReferenceViewer/Tk-Tcl/GUI/Slate close热重载not_run，prepared_unverified。实际5h70%已用（剩30%）、周57%，继续ue_source_finder；heartbeat保持暂停。

# 2026-10-02：UE源文件复制完整候选，累计92/109

- 原单文件SHA归档，完整源查找/按资产名重命名/copy2元数据/成功缺失失败TXT+名单+汇总+Explorer功能保留；取消import自动复制，default inspect/dry，Schema/结构化原生API。reviewed source reader独立复制自包含，多源default first保原，all额外_srcN；raw相对不猜cwd。独占fresh会话目录/full UE父路径/Windows名与collision预检保护原桌面文件，源SHA/size复核+copy独占+目标SHA+copystat，失败只删自己的partial且报告；mkdir/log失败也进入summary。Explorer default False，显式True用参数数组无shell。
- 3离线真实临时IO与mock+临时最终布局/fingerprint通过，distinct /Game/A/Hero与B/Hero/同asset名不碰、first/all/三份bytes一致/source不改/四TXT与summary/missing/已存在session拒绝/真实模拟copy失败partial清理与失败日志/相对路径与escape拒绝。源读取pattern构建含control字符初测语法失败已修，最终静态/单测通过。真实UE/Explorer/跨版本not_run，prepared_unverified。实际5h72%已用（剩28%）、周57%，继续06_diagnostics_security/clean_junk_nodes；heartbeat保持暂停。

# 2026-10-02：HM未知节点清理完整候选，累计93/109

- 原PyMel入口SHA归档；全部unknown节点/unknownPlugin requires/ModelEditor callback与一键UI保留，修正字面量ls_unknownNodes判断与漏cmds、免PyMel。Base/Schema/ToolResult/scene_hygiene/完整UUID与锁/引用/插件元数据/回调scope预检；unknown不等于junk，默认inspect，unknownDag/解锁/插件永久移除/allCallbacks分别显式选择，引用/default/有后代Dag/instance拒绝；自有MPx+MDagModifierFalse保父/原UUID属性连接锁UndoRedo，callback原字串恢复。
- 2离线+3隔离Maya2025+临时注册/domain/panel/fingerprint通过，真实unknown attr+连接+locked→delete/oneUndoUUID连接锁/Redo、坏最后locked全表无删除、真实MA missing plugin fixture原metadata只查/未确认拒绝/明确confirm永久移除；原plugin remove文档虽称undoable，本机实际Undo不恢复，未谎称可Undo，新增confirm_plugin_metadata_loss/GUI须备份提示并记录不可逆元数据影响。初测MDagModifier对locked节点排队静默不删，修正先解锁再排队后严格测试通过；不降低节点生命周期恢复断言。
- GUI/modelEditor回调Undo、unknownDag/reference/真实custom data/跨版本not_run，prepared_unverified。实际5h77%已用（剩23%）、周58%，继续scene_virus_cleaner；heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：Maya ASCII策略文件清理完整候选，累计94/109

- 原单文件SHA归档；完整多目录拖放/list/clear/progress/cancel/备份/批量过滤保留，Base/Schema/ToolResult/scene_hygiene/预检UI。原输入覆盖+errors ignore+固定history覆盖改为完全新output/history精确原bytes/report，原file与caller永不保存；默认known准确script names（仅策略，不等于病毒signature），all_scripts+confirm与非maya requires显式原广泛模式保留，scene/ui config两默认保留（原只scene）。
- 自包含byte MEL lexer，strings/escape/line-block comments/embedded semicolons/多行payload准确分界；不执行源、保ANSI/UTF8与换行，删除script块与其实际connect/select引用，字符串metadata里含同名保持；缺semicolon/引号block不闭/混select/超128MB/非MA/坏最后file全表拒绝。输出path源路径hash防同名，写前SHA复核、backupSHA验证、不完整ownbackup/output清理，成功备份保留、cancel/错误partial报告如实。
- 3离线真实bytes/CRLF/非UTF8尾/quotedpayload/合法script/plugin/string保持/newoutput exactbackup/source不改/坏最后file不mkdir/取消保完成报告+1隔离Maya2025真实保存MA/过滤/ScriptNodes=False读回cube tx7+合法script/known删除/caller dirtyscene全部nodes/Undo/ty9保持+临时注册/domain/panel/fingerprint通过。真正GUI/复杂生产MA/plugin与手写MEL语义/跨版本not_run；未称完整杀毒，prepared_unverified。实际5h80%已用（剩20%）、周58%，继续undo_checkpoint，heartbeat暂停。

# 2026-10-02：Undo记录点完整候选，累计95/109

- 原六文件SHA归档，完整Qt窗口/名称时间状态/创建/选中或最近回退/清空/双击/确认/viewport提示与四个Shelf快捷入口保留。Base/Schema/ToolResult/default inspect；静态MPx无场景marker、session元数据、唯一命名native Undo chunk和只读queue完整预检，max_steps不足/flush/stale/foreign id在首次Undo前拒绝。逐步Undo复核queue，Redo同步applied；clear/overwrite只清元数据，不flush用户Undo。原始文件不改、不自动加载、Shelf仅docTag自有项，实际GUI/开放外层chunk/跨版本not_run。
- 2离线+3隔离Maya2025+临时最终注册/domain/panel/fingerprint通过，cube tx1/A/tx2/B/tx3→B与A准确回退/Redo、dry队列和scene无变、max_steps拒绝/flush旧ID与陌生ID不回退、overwrite/clear与Undo禁用保护。初版输出过滤回调虽然功能断言通过但进程退出CPython bool_dealloc崩溃，失败报告保留；改MCommandMessage普通输出回调finally remove后断言通过且正常exit0，未把崩溃写成成功。
- 补修90双运行时候选launch_candidate缺engine_toolkit搜索路径：launcher自身添加候选根，移除测试预置路径后再验真实隔离配置API与最终布局均通过，未来正式布局不依赖staging。实际5h87%已用（剩13%）、周59%，继续07_subsystems_suites/animbot_copy，heartbeat暂停。

# 2026-10-02：animBot Copy完整UI原型候选，累计96/109

- 82源文件包含全部历史截图SHA归档，全部Python AST检查/结构清单、主/Graph Editor工具栏/Workspace全布局、程序绘图图标/各独立slider动态模式/右键菜单/预设/勾选/换行/拖动滚轮/回弹保留。原项目动画按钮缺业务算法，本候选诚实标animation_algorithms_implemented=false，不凭UI标签声称可烘焙/复制姿态；Schema/Base/ToolResult统一配置API只操作session/UI。默认inspect，config全表校验、main/graph独立、dry零Qt初始化/场景/配置/文件修改，run不引入无意义Undo。新窗口主线程/Maya QApplication校验。
- 修复自建英文left/right预设错误、新名称不覆盖旧preset、取消每次launch广泛reload、旧singleton lambda保留delete控件改bound QtSlot、close全自有窗口及Graph Editor控件。全相对native package、独立Qt5/Qt6导入、原机器图标路径移除使用现有完整QPainter fallback，不依赖商业资源。独立单tab才隐藏并记录恢复，不改共享多tab祖先样式；Viewport原映射TimeSlider限制如实保留。
- 2离线配置原子/坏最后ID/重复/位置/严格bool/全preset/英文对齐检查、1隔离Maya2025 cube tx7/dirty/nodes/Undo保持与batchUI拒绝、1单独Qt离屏全主/graph/workspace构造/所有preset/双向显示同步/DeferredDelete后singleton无dead callback、临时正式注册/domain/panel/fingerprint通过。第一次把Qt QWidget构造放在maya.standalone.initialize后原生fastfail3221226505；逐步定位在主toolbar构造，失败原始报告保留。拆为无Maya初始化的独立Qt构造测试后正常exit0；场景API单独隔离测试亦exit0，不将离屏替代实际Maya GUI。Qt退出有SWIG MObject leak warning，记录为重复真实GUI生命周期待核对，没有声称无内存泄漏。
- 实际5小时95%已用（剩5%）、周60%已用（剩40%），本轮78–96共19项完成，按用户低于6%规则保存，下一项07_subsystems_suites/getools_overlappy。全部候选保持待整理池，真实Maya/UE验收not_run，不运行Obsidian同步、不用重置卡、不购买。
- 96候选提交58ca44c4f07876af165410575ed41e0da0b6e3a0，manifest检查点保存；App将同聊天30分钟heartbeat改ACTIVE，enter_quota_wait核对本地配置确实ACTIVE并记录waiting_for_quota/96 complete，动态重扫109项入口全部存在，下一项pending。恢复须实际五小时剩余>95%、周额度允许且无另一运行回合，不以预测刷新时间代替额度读数。

# 2026-10-02：GETools/Overlappy完整候选，累计97/109

- 开始实际5h0%已用、周61%，无其他写入回合；App暂停heartbeat且resume_run核验。109项动态对账全部入口存在。原8中文模块缺Settings/utils/experimental/values及素材；官方GitHub固定commit 45c4e17504fded01262941843ed186e9ac73c477，直接Git/下载超时，固定SHA的jsDelivr源清单/每文件SHA256核验成功，67项MIT依赖完整归档、原9文件SHA保留，全7模块GUI/相对图标/内置preset保留，未运行未完成prototype。
- 完整Base/Schema/ToolResult、COM create/activate/targets/project/delete、native overlap setup/bake/clear、预设read/save及UI，默认inspect。借用COM不删，固定group须实例UUID匹配；scene操作复用UndoChunk、恢复时间/范围/选择/refresh/cachedPlayback，修正恢复在chunk外造成一次Undo只撤选择的实际缺陷，保持严格一次Undo断言。原COM nested list参数修正。literal preset不exec/globals.update，1MiB上限/独占新文件/已有parent；启动不mkdir、不改全局HelpPopup/CachedPlayback，Reload/Quit显式默认Cancel。
- 2离线+2隔离Maya2025+临时最终注册/domain/panel/fingerprint通过：全模块import无新节点、COM两目标tx5/一次Undo恢复tx0、删除一次Undo准确UUID恢复、借用/foreign拒绝、native默认preset无globals污染。下载快照Python2 prototypes仅原文归档.py.original不作为候选可执行代码；复核全部可执行Python静态通过，mayapy正常exit0，最终Python指纹628a34b0f417f22a109f5fffd6c58d2e2ce8241535137fb608bc1b836cbe50fb与runtime报告匹配。
- 完整真实GUI、nParticle物理/solver缓存/bake/跨版本及native广范围菜单not_run，prepared_unverified。实际5h14%已用（剩86%）、周63%（剩37%）；继续malcolm341_mega_pack，heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：Malcolm341 Mega Pack完整候选，累计98/109

- 用户提供付费MEL shelf/安装说明2文件SHA完整原bytes归档，个人候选不推定公开再分发许可。完整49按钮、119回调位（含空菜单分隔）、全部右键/双击/布局保留；MEL字符串/comment lexer提取精确callbacks，无执行原入口。自有MTB Shelf、所有m341_窗口/optionVar/函数隔离命名，固定id/event API、Base/Schema/ToolResult/default inspect，scene UndoChunk，真实GUI要求与显式confirm_native。
- pivot非空单poly mesh/组件、锁/reference/pivot锁/坏选择预检；临时ma/obj/fbx转移显式绝对file_path、parent存在、导出新文件、导入不执行MA scriptNodes，取消不运行。native所有明确file-export/FBXExport/UV快照路径guard拒绝已存在文件；原fopen a/w的userSetup及UV snapshot删除前同目录独占精确byte备份/SHA验证。其他原prefs/系统/插件/延迟jobs/硬退出不假称由scene Undo恢复，完整影响和逐项备份场景验收文档。
- 2离线+2隔离Maya2025+最终临时注册/domain/panel/fingerprint通过：完整Shelf只编译不安装、不增加场景nodes，fileguard旧bytes保持/真正native fopen追加前精确备份、nativecube顶点中心pivot/dry不动/一次Undo与选择恢复/锁与多mesh拒绝。分类初版不属于六个domain，修正modeling_surfacing并重验通过。完整49实际UI/原子窗口/全部菜单/导出插件/偏好/退出/跨版本not_run，prepared_unverified。
- 实际5h20%已用（剩80%）、周64%（剩36%）；继续maya_blueprint_toolbox，heartbeat保持暂停，不迁正式/同步/用卡/购买。

# 2026-10-02：蓝图工具盒完整候选，累计99/109

- 29原文件SHA归档；45原类型节点、完整中文Qt5/6 canvas/数据模型/全部Maya包装/原文档/两示例保留。Base/Schema/ToolResult、完整graph API/default inspect、typed port/strict bool/有限数值/必填/未知节点参数/双来源/重复id/cycle/目标上游范围与8MiB/1000nodes/10000links。无Qt eager launch；自有MTB窗、主线程/已有QApplication、shared UndoChunkContext，不改正式core。
- dry仅纯结构及当前可解析readonly数据/目标预检，写入依赖结果列deferred，实际每操作前再次全表校验；整graph一个Undo、重入拒绝。missing/ambiguous/锁/reference/default/保护后代拒绝，group/rename碰撞与祖孙混批拒绝，全部attr converted值及目标轴/constraint受驱通道首写前检。JSON exclusive新名、显式overwrite备份+原子替换，CopyFrame唯一temp，不mkdir；FBX文件保护/显式备份/finally恢复选择与三项Bake flags，import MA scriptNodes=False。
- 修正确定原world samples按local scalar写入错误：Maya xform按parent space/rotateOrder转世界位移/欧拉，部分world轴保持其他world轴并全localXYZ耦合预检/打键，scale保持原relative local语义；全部samples首写前检。隔离parent tx10/ry90/sx2+target rotateOrder3→source世界tx7/ty3/rot15,25,0准确，真正一次Undo/Redo恢复，锁tz耦合轴拒绝不改。首次测试在write之后先scrub时间才Undo，撤的是测试的时间操作，保留初次报告并将一次Undo断言移到真实write后立即执行，没有削弱断言。
- 2离线+4隔离Maya2025+独立无Maya初始化Qt离屏完整canvas/all45类型/示例序列化与连线+最终临时注册/domain/panel/fingerprint通过，Qt额外报告指纹核验后入manifest。bad最后锁目标/缺失对象前项tx保持、图写两对象一次Undo完整、采样恢复时间/既有JSON bytes保持、原data transform示例准确。真实Maya UI/45 production节点、复杂rig负scale/shear/jointOrient/FBX/reference/跨版本not_run；prepared_unverified。实际5h27%已用（剩73%）、周65%（剩35%），继续smart_assistant；heartbeat暂停。

# 2026-10-02：Smart Assistant完整候选，累计100/109

- 17原文件SHA归档；完整prefs/Drop ma-mb-fbx-obj-abc选择open/import/reference/sequence camera+modelPanel/Python fileDialog2路径功能、控制UI和独立monitor/patch启停API。修正原空path_utils/QObject错误/Qt6缺失/弱filter引用/namespace取消root引用/所有prefs写string的缺陷；默认inspect或show_ui无全局hooks，enable显式注册，会话恢复不覆盖foreign后来wrapper，enable失败只撤本次新增hook。
- 原5optionVar白名单全表typed/有限/大小边界、literal JSON/new文件/已有parent、不覆写package或prefs文件，apply记录首状态、失败回滚/restore各key原类型和不存在状态；实际gridDivisions为float而非固定int，接受整数数值保留存储类型。只optionVar不谎称改变scene currentUnit。全64files首写前检查、missing最后不import首项、explicit reference namespace、dirty open先保存+1file/confirm/forceFalse/scriptNodesFalse；不消费系统文件或场景真实源。
- Sequence唯一prefix/padding/扩展/数字顺序/连续至少2帧、正确imagePlane shape和frame_driver、camera隐藏/当前cam显示/可选view；单Undo保持选择，frame2真正驱动plane.frameExtension2。初版尝试额外expression遇native已连接time，改复用本次new imagePlane原驱动，不覆盖连接；首次失败报告保留。原renameAll=True导入cube变source_fixtureCube保持原语义，测试核对真实mesh6faces与returnNewNodes长路径，不猜短名。
- 2离线+4隔离Maya2025+独立Qt无Maya-init QObject/QDropEvent测试（自有子树受支持文件消费/foreign或py后缀不吞/停止强引用filter）+最终临时注册/domain/panel/fingerprint通过。Python dialog wrapper kwargs/显式dir/返回/重复不叠加/foreign拒绝/restore在隔离fixture通过；Qt文件URL原生斜杠和Windows反斜杠用Path语义核对。全部真实Maya GUI/drop长期生命周期/dialog/sequence显示/plugins/reference/跨版本not_run；原不合法MEL global fileDialog2覆写不保留，MEL原生签名与返回不破坏，文档明确Python路径功能边界。prepared_unverified。
- 实际5h33%已用（剩67%）、周66%（剩34%）；继续studiolibrary_patch，heartbeat保持暂停，不迁正式/同步/用卡/购买。
