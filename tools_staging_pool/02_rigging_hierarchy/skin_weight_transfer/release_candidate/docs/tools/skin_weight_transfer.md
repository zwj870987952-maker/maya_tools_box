# 骨骼权重批量转移候选

状态 `prepared_unverified`：离线与隔离 Maya 2025 检查通过，真实 GUI / 大网格 / 生产 rig 和其它版本未验收。只留在待整理池。原 `骨骼权重转移.py` 全15函数及原字节/SHA归档；原代码无作者/许可说明，不推断发布权限。

用途：同一个 skinCluster 内，把源关节每个顶点的权重累加到目标关节，源归零，再对全部影响归一化；可在完成后移除源蒙皮影响，保留源关节。支持按输入顺序的多行任务，每行显式多个模型或省略模型从源关节已连接的 skin 自动发现。不会绑定新skin、补新影响、跨拓扑复制权重或删除骨骼。

原全任务界面、加载选择、多行编辑、执行均保留，增加只读预检。加载选择使用完整DAG路径，窗口/控件仅清本次自有实例。业务封装为 `SkinWeightTransferTool`（category=`rigging`），继承 BaseMayaTool、ToolResult、`run`、Undo Chunk 和 Schema，无生产注册表变动；候选内部镜像正式目录及完整晋级信息已预制。

| 参数 | 内容 |
|---|---|
| `action` | `transfer` 默认执行；`inspect` 返回完整计划 |
| `tasks` | 1..1000个有序对象，各含 `source_joint`、`target_joint`，可选 `meshes` 字符串列表、`remove_source=False` |
| `task_text` | 多行文本；与tasks二选一，空行忽略；`源 => 目标 => 模型1,模型2 => DelSkin`，后两列可省略；第四列只有空或DelSkin合法 |

```python
from maya_toolkit.tools.skin_weight_transfer import SkinWeightTransferTool
tool = SkinWeightTransferTool()
args = dict(task_text='|root|a => |root|b => |body => DelSkin\n|root|b => |root|c => |body')
plan = tool.run(dry_run=True, **args)
if plan.success:
    print(tool.run(**args).to_dict())
```

候选阶段通过 `launch_candidate.py` 的 `load_tool()` / `show_ui()` 加载。晋级后统一 `maya_toolkit.execute_tool('skin_weight_transfer', args, dry_run=True)`，晋级清单包含代码、文档、测试、类注册及面板接入。

输入必须是完整或唯一全节点名；歧义短名、实例、重复模型别名、缺失源/目标影响、同一源目标、非网格、中间Shape、多个skin/多geometry拒绝。写入网格/skin锁住或引用拒绝；任一影响liw锁住、连接驱动权重、保持最大影响数开启、DQ/混合skin拒绝，先在备份场景确认调整后再用本候选。只读预检列出每任务mesh/skin/影响与顶点数，不改变选择、时间、Undo、权重或文件。

完整列表先预检，并模拟每行移除影响的结果；后续再使用已移除的源/目标时整个列表失败，避免原来的部分成功/静默跳过。执行按序重新读实际权重，所以 A→B 后 B→C 会继续转入 A。每行全部顶点 `target += source, source=0` 后除权重总和；零总和行保留零。原 MFnSkinCluster 批量读取保留；非可撤销的API setWeights改成cmds.skinPercent逐顶点可撤销写入，完整归一化也通过该写入实现，而非依赖不可靠的API Undo。DelSkin通过原生removeInfluence，隔离实测单次Undo恢复源影响及原权重。大网格可能比原非Undo的API写更慢，实际速度与生产精度待验收。

输出包含 `tasks_completed` 及每次处理的shape/skin/source/target/vertices/source_removed；不输出 Maya 对象。没有外部文件写入，选择与时间保持。运行时异常可能留下已执行部分；检查错误并Undo本次再继续，不声称失败自动回滚。

知识复用：使用现有框架Undo和协议。正式 `weights_copy` 是网格之间权重复制/补绑定，core的 `get_skin_cluster` 只取第一个；本工具需要严格唯一skin检查和同skin内关节权重合并，不强行替换为这些不同语义能力，不修改core。可在确认蒙皮后用于减少冗余骨骼影响，再接SkinInfo导出或SkinMagic LoD；这些组合尚未真实Maya验收，工具仍独立自包含，不依赖其它staging路径。

检查：3组离线（原15函数/SHA、任务文本/Schema、合并与归一化）；4组隔离Maya2025（全顶点实权重/dry/单Undo，自动发现/连续链/DelSkin及Undo，未归一化数据完整恢复，全表错误不写/锁/重复别名/实例/GUI batch拒绝）。这些检查不等于真实GUI验收。
