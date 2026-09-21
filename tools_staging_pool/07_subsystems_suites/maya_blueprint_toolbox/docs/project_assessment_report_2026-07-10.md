# Maya Blueprint Toolbox 项目评估报告

评估日期：2026-07-10

> 说明：本报告中的 Git 状态（HEAD `f41633c`、未跟踪文件等）对应历史副本 `D:\Users\zhongweijie\Documents\maya蓝图工具`。当前工作目录 `D:\jiaoben\maya_blueprint_toolbox` 尚未初始化 git 仓库，其余源码级结论仍然适用。

## 1. 总体结论

这是一个面向 Autodesk Maya 的“蓝图式节点工具盒”项目，目标是把 Maya 常见操作、数据获取、数据转换和动画工作流拆成可视化节点，让用户像 ComfyUI 一样通过节点连接组织 Maya 工具流程。

当前项目已经不是空壳原型，而是进入了“可打开 UI、可创建节点、可连线、可保存/加载、可验证、可执行一批真实 Maya 操作”的早期可用阶段。核心架构已经成型，分层也比较清楚：UI 负责画布与交互，core 负责类型、节点规格和执行调度，maya_api 负责封装 Maya 命令，docs/examples 负责规则和示例。

最大优势是方向清晰、Maya 操作边界意识较好、节点类型系统已经建立；最大短板是缺少自动化测试和真实 Maya 环境回归记录，`executor.py` 与 `node_specs.py` 已经开始变重，后续继续加节点时会较快遇到维护压力。

## 2. 检查范围与验证方式

本次检查覆盖：

- 项目结构与 Git 状态。
- README、docs、examples。
- UI 入口、Qt 兼容层、画布交互。
- 节点规格、端口类型、执行器。
- Maya API 包装层，包括选择、场景节点、属性、动画、约束、导入导出、FBX。
- 示例 JSON 可读性。
- 基础静态风险，如测试缺失、未跟踪文件、缓存目录忽略。

已完成验证：

- `git status --short`：只有 `gpt-5.5-base-instructions.md` 是未跟踪文件。
- `git log -1 --oneline --decorate`：当前 HEAD 为 `f41633c (HEAD -> master, origin/master) Add animation copy frame workflow nodes`。
- `git ls-files`：主要项目文件均被 Git 跟踪，`.firecrawl/`、`.vs/`、`__pycache__/` 被 `.gitignore` 忽略。
- Node.js JSON 解析：`examples/workflows/data_transform_test.json` 与 `examples/workflows/copy_frame_json_test.json` 均可被正常解析。
- UTF-8 读取：docs 和 examples 按 UTF-8 读取为正常中文；PowerShell `Get-Content` 出现过乱码显示，但不是文件内容损坏。

未完成验证：

- 无法运行 Python 编译检查，因为当前系统 `python.exe` 报“指定的登录会话不存在”，`py -3` 报 “No installed Python found”。
- 未在 Maya 内实际运行 UI 和节点流程，因此 Maya API 行为只能做源码级审查。

## 3. 项目目标评估

项目目标可以概括为：在 Maya 内提供一个中文、节点式、可保存工作流的工具平台，先支持基础数据流和常见 Maya 操作，再逐步扩展动画、绑定、导入导出等生产流程。

目标匹配度较高：

- README 明确把项目定义为 “ComfyUI-style node canvas inside Maya”。
- docs 中的节点类型规则强调按 Maya 用户操作习惯分类，而不是按代码文件或 Maya 菜单机械分类。
- 代码中已经实现“节点功能类型颜色”和“端口数据类型颜色”两个设计原则。
- `maya_api` 包装层说明项目有意避免把大量 `cmds` 逻辑塞进执行器。
- 当前最新提交名是 “Add animation copy frame workflow nodes”，和文档中动画工作流规划吻合。

需要继续明确的目标：

- 这是工具平台，还是某几个具体 Maya 工具的蓝图化容器？如果后续节点很多，需要定义插件式节点注册机制。
- 是偏动画师使用，还是也覆盖建模、绑定、导出全流程？不同用户会影响默认节点分类和示例工作流。
- 是否要支持 Maya 2020-2027 全版本？当前代码是 PySide6-first/PySide2 fallback，但需要 Maya 版本矩阵验证。

## 4. 结构评估

项目结构清晰，当前主要模块如下：

- `maya_blueprint_toolbox/main.py`：Maya 内窗口入口，创建 `BlueprintToolboxWindow`。
- `maya_blueprint_toolbox/qt_compat.py`：PySide6/PySide2 兼容、Qt enum 兼容、Maya 主窗口包装。
- `maya_blueprint_toolbox/ui/canvas.py`：核心 UI，包含端口、连线、节点图元、画布场景、搜索、参数面板、保存加载和运行按钮。
- `maya_blueprint_toolbox/core/types.py`：端口类型、类型兼容规则、运行时数据结构。
- `maya_blueprint_toolbox/core/node_specs.py`：内置节点定义，当前约 46 个节点规格。
- `maya_blueprint_toolbox/core/executor.py`：工作流拓扑排序、输入收集、节点执行分发。
- `maya_blueprint_toolbox/maya_api/`：Maya 命令封装，包含 `selection`、`scene_nodes`、`attributes`、`animation`、`constraints`、`io`、`export`。
- `docs/`：节点类型规则、动画工作流设计和交接说明。
- `examples/workflows/`：示例工作流 JSON。

结构优点：

- UI、执行器、Maya API 封装三层边界明确。
- Maya 操作基本都集中在 `maya_api`，没有大量散落在 UI 中。
- 节点定义集中，便于快速查找现有节点。
- 示例工作流已经覆盖数据转换和复制帧。

结构风险：

- `ui/canvas.py` 超过 1400 行，承担了图形项、场景、视图、搜索、参数编辑、保存加载、运行控制等职责，后续维护成本会明显上升。
- `core/executor.py` 使用长 `if node_type == ...` 分发，节点继续增加后会变成主要拥堵点。
- `core/node_specs.py` 所有节点规格集中在一个函数中，节点数量继续增长后可读性会下降。
- 目前没有独立测试目录，也没有 CI 或本地测试脚本。

## 5. 底层逻辑评估

### 5.1 类型系统

`core/types.py` 定义了 `ANY`、`STRING`、`PATH`、`NUMBER`、`BOOL`、`VALUE`、`NODE_LIST`、`ATTR_LIST`、`FRAME_LIST`、`CHANNEL_LIST`、`TRANSFORM_FRAME_DATA` 等类型。

设计判断是正确的：项目不是简单连字符串，而是在节点连接阶段就通过端口类型限制错误连接。`VALUE` 被允许兼容部分基础类型和复杂动画数据，这让 `设置属性` 等节点可以接收多种值。

风险点：

- `VALUE` 兼容面会越来越大，长期可能弱化类型系统。建议高级动画数据继续补明确端口类型，而不是都塞进 `VALUE`。
- `NODE_REF`、`ATTR_REF` 已定义，但公开节点主要使用列表型端口，这符合当前易用性；后续如果引入单节点端口，要注意兼容规则。

### 5.2 节点规格

`node_specs.py` 已包含常量、数据获取、数据转换、Maya 操作、动画复制帧、调试输出等节点。节点规格包含类型 ID、标题、分类、功能类型、输入、输出和参数。

覆盖情况较好：

- 常量：文本、数字、布尔、路径。
- 数据获取：当前选择、节点名称、按 Maya 类型获取、SkinCluster、BlendShape、变形器、材质、约束、属性读取/检查、当前帧、范围帧、通道栏选择。
- 数据转换：节点列表合并/去重/排序/反转/层级排序/过滤/取项/计数，属性列表合并/去重/过滤/取项/计数，创建属性引用，变换通道。
- Maya 操作：选择、设置属性、重命名、打组、删除、四类约束、导入文件、导出 FBX。
- 动画：复制帧。
- 调试：打印结果。

风险点：

- `maya.animation.copy_frame` 的分类是“动画操作 / 世界坐标”，但 `node_class` 是“数据获取”。这是有意表达“读取为主、未连接时写 JSON”的混合行为，但对用户可能有点模糊。建议在 UI 上加入更明确的危险/副作用提示，或者定义“条件输出”类规则。
- 节点定义全部集中，建议后续拆为 `constant_specs.py`、`data_get_specs.py`、`data_transform_specs.py`、`maya_operation_specs.py`、`animation_specs.py`，再汇总注册。

### 5.3 执行器

`WorkflowExecutor.execute()` 的核心流程是：

1. 从工作流 JSON 取 nodes/connections。
2. 建立 node id 映射。
3. 根据连接关系做拓扑排序。
4. 按顺序收集输入值。
5. 执行节点。
6. 通过 callback 更新 UI 状态。

这个模型适合当前数据流节点系统，简单、稳定、可解释。拓扑排序可以防止环依赖，选中节点运行时 UI 会通过 upstream 子图执行依赖节点。

风险点：

- `_collect_inputs()` 对同一个输入端口多条连线时，后面的连接会覆盖前面的值；UI 层没有看到显式禁止同一 input 多连。建议输入端默认单连，创建新连接时自动替换旧连接，或者端口规格增加 `multi=True`。
- 执行器没有跳过未连接的可选输入问题，但 UI 验证已覆盖必填输入，当前可接受。
- 执行器所有节点分发集中在一个函数，继续扩展会变得难维护。建议引入 registry：`node_type -> callable`。
- 执行失败后已标记 failed 并 raise，但没有结构化错误对象，UI 只能显示字符串。

## 6. UI 与交互评估

UI 当前已经具备一个节点画布应有的最小闭环：

- Maya 父窗口。
- `QGraphicsScene` / `QGraphicsView` 画布。
- 可移动、可选择节点。
- 输入/输出端口。
- Bezier 连线。
- 类型兼容检查。
- Delete/Backspace 删除。
- 鼠标滚轮缩放。
- 中键或 Space + 左键平移。
- 双击搜索添加节点。
- 右键分类菜单添加节点。
- 右侧参数面板。
- 保存/加载 JSON。
- 检查和运行。
- 运行状态显示。

优点：

- 交互模型符合节点编辑器习惯。
- 中文 UI 已经贯穿按钮、节点标题和参数。
- 属性面板针对 `node_list` 和 `attribute_item_list` 做了专用编辑器，不只是普通文本框。
- 录入当前 Maya 选择、录入 Channel Box 属性这类设计很贴合 Maya 使用场景。

风险点：

- UI 文件过大，建议拆分成 `graphics_items.py`、`scene.py`、`view.py`、`dialogs.py`、`parameter_editors.py`、`canvas_widget.py`。
- 参数面板目前由参数类型字符串分支创建控件，后续参数类型多了会变重。
- 缺少用户确认类危险操作提示，例如删除节点、导出覆盖、设置属性批量写入等。
- 缺少运行中禁用按钮/防重复点击机制，长流程可能被重复触发。

## 7. Maya API 包装层评估

整体评价：包装层方向正确，已经把真实 Maya 操作和 UI/执行器隔离开。

### common.py

提供 `maya_modules()` 和 `UndoChunk`。这是必要的基础设施。

风险：`UndoChunk.__exit__` 内再次调用 `maya_modules()`，一般可用，但如果 Maya 环境异常可能掩盖原异常。风险较低。

### selection.py

支持读取当前选择和替换选择。逻辑直接、清晰。

风险：`replace_selection()` 会修改当前选择，但没有 undo chunk。选择变化是否进 undo 在 Maya 中通常不是重点，不过对“运行后恢复选择”的工具最好独立处理。

### scene_nodes.py

覆盖节点名称解析、去重、存在性检查、按类型获取、shape/parent transform、相关变形器、材质、约束、选择、重命名、打组、删除。

优点：场景修改操作如 rename/group/delete 已用 `UndoChunk`。

风险：

- `select_nodes()` 修改选择但未恢复，这是节点本身语义，合理。
- `group_nodes()` 会改变 DAG 层级和 selection 行为，建议后续记录/恢复选择或在说明中明确。
- `related_materials()` 对复杂材质网络只取 `surfaceShader`，第一版可接受。

### attributes.py

这是当前最核心的 Maya 操作模块之一，支持属性引用、属性检查、读写、Channel Box 属性读取、复制帧数据粘贴并设 key。

优点：

- `AttrRef`/`AttrPacket` 让属性流程更安全。
- `make_attribute_refs_from_items()` 支持完整 `node.attr` 和“节点输入 + 属性名”两种方式。
- 批量设置属性用 undo chunk。
- 复制帧粘贴时保存并恢复当前时间。

风险：

- `set_attribute_refs()` 写入前没有显式检查 locked/writable/connected 状态，Maya 会报错，但用户收到的是较底层错误。建议在写入前调用 inspect 或轻量检查，给出更友好的失败报告。
- `_set_transform_frame_data_attr_refs()` 会逐帧 setAttr + setKeyframe，这是正确方向，但没有处理动画层、约束、引用锁定、通道锁定等复杂生产情况。
- 粘贴依赖列表顺序 1 对 1，文档有说明，但 UI 中应给用户可见提示。

### animation.py

提供当前帧、范围帧、变换通道、Channel Box 通道、复制帧、保存 JSON、帧/通道归一化。

优点：

- `copy_frame()` 会保存并恢复 currentTime，符合动画安全要求。
- 默认通道是位移+旋转，缩放默认关闭，符合常见动画工作流。
- JSON 输出路径默认到 temp，避免强制用户配置。

风险：

- `copy_frame()` 读取所有 transform 通道作为 recorded_channels，但 `paste_channels` 仅用于后续粘贴筛选；这设计可以，但命名上可能让用户误解“复制时只复制这些通道”。
- 世界旋转用 `cmds.xform(... rotation=True)`，复杂 rotate order、joint orient、父层级情况下可能不是最终动画师预期，需要 Maya 实测。
- `save_frame_data_json()` 没有指定 `encoding="utf-8"`，虽然数据多为 ASCII，但建议统一补上。

### constraints.py

封装 parent/point/orient/scale constraint，带 undo chunk。

风险：没有处理 driver/driven 数量关系的 UI 说明。当前实现是多个 driver 约束每个 driven，这符合 Maya 命令但用户需要知道。

### io.py / export.py

支持导入/引用文件和 FBX 导出。FBX 导出会加载插件、配置烘焙、选择目标节点、导出后恢复 selection。

优点：FBX 导出恢复选择，这一点很好。

风险：

- `mel.eval('FBXExport -f "{0}" -s')` 对路径中的双引号等特殊字符没有转义，通常问题不大，但更严谨可以加转义。
- 导出只恢复选择，没有恢复 FBX export 全局设置；Maya FBX MEL 设置是全局状态，可能影响用户后续手工导出。
- 导入/引用属于较重操作，建议 UI 增加确认或预检查报告。

## 8. 文档与示例评估

文档体系比较完整，已经包含：

- 通用节点类型规则。
- 常量节点规则。
- 数据获取节点规则。
- 数据转换节点规则。
- 动画工作流节点规划。
- 世界变换复制粘贴工具拆解。
- 下一轮开发交接说明。

优点：

- 文档不是简单说明按钮，而是在定义分类边界，这对后续长期扩展很重要。
- 文档明确“按 Maya 操作习惯设计节点”，这是正确产品方向。
- 示例工作流 JSON 可解析，说明保存格式基本可用。

风险：

- README 的早期段落和后续段落重复度较高，建议后续整理成“快速开始 / 当前能力 / 示例 / 开发规则”。
- docs 中有“交接文档”性质文件，适合作为历史上下文，但不应长期作为主要设计规范。
- 示例 JSON 的 `title` 是展示字段，虽然可加载，但如果节点标题后续改名，依赖 title 没意义。建议示例只把 `type` 作为真实逻辑字段，title 可选或加载时刷新。

## 9. 当前进度判断

按“从原型到生产工具”的阶段划分：

当前处于 2.5/5 阶段。

1. 概念设计：已完成。
2. UI 原型：已完成。
3. 可用 MVP：基本完成，但缺少 Maya 内回归测试记录。
4. 可扩展工具平台：部分完成，节点注册和文件拆分还没做。
5. 生产级工具：尚未达到，需要测试、错误处理、版本兼容验证、打包安装和更多安全机制。

已完成的关键能力：

- Maya 内窗口入口。
- 节点画布和连接。
- 类型检查。
- 保存/加载工作流。
- 选中节点及上游依赖运行。
- 常量、数据获取、数据转换、Maya 操作节点。
- 属性引用工作流。
- 复制帧数据到 JSON 或连接到设置属性后粘贴并打 key。
- FBX 导出恢复选择。

未完成或待强化：

- 自动化测试。
- Maya 版本兼容矩阵。
- 节点注册机制。
- UI 文件拆分。
- 危险操作确认。
- 长流程运行状态管理。
- 更复杂动画场景支持：动画层、引用、锁定通道、约束烘焙、rotate order。
- 打包/安装说明，例如 shelf 按钮、Maya module、userSetup。

## 10. 主要风险列表

高优先级：

- 缺少测试：现在新增节点只能靠手工在 Maya 里试，风险会随节点数量增加。
- `canvas.py`、`executor.py`、`node_specs.py` 单文件过重，扩展速度越快，维护成本越高。
- 危险 Maya 操作缺少 UI 层确认和更友好的预检查。
- Python 编译和 Maya 内运行未在本次环境中验证。

中优先级：

- `VALUE` 类型过宽，后续可能削弱端口类型安全。
- FBX 导出会修改全局 FBX 设置，未恢复。
- 复制帧/粘贴帧对复杂动画生产场景支持仍基础。
- 示例工作流缺少“预期结果”和 Maya 场景前置条件说明。

低优先级：

- PowerShell `Get-Content` 中文显示不稳定，但文件 UTF-8 读取正常。
- 未跟踪文件 `gpt-5.5-base-instructions.md` 与项目无直接关系，建议保持不提交或移出项目目录。

## 11. 建议路线图

第一阶段：稳定当前 MVP

1. 增加一个最小测试框架，优先测试 `core/types.py`、`core/executor.py` 的纯 Python 逻辑。
2. 增加 Maya mock 层，测试 `executor` 是否能正确分发到 API 包装函数。
3. 写一份 `docs/testing_in_maya.md`，记录每个示例工作流的 Maya 前置条件和预期结果。
4. 把 `canvas.py` 拆成多个 UI 模块。
5. 给删除、设置属性、导入、导出等操作加确认或预检查提示。

第二阶段：扩展节点体系

1. 引入节点注册机制，让节点规格和执行函数靠 registry 对齐。
2. 将 `node_specs.py` 按功能类型拆分。
3. 将 `executor.py` 的长分发改成 `NodeExecutorRegistry`。
4. 增加执行报告结构，包含成功节点、失败节点、耗时、修改对象。
5. 增加工作流版本迁移函数。

第三阶段：生产化 Maya 工具

1. 提供 Maya module 或 shelf 安装方式。
2. 做 Maya 2020-2027 / PySide2-PySide6 兼容验证表。
3. 增加动画工作流第二批节点：获取对象关键帧、帧范围过滤、保存/读取帧数据文件。
4. 增加常用 Maya 操作节点：复制节点、设置父子层级、解除父子层级、冻结变换、删除历史、居中轴心。
5. 加入更完整的错误提示和日志面板。

## 12. 最终评分

- 项目方向：9/10。目标明确，贴合 Maya 用户习惯。
- 架构分层：7.5/10。三层结构清楚，但关键文件开始过大。
- 底层逻辑：7.5/10。类型系统和执行模型合理，但 registry 和测试还缺。
- Maya 安全性：7/10。多数修改操作有 undo chunk，但危险操作 UX 和复杂动画场景仍需加强。
- UI 完整度：7/10。MVP 交互完整，但还不是生产级节点编辑器。
- 文档完整度：8/10。规则文档丰富，但需要整理主次和补测试说明。
- 工程成熟度：5.5/10。缺测试、缺打包、缺版本验证。

综合评价：这是一个方向非常明确、已经具备可用雏形的 Maya 节点工具平台。现在最应该做的不是继续堆很多节点，而是先把测试、模块拆分、节点注册、危险操作安全提示补上。这样后续扩展到动画、绑定、导出管线时，项目不会被单文件和手工测试拖慢。
