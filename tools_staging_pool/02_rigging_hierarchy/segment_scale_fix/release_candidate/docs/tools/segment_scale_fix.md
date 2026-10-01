# 关闭骨骼分段比例补偿

工具 ID `segment_scale_fix`，类别 `rigging`。完整保留原 Python/MEL 两份脚本；两份原件均将当前选择中的 joint 的 `segmentScaleCompensate` 设为 0，没有递归操作或额外算法。候选消除顶层自动执行，提供 BaseMayaTool 协议、Schema、真实 Maya 小界面与单次晋级清单。无署名和许可文件，不推断对外发布权限。

`action=disable` 为默认；`objects` 是非空、唯一的完整 joint 列表，省略时严格沿用原脚本筛选所选关节，混合选择中的普通 transform 不处理；显式传普通 transform 报错。不展开层级，不改变父子关系、inverseScale 连接、transform 属性或未选择关节。`action=inspect` 返回资源与原功能记录，不接受 objects。

预检拒绝同一节点别名重复、歧义叶名、组件、引用/锁节点、锁定/连接驱动属性、真实 DAG 实例；Undo 必须开启。`dry_run=True` 返回 objects、changes（UUID、前后值）、unchanged_count、scene_write，无场景改动。已关闭的属性列入未修改计数，执行不重复 setAttr。实际修改由 BaseMayaTool.run 的一个 Undo chunk 分组，不改变选择、当前时间或 namespace，不写外部文件。

关闭补偿会使子关节继承父关节的比例，可能改变蒙皮/骨架的可见比例；本工具不会重新计算蒙皮权重，也不会自动修复 rig。应先保存备份、用 hierarchy_analyzer 检查关节树，再对明确范围运行，比较蒙皮和动画。不声称与任何其它工具已完成真实组合验收。

```python
tool.run(dry_run=True, objects=['rig:elbow_joint'])
tool.run(objects=['rig:elbow_joint'])
# Maya Undo 一次恢复本次属性。
```

隔离 Maya fixture 检查实际父缩放下的世界矩阵变化、scope、Undo 和保护；真实 GUI、生产 rig/蒙皮和其它 Maya 版本仍 not_run。文件及注册/面板晋级信息完整准备，人工验收前仍留在待整理池。
