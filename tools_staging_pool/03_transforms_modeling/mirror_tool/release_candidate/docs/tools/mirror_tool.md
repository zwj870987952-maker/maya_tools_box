# 变换镜像工具

id `mirror_tool`，域 `modeling_surfacing`。原完整单文件/SHA 归档 upstream；完整原类/所有方法/窗口代码保留 native，受支持的 MirrorCandidateUI 把两写入口接 BaseMayaTool。保留左右命名、层级、XY/YZ/XZ 三平面、控制/普通/复制三模式及执行反馈，增加只读预检。导入不打开窗口。真实 Maya GUI/生产 rig/跨版本 not_run，候选尚未转正。

完整原算法保留：世界位置沿平面法线取负，世界缩放复制；控制按原 Euler 对应两轴取负，普通按原公式再加 180 度，复制模式应用源局部旋转。公式不是通用矩阵/四元数对称算法，不承诺所有旋转顺序与复杂非均匀父级的几何对称。正负轴和模式示例以真实目标世界矩阵验收。目标只接受普通 transform；jointOrient 的 joint、shape/组件不适用。

输入 `objects` 默认当前选择，`left='_L'`、`right='_R'`、`include_hierarchy=False`、`plane='XY'`、`mode='orientation'`。命名只改 basename，保留 namespace；同时含两侧标识拒绝。层级只扩展 transform，去重重叠根，并按目标 DAG 深度先父后子，修正原按 `/` 排序无效及 shape 被当对象。先匹配映射祖先后的完整路径，若不存在再找相同 namespace 的唯一短名；歧义/缺对应有侧标识对象拒绝，无标识中心节点记录 skipped。不采用原“随意第一个同名”匹配。

`pairs=[{'source':'|hand_L','target':'|hand_R'}]` 支持明确任意命名配对；与 objects/层级扩展互斥。来源可多次读取，但每个目标仅一次，禁止自身、重复目标、实例与缺节点。目标锁、引用、关键帧/约束/驱动通道拒绝，全表检查避免部分处理。目标 shear/非 identity offsetParentMatrix、非正 scale、父链非均匀/负 scale 或 shear 拒绝；已计划修改的目标祖先也检查将写缩放，避免使子目标操作失效。源世界缩放须有限正值。源可只读查询引用对象，未直接写源节点。

`validate`/`run(dry_run=True)` 返回完整配对和原算法计划，不改场景/选区/时间/Undo/AutoKey。执行预先采样全部源值，解决两侧都选时前一写污染后一读取；目标按深度执行。返回 ToolResult.data `{parameters,rows,skipped,source_values_sampled_before_writes}`，每行含源/目标全路径、UUID 和三变换计划。实际场景写入标准 UndoChunk；AutoKey 临时关闭并恢复，不主动建 key，选择/时间不变。意外 Maya 命令失败可能已有部分变换，基类不会自动回滚，Undo 本次调用后复查；不写外部文件、不改 shelf/偏好。

示例：`tool=launch_candidate.load_tool(); preview=tool.run(objects=['|hand_L'],plane='YZ',mode='orientation',dry_run=True)`，成功后同参数 `run()`；窗口 `launch_candidate.show_ui()`。候选原 native class 属于内部保存源，不绕开受支持的 UI/API 调原写入口。

core/正式库未发现相同三模式完整流程，复用框架 Undo/ToolResult，不为统一架构改变 Euler 行为。可在 FCM Hider/WorldSpaceTools 恢复显示或烘焙之后使用输出确切对象，但目标动画通道需另备份静态对象并明确移除驱动，不自动删 rig/keys。组合只是作用域分析，生产组合待验收。

离线检查原 SHA/所有定义/UI保留、Schema/严格类型及公式。隔离 Maya2025 九平面模式与原 mirror_transform 实际世界矩阵一致；dry 无变/一次 Undo 原姿态/AutoKey，双向预采样、层级先父与忽略 shapes、namespace 保存、错误后行/锁/动画/歧义/实例/GUI batch 拒绝。真实 GUI、复杂控制器 pivot/rotateOrder/父级/大层级及其它 Maya 版本未验收。原作者/发行授权未推断，随源保留。
