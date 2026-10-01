# Relationship Tools v19

用途：以父相对定位器或静态足部标记重建对象关系，记录动画标记；One/More Step对齐或粘贴世界姿态，单帧/多帧Align，支持TR选项、Bake/Step和新动画层。原作者ZWJ，历史与完整原源码SHA保存在vendor/*.py.original；全部50个RelationshipTool方法与完整原Maya原生UI保留在original_logic.py，没有把旧功能替换成模拟器。候选独立engine继承原算法，修改危险范围、选项/缓存/帧采样与调用契约；原自动开窗移除。

候选launch_candidate.py通过load_tool()/show_ui()使用，晋级后maya_toolkit.execute_tool('relationship_tools_v19', arguments,dry_run)。业务按钮全部从完整UI路由同一API，主布局、checkbox/step/折叠/说明按钮保留，另加明确JSON导入导出按钮。原UI选项读取改为引擎option(name)，不在batch制造假checkbox或timeline。晋级包自包含，无待整理池或系统临时文件依赖。

| 参数 | 默认/含义 |
| --- | --- |
| action | inspect默认；mark、mark_foot、mark_animation、copy_world、one_step、more_step、align、delete_marks、export_pose、import_pose |
| objects | 可选有序唯一whole节点，1..1000；mark/mark_animation/align最后一个是父/目标；省略step选择时仅当前owned标记或复制UUID集 |
| translate / rotate | 默认true；至少选一组，仅写所选TR，不写scale或自定义属性 |
| bake | 默认true；false只处理明确范围内所选TR真实关键帧，空范围为no-op，不偷偷全帧烘焙 |
| step | 1..1000，默认1；bake采样从start起间隔step，并保留end-1端点 |
| frame_range | 整数[start inclusive,end exclusive]，≤10000帧；more/mark_animation默认playback min..max+1；align省略是当前单帧 |
| world_coords | 默认false；One/More使用owned locator，true使用已复制UUID姿态 |
| layer | 默认false；TR写入新override层，仅所选属性，不重复执行失败流程 |
| advance | 默认false；One/More成功后恰好前进一帧；GUI保持原前进行为，失败不前进 |
| file_path | 只用于explicit pose import/export：绝对JSON；导出新文件独占不覆盖，导入≤5MB/1000姿态 |

```python
tool = load_tool()
tool.run(action='mark', objects=['childControl', 'worldReference'], dry_run=True)
tool.run(action='mark_animation', objects=['childControl', 'worldReference'], frame_range=[1, 25], step=2)
tool.run(action='more_step', objects=['childControl'], frame_range=[1, 25], translate=True, rotate=False)
tool.run(action='copy_world', objects=['childControl'])
tool.run(action='one_step', objects=['childControl'], world_coords=True)
```

validate/dry_run/inspect只读，不建locator/层/窗口，不改关键帧、场景、时间、选择、UI、文件或缓存。inspect返回完整原方法/SHA、owned marks、源连接映射、当前复制对象和not_run；call返回ToolResult、targets/frames、created_node_uuids、created_layer、copied_objects、owned_marks和操作结束选择。一个frame*object预算200000避免意外大范围工作。

Mark、Mark Foot、Mark Ani仍分别建立父相对、静态世界足部、随帧采样的标记。差异：原cleanup按全场景_locatorPar/_locatorTag名称后缀删节点，候选只删带本工具ownership/role的节点，并用message连接记录实际source；重复短名/namespace不再靠字符串反推对象。外来同名节点保护，owned下外来transform子节点、对外驱动或锁引用会阻止删除；原未知旧标记不自动认领。普通新Mark替换本候选已有标记，删除范围在dry-run可审阅；新定位器/形状/约束/mark动画曲线统一ownership，场景Undo可撤回创建/删除。重命名源仍可message追踪，删除源造成悬空标记时不把名字重用者当原对象。

One/More保留原层级排序、最多六次world pose重试、TR匹配和关键帧写入，检查实际世界平移/旋转收敛，失败如实报错。拒绝写入者会驱动自己的mark parent、Align目标处于写入祖先之下、真实多父DAG、锁/引用、非普通单独time animCurve驱动或已有复杂层/约束/warp；不声称兼容任意生产rig。Copy World保存源UUID、pos/rot，改名后仍可粘贴；默认会话缓存替代共享系统temp JSON，原copy/paste功能保留。显式JSON跨文件保存只接受有限三坐标和当前唯一UUID，全部预检后更新缓存，不执行输入代码；读写文件与Python缓存不由Maya Undo恢复。

统一start含/end不含，修复原Mark Ani多采一帧和Optimize Key按绝对frame%step删除所有属性的问题。候选先按步长采样，只给选定TR写键，从不cutKey旧对象；未采样帧已有TR键也保留，范围外键、scale/custom/未启用TR不删。因此若范围内已有未采样的旧键，它们继续影响插值，Step不宣称清空原动画。非Bake只处理范围内真正选定属性的键（包括子帧），无键即明确no-op；静态标记OneStep仍对当前帧写TR键，单帧Align保留原只匹配无强制加键行为。

新层采用override明确写世界对齐结果，只加入所选TR；原代码默认additive并把对象全部属性加层，异常还重跑函数，候选改为一次执行/原层preferred与selected恢复。已有复杂animBlend驱动保守拒绝，新层真实基础样例通过，生产层/旋转组合待实测。框架UndoChunk覆盖API场景改动；finally恢复时间（除明确advance）、selection UUID、namespace、autokey、trackSelectionOrder、refresh原暂停状态和evaluation原模式。原异常恢复总是不暂停的风险已修正，UI按钮也使用相同API保护。函数异常不自动回滚，检查报告并一次Undo。

两组普通Python验证全50原方法/原SHA/无自动启动、Schema/参数范围；五组隔离真实Maya2025验证真实parent运动→标记OneStep/Undo与owned删除/Undo/外来后缀保留，Foot与Mark Ani exclusive真实曲线键，UUID改名世界姿态/More采样与禁用属性/范围外键保留、JSON独占/有限数拒绝，单/多帧Align、空key-only不烘焙、新层TR/实际值/Undo与选择恢复，外来名称/子节点、锁/实例/GUI拒绝。对锁定tag的keyframe(transform,attr)查询未返回时间，改直接查询真实连接animCurve验证实际键，非伪造通过。临时正式布局/注册/rigging域/面板与候选指纹验证，不触正式库。

真实GUI/timeline范围/折叠/生产父子/负缩放/jointOrient/复杂层和跨版本not_run，prepared_unverified。可把标记和最终keyed目标接到后续曲线整理或层级分析；未实测跨工具组合。acceptance.md通过后才用精确候选指纹的实测JSON与promote_candidate.py晋级，当前不运行Obsidian同步。
