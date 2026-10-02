# 引用替换与批量场景替换

原三入口完整SHA归档：EN多选整引用替换并改namespace、MEL单选替换保namespace、Python批量文件列表/添加删除匹配条目。保留全部三版native布局、浏览/替换/条目增删，并提供模式小窗；import不自动开启UI。原EN通过删RN字符串猜namespace可能改错、MEL强制ASCII、batch按旧扩展选新格式且只打开不保存（处理结果丢失）均修正。

## 标准调用

`ReplaceReferencesTool`，id replace_references，pipeline_io，Base/ToolResult/Schema/Undo。默认inspect提供new_file（已有绝对MA/MB），reference_nodes或objects唯一精确范围（二选一，可省略用选区，RN或对象/shape去重），rename_namespace默认True。replace才执行整文件引用替换。preview列原path/SHA/RN UUID/namespace/load/metadata-lock/全部nodes、新文件/SHA/计划namespace；会替换整份文件，不仅选中的mesh。

```python
from maya_toolkit.tools.replace_references import ReplaceReferencesTool
tool=ReplaceReferencesTool()
preview=tool.run(dry_run=True,objects=['old:mesh'],new_file='D:/temp/new.mb')
result=tool.run(action='replace',objects=['old:mesh'],new_file='D:/temp/new.mb',rename_namespace=False)
```

使用实际referenceQuery namespace+原生file edit namespace，basename全名规范化（保留RN字符，不按RN字符串推断），碰撞追加序号；简单namespace，不支持nested namespaces。只允许顶层无nested子/父、无reference edits且来源可读范围，避免无法完整恢复编辑。原生RN标准锁不误拒绝file reload。新文件类型由新文件自身MA/MB检测，不依据旧扩展。

namespace编辑使用带copy-number的准确reference文件参数，不能只传RN flag。Maya的file edit namespace也会搬迁该namespace里的本地节点，因此改namespace前拒绝任何本地或其他引用节点，避免移动无关对象；这是[Autodesk file命令](https://help.autodesk.com/cloudhelp/2025/ENU/Maya-Tech-Docs/CommandsPython/file.html)的原生行为边界。

## 场景、Undo边界

自有MPxCommand执行原生loadReference和namespace编辑；捕获来源SHA/相同RN UUID、load状态。一次Undo重载原来源和namespace，Redo重载目标。对象UUID可变，mesh/骨架/材质可能全变，参考原文件须一直可读且同SHA。unloaded引用用loadReferenceDepth none只改路径，保留unloaded；native loader不执行scriptNodes。时间/AutoKey/currentnamespace恢复存在的namespace，旧namespace已改名而当前namespace失效时返回root；被替换对象选区可能消失，Undo恢复存在的原名。

原生MA→MB重载可能惰性创建默认sharedReferenceNode元数据；Undo恢复资产对象/路径/namespace，不删除该Maya共享元数据节点。检查允许唯一这种默认辅助节点新增，仍严格拒绝其他节点丢失或多余生成。不声明整个默认节点集合逐字节回滚。

Undo/Redo前检查命令拥有的RN UUID、当前路径、namespace占用、sourceSHA、后来产生的reference edits，拒绝覆盖外部改动。异常尽力按已触及条目回滚，不保证任意插件/损坏file的事务恢复；先用备份场景。file load本身不能靠外层Undo回滚，所以命令显式保存重载信息，不把它误标原生可Undo。实际没有删除或改写原资产文件。源变化/名称被占用时Undo受限，生产复杂引用图需原生引用编辑器及人工方案。

## 批量替换

action=batch_inspect或batch，files为1..1000个已存在绝对MA/MB场景，rules为1..1000条 `{source_contains:非空字面串,target:已有绝对MA/MB}`，output_dir为已有绝对目录，timeout每场景10..3600秒（默认180）。source_contains按原case-sensitive substring匹配原reference来源；单引用命中多规则拒绝，空串不表示替换所有。default rename_namespace=True可规范改名，原批量UI固定False保留原namespace。每文件独立mayapy，先验证该场景全部匹配引用后执行，无匹配仍另存并报告replaced=0。工作进程禁止scene scriptNodes，结果写全新 `<scene-stem>__<pathhash8><原MA/MB扩展>`，使用正确编码，原源场景字节保持；已有输出/本批碰撞拒绝，最终xb仍阻止竞态覆盖。

调用者dirty场景不打开/保存，选区/time/AutoKey/namespace/Undo保持。batch_inspect/dry只检查磁盘路径/SHA/rules/输出计划，不打开外部场景，不能声称已审查其全部reference edits/匹配；子进程打开后再次完整预检，bad/nested/edited/规则冲突失败不保存该场景，其他成功输出保留。返回scenes逐场景success/replaced/output或message/traceback、processed/caller_scene_preserved。batch输出和插件日志不能Maya Undo；timeout杀进程可能保留独有临时或已完成结果，无自动场景覆盖。原UI无取消功能，当前批次同步等待每文件timeout，长运行使用小批备份。

## 复用与验收

复用标准框架、与batch_importer_v3一致的引用准入/SHA，但自包含reference helper随晋级打包；不引用池内路径。batchprocessor_v3可随后读新结果，fbx_batch_exporter_v7可导出替换资产，但仅文件接口衔接未生产组合实测。

离线原件/schema/三完整UI、非法范围，隔离Maya2025多RN去重/MA→MB实际replacement/namespace/UndoRedo、unloaded保持、edited坏后行不写、真实child batch另存保原源/dirty调用者、规则多命中拒绝无输出。GUI/nested生产reference、来源损坏后rollback、复杂插件/跨版本not_run，prepared_unverified；详见acceptance.md，满意后才晋级。
