# Maya 蓝图工具盒：完整45节点候选

用户自有29原文件/全部中文文档/两示例完整SHA归档，17Python模块（以catalog/source_review实际数量为准）完整native运行树、45节点规格与全canvas保留。不扩展原规划的条件/循环/JSON帧数据加载或新Maya节点；所有原实现功能、类型颜色、拖连线/搜索/属性编辑/选中上游子图/多次运行/JSON/结果状态保留。native.core是套件自有数据层，现有正式maya_toolkit.core不改；native Undo共享正式UndoChunkContext。无外部临时路径、无Qt启动import依赖，Qt5/6完整兼容入口保留，自有MTB窗与主线程/已有QApplication/真实GUI检查。

统一API actions inspect/show_ui/close_ui/validate_workflow/execute_workflow/read_workflow/save_workflow，Base/Schema/ToolResult；默认inspect只列45spec，执行实例化Qt为显式show_ui。workflow为version1/nodes/connections，每node含id/type/parameters/可选title+position；target_node_ids仅该节点+全部上游，完整Graph先结构检查，选中子图才必连校验。有限8MiB/1000nodes/10000links，重复id/未知节点/参数/端口/多个来源/不兼容类型/环/严格bool/非有限数字/必填参数拒绝，不静默跳过非法图。save/load可保存合法结构的未连接草稿，不以加载即执行；读取重复JSON键/非有限常量/大文件拒绝。

```python
from maya_toolkit.tools.maya_blueprint_toolbox import MayaBlueprintToolboxTool
t=MayaBlueprintToolboxTool()
t.run() # all specs
t.show_ui()
saved=t.run(action='read_workflow',path=r'C:/temp/workflow.json')
graph=saved.data['workflow']
t.run(action='execute_workflow',workflow=graph,dry_run=True)
t.run(action='execute_workflow',workflow=graph)
```

dry/validate不运行修改节点、不改时间/选择/场景/文件、不编译UI：纯结构检查+当前可解析的只读节点求值，当前目标全表缺失/歧义/锁/reference/default节点/plug连接等检查。涉及前序写入才有的输出列deferred_nodes，真实执行每个操作前再次全表校验；此范围不能假称能预测全部未来节点名和运行状态。全graph scene操作同一个UndoChunk；拒绝重入，失败可能留可Undo的已完成步骤，文件/导入reference/插件不能保证scene Undo完全恢复。多次UI运行各自一group，状态回调保持原运行/完成/失败/跳过。

原静默丢失missing nodes改全表报错；rename/group/delete拒绝锁/reference/default、锁或引用后代及混祖孙批次，rename/group碰撞拒绝；属性设置全部converted value/属性settable先检，CopyFrame数据全部sample先检再写。约束驱动/受驱不同且transform，全部受驱轴可写，权重正有限。复制帧原世界位移/欧拉+相对scale取样/列表1:1保持，采样恢复currentTime，frame range上限10000。修正原世界样本按local scalar setAttr的确定问题：世界位移/欧拉交由Maya xform转换到目标父级空间与rotateOrder；部分世界轴粘贴保留其他世界轴，并预检/打键全部耦合local XYZ轴。scale仍为原相对local scale，不伪称世界scale。所有样本/目标/受影响轴在首写前全检，锁任一耦合轴拒绝。带父级旋转+缩放+不同rotateOrder的隔离fixture证明世界位移/角度与一次Undo/Redo；jointOrient/负scale/shear/复杂constraint rig尚未实测，需真实备份场景验收。

JSON save/new CopyFrame默认独占新文件与已有parent；空CopyFrame路径改系统temp唯一UUID而非固定覆盖，UI保存已存在名拒绝，API明确overwrite_existing才允许备份后原子替换JSON。FBX输出绝对路径/parent/后缀/全部目标/有限帧范围；overwrite_existing明确True保存同目录精确备份后导出，不默认覆盖，插件只真实export加载，finally恢复选择及三项修改的Bake flag。导入source绝对file、MA scriptNodes=False（不能保证其他插件/复杂reference不执行代码）。backup/输出文件/插件加载不由Maya Undo回滚，使用独占临时目录避免检查与写之间竞态。

可组合：节点类型与typed ports、复制帧TransformFrameData、AttrRef/AttrPacket/data lists、导出FILE_RESULT可串联本套45节点。返回results统一序列化到ToolResult；不存在的计划节点不会伪造。其他工具配合以实际输入输出和用户验收为准，未声明跨套件实测组合。

非Maya结构/JSON检查、隔离mayapy图写属性/一次Undo/坏最后锁目标/缺失目标/世界采样与parent-space转换/采样恢复时间/防覆盖/原data-transform示例，以及单独无Maya初始化Qt离屏全canvas/all45类型/示例加载可检查；这些不是已打开Maya的真实UI/生产rig/FBX/reference/跨版本验收。完整代码/资源/专项doc/tests与面板注册晋级已预制，真实验收not_run，仍留staging。
