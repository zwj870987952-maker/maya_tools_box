# 层级与约束影响分析候选

`tool_id=hierarchy_analyzer`，类 `HierarchyAnalyzerTool`，分类 rigging。自有 `maya_hierarchy_analysis.py` 的原字节 SHA256 归档到 `vendor/*.original`，原七函数完整保留到 `original_logic.py` 且不自动运行；新 `engine.py` 保留六个分析函数入口，原完整结果界面 `main` 接入统一只读 API。

## 功能与修正

分析指定或当前选择的完整 transform/joint：祖先链、原生约束驱动、完整场景潜在影响图、穿过未选节点的间接影响、稳定拓扑分层、结构环及阻塞节点。原结果窗口保留滚动文本/验证信息/关闭，显示完整 DAG 路径，Close 为 callable 回调，不依赖 Script Editor 全局 cmds。

原混用 long/short 路径会漏关系或 KeyError；候选统一长 DAG 与 UUID，拒绝同一对象多个别名或不明确重名、组件/通配符/实例。原约束输出用 destination=False 查被驱动者的方向错误；候选由原约束 DAG parent 取得 child、实际 target query/matrix 取得 driver，统一边为 **影响者 → 被影响者**。保留原六约束并明确支持查询 normal/tangent/poleVector/pointOnPoly，geometry driver 补入。

原将约束视为覆盖所有父级影响并直接删除 DAG 边，对部分轴约束等没有依据；候选保守保留父子边。原分组用了无序 set，可能漏同层内部反向关系；候选按输入顺序稳定 Kahn 分层，独立纯图验证严格检查所有边都从前层指向后层。原发现环把剩余节点直接追加为假排序；候选输出 SCC cycles、unresolved，不给被环阻塞的节点虚构层级，纯图/兼容排序函数在有环时抛出明确错误。

## 接口与输出

继承 `BaseMayaTool`，实现 validate/execute，外部继承 run 返回 ToolResult；完整 JSON Schema 可导出 OpenAI/MCP。默认读取当前选择。

| 参数 | 默认与含义 |
| --- | --- |
| `objects` | 1..1000 唯一完整 transform/joint；省略时当前选择，引用/锁定对象可只读分析 |
| `include_hierarchy` | true，纳入父子潜在边 |
| `include_constraints` | true，纳入原生约束潜在边 |
| `include_graph` | false；true 返回全场景 direct_graph，否则只返回选择之间的传递影响和详细约束 |
| `max_nodes` | 5000，1..50000；包括全场景 transform/joint 捕获与约束数量预算，超限失败，不返回半排序 |
| `max_edges` | 100000，1..1000000；直接边及投影后传递边预算 |

输出 objects、object_uuids、hierarchy、drivers、constraints（类型/UUID/实际 child/drivers）、selected_influence、layers、cycles、unresolved、valid、场景节点/边计数与 warnings。`success=true` 表示分析执行成功，**不是** `valid=true`；结构存在环也会返回可审阅报告。未知约束类型会列警告并令 valid=false；大场景预算、重名/实例或不明确 target mapping 明确失败。

```python
result = tool.run(dry_run=True, objects=["|rig|source", "|rig|driven"])
result = tool.run(objects=["|rig|source", "|rig|driven"], include_graph=True)
print(result.data["layers"], result.data["cycles"], result.data["valid"])
tool.show_ui()
```

兼容函数：get_hierarchy_info、get_constraint_info、build_global_influence_graph、analyze_influence_hierarchy、topological_sort、verify_influence_hierarchy。全局闭包只供明确需要完整集合的 Python 调用；大图优先用 API 的选择投影和 direct_graph，避免 N² 结果。

## 条件、作用与组合

这是**结构性的 DAG/原生约束潜在影响**，不是完整 Maya DG、Evaluation Manager 顺序或运行时影响证明。即使零权重目标仍保守纳入；全轴 parentConstraint 可能补偿部分父级作用，但没有做求值或数值证明，所以也保留父边。pairBlend、offsetParentMatrix、自定义矩阵、表达式、驱动关键帧、deformer、动力学、Maya cycleCheck 及插件 DG 未纳入完整分析；不能凭 layers 自动认为并行执行安全，不能凭 cycles 宣称实际 DG 必有致命环。

validate、dry-run、execute 都只读：不改 scene/选择/时间/AutoKey/namespace/Undo，不加载 UI/插件，不写文件；原 UI 仅显式 show_ui 时打开。多个对象的只读捕获可用于备份场景检查，保留入参顺序。现有 core 提供 DAG/mesh/Undo 辅助但无通用拓扑图算法，纯图组件留候选内，未提前下沉正式 core。

输出完整 DAG、UUID、driver 列表可为用户明确选择的约束管理或层级工具提供审阅资料；跨工具自动执行顺序尚未实测，不能从静态图推导“已验证组合”。

## 检查与待验收

普通 Python：原七函数/散列/无自动入口、间接路径投影、稳定分层、同层边验证拒绝、SCC 环及下游阻塞、自环、1500 节点深链非递归、类型和预算。隔离 Maya 2025：真实 namespace/重复 leaf 长路径与只读状态，实际 pointConstraint 方向和未选中中介，保留父边，geometry 目标、joint 祖先，真实结构环、预算/别名/实例拒绝。正式目录模拟检查注册、Schema、rigging 筛选和面板入口。

真实结果 GUI、生产角色、多种约束及特殊图、更多 Maya 版本均 **not_run**。所有内容仍在待整理池，实测后按 acceptance.md 晋级。
