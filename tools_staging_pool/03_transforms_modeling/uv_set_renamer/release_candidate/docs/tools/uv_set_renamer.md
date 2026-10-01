# UV集改名工具

id `uv_set_renamer`，域 `modeling_surfacing`。原ZWJ单文件/SHA归档 upstream；完整跨选择模型UV集联合列表、原名/新字段、空字段跳过、逐mesh批量改名与水印保留；新增预检/刷新，原两函数提供兼容显式入口，Base/Schema/Undo/完整晋级备齐。导入不启动UI，真实GUI/生产材质网络/跨版本not_run。

action='inspect'默认，objects默认当前整节点选择，mesh或一个可见polygon shape的transform；返回所有mesh的UV名联合列表，不能组件/非mesh/歧义/重复shape别名/中间shape/实例。action='rename'需renames={old:new}非空字典，新名限ASCII标识符；有旧集的mesh才应用，原联合列表中没有此旧名的其它mesh不创建它。某old全表不存在拒绝；同名到同名为无操作。最终每mesh的名称不能碰撞未改集或另一个新名，引用/节点锁/uvSet或currentUVSet锁/被驱动、具体uvSetName锁驱动全表拒绝。

所有最终名称在写之前检查。先每个原名改独占临时mtbUV名称，再全部改最终名，支持同一mesh名称交换/循环，不用原逐行改名覆盖/后行失败后前行已改。UV数据、set index、坐标与面顶点分配由原生polyUVSet(rename=True)保持，当前UV集跟随原集身份映射到新名。当前集不切到别的数据。节点UUID让窗口打开后对象重命名仍正确；删对象/变UV表后旧输入可能失效，重新按当前选择刷新。

API例`tool.run(action='rename',objects=['|mesh'],renames={'map1':'base','lightmap':'map1'},dry_run=True)`，成功同参数run。inspect/dry_run只查询/构建计划，不改UV名、当前集、节点、selection/time/Undo/AutoKey。结果data `{rows,uv_sets,two_phase_names}`，rows含node/shape/UUID/names/indices/current/renames/final_names/final_current。run场景修改在一个UndoChunk，选择/时间/AutoKey不改，不写外部文件。未知原生命令错误可能留下临时名字/部分改名，Undo本次并检查，基类不会自动回滚。

Shader/UVChooser及外部管线可能按UV名字选择纹理，改名可能改变材质行为；保留索引/数据不等于所有按名引用自动更新。真实材质网络和导出约定需备份Maya验收，不自行改shader/UV链接或重写外部资源。现有history/变形器中的UV更新按Maya原生命令，复杂生产rig未验证，不把纯坐标检查当完整材质验收。

完整小UI显式launch_candidate.show_ui()或create_uv_set_renamer()；原rename_uv_sets(fields,uv_sets)兼容函数把输入转统一API，空字段全空返回no-op，不执行原代码打印失败后继续行为。core未发现同一UV集批量命名流程，复用框架结果/Undo；SmartMesh输出网格可继续检查/规范UV集命名，组合未生产验证。不要未核对就把重命名map1输出喂给要求固定UV名的导出器。

验证：原字节/Schema/严格类型；Maya2025隔离实际两mesh联合列表/只在存在old处改名、真实UV坐标/面顶点分配/索引/当前集、双向交换/索引孔洞、dry无变/oneUndo、全表冲突/坏old/后行锁/alias/组件/shape实例/GUIbatch拒绝。真实完整GUI/材质按名选择/生产rig/跨版本not_run。原by ZWJ归档，不推断公开发行许可。
