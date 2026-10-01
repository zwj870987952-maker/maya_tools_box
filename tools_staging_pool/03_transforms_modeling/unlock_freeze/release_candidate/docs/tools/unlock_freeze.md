# 解锁并冻结变换

id `unlock_freeze`，域 `modeling_surfacing`。原单文件SHA完整归档 upstream；完整原九TRS属性解锁、apply=True的translate/rotate/scale makeIdentity冻结和原选择恢复，通过Base/ToolResult/Schema提供，兼容unlock_and_freeze_transforms函数。原无UI，候选增加预检/执行及原锁恢复选项。导入不执行；真实GUI/生产复杂模型骨架/跨版本not_run。

objects默认当前整节点transform/joint选择，restore_locks=False保持原“全部TRS解锁”行为，可选True在成功冻结后准确还原compound/九子属性原锁。候选不调用channelBoxCommand/CBunlockAttr、不拼接用户对象进MEL，避免原解锁当前ChannelBox选中其它属性；只解本工具TRS，visibility/自定义属性不动。

冻结实际影响所选根及其所有后代geometry/transform，不能把输入根当唯一写scope。全表预检精确UUID/完整路径，拒绝歧义/重复别名/根层级重叠、引用/节点锁/DAG实例、相机/灯/其它shape、后代锁TRS/动画驱动/OPM、jointOrient驱动锁、退化矩阵、intermediate/变形geometry、共享construction或geometry外部消费者。根TRS属性锁允许并显式解开；后代不会自动解锁。mesh/nurbsCurve/nurbsSurface只允许其几何输入的独占静态poly/明确nurbs构造历史，不自动处理skin/blendShape/rig连接。shape-wide材质关系不当可写history。

validate/dry_run仅查询所有受影响节点和construction，返回计划，无解锁/场景/选择/时间/Undo写入。结果data `{roots,geometries,affected_nodes,construction_nodes,restore_locks}`，roots含UUID/原locks。run标准UndoChunk，临时AutoKey关闭恢复，finally原有效选择恢复，时间不变；cmds.makeIdentity原生几何/法线/history/JO规则保留。普通transform重置TRS并把变换作用到几何，世界外形应保留；joint的translate按Maya原生规则不会强制清零，rotate冻结进入JO，不能宣传“所有关节T归零”。pivot/法线/原构造历史的具体结果需真实生产场景验收。

不删原历史/不写外部文件或偏好。错误可能已修改前对象/几何，基类不自动回滚，Undo本调用复查。示例`tool.run(objects=['|mesh'],restore_locks=False,dry_run=True)`成功后同参数run；显式launch_candidate.show_ui()。复用标准Undo/结果，不改core。与SmartMesh静态几何操作可按备份先freeze再combine/提取，但deformer/引用拒绝条件一致且组合未生产实测；不要在WorldSpaceTools已建动画的目标上直接冻结。

验证：离线原字节/Schema/严格类型；隔离Maya2025实际TRS锁/世界mesh点保持/一次Undo/原锁与选择/AutoKey/v锁不变、restore_locks；实际nurbs circle构造/controller点、组后代mesh点与joint原生JO/骨段位置、全表坏后行/驱动/alias/overlap/实例/GUI batch拒绝。真实界面、复杂法线/pivot/生产骨架与其它版本not_run。原作者/许可未明确，不推断公开发行授权。
