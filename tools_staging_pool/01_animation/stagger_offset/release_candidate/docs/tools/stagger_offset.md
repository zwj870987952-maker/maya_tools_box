# 减选关键帧偏移候选

tool_id: stagger_offset，animation，prepared_unverified，真实 GUI not_run。原单次/批量两个脚本全部字节归档，两个完整工作方式都实现；原文件顶层自动打开窗口现在只留档，不作为模块导入入口。无外部依赖、素材或文件写入。

按 objects 显式列表顺序执行；省略则按 cmds.ls(selection=True,long=True) 返回的整节点列表，不保证关闭 Maya selection-order tracking 时与点击顺序完全一致。推荐 API 传 objects。原 ls(dag=True) 会自动展开子层级，候选明确不隐式扩展：需要处理子节点应显式加入。原始脚本在剩余所有对象上 selectKey，实际目标是全部现有键，候选也移动全部键，不误用预先图表选中的一小组键。

mode=once：首个不动，其余各移动一次 offset；mode=batch（默认）：模拟反复减选第一个，最终各对象累计 0、offset、2×offset……。offset -1000..1000默认5，支持负值/小数；至少两整 transform/joint。输出 ToolResult.data 含 objects、每对象 offsets、每曲线偏移/owners/key_count，以及是否改变选择。

原 per-time keyframe(...timeChange=new_time) 会遇到新时间与旧邻键碰撞或重复时间查询，多通道同帧还会重复处理。候选按曲线一次 relative timeChange 同步平移，保留键数量、值、切线，不通过逐帧重建曲线。不改 animation 形状，不把减选循环化简为不同含义。共享曲线必须每个输出对象都在此次范围且期望同一偏移；同偏移去重只移一次，不同偏移或输出至首个不动对象则整批拒绝。

整批 validate/dry_run 无键/时间/对象选择/键选择/Undo 栈修改，拒引用/锁定、非时间curve、time warp、animBlend/pairBlend/unitConversion图、外部共享输出或通道锁；没有动画的对象记为无curve，不导致其他对象失败。offset=0为无键写入操作。API update_selection=False默认保持选择；GUI选True保留原副作用：once选objects[1:]及其键，batch选最后对象及其键。选中键/图表上下文是UI状态，场景Undo不能当保证完整还原该状态。键移动本身使用共用UndoChunkContext，一次Undo/Redo整组恢复，失败可能部分键写入须Undo；未修改正式core。

GUI保留250宽、-1000..1000两位小数step0.1输入，合并原两个按钮/工作方式并私有窗口名，不覆盖旧selectFramesTool。Batch修改全部现有动画，应在备份场景验证约束/复杂rig前先烘焙为独立曲线。

```python
tool.run(dry_run=True,objects=['A','B','C'],offset=2,mode='batch')
tool.run(objects=['A','B','C'],offset=2,mode='batch') # 0,2,4
tool.run(objects=['A','B','C'],offset=-0.5,mode='once') # 0,-.5,-.5
```

潜在组合：动画烘焙→本工具错时→Graph Editor/曲线整理；和stagger_gui的区间值重采样不同，组合未实测。docs/tests/注册面板/资源迁移全部由promotion清单预制，真人验收通过才apply。
