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
